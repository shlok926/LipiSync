"""
Speech-to-Braille Recognition Module

Converts spoken audio to Braille text using:
- Speech Recognition: speech_recognition library (Google API) [Optional]
- Text-to-Braille: Existing braille_engine.py
"""

from braille_engine import text_to_braille
from typing import Optional, Tuple

# Try to import speech_recognition, but make it optional
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    pass


class SpeechToBrailleConverter:
    """Convert speech audio to Braille text."""
    
    def __init__(self):
        """Initialize speech recognizer."""
        self.recognizer = None
        self.microphone = None
        self.microphone_available = False

        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            try:
                self.microphone = sr.Microphone()
                self.microphone_available = True
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            except Exception:
                self.microphone = None
                self.microphone_available = False
                print("WARNING: Microphone not available")
        
        self.last_recognized_text = ""
        self.last_braille_output = ""
    
    def recognize_from_microphone(self, language: str = "en-US", timeout: int = 10) -> Optional[str]:
        """
        Recognize speech from microphone in real-time.
        
        Args:
            language: Language code (en-US, hi-IN, etc.)
            timeout: Max seconds to listen
        
        Returns:
            Recognized text or None if failed
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            print("ERROR: speech_recognition not installed")
            print("   Install: pip install SpeechRecognition")
            return None

        if not self.microphone_available or self.microphone is None:
            print("ERROR: Microphone not available. Install PyAudio or use audio file recognition.")
            return None
        
        try:
            print("Listening... (speak now)")
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=30)
            
            print("Processing speech...")
            text = self.recognizer.recognize_google(audio, language=language)
            self.last_recognized_text = text
            print(f"Recognized: {text}")
            return text
            
        except Exception as e:
            print(f"ERROR: {e}")
            return None
    
    def recognize_from_file(self, file_path: str, language: str = "en-US") -> Optional[str]:
        """Recognize speech from audio file."""
        if not SPEECH_RECOGNITION_AVAILABLE:
            print("ERROR: speech_recognition not installed")
            return None
        
        try:
            from pathlib import Path
            if not Path(file_path).exists():
                print(f"ERROR: File not found: {file_path}")
                return None
            
            print(f"Reading audio file: {file_path}")
            
            if file_path.endswith(('.wav', '.flac')):
                with sr.AudioFile(file_path) as source:
                    audio = self.recognizer.record(source)
            else:
                print("ERROR: Unsupported format. Use WAV or FLAC")
                return None
            
            print("Processing audio...")
            text = self.recognizer.recognize_google(audio, language=language)
            self.last_recognized_text = text
            print(f"Recognized: {text}")
            return text
            
        except Exception as e:
            print(f"ERROR: {e}")
            return None
    
    def speech_to_braille(
        self, 
        text: str, 
        language_braille: str = "English"
    ) -> Optional[str]:
        """
        Convert recognized speech text to Braille.
        
        Args:
            text: Recognized text from speech
            language_braille: Output braille language (e.g., "Hindi")
        
        Returns:
            Braille text or None
        """
        try:
            if not text:
                print("ERROR: No text to convert")
                return None
            
            print(f"Input text: {text}")
            print(f"Converting to {language_braille} Braille...")
            
            braille = text_to_braille(text, language_braille)
            self.last_braille_output = braille
            
            print(f"Braille output (length: {len(braille)} chars)")
            return braille
            
        except Exception as e:
            print(f"ERROR: Conversion error: {e}")
            return None
    
    def speech_to_braille_live(
        self,
        language_input: str = "en-US",
        language_braille: str = "English",
        timeout: int = 10
    ) -> Tuple[Optional[str], Optional[str]]:
        """Live speech recognition and conversion to Braille."""
        recognized_text = self.recognize_from_microphone(
            language=language_input,
            timeout=timeout
        )
        
        if not recognized_text:
            return None, None
        
        braille = self.speech_to_braille(
            recognized_text,
            language_braille=language_braille
        )
        
        return recognized_text, braille
    
    def get_language_codes(self) -> dict:
        """Get supported language codes for speech recognition."""
        return {
            "English (US)": "en-US",
            "English (UK)": "en-GB",
            "Hindi": "hi-IN",
            "Marathi": "mr-IN",
            "Spanish": "es-ES",
            "French": "fr-FR",
            "German": "de-DE",
            "Chinese": "zh-CN",
            "Japanese": "ja-JP",
            "Korean": "ko-KR",
        }
    
    def get_statistics(self) -> dict:
        """Get statistics about last conversion."""
        return {
            "last_recognized_text": self.last_recognized_text,
            "last_recognized_length": len(self.last_recognized_text),
            "last_braille_output": self.last_braille_output,
            "last_braille_length": len(self.last_braille_output),
            "compression_ratio": (
                f"{100 - (len(self.last_braille_output) / max(1, len(self.last_recognized_text)) * 100):.1f}%"
                if self.last_recognized_text else "N/A"
            ),
            "speech_recognition_available": SPEECH_RECOGNITION_AVAILABLE
        }
    
    def get_status(self) -> dict:
        """Get current status of the module."""
        return {
            "speech_recognition_available": SPEECH_RECOGNITION_AVAILABLE,
            "microphone_available": self.microphone_available,
            "supported_languages": len(self.get_language_codes()),
            "status": (
                "Ready (speech recognition + microphone)"
                if SPEECH_RECOGNITION_AVAILABLE and self.microphone_available
                else "Limited (speech recognition only; microphone unavailable)"
                if SPEECH_RECOGNITION_AVAILABLE
                else "Limited (Install: pip install SpeechRecognition)"
            )
        }


# Global instance
speech_converter = SpeechToBrailleConverter()


if __name__ == "__main__":
    print("=" * 60)
    print("SPEECH-TO-BRAILLE MODULE")
    print("=" * 60)
    print()
    
    # Show status
    status = speech_converter.get_status()
    print(f"Status: {status['status']}")
    print(f"Languages: {status['supported_languages']}")
    print()
    
    # Example: Simulated speech-to-braille
    print("Example: Simulated Speech-to-Braille")
    print("-" * 60)
    simulated_speech = "Hello World"
    print(f"Simulated spoken text: '{simulated_speech}'")
    
    braille = speech_converter.speech_to_braille(
        simulated_speech,
        language_braille="English"
    )
    
    if braille:
        print("Conversion successful!")
        stats = speech_converter.get_statistics()
        print(f"   Stats: {stats}")

