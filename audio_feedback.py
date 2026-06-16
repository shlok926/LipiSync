# audio_feedback.py — Text-to-Speech conversion for braille & text output

import pyttsx3
from threading import Thread
from typing import Optional

class AudioFeedback:
    """Handles TTS (Text-to-Speech) for accessibility."""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed: 150 wpm
        self.engine.setProperty('volume', 0.9)  # Volume 0-1
        self.is_playing = False
        
    def speak(self, text: str, language: str = 'en', wait: bool = False):
        """
        Speak the given text asynchronously.
        
        Args:
            text: Text to speak
            language: 'en' for English, 'hi' for Hindi/Marathi
            wait: If True, blocks until speech finishes
        """
        if not text.strip():
            return
            
        try:
            # Set voice language
            voices = self.engine.getProperty('voices')
            if language == 'hi':
                # Try Hindi voice if available
                for voice in voices:
                    if 'hindi' in voice.name.lower() or 'hindi' in voice.languages:
                        self.engine.setProperty('voice', voice.id)
                        break
            else:
                self.engine.setProperty('voice', voices[0].id)
            
            self.is_playing = True
            self.engine.say(text)
            
            if wait:
                self.engine.runAndWait()
            else:
                # Run in background thread
                Thread(target=self.engine.runAndWait, daemon=True).start()
                
        except Exception as e:
            print(f"Audio error: {e}")
            
    def stop(self):
        """Stop current speech."""
        try:
            self.engine.stop()
            self.is_playing = False
        except:
            pass
    
    def set_rate(self, wpm: int):
        """Set speech rate in words per minute (50-300)."""
        wpm = max(50, min(300, wpm))
        self.engine.setProperty('rate', wpm)
    
    def set_volume(self, level: float):
        """Set volume 0.0 to 1.0."""
        level = max(0.0, min(1.0, level))
        self.engine.setProperty('volume', level)

# Global instance
audio_engine = AudioFeedback()

def speak_text(text: str, language: str = 'en'):
    """Quick function to speak text."""
    audio_engine.speak(text, language)

def stop_audio():
    """Stop current audio playback."""
    audio_engine.stop()
