#!/usr/bin/env python3
"""
Configuration management for security system
"""

import json
from pathlib import Path


def load_config(config_file='config.json'):
    """
    Load configuration from JSON file
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    config_path = Path(config_file)
    
    # Default configuration
    default_config = {
        "camera_type": "pi_camera",
        "camera_resolution": [1280, 720],
        "camera_fps": 9,
        "usb_camera_index": 0,
        "faces_directory": "authorized_faces",
        "unauthorized_directory": "unauthorized_detections",
        "location": "Room",
        "display": True,
        "process_every_n_frames": 2,
        "face_recognition_tolerance": 0.6,
        "detection_cooldown": 30,
        "unauthorized_delay": 5,
        "repeat_offender_delay": 1,
        "unauthorized_memory_time": 3600,
        "motion_detection_enabled": True,
        "motion_threshold": 5000,
        "motion_check_interval": 10,
        "scan_interval_motion": 20,
        "scan_interval_no_motion": 40,
        "min_processing_interval": 0.5,
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "sender_password": "",
            "recipient_email": ""
        }
    }
    
    # Load from file if exists
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                # Merge with defaults
                default_config.update(user_config)
                # Deep merge for nested dicts
                if 'email' in user_config:
                    default_config['email'].update(user_config['email'])
        except Exception as e:
            print(f"Error loading config file: {e}")
            print("Using default configuration")
    else:
        # Create default config file
        print(f"Config file not found. Creating default {config_file}...")
        save_config(default_config, config_file)
        print("Please edit config.json to configure your settings")
    
    return default_config


def save_config(config, config_file='config.json'):
    """Save configuration to JSON file"""
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

