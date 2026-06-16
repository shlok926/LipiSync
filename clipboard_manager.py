# clipboard_manager.py — System clipboard integration & global hotkeys

import pyperclip
import threading
import time
from typing import Callable, Optional
from enum import Enum

class ClipboardMode(Enum):
    TEXT_TO_BRAILLE = 1
    BRAILLE_TO_TEXT = 2
    TOGGLE = 3

class ClipboardManager:
    """
    Manages system clipboard for quick conversions.
    Integrates with system clipboard for instant access.
    """
    
    def __init__(self):
        self.last_clipboard = ""
        self.monitoring = False
        self.monitor_thread = None
        self.callback = None
    
    def get_clipboard_text(self) -> str:
        """Get current clipboard content."""
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"Clipboard read error: {e}")
            return ""
    
    def set_clipboard_text(self, text: str) -> bool:
        """Set clipboard content. Returns success status."""
        try:
            pyperclip.copy(text)
            return True
        except Exception as e:
            print(f"Clipboard write error: {e}")
            return False
    
    def quick_convert_clipboard(self, convert_func: Callable) -> Tuple[str, bool]:
        """
        Convert clipboard content using given function.
        Returns (result, success)
        """
        try:
            text = self.get_clipboard_text()
            if not text:
                return "", False
            
            result = convert_func(text)
            return result, True
        
        except Exception as e:
            return f"Error: {str(e)}", False
    
    def convert_and_replace_clipboard(self, convert_func: Callable) -> bool:
        """Convert clipboard content and replace it. Returns success status."""
        result, success = self.quick_convert_clipboard(convert_func)
        
        if success:
            return self.set_clipboard_text(result)
        return False
    
    def start_clipboard_monitor(self, callback: Callable):
        """
        Start monitoring clipboard for changes.
        Useful for real-time sync with other apps.
        """
        self.monitoring = True
        self.callback = callback
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_clipboard_monitor(self):
        """Stop clipboard monitoring."""
        self.monitoring = False
    
    def _monitor_loop(self):
        """Background loop that monitors clipboard changes."""
        while self.monitoring:
            try:
                current = self.get_clipboard_text()
                
                if current != self.last_clipboard and current:
                    self.last_clipboard = current
                    
                    if self.callback:
                        self.callback(current)
                
                time.sleep(0.5)  # Check every 500ms
            
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(1)

class HotkeyManager:
    """
    Manages global hotkeys for quick conversions.
    Note: keyboard library required for global hotkeys.
    """
    
    def __init__(self):
        self.hotkeys_registered = {}
        try:
            import keyboard
            self.keyboard = keyboard
            self.keyboard_available = True
        except ImportError:
            self.keyboard = None
            self.keyboard_available = False
    
    def register_hotkey(self, key_combination: str, callback: Callable) -> bool:
        """
        Register a global hotkey.
        
        Args:
            key_combination: e.g. 'ctrl+shift+b' for convert clipboard
            callback: Function to call when hotkey is pressed
        
        Returns: Success status
        """
        if not self.keyboard_available:
            print("keyboard library not available for global hotkeys")
            return False
        
        try:
            self.keyboard.add_hotkey(key_combination, callback)
            self.hotkeys_registered[key_combination] = callback
            return True
        
        except Exception as e:
            print(f"Hotkey registration error: {e}")
            return False
    
    def unregister_hotkey(self, key_combination: str) -> bool:
        """Unregister a hotkey."""
        if not self.keyboard_available:
            return False
        
        try:
            self.keyboard.remove_hotkey(key_combination)
            self.hotkeys_registered.pop(key_combination, None)
            return True
        
        except Exception as e:
            print(f"Hotkey unregistration error: {e}")
            return False
    
    def list_registered_hotkeys(self) -> dict:
        """Get all registered hotkeys."""
        return self.hotkeys_registered.copy()

class QuickAccessPanel:
    """
    Quick access buttons/shortcuts for common operations.
    (UI integration handled in main UI module)
    """
    
    QUICK_ACTIONS = {
        'convert_clipboard_t2b': {
            'label': 'Clipboard: Text→Braille',
            'icon': '📋',
            'tooltip': 'Convert clipboard text to Braille',
            'hotkey': 'ctrl+shift+t',
        },
        'convert_clipboard_b2t': {
            'label': 'Clipboard: Braille→Text',
            'icon': '📋',
            'tooltip': 'Convert clipboard Braille to text',
            'hotkey': 'ctrl+shift+b',
        },
        'paste_and_convert': {
            'label': 'Paste & Convert',
            'icon': '📌',
            'tooltip': 'Paste from clipboard and auto-convert',
            'hotkey': 'ctrl+shift+p',
        },
        'clear_all': {
            'label': 'Clear',
            'icon': '🗑️',
            'tooltip': 'Clear all text',
            'hotkey': 'ctrl+shift+c',
        },
        'copy_result': {
            'label': 'Copy Result',
            'icon': '📋',
            'tooltip': 'Copy conversion result to clipboard',
            'hotkey': 'ctrl+shift+o',
        },
    }
    
    @staticmethod
    def get_quick_actions() -> dict:
        """Get all quick access actions."""
        return QuickAccessPanel.QUICK_ACTIONS.copy()
    
    @staticmethod
    def get_hotkeys() -> dict:
        """Extract hotkeys from actions."""
        hotkeys = {}
        for action_id, action_data in QuickAccessPanel.QUICK_ACTIONS.items():
            if 'hotkey' in action_data:
                hotkeys[action_data['hotkey']] = action_id
        return hotkeys

# Global instances
clipboard_manager = ClipboardManager()
hotkey_manager = HotkeyManager()
quick_panel = QuickAccessPanel()

def quick_convert_clipboard_text_to_braille() -> str:
    """Quick function for hotkey."""
    result, _ = clipboard_manager.quick_convert_clipboard(
        lambda t: __import__('braille_engine').text_to_braille(t)
    )
    return result

def quick_convert_clipboard_braille_to_text() -> str:
    """Quick function for hotkey."""
    result, _ = clipboard_manager.quick_convert_clipboard(
        lambda t: __import__('braille_engine').braille_to_text(t)
    )
    return result
