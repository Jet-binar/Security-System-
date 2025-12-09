#!/usr/bin/env python3
"""
Voice features for security system
- Text-to-speech announcements
- Future: Voice recognition and responses
"""

import pyttsx3
import threading
import queue


class VoiceSystem:
    """Voice system for security announcements"""
    
    def __init__(self):
        """Initialize voice system"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Speech rate
            self.engine.setProperty('volume', 0.8)  # Volume (0.0 to 1.0)
            
            # Queue for voice messages
            self.message_queue = queue.Queue()
            self.is_speaking = False
            
            # Start voice thread
            self.voice_thread = threading.Thread(target=self._voice_worker, daemon=True)
            self.voice_thread.start()
            
            print("Voice system initialized")
        except Exception as e:
            print(f"Warning: Voice system not available: {e}")
            self.engine = None
    
    def _voice_worker(self):
        """Worker thread for voice announcements"""
        while True:
            try:
                message = self.message_queue.get(timeout=1)
                if self.engine:
                    self.is_speaking = True
                    self.engine.say(message)
                    self.engine.runAndWait()
                    self.is_speaking = False
                self.message_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in voice worker: {e}")
                self.is_speaking = False
    
    def speak(self, message):
        """Queue a message to be spoken"""
        if self.engine:
            self.message_queue.put(message)
        else:
            print(f"[Voice]: {message}")
    
    def speak_unauthorized(self):
        """Announce unauthorized person detection"""
        import time
        messages = [
            "Who are you?",
            "What are you doing in my room?",
            "You are not authorized to be here.",
            "Security alert activated."
        ]
        for msg in messages:
            self.speak(msg)
            time.sleep(0.5)
    
    def speak_authorized(self, name):
        """Announce authorized person"""
        self.speak(f"Welcome, {name}")
    
    def stop(self):
        """Stop voice system"""
        if self.engine:
            self.engine.stop()


# Example usage and testing
if __name__ == "__main__":
    import time
    
    voice = VoiceSystem()
    
    print("Testing voice system...")
    voice.speak("Security system voice test")
    time.sleep(2)
    voice.speak_unauthorized()
    
    time.sleep(5)
    print("Voice test complete")

