#!/usr/bin/env python3
"""
Simple email test - no dependencies on OpenCV
"""

import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

def test_email_simple():
    """Simple email test without image attachment"""
    
    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config.json: {e}")
        return False
    
    email_config = config.get('email', {})
    
    print("=" * 60)
    print("SIMPLE EMAIL TEST")
    print("=" * 60)
    print(f"SMTP Server: {email_config.get('smtp_server')}")
    print(f"SMTP Port: {email_config.get('smtp_port')}")
    print(f"Sender: {email_config.get('sender_email')}")
    print(f"Recipient: {email_config.get('recipient_email')}")
    print()
    
    sender_email = email_config.get('sender_email')
    sender_password = email_config.get('sender_password')
    recipient_email = email_config.get('recipient_email')
    smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
    smtp_port = email_config.get('smtp_port', 587)
    
    if not all([sender_email, sender_password, recipient_email]):
        print("ERROR: Missing email configuration")
        return False
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "TEST: Security System Email Test"
    
    body = f"""
This is a test email from your Raspberry Pi Security System.

Test Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

If you received this email, your email configuration is working correctly!
"""
    msg.attach(MIMEText(body, 'plain'))
    
    # Try to send
    print("Attempting to connect to SMTP server...")
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        print("Connected! Starting TLS...")
        server.starttls()
        print("TLS started! Attempting login...")
        server.login(sender_email, sender_password)
        print("Login successful! Sending email...")
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        print()
        print("SUCCESS! Email sent successfully!")
        print(f"Check your inbox: {recipient_email}")
        print("Also check spam/junk folder if you don't see it.")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print()
        print("ERROR: Authentication failed!")
        print(f"Details: {e}")
        print()
        print("For Gmail, make sure:")
        print("  1. You're using an App Password (16 characters)")
        print("  2. 2-Factor Authentication is enabled")
        print("  3. The password has no spaces")
        return False
    except smtplib.SMTPException as e:
        print()
        print(f"ERROR: SMTP error: {e}")
        return False
    except Exception as e:
        print()
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_email_simple()

