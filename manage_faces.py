#!/usr/bin/env python3
"""
Utility script to manage authorized faces database
- Add faces from images
- List authorized faces
- Remove faces
"""

import sys
import argparse
from pathlib import Path
import face_recognition
import cv2
import config as cfg


def add_face(image_path, name=None):
    """
    Add a face to the authorized faces database
    
    Args:
        image_path: Path to image file
        name: Name for the person (if None, uses filename)
    """
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"Error: Image file not found: {image_path}")
        return False
    
    config = cfg.load_config()
    faces_dir = Path(config['faces_directory'])
    faces_dir.mkdir(exist_ok=True)
    
    # Use provided name or filename
    if name is None:
        name = image_path.stem
    
    # Check if face exists in image
    try:
        image = face_recognition.load_image_file(str(image_path))
        encodings = face_recognition.face_encodings(image)
        
        if not encodings:
            print(f"Error: No face found in {image_path}")
            return False
        
        if len(encodings) > 1:
            print(f"Warning: Multiple faces found in {image_path}. Using the first one.")
        
        # Save to faces directory
        output_path = faces_dir / f"{name}{image_path.suffix}"
        
        # Copy image
        import shutil
        shutil.copy2(image_path, output_path)
        
        print(f"✓ Added face: {name}")
        print(f"  Saved to: {output_path}")
        return True
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return False


def list_faces():
    """List all authorized faces"""
    config = cfg.load_config()
    faces_dir = Path(config['faces_directory'])
    
    if not faces_dir.exists():
        print("No faces directory found.")
        return
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    faces = [f for f in faces_dir.iterdir() if f.suffix.lower() in image_extensions]
    
    if not faces:
        print("No authorized faces found.")
        return
    
    print(f"\nAuthorized Faces ({len(faces)}):")
    print("-" * 40)
    for face_file in sorted(faces):
        print(f"  - {face_file.stem}")
    print()


def remove_face(name):
    """Remove a face from the authorized database"""
    config = cfg.load_config()
    faces_dir = Path(config['faces_directory'])
    
    if not faces_dir.exists():
        print("No faces directory found.")
        return False
    
    # Find matching files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    matches = []
    
    for ext in image_extensions:
        face_file = faces_dir / f"{name}{ext}"
        if face_file.exists():
            matches.append(face_file)
    
    if not matches:
        print(f"No face found with name: {name}")
        return False
    
    for match in matches:
        match.unlink()
        print(f"✓ Removed: {name}")
    
    return True


def capture_face_from_camera(name):
    """Capture a face directly from camera"""
    from picamera2 import Picamera2
    import time
    
    print(f"Capturing face for: {name}")
    print("Position yourself in front of the camera...")
    
    camera = Picamera2()
    camera_config = camera.create_preview_configuration(
        main={"size": (1280, 720)},
        format="RGB888"
    )
    camera.configure(camera_config)
    camera.start()
    time.sleep(2)
    
    print("Press SPACE to capture, ESC to cancel")
    
    try:
        while True:
            frame = camera.capture_array()
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Try to detect face
            rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            
            if face_locations:
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(frame_bgr, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame_bgr, "Face detected - Press SPACE", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame_bgr, "No face detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.imshow("Capture Face", frame_bgr)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # Space to capture
                if face_locations:
                    # Save image
                    config = cfg.load_config()
                    faces_dir = Path(config['faces_directory'])
                    faces_dir.mkdir(exist_ok=True)
                    
                    output_path = faces_dir / f"{name}.jpg"
                    cv2.imwrite(str(output_path), frame_bgr)
                    print(f"✓ Face captured and saved: {output_path}")
                    break
                else:
                    print("No face detected. Please try again.")
            elif key == 27:  # ESC to cancel
                print("Cancelled.")
                break
    
    finally:
        camera.stop()
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description='Manage authorized faces database')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Add face command
    add_parser = subparsers.add_parser('add', help='Add a face from image file')
    add_parser.add_argument('image', help='Path to image file')
    add_parser.add_argument('-n', '--name', help='Name for the person')
    
    # Capture from camera
    capture_parser = subparsers.add_parser('capture', help='Capture face from camera')
    capture_parser.add_argument('name', help='Name for the person')
    
    # List faces
    subparsers.add_parser('list', help='List all authorized faces')
    
    # Remove face
    remove_parser = subparsers.add_parser('remove', help='Remove a face')
    remove_parser.add_argument('name', help='Name of the person to remove')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        add_face(args.image, args.name)
    elif args.command == 'capture':
        capture_face_from_camera(args.name)
    elif args.command == 'list':
        list_faces()
    elif args.command == 'remove':
        remove_face(args.name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

