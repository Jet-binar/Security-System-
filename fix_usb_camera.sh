#!/bin/bash
# Script to fix USB camera issues on Raspberry Pi

echo "=== USB Camera Fix Script ==="
echo ""

# 1. Load UVC driver
echo "1. Loading UVC video driver..."
sudo modprobe uvcvideo
echo "   ✓ Driver loaded"

# 2. Check video devices
echo ""
echo "2. Checking video devices..."
if ls /dev/video* 1> /dev/null 2>&1; then
    echo "   Found video devices:"
    ls -l /dev/video*
else
    echo "   ⚠️  No video devices found"
fi

# 3. Check user groups
echo ""
echo "3. Checking user groups..."
if groups | grep -q video; then
    echo "   ✓ User is in 'video' group"
else
    echo "   ⚠️  User NOT in 'video' group"
    echo "   Adding user to video group..."
    sudo usermod -a -G video $USER
    echo "   ✓ User added to video group"
    echo "   ⚠️  You need to logout and login again for this to take effect"
fi

# 4. Check USB devices
echo ""
echo "4. Checking USB devices..."
lsusb | grep -i camera || echo "   No camera found in USB devices"

# 5. Check dmesg for errors
echo ""
echo "5. Recent system messages (last 10 lines):"
dmesg | tail -10

echo ""
echo "=== Done ==="
echo ""
echo "If video devices still don't appear, try:"
echo "  1. Unplug and replug the USB camera"
echo "  2. Try a different USB port (prefer USB 2.0)"
echo "  3. Reboot: sudo reboot"
echo "  4. After reboot, check: ls -l /dev/video*"

