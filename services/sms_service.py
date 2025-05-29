import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

from config import config
from utils.logger import logger, log_operation, log_error, log_rate_limit, log_compliance

class SMSService:
    """Twilio SMS service for sending cold outreach messages."""
    
    def __init__(self):
        self.client = None
        self.sent_count = 0
        self.last_reset = datetime.now()
        self._authenticate()
    
    def _authenticate(self):
        """Initialize Twilio client."""
        try:
            if not config.TWILIO_ACCOUNT_SID or not config.TWILIO_AUTH_TOKEN:
                raise ValueError("Twilio credentials not configured")
            
            self.client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
            
            # Test authentication by fetching account info
            account = self.client.api.accounts(config.TWILIO_ACCOUNT_SID).fetch()
            logger.info(f"Successfully authenticated with Twilio - Account: {account.friendly_name}")
            
        except Exception as error:
            log_error("TWILIO_AUTH", error)
            raise
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within SMS rate limits."""
        # Reset counter if it's been an hour
        if datetime.now() - self.last_reset > timedelta(hours=1):
            self.sent_count = 0
            self.last_reset = datetime.now()
        
        log_rate_limit("SMS", self.sent_count, config.SMS_RATE_LIMIT)
        
        if self.sent_count >= config.SMS_RATE_LIMIT:
            logger.warning(f"SMS rate limit reached ({config.SMS_RATE_LIMIT}/hour)")
            return False
        
        return True
    
    def _validate_phone_number(self, phone: str) -> str:
        """Validate and format phone number."""
        # Remove all non-digit characters
        cleaned = ''.join(filter(str.isdigit, phone))
        
        # Add country code if missing
        if len(cleaned) == 10:
            cleaned = '1' + cleaned
        
        # Format as E.164
        if len(cleaned) == 11 and cleaned.startswith('1'):
            return f"+{cleaned}"
        
        raise ValueError(f"Invalid phone number format: {phone}")
    
    def send_sms(self, to_phone: str, template_type: str, lead_data: Dict) -> bool:
        """Send personalized SMS to lead."""
        try:
            # Check rate limit
            if not self._check_rate_limit():
                return False
            
            # Validate phone number
            formatted_phone = self._validate_phone_number(to_phone)
            
            # Get template
            template = config.SMS_TEMPLATES.get(template_type)
            if not template:
                raise ValueError(f"SMS template '{template_type}' not found")
            
            # Personalize content
            personalized_message = self._personalize_content(template, lead_data)
            
            # Send SMS
            message = self.client.messages.create(
                body=personalized_message,
                from_=config.TWILIO_PHONE_NUMBER,
                to=formatted_phone
            )
            
            self.sent_count += 1
            
            log_operation("SEND_SMS", {
                "to": formatted_phone,
                "template": template_type,
                "message_sid": message.sid,
                "status": message.status
            })
            
            log_compliance("SMS_SENT", formatted_phone, "TCPA compliant with opt-out")
            
            # Add delay between sends
            time.sleep(1)
            
            return True
            
        except TwilioException as error:
            log_error("SEND_SMS", error, {
                "to": to_phone,
                "template": template_type,
                "error_code": getattr(error, 'code', None)
            })
            return False
        except Exception as error:
            log_error("SEND_SMS", error, {
                "to": to_phone,
                "template": template_type
            })
            return False
    
    def _personalize_content(self, content: str, lead_data: Dict) -> str:
        """Personalize SMS content with lead data."""
        replacements = {
            'name': lead_data.get('name', 'there'),
            'trainer_name': config.TRAINER_NAME,
            'business_name': config.BUSINESS_NAME,
            'phone_number': config.PHONE_NUMBER,
            'website_url': config.WEBSITE_URL
        }
        
        for key, value in replacements.items():
            content = content.replace(f'{{{key}}}', value)
        
        return content.strip()
    
    def send_initial_sms(self, lead_data: Dict) -> bool:
        """Send initial outreach SMS."""
        return self.send_sms(
            to_phone=lead_data['phone'],
            template_type='initial',
            lead_data=lead_data
        )
    
    def send_follow_up_sms(self, lead_data: Dict) -> bool:
        """Send follow-up SMS."""
        return self.send_sms(
            to_phone=lead_data['phone'],
            template_type='follow_up',
            lead_data=lead_data
        )
    
    def check_replies(self) -> List[Dict]:
        """Check for SMS replies and opt-outs."""
        try:
            # Get messages from the last 7 days
            since = datetime.now() - timedelta(days=7)
            
            messages = self.client.messages.list(
                to=config.TWILIO_PHONE_NUMBER,
                date_sent_after=since,
                limit=100
            )
            
            replies = []
            
            for message in messages:
                body = message.body.lower()
                
                # Check for opt-out keywords
                opt_out_keywords = ['stop', 'unsubscribe', 'opt out', 'remove', 'quit']
                is_opt_out = any(keyword in body for keyword in opt_out_keywords)
                
                # Check for positive responses
                positive_keywords = ['yes', 'interested', 'tell me more', 'info']
                is_positive = any(keyword in body for keyword in positive_keywords)
                
                reply_type = 'opt_out' if is_opt_out else ('positive' if is_positive else 'reply')
                
                replies.append({
                    'type': reply_type,
                    'from': message.from_,
                    'body': message.body,
                    'message_sid': message.sid,
                    'date_sent': message.date_sent.isoformat() if message.date_sent else None
                })
            
            log_operation("CHECK_SMS_REPLIES", {"count": len(replies)})
            return replies
            
        except TwilioException as error:
            log_error("CHECK_SMS_REPLIES", error)
            return []
    
    def get_message_status(self, message_sid: str) -> Dict:
        """Get detailed status of a sent message."""
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                'sid': message.sid,
                'status': message.status,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'date_sent': message.date_sent.isoformat() if message.date_sent else None,
                'date_updated': message.date_updated.isoformat() if message.date_updated else None
            }
            
        except TwilioException as error:
            log_error("GET_MESSAGE_STATUS", error, {"message_sid": message_sid})
            return {}
    
    def get_sms_stats(self) -> Dict:
        """Get SMS sending statistics."""
        return {
            'sent_this_hour': self.sent_count,
            'rate_limit': config.SMS_RATE_LIMIT,
            'last_reset': self.last_reset.isoformat(),
            'can_send_more': self.sent_count < config.SMS_RATE_LIMIT
        }
    
    def validate_phone_numbers(self, phone_numbers: List[str]) -> Dict[str, Dict]:
        """Validate a list of phone numbers using Twilio Lookup API."""
        results = {}
        
        for phone in phone_numbers:
            try:
                # Use Twilio Lookup API to validate
                lookup = self.client.lookups.phone_numbers(phone).fetch()
                
                results[phone] = {
                    'valid': True,
                    'formatted': lookup.phone_number,
                    'country_code': lookup.country_code,
                    'carrier': getattr(lookup.carrier, 'name', None) if hasattr(lookup, 'carrier') else None
                }
                
            except TwilioException as error:
                results[phone] = {
                    'valid': False,
                    'error': str(error),
                    'error_code': getattr(error, 'code', None)
                }
        
        log_operation("VALIDATE_PHONE_NUMBERS", {
            "total": len(phone_numbers),
            "valid": sum(1 for r in results.values() if r['valid'])
        })
        
        return results 