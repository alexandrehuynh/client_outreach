import os
import pickle
from datetime import datetime
from typing import Dict, List, Optional, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import config
from utils.logger import logger, log_operation, log_error

class GoogleSheetsService:
    """Google Sheets service for managing lead data."""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self):
        self.service = None
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
    
    def get_leads(self) -> List[Dict]:
        """Get all leads from the spreadsheet."""
        try:
            # Read data from the sheet
            range_name = f"{config.SHEET_NAME}!A:H"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=config.SPREADSHEET_ID,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning("No data found in spreadsheet")
                return []
            
            # Convert to list of dictionaries
            headers = values[0] if values else []
            leads = []
            
            for i, row in enumerate(values[1:], start=2):  # Start from row 2
                if len(row) >= 3:  # Must have at least name, email, phone
                    lead = {
                        'row_number': i,
                        'name': row[config.COLUMN_MAPPING['name']] if len(row) > config.COLUMN_MAPPING['name'] else '',
                        'email': row[config.COLUMN_MAPPING['email']] if len(row) > config.COLUMN_MAPPING['email'] else '',
                        'phone': row[config.COLUMN_MAPPING['phone']] if len(row) > config.COLUMN_MAPPING['phone'] else '',
                        'status': row[config.COLUMN_MAPPING['status']] if len(row) > config.COLUMN_MAPPING['status'] else config.STATUS_NEW,
                        'date_contacted': row[config.COLUMN_MAPPING['date_contacted']] if len(row) > config.COLUMN_MAPPING['date_contacted'] else '',
                        'response_received': row[config.COLUMN_MAPPING['response_received']] if len(row) > config.COLUMN_MAPPING['response_received'] else '',
                        'follow_up_sent': row[config.COLUMN_MAPPING['follow_up_sent']] if len(row) > config.COLUMN_MAPPING['follow_up_sent'] else '',
                        'notes': row[config.COLUMN_MAPPING['notes']] if len(row) > config.COLUMN_MAPPING['notes'] else ''
                    }
                    leads.append(lead)
            
            log_operation("GET_LEADS", {"count": len(leads), "service": "google_sheets"})
            return leads
            
        except HttpError as error:
            log_error("GET_LEADS", error, {"service": "google_sheets"})
            return []
        except Exception as error:
            log_error("GET_LEADS", error, {"service": "google_sheets"})
            return []
    
    def update_lead_status(self, row_number: int, status: str, notes: str = "") -> bool:
        """Update lead status and notes."""
        try:
            # Calculate column letters
            status_col = chr(ord('A') + config.COLUMN_MAPPING['status'])
            notes_col = chr(ord('A') + config.COLUMN_MAPPING['notes'])
            date_col = chr(ord('A') + config.COLUMN_MAPPING['date_contacted'])
            
            # Prepare updates
            updates = [
                {
                    'range': f"{config.SHEET_NAME}!{status_col}{row_number}",
                    'values': [[status]]
                },
                {
                    'range': f"{config.SHEET_NAME}!{notes_col}{row_number}",
                    'values': [[notes]]
                }
            ]
            
            # Add date if status is being changed to contacted
            if status == config.STATUS_CONTACTED:
                updates.append({
                    'range': f"{config.SHEET_NAME}!{date_col}{row_number}",
                    'values': [[datetime.now().strftime('%Y-%m-%d %H:%M:%S')]]
                })
            
            # Batch update
            body = {
                'valueInputOption': 'RAW',
                'data': updates
            }
            
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=config.SPREADSHEET_ID,
                body=body
            ).execute()
            
            log_operation("UPDATE_LEAD_STATUS", {
                "row": row_number,
                "status": status,
                "notes": notes,
                "service": "google_sheets"
            })
            
            return True
            
        except HttpError as error:
            log_error("UPDATE_LEAD_STATUS", error, {
                "row": row_number,
                "status": status,
                "service": "google_sheets"
            })
            return False
        except Exception as error:
            log_error("UPDATE_LEAD_STATUS", error, {
                "row": row_number,
                "status": status,
                "service": "google_sheets"
            })
            return False
    
    def update_follow_up_status(self, row_number: int) -> bool:
        """Mark that follow-up has been sent."""
        try:
            follow_up_col = chr(ord('A') + config.COLUMN_MAPPING['follow_up_sent'])
            
            self.service.spreadsheets().values().update(
                spreadsheetId=config.SPREADSHEET_ID,
                range=f"{config.SHEET_NAME}!{follow_up_col}{row_number}",
                valueInputOption='RAW',
                body={'values': [[datetime.now().strftime('%Y-%m-%d %H:%M:%S')]]}
            ).execute()
            
            log_operation("UPDATE_FOLLOW_UP", {
                "row": row_number,
                "service": "google_sheets"
            })
            
            return True
            
        except HttpError as error:
            log_error("UPDATE_FOLLOW_UP", error, {
                "row": row_number,
                "service": "google_sheets"
            })
            return False
        except Exception as error:
            log_error("UPDATE_FOLLOW_UP", error, {
                "row": row_number,
                "service": "google_sheets"
            })
            return False
    
    def add_lead(self, name: str, email: str, phone: str) -> bool:
        """Add a new lead to the spreadsheet."""
        try:
            # Prepare new row data
            new_row = [''] * 8  # Initialize with empty strings
            new_row[config.COLUMN_MAPPING['name']] = name
            new_row[config.COLUMN_MAPPING['email']] = email
            new_row[config.COLUMN_MAPPING['phone']] = phone
            new_row[config.COLUMN_MAPPING['status']] = config.STATUS_NEW
            
            # Append to sheet
            self.service.spreadsheets().values().append(
                spreadsheetId=config.SPREADSHEET_ID,
                range=f"{config.SHEET_NAME}!A:H",
                valueInputOption='RAW',
                body={'values': [new_row]}
            ).execute()
            
            log_operation("ADD_LEAD", {
                "name": name,
                "email": email,
                "phone": phone,
                "service": "google_sheets"
            })
            
            return True
            
        except HttpError as error:
            log_error("ADD_LEAD", error, {
                "name": name,
                "email": email,
                "service": "google_sheets"
            })
            return False
        except Exception as error:
            log_error("ADD_LEAD", error, {
                "name": name,
                "email": email,
                "service": "google_sheets"
            })
            return False
    
    def get_leads_for_follow_up(self, days_since_contact: int = 2) -> List[Dict]:
        """Get leads that need follow-up."""
        try:
            leads = self.get_leads()
            follow_up_leads = []
            
            for lead in leads:
                # Check if lead was contacted but no follow-up sent yet
                if (lead['status'] == config.STATUS_CONTACTED and 
                    not lead['follow_up_sent'] and 
                    lead['date_contacted']):
                    
                    try:
                        # Parse contact date
                        contact_date = datetime.strptime(lead['date_contacted'], '%Y-%m-%d %H:%M:%S')
                        days_passed = (datetime.now() - contact_date).days
                        
                        if days_passed >= days_since_contact:
                            follow_up_leads.append(lead)
                    except ValueError:
                        # Skip if date format is invalid
                        continue
            
            log_operation("GET_FOLLOW_UP_LEADS", {
                "count": len(follow_up_leads),
                "days_since_contact": days_since_contact,
                "service": "google_sheets"
            })
            
            return follow_up_leads
            
        except Exception as error:
            log_error("GET_FOLLOW_UP_LEADS", error, {"service": "google_sheets"})
            return []
    
    def create_spreadsheet_template(self) -> str:
        """Create a new spreadsheet with proper headers."""
        try:
            # Create new spreadsheet
            spreadsheet = {
                'properties': {
                    'title': 'Lead Tracking - Bay Club Outreach'
                },
                'sheets': [{
                    'properties': {
                        'title': config.SHEET_NAME
                    }
                }]
            }
            
            result = self.service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = result['spreadsheetId']
            
            # Add headers
            headers = ['Name', 'Email', 'Phone', 'Status', 'Date Contacted', 'Response Received', 'Follow-up Sent', 'Notes']
            
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{config.SHEET_NAME}!A1:H1",
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            
            # Format headers (bold)
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': 8
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat.textFormat.bold'
                }
            }]
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            log_operation("CREATE_SPREADSHEET", {
                "spreadsheet_id": spreadsheet_id,
                "service": "google_sheets"
            })
            
            return spreadsheet_id
            
        except HttpError as error:
            log_error("CREATE_SPREADSHEET", error, {"service": "google_sheets"})
            return ""
        except Exception as error:
            log_error("CREATE_SPREADSHEET", error, {"service": "google_sheets"})
            return ""

# For backward compatibility
SheetsService = GoogleSheetsService 