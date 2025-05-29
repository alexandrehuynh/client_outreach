# Cold Outreach Automation System for Personal Training Business

A comprehensive Python automation system for managing cold email and SMS outreach to fitness leads. This system integrates with Google Sheets for lead management, Gmail for email sending, and Twilio for SMS messaging.

## Features

✅ **Multi-Channel Outreach**: Send both emails and SMS messages  
✅ **Google Sheets Integration**: Automatic lead management and status tracking  
✅ **Smart Follow-ups**: Automated follow-up messages after 2 days  
✅ **Rate Limiting**: Built-in protection against being flagged as spam  
✅ **Compliance**: CAN-SPAM and TCPA compliant with unsubscribe mechanisms  
✅ **Response Tracking**: Monitor replies and automatically handle unsubscribes  
✅ **Comprehensive Logging**: Detailed logs for monitoring and debugging  
✅ **Backup System**: Automatic data backups before processing  

## System Requirements

- Python 3.8 or higher
- Google Cloud Platform account (for Gmail and Sheets APIs)
- Twilio account (for SMS)
- Google Sheets document with lead data

## Installation

### 1. Clone and Install Dependencies

```bash
git clone <your-repo-url>
cd client_reachout
pip install -r requirements.txt
```

### 2. Google Cloud Console Setup

#### Enable APIs
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Gmail API
   - Google Sheets API

#### Create Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop Application"
4. Download the JSON file and rename it to `credentials.json`
5. Place `credentials.json` in the project root directory

### 3. Twilio Setup

1. Sign up for [Twilio](https://www.twilio.com/)
2. Get your Account SID and Auth Token from the dashboard
3. Purchase a phone number for sending SMS

### 4. Google Sheets Setup

1. Create a new Google Sheets document
2. Set up columns in this exact order:
   - Column A: Name
   - Column B: Email  
   - Column C: Phone
   - Column D: Status
   - Column E: Date_Contacted
   - Column F: Response_Received
   - Column G: Follow_Up_Sent
   - Column H: Notes

3. Add a header row with these column names
4. Copy the spreadsheet ID from the URL (the long string between `/d/` and `/edit`)

### 5. Configuration

1. Copy the environment file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` with your actual credentials:
   ```bash
   SPREADSHEET_ID=your_actual_spreadsheet_id
   SENDER_EMAIL=your_bayclub_email@domain.com
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

3. Customize business information in `config.py`:
   ```python
   BUSINESS_NAME = 'Your Fitness Studio'
   TRAINER_NAME = 'Your Name'
   WEBSITE_URL = 'https://yourwebsite.com'
   PHONE_NUMBER = '+1234567890'
   ```

## Usage

### First Run Authentication

On first run, the system will open a browser window for Google authentication:

```bash
python main.py --mode status
```

Follow the prompts to authorize access to Gmail and Sheets.

### Basic Operations

#### Process New Leads
```bash
# Send both email and SMS to new leads
python main.py --mode new

# Email only
python main.py --mode new --email-only

# SMS only  
python main.py --mode new --sms-only
```

#### Process Follow-ups
```bash
# Send follow-ups to leads contacted 2+ days ago
python main.py --mode follow-up
```

#### Process Both New and Follow-ups
```bash
python main.py --mode both
```

#### Check System Status
```bash
python main.py --mode status
```

#### Check for Responses
```bash
python main.py --mode check-responses
```

#### Dry Run (Preview Only)
```bash
python main.py --mode both --dry-run
```

### Automated Scheduling

#### macOS/Linux (Cron)

Add to crontab (`crontab -e`):

```bash
# Run every 4 hours during business days
0 9,13,17 * * 1-5 cd /path/to/client_reachout && python main.py --mode both

# Check responses every 2 hours
0 */2 * * * cd /path/to/client_reachout && python main.py --mode check-responses
```

#### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 9 AM)
4. Set action to start program: `python`
5. Add arguments: `/path/to/client_reachout/main.py --mode both`
6. Set start in: `/path/to/client_reachout`

## Message Templates

The system includes professional, fitness-focused templates:

### Email Templates
- **Initial**: Warm introduction with free consultation offer
- **Follow-up**: Brief reminder with added value proposition

### SMS Templates  
- **Initial**: Concise offer with clear opt-out
- **Follow-up**: Short reminder maintaining engagement

### Customizing Templates

Edit templates in `config.py`:

```python
EMAIL_TEMPLATES = {
    'initial': """
Subject: Your Custom Subject

Your custom email content with {name} personalization.

Best regards,
{trainer_name}
    """,
    # ... more templates
}
```

## Lead Status Workflow

```
New → Contacted → Follow-up Sent → Responded/Converted
                ↓
           Unsubscribed
```

- **New**: Fresh leads ready for initial outreach
- **Contacted**: Initial message sent, waiting for response  
- **Follow-up Sent**: Follow-up message sent after 2 days
- **Responded**: Lead replied to messages
- **Unsubscribed**: Lead opted out
- **Converted**: Lead became a client

## Rate Limiting & Compliance

### Built-in Protections
- **Email**: 50 messages per hour maximum
- **SMS**: 30 messages per hour maximum
- **Delays**: 2-3 seconds between messages
- **Unsubscribe**: Automatic opt-out handling

### Compliance Features
- **CAN-SPAM**: Unsubscribe headers in all emails
- **TCPA**: STOP keyword handling for SMS
- **Logging**: Complete audit trail for compliance

## Monitoring & Logs

### Log Files
- Location: `logs/outreach_automation.log`
- Rotation: Automatic when files exceed 10MB
- Retention: 5 backup files

### Key Metrics to Monitor
- Send success rates
- Response rates
- Unsubscribe rates
- Error frequencies

## Troubleshooting

### Common Issues

#### "Credentials file not found"
- Ensure `credentials.json` is in the project root
- Re-download from Google Cloud Console if needed

#### "Invalid phone number format"
- Phone numbers must be in format: +1234567890
- Check Twilio phone number configuration

#### "Rate limit exceeded"
- Wait for the hourly reset
- Consider reducing batch sizes

#### "Spreadsheet not found"
- Verify SPREADSHEET_ID in `.env`
- Ensure the sheet is shared with your Google account

### Email Delivery Issues

1. **Emails going to spam**:
   - Reduce sending rate
   - Improve email content quality
   - Use authenticated domain

2. **Gmail API errors**:
   - Check API quotas in Google Cloud Console
   - Verify OAuth scopes are correct

### SMS Delivery Issues

1. **SMS not delivering**:
   - Verify phone number format
   - Check Twilio account balance
   - Review Twilio console logs

## Security Best Practices

1. **Credential Management**:
   - Never commit `.env` or `credentials.json` to version control
   - Use strong, unique passwords
   - Enable 2FA on all accounts

2. **Rate Limiting**:
   - Don't exceed built-in limits
   - Monitor for unusual error rates
   - Implement additional delays if needed

3. **Data Protection**:
   - Regular backups (automated by system)
   - Secure local file storage
   - Compliance with data protection laws

## Support

For issues or questions:

1. Check logs in `logs/outreach_automation.log`
2. Review this README for common solutions
3. Check Google Cloud Console for API quotas/errors
4. Review Twilio console for SMS delivery issues

## License

This project is for personal/business use. Ensure compliance with local regulations regarding cold outreach.

---

**Important**: Always comply with CAN-SPAM, TCPA, and local regulations when conducting cold outreach. This system provides compliance tools but the responsibility for lawful use remains with the operator. 