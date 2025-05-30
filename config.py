import os
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Config:
    # Microsoft OneDrive Excel Configuration (replaces Google Sheets)
    WORKBOOK_ID: str = field(default_factory=lambda: os.getenv('WORKBOOK_ID', 'your_onedrive_workbook_id_here'))
    WORKSHEET_NAME: str = 'Leads'
    
    # Microsoft Outlook Configuration (replaces Gmail)
    OUTLOOK_CLIENT_ID: str = field(default_factory=lambda: os.getenv('OUTLOOK_CLIENT_ID', 'your_azure_app_client_id'))
    OUTLOOK_CLIENT_SECRET: str = field(default_factory=lambda: os.getenv('OUTLOOK_CLIENT_SECRET', 'your_azure_app_client_secret'))
    OUTLOOK_TENANT_ID: str = field(default_factory=lambda: os.getenv('OUTLOOK_TENANT_ID', 'your_azure_tenant_id'))
    SENDER_EMAIL: str = field(default_factory=lambda: os.getenv('SENDER_EMAIL', 'alex.huynh@bayclubs.com'))
    SENDER_NAME: str = 'Alex Huynh - Personal Trainer'
    
    # Microsoft authentication files
    OUTLOOK_TOKEN_FILE: str = 'outlook_token.json'
    
    # Twilio SMS Configuration
    TWILIO_ACCOUNT_SID: str = field(default_factory=lambda: os.getenv('TWILIO_ACCOUNT_SID', 'your_twilio_sid'))
    TWILIO_AUTH_TOKEN: str = field(default_factory=lambda: os.getenv('TWILIO_AUTH_TOKEN', 'your_twilio_token'))
    TWILIO_PHONE_NUMBER: str = field(default_factory=lambda: os.getenv('TWILIO_PHONE_NUMBER', '+1234567890'))
    
    # Rate Limiting (messages per hour)
    EMAIL_RATE_LIMIT: int = 50
    SMS_RATE_LIMIT: int = 30
    
    # Follow-up timing (days)
    FOLLOW_UP_DELAY_DAYS: int = 2
    
    # Logging
    LOG_FILE: str = 'outreach_automation.log'
    LOG_LEVEL: str = 'INFO'
    
    # Business Information
    BUSINESS_NAME: str = 'Bay Club'
    TRAINER_NAME: str = 'Alex Huynh'
    WEBSITE_URL: str = 'https://bayclubs.com'
    PHONE_NUMBER: str = '+1234567890'  # Update with your actual phone number
    
    # Message Templates
    EMAIL_TEMPLATES: Dict[str, str] = field(default_factory=lambda: {
        'initial': """
Subject: Transform Your Fitness Journey at Bay Club - Free Consultation Available

Hi {name},

I hope this email finds you well! My name is {trainer_name}, and I'm a certified personal trainer at {business_name}.

I came across your information and noticed you might be interested in taking your fitness to the next level. I specialize in helping busy professionals like yourself achieve their health and fitness goals through personalized training programs at Bay Club.

Here's what I can offer you:
✓ Customized workout plans tailored to your lifestyle
✓ Nutrition guidance that actually works
✓ Access to Bay Club's premium facilities and equipment
✓ Flexible scheduling that fits your busy life
✓ Proven results with my 12-week transformation program

I'd love to offer you a complimentary 30-minute consultation where we can discuss your fitness goals and create a plan that works specifically for you. This consultation is completely free with no strings attached.

Would you be interested in scheduling a quick call this week? I have availability on weekday evenings and weekends.

Looking forward to helping you achieve your fitness goals!

Best regards,
{trainer_name}
{business_name}
📞 {phone_number}
🌐 {website_url}

P.S. If you're not interested in personal training services, simply reply with "UNSUBSCRIBE" and I'll remove you from my list immediately.
        """,
        
        'follow_up': """
Subject: Quick Follow-up - Your Free Fitness Consultation at Bay Club

Hi {name},

I wanted to follow up on my previous email about your complimentary fitness consultation at Bay Club. I understand you're probably busy, so I'll keep this brief.

As someone who's helped over 100 people transform their health and fitness, I know that taking the first step can feel overwhelming. That's exactly why I offer free consultations - to remove any barriers and help you get started on the right path.

This week only, I'm also including a free fitness assessment (normally $75) with your consultation at our state-of-the-art Bay Club facility.

If you're ready to invest in your health, just reply to this email or text me at {phone_number}. If you'd prefer not to hear from me again, simply reply with "UNSUBSCRIBE."

Your health is your wealth - let's make it a priority together.

Best,
{trainer_name}
{business_name}
        """
    })
    
    SMS_TEMPLATES: Dict[str, str] = field(default_factory=lambda: {
        'initial': """
Hi {name}! This is {trainer_name}, personal trainer at {business_name}. 

I'd love to offer you a FREE 30-min fitness consultation + assessment (worth $75) at our Bay Club facility. No strings attached - just want to help you reach your goals! 

Interested? Text YES for more info or STOP to opt out.

- {trainer_name}
        """,
        
        'follow_up': """
Hi {name}, quick follow-up from {trainer_name} at {business_name}. 

Still have your FREE consultation + $75 fitness assessment available at Bay Club. Many clients see results in just 2 weeks!

Ready to start your transformation? Text YES or STOP to opt out.

- {trainer_name}
        """
    })
    
    # Spreadsheet Column Mapping (same structure for Excel)
    COLUMN_MAPPING: Dict[str, int] = field(default_factory=lambda: {
        'name': 0,      # Column A
        'email': 1,     # Column B  
        'phone': 2,     # Column C
        'status': 3,    # Column D
        'date_contacted': 4,  # Column E
        'response_received': 5,  # Column F
        'follow_up_sent': 6,   # Column G
        'notes': 7      # Column H
    })
    
    # Status Constants
    STATUS_NEW: str = 'New'
    STATUS_CONTACTED: str = 'Contacted'
    STATUS_RESPONDED: str = 'Responded'
    STATUS_FOLLOW_UP_SENT: str = 'Follow-up Sent'
    STATUS_UNSUBSCRIBED: str = 'Unsubscribed'
    STATUS_CONVERTED: str = 'Converted'

# Create global config instance
config = Config() 