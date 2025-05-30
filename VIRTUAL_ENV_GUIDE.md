# Virtual Environment Guide - Microsoft Services

## Updated Setup for Microsoft Services

This project now uses **Microsoft Graph API** (Outlook + OneDrive Excel) instead of Google services. Here's how to manage your virtual environment.

## Current Environment: `venv`

### 🔄 **Activate the Environment**

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```cmd
venv\Scripts\activate
```

### ✅ **Verify You're in the Right Environment**

When activated, your terminal should show:
```bash
(venv) your-computer:client_outreach$
```

### 📦 **Dependencies Installed**

The new environment includes:
- **Microsoft Graph SDK** (msgraph-sdk==1.0.0)
- **Azure Identity** (azure-identity==1.15.0)
- **MSAL** (msal==1.25.0) for authentication
- **Twilio** (twilio==8.10.0) for SMS
- **OpenPyXL** (openpyxl==3.1.2) for Excel support
- All other required dependencies

### 🧪 **Test Your Setup**

```bash
# Make sure you're in the activated environment
python test_setup.py
```

### 🔧 **Next Steps**

1. **Create `.env` file:**
   ```bash
   cp env.example .env
   ```

2. **Follow the setup guide:**
   - Read `MICROSOFT_SETUP_GUIDE.md`
   - Set up Azure AD app registration
   - Create OneDrive Excel workbook
   - Configure Twilio with your Bay Club email

3. **Configure your `.env` with real values:**
   ```env
   WORKBOOK_ID=your_actual_workbook_id
   OUTLOOK_CLIENT_ID=your_azure_app_client_id
   OUTLOOK_CLIENT_SECRET=your_azure_app_client_secret
   OUTLOOK_TENANT_ID=your_azure_tenant_id
   SENDER_EMAIL=alex.huynh@bayclubs.com
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### 🚫 **Deactivate Environment**

When you're done working:
```bash
deactivate
```

## Migration from Google Services ✅

**What was removed:**
- Google Auth libraries
- Google Sheets API
- Gmail API
- All Google-specific credentials

**What was added:**
- Microsoft Graph SDK
- Azure authentication
- OneDrive Excel support
- Outlook email integration

## Environment Management

### If You Need to Recreate the Environment:

```bash
# Remove old environment
rm -rf venv

# Create new environment
python -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Keep Dependencies Updated:

```bash
# Activate environment first
source venv/bin/activate

# Update all packages
pip install --upgrade -r requirements.txt
```

---

## 🎯 Quick Reference

**Activate:** `source venv/bin/activate`  
**Test:** `python test_setup.py`  
**Run:** `python main.py --mode status`  
**Deactivate:** `deactivate`

Your project is now fully migrated to Microsoft services! 🚀 