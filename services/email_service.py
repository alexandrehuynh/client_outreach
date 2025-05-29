import os
import pickle
import base64
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import config
from utils.logger import logger, log_operation, log_error, log_rate_limit, log_compliance

class EmailService:
    """Gmail service for sending cold outreach emails."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly'
    ]
    
    def __init__(self):
        self.service = None
        self.sent_count = 0
        self.last_reset = datetime.now()
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
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
        
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Successfully authenticated with Gmail API")
    
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
        """Create email message."""
        message = MIMEMultipart('alternative')
        message['to'] = to_email
        message['from'] = f"{config.SENDER_NAME} <{config.SENDER_EMAIL}>"
        message['subject'] = subject
        
        # Add unsubscribe headers for compliance
        message['List-Unsubscribe'] = f"<mailto:{config.SENDER_EMAIL}?subject=UNSUBSCRIBE>"
        message['List-Unsubscribe-Post'] = "List-Unsubscribe=One-Click"
        
        # Create HTML and text versions
        html_body = self._convert_to_html(body)
        
        text_part = MIMEText(body, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        message.attach(text_part)
        message.attach(html_part)
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}
    
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
        """Send personalized email to lead."""
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
            
            # Create and send message
            message = self._create_message(to_email, personalized_subject, personalized_body)
            
            result = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            self.sent_count += 1
            
            log_operation("SEND_EMAIL", {
                "to": to_email,
                "template": template_type,
                "message_id": result.get('id'),
                "subject": personalized_subject
            })
            
            log_compliance("EMAIL_SENT", to_email, "CAN-SPAM compliant with unsubscribe")
            
            # Add delay between sends to avoid being flagged
            time.sleep(2)
            
            return True
            
        except HttpError as error:
            log_error("SEND_EMAIL", error, {
                "to": to_email,
                "template": template_type
            })
            return False
        except Exception as error:
            log_error("SEND_EMAIL", error, {
                "to": to_email,
                "template": template_type
            })
            return False
    
    def _personalize_content(self, content: str, lead_data: Dict) -> str:
        """Personalize email content with lead data."""
        replacements = {
            'name': lead_data.get('name', 'there'),
            'trainer_name': config.TRAINER_NAME,
            'business_name': config.BUSINESS_NAME,
            'phone_number': config.PHONE_NUMBER,
            'website_url': config.WEBSITE_URL
        }
        
        for key, value in replacements.items():
            content = content.replace(f'{{{key}}}', value)
        
        return content
    
    def send_initial_email(self, lead_data: Dict) -> bool:
        """Send initial outreach email."""
        return self.send_email(
            to_email=lead_data['email'],
            template_type='initial',
            lead_data=lead_data
        )
    
    def send_follow_up_email(self, lead_data: Dict) -> bool:
        """Send follow-up email."""
        return self.send_email(
            to_email=lead_data['email'],
            template_type='follow_up',
            lead_data=lead_data
        )
    
    def check_replies(self) -> List[Dict]:
        """Check for replies to sent emails."""
        try:
            # Search for emails in the last 7 days
            query = f"from:(-{config.SENDER_EMAIL}) newer_than:7d"
            
            result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=50
            ).execute()
            
            messages = result.get('messages', [])
            replies = []
            
            for message in messages:
                msg_detail = self.service.users().messages().get(
                    userId='me',
                    id=message['id']
                ).execute()
                
                headers = msg_detail['payload']['headers']
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                
                # Check if it's an unsubscribe request
                if 'unsubscribe' in subject.lower() or 'unsubscribe' in sender.lower():
                    replies.append({
                        'type': 'unsubscribe',
                        'from': sender,
                        'subject': subject,
                        'message_id': message['id']
                    })
                else:
                    replies.append({
                        'type': 'reply',
                        'from': sender,
                        'subject': subject,
                        'message_id': message['id']
                    })
            
            log_operation("CHECK_REPLIES", {"count": len(replies)})
            return replies
            
        except HttpError as error:
            log_error("CHECK_REPLIES", error)
            return []
    
    def get_email_stats(self) -> Dict:
        """Get email sending statistics."""
        return {
            'sent_this_hour': self.sent_count,
            'rate_limit': config.EMAIL_RATE_LIMIT,
            'last_reset': self.last_reset.isoformat(),
            'can_send_more': self.sent_count < config.EMAIL_RATE_LIMIT
        } 