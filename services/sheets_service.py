import os
import pickle
from datetime import datetime
from typing import List, Dict, Optional, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import config
from utils.logger import logger, log_operation, log_error

class SheetsService:
    """Google Sheets service for managing lead data."""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self):
        self.service = None
        self.spreadsheet_id = config.SPREADSHEET_ID
        self.sheet_name = config.SHEET_NAME
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API."""
        creds = None
        
        # Load existing token
        if os.path.exists(config.GMAIL_TOKEN_FILE):
            with open(config.GMAIL_TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(config.GMAIL_CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"Credentials file {config.GMAIL_CREDENTIALS_FILE} not found. "
                        "Please download it from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.GMAIL_CREDENTIALS_FILE, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(config.GMAIL_TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('sheets', 'v4', credentials=creds)
        logger.info("Successfully authenticated with Google Sheets API")
    
    def get_all_leads(self) -> List[Dict[str, Any]]:
        """Get all leads from the spreadsheet."""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A:H"
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning("No data found in spreadsheet")
                return []
            
            # Skip header row and convert to dictionaries
            leads = []
            headers = ['name', 'email', 'phone', 'status', 'date_contacted', 
                      'response_received', 'follow_up_sent', 'notes']
            
            for i, row in enumerate(values[1:], start=2):  # Start from row 2
                # Pad row with empty strings if needed
                padded_row = row + [''] * (len(headers) - len(row))
                
                lead = dict(zip(headers, padded_row))
                lead['row_number'] = i
                leads.append(lead)
            
            log_operation("GET_LEADS", {"count": len(leads)})
            return leads
            
        except HttpError as error:
            log_error("GET_LEADS", error)
            raise
    
    def get_leads_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get leads filtered by status."""
        all_leads = self.get_all_leads()
        filtered_leads = [lead for lead in all_leads if lead.get('status', '').lower() == status.lower()]
        
        log_operation("GET_LEADS_BY_STATUS", {
            "status": status, 
            "count": len(filtered_leads)
        })
        return filtered_leads
    
    def update_lead_status(self, row_number: int, status: str, 
                          date_contacted: str = None, response_received: str = None,
                          follow_up_sent: str = None, notes: str = None):
        """Update lead status and related fields."""
        try:
            updates = []
            
            # Status update
            updates.append({
                'range': f"{self.sheet_name}!D{row_number}",
                'values': [[status]]
            })
            
            # Date contacted
            if date_contacted:
                updates.append({
                    'range': f"{self.sheet_name}!E{row_number}",
                    'values': [[date_contacted]]
                })
            
            # Response received
            if response_received:
                updates.append({
                    'range': f"{self.sheet_name}!F{row_number}",
                    'values': [[response_received]]
                })
            
            # Follow-up sent
            if follow_up_sent:
                updates.append({
                    'range': f"{self.sheet_name}!G{row_number}",
                    'values': [[follow_up_sent]]
                })
            
            # Notes
            if notes:
                updates.append({
                    'range': f"{self.sheet_name}!H{row_number}",
                    'values': [[notes]]
                })
            
            # Batch update
            body = {
                'valueInputOption': 'RAW',
                'data': updates
            }
            
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            log_operation("UPDATE_LEAD_STATUS", {
                "row": row_number,
                "status": status,
                "updates": len(updates)
            })
            
        except HttpError as error:
            log_error("UPDATE_LEAD_STATUS", error, {"row": row_number})
            raise
    
    def mark_contacted(self, row_number: int, contact_type: str):
        """Mark a lead as contacted with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notes = f"{contact_type} sent at {timestamp}"
        
        self.update_lead_status(
            row_number=row_number,
            status=config.STATUS_CONTACTED,
            date_contacted=timestamp,
            notes=notes
        )
    
    def mark_follow_up_sent(self, row_number: int, contact_type: str):
        """Mark follow-up as sent with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notes = f"Follow-up {contact_type} sent at {timestamp}"
        
        self.update_lead_status(
            row_number=row_number,
            status=config.STATUS_FOLLOW_UP_SENT,
            follow_up_sent=timestamp,
            notes=notes
        )
    
    def mark_unsubscribed(self, row_number: int, reason: str = "User request"):
        """Mark a lead as unsubscribed."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notes = f"Unsubscribed: {reason} at {timestamp}"
        
        self.update_lead_status(
            row_number=row_number,
            status=config.STATUS_UNSUBSCRIBED,
            notes=notes
        )
    
    def get_leads_for_follow_up(self) -> List[Dict[str, Any]]:
        """Get leads that need follow-up (contacted 2+ days ago, no response)."""
        from datetime import datetime, timedelta
        
        all_leads = self.get_all_leads()
        follow_up_leads = []
        
        cutoff_date = datetime.now() - timedelta(days=config.FOLLOW_UP_DELAY_DAYS)
        
        for lead in all_leads:
            if (lead.get('status') == config.STATUS_CONTACTED and 
                not lead.get('response_received') and 
                not lead.get('follow_up_sent')):
                
                date_contacted = lead.get('date_contacted')
                if date_contacted:
                    try:
                        contacted_date = datetime.strptime(date_contacted, "%Y-%m-%d %H:%M:%S")
                        if contacted_date <= cutoff_date:
                            follow_up_leads.append(lead)
                    except ValueError:
                        # Skip if date format is invalid
                        continue
        
        log_operation("GET_FOLLOW_UP_LEADS", {"count": len(follow_up_leads)})
        return follow_up_leads
    
    def create_backup(self) -> str:
        """Create a backup of the current spreadsheet data."""
        try:
            leads = self.get_all_leads()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backups/leads_backup_{timestamp}.json"
            
            # Create backups directory
            os.makedirs('backups', exist_ok=True)
            
            import json
            with open(backup_file, 'w') as f:
                json.dump(leads, f, indent=2)
            
            log_operation("CREATE_BACKUP", {"file": backup_file, "records": len(leads)})
            return backup_file
            
        except Exception as error:
            log_error("CREATE_BACKUP", error)
            raise 