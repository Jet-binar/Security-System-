# Testing Guide for Security System

This guide will help you test all the features of your security system.

## 1. Test Email Functionality

### On Your Local Machine (Windows):

```bash
python simple_email_test.py
```

**Expected Output:**
```
============================================================
SIMPLE EMAIL TEST
============================================================
SMTP Server: smtp.gmail.com
SMTP Port: 587
Sender: consultingjetmir@gmail.com
Recipient: consultingjetmir@gmail.com

Attempting to connect to SMTP server...
Connected! Starting TLS...
TLS started! Attempting login...
Login successful! Sending email...

SUCCESS! Email sent successfully!
Check your inbox: consultingjetmir@gmail.com
Also check spam/junk folder if you don't see it.
```

**What to Check:**
- ✅ Email appears in your inbox (check spam folder too)
- ✅ Email subject: "TEST: Security System Email Test"
- ✅ Email contains test message

### On Raspberry Pi:

```bash
cd ~/Documents/SECURITY-System-
source venv/bin/activate  # If using virtual environment
python3 simple_email_test.py
```

## 2. Test Full Security System

### On Raspberry Pi:

```bash
cd ~/Documents/SECURITY-System-
source venv/bin/activate  # If using virtual environment
python3 security_system.py
```

### What to Test:

#### Test 1: Authorized Person Detection
1. **Setup:** Add yourself to authorized faces first:
   ```bash
   python3 manage_faces.py --add "Your Name"
   ```
   Follow the prompts to capture your face.

2. **Test:** Stand in front of the camera
   - ✅ Should see "Authorized: Your Name" on screen
   - ✅ No email should be sent
   - ✅ Green box around your face

#### Test 2: Unauthorized Person Detection
1. **Setup:** Have someone NOT in the authorized list stand in front of camera

2. **Test:** 
   - ✅ After 5 seconds, you should see:
     - Red box around the face
     - "⚠️ UNAUTHORIZED PERSON DETECTED!" message
     - "Photo saved: unauthorized_YYYYMMDD_HHMMSS.jpg"
     - "Alert email sent successfully"
   - ✅ Check your email for the alert with photo attached
   - ✅ Photo should be saved in `unauthorized_detections/` folder

#### Test 3: Repeat Offender Detection
1. **Setup:** Same unauthorized person from Test 2

2. **Test:**
   - ✅ Person leaves camera view
   - ✅ Person returns after a few minutes
   - ✅ Alert should trigger after only **1 second** (not 5 seconds)
   - ✅ Email should be sent faster

#### Test 4: Motion Detection
1. **Setup:** Ensure `motion_detection_enabled: true` in config.json

2. **Test:**
   - ✅ When no motion: System scans less frequently (every 40 frames)
   - ✅ When motion detected: System scans more frequently (every 20 frames)
   - ✅ Camera feed should remain smooth

## 3. Verify Email Configuration

### Check config.json:

```bash
cat config.json | grep -A 5 email
```

**Should show:**
```json
"email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "consultingjetmir@gmail.com",
    "sender_password": "dkvvsempreyldobe",
    "recipient_email": "consultingjetmir@gmail.com"
}
```

## 4. Test Camera Feed

### Check camera is working:

```bash
python3 -c "from picamera2 import Picamera2; import time; cam = Picamera2(); cam.start(); time.sleep(2); cam.stop(); print('Camera OK')"
```

**Expected:** "Camera OK" message

## 5. Test Face Recognition

### Check if faces are loaded:

When you run `security_system.py`, look for:
```
Loading authorized faces...
Loaded 1 authorized face(s)
```

If you see "Loaded 0 authorized face(s)", add faces first:
```bash
python3 manage_faces.py --add "Test Person"
```

## 6. Troubleshooting Tests

### Email Not Sending?

1. **Test email connection:**
   ```bash
   python3 simple_email_test.py
   ```

2. **Check error messages:**
   - "SMTP Authentication Error" → Check app password
   - "Connection refused" → Check internet/firewall
   - "Email configuration incomplete" → Check config.json

3. **Verify Gmail settings:**
   - ✅ 2-Factor Authentication enabled
   - ✅ App Password generated (16 characters, no spaces)
   - ✅ App Password entered correctly in config.json

### Camera Not Working?

1. **Check camera connection:**
   ```bash
   libcamera-hello --list-cameras
   ```

2. **Test camera capture:**
   ```bash
   libcamera-still -o test.jpg
   ```

3. **Check permissions:**
   ```bash
   groups | grep video
   ```
   If not in video group: `sudo usermod -a -G video $USER` (then logout/login)

### Face Recognition Not Working?

1. **Check if faces are loaded:**
   - Look for "Loaded X authorized face(s)" message
   - Check `authorized_faces/` folder has `.jpg` files

2. **Test face detection:**
   - Make sure face is clearly visible
   - Good lighting helps
   - Face should be facing camera directly

3. **Check console output:**
   - Look for "Recognized:" or "Unrecognized:" messages
   - Check for any error messages

## 7. Performance Testing

### Monitor System Resources:

```bash
# In another terminal while security_system.py is running
htop
# or
top
```

**What to check:**
- ✅ CPU usage should be reasonable (< 80% on average)
- ✅ Memory usage should be stable
- ✅ Camera feed should be smooth (no stuttering)

### Check Processing Speed:

Watch the console output for:
- Frame processing messages
- "Processing frame..." messages
- Time between detections

## 8. Integration Test (Full Workflow)

### Complete Test Scenario:

1. **Start the system:**
   ```bash
   python3 security_system.py
   ```

2. **Test sequence:**
   - ✅ Authorized person appears → No alert
   - ✅ Unauthorized person appears → Wait 5 seconds → Email sent
   - ✅ Unauthorized person leaves
   - ✅ Same unauthorized person returns → Wait 1 second → Email sent (repeat offender)
   - ✅ Authorized person appears again → No alert

3. **Verify results:**
   - ✅ Check email inbox for alerts
   - ✅ Check `unauthorized_detections/` folder for saved photos
   - ✅ Check console for all expected messages

## 9. Quick Test Checklist

- [ ] Email test script runs successfully
- [ ] Email received in inbox
- [ ] Camera feed displays smoothly
- [ ] Authorized faces are recognized
- [ ] Unauthorized faces trigger alerts after 5 seconds
- [ ] Repeat offenders trigger alerts after 1 second
- [ ] Photos are saved correctly
- [ ] Emails include photo attachments
- [ ] System runs without crashes
- [ ] Performance is acceptable (smooth camera feed)

## 10. Common Issues and Solutions

### Issue: "Email configuration incomplete"
**Solution:** Check config.json has all email fields filled

### Issue: "Cannot send email: Email configuration incomplete"
**Solution:** Verify sender_email, sender_password, and recipient_email are set

### Issue: Camera stuttering
**Solution:** 
- Lower resolution in config.json
- Increase `process_every_n_frames` value
- Check system resources (CPU/memory)

### Issue: No faces detected
**Solution:**
- Check lighting
- Ensure face is clearly visible
- Verify camera is working
- Check face_recognition library is installed

### Issue: False positives (authorized person marked as unauthorized)
**Solution:**
- Re-add the person with better lighting/angle
- Lower `face_recognition_tolerance` in config.json (try 0.5)

## Need Help?

If tests fail, check:
1. Console error messages
2. Email test script output
3. System logs
4. Camera permissions
5. Network connectivity (for email)
