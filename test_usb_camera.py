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
    import os
    try:
        # Try ls command first
        result = subprocess.run(['ls', '/dev/video*'], capture_output=True, text=True, shell=True)
        if result.returncode == 0 and result.stdout.strip():
            print("  Found video devices:")
            for line in result.stdout.strip().split('\n'):
                print(f"    {line}")
        else:
            # Try checking if video devices exist with glob
            import glob
            video_devices = glob.glob('/dev/video*')
            if video_devices:
                print("  Found video devices:")
                for device in video_devices:
                    # Check permissions
                    perms = os.stat(device)
                    print(f"    {device} (permissions: {oct(perms.st_mode)[-3:]})")
            else:
                print("  ⚠️  No /dev/video* devices found")
                print("\n  This is likely a permissions or driver issue.")
                print("  Try these commands:")
                print("    sudo modprobe uvcvideo")
                print("    ls -l /dev/video*")
    except Exception as e:
        print(f"  ⚠️  Could not check /dev/video* devices: {e}")
    
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
        print("\nTroubleshooting steps:")
        print("\n1. Load USB video driver:")
        print("   sudo modprobe uvcvideo")
        print("\n2. Check if video devices appear:")
        print("   ls -l /dev/video*")
        print("\n3. Check camera permissions:")
        print("   groups  # Should include 'video' group")
        print("   If not, run: sudo usermod -a -G video $USER")
        print("   Then logout and login again")
        print("\n4. Check if camera needs different backend:")
        print("   Try: v4l2-ctl --list-devices")
        print("\n5. Try different USB port (USB 2.0 recommended)")
        print("\n6. Check dmesg for errors:")
        print("   dmesg | tail -20")
        print("\n7. If still not working, use Pi Camera:")
        print('   Edit config.json: "camera_type": "pi_camera"')
        sys.exit(1)

if __name__ == "__main__":
    main()

