#!/usr/bin/env python3
"""
Camera test that saves photos instead of showing window
Useful when no display is available (SSH connection)
"""

import cv2
from picamera2 import Picamera2
import time
import os

print("Starting camera test (saving photos)...")
print("Press Ctrl+C to stop")

# Initialize camera
camera = Picamera2()

# Configure camera
camera_config = camera.create_preview_configuration(
    main={"size": (1280, 720)}
)
camera.configure(camera_config)
camera.start()

# Allow camera to stabilize
time.sleep(2)

print("Camera is running. Taking test photos...")

try:
    # Take 3 test photos
    for i in range(1, 4):
        print(f"Taking photo {i}...")
        frame = camera.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Add text
        cv2.putText(frame_bgr, f"Camera Test Photo {i}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame_bgr, "Camera is working!", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Save photo
        filename = f"test_camera_{i}.jpg"
        cv2.imwrite(filename, frame_bgr)
        print(f"  ✓ Saved: {filename}")
        
        time.sleep(1)
    
    print("\n✓ Camera test complete!")
    print("Check the photos: test_camera_1.jpg, test_camera_2.jpg, test_camera_3.jpg")
    
except KeyboardInterrupt:
    print("\nStopping...")

finally:
    camera.stop()
    print("Camera stopped.")

