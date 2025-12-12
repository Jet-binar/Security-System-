# Troubleshooting: Unauthorized Photos Not Saved / Emails Not Sent

## Quick Diagnostic Steps

### 1. Run the Debug Script

On your Raspberry Pi:
```bash
cd ~/Documents/SECURITY-System-
python3 debug_unauthorized.py
```

This will check:
- ✅ If the unauthorized_detections folder exists and is writable
- ✅ If email is configured correctly
- ✅ If the alert function works when called directly

### 2. Check Console Output

When running `python3 security_system.py`, look for these messages:

**If unauthorized person is detected, you should see:**
```
[DEBUG] Found 0 recognized, 1 unrecognized faces
[DEBUG] Processing 1 unrecognized face(s) - will track for 5s
[DEBUG] Face ID 0: elapsed=1.2s/5s, ever_authorized=False
[DEBUG] Face ID 0: elapsed=2.5s/5s, ever_authorized=False
[DEBUG] Face ID 0: elapsed=3.8s/5s, ever_authorized=False
[DEBUG] Face ID 0: elapsed=5.1s/5s, ever_authorized=False
[DEBUG] ✓ Triggering alert for Face ID 0: UNAUTHORIZED
⚠️  UNAUTHORIZED PERSON DETECTED! (Face ID: 0)
  Photo saved: unauthorized_detections/unauthorized_20241201_143022.jpg
  Photo absolute path: /home/pi/Documents/SECURITY-System-/unauthorized_detections/unauthorized_20241201_143022.jpg
  Photo file size: 45234 bytes
  Attempting to send email with photo: ...
  ✓ Alert email sent successfully
```

### 3. Common Issues and Solutions

#### Issue: No "[DEBUG] Found ... unrecognized faces" messages

**Problem:** Faces are not being detected

**Solutions:**
- Check lighting - face needs to be clearly visible
- Face should be facing camera directly
- Check if camera is working: `libcamera-hello --list-cameras`
- Verify face_recognition library is installed: `python3 -c "import face_recognition; print('OK')"`

#### Issue: See "[DEBUG] Found ... unrecognized faces" but no alert after 5 seconds

**Problem:** Face tracking might be removing the face too early, or delay logic isn't working

**Check:**
- Look for "[DEBUG] Face ID X: elapsed=..." messages
- If you see "Face ID X: elapsed=5.1s/5s" but no alert, check cooldown
- Cooldown is 30 seconds by default - if you sent an alert recently, wait 30 seconds

**Solution:**
- Reduce cooldown in config.json: `"detection_cooldown": 5` (for testing)
- Check console for cooldown messages

#### Issue: See "⚠️ UNAUTHORIZED PERSON DETECTED!" but no photo saved

**Problem:** File write permissions or path issue

**Solutions:**
```bash
# Check folder exists and permissions
ls -la ~/Documents/SECURITY-System-/unauthorized_detections/

# If folder doesn't exist, create it
mkdir -p ~/Documents/SECURITY-System-/unauthorized_detections/

# Fix permissions
chmod 755 ~/Documents/SECURITY-System-/unauthorized_detections/
chmod 644 ~/Documents/SECURITY-System-/unauthorized_detections/*.jpg 2>/dev/null

# Check disk space
df -h
```

#### Issue: Photo saved but email not sent

**Problem:** Email configuration or network issue

**Solutions:**
1. **Test email separately:**
   ```bash
   python3 simple_email_test.py
   ```

2. **Check email config:**
   ```bash
   cat config.json | grep -A 5 email
   ```

3. **Check error messages:**
   - Look for "Error sending email: ..." in console
   - Common errors:
     - "SMTP Authentication Error" → Wrong app password
     - "Connection refused" → No internet or firewall blocking
     - "Email configuration incomplete" → Missing fields in config.json

4. **Verify internet connection:**
   ```bash
   ping -c 3 smtp.gmail.com
   ```

#### Issue: Face is detected but immediately disappears from tracking

**Problem:** Face might be getting marked as authorized accidentally, or frame is invalid

**Check:**
- Look for messages like "Face ID X: elapsed=..." - if they stop appearing, face was removed
- Check if face is being recognized as authorized (should see "Authorized: ..." message)

**Solution:**
- Make sure you're testing with someone NOT in authorized_faces folder
- Check authorized_faces folder: `ls authorized_faces/`
- If folder is empty, everyone should be unauthorized

### 4. Step-by-Step Debugging

**Step 1: Verify unauthorized person is detected**
```bash
# Run security system
python3 security_system.py

# Look for:
# [DEBUG] Found 0 recognized, 1 unrecognized faces
```

**Step 2: Verify face is being tracked**
```bash
# Look for repeated messages:
# [DEBUG] Face ID 0: elapsed=X.Xs/5s, ever_authorized=False
```

**Step 3: Verify alert triggers**
```bash
# After 5 seconds, should see:
# [DEBUG] ✓ Triggering alert for Face ID 0: UNAUTHORIZED
# ⚠️  UNAUTHORIZED PERSON DETECTED!
```

**Step 4: Verify photo is saved**
```bash
# Check console for:
# Photo saved: unauthorized_detections/unauthorized_...

# Verify file exists:
ls -lh unauthorized_detections/
```

**Step 5: Verify email is sent**
```bash
# Check console for:
# ✓ Alert email sent successfully

# Check email inbox
```

### 5. Manual Test

If automatic detection isn't working, test the alert function directly:

```python
# In Python shell on Raspberry Pi
from security_system import SecuritySystem
import numpy as np
import cv2

system = SecuritySystem()
test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
test_location = (100, 500, 300, 300)
system.send_unauthorized_alert(test_frame, test_location, 999, "TEST")
```

This should:
- Create a test photo
- Send a test email
- Show you exactly where the issue is

### 6. Check Logs

All important messages are printed to console. Look for:
- `[DEBUG]` messages - show what's happening
- `⚠️` messages - alerts triggered
- `ERROR` or `✗` messages - problems
- `✓` messages - successful operations

### 7. Reset and Test

If nothing works, try a clean test:

```bash
# 1. Make sure no authorized faces
rm -rf authorized_faces/*

# 2. Clear unauthorized detections
rm -rf unauthorized_detections/*

# 3. Test email
python3 simple_email_test.py

# 4. Run system
python3 security_system.py

# 5. Stand in front of camera (you should be unauthorized)
# 6. Wait 5+ seconds
# 7. Check console output
```

## Still Not Working?

Share the console output from when you run the system. Look for:
- Any `[DEBUG]` messages
- Any `ERROR` or `✗` messages
- The last few lines before the system stops or continues running

This will help identify exactly where the problem is.

