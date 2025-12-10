#!/usr/bin/env python3
"""
Raspberry Pi 5 with Hailo Card and RPi Camera Example

This script demonstrates:
1. Capturing frames from the Raspberry Pi camera
2. Processing frames with the Hailo AI accelerator
3. Displaying results (if display available)
"""

import cv2
import numpy as np
from picamera2 import Picamera2
import time
import sys

try:
    from hailo_platform import Device, VStreams, ConfigureParams, InferVStreams
    HAILO_AVAILABLE = True
except ImportError:
    print("Warning: Hailo platform library not found. Install Hailo runtime.")
    HAILO_AVAILABLE = False


class HailoCameraProcessor:
    def __init__(self, model_path=None, camera_resolution=(640, 480)):
        """
        Initialize Hailo camera processor
        
        Args:
            model_path: Path to Hailo model file (.hef)
            camera_resolution: Tuple of (width, height) for camera capture
        """
        self.model_path = model_path
        self.camera_resolution = camera_resolution
        self.device = None
        self.network_group = None
        self.input_vstreams = None
        self.output_vstreams = None
        
        # Initialize camera
        self.camera = Picamera2()
        self.setup_camera()
        
        # Initialize Hailo if available
        if HAILO_AVAILABLE and model_path:
            self.setup_hailo()
    
    def setup_camera(self):
        """Configure and start the Raspberry Pi camera"""
        print("Setting up camera...")
        
        # Configure camera with higher FPS (30 FPS for faster checking)
        camera_config = self.camera.create_preview_configuration(
            main={"size": self.camera_resolution},
            format="RGB888",
            controls={"FrameRate": 30}
        )
        self.camera.configure(camera_config)
        self.camera.start()
        
        # Allow camera to stabilize
        time.sleep(2)
        print(f"Camera initialized at {self.camera_resolution} @ 30 FPS")
    
    def setup_hailo(self):
        """Initialize Hailo device and load model"""
        if not HAILO_AVAILABLE:
            print("Hailo library not available")
            return
        
        try:
            print("Initializing Hailo device...")
            # Scan for available Hailo devices
            devices = Device.scan()
            if not devices:
                print("No Hailo devices found!")
                return
            
            self.device = Device(devices[0])
            print(f"Hailo device found: {devices[0]}")
            
            if self.model_path:
                print(f"Loading model: {self.model_path}")
                self.network_group = self.device.configure(self.model_path)
                print("Model loaded successfully")
                
                # Get input and output vstreams
                self.input_vstreams, self.output_vstreams = \
                    self.network_group.create_vstreams()
                print("Hailo initialized successfully")
            else:
                print("No model path provided, running in camera-only mode")
                
        except Exception as e:
            print(f"Error initializing Hailo: {e}")
            self.device = None
    
    def capture_frame(self):
        """Capture a frame from the camera"""
        frame = self.camera.capture_array()
        return frame
    
    def process_with_hailo(self, frame):
        """Process frame with Hailo accelerator"""
        if not self.device or not self.network_group:
            return None, None
        
        try:
            # Prepare input (adjust based on your model requirements)
            # This is a placeholder - adjust based on your specific model
            input_data = {name: frame for name in self.input_vstreams.keys()}
            
            # Run inference
            with InferVStreams(self.network_group, self.input_vstreams, 
                            self.output_vstreams) as infer_pipeline:
                output = infer_pipeline.infer(input_data)
            
            return output, None
        except Exception as e:
            print(f"Error during inference: {e}")
            return None, str(e)
    
    def draw_results(self, frame, results):
        """Draw inference results on frame"""
        # Placeholder for drawing results
        # Customize based on your model's output format
        if results:
            cv2.putText(frame, "Hailo Processing Active", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return frame
    
    def run(self, display=True, max_frames=None):
        """Main processing loop"""
        print("Starting camera capture loop...")
        print("Press Ctrl+C to stop")
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                if max_frames and frame_count >= max_frames:
                    break
                
                # Capture frame
                frame = self.capture_frame()
                
                # Process with Hailo if available
                if self.device:
                    results, error = self.process_with_hailo(frame)
                    if error:
                        print(f"Inference error: {error}")
                    else:
                        frame = self.draw_results(frame, results)
                else:
                    # Just show camera feed
                    cv2.putText(frame, "Camera Only Mode", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                # Display frame
                if display:
                    cv2.imshow("RPi Camera + Hailo", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                frame_count += 1
                
                # Print FPS every 30 frames
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"FPS: {fps:.2f}")
        
        except KeyboardInterrupt:
            print("\nStopping...")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        if self.camera:
            self.camera.stop()
        if self.device:
            self.device.release()
        cv2.destroyAllWindows()
        print("Cleanup complete")


def main():
    """Main entry point"""
    print("=" * 50)
    print("Raspberry Pi 5 + Hailo Card + RPi Camera Example")
    print("=" * 50)
    
    # Configuration
    # Set your Hailo model path here, or None for camera-only mode
    MODEL_PATH = None  # e.g., "/path/to/your/model.hef"
    CAMERA_RESOLUTION = (640, 480)
    
    # Create processor
    processor = HailoCameraProcessor(
        model_path=MODEL_PATH,
        camera_resolution=CAMERA_RESOLUTION
    )
    
    # Run processing loop
    processor.run(display=True)


if __name__ == "__main__":
    main()

