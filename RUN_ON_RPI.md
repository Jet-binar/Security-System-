# Step-by-Step Guide: Running Security System on Raspberry Pi

## Prerequisites Checklist

- [ ] Raspberry Pi 5 with monitor/keyboard connected
- [ ] Camera module connected
- [ ] Internet connection
- [ ] Project files on Raspberry Pi (cloned from GitHub)

---

## Step 1: Connect to Your Raspberry Pi

### Option A: Direct Access (Monitor + Keyboard)
- Power on Raspberry Pi
- Log in to desktop
- Open Terminal application

### Option B: Via SSH (from your Windows PC)
```bash
ssh 192.168.0.110
# Enter password when prompted
```

---

## Step 2: Navigate to Project Directory

```bash
cd ~/Documents/SECURITY-System-
```

If the project is in a different location:
```bash
cd ~/Security-System-  # or wherever you cloned it
```

---

## Step 3: Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your prompt.

**If venv doesn't exist**, create it:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Step 4: Verify Dependencies Are Installed

```bash
# Check if key packages are installed
python3 -c "import cv2; import face_recognition; import picamera2; print('✓ All packages OK')"
```

**If you get import errors**, install dependencies:
```bash
# Install system packages
sudo apt install -y python3-libcamera python3-picamera2

# Install Python packages
pip install -r requirements.txt
```

**Note:** Installing `dlib` can take 10-30 minutes. Be patient!

---

## Step 5: Test Camera First

```bash
# Quick camera test
libcamera-hello --list-cameras
```

You should see your camera listed. If not:
```bash
# Enable camera
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
# Reboot: sudo reboot
```

---

## Step 6: Add Authorized Faces

### Option A: Capture from Camera
```bash
python3 manage_faces.py capture "YourName"
```

**What happens:**
- Camera window opens
- Position yourself in front of camera
- When you see green box around face, press **SPACE** to capture
- Press **ESC** to cancel

### Option B: Add from Photo File
```bash
python3 manage_faces.py add /path/to/photo.jpg -n "PersonName"
```

### Verify Faces Were Added
```bash
python3 manage_faces.py list
```

Should show your authorized faces.

---

## Step 7: Configure Email (Optional)

Edit the config file:
```bash
nano config.json
```

Update email settings:
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

Save: `Ctrl+X`, then `Y`, then `Enter`

---

## Step 8: Run Security System

### If Running on Pi Desktop (with monitor):
```bash
python3 security_system.py
```

### If Running via SSH (no display):
```bash
# Edit config.json first to disable display
nano config.json
# Change: "display": false

# Then run
python3 security_system.py
```

**What you should see:**
- Camera window opens (if display enabled)
- Your authorized face shows with **green box** and name
- Status text showing "Authorized: X | Frame: Y"
- Press **q** to quit

---

## Step 9: Test Unauthorized Detection

While security system is running:
1. Have someone else stand in front of camera (or cover your face)
2. You should see:
   - **Red box** with "UNAUTHORIZED"
   - Terminal message: "⚠️ UNAUTHORIZED PERSON DETECTED!"
   - Photo saved in `unauthorized_detections/` folder
   - Email sent (if configured)

---

## Step 10: Check Results

```bash
# View authorized faces
ls -la authorized_faces/

# View unauthorized detections
ls -la unauthorized_detections/

# View latest unauthorized photo
ls -lt unauthorized_detections/ | head -5
```

---

## Quick Command Reference

```bash
# 1. Navigate to project
cd ~/Documents/SECURITY-System-

# 2. Activate venv
source venv/bin/activate

# 3. Add face
python3 manage_faces.py capture "Name"

# 4. List faces
python3 manage_faces.py list

# 5. Run security system
python3 security_system.py
```

---

## Troubleshooting

### Camera not detected
```bash
sudo raspi-config  # Enable camera
sudo reboot
```

### Import errors
```bash
source venv/bin/activate  # Make sure venv is active
pip install --force-reinstall -r requirements.txt
```

### Display errors (SSH)
- Run directly on Pi desktop, OR
- Set `"display": false` in config.json

### Face not detected
- Ensure good lighting
- Face should be clearly visible
- Try adjusting `face_recognition_tolerance` in config.json (lower = stricter)

### System too slow
- Lower resolution in config.json: `"camera_resolution": [640, 480]`
- Increase `"process_every_n_frames": 5`

---

## Running in Background

To run security system continuously:

```bash
# Using nohup
nohup python3 security_system.py > security.log 2>&1 &

# Check if running
ps aux | grep security_system

# View logs
tail -f security.log

# Stop it
pkill -f security_system.py
```

---

## Next Steps After Testing

1. ✅ Camera works
2. ✅ Can add faces
3. ✅ Security system runs
4. ✅ Recognizes authorized faces
5. ✅ Detects unauthorized persons
6. ✅ Saves photos
7. ✅ Sends emails (if configured)

**Your security system is ready to use!**

