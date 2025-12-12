#!/usr/bin/env python3
"""
Test script to verify email configuration and sending
"""

import json
from email_sender import EmailSender
from pathlib import Path
import datetime

def test_email():
    """Test email sending with current configuration"""
    
    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config.json: {e}")
        return
    
    # Check email configuration
    email_config = config.get('email', {})
    print("=" * 60)
    print("EMAIL CONFIGURATION CHECK")
    print("=" * 60)
    print(f"SMTP Server: {email_config.get('smtp_server')}")
    print(f"SMTP Port: {email_config.get('smtp_port')}")
    print(f"Sender Email: {email_config.get('sender_email')}")
    print(f"Sender Password: {'*' * len(email_config.get('sender_password', ''))} ({len(email_config.get('sender_password', ''))} chars)")
    print(f"Recipient Email: {email_config.get('recipient_email')}")
    print()
    
    # Validate configuration
    required_fields = ['smtp_server', 'smtp_port', 'sender_email', 'sender_password', 'recipient_email']
    missing_fields = [field for field in required_fields if not email_config.get(field)]
    
    if missing_fields:
        print("❌ ERROR: Missing required email fields:")
        for field in missing_fields:
            print(f"   - {field}")
        return
    
    # Check if password looks like placeholder
    password = email_config.get('sender_password', '')
    if 'your' in password.lower() or 'password' in password.lower() or len(password) < 10:
        print("⚠️  WARNING: Password might be a placeholder. Make sure you're using a real app password!")
        print()
    
    # Initialize email sender
    print("Initializing EmailSender...")
    try:
        email_sender = EmailSender(config)
    except Exception as e:
        print(f"❌ Error initializing EmailSender: {e}")
        return
    
    # Create a test image
    print("\nCreating test image...")
    test_image_path = Path("test_email_image.jpg")
    
    # Create a simple test image using OpenCV or PIL
    try:
        import cv2
        import numpy as np
        # Create a simple colored image
        test_img = np.zeros((480, 640, 3), dtype=np.uint8)
        test_img[:] = (100, 150, 200)  # Light blue color
        cv2.putText(test_img, "TEST EMAIL", (200, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        cv2.putText(test_img, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                   (150, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imwrite(str(test_image_path), test_img)
        print(f"✓ Test image created: {test_image_path}")
    except ImportError:
        print("WARNING: OpenCV not available, creating dummy file...")
        test_image_path.write_bytes(b'fake image data')
    except Exception as e:
        print(f"⚠️  Could not create test image: {e}")
        print("   Will try to send email anyway...")
    
    # Test sending email
    print("\n" + "=" * 60)
    print("ATTEMPTING TO SEND TEST EMAIL")
    print("=" * 60)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        email_sender.send_alert(str(test_image_path), timestamp)
        print("\n✅ Email sent successfully!")
        print(f"   Check your inbox: {email_config.get('recipient_email')}")
        print("   Also check your spam/junk folder if you don't see it.")
    except Exception as e:
        print(f"\n❌ ERROR sending email: {e}")
        print("\nCommon issues:")
        print("1. Gmail App Password: Make sure you're using a 16-character app password, not your regular password")
        print("2. 2FA Required: Gmail requires 2-Factor Authentication to be enabled")
        print("3. Network: Check your internet connection")
        print("4. Firewall: Port 587 might be blocked")
        print("5. Wrong credentials: Double-check email and password")
        import traceback
        print("\nFull error details:")
        traceback.print_exc()
    
    # Cleanup
    if test_image_path.exists() and test_image_path.name.startswith('test_'):
        try:
            test_image_path.unlink()
            print(f"\n✓ Cleaned up test image")
        except:
            pass

if __name__ == "__main__":
    test_email()

