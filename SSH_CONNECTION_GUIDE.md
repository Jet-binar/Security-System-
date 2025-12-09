# Connecting to Raspberry Pi via SSH

This guide shows you how to connect to your Raspberry Pi 5 from your Windows computer using SSH.

## Prerequisites

1. **Raspberry Pi must be on the same network** as your Windows computer
2. **SSH must be enabled** on the Raspberry Pi
3. **Know your Raspberry Pi's IP address** or hostname

## Step 1: Enable SSH on Raspberry Pi

If SSH is not already enabled, you can enable it in two ways:

### Option A: Using Raspberry Pi Desktop (if you have monitor/keyboard)
1. Open Terminal on Raspberry Pi
2. Run: `sudo systemctl enable ssh`
3. Run: `sudo systemctl start ssh`

### Option B: Using raspi-config
1. Open Terminal on Raspberry Pi
2. Run: `sudo raspi-config`
3. Navigate to: **Interface Options** → **SSH**
4. Select **Yes** to enable SSH
5. Reboot if prompted

## Step 2: Find Your Raspberry Pi's IP Address

### On Raspberry Pi (if you have access):
```bash
hostname -I
```
or
```bash
ip addr show
```

### From Windows (if Pi is on same network):
1. Open Command Prompt or PowerShell
2. Run: `arp -a` to see all devices on your network
3. Look for a device with hostname like "raspberrypi" or check MAC addresses

### Alternative: Use hostname (if mDNS is enabled)
- Try: `raspberrypi.local` or `raspberrypi5.local`

## Step 3: Open Terminal on Windows

### Option A: PowerShell (Recommended)
1. Press `Windows Key + X`
2. Select **Windows PowerShell** or **Terminal**
3. Or search for "PowerShell" in Start menu

### Option B: Command Prompt
1. Press `Windows Key + R`
2. Type `cmd` and press Enter
3. Or search for "Command Prompt" in Start menu

### Option C: Windows Terminal (Modern)
1. Press `Windows Key`
2. Search for "Terminal" or "Windows Terminal"
3. Install from Microsoft Store if not available

## Step 4: Connect via SSH

### Basic SSH Command:
```bash
ssh pi@<RASPBERRY_PI_IP_ADDRESS>
```

### Example:
```bash
ssh pi@192.168.1.100
```

### Using hostname (if available):
```bash
ssh pi@raspberrypi.local
```

### First Time Connection:
- You'll see a security warning - type `yes` to continue
- Enter your Raspberry Pi password (default is usually `raspberry`)

## Step 5: Common SSH Commands

### Connect with specific user:
```bash
ssh username@192.168.1.100
```

### Connect with key file (if you set up SSH keys):
```bash
ssh -i path/to/private_key pi@192.168.1.100
```

### Copy files TO Raspberry Pi:
```bash
scp file.txt pi@192.168.1.100:/home/pi/
```

### Copy files FROM Raspberry Pi:
```bash
scp pi@192.168.1.100:/home/pi/file.txt ./
```

### Copy entire directory:
```bash
scp -r folder/ pi@192.168.1.100:/home/pi/
```

## Step 6: Transfer This Project to Raspberry Pi

### Option A: Using SCP (from Windows terminal):
```bash
# Navigate to project folder first
cd C:\Users\jsali\OneDrive\Documents\hailo-rpi5-examples

# Copy entire project to Raspberry Pi
scp -r * pi@192.168.1.100:/home/pi/hailo-rpi5-examples/
```

### Option B: Using Git (if you have a repository):
```bash
# On Raspberry Pi
cd ~
git clone <your-repo-url>
cd hailo-rpi5-examples
```

### Option C: Using SFTP client (WinSCP, FileZilla):
- Use GUI tools like WinSCP or FileZilla
- Connect using same credentials
- Drag and drop files

## Troubleshooting

### "Connection refused" or "Connection timed out"
- Check if SSH is enabled on Raspberry Pi
- Verify Raspberry Pi is on same network
- Check firewall settings
- Try pinging: `ping 192.168.1.100`

### "Host key verification failed"
- Remove old key: `ssh-keygen -R 192.168.1.100`
- Or edit: `C:\Users\jsali\.ssh\known_hosts` and remove the line with your Pi's IP

### "Permission denied"
- Check username (default is `pi`)
- Verify password is correct
- Check if user has SSH access

### Can't find IP address
- Connect monitor/keyboard to Raspberry Pi
- Or check your router's admin page for connected devices
- Use network scanner tools

## Quick Reference

```bash
# 1. Find Pi's IP (on Pi)
hostname -I

# 2. Connect from Windows
ssh pi@<IP_ADDRESS>

# 3. Transfer project files
scp -r * pi@<IP_ADDRESS>:/home/pi/hailo-rpi5-examples/

# 4. After connecting, navigate to project
cd ~/hailo-rpi5-examples

# 5. Run security system
python3 security_system.py
```

## Setting Up SSH Keys (Optional - More Secure)

### On Windows:
```bash
# Generate SSH key
ssh-keygen -t rsa -b 4096

# Copy key to Raspberry Pi
ssh-copy-id pi@192.168.1.100
```

After this, you won't need to enter password each time!

## Next Steps After Connecting

Once connected via SSH:

1. **Update system:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install dependencies:**
   ```bash
   sudo apt install -y python3-pip python3-venv python3-picamera2
   ```

3. **Navigate to project:**
   ```bash
   cd ~/hailo-rpi5-examples
   ```

4. **Set up virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Run the security system:**
   ```bash
   python3 security_system.py
   ```


