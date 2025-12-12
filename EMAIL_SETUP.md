# Email Configuration Guide

This guide will help you configure email alerts for unauthorized person detection.

## Gmail Setup (Recommended)

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** in the left menu
3. Under "Signing in to Google", enable **2-Step Verification**

### Step 2: Generate an App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Or navigate: **Security** → **2-Step Verification** → **App passwords**
3. Select **Mail** as the app
4. Select **Other (Custom name)** as the device
5. Enter "Raspberry Pi Security" as the name
6. Click **Generate**
7. **Copy the 16-character password** (you'll need this!)

### Step 3: Update config.json

Edit your `config.json` file and update the email section:

```json
{
    ...
    "email": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your_actual_email@gmail.com",
        "sender_password": "your_16_char_app_password",
        "recipient_email": "recipient_email@gmail.com"
    }
}
```

**Important:**
- `sender_email`: Your Gmail address (e.g., `john.doe@gmail.com`)
- `sender_password`: The 16-character app password (NOT your regular Gmail password)
- `recipient_email`: Where you want to receive alerts (can be the same as sender_email)

### Step 4: Test the Configuration

Run the security system and it will automatically send emails when unauthorized persons are detected.

## Other Email Providers

### Outlook/Hotmail
```json
"email": {
    "smtp_server": "smtp-mail.outlook.com",
    "smtp_port": 587,
    "sender_email": "your_email@outlook.com",
    "sender_password": "your_password",
    "recipient_email": "recipient@outlook.com"
}
```

### Yahoo Mail
```json
"email": {
    "smtp_server": "smtp.mail.yahoo.com",
    "smtp_port": 587,
    "sender_email": "your_email@yahoo.com",
    "sender_password": "your_app_password",
    "recipient_email": "recipient@yahoo.com"
}
```

### Custom SMTP Server
```json
"email": {
    "smtp_server": "smtp.yourdomain.com",
    "smtp_port": 587,
    "sender_email": "alerts@yourdomain.com",
    "sender_password": "your_password",
    "recipient_email": "recipient@yourdomain.com"
}
```

## Troubleshooting

### Error: "Authentication failed"
- **Gmail**: Make sure you're using an App Password, not your regular password
- **Other providers**: Check if you need to enable "Less secure app access" or use an app password

### Error: "Connection refused"
- Check your internet connection
- Verify the SMTP server and port are correct
- Some networks block port 587 - try port 465 with SSL (requires code modification)

### Error: "Email configuration incomplete"
- Make sure all email fields in `config.json` are filled out
- Check for typos in the JSON file (commas, quotes, brackets)

### Email not sending but no error
- Check your spam/junk folder
- Verify the recipient email address is correct
- Check the console output for any error messages

## Security Notes

⚠️ **Important Security Tips:**
- Never commit your `config.json` with real passwords to Git
- Use app passwords instead of your main email password
- Consider using environment variables for sensitive data
- Keep your `config.json` file permissions restricted: `chmod 600 config.json`

## Testing Email Without Waiting for Detection

You can test the email system by temporarily modifying the code or by using a simple test script. The email will automatically send when:
1. An unauthorized person is detected
2. The 5-second delay has passed (or 1 second for repeat offenders)
3. The person was never authorized during that time

