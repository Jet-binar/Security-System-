#!/usr/bin/env python3
"""
Test script to diagnose USB camera issues on Raspberry Pi
Run this to check if your USB webcam is detected and working
"""

import cv2
import sys

def test_camera(index):
    """Test a specific camera index"""
    print(f"\nTesting camera index {index}...")
    cap = cv2.VideoCapture(index)
    
    if not cap.isOpened():
        print(f"  ❌ Camera {index}: Could not open")
        return False
    
    print(f"  ✓ Camera {index}: Opened successfully")
    
    # Try to read a frame
    ret, frame = cap.read()
    if not ret or frame is None:
        print(f"  ❌ Camera {index}: Could not capture frame")
        cap.release()
        return False
    
    print(f"  ✓ Camera {index}: Frame captured successfully")
    print(f"    Frame size: {frame.shape[1]}x{frame.shape[0]}")
    
    # Get camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print(f"    Properties: {width}x{height} @ {fps} FPS")
    
    cap.release()
    return True

def main():
    print("=" * 60)
    print("USB Camera Diagnostic Tool")
    print("=" * 60)
    
    # Check system devices
    print("\n1. Checking system for video devices...")
    import subprocess
    try:
        result = subprocess.run(['ls', '/dev/video*'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("  Found video devices:")
            for line in result.stdout.strip().split('\n'):
                print(f"    {line}")
        else:
            print("  ⚠️  No /dev/video* devices found")
    except:
        print("  ⚠️  Could not check /dev/video* devices")
    
    # Check USB devices
    print("\n2. Checking USB devices...")
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        if result.returncode == 0:
            print("  USB devices:")
            for line in result.stdout.strip().split('\n'):
                if 'camera' in line.lower() or 'webcam' in line.lower() or 'video' in line.lower():
                    print(f"    {line}")
        else:
            print("  ⚠️  Could not list USB devices")
    except:
        print("  ⚠️  Could not check USB devices")
    
    # Test camera indices
    print("\n3. Testing camera indices...")
    working_cameras = []
    
    for i in range(4):  # Test indices 0-3
        if test_camera(i):
            working_cameras.append(i)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if working_cameras:
        print(f"✓ Found {len(working_cameras)} working camera(s) at index(es): {working_cameras}")
        print(f"\nRecommended: Use index {working_cameras[0]} in config.json:")
        print(f'  "usb_camera_index": {working_cameras[0]}')
    else:
        print("❌ No working cameras found!")
        print("\nTroubleshooting:")
        print("  1. Make sure USB camera is connected")
        print("  2. Check USB cable connection")
        print("  3. Try a different USB port")
        print("  4. Check if camera works on another computer")
        print("  5. Make sure no other application is using the camera")
        print("  6. Try: sudo modprobe v4l2loopback (if using virtual camera)")
        sys.exit(1)

if __name__ == "__main__":
    main()

