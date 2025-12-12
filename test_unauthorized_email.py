#!/usr/bin/env python3
"""
Quick test to capture an unauthorized photo and send it via email
"""

import cv2
import numpy as np
import datetime
from pathlib import Path
from security_system import SecuritySystem
import time

def test_unauthorized_alert():
    """Test unauthorized alert with real camera capture"""
    
    print("=" * 60)
    print("UNAUTHORIZED ALERT TEST")
    print("=" * 60)
    
    # Initialize system
    print("\n1. Initializing security system...")
    try:
        system = SecuritySystem()
        print("   ✓ System initialized")
        print(f"   - Unauthorized directory: {system.unauthorized_dir}")
        print(f"   - Email configured: {bool(system.email_sender.sender_email)}")
    except Exception as e:
        print(f"   ✗ Error initializing: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Capture a frame from camera
    print("\n2. Capturing frame from camera...")
    print("   (Make sure you're in front of the camera)")
    print("   Waiting 3 seconds for camera to stabilize...")
    time.sleep(3)
    
    try:
        # Capture frame from camera
        frame_rgb = system.camera.capture_array()
        if frame_rgb is None:
            print("   ✗ Failed to capture frame from camera")
            return
        
        # Convert RGB to BGR for OpenCV
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        
        print(f"   ✓ Frame captured: {frame.shape}")
        
        # Create a fake face location (you can adjust these coordinates)
        # This simulates a face detection in the center of the frame
        height, width = frame.shape[:2]
        face_top = int(height * 0.3)
        face_bottom = int(height * 0.7)
        face_left = int(width * 0.3)
        face_right = int(width * 0.7)
        face_location = (face_top, face_right, face_bottom, face_left)
        
        print(f"   - Face location: top={face_top}, right={face_right}, bottom={face_bottom}, left={face_left}")
        
        # Send unauthorized alert
        print("\n3. Sending unauthorized alert...")
        print("   (This will save a photo and send an email)")
        
        system.send_unauthorized_alert(frame, face_location, 999, "TEST")
        
        print("\n4. Checking results...")
        
        # Check if photo was saved
        files = list(system.unauthorized_dir.glob("unauthorized_*.jpg"))
        if files:
            latest = max(files, key=lambda p: p.stat().st_mtime)
            print(f"   ✓ Photo saved: {latest.name}")
            print(f"   - File size: {latest.stat().st_size} bytes")
            print(f"   - Full path: {latest.absolute()}")
        else:
            print("   ✗ No photo files found")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        print("\nCheck:")
        print("1. The photo file in:", system.unauthorized_dir.absolute())
        print("2. Your email inbox for the alert")
        print("\nIf email wasn't received, check:")
        print("- Console output above for any error messages")
        print("- Run: python3 simple_email_test.py")
        
    except Exception as e:
        print(f"   ✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up camera
        if system.camera:
            system.camera.stop()
            print("\n   Camera stopped")

if __name__ == "__main__":
    test_unauthorized_alert()

