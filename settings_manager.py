"""
Settings Page Module - User preferences and app configuration

Settings include:
- Audio speed (50-300 wpm)
- Audio volume (0-100%)
- Default language (English, Hindi, Marathi)
- Default braille grade (1, 2, 3)
- Embosser format (80 or 40 chars per line)
- Auto-save history (on/off)
- Enable speech recognition (on/off)
- Keyboard hotkey customization
- Theme preferences
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


class SettingsManager:
    """Manage application settings and user preferences."""
    
    # Default settings
    DEFAULT_SETTINGS = {
        # Audio settings
        "audio_speed": 150,  # Words per minute (50-300)
        "audio_volume": 1.0,  # 0-1 scale
        "audio_language": "English",
        
        # Braille settings
        "braille_grade": 2,  # 1, 2, or 3
        "braille_language": "English",
        
        # Embosser settings
        "embosser_chars_per_line": 80,  # 40 or 80
        "embosser_format": "standard",  # standard or compact
        
        # App behavior
        "auto_save_history": True,
        "history_limit": 1000,
        "auto_convert": True,
        "dark_mode": True,
        
        # Features
        "enable_speech_recognition": True,
        "enable_audio_export": True,
        "enable_ocr": True,
        "enable_learning": False,
        
        # Keyboard shortcuts (can be customized)
        "shortcuts": {
            "speak_output": "Ctrl+Shift+S",
            "copy_output": "Ctrl+3",
            "show_history": "Ctrl+Shift+H",
            "add_favorite": "Ctrl+Shift+F",
            "help": "F1",
        },
        
        # Accessibility
        "screen_reader_enabled": True,
        "keyboard_only_mode": False,
        "high_contrast": False,
        
        # Developer
        "debug_mode": False,
        "log_conversions": True,
    }
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize settings manager.
        
        Args:
            config_dir: Directory to store settings (default: ~/.braille_converter)
        """
        if config_dir is None:
            config_dir = os.path.expanduser("~/.braille_converter")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.settings_file = self.config_dir / "settings.json"
        self.settings = self.DEFAULT_SETTINGS.copy()
        
        # Load existing settings
        self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults (keep new defaults if config is old)
                    self.settings = {**self.DEFAULT_SETTINGS, **loaded}
                    return self.settings
        except Exception as e:
            print(f"⚠️ Warning: Could not load settings: {e}")
        
        return self.settings
    
    def save_settings(self, settings: Optional[Dict] = None) -> bool:
        """
        Save settings to file.
        
        Args:
            settings: Settings dict (uses current if None)
        
        Returns:
            Success status
        """
        try:
            if settings:
                self.settings = {**self.DEFAULT_SETTINGS, **settings}
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ Error saving settings: {e}")
            return False
    
    def get_setting(self, key: str, default=None) -> Any:
        """Get a single setting value."""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set a single setting value and save.
        
        Args:
            key: Setting key
            value: New value
        
        Returns:
            Success status
        """
        self.settings[key] = value
        return self.save_settings()
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults."""
        self.settings = self.DEFAULT_SETTINGS.copy()
        return self.save_settings()
    
    def validate_setting(self, key: str, value: Any) -> Tuple[bool, str]:
        """
        Validate a setting value before applying.
        
        Args:
            key: Setting key
            value: Value to validate
        
        Returns:
            (is_valid, error_message)
        """
        # Audio speed validation
        if key == "audio_speed":
            if not isinstance(value, (int, float)) or not (50 <= value <= 300):
                return False, "Audio speed must be between 50-300 wpm"
        
        # Audio volume validation
        elif key == "audio_volume":
            if not isinstance(value, (int, float)) or not (0 <= value <= 1):
                return False, "Audio volume must be between 0-1"
        
        # Language validation
        elif key in ["audio_language", "braille_language"]:
            valid_languages = ["English", "Hindi", "Marathi"]
            if value not in valid_languages:
                return False, f"Language must be one of: {', '.join(valid_languages)}"
        
        # Braille grade validation
        elif key == "braille_grade":
            if value not in [1, 2, 3]:
                return False, "Braille grade must be 1, 2, or 3"
        
        # Embosser format validation
        elif key == "embosser_chars_per_line":
            if value not in [40, 80]:
                return False, "Embosser chars per line must be 40 or 80"
        
        # History limit validation
        elif key == "history_limit":
            if not isinstance(value, int) or value < 100:
                return False, "History limit must be at least 100"
        
        return True, ""
    
    def get_audio_config(self) -> Dict[str, Any]:
        """Get audio-related settings."""
        return {
            "speed": self.get_setting("audio_speed"),
            "volume": self.get_setting("audio_volume"),
            "language": self.get_setting("audio_language"),
        }
    
    def get_braille_config(self) -> Dict[str, Any]:
        """Get braille-related settings."""
        return {
            "grade": self.get_setting("braille_grade"),
            "language": self.get_setting("braille_language"),
            "embosser_width": self.get_setting("embosser_chars_per_line"),
        }
    
    def get_keyboard_shortcuts(self) -> Dict[str, str]:
        """Get all keyboard shortcuts."""
        return self.get_setting("shortcuts", {})
    
    def set_keyboard_shortcut(self, action: str, shortcut: str) -> bool:
        """
        Set a keyboard shortcut.
        
        Args:
            action: Action name (e.g., 'speak_output')
            shortcut: Shortcut key combo (e.g., 'Ctrl+Shift+S')
        
        Returns:
            Success status
        """
        shortcuts = self.get_setting("shortcuts", {})
        shortcuts[action] = shortcut
        return self.set_setting("shortcuts", shortcuts)
    
    def get_status(self) -> Dict[str, Any]:
        """Get settings manager status."""
        return {
            "config_file": str(self.settings_file),
            "file_exists": self.settings_file.exists(),
            "total_settings": len(self.settings),
            "status": "✅ Ready"
        }
    
    def export_settings(self, export_path: str) -> Tuple[bool, str]:
        """
        Export settings to a file.
        
        Args:
            export_path: Where to save exported settings
        
        Returns:
            (success, message)
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            return True, f"✅ Settings exported to {export_path}"
        except Exception as e:
            return False, f"❌ Export failed: {str(e)}"
    
    def import_settings(self, import_path: str) -> Tuple[bool, str]:
        """
        Import settings from a file.
        
        Args:
            import_path: Path to settings file to import
        
        Returns:
            (success, message)
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            
            # Validate all imported settings
            for key, value in imported.items():
                is_valid, error = self.validate_setting(key, value)
                if not is_valid:
                    return False, f"❌ Invalid setting {key}: {error}"
            
            self.settings = {**self.DEFAULT_SETTINGS, **imported}
            self.save_settings()
            return True, f"✅ Settings imported from {import_path}"
        
        except Exception as e:
            return False, f"❌ Import failed: {str(e)}"
    
    def print_summary(self):
        """Print a summary of all settings."""
        print("\n" + "=" * 70)
        print("⚙️  CURRENT SETTINGS")
        print("=" * 70)
        
        categories = {
            "AUDIO": ["audio_speed", "audio_volume", "audio_language"],
            "BRAILLE": ["braille_grade", "braille_language", "embosser_chars_per_line"],
            "APP BEHAVIOR": ["auto_save_history", "auto_convert", "dark_mode"],
            "FEATURES": ["enable_speech_recognition", "enable_audio_export", "enable_ocr"],
            "ACCESSIBILITY": ["screen_reader_enabled", "keyboard_only_mode"],
        }
        
        for category, keys in categories.items():
            print(f"\n{category}:")
            for key in keys:
                value = self.get_setting(key)
                print(f"  • {key}: {value}")
        
        print("\n" + "=" * 70)


# Global instance
settings_manager = SettingsManager()

def get_setting(key: str, default=None):
    """Module-level wrapper for get_setting."""
    return settings_manager.get_setting(key, default)

def set_setting(key: str, value: Any) -> bool:
    """Module-level wrapper for set_setting."""
    return settings_manager.set_setting(key, value)

def get_all_settings() -> Dict[str, Any]:
    """Module-level wrapper for getting all settings."""
    return settings_manager.settings


# Type hints
from typing import Tuple


if __name__ == "__main__":
    print("=" * 70)
    print("SETTINGS MODULE")
    print("=" * 70)
    print()
    
    # Test settings manager
    manager = SettingsManager()
    
    print("✅ Settings loaded from:", manager.settings_file)
    print()
    
    # Show current settings
    manager.print_summary()
    print()
    
    # Test setting a value
    print("Testing: Set audio speed to 200 wpm")
    manager.set_setting("audio_speed", 200)
    print(f"Audio speed now: {manager.get_setting('audio_speed')} wpm")
    print()
    
    # Test validation
    print("Testing: Validate audio speed of 350 (should fail)")
    is_valid, error = manager.validate_setting("audio_speed", 350)
    print(f"Valid: {is_valid}, Error: {error}")
    print()
    
    # Test status
    status = manager.get_status()
    print("Status:", status)
    print()
    
    print("=" * 70)
    print("✅ Settings Module Ready!")
    print("=" * 70)
