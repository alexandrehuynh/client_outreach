import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio

from msal import ConfidentialClientApplication, PublicClientApplication
from msgraph import GraphServiceClient
from azure.identity import ClientSecretCredential
import requests

from config import config
from utils.logger import logger, log_operation, log_error, log_rate_limit, log_compliance

class OutlookEmailService:
    """Microsoft Outlook service for sending cold outreach emails via Graph API."""
    
    # Microsoft Graph scopes needed for sending emails
    SCOPES = [
        'https://graph.microsoft.com/Mail.Send',
        'https://graph.microsoft.com/Mail.Read'
    ]
    
    def __init__(self):
        self.graph_client = None
        self.sent_count = 0
        self.last_reset = datetime.now()
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Microsoft Graph API."""
        try:
            # Use client credentials flow for server-to-server authentication
            credential = ClientSecretCredential(
                tenant_id=config.OUTLOOK_TENANT_ID,
                client_id=config.OUTLOOK_CLIENT_ID,
                client_secret=config.OUTLOOK_CLIENT_SECRET
            )
            
            # Create Graph service client
            self.graph_client = GraphServiceClient(
                credentials=credential,
                scopes=self.SCOPES
            )
            
            logger.info("Successfully authenticated with Microsoft Graph API")
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Microsoft Graph: {e}")
            raise
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        # Reset counter if it's been an hour
        if datetime.now() - self.last_reset > timedelta(hours=1):
            self.sent_count = 0
            self.last_reset = datetime.now()
        
        log_rate_limit("EMAIL", self.sent_count, config.EMAIL_RATE_LIMIT)
        
        if self.sent_count >= config.EMAIL_RATE_LIMIT:
            logger.warning(f"Email rate limit reached ({config.EMAIL_RATE_LIMIT}/hour)")
            return False
        
        return True
    
    def _create_message(self, to_email: str, subject: str, body: str) -> Dict:
        """Create email message for Graph API."""
        
        # Convert plain text to HTML with basic formatting
        html_body = self._convert_to_html(body)
        
        message = {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": html_body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to_email
                    }
                }
            ],
            "from": {
                "emailAddress": {
                    "address": config.SENDER_EMAIL,
                    "name": config.SENDER_NAME
                }
            },
            # Add compliance headers
            "internetMessageHeaders": [
                {
                    "name": "List-Unsubscribe",
                    "value": f"<mailto:{config.SENDER_EMAIL}?subject=UNSUBSCRIBE>"
                },
                {
                    "name": "List-Unsubscribe-Post", 
                    "value": "List-Unsubscribe=One-Click"
                }
            ]
        }
        
        return message
    
    def _convert_to_html(self, text: str) -> str:
        """Convert plain text to HTML with basic formatting."""
        html = text.replace('\n', '<br>')
        
        # Convert bullet points
        lines = html.split('<br>')
        for i, line in enumerate(lines):
            if line.strip().startswith('✓'):
                lines[i] = f"<li>{line.strip()[1:].strip()}</li>"
        
        html = '<br>'.join(lines)
        
        # Wrap list items
        if '<li>' in html:
            html = html.replace('<li>', '<ul><li>', 1)
            html = html.replace('</li><br>', '</li></ul><br>', html.count('</li>') - 1)
            html = html.replace('</li>', '</li></ul>', 1)
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        {html}
        </body>
        </html>
        """
    
    def send_email(self, to_email: str, template_type: str, lead_data: Dict) -> bool:
        """Send personalized email to lead via Microsoft Graph."""
        try:
            # Check rate limit
            if not self._check_rate_limit():
                return False
            
            # Get template
            template = config.EMAIL_TEMPLATES.get(template_type)
            if not template:
                raise ValueError(f"Template '{template_type}' not found")
            
            # Extract subject and body
            lines = template.strip().split('\n')
            subject_line = next((line for line in lines if line.startswith('Subject:')), '')
            subject = subject_line.replace('Subject:', '').strip()
            
            # Get body (everything after subject)
            body_start = template.find('\n', template.find('Subject:'))
            body = template[body_start:].strip()
            
            # Personalize content
            personalized_subject = self._personalize_content(subject, lead_data)
            personalized_body = self._personalize_content(body, lead_data)
            
            # Create message
            message = self._create_message(to_email, personalized_subject, personalized_body)
            
            # Send via Graph API using requests (simpler than async client)
            access_token = self._get_access_token()
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Use the /sendMail endpoint
            url = f"https://graph.microsoft.com/v1.0/users/{config.SENDER_EMAIL}/sendMail"
            payload = {
                "message": message,
                "saveToSentItems": True
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 202:  # Microsoft Graph returns 202 for successful send
                self.sent_count += 1
                
                log_operation("SEND_EMAIL", {
                    "to": to_email,
                    "template": template_type,
                    "subject": personalized_subject,
                    "service": "outlook"
                })
                
                log_compliance("EMAIL_SENT", to_email, "CAN-SPAM compliant with unsubscribe")
                
                # Add delay between sends to avoid being flagged
                time.sleep(2)
                
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code} - {response.text}")
                return False
            
        except Exception as error:
            log_error("SEND_EMAIL", error, {
                "to": to_email,
                "template": template_type,
                "service": "outlook"
            })
            return False
    
    def _get_access_token(self) -> str:
        """Get access token for Microsoft Graph API."""
        try:
            # Use MSAL to get token
            app = ConfidentialClientApplication(
                client_id=config.OUTLOOK_CLIENT_ID,
                client_credential=config.OUTLOOK_CLIENT_SECRET,
                authority=f"https://login.microsoftonline.com/{config.OUTLOOK_TENANT_ID}"
            )
            
            result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
            
            if "access_token" in result:
                return result["access_token"]
            else:
                raise Exception(f"Failed to acquire token: {result}")
                
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            raise
    
    def _personalize_content(self, content: str, lead_data: Dict) -> str:
        """Personalize email content with lead data."""
        replacements = {
            'name': lead_data.get('name', 'there'),
            'trainer_name': config.TRAINER_NAME,
            'business_name': config.BUSINESS_NAME,
            'phone_number': config.PHONE_NUMBER,
            'website_url': config.WEBSITE_URL
        }
        
        personalized = content
        for key, value in replacements.items():
            personalized = personalized.replace(f'{{{key}}}', str(value))
        
        return personalized
    
    def check_responses(self) -> List[Dict]:
        """Check for email responses and unsubscribe requests."""
        try:
            access_token = self._get_access_token()
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get recent emails from inbox
            url = f"https://graph.microsoft.com/v1.0/users/{config.SENDER_EMAIL}/mailFolders/inbox/messages"
            params = {
                '$top': 50,
                '$orderby': 'receivedDateTime desc',
                '$filter': f"receivedDateTime ge {(datetime.now() - timedelta(days=7)).isoformat()}"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                messages = response.json().get('value', [])
                responses = []
                
                for message in messages:
                    # Check if it's a response to our outreach
                    subject = message.get('subject', '').lower()
                    body = message.get('body', {}).get('content', '').lower()
                    sender = message.get('from', {}).get('emailAddress', {}).get('address', '')
                    
                    if any(keyword in subject or keyword in body for keyword in ['unsubscribe', 'remove', 'stop']):
                        responses.append({
                            'type': 'unsubscribe',
                            'sender': sender,
                            'subject': message.get('subject'),
                            'received': message.get('receivedDateTime')
                        })
                    elif 'yes' in body or 'interested' in body:
                        responses.append({
                            'type': 'interested',
                            'sender': sender,
                            'subject': message.get('subject'),
                            'received': message.get('receivedDateTime')
                        })
                
                log_operation("CHECK_RESPONSES", {"count": len(responses), "service": "outlook"})
                return responses
            else:
                logger.error(f"Failed to check responses: {response.status_code}")
                return []
                
        except Exception as error:
            log_error("CHECK_RESPONSES", error, {"service": "outlook"})
            return []
    
    def get_sent_count(self) -> int:
        """Get number of emails sent in current hour."""
        return self.sent_count

# For backward compatibility, alias the new service
EmailService = OutlookEmailService 