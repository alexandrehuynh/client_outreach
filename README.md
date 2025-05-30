# 🎯 Bay Club Cold Outreach Automation

Automated email and SMS outreach system for Bay Club personal training services using **Google Gmail + Google Sheets** with professional Bay Club branding.

## 🌟 Features

- **Gmail Integration**: Send from `alexhuynhfitness@gmail.com` that appears to come from `alex.huynh@bayclubs.com`
- **Google Sheets Tracking**: Comprehensive lead management and response tracking
- **Twilio SMS**: Professional text message outreach
- **Smart Follow-ups**: Automated follow-up sequences
- **Compliance**: CAN-SPAM and TCPA compliant
- **Rate Limiting**: Prevents spam flags and account issues
- **Response Monitoring**: Automatic unsubscribe and interest detection

## 🚀 Quick Start

### 1. Setup
```bash
git clone <your-repo>
cd client_outreach
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
```bash
cp env.example .env
# Edit .env with your credentials
```

### 3. Google Services Setup
Follow the detailed [Google Setup Guide](GOOGLE_SETUP_GUIDE.md) to configure:
- Google Cloud Project with Gmail & Sheets APIs
- OAuth credentials download
- Google Spreadsheet creation
- Gmail "Send As" configuration for Bay Club email

### 4. Test Setup
```bash
python test_setup.py
```

### 5. Start Outreach
```bash
python main.py --send-emails
```

## 📊 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Google Sheets  │    │   Gmail API      │    │   Twilio SMS    │
│  Lead Tracking  │◄──►│  Email Service   │◄──►│   Service       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Main Automation Engine                         │
│  • Lead Processing  • Response Monitoring  • Follow-ups        │
└─────────────────────────────────────────────────────────────────┘
```

## 📧 Email Flow

1. **Personal Gmail Account**: `alexhuynhfitness@gmail.com` (actual sender)
2. **Gmail "Send As" Feature**: Makes emails appear from `alex.huynh@bayclubs.com`
3. **Professional Branding**: All emails branded as Bay Club
4. **Compliance**: Automatic unsubscribe headers and CAN-SPAM compliance

## 📱 SMS Flow

1. **Twilio Account**: Registered with `alex.huynh@bayclubs.com`
2. **Professional Messages**: Bay Club branded SMS templates
3. **Opt-out Compliance**: STOP keyword handling
4. **Rate Limiting**: Prevents carrier blocking

## 🎯 Lead Management

### Lead Status Flow
```
New → Contacted → Responded/Follow-up Sent → Converted/Unsubscribed
```

### Google Sheets Structure
| Column | Purpose | Auto-Updated |
|--------|---------|--------------|
| Name | Lead's name | Manual |
| Email | Contact email | Manual |
| Phone | Phone number | Manual |
| Status | Current status | ✅ Auto |
| Date Contacted | When first contacted | ✅ Auto |
| Response Received | If they responded | ✅ Auto |
| Follow-up Sent | Follow-up timestamp | ✅ Auto |
| Notes | Additional info | Manual/Auto |

## 🔧 Commands

```bash
# System Status
python main.py --mode status

# Send initial outreach emails
python main.py --send-emails

# Send SMS to new leads
python main.py --send-sms  

# Send follow-up emails (2+ days after initial contact)
python main.py --send-follow-ups

# Check for email responses and unsubscribes
python main.py --check-responses

# Interactive mode for testing
python main.py --interactive
```

## 📈 Monitoring & Analytics

### Real-time Tracking
- Email delivery status
- SMS delivery confirmation  
- Response detection
- Unsubscribe processing
- Lead conversion tracking

### Compliance Logging
- All outreach activities logged
- Unsubscribe request timestamps
- Rate limiting enforcement
- Error tracking and recovery

## 🔒 Security & Compliance

### Email Compliance (CAN-SPAM)
- ✅ Clear sender identification
- ✅ Truthful subject lines  
- ✅ Business address included
- ✅ Easy unsubscribe process
- ✅ Prompt unsubscribe processing

### SMS Compliance (TCPA)
- ✅ Explicit consent assumed for business leads
- ✅ Clear opt-out instructions (STOP)
- ✅ Business identification in messages
- ✅ Reasonable sending hours
- ✅ Rate limiting to prevent spam

### Data Security
- ✅ Credentials stored in environment variables
- ✅ No hardcoded sensitive information
- ✅ Secure OAuth 2.0 authentication
- ✅ Activity logging for audit trails

## 🎨 Customization

### Email Templates
Located in `config.py` - easily customizable:
- Initial outreach email
- Follow-up email
- Personalized with lead information
- Bay Club branding and contact info

### SMS Templates  
Professional SMS templates with:
- Bay Club branding
- Clear call-to-action
- Opt-out instructions
- Personal trainer identification

### Business Information
Update `config.py` for your specific details:
```python
BUSINESS_NAME = 'Bay Club'
TRAINER_NAME = 'Alex Huynh'  
SENDER_EMAIL = 'alex.huynh@bayclubs.com'
WEBSITE_URL = 'https://bayclubs.com'
```

## 📚 File Structure

```
client_outreach/
├── services/
│   ├── email_service.py      # Gmail API integration
│   ├── sheets_service.py     # Google Sheets API
│   └── sms_service.py        # Twilio SMS service
├── utils/
│   └── logger.py             # Logging and compliance
├── config.py                 # Configuration and templates
├── main.py                   # Main automation script
├── test_setup.py             # System verification
├── GOOGLE_SETUP_GUIDE.md     # Detailed setup instructions
└── requirements.txt          # Python dependencies
```

## 🔧 Development

### Adding New Features
1. Fork the repository
2. Create feature branch
3. Add functionality with proper logging
4. Update tests and documentation
5. Submit pull request

### Testing
```bash
# Test all system components
python test_setup.py

# Test specific functionality
python -m pytest tests/
```

## 📞 Troubleshooting

### Common Issues

1. **Gmail Authentication Errors**
   - Ensure `credentials.json` is downloaded from Google Cloud
   - Verify Gmail API is enabled
   - Check OAuth consent screen configuration

2. **"Send As" Not Working**
   - Complete Gmail "Send As" verification process
   - Check `alex.huynh@bayclubs.com` for verification email
   - Ensure Bay Club email is set as default sender

3. **Google Sheets Access Issues**
   - Verify Google Sheets API is enabled  
   - Check spreadsheet sharing permissions
   - Confirm SPREADSHEET_ID in .env file

4. **Twilio SMS Issues**
   - Verify account credentials in .env
   - Check phone number format (+1XXXXXXXXXX)
   - Ensure sufficient Twilio account balance

### Logs
Check `outreach_automation.log` for detailed error information and system activity.

## 🎯 Best Practices

1. **Start Small**: Test with 2-3 leads initially
2. **Monitor Deliverability**: Check spam folders for first few sends
3. **Respect Unsubscribes**: Process them immediately
4. **Regular Backups**: Export Google Sheets data regularly
5. **Update Templates**: Keep messaging fresh and relevant

## 📄 License

This project is for Bay Club internal use. All rights reserved.

---

🏆 **Professional outreach automation for Bay Club personal training services**

For detailed setup instructions, see [GOOGLE_SETUP_GUIDE.md](GOOGLE_SETUP_GUIDE.md) 