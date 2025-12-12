#!/usr/bin/env python3
"""
Debug script to test unauthorized detection and alert sending
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from security_system import SecuritySystem
import cv2
import numpy as np
import time

def test_unauthorized_alert():
    """Test if unauthorized alert system works"""
    
    print("=" * 60)
    print("UNAUTHORIZED ALERT DEBUG TEST")
    print("=" * 60)
    
    # Initialize system
    print("\n1. Initializing security system...")
    try:
        system = SecuritySystem()
        print("   ✓ System initialized")
        print(f"   - Authorized faces loaded: {len(system.known_faces)}")
        print(f"   - Unauthorized directory: {system.unauthorized_dir}")
        print(f"   - Unauthorized delay: {system.unauthorized_delay} seconds")
    except Exception as e:
        print(f"   ✗ Error initializing: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check directory exists
    print(f"\n2. Checking unauthorized_detections folder...")
    if system.unauthorized_dir.exists():
        print(f"   ✓ Folder exists: {system.unauthorized_dir}")
        print(f"   - Absolute path: {system.unauthorized_dir.absolute()}")
        
        # Check if writable
        test_file = system.unauthorized_dir / "test_write.txt"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print("   ✓ Folder is writable")
        except Exception as e:
            print(f"   ✗ Folder is NOT writable: {e}")
            print(f"   - Check permissions: chmod 755 {system.unauthorized_dir}")
    else:
        print(f"   ✗ Folder does not exist: {system.unauthorized_dir}")
        print(f"   - Trying to create it...")
        try:
            system.unauthorized_dir.mkdir(parents=True, exist_ok=True)
            print(f"   ✓ Folder created")
        except Exception as e:
            print(f"   ✗ Cannot create folder: {e}")
    
    # Check email configuration
    print(f"\n3. Checking email configuration...")
    email_config = system.config.get('email', {})
    sender = email_config.get('sender_email')
    password = email_config.get('sender_password')
    recipient = email_config.get('recipient_email')
    
    if sender and password and recipient:
        print(f"   ✓ Email configured")
        print(f"   - Sender: {sender}")
        print(f"   - Recipient: {recipient}")
    else:
        print(f"   ✗ Email NOT configured")
        print(f"   - Missing: sender={bool(sender)}, password={bool(password)}, recipient={bool(recipient)}")
    
    # Test direct alert sending
    print(f"\n4. Testing direct alert sending...")
    try:
        # Create a test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame[:] = (100, 150, 200)  # Light blue
        cv2.putText(test_frame, "TEST FRAME", (200, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Test face location (fake)
        test_location = (100, 500, 300, 300)  # top, right, bottom, left
        
        print(f"   - Calling send_unauthorized_alert()...")
        system.send_unauthorized_alert(test_frame, test_location, 999, "TEST")
        print(f"   ✓ Alert function completed")
        
        # Check if file was created
        import glob
        files = list(system.unauthorized_dir.glob("unauthorized_*.jpg"))
        if files:
            latest = max(files, key=lambda p: p.stat().st_mtime)
            print(f"   ✓ Photo file created: {latest}")
            print(f"   - File size: {latest.stat().st_size} bytes")
        else:
            print(f"   ✗ No photo files found in {system.unauthorized_dir}")
        
    except Exception as e:
        print(f"   ✗ Error in send_unauthorized_alert: {e}")
        import traceback
        traceback.print_exc()
    
    # Check face tracking logic
    print(f"\n5. Checking face tracking configuration...")
    print(f"   - unauthorized_delay: {system.unauthorized_delay} seconds")
    print(f"   - repeat_offender_delay: {system.repeat_offender_delay} seconds")
    print(f"   - detection_cooldown: {system.detection_cooldown} seconds")
    print(f"   - unauthorized_memory_time: {system.unauthorized_memory_time} seconds")
    
    print(f"\n" + "=" * 60)
    print("DEBUG TEST COMPLETE")
    print("=" * 60)
    print("\nTo test the full system:")
    print("1. Run: python3 security_system.py")
    print("2. Have an unauthorized person stand in front of camera")
    print("3. Wait 5+ seconds")
    print("4. Check console for:")
    print("   - '⚠️ UNAUTHORIZED PERSON DETECTED!'")
    print("   - 'Photo saved: ...'")
    print("   - 'Alert email sent successfully'")
    print("5. Check folder:", system.unauthorized_dir.absolute())
    print("6. Check your email inbox")

if __name__ == "__main__":
    test_unauthorized_alert()

