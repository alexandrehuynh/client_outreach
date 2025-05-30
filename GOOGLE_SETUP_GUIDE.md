# 🚀 Google Services Setup Guide

Complete setup guide for the Bay Club Cold Outreach Automation system using **Google Gmail + Google Sheets**.

## 📋 Overview

This system uses:
- **Gmail API**: Send emails from `alexhuynhfitness@gmail.com` that appear to come from `alex.huynh@bayclubs.com`
- **Google Sheets API**: Track leads and responses
- **Twilio SMS**: Send text messages (using Bay Club email for account)

## 🔧 Prerequisites

- Google account: `alexhuynhfitness@gmail.com`
- Access to `alex.huynh@bayclubs.com` email for Twilio verification
- Python 3.8+ installed
- Git (for version control)

## 📝 Step 1: Google Cloud Setup

### 1.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with `alexhuynhfitness@gmail.com`
3. Click "Select a project" → "New Project"
4. Project Name: `bay-club-outreach`
5. Click "Create"

### 1.2 Enable APIs

1. In your project, go to **APIs & Services** → **Library**
2. Search and enable these APIs:
   - **Gmail API**
   - **Google Sheets API**

### 1.3 Create Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth 2.0 Client IDs**
3. Configure OAuth consent screen:
   - User Type: **External**
   - App name: `Bay Club Outreach`
   - User support email: `alexhuynhfitness@gmail.com`
   - Authorized domains: Leave empty for now
   - Developer contact: `alexhuynhfitness@gmail.com`
   - Scopes: Add Gmail and Sheets scopes (handled automatically)
   - Test users: Add `alexhuynhfitness@gmail.com`
4. Create OAuth 2.0 Client ID:
   - Application type: **Desktop application**
   - Name: `Bay Club Outreach Desktop`
   - Click **Create**
5. **Download JSON** and save as `credentials.json` in your project folder

## 📊 Step 2: Google Sheets Setup

### 2.1 Create Spreadsheet

1. Go to [Google Sheets](https://sheets.google.com/)
2. Sign in with `alexhuynhfitness@gmail.com`
3. Create new spreadsheet: "Bay Club Lead Tracking"
4. Rename Sheet1 to "Leads"

### 2.2 Setup Headers

In the first row, add these exact headers:

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| Name | Email | Phone | Status | Date Contacted | Response Received | Follow-up Sent | Notes |

### 2.3 Get Spreadsheet ID

1. Copy the URL of your spreadsheet
2. Extract the ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0
   ```
3. Save this ID for your `.env` file

### 2.4 Add Sample Data (Optional)

Add a few test leads to verify the system works:

| Name | Email | Phone | Status | Date Contacted | Response Received | Follow-up Sent | Notes |
|------|-------|-------|--------|----------------|-------------------|----------------|-------|
| John Doe | john@example.com | +1234567890 | New | | | | Test lead |
| Jane Smith | jane@example.com | +1987654321 | New | | | | Test lead |

## 📧 Step 3: Gmail "Send As" Configuration

This makes emails appear to come from your Bay Club address while actually sending from your personal Gmail.

### 3.1 Setup Send As

1. Go to [Gmail Settings](https://mail.google.com/mail/u/0/#settings/accounts)
2. Sign in with `alexhuynhfitness@gmail.com`
3. Go to **Accounts and Import** tab
4. In "Send mail as" section, click **Add another email address**
5. Fill out the form:
   - Name: `Alex Huynh - Personal Trainer`
   - Email: `alex.huynh@bayclubs.com`
   - ☐ Treat as an alias (UNCHECK this!)
6. Click **Next Step**
7. Choose how to send emails:
   - **Option A**: If you have access to Bay Club email server settings, use SMTP
   - **Option B**: Gmail will send a verification email to `alex.huynh@bayclubs.com`

### 3.2 Verification

1. Check `alex.huynh@bayclubs.com` for verification email
2. Click the verification link or enter the code in Gmail
3. In Gmail settings, set `alex.huynh@bayclubs.com` as **default** sender

## 📱 Step 4: Twilio Setup

### 4.1 Create Twilio Account

1. Go to [Twilio Console](https://console.twilio.com/)
2. Sign up using `alex.huynh@bayclubs.com` email
3. Verify your phone number
4. Choose "SMS" as primary use case

### 4.2 Get Credentials

1. From Twilio Console Dashboard:
   - Copy **Account SID**
   - Copy **Auth Token**
2. Purchase a phone number or use trial number

## ⚙️ Step 5: Project Configuration

### 5.1 Clone and Setup

```bash
git clone <your-repo-url>
cd client_outreach
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5.2 Environment Configuration

1. Copy example environment file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` file with your credentials:
   ```bash
   # Google Sheets Configuration
   SPREADSHEET_ID=your_actual_spreadsheet_id_here
   
   # Gmail Configuration (actual account sending emails)
   GMAIL_ACCOUNT=alexhuynhfitness@gmail.com
   
   # Bay Club Business Email (what emails appear to come from)
   SENDER_EMAIL=alex.huynh@bayclubs.com
   
   # Twilio SMS Configuration
   TWILIO_ACCOUNT_SID=your_actual_twilio_sid
   TWILIO_AUTH_TOKEN=your_actual_twilio_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### 5.3 Place Credentials File

1. Put the downloaded `credentials.json` in your project root folder
2. Make sure it's in `.gitignore` (already configured)

## 🧪 Step 6: Test Setup

Run the test script to verify everything works:

```bash
python test_setup.py
```

This will test:
- ✅ Configuration loading
- ✅ Gmail API authentication  
- ✅ Google Sheets API authentication
- ✅ Twilio authentication
- ✅ Spreadsheet access
- ✅ Email template rendering
- ✅ SMS template rendering
- ✅ Logging system

## 🚀 Step 7: Usage

### 7.1 Basic Commands

```bash
# Check system status
python main.py --mode status

# Send initial emails to new leads
python main.py --send-emails

# Send SMS to new leads  
python main.py --send-sms

# Send follow-up emails
python main.py --send-follow-ups

# Check for responses
python main.py --check-responses
```

### 7.2 Add Leads

1. Open your Google Spreadsheet
2. Add new leads with Name, Email, Phone
3. Status will automatically be "New"
4. Run outreach commands

## 🔒 Security & Compliance

### Email Compliance
- ✅ CAN-SPAM compliant headers
- ✅ Unsubscribe links in every email
- ✅ Business contact information
- ✅ Professional sender identification

### SMS Compliance  
- ✅ TCPA compliant opt-out (STOP keyword)
- ✅ Business identification in messages
- ✅ Rate limiting to prevent spam flags

### Data Security
- ✅ Credentials stored in `.env` (not in code)
- ✅ Token files in `.gitignore`
- ✅ Activity logging for compliance

## 🔧 Troubleshooting

### Gmail Authentication Issues
```
FileNotFoundError: credentials.json not found
```
**Solution**: Download credentials.json from Google Cloud Console

### Google Sheets Access Issues
```
403 Forbidden
```
**Solution**: Enable Google Sheets API in Google Cloud Console

### "Send As" Not Working
```
Emails send but don't appear from Bay Club address
```
**Solution**: Complete Gmail "Send As" verification process

### Twilio SMS Issues
```
Authentication failed
```
**Solution**: Verify TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env

## 📞 Support

If you encounter issues:

1. Check the logs: `tail -f outreach_automation.log`
2. Run tests: `python test_setup.py`
3. Verify credentials in `.env` file
4. Ensure all APIs are enabled in Google Cloud

## 🎯 Best Practices

1. **Start Small**: Test with 2-3 leads first
2. **Monitor Deliverability**: Check spam folders initially  
3. **Track Responses**: Update spreadsheet with responses
4. **Respect Unsubscribes**: Process them immediately
5. **Regular Backups**: Export spreadsheet regularly

---

🏆 **Your Bay Club outreach system is now ready!**

The system will send professional emails that appear to come from `alex.huynh@bayclubs.com` while using the reliable Google infrastructure, with full tracking in your Google Spreadsheet. 