#!/usr/bin/env python3
"""
Email notification system for security alerts
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
import datetime


class EmailSender:
    def __init__(self, config):
        """
        Initialize email sender
        
        Args:
            config: Configuration dictionary with email settings
        """
        self.config = config
        self.smtp_server = config.get('email', {}).get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('email', {}).get('smtp_port', 587)
        self.sender_email = config.get('email', {}).get('sender_email')
        self.sender_password = config.get('email', {}).get('sender_password')
        self.recipient_email = config.get('email', {}).get('recipient_email')
        
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            print("Warning: Email configuration incomplete. Email alerts will not work.")
            print("Please configure email settings in config.json")
    
    def send_alert(self, image_path, timestamp):
        """
        Send security alert email with photo
        
        Args:
            image_path: Path to the captured image
            timestamp: Timestamp string for the detection
        """
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            print("Cannot send email: Email configuration incomplete")
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = f"SECURITY ALERT: Unauthorized Person Detected - {timestamp}"
            
            # Email body
            body = f"""
SECURITY ALERT

An unauthorized person has been detected in your room.

Detection Time: {timestamp}
Location: {self.config.get('location', 'Room')}

Please review the attached image.

---
This is an automated message from your Raspberry Pi Security System.
"""
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach image
            if Path(image_path).exists():
                try:
                    with open(image_path, 'rb') as f:
                        img_data = f.read()
                        image = MIMEImage(img_data)
                        image.add_header('Content-Disposition', 
                                       f'attachment; filename="{Path(image_path).name}"')
                        msg.attach(image)
                        print(f"  Image attached: {Path(image_path).name}")
                except Exception as e:
                    print(f"  Warning: Could not attach image: {e}")
                    print(f"  Email will be sent without image attachment")
            else:
                print(f"  Warning: Image file not found: {image_path}")
                print(f"  Email will be sent without image attachment")
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, self.recipient_email, text)
            server.quit()
            
            print(f"Alert email sent to {self.recipient_email}")
        
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP Authentication Error: {e}"
            print(f"Error sending email: {error_msg}")
            print("Common causes:")
            print("  - Wrong email address or password")
            print("  - For Gmail: Make sure you're using an App Password, not your regular password")
            print("  - For Gmail: Make sure 2-Factor Authentication is enabled")
            raise
        except smtplib.SMTPException as e:
            error_msg = f"SMTP Error: {e}"
            print(f"Error sending email: {error_msg}")
            raise
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(f"Error sending email: {error_msg}")
            import traceback
            traceback.print_exc()
            raise
