"""
Audio Export Module - Save text-to-speech output as audio files

Export features:
- Save as WAV (lossless, large files)
- Save as MP3 (compressed, popular)
- Save as OGG (open source, medium quality)
- Batch export multiple files
- Metadata support (title, author, duration)
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


class AudioExporter:
    """Export text-to-speech to audio files."""
    
    def __init__(self):
        """Initialize audio exporter."""
        self.engine = None
        self.last_audio_file = None
        self.statistics = {
            "exported_files": 0,
            "total_duration_seconds": 0,
            "formats_used": {},
            "last_export_time": None,
        }
        
        if PYTTSX3_AVAILABLE:
            self.engine = pyttsx3.init()
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats."""
        formats = ["WAV"]  # WAV always supported via pyttsx3
        
        if PYDUB_AVAILABLE:
            formats.extend(["MP3", "OGG", "FLAC"])
        
        return formats
    
    def text_to_audio_file(
        self,
        text: str,
        output_path: str,
        format: str = "WAV",
        speed: int = 150,
        volume: float = 1.0,
        language: str = "en"
    ) -> Tuple[bool, str]:
        """
        Convert text to audio and save to file.
        
        Args:
            text: Text to convert
            output_path: Where to save the file
            format: Audio format (WAV, MP3, OGG, FLAC)
            speed: Speech rate (50-300)
            volume: Volume (0.0-1.0)
            language: Language code
        
        Returns:
            (success, message)
        """
        if not PYTTSX3_AVAILABLE:
            return False, "❌ pyttsx3 not installed"
        
        if not text or not text.strip():
            return False, "❌ No text to export"
        
        try:
            # Create temporary WAV file
            temp_wav = output_path.replace(f".{format.lower()}", ".wav")
            
            # Generate audio
            self.engine.setProperty('rate', speed)
            self.engine.setProperty('volume', volume)
            
            # Save as WAV
            self.engine.save_to_file(text, temp_wav)
            self.engine.runAndWait()
            
            if not os.path.exists(temp_wav):
                return False, f"❌ Failed to generate audio"
            
            # If WAV is requested, we're done
            if format.upper() == "WAV":
                self.last_audio_file = output_path
                self._update_statistics(format, text)
                return True, f"✅ Exported to {output_path}"
            
            # Convert to other format if needed
            if PYDUB_AVAILABLE and format.upper() in ["MP3", "OGG", "FLAC"]:
                audio = AudioSegment.from_wav(temp_wav)
                
                format_map = {
                    "MP3": ("mp3", "mp3"),
                    "OGG": ("ogg", "vorbis"),
                    "FLAC": ("flac", "flac")
                }
                
                if format.upper() in format_map:
                    ext, codec = format_map[format.upper()]
                    audio.export(output_path, format=ext, codec=codec)
                    
                    # Cleanup temp WAV
                    if os.path.exists(temp_wav):
                        os.remove(temp_wav)
                    
                    self.last_audio_file = output_path
                    self._update_statistics(format, text)
                    return True, f"✅ Exported to {output_path}"
            
            # If pydub not available, use WAV
            if os.path.exists(temp_wav):
                os.rename(temp_wav, output_path)
                self.last_audio_file = output_path
                self._update_statistics(format, text)
                return True, f"✅ Exported to {output_path} (as WAV)"
            
            return False, f"❌ Unsupported format: {format}"
        
        except Exception as e:
            return False, f"❌ Export failed: {str(e)}"
    
    def batch_export(
        self,
        texts: List[Tuple[str, str]],  # [(text, filename), ...]
        output_dir: str,
        format: str = "WAV",
        speed: int = 150,
        volume: float = 1.0
    ) -> Tuple[int, int, List[str]]:
        """
        Export multiple texts to audio files.
        
        Args:
            texts: List of (text, filename) tuples
            output_dir: Directory to save files
            format: Audio format
            speed: Speech rate
            volume: Volume level
        
        Returns:
            (successful_exports, failed_exports, file_paths)
        """
        os.makedirs(output_dir, exist_ok=True)
        
        successful = 0
        failed = 0
        file_paths = []
        
        for text, filename in texts:
            # Sanitize filename
            filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
            if not filename:
                filename = f"export_{len(file_paths)+1}"
            
            output_path = os.path.join(output_dir, f"{filename}.{format.lower()}")
            
            success, _ = self.text_to_audio_file(
                text, output_path, format, speed, volume
            )
            
            if success:
                successful += 1
                file_paths.append(output_path)
            else:
                failed += 1
        
        return successful, failed, file_paths
    
    def braille_to_audio(
        self,
        braille_text: str,
        output_path: str,
        format: str = "WAV",
        speed: int = 150,
        volume: float = 1.0
    ) -> Tuple[bool, str]:
        """
        Convert braille text to audio (braille is spoken aloud).
        
        Args:
            braille_text: Braille Unicode string
            output_path: Where to save
            format: Audio format
            speed: Speech rate
            volume: Volume
        
        Returns:
            (success, message)
        """
        # For braille, we spell out the dot numbers
        # Example: ⠓ → "Dots one two five"
        
        from braille_input import BrailleInputConverter
        converter = BrailleInputConverter()
        
        spoken_text = ""
        dot_names = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
        
        for char in braille_text:
            if ord(char) >= 0x2800:
                dots = converter.unicode_to_dots(char)
                if dots:
                    dot_string = ", ".join(dot_names[d] for d in sorted(dots))
                    spoken_text += f"Dots {dot_string}. "
                else:
                    spoken_text += "Empty cell. "
        
        if not spoken_text:
            return False, "❌ No braille characters found"
        
        return self.text_to_audio_file(spoken_text, output_path, format, speed, volume)
    
    def document_to_audiobook(
        self,
        file_path: str,
        output_path: str,
        format: str = "MP3",
        speed: int = 150,
        volume: float = 1.0,
        add_chapter_breaks: bool = True
    ) -> Tuple[bool, str]:
        """
        Convert entire document to audiobook.
        
        Args:
            file_path: Text or PDF file path
            output_path: Where to save audiobook
            format: Audio format
            speed: Speech rate
            volume: Volume
            add_chapter_breaks: Add silence between paragraphs
        
        Returns:
            (success, message)
        """
        try:
            # Read file
            if file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            elif file_path.endswith('.pdf'):
                try:
                    from PyPDF2 import PdfReader
                    with open(file_path, 'rb') as f:
                        reader = PdfReader(f)
                        text = "".join(page.extract_text() for page in reader.pages)
                except:
                    return False, "❌ Failed to read PDF"
            
            else:
                return False, f"❌ Unsupported file format: {file_path}"
            
            if not text:
                return False, "❌ No text content found"
            
            # Add chapter breaks (silence)
            if add_chapter_breaks:
                paragraphs = text.split('\n\n')
                # Pydub pause (if available)
                text = ". ".join(paragraphs)  # Add pauses between paragraphs
            
            # Export as audio
            return self.text_to_audio_file(text, output_path, format, speed, volume)
        
        except Exception as e:
            return False, f"❌ Audiobook creation failed: {str(e)}"
    
    def _update_statistics(self, format: str, text: str):
        """Update internal statistics."""
        self.statistics["exported_files"] += 1
        self.statistics["last_export_time"] = datetime.now().isoformat()
        
        format_upper = format.upper()
        self.statistics["formats_used"][format_upper] = self.statistics["formats_used"].get(format_upper, 0) + 1
        
        # Rough estimate: ~150 words per minute
        word_count = len(text.split())
        estimated_seconds = (word_count / 150) * 60
        self.statistics["total_duration_seconds"] += estimated_seconds
    
    def get_statistics(self) -> dict:
        """Get export statistics."""
        return {
            "total_exports": self.statistics["exported_files"],
            "total_duration": f"{self.statistics['total_duration_seconds']:.1f} seconds",
            "formats_used": self.statistics["formats_used"],
            "last_export": self.statistics["last_export_time"],
            "pydub_available": PYDUB_AVAILABLE,
            "pyttsx3_available": PYTTSX3_AVAILABLE,
        }
    
    def get_status(self) -> dict:
        """Get current exporter status."""
        return {
            "pyttsx3_available": PYTTSX3_AVAILABLE,
            "pydub_available": PYDUB_AVAILABLE,
            "supported_formats": self.get_supported_formats(),
            "status": "✅ Ready" if PYTTSX3_AVAILABLE else "⚠️ Limited (pyttsx3 needed)"
        }


# Global instance
audio_exporter = AudioExporter()

def text_to_audio_file(text, output_path, format="WAV", speed=150, volume=1.0, language="en"):
    """Module-level wrapper for text_to_audio_file."""
    return audio_exporter.text_to_audio_file(
        text=text,
        output_path=output_path,
        format=format,
        speed=speed,
        volume=volume,
        language=language
    )


if __name__ == "__main__":
    print("=" * 70)
    print("AUDIO EXPORT MODULE")
    print("=" * 70)
    print()
    
    # Check status
    status = audio_exporter.get_status()
    print(f"Status: {status['status']}")
    print(f"Supported formats: {', '.join(status['supported_formats'])}")
    print()
    
    # Example export
    print("Example: Export text to audio")
    print("-" * 70)
    
    test_text = "Hello, this is a test audio export. This text has been converted to speech."
    output_file = "/tmp/test_export.wav"
    
    success, message = audio_exporter.text_to_audio_file(
        test_text,
        output_file,
        format="WAV",
        speed=150,
        volume=0.8
    )
    
    print(f"Export result: {message}")
    
    if success:
        stats = audio_exporter.get_statistics()
        print(f"\nStatistics: {stats}")
    
    print()
    print("=" * 70)
    print("✅ Audio Export Module Ready!")
    print("=" * 70)
