# Microsoft Services Setup Guide

This guide will help you set up Microsoft services (Outlook + OneDrive Excel) to replace Google services (Gmail + Google Sheets) for your Bay Club outreach automation.

## Overview

You'll need to set up:
1. **Azure AD Application** (for authentication)
2. **OneDrive Excel Workbook** (for lead management)
3. **Outlook Email** (already using alex.huynh@bayclubs.com)
4. **Twilio Account** (for SMS using your Bay Club email)

---

## 1. Azure AD Application Setup

### Step 1: Create Azure AD App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Sign in with your `alex.huynh@bayclubs.com` account
3. Navigate to **Azure Active Directory** > **App registrations**
4. Click **"New registration"**
5. Fill in the details:
   - **Name**: `Bay Club Outreach Automation`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: Leave blank for now
6. Click **"Register"**

### Step 2: Get Required IDs

After registration, copy these values to your `.env` file:

- **Application (client) ID** → `OUTLOOK_CLIENT_ID`
- **Directory (tenant) ID** → `OUTLOOK_TENANT_ID`

### Step 3: Create Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **"New client secret"**
3. Add description: `Outreach Automation Secret`
4. Set expiration: `24 months`
5. Click **"Add"**
6. **IMPORTANT**: Copy the secret **Value** immediately → `OUTLOOK_CLIENT_SECRET`

### Step 4: Configure API Permissions

1. Go to **API permissions**
2. Click **"Add a permission"**
3. Select **Microsoft Graph**
4. Choose **Application permissions**
5. Add these permissions:
   - `Mail.Send`
   - `Mail.Read`
   - `Files.ReadWrite.All`
   - `Sites.ReadWrite.All`

6. Click **"Grant admin consent for [your org]"**
7. Confirm by clicking **"Yes"**

---

## 2. OneDrive Excel Workbook Setup

### Step 1: Create Excel Workbook

1. Go to [OneDrive](https://onedrive.live.com) or [Office 365](https://office.com)
2. Sign in with `alex.huynh@bayclubs.com`
3. Create a new **Excel workbook**
4. Name it: `Bay Club Leads`

### Step 2: Set Up Worksheet Structure

Create a worksheet named **"Leads"** with these column headers in row 1:

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| Name | Email | Phone | Status | Date Contacted | Response Received | Follow-up Sent | Notes |

### Step 3: Add Sample Data (Optional)

Add a few sample leads in rows 2-4:

| Name | Email | Phone | Status | Date Contacted | Response Received | Follow-up Sent | Notes |
|------|-------|-------|--------|---------------|-------------------|----------------|-------|
| John Doe | john@example.com | +1234567890 | New | | | | |
| Jane Smith | jane@example.com | +1987654321 | New | | | | |

### Step 4: Get Workbook ID

1. With your Excel file open in the browser
2. Look at the URL - it should contain something like:
   ```
   https://bayclub-my.sharepoint.com/personal/alex_huynh_bayclubs_com/_layouts/15/Doc.aspx?sourcedoc={WORKBOOK_ID}
   ```
3. Copy the `WORKBOOK_ID` value → `WORKBOOK_ID` in your `.env` file

**Alternative method to get Workbook ID:**
1. In Excel Online, go to **File** > **Info**
2. Copy the file ID from the properties

---

## 3. Twilio Setup with Bay Club Email

### Step 1: Sign Up for Twilio

1. Go to [Twilio](https://www.twilio.com)
2. Sign up using **alex.huynh@bayclubs.com**
3. Verify your email and phone number

### Step 2: Get Twilio Credentials

1. Go to [Twilio Console](https://console.twilio.com)
2. Find your **Account SID** → `TWILIO_ACCOUNT_SID`
3. Find your **Auth Token** → `TWILIO_AUTH_TOKEN`

### Step 3: Get Phone Number

1. In Twilio Console, go to **Phone Numbers** > **Manage** > **Buy a number**
2. Choose a phone number for SMS
3. Purchase the number
4. Copy the number → `TWILIO_PHONE_NUMBER` (format: +1234567890)

---

## 4. Environment Configuration

Create a `.env` file in your project root with these values:

```env
# Microsoft OneDrive Excel Configuration
WORKBOOK_ID=your_actual_workbook_id_from_step_2.4

# Microsoft Outlook Configuration  
OUTLOOK_CLIENT_ID=your_client_id_from_step_1.2
OUTLOOK_CLIENT_SECRET=your_client_secret_from_step_1.3
OUTLOOK_TENANT_ID=your_tenant_id_from_step_1.2
SENDER_EMAIL=alex.huynh@bayclubs.com

# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=your_account_sid_from_step_3.2
TWILIO_AUTH_TOKEN=your_auth_token_from_step_3.2
TWILIO_PHONE_NUMBER=your_phone_number_from_step_3.3

# Business Information (already configured)
BUSINESS_NAME=Bay Club
TRAINER_NAME=Alex Huynh
WEBSITE_URL=https://bayclubs.com
PHONE_NUMBER=your_actual_phone_number
```

---

## 5. Install Dependencies

Update your Python environment:

```bash
# Remove old Google dependencies and install Microsoft ones
pip uninstall google-auth google-auth-oauthlib google-api-python-client
pip install -r requirements.txt
```

---

## 6. Test Your Setup

Run the test script to verify everything works:

```bash
python test_setup.py
```

This will verify:
- ✅ Microsoft Graph authentication
- ✅ OneDrive Excel access
- ✅ Outlook email configuration
- ✅ Twilio SMS setup

---

## 7. Key Differences from Google Setup

### What Changed:
- **Gmail** → **Outlook** (Microsoft Graph API)
- **Google Sheets** → **OneDrive Excel** (Microsoft Graph API)
- **Google OAuth** → **Azure AD Application**
- **Service Account** → **Client Credentials Flow**

### What Stayed the Same:
- Twilio SMS functionality
- Email templates and messaging
- Rate limiting and compliance features
- Logging and monitoring
- Lead management workflow

---

## 8. Troubleshooting

### Common Issues:

**Authentication Errors:**
- Verify all IDs and secrets are correct in `.env`
- Ensure admin consent was granted for API permissions
- Check that the Azure AD app has the right permissions

**Workbook Access Issues:**
- Ensure the workbook is in your OneDrive (not SharePoint team site)
- Verify the workbook ID is correct
- Make sure the worksheet is named "Leads"

**Email Sending Issues:**
- Confirm `alex.huynh@bayclubs.com` has the necessary permissions
- Check that Mail.Send permission was granted
- Verify the tenant ID matches your organization

### Getting Help:

If you encounter issues:
1. Check the logs in `outreach_automation.log`
2. Run `python test_setup.py` for detailed diagnostics
3. Verify all environment variables are set correctly

---

## 9. Security Best Practices

1. **Never commit `.env` file** to version control
2. **Rotate client secrets** every 12-24 months
3. **Use least-privilege permissions** in Azure AD
4. **Monitor authentication logs** in Azure portal
5. **Keep dependencies updated** regularly

---

You're now ready to use Microsoft services for your Bay Club outreach automation! 🎉 