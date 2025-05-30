import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import requests

from msal import ConfidentialClientApplication
from azure.identity import ClientSecretCredential

from config import config
from utils.logger import logger, log_operation, log_error

class OneDriveExcelService:
    """Microsoft OneDrive Excel service for managing lead data via Graph API."""
    
    def __init__(self):
        self.workbook_id = config.WORKBOOK_ID
        self.worksheet_name = config.WORKSHEET_NAME
        self._access_token = None
    
    def _get_access_token(self) -> str:
        """Get access token for Microsoft Graph API."""
        if not self._access_token:
            try:
                # Use MSAL to get token
                app = ConfidentialClientApplication(
                    client_id=config.OUTLOOK_CLIENT_ID,
                    client_credential=config.OUTLOOK_CLIENT_SECRET,
                    authority=f"https://login.microsoftonline.com/{config.OUTLOOK_TENANT_ID}"
                )
                
                result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
                
                if "access_token" in result:
                    self._access_token = result["access_token"]
                else:
                    raise Exception(f"Failed to acquire token: {result}")
                    
            except Exception as e:
                logger.error(f"Failed to get access token: {e}")
                raise
        
        return self._access_token
    
    def _make_graph_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make authenticated request to Microsoft Graph API."""
        access_token = self._get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"https://graph.microsoft.com/v1.0{endpoint}"
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        if response.status_code in [200, 201, 202]:
            return response.json() if response.content else {}
        else:
            raise Exception(f"Graph API request failed: {response.status_code} - {response.text}")
    
    def get_all_leads(self) -> List[Dict[str, Any]]:
        """Get all leads from the Excel worksheet."""
        try:
            # Get worksheet data
            endpoint = f"/me/drive/items/{self.workbook_id}/workbook/worksheets('{self.worksheet_name}')/usedRange"
            result = self._make_graph_request('GET', endpoint)
            
            values = result.get('values', [])
            
            if not values:
                logger.warning("No data found in Excel worksheet")
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
            
            log_operation("GET_LEADS", {"count": len(leads), "service": "onedrive_excel"})
            return leads
            
        except Exception as error:
            log_error("GET_LEADS", error, {"service": "onedrive_excel"})
            raise
    
    def get_leads_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get leads filtered by status."""
        all_leads = self.get_all_leads()
        filtered_leads = [lead for lead in all_leads if lead.get('status', '').lower() == status.lower()]
        
        log_operation("GET_LEADS_BY_STATUS", {
            "status": status, 
            "count": len(filtered_leads),
            "service": "onedrive_excel"
        })
        return filtered_leads
    
    def update_lead_status(self, row_number: int, status: str, 
                          date_contacted: str = None, response_received: str = None,
                          follow_up_sent: str = None, notes: str = None):
        """Update lead status and related fields."""
        try:
            # Prepare update data
            updates = []
            
            # Status update (Column D)
            if status:
                updates.append({
                    'address': f'D{row_number}',
                    'values': [[status]]
                })
            
            # Date contacted (Column E)
            if date_contacted:
                updates.append({
                    'address': f'E{row_number}',
                    'values': [[date_contacted]]
                })
            
            # Response received (Column F)
            if response_received:
                updates.append({
                    'address': f'F{row_number}',
                    'values': [[response_received]]
                })
            
            # Follow-up sent (Column G)
            if follow_up_sent:
                updates.append({
                    'address': f'G{row_number}',
                    'values': [[follow_up_sent]]
                })
            
            # Notes (Column H)
            if notes:
                updates.append({
                    'address': f'H{row_number}',
                    'values': [[notes]]
                })
            
            # Batch update all changes
            for update in updates:
                endpoint = f"/me/drive/items/{self.workbook_id}/workbook/worksheets('{self.worksheet_name}')/range(address='{update['address']}')"
                self._make_graph_request('PATCH', endpoint, {'values': update['values']})
            
            log_operation("UPDATE_LEAD_STATUS", {
                "row": row_number,
                "status": status,
                "updates": len(updates),
                "service": "onedrive_excel"
            })
            
        except Exception as error:
            log_error("UPDATE_LEAD_STATUS", error, {"row": row_number, "service": "onedrive_excel"})
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
        try:
            contacted_leads = self.get_leads_by_status(config.STATUS_CONTACTED)
            follow_up_leads = []
            
            for lead in contacted_leads:
                date_contacted = lead.get('date_contacted', '')
                if not date_contacted:
                    continue
                
                try:
                    # Parse the date
                    contact_date = datetime.strptime(date_contacted.split(' ')[0], "%Y-%m-%d")
                    days_since_contact = (datetime.now() - contact_date).days
                    
                    # If it's been more than the configured follow-up delay
                    if days_since_contact >= config.FOLLOW_UP_DELAY_DAYS:
                        follow_up_leads.append(lead)
                        
                except ValueError:
                    # Skip if date format is invalid
                    continue
            
            log_operation("GET_FOLLOW_UP_LEADS", {
                "count": len(follow_up_leads),
                "service": "onedrive_excel"
            })
            return follow_up_leads
            
        except Exception as error:
            log_error("GET_FOLLOW_UP_LEADS", error, {"service": "onedrive_excel"})
            return []
    
    def create_backup(self) -> str:
        """Create a backup of the current worksheet data."""
        try:
            leads_data = self.get_all_leads()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create backups directory if it doesn't exist
            os.makedirs('backups', exist_ok=True)
            
            backup_filename = f"backups/leads_backup_{timestamp}.json"
            
            with open(backup_filename, 'w') as f:
                json.dump(leads_data, f, indent=2, default=str)
            
            log_operation("CREATE_BACKUP", {
                "filename": backup_filename,
                "record_count": len(leads_data),
                "service": "onedrive_excel"
            })
            
            return backup_filename
            
        except Exception as error:
            log_error("CREATE_BACKUP", error, {"service": "onedrive_excel"})
            raise
    
    def get_worksheet_stats(self) -> Dict:
        """Get statistics about the worksheet data."""
        try:
            all_leads = self.get_all_leads()
            
            stats = {
                'total_leads': len(all_leads),
                'by_status': {},
                'last_updated': datetime.now().isoformat(),
                'service': 'onedrive_excel'
            }
            
            # Count by status
            for lead in all_leads:
                status = lead.get('status', 'Unknown')
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            return stats
            
        except Exception as error:
            log_error("GET_WORKSHEET_STATS", error, {"service": "onedrive_excel"})
            return {'error': str(error)}

# For backward compatibility, alias the new service
SheetsService = OneDriveExcelService 