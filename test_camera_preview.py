#!/usr/bin/env python3
"""
Simple camera preview test
Opens a window showing live camera feed to verify camera is working
"""

import cv2
from picamera2 import Picamera2
import time

print("Starting camera preview...")
print("Press 'q' to quit")

# Initialize camera
camera = Picamera2()

# Configure camera
camera_config = camera.create_preview_configuration(
    main={"size": (1280, 720)},
    format="RGB888"
)
camera.configure(camera_config)
camera.start()

# Allow camera to stabilize
time.sleep(2)

print("Camera is running. You should see a window with the camera feed.")
print("Press 'q' in the window to quit.")

try:
    while True:
        # Capture frame
        frame = camera.capture_array()
        
        # Convert RGB to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Add text overlay
        cv2.putText(frame_bgr, "Camera Test - Press 'q' to quit", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Show frame
        cv2.imshow("Camera Preview", frame_bgr)
        
        # Check for 'q' key to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    # Cleanup
    camera.stop()
    cv2.destroyAllWindows()
    print("Camera preview closed.")

