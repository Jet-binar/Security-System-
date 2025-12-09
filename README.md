# Raspberry Pi 5 Security System with Hailo Card and RPi Camera

A comprehensive security system that uses face recognition to identify authorized persons and automatically captures photos and sends email alerts for unauthorized access. Includes voice features for future expansion.

## Features

- ✅ **Face Recognition**: Recognizes authorized faces from a database
- ✅ **Unauthorized Detection**: Automatically detects and captures photos of unauthorized persons
- ✅ **Email Alerts**: Sends email notifications with photos when unauthorized access is detected
- ✅ **Voice Announcements**: Optional text-to-speech announcements (ready for future voice features)
- ✅ **Easy Face Management**: Command-line tools to add/remove authorized faces
- ✅ **Hailo AI Support**: Ready for Hailo accelerator card integration

## Hardware Requirements

- Raspberry Pi 5
- Hailo AI accelerator card (Hailo-8L or compatible) - Optional
- Raspberry Pi Camera Module (v2 or v3)
- Compatible camera ribbon cable
- Microphone and speaker (for voice features)

## Software Requirements

- Raspberry Pi OS (64-bit recommended)
- Python 3.9+
- Hailo runtime libraries (optional, for Hailo acceleration)
- picamera2 library for camera access

## Installation

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv python3-picamera2
sudo apt install -y cmake build-essential
sudo apt install -y libopenblas-dev liblapack-dev
```

### 2. Install Face Recognition Dependencies

The `face_recognition` library requires `dlib`, which needs to be compiled:

```bash
# Install dlib dependencies
sudo apt install -y python3-dev python3-setuptools
pip3 install dlib
pip3 install face_recognition
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Email Settings

Edit `config.json` and set up your email credentials:

```json
{
    "email": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your_email@gmail.com",
        "sender_password": "your_app_password",
        "recipient_email": "recipient@gmail.com"
    }
}
```

**For Gmail**: You'll need to use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

## Usage

### Setting Up Authorized Faces

#### Option 1: Add faces from image files

```bash
python manage_faces.py add path/to/person_photo.jpg -n "John Doe"
```

#### Option 2: Capture face directly from camera

```bash
python manage_faces.py capture "John Doe"
```

This will open the camera and let you capture a face directly.

#### List all authorized faces

```bash
python manage_faces.py list
```

#### Remove an authorized face

```bash
python manage_faces.py remove "John Doe"
```

### Running the Security System

```bash
python security_system.py
```

The system will:
- Monitor the camera feed
- Recognize authorized faces (shown in green)
- Detect unauthorized persons (shown in red)
- Capture photos of unauthorized persons
- Send email alerts with photos
- Optionally announce via voice (if enabled)

Press `q` to quit or `Ctrl+C` to stop.

### Configuration

Edit `config.json` to customize:

- `camera_resolution`: Camera resolution [width, height]
- `faces_directory`: Directory storing authorized face images
- `unauthorized_directory`: Directory for captured unauthorized photos
- `face_recognition_tolerance`: Lower = stricter (0.4-0.6 recommended)
- `detection_cooldown`: Seconds between email alerts (prevents spam)
- `enable_voice`: Enable/disable voice announcements
- `email`: Email configuration

## Project Structure

```
hailo-rpi5-examples/
├── security_system.py      # Main security system
├── manage_faces.py         # Face database management utility
├── email_sender.py         # Email notification system
├── voice_features.py       # Voice announcements (future features)
├── config.py               # Configuration management
├── config.json             # Configuration file
├── camera_hailo_example.py # Original Hailo example
├── requirements.txt        # Python dependencies
├── authorized_faces/       # Directory for authorized face images (created automatically)
└── unauthorized_detections/ # Directory for captured unauthorized photos (created automatically)
```

## Voice Features (Future Expansion)

The system includes a voice module ready for future features:

- ✅ Text-to-speech announcements
- 🔄 Voice recognition (to be implemented)
- 🔄 Interactive responses (to be implemented)

To enable voice features, set `"enable_voice": true` in `config.json`.

The system will announce:
- "Who are you?"
- "What are you doing in my room?"
- "You are not authorized to be here."
- "Security alert activated."

## Troubleshooting

### Face Recognition Not Working

- Ensure faces are clearly visible in the images
- Use good lighting
- Try adjusting `face_recognition_tolerance` in config.json
- Make sure `dlib` is properly installed

### Email Not Sending

- Check your email credentials in `config.json`
- For Gmail, use an App Password, not your regular password
- Check firewall settings for SMTP port 587
- Verify internet connection

### Camera Not Detected

- Ensure camera is properly connected
- Check camera ribbon cable
- Try: `libcamera-hello` to test camera
- Verify camera is enabled: `sudo raspi-config` → Interface Options → Camera

### Performance Issues

- Increase `process_every_n_frames` in config.json (processes fewer frames)
- Lower camera resolution
- Use Hailo accelerator card for better performance

## Security Considerations

- Store authorized face images securely
- Use strong email passwords/app passwords
- Consider encrypting stored photos
- Regularly review unauthorized detection logs
- Keep system updated

## License

This project is provided as-is for educational and personal use.

## Notes

- The system processes frames every N frames for performance (configurable)
- Face database is reloaded periodically to pick up new faces
- Email alerts have a cooldown period to prevent spam
- Unauthorized photos are saved locally for review
- Hailo card integration is optional - system works with CPU-based face recognition
