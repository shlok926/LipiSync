# accessibility_features.py — Screen reader support & blind-friendly UI features

from typing import Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, QObject

class AccessibilityAnnouncer(QObject):
    """
    Announces UI changes for screen reader users.
    Works with JAWS, NVDA, Narrator, and other screen readers.
    """
    
    announcement = pyqtSignal(str)  # Signal to announce text to screen reader
    
    def __init__(self):
        super().__init__()
        self.last_announcement = ""
    
    def announce(self, text: str, priority: str = 'normal'):
        """
        Announce text to screen readers.
        
        Args:
            text: What to announce
            priority: 'normal', 'urgent', 'polite'
        
        Screen readers will read this text aloud.
        """
        if not text or text == self.last_announcement:
            return
        
        self.last_announcement = text
        self.announcement.emit(text)
        print(f"[ACCESSIBILITY] {text}")  # For debugging
    
    def announce_conversion(self, input_text: str, output_text: str, mode: str):
        """Announce a successful conversion."""
        announcement = f"Conversion complete. Input: {input_text[:50]}. Output: {output_text[:50]}"
        self.announce(announcement, 'polite')
    
    def announce_error(self, error_msg: str):
        """Announce an error."""
        self.announce(f"Error: {error_msg}", 'urgent')
    
    def announce_page_change(self, page_name: str):
        """Announce when user navigates to new page."""
        self.announce(f"Navigated to {page_name} page", 'polite')
    
    def announce_button_action(self, action: str):
        """Announce when a button is activated."""
        self.announce(f"Activated: {action}", 'normal')


class KeyboardShortcutManager:
    """
    Manages keyboard shortcuts for better accessibility.
    Allows blind users to navigate without mouse.
    """
    
    SHORTCUTS = {
        'Alt+1': 'Switch to Converter',
        'Alt+2': 'Switch to OCR',
        'Alt+3': 'Switch to Audio',
        'Alt+4': 'Switch to Grades',
        'Alt+5': 'Switch to Math',
        'Alt+6': 'Switch to Documents',
        'Alt+7': 'Switch to Live Preview',
        'Alt+8': 'Switch to Learning',
        'Alt+9': 'Switch to History',
        'Alt+0': 'Switch to Audit',
        'Ctrl+1': 'Convert',
        'Ctrl+2': 'Clear All',
        'Ctrl+3': 'Copy Output',
        'Ctrl+4': 'Paste Input',
        'Ctrl+Shift+S': 'Speak Output',
        'Ctrl+Shift+H': 'Show History',
        'Ctrl+Shift+F': 'Add to Favorites',
        'F1': 'Help/Keyboard Shortcuts',
    }
    
    @staticmethod
    def get_shortcuts() -> dict:
        """Get all keyboard shortcuts."""
        return KeyboardShortcutManager.SHORTCUTS.copy()
    
    @staticmethod
    def get_shortcut_help() -> str:
        """Generate help text for keyboard shortcuts."""
        help_text = "KEYBOARD SHORTCUTS FOR ACCESSIBILITY:\n\n"
        for shortcut, action in KeyboardShortcutManager.SHORTCUTS.items():
            help_text += f"{shortcut:<20} : {action}\n"
        return help_text


class TextDescriptionGenerator:
    """
    Generates detailed text descriptions of visual elements
    for blind/low-vision users.
    """
    
    @staticmethod
    def describe_braille_cell(dots: list[int]) -> str:
        """
        Describe a braille cell in text form.
        
        Example:
        Dots: [1, 4] → "Top-left and middle-right dots"
        """
        dot_positions = {
            1: "top-left",
            2: "middle-left",
            3: "bottom-left",
            4: "top-right",
            5: "middle-right",
            6: "bottom-right",
        }
        
        if not dots:
            return "Empty cell (space)"
        
        positions = [dot_positions[d] for d in sorted(dots)]
        if len(positions) == 1:
            return f"Braille cell with {positions[0]} dot"
        elif len(positions) == 2:
            return f"Braille cell with {positions[0]} and {positions[1]} dots"
        else:
            return f"Braille cell with dots at: {', '.join(positions)}"
    
    @staticmethod
    def describe_conversion_process(input_text: str, output_text: str, language: str) -> str:
        """
        Describe what happened during conversion in detail.
        """
        input_chars = len(input_text)
        output_chars = len(output_text)
        
        description = f"""
        CONVERSION SUMMARY:
        
        Input Language: {language}
        Input Text: {input_text[:100]}{'...' if len(input_text) > 100 else ''}
        Input Length: {input_chars} characters
        
        Output: Braille Unicode
        Output Length: {output_chars} characters
        
        Conversion Information:
        - Each character in '{language}' has been converted to its Braille equivalent
        - Braille characters are Unicode symbols from U+2800 to U+28FF range
        - This Braille can be:
          * Printed using a Braille embosser (creates physical tactile Braille)
          * Spoken aloud using text-to-speech
          * Converted back to text
        
        To use this Braille:
        1. Press Ctrl+Shift+S to hear it spoken
        2. Press Ctrl+3 to copy it to clipboard
        3. Send to Braille embosser to print physical Braille
        """
        return description.strip()
    
    @staticmethod
    def describe_page_features(page_name: str) -> str:
        """
        Describe what a page does in detail.
        """
        descriptions = {
            'Converter': """
            CONVERTER PAGE:
            - Main text-to-Braille conversion tool
            - Select language (English, Hindi, Marathi)
            - Choose mode: Text→Braille or Braille→Text
            - Type or paste input text
            - Press Convert or it auto-converts
            - Output shows in Braille format
            - Visual braille dots shown below (sighted users)
            - Use Ctrl+Shift+S to hear output spoken
            """,
            'Audio': """
            AUDIO PAGE:
            - Text-to-Speech conversion
            - Type any text
            - Press Play to hear it spoken
            - Adjust speed: use left/right arrows on speed slider
            - Adjust volume: use left/right arrows on volume slider
            - Press Stop to stop audio
            - Supports English, Hindi, and Marathi
            """,
            'Grades': """
            ADVANCED BRAILLE GRADES:
            - Grade 1: Full character mapping (basic)
            - Grade 2: Uses contractions (shorter, faster to read)
            - Grade 3: Maximum abbreviations (experimental)
            - Select grade from dropdown
            - Type text to convert
            - See which contractions were used
            """,
            'Math': """
            MATH & SCIENCE:
            - Convert mathematical equations to Braille
            - Examples: x², π, ±, ∑, √
            - Chemistry formulas: H₂O, CO₂
            - Quick symbol buttons for common math symbols
            - Type equation or paste it
            - See Braille conversion
            """,
            'Documents': """
            DOCUMENT PROCESSING:
            - Convert PDF files to Braille
            - Batch convert entire folders
            - Export in embosser format (ready to print)
            - Select PDF file or folder
            - Choose output location
            - Auto-converts all text to Braille
            """,
            'Learning': """
            BRAILLE LEARNING MODULE:
            - Interactive lessons for learning Braille
            - Progress bar shows completion
            - Lessons by difficulty level
            - Flashcard system for practice
            - Quizzes to test knowledge
            - Tracks your progress and scores
            """,
            'History': """
            HISTORY & FAVORITES:
            - All conversions are auto-saved
            - Search and filter history
            - Save favorite conversions
            - Tag your favorites
            - Import/export favorites
            - Never lose a conversion again
            """,
            'Audit': """
            ACCESSIBILITY AUDIT:
            - Check text for accessibility issues
            - Validate Braille conversions
            - Get improvement suggestions
            - Accessibility score 0-100
            - Identifies missing character mappings
            - Detailed recommendations
            """,
        }
        return descriptions.get(page_name, "Page information not available")


class BlindUserHelper:
    """
    Helper utilities specifically for blind users using screen readers.
    """
    
    @staticmethod
    def create_accessible_label(label_text: str, additional_info: str = "") -> str:
        """
        Create a comprehensive label for screen readers.
        """
        if additional_info:
            return f"{label_text}. {additional_info}"
        return label_text
    
    @staticmethod
    def create_button_description(button_name: str, action: str) -> str:
        """
        Create detailed description of what a button does.
        """
        return f"{button_name} button. Activating this will: {action}"
    
    @staticmethod
    def get_quick_start_guide() -> str:
        """
        Get quick start guide for blind users.
        """
        guide = """
        BRAILLE CONVERTER - QUICK START FOR BLIND USERS
        ================================================
        
        PRIMARY USE CASE:
        This tool converts text to Braille characters that can be:
        1. Printed on a Braille embosser (creates physical tactile Braille)
        2. Heard aloud using the Audio feature
        3. Read back as text using any screen reader
        
        BASIC WORKFLOW:
        1. Type or paste your text
        2. Press Ctrl+Shift+S to hear the output
        3. Use Ctrl+3 to copy for printing on embosser
        
        KEYBOARD NAVIGATION:
        - Alt+1 to Alt+0: Switch between pages
        - Tab: Navigate between controls
        - Enter: Activate buttons
        - Arrow keys: Adjust sliders
        
        MOST USEFUL FEATURES FOR YOU:
        - 🔊 Audio Page: Hear any text spoken aloud
        - 📚 Grades Page: Learn Braille contractions
        - 📖 Learning Page: Interactive Braille lessons
        - 📜 History: Auto-saved conversion history
        - ✅ Audit: Check text accessibility
        
        EMBOSSER WORKFLOW:
        1. Type text in Converter
        2. Copy braille output (Ctrl+3)
        3. Open your embosser software
        4. Paste the braille
        5. Print
        → Creates physical, tactile Braille you can feel and read
        
        GETTING HELP:
        - Press F1 for keyboard shortcuts
        - Use Tab to explore all options
        - Press Alt+1 to return to Converter page
        
        TIPS:
        - Use Audio page frequently to verify conversions
        - Check History (Alt+9) to see past conversions
        - Use Learning (Alt+8) to improve Braille knowledge
        - Add favorites (Ctrl+Shift+F) for frequently used conversions
        """
        return guide.strip()
    
    @staticmethod
    def generate_status_report(
        input_text: str,
        output_text: str,
        language: str,
        page_name: str
    ) -> str:
        """
        Generate comprehensive status report for screen reader.
        """
        report = f"""
        STATUS REPORT
        
        Current Page: {page_name}
        
        Input Details:
        - Language: {language}
        - Character count: {len(input_text)}
        - Word count: {len(input_text.split())}
        - Content preview: {input_text[:50]}{'...' if len(input_text) > 50 else ''}
        
        Output Details:
        - Format: Braille Unicode
        - Character count: {len(output_text)}
        - Status: Conversion complete
        - Ready to: Copy, Print, or Speak
        
        Next Steps:
        - Press Ctrl+Shift+S to hear it
        - Press Ctrl+3 to copy it
        - Go to Documents page to export for embosser
        """
        return report.strip()


# Global announcer instance
announcer = AccessibilityAnnouncer()

def announce(text: str, priority: str = 'normal'):
    """Global function to make announcements."""
    announcer.announce(text, priority)
