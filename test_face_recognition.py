#!/usr/bin/env python3
"""
Test face recognition with USB webcam
Quick diagnostic to see if face recognition is working
"""

import cv2
import face_recognition
import sys
from pathlib import Path
import config as cfg

def test_face_recognition():
    """Test face recognition with live camera"""
    print("=" * 60)
    print("Face Recognition Test")
    print("=" * 60)
    
    # Load config
    config = cfg.load_config()
    faces_dir = Path(config['faces_directory'])
    
    # Load authorized faces
    print("\n1. Loading authorized faces...")
    known_faces = []
    known_names = []
    
    if not faces_dir.exists():
        print(f"❌ Faces directory not found: {faces_dir}")
        print("   Add faces first with: python3 manage_faces.py capture 'Name'")
        return False
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    face_files = [f for f in faces_dir.iterdir() if f.suffix.lower() in image_extensions]
    
    if not face_files:
        print(f"❌ No authorized faces found in {faces_dir}")
        print("   Add faces first with: python3 manage_faces.py capture 'Name'")
        return False
    
    for image_file in face_files:
        try:
            image = face_recognition.load_image_file(str(image_file))
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_faces.append(encodings[0])
                known_names.append(image_file.stem)
                print(f"  ✓ Loaded: {image_file.stem}")
            else:
                print(f"  ⚠️  No face found in {image_file.name}")
        except Exception as e:
            print(f"  ❌ Error loading {image_file.name}: {e}")
    
    if not known_faces:
        print("❌ No valid faces loaded!")
        return False
    
    print(f"\n✓ Loaded {len(known_faces)} authorized face(s)")
    
    # Open camera
    print("\n2. Opening camera...")
    camera_type = config.get('camera_type', 'pi_camera')
    camera_index = config.get('usb_camera_index', 0)
    
    if camera_type == 'usb_webcam':
        print(f"  Using USB webcam (index {camera_index})")
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"❌ Could not open USB camera at index {camera_index}")
            return False
    else:
        print("  Using Raspberry Pi Camera")
        try:
            from picamera2 import Picamera2
            camera = Picamera2()
            camera_config = camera.create_preview_configuration(
                main={"size": (640, 480)}
            )
            camera.configure(camera_config)
            camera.start()
            cap = None
        except Exception as e:
            print(f"❌ Could not open Pi Camera: {e}")
            return False
    
    print("✓ Camera opened")
    print("\n3. Testing face recognition...")
    print("   Position yourself in front of the camera")
    print("   Press 'q' to quit")
    print("   Press 's' to save a test frame")
    
    frame_count = 0
    faces_detected_count = 0
    faces_recognized_count = 0
    
    try:
        while True:
            # Capture frame
            if camera_type == 'usb_webcam':
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to capture frame")
                    break
                frame_bgr = frame
            else:
                frame = camera.capture_array()
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Resize for faster processing
            small_frame = cv2.resize(frame_bgr, (0, 0), fx=0.5, fy=0.5)
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Find faces
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            # Scale back to original size
            face_locations = [(top*2, right*2, bottom*2, left*2) for (top, right, bottom, left) in face_locations]
            
            # Draw results
            display_frame = frame_bgr.copy()
            
            if face_locations:
                faces_detected_count += 1
                for face_encoding, face_location in zip(face_encodings, face_locations):
                    top, right, bottom, left = face_location
                    
                    # Compare with known faces
                    if known_faces:
                        matches = face_recognition.compare_faces(
                            known_faces, 
                            face_encoding,
                            tolerance=config.get('face_recognition_tolerance', 0.6)
                        )
                        face_distance = face_recognition.face_distance(known_faces, face_encoding)
                        
                        name = "Unknown"
                        if len(face_distance) > 0:
                            best_match_index = face_distance.argmin()
                            if matches[best_match_index]:
                                name = known_names[best_match_index]
                                faces_recognized_count += 1
                                color = (0, 255, 0)  # Green
                            else:
                                color = (0, 0, 255)  # Red
                        else:
                            color = (0, 0, 255)  # Red
                    else:
                        name = "Unknown"
                        color = (0, 0, 255)  # Red
                    
                    # Draw box
                    cv2.rectangle(display_frame, (left, top), (right, bottom), color, 2)
                    cv2.rectangle(display_frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    cv2.putText(display_frame, name, (left + 6, bottom - 6),
                               cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
            
            # Add status
            status = f"Frame: {frame_count} | Faces detected: {len(face_locations)}"
            if face_locations:
                status += f" | Detected: {faces_detected_count} | Recognized: {faces_recognized_count}"
            cv2.putText(display_frame, status, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow("Face Recognition Test", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save test frame
                cv2.imwrite('test_frame.jpg', display_frame)
                print(f"  Test frame saved as test_frame.jpg")
            
            frame_count += 1
            
            # Print status every 30 frames
            if frame_count % 30 == 0:
                print(f"  Processed {frame_count} frames | Faces detected: {faces_detected_count} | Recognized: {faces_recognized_count}")
    
    except KeyboardInterrupt:
        print("\n\nStopping...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if camera_type == 'usb_webcam':
            cap.release()
        else:
            camera.stop()
        cv2.destroyAllWindows()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total frames processed: {frame_count}")
    print(f"Frames with faces detected: {faces_detected_count}")
    print(f"Frames with recognized faces: {faces_recognized_count}")
    
    if frame_count > 0:
        detection_rate = (faces_detected_count / frame_count) * 100
        print(f"Face detection rate: {detection_rate:.1f}%")
    
    if faces_detected_count > 0:
        recognition_rate = (faces_recognized_count / faces_detected_count) * 100
        print(f"Face recognition rate: {recognition_rate:.1f}%")
    
    if faces_detected_count == 0:
        print("\n⚠️  No faces detected!")
        print("   - Check lighting")
        print("   - Make sure face is clearly visible")
        print("   - Try adjusting camera position")
    elif faces_recognized_count == 0:
        print("\n⚠️  Faces detected but not recognized!")
        print("   - Check if authorized faces are loaded correctly")
        print("   - Try adjusting face_recognition_tolerance in config.json")
        print("   - Make sure you're using the same person as in authorized faces")
    
    return True

if __name__ == "__main__":
    test_face_recognition()

