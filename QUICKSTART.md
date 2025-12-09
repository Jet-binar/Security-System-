# Quick Start Guide

## 1. First Time Setup (5 minutes)

### Install dependencies:
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv python3-picamera2 cmake build-essential
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure email in `config.json`:
```json
{
    "email": {
        "sender_email": "your_email@gmail.com",
        "sender_password": "your_app_password",
        "recipient_email": "alert_recipient@gmail.com"
    }
}
```

## 2. Add Authorized Faces (2 minutes)

### Option A: From existing photos
```bash
python manage_faces.py add photo.jpg -n "Person Name"
```

### Option B: Capture from camera
```bash
python manage_faces.py capture "Person Name"
```

## 3. Run Security System

```bash
python security_system.py
```

## That's it! 

The system will now:
- ✅ Recognize authorized faces (green boxes)
- ✅ Detect unauthorized persons (red boxes)
- ✅ Save photos of unauthorized persons
- ✅ Send email alerts

Press `q` or `Ctrl+C` to stop.

## Common Commands

```bash
# List authorized faces
python manage_faces.py list

# Remove a face
python manage_faces.py remove "Person Name"

# Add multiple faces
python manage_faces.py add person1.jpg -n "Alice"
python manage_faces.py add person2.jpg -n "Bob"
```

## Troubleshooting

**Email not working?**
- Use Gmail App Password (not regular password)
- Check `config.json` email settings

**No faces detected?**
- Ensure good lighting
- Face should be clearly visible
- Try: `python manage_faces.py capture "Test"` to test

**Camera not working?**
- Test with: `libcamera-hello`
- Check camera connection

