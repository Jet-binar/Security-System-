# Quick Test Guide - Security System

Follow these steps to test your security system on Raspberry Pi.

## Step 1: Verify Installation

```bash
# Make sure you're in the project directory
cd ~/Documents/SECURITY-System-  # or wherever you cloned it

# Activate virtual environment
source venv/bin/activate

# Check if packages are installed
python3 -c "import cv2; import face_recognition; import picamera2; print('All packages OK!')"
```

If you see "All packages OK!" - proceed. If errors, install missing packages.

## Step 2: Test Camera

```bash
# Test if camera is detected
libcamera-hello --list-cameras

# Take a test photo
libcamera-jpeg -o test.jpg

# Check if photo was created
ls -la test.jpg
```

If camera works, you'll see the photo file created.

## Step 3: Add Your Face (First Test)

```bash
# Make sure virtual environment is active
source venv/bin/activate

# Capture your face
python3 manage_faces.py capture "YourName"
```

**What happens:**
- Camera window opens
- Position yourself in front of camera
- When you see green box around your face, press **SPACE** to capture
- Press **ESC** to cancel

**Expected result:**
```
✓ Face captured and saved: authorized_faces/YourName.jpg
```

## Step 4: Verify Face Was Added

```bash
# List all authorized faces
python3 manage_faces.py list
```

**Expected output:**
```
Authorized Faces (1):
----------------------------------------
  - YourName
```

## Step 5: Run Security System

```bash
# Make sure virtual environment is active
source venv/bin/activate

# Run the security system
python3 security_system.py
```

**What you should see:**
- Camera window opens showing live feed
- Your face should have a **green box** with your name
- Status text at top showing "Authorized: 1 | Frame: X"
- Press **q** to quit

## Step 6: Test Unauthorized Detection

1. Keep security system running
2. Have someone else stand in front of camera (or cover your face)
3. You should see:
   - **Red box** with "UNAUTHORIZED" text
   - Message in terminal: "⚠️  UNAUTHORIZED PERSON DETECTED!"
   - Photo saved in `unauthorized_detections/` folder
   - Email sent (if configured)

## Step 7: Check Saved Files

```bash
# Check authorized faces
ls -la authorized_faces/

# Check unauthorized detections
ls -la unauthorized_detections/
```

You should see:
- `authorized_faces/YourName.jpg` - Your authorized face
- `unauthorized_detections/unauthorized_YYYYMMDD_HHMMSS.jpg` - Unauthorized photos

## Troubleshooting

### Camera not working?
```bash
# Enable camera
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
# Reboot: sudo reboot
```

### Face not detected?
- Ensure good lighting
- Face should be clearly visible
- Try adjusting in config.json: `"face_recognition_tolerance": 0.5` (lower = stricter)

### Import errors?
```bash
# Make sure virtual environment is active
source venv/bin/activate

# Reinstall if needed
pip install --force-reinstall face-recognition opencv-python picamera2
```

### System too slow?
- Lower camera resolution in `config.json`: `"camera_resolution": [640, 480]`
- Increase `"process_every_n_frames": 5` (processes every 5th frame)

### Want faster checking/more frequent detection?
- Increase `"camera_fps": 9` (default is 9, can go up to 30-60 for some cameras)
- Decrease `"process_every_n_frames": 2` (lower number = checks more frames, default is now 2)
- Note: Lower `process_every_n_frames` values will use more CPU but check more often

## Quick Test Checklist

Run through this checklist:

- [ ] Camera works (`libcamera-hello`)
- [ ] Can import packages (Step 1)
- [ ] Can capture face (`manage_faces.py capture`)
- [ ] Can list faces (`manage_faces.py list`)
- [ ] Security system runs (`python3 security_system.py`)
- [ ] Recognizes authorized face (green box with name)
- [ ] Detects unauthorized (red box)
- [ ] Saves unauthorized photos
- [ ] Email works (if configured)

## Test Email (Optional)

If you configured email, test it:

```bash
# Create a simple test
python3 << 'EOF'
from email_sender import EmailSender
import config

cfg = config.load_config()
sender = EmailSender(cfg)

# Use the test photo we created earlier
import os
if os.path.exists("test.jpg"):
    sender.send_alert("test.jpg", "20250101_120000")
    print("✓ Test email sent!")
else:
    print("Create test.jpg first: libcamera-jpeg -o test.jpg")
EOF
```

## Success Indicators

✅ **System is working if:**
- Camera feed shows in window
- Your face is recognized (green box)
- Unauthorized person triggers red box
- Photos are saved correctly
- No error messages in terminal

❌ **If something doesn't work:**
- Check error messages in terminal
- Verify camera is enabled
- Ensure virtual environment is activated
- Check file permissions

