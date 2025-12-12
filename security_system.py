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
import threading
from queue import Queue
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
        self.camera_type = None  # 'pi_camera' or 'usb_webcam'
        self.usb_camera = None  # OpenCV VideoCapture for USB webcam
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
        
        # Face tracking for 5-second delay before alert
        self.face_tracking = {}  # Track faces: {face_id: {'first_seen': time, 'ever_authorized': bool, 'location': tuple, 'frame': array}}
        self.face_tracking_lock = threading.Lock()
        self.unauthorized_delay = self.config.get('unauthorized_delay', 5)  # seconds to wait before alert
        
        # Track previously detected unauthorized persons (for repeat offenders)
        self.previously_unauthorized = []  # List of face encodings that were previously unauthorized
        self.previously_unauthorized_lock = threading.Lock()
        self.repeat_offender_delay = self.config.get('repeat_offender_delay', 1)  # Shorter delay for repeat offenders
        self.unauthorized_memory_time = self.config.get('unauthorized_memory_time', 3600)  # Remember for 1 hour (3600 seconds)
        
        # Threading for smooth camera feed
        self.frame_queue = Queue(maxsize=2)  # Keep only latest frames
        self.latest_results = {'recognized': [], 'unrecognized': []}
        self.results_lock = threading.Lock()
        self.processing_thread = None
        self.running = False
        
        # Motion detection for adaptive scanning (reduces frequency, never stops)
        self.motion_detection_enabled = self.config.get('motion_detection_enabled', True)
        self.motion_threshold = self.config.get('motion_threshold', 5000)  # Sensitivity threshold
        self.motion_check_interval = self.config.get('motion_check_interval', 10)  # Check every N frames
        self.previous_frame = None
        self.motion_detected = True  # Start with motion detected to begin scanning
        self.scan_interval_motion = self.config.get('scan_interval_motion', 20)  # Scan every N frames when motion detected
        self.scan_interval_no_motion = self.config.get('scan_interval_no_motion', 40)  # Scan every N frames when no motion
        self.min_processing_interval = self.config.get('min_processing_interval', 0.5)  # Minimum seconds between processing
        self.last_processing_time = 0
        
        print(f"Security system initialized with {len(self.known_faces)} authorized faces")
        if self.motion_detection_enabled:
            print(f"Motion detection: ENABLED (adaptive scanning)")
    
    def setup_camera(self):
        """Configure and start camera (Pi Camera or USB Webcam)"""
        camera_type = self.config.get('camera_type', 'pi_camera')  # 'pi_camera' or 'usb_webcam'
        self.camera_type = camera_type
        
        print(f"Setting up camera ({camera_type})...")
        
        if camera_type == 'usb_webcam':
            self.setup_usb_webcam()
        else:
            self.setup_pi_camera()
    
    def setup_pi_camera(self):
        """Setup Raspberry Pi Camera Module"""
        try:
            self.camera = Picamera2()
            
            # Get FPS setting from config (default to 9)
            target_fps = self.config.get('camera_fps', 9)
            
            # Configure camera
            camera_config = self.camera.create_preview_configuration(
                main={"size": tuple(self.config['camera_resolution'])},
                controls={"FrameRate": target_fps}
            )
            self.camera.configure(camera_config)
            self.camera.start()
            time.sleep(2)  # Allow camera to stabilize
            print(f"✓ Raspberry Pi Camera initialized at {self.config['camera_resolution']} @ {target_fps} FPS")
        except Exception as e:
            print(f"Error setting up Pi Camera: {e}")
            print("Falling back to USB webcam...")
            self.setup_usb_webcam()
    
    def setup_usb_webcam(self):
        """Setup USB Webcam (e.g., Logitech C920e)"""
        resolution = tuple(self.config['camera_resolution'])
        target_fps = self.config.get('camera_fps', 9)
        preferred_index = self.config.get('usb_camera_index', 0)
        
        # Try multiple camera indices (0, 1, 2)
        camera_indices = [preferred_index, 0, 1, 2]
        camera_indices = list(dict.fromkeys(camera_indices))  # Remove duplicates while preserving order
        
        for camera_index in camera_indices:
            try:
                print(f"  Trying USB camera index {camera_index}...")
                self.usb_camera = cv2.VideoCapture(camera_index)
                
                if not self.usb_camera.isOpened():
                    if self.usb_camera:
                        self.usb_camera.release()
                    continue  # Try next index
                
                # Set camera properties
                self.usb_camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
                self.usb_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
                self.usb_camera.set(cv2.CAP_PROP_FPS, target_fps)
                
                # Allow camera to stabilize
                time.sleep(1)
                
                # Test capture - try multiple times
                ret = False
                test_frame = None
                for attempt in range(5):
                    ret, test_frame = self.usb_camera.read()
                    if ret and test_frame is not None:
                        break
                    time.sleep(0.2)
                
                if not ret or test_frame is None:
                    print(f"    Camera {camera_index} opened but could not capture frame")
                    self.usb_camera.release()
                    continue  # Try next index
                
                actual_width = int(self.usb_camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(self.usb_camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                actual_fps = int(self.usb_camera.get(cv2.CAP_PROP_FPS))
                
                print(f"✓ USB Webcam initialized at index {camera_index}: {actual_width}x{actual_height} @ {actual_fps} FPS")
                self.camera_type = 'usb_webcam'
                return  # Success!
                
            except Exception as e:
                print(f"    Error with camera index {camera_index}: {e}")
                if self.usb_camera:
                    try:
                        self.usb_camera.release()
                    except:
                        pass
                continue  # Try next index
        
        # If we get here, all indices failed
        print("\n❌ ERROR: Could not initialize USB webcam at any index (0, 1, 2)")
        print("\nTroubleshooting steps:")
        print("  1. Check USB camera is connected: lsusb")
        print("  2. Check camera permissions: ls -l /dev/video*")
        print("  3. Try different camera index in config.json: 'usb_camera_index': 1 or 2")
        print("  4. Make sure no other app is using the camera")
        print("  5. Try switching to Pi Camera: 'camera_type': 'pi_camera'")
        print("\nFalling back to Raspberry Pi Camera...")
        
        # Fallback to Pi Camera
        try:
            self.setup_pi_camera()
        except Exception as e:
            print(f"❌ ERROR: Pi Camera also failed: {e}")
            raise Exception("Could not initialize any camera. Please check your camera connection.")
    
    def capture_frame(self):
        """Capture a frame from the active camera"""
        if self.camera_type == 'usb_webcam':
            ret, frame = self.usb_camera.read()
            if not ret:
                raise Exception("Failed to capture frame from USB webcam")
            return frame  # USB webcam already returns BGR format
        else:
            # Pi Camera
            frame = self.camera.capture_array()
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR
            return frame_bgr
    
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
        Recognize faces in the frame (optimized for performance)
        
        Returns:
            list of tuples: [(name, location, encoding), ...] for recognized faces
            list of tuples: [(location, encoding), ...] for unrecognized faces
        """
        # Resize frame to smaller size for faster processing (maintains aspect ratio)
        # Process at 320x240 for much faster face recognition
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        
        # Convert BGR to RGB (face_recognition uses RGB)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Find face locations and encodings on smaller frame
        # Use faster model for better performance
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")  # "hog" is faster than "cnn"
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        # Scale face locations back to original frame size
        face_locations = [(top*2, right*2, bottom*2, left*2) for (top, right, bottom, left) in face_locations]
        
        recognized = []
        unrecognized = []
        
        # If no faces found, return empty lists
        if not face_locations:
            return recognized, unrecognized
        
        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Compare with known faces
            if len(self.known_faces) > 0:
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
                    unrecognized.append((face_location, face_encoding))
                else:
                    recognized.append((name, face_location, face_encoding))
            else:
                # No authorized faces loaded, treat all as unauthorized
                unrecognized.append((face_location, face_encoding))
        
        return recognized, unrecognized
    
    def find_matching_face_id(self, face_encoding, current_time, face_tracking_dict):
        """Find matching face ID by comparing with tracked faces"""
        # Compare with all tracked faces to find the best match
        best_match_id = None
        best_distance = float('inf')
        
        for face_id, face_data in face_tracking_dict.items():
            # Only match with faces seen recently (within last 2 seconds)
            if current_time - face_data['first_seen'] < 2:
                # Calculate face distance
                if 'encoding' in face_data:
                    try:
                        distance = face_recognition.face_distance([face_data['encoding']], face_encoding)[0]
                        if distance < 0.5 and distance < best_distance:  # 0.5 is a reasonable threshold
                            best_distance = distance
                            best_match_id = face_id
                    except:
                        pass
        
        return best_match_id
    
    def update_face_tracking(self, recognized, unrecognized, frame):
        """Update face tracking and check if alerts should be sent"""
        current_time = time.time()
        
        with self.face_tracking_lock:
            # Mark all current faces as seen
            current_face_ids = set()
            
            # Update recognized faces
            for name, location, encoding in recognized:
                # Try to find matching existing face
                face_id = self.find_matching_face_id(encoding, current_time, self.face_tracking)
                
                if face_id is None:
                    # New face detected - create new ID
                    face_id = len(self.face_tracking)  # Simple ID generation
                    self.face_tracking[face_id] = {
                        'first_seen': current_time,
                        'ever_authorized': True,  # This face is authorized
                        'location': location,
                        'frame': frame.copy(),
                        'name': name,
                        'encoding': encoding
                    }
                else:
                    # Existing face - mark as authorized
                    self.face_tracking[face_id]['ever_authorized'] = True
                    self.face_tracking[face_id]['location'] = location
                    self.face_tracking[face_id]['frame'] = frame.copy()
                    self.face_tracking[face_id]['encoding'] = encoding
                
                current_face_ids.add(face_id)
            
            # Update unrecognized faces
            for location, encoding in unrecognized:
                # Try to find matching existing face
                face_id = self.find_matching_face_id(encoding, current_time, self.face_tracking)
                
                if face_id is None:
                    # New unauthorized face detected - start tracking
                    face_id = len(self.face_tracking)  # Simple ID generation
                    self.face_tracking[face_id] = {
                        'first_seen': current_time,
                        'ever_authorized': False,
                        'location': location,
                        'frame': frame.copy(),
                        'name': None,
                        'encoding': encoding
                    }
                else:
                    # Existing face - update location and frame
                    self.face_tracking[face_id]['location'] = location
                    self.face_tracking[face_id]['frame'] = frame.copy()
                    self.face_tracking[face_id]['encoding'] = encoding
                    # Don't change ever_authorized if it was True before
                
                current_face_ids.add(face_id)
            
            # Check for faces that should trigger alerts
            faces_to_remove = []
            for face_id, face_data in self.face_tracking.items():
                elapsed = current_time - face_data['first_seen']
                
                # Check if this is a repeat offender (previously detected unauthorized)
                is_repeat_offender = False
                if 'encoding' in face_data:
                    with self.previously_unauthorized_lock:
                        for prev_encoding, prev_time in self.previously_unauthorized:
                            # Check if face matches and memory hasn't expired
                            if current_time - prev_time < self.unauthorized_memory_time:
                                try:
                                    distance = face_recognition.face_distance([prev_encoding], face_data['encoding'])[0]
                                    if distance < 0.5:  # Same person
                                        is_repeat_offender = True
                                        break
                                except:
                                    pass
                
                # Determine delay: shorter for repeat offenders
                required_delay = self.repeat_offender_delay if is_repeat_offender else self.unauthorized_delay
                
                # If delay has passed and face was never authorized
                if elapsed >= required_delay and not face_data['ever_authorized']:
                    # Check cooldown to avoid spamming
                    last_alert = self.last_detection_time.get('unauthorized', 0)
                    if current_time - last_alert >= self.detection_cooldown:
                        # Send alert
                        alert_type = "REPEAT OFFENDER" if is_repeat_offender else "UNAUTHORIZED"
                        self.send_unauthorized_alert(face_data['frame'], face_data['location'], face_id, alert_type)
                        self.last_detection_time['unauthorized'] = current_time
                        
                        # Add to previously unauthorized list if not already there
                        if 'encoding' in face_data and not is_repeat_offender:
                            with self.previously_unauthorized_lock:
                                self.previously_unauthorized.append((face_data['encoding'].copy(), current_time))
                        
                        faces_to_remove.append(face_id)
                # If face was authorized, we can remove it from tracking after a delay
                elif face_data['ever_authorized'] and elapsed > 10:
                    faces_to_remove.append(face_id)
            
            # Remove old/processed faces
            for face_id in faces_to_remove:
                if face_id in self.face_tracking:
                    del self.face_tracking[face_id]
            
            # Remove faces that are no longer visible (not in current frame)
            # Keep them for a bit in case they come back
            faces_to_remove_old = []
            for face_id in self.face_tracking:
                if face_id not in current_face_ids:
                    # Face not seen in this frame, but keep tracking for 2 seconds
                    if current_time - self.face_tracking[face_id]['first_seen'] > 2:
                        faces_to_remove_old.append(face_id)
            
            for face_id in faces_to_remove_old:
                if face_id in self.face_tracking:
                    del self.face_tracking[face_id]
            
            # Clean up old entries from previously_unauthorized list (older than memory time)
            with self.previously_unauthorized_lock:
                self.previously_unauthorized = [
                    (encoding, prev_time) for encoding, prev_time in self.previously_unauthorized
                    if current_time - prev_time < self.unauthorized_memory_time
                ]
    
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
    
    def detect_motion(self, current_frame):
        """Detect motion between frames using frame differencing"""
        if not self.motion_detection_enabled:
            self.motion_detected = True
            return True  # If motion detection disabled, always return True
        
        if self.previous_frame is None:
            self.previous_frame = current_frame.copy()
            self.motion_detected = True
            return True  # First frame, assume motion to start processing
        
        # Convert to grayscale for comparison
        gray_current = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        gray_previous = cv2.cvtColor(self.previous_frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate frame difference
        frame_diff = cv2.absdiff(gray_current, gray_previous)
        
        # Apply threshold
        _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)
        
        # Count non-zero pixels (motion pixels)
        motion_pixels = cv2.countNonZero(thresh)
        
        # Update previous frame
        self.previous_frame = current_frame.copy()
        
        # Check if motion exceeds threshold
        motion_detected = motion_pixels > self.motion_threshold
        self.motion_detected = motion_detected
        
        return motion_detected
    
    def send_unauthorized_alert(self, frame, face_location, face_id, alert_type="UNAUTHORIZED"):
        """Send alert for unauthorized person after delay"""
        print(f"⚠️  {alert_type} PERSON DETECTED! (Face ID: {face_id})")
        
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
        cv2.putText(frame_copy, alert_type, (left, top - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imwrite(str(filepath), frame_copy)
        print(f"  Photo saved: {filepath}")
        
        # Send email
        try:
            self.email_sender.send_alert(filepath, timestamp)
            print("  Alert email sent successfully")
        except Exception as e:
            print(f"  Error sending email: {e}")
    
    def process_frames_thread(self):
        """Background thread for processing face recognition"""
        process_every_n_frames = self.config.get('process_every_n_frames', 2)
        frame_count = 0
        motion_check_counter = 0
        last_debug_time = time.time()
        
        while self.running:
            try:
                # Get frame from queue (non-blocking with timeout)
                try:
                    frame_data = self.frame_queue.get(timeout=0.1)
                    frame, original_frame = frame_data
                    frame_count += 1
                except:
                    continue
                
                # Check for motion periodically (lightweight check)
                if self.motion_detection_enabled:
                    motion_check_counter += 1
                    if motion_check_counter >= self.motion_check_interval:
                        self.detect_motion(original_frame)
                        motion_check_counter = 0
                
                # Always process, but adjust frequency based on motion
                # Scan more frequently when motion detected, less when no motion
                if self.motion_detection_enabled:
                    scan_interval = self.scan_interval_motion if self.motion_detected else self.scan_interval_no_motion
                else:
                    scan_interval = self.scan_interval_motion  # Use motion interval if detection disabled
                
                # Time-based throttling to prevent overload
                current_time = time.time()
                time_since_last_process = current_time - self.last_processing_time
                
                # Process face recognition at adaptive interval AND minimum time interval
                if frame_count % scan_interval == 0 and time_since_last_process >= self.min_processing_interval:
                    self.last_processing_time = current_time
                    
                    # Debug output every 5 seconds
                    if current_time - last_debug_time > 5:
                        print(f"[DEBUG] Processing frame {frame_count}, scan_interval={scan_interval}, motion={self.motion_detected}, known_faces={len(self.known_faces)}")
                        last_debug_time = current_time
                    
                    recognized, unrecognized = self.recognize_face(original_frame)
                    
                    # Debug if faces found
                    if recognized or unrecognized:
                        print(f"[DEBUG] Found {len(recognized)} recognized, {len(unrecognized)} unrecognized faces")
                    
                    # Update face tracking (handles 5-second delay and authorization checking)
                    self.update_face_tracking(recognized, unrecognized, original_frame)
                    
                    # Convert back to old format for display (without encodings)
                    recognized_display = [(name, loc) for name, loc, _ in recognized]
                    unrecognized_display = [loc for loc, _ in unrecognized]
                    
                    # Update results thread-safely
                    with self.results_lock:
                        self.latest_results['recognized'] = recognized_display
                        self.latest_results['unrecognized'] = unrecognized_display
                    
                    # Voice announcements for authorized persons
                    if self.voice_system and recognized:
                        for name, _, _ in recognized:
                            if name != "Unknown":
                                self.voice_system.speak_authorized(name)
                
            except Exception as e:
                print(f"Error in processing thread: {e}")
                continue
    
    def run(self):
        """Main security system loop"""
        print("\n" + "=" * 60)
        print("SECURITY SYSTEM ACTIVE")
        print("=" * 60)
        print(f"Monitoring for unauthorized access...")
        print(f"Authorized faces: {len(self.known_faces)}")
        print("Press Ctrl+C to stop\n")
        
        self.running = True
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self.process_frames_thread, daemon=True)
        self.processing_thread.start()
        
        frame_count = 0
        start_time = time.time()
        
        # Get display size for resizing
        display_size = tuple(self.config.get('display_size', [640, 480]))
        
        try:
            while True:
                # Capture frame (this is fast, doesn't block)
                frame_bgr = self.capture_frame()
                
                # Resize frame for display (smaller = faster)
                display_frame = cv2.resize(frame_bgr, display_size) if display_size != tuple(frame_bgr.shape[:2][::-1]) else frame_bgr.copy()
                
                # Add frame to processing queue (non-blocking, drops old frames if queue full)
                # Only add if queue has space to prevent backup
                if not self.frame_queue.full():
                    try:
                        self.frame_queue.put_nowait((display_frame.copy(), frame_bgr.copy()))
                    except:
                        pass  # Queue full, skip this frame
                else:
                    # Queue full, remove oldest and add new (don't block)
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait((display_frame.copy(), frame_bgr.copy()))
                    except:
                        pass  # Skip if can't add
                
                # Get latest recognition results (thread-safe)
                with self.results_lock:
                    recognized = self.latest_results['recognized'].copy()
                    unrecognized = self.latest_results['unrecognized'].copy()
                
                # Get face tracking info for countdown display
                current_time = time.time()
                with self.face_tracking_lock:
                    tracking_info = {}
                    for face_id, face_data in self.face_tracking.items():
                        if not face_data['ever_authorized']:
                            elapsed = current_time - face_data['first_seen']
                            
                            # Check if repeat offender
                            is_repeat = False
                            if 'encoding' in face_data:
                                with self.previously_unauthorized_lock:
                                    for prev_encoding, prev_time in self.previously_unauthorized:
                                        if current_time - prev_time < self.unauthorized_memory_time:
                                            try:
                                                distance = face_recognition.face_distance([prev_encoding], face_data['encoding'])[0]
                                                if distance < 0.5:
                                                    is_repeat = True
                                                    break
                                            except:
                                                pass
                            
                            required_delay = self.repeat_offender_delay if is_repeat else self.unauthorized_delay
                            remaining = max(0, required_delay - elapsed)
                            tracking_info[face_id] = {
                                'remaining': remaining,
                                'location': face_data['location'],
                                'is_repeat': is_repeat
                            }
                
                # Draw recognized faces (green)
                for name, location in recognized:
                    # Scale location if frame was resized
                    if display_frame.shape[:2] != frame_bgr.shape[:2]:
                        scale_x = display_size[0] / frame_bgr.shape[1]
                        scale_y = display_size[1] / frame_bgr.shape[0]
                        top, right, bottom, left = location
                        location_scaled = (
                            int(top * scale_y), int(right * scale_x),
                            int(bottom * scale_y), int(left * scale_x)
                        )
                        self.draw_face_box(display_frame, location_scaled, name, (0, 255, 0))
                    else:
                        self.draw_face_box(display_frame, location, name, (0, 255, 0))
                
                # Draw unrecognized faces (red) with countdown
                for location in unrecognized:
                    # Scale location if frame was resized
                    if display_frame.shape[:2] != frame_bgr.shape[:2]:
                        scale_x = display_size[0] / frame_bgr.shape[1]
                        scale_y = display_size[1] / frame_bgr.shape[0]
                        top, right, bottom, left = location
                        location_scaled = (
                            int(top * scale_y), int(right * scale_x),
                            int(bottom * scale_y), int(left * scale_x)
                        )
                        scaled_location = location_scaled
                    else:
                        scaled_location = location
                    
                    # Find matching tracking info (approximate match by location)
                    top, right, bottom, left = scaled_location
                    center_x = (left + right) // 2
                    center_y = (top + bottom) // 2
                    
                    # Find closest tracking entry
                    countdown_text = "UNAUTHORIZED"
                    for face_id, info in tracking_info.items():
                        track_top, track_right, track_bottom, track_left = info['location']
                        track_center_x = (track_left + track_right) // 2
                        track_center_y = (track_top + track_bottom) // 2
                        
                        # If locations are close (within 50 pixels), show countdown
                        if abs(center_x - track_center_x) < 50 and abs(center_y - track_center_y) < 50:
                            remaining = info['remaining']
                            is_repeat = info.get('is_repeat', False)
                            prefix = "REPEAT OFFENDER" if is_repeat else "UNAUTHORIZED"
                            if remaining > 0:
                                countdown_text = f"{prefix} ({remaining:.1f}s)"
                            else:
                                countdown_text = "ALERT SENT!"
                            break
                    
                    self.draw_face_box(display_frame, scaled_location, countdown_text, (0, 0, 255))
                
                # Add status text
                elapsed = time.time() - start_time
                fps = frame_count / max(0.1, elapsed)
                status_text = f"Authorized: {len(self.known_faces)} | Frame: {frame_count} | FPS: {fps:.1f}"
                cv2.putText(display_frame, status_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Show motion detection status
                if self.motion_detection_enabled:
                    if self.motion_detected:
                        motion_status = "MOTION - Fast Scan"
                        motion_color = (0, 255, 0)  # Green
                    else:
                        motion_status = "No Motion - Slow Scan"
                        motion_color = (0, 165, 255)  # Orange
                    cv2.putText(display_frame, motion_status, (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, motion_color, 2)
                
                # Show detection status
                if len(unrecognized) > 0:
                    cv2.putText(display_frame, "UNAUTHORIZED DETECTED!", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Display frame immediately (smooth display)
                if self.config.get('display', True):
                    cv2.imshow("Security System", display_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                frame_count += 1
                
                # Reload faces periodically (in case new faces are added)
                if frame_count % 300 == 0:  # Every 300 frames
                    self.load_authorized_faces()
        
        except KeyboardInterrupt:
            print("\n\nShutting down security system...")
        
        finally:
            self.running = False
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        self.running = False
        
        # Wait for processing thread to finish
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
        
        # Clean up camera
        if self.camera_type == 'usb_webcam' and self.usb_camera:
            self.usb_camera.release()
        elif self.camera:
            self.camera.stop()
        
        cv2.destroyAllWindows()
        print("Security system stopped.")


def main():
    """Main entry point"""
    system = SecuritySystem()
    system.run()


if __name__ == "__main__":
    main()

