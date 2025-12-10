#!/usr/bin/env python3
"""
Raspberry Pi 5 Security System with Face Recognition
- Recognizes authorized faces from database
- Captures and emails photos of unauthorized persons
- Ready for future voice features
"""

import cv2
import numpy as np
import face_recognition
import os
import json
import time
import datetime
from pathlib import Path
from picamera2 import Picamera2
from email_sender import EmailSender
from voice_features import VoiceSystem
import config

try:
    from hailo_platform import Device, VStreams, ConfigureParams, InferVStreams
    HAILO_AVAILABLE = True
except ImportError:
    HAILO_AVAILABLE = False
    print("Note: Hailo not available, using CPU-based face recognition")


class SecuritySystem:
    def __init__(self):
        """Initialize the security system"""
        self.config = config.load_config()
        self.camera = None
        self.known_faces = []
        self.known_names = []
        self.email_sender = EmailSender(self.config)
        self.voice_system = VoiceSystem() if self.config.get('enable_voice', False) else None
        
        # Create necessary directories
        self.faces_dir = Path(self.config['faces_directory'])
        self.unauthorized_dir = Path(self.config['unauthorized_directory'])
        self.faces_dir.mkdir(exist_ok=True)
        self.unauthorized_dir.mkdir(exist_ok=True)
        
        # Load authorized faces
        self.load_authorized_faces()
        
        # Initialize camera
        self.setup_camera()
        
        # Detection state
        self.last_detection_time = {}
        self.detection_cooldown = self.config.get('detection_cooldown', 30)  # seconds
        
        print(f"Security system initialized with {len(self.known_faces)} authorized faces")
    
    def setup_camera(self):
        """Configure and start the Raspberry Pi camera"""
        print("Setting up camera...")
        self.camera = Picamera2()
        
        camera_config = self.camera.create_preview_configuration(
            main={"size": tuple(self.config['camera_resolution'])}
        )
        self.camera.configure(camera_config)
        self.camera.start()
        time.sleep(2)  # Allow camera to stabilize
        print(f"Camera initialized at {self.config['camera_resolution']}")
    
    def load_authorized_faces(self):
        """Load all authorized faces from the faces directory"""
        print("Loading authorized faces...")
        self.known_faces = []
        self.known_names = []
        
        if not self.faces_dir.exists():
            print(f"Faces directory {self.faces_dir} does not exist. Creating it...")
            self.faces_dir.mkdir(parents=True, exist_ok=True)
            return
        
        # Supported image formats
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        
        for image_file in self.faces_dir.iterdir():
            if image_file.suffix.lower() in image_extensions:
                try:
                    # Load image
                    image = face_recognition.load_image_file(str(image_file))
                    # Find face encodings
                    encodings = face_recognition.face_encodings(image)
                    
                    if encodings:
                        # Use the first face found in the image
                        self.known_faces.append(encodings[0])
                        # Use filename (without extension) as the name
                        name = image_file.stem
                        self.known_names.append(name)
                        print(f"  Loaded: {name}")
                    else:
                        print(f"  Warning: No face found in {image_file.name}")
                
                except Exception as e:
                    print(f"  Error loading {image_file.name}: {e}")
        
        print(f"Loaded {len(self.known_faces)} authorized faces")
    
    def recognize_face(self, frame):
        """
        Recognize faces in the frame
        
        Returns:
            list of tuples: [(name, location), ...] for recognized faces
            list of locations: for unrecognized faces
        """
        # Convert BGR to RGB (face_recognition uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        recognized = []
        unrecognized = []
        
        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_faces, 
                face_encoding,
                tolerance=self.config.get('face_recognition_tolerance', 0.6)
            )
            face_distance = face_recognition.face_distance(self.known_faces, face_encoding)
            
            name = "Unknown"
            best_match_index = None
            
            if len(face_distance) > 0:
                best_match_index = np.argmin(face_distance)
                if matches[best_match_index]:
                    name = self.known_names[best_match_index]
            
            if name == "Unknown":
                unrecognized.append(face_location)
            else:
                recognized.append((name, face_location))
        
        return recognized, unrecognized
    
    def draw_face_box(self, frame, location, name, color=(0, 255, 0)):
        """Draw a box around a face with the name"""
        top, right, bottom, left = location
        
        # Draw rectangle
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Draw label background
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        
        # Draw name
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)
    
    def handle_unauthorized_person(self, frame, face_location):
        """Handle detection of unauthorized person"""
        current_time = time.time()
        
        # Check cooldown to avoid spamming emails
        if current_time - self.last_detection_time.get('unauthorized', 0) < self.detection_cooldown:
            return
        
        self.last_detection_time['unauthorized'] = current_time
        
        print("⚠️  UNAUTHORIZED PERSON DETECTED!")
        
        # Voice announcement
        if self.voice_system:
            self.voice_system.speak_unauthorized()
        
        # Create timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save photo
        filename = f"unauthorized_{timestamp}.jpg"
        filepath = self.unauthorized_dir / filename
        
        # Draw box on frame before saving
        frame_copy = frame.copy()
        top, right, bottom, left = face_location
        cv2.rectangle(frame_copy, (left, top), (right, bottom), (0, 0, 255), 3)
        cv2.putText(frame_copy, "UNAUTHORIZED", (left, top - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imwrite(str(filepath), frame_copy)
        print(f"  Photo saved: {filepath}")
        
        # Send email
        try:
            self.email_sender.send_alert(filepath, timestamp)
            print("  Alert email sent successfully")
        except Exception as e:
            print(f"  Error sending email: {e}")
    
    def run(self):
        """Main security system loop"""
        print("\n" + "=" * 60)
        print("SECURITY SYSTEM ACTIVE")
        print("=" * 60)
        print(f"Monitoring for unauthorized access...")
        print(f"Authorized faces: {len(self.known_faces)}")
        print("Press Ctrl+C to stop\n")
        
        frame_count = 0
        process_every_n_frames = self.config.get('process_every_n_frames', 2)  # Process every Nth frame for performance
        
        try:
            while True:
                # Capture frame
                frame = self.camera.capture_array()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert to BGR for OpenCV
                
                # Process faces every N frames (for performance)
                if frame_count % process_every_n_frames == 0:
                    recognized, unrecognized = self.recognize_face(frame)
                    
                    # Draw recognized faces (green)
                    for name, location in recognized:
                        self.draw_face_box(frame, location, name, (0, 255, 0))
                    
                    # Handle unrecognized faces (red)
                    for location in unrecognized:
                        self.draw_face_box(frame, location, "UNAUTHORIZED", (0, 0, 255))
                        self.handle_unauthorized_person(frame, location)
                    
                    # Voice announcements for authorized persons
                    if self.voice_system and recognized:
                        for name, _ in recognized:
                            if name != "Unknown":
                                self.voice_system.speak_authorized(name)
                
                # Add status text
                status_text = f"Authorized: {len(self.known_faces)} | Frame: {frame_count}"
                cv2.putText(frame, status_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Display frame
                if self.config.get('display', True):
                    cv2.imshow("Security System", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                frame_count += 1
                
                # Reload faces periodically (in case new faces are added)
                if frame_count % 300 == 0:  # Every 300 frames
                    self.load_authorized_faces()
        
        except KeyboardInterrupt:
            print("\n\nShutting down security system...")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        if self.camera:
            self.camera.stop()
        cv2.destroyAllWindows()
        print("Security system stopped.")


def main():
    """Main entry point"""
    system = SecuritySystem()
    system.run()


if __name__ == "__main__":
    main()

