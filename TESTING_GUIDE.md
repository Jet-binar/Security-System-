# Testing Guide for Security System

This guide will help you test your security system step by step.

## Prerequisites

1. Raspberry Pi 5 with camera connected
2. SSH access to Raspberry Pi
3. Project files on Raspberry Pi

## Step 1: Clone/Transfer Project to Raspberry Pi

### Option A: Clone from GitHub
```bash
cd ~
git clone https://github.com/Jet-binar/Security-System-.git
cd Security-System-
```

### Option B: If already transferred via SCP
```bash
cd ~/security_system
# or wherever you copied the files
```

## Step 2: Install Dependencies

```bash
# Update system
sudo apt update

# Install system dependencies
sudo apt install -y python3-pip python3-venv python3-picamera2
sudo apt install -y cmake build-essential libopenblas-dev liblapack-dev
sudo apt install -y python3-dev python3-setuptools

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** Installing `dlib` and `face_recognition` can take 10-30 minutes. Be patient!

## Step 3: Test Camera

```bash
# Test if camera is detected
libcamera-hello --list-cameras

# Take a test photo
libcamera-jpeg -o test.jpg

# If camera works, you should see test.jpg created
ls -la test.jpg
```

## Step 4: Test Face Management

### Test adding a face from camera:
```bash
python3 manage_faces.py capture "TestPerson"
```

This will:
- Open camera preview
- Detect your face
- Press SPACE to capture
- Save to `authorized_faces/TestPerson.jpg`

### Test listing faces:
```bash
python3 manage_faces.py list
```

Should show:
```
Authorized Faces (1):
----------------------------------------
  - TestPerson
```

### Test adding face from image file:
```bash
# If you have a photo file
python3 manage_faces.py add /path/to/photo.jpg -n "PersonName"
```

## Step 5: Configure Email (Optional for Testing)

Edit `config.json`:
```json
{
    "email": {
        "sender_email": "your_email@gmail.com",
        "sender_password": "your_app_password",
        "recipient_email": "recipient@gmail.com"
    }
}
```

**For Gmail:** Use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

## Step 6: Test Security System

### Basic Test (without email):
```bash
# Make sure you're in the project directory
cd ~/Security-System-  # or your project path
source venv/bin/activate

# Run the security system
python3 security_system.py
```

**What to expect:**
- Camera feed should open
- Your authorized face should show with green box and name
- If someone unauthorized appears, red box with "UNAUTHORIZED"
- Press `q` to quit

### Test with Unauthorized Person:
1. Add your face as authorized (Step 4)
2. Run security system
3. Have someone else (or cover your face) stand in front of camera
4. System should:
   - Show red box
   - Save photo to `unauthorized_detections/` folder
   - Send email (if configured)

## Step 7: Verify Files Created

```bash
# Check authorized faces
ls -la authorized_faces/

# Check unauthorized detections
ls -la unauthorized_detections/

# Should see captured photos
```

## Step 8: Test Email (If Configured)

To test email without waiting for unauthorized person:

```bash
# Create a test script
cat > test_email.py << 'EOF'
from email_sender import EmailSender
import config

cfg = config.load_config()
sender = EmailSender(cfg)

# Create a dummy image path (or use existing)
import os
test_image = "test.jpg"  # or any image file
if os.path.exists(test_image):
    sender.send_alert(test_image, "20250101_120000")
    print("Test email sent!")
else:
    print("Create test.jpg first with: libcamera-jpeg -o test.jpg")
EOF

python3 test_email.py
```

## Troubleshooting

### Camera not detected:
```bash
# Enable camera in raspi-config
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable

# Reboot
sudo reboot
```

### Face recognition not working:
- Ensure good lighting
- Face should be clearly visible
- Try adjusting tolerance in `config.json`: `"face_recognition_tolerance": 0.5` (lower = stricter)

### Import errors:
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall packages
pip install --force-reinstall -r requirements.txt
```

### Performance issues:
- Lower camera resolution in `config.json`
- Increase `process_every_n_frames` (processes fewer frames)

## Quick Test Checklist

- [ ] Camera works (`libcamera-hello`)
- [ ] Dependencies installed (`pip list | grep face`)
- [ ] Can add face (`manage_faces.py capture`)
- [ ] Can list faces (`manage_faces.py list`)
- [ ] Security system runs (`python3 security_system.py`)
- [ ] Recognizes authorized face (green box)
- [ ] Detects unauthorized (red box)
- [ ] Saves unauthorized photos
- [ ] Sends email (if configured)

## Running in Background

To run security system continuously:

```bash
# Using nohup
nohup python3 security_system.py > security.log 2>&1 &

# Or using screen
screen -S security
python3 security_system.py
# Press Ctrl+A then D to detach
# Reattach with: screen -r security
```

## View Logs

```bash
# If using nohup
tail -f security.log

# Check system status
ps aux | grep security_system
```

