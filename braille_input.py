"""
Braille Input Mode - Convert typed braille patterns to text

Users type braille dot patterns using keyboard, then convert to readable text.
Supports multiple input methods:
1. Dot notation: Type dot numbers (1-6) to form patterns
2. Braille characters: Paste Unicode braille and convert to text
3. Pattern builder: Visual interface to select dots
"""

from braille_engine import braille_to_text


class BrailleInputConverter:
    """Convert typed braille patterns to readable text."""
    
    # Dot positions (visual layout):
    # 1 4
    # 2 5
    # 3 6
    
    # Unicode braille patterns start at U+2800
    # Each pattern is a combination of dots
    BRAILLE_BASE = 0x2800
    
    def __init__(self):
        """Initialize braille input converter."""
        self.current_pattern = set()  # Current dots being formed
        self.pattern_history = []
    
    def dots_to_unicode(self, dots):
        """
        Convert dot set to Unicode braille character.
        
        Args:
            dots: Set of dot numbers (1-6) or list [1, 4, 2, 5]
        
        Returns:
            Unicode braille character
        
        Example:
            dots_to_unicode({1, 4}) → '⠑' (letter 'E')
            dots_to_unicode({1, 2, 3, 4, 5, 6}) → '⠿' (full cell)
        """
        if not dots:
            return chr(self.BRAILLE_BASE)  # Empty cell
        
        # Convert dot numbers to bit positions
        # Dot 1→bit 0, Dot 2→bit 1, Dot 3→bit 2
        # Dot 4→bit 3, Dot 5→bit 4, Dot 6→bit 5
        value = 0
        dot_to_bit = {
            1: 0, 2: 1, 3: 2,
            4: 3, 5: 4, 6: 5
        }
        
        for dot in dots:
            if dot in dot_to_bit:
                value |= (1 << dot_to_bit[dot])
        
        return chr(self.BRAILLE_BASE + value)
    
    def unicode_to_dots(self, braille_char):
        """
        Convert Unicode braille character to dot set.
        
        Args:
            braille_char: Unicode braille character
        
        Returns:
            Set of dot numbers (1-6)
        
        Example:
            unicode_to_dots('⠑') → {1, 4}
            unicode_to_dots('⠿') → {1, 2, 3, 4, 5, 6}
        """
        if not braille_char or ord(braille_char) < self.BRAILLE_BASE:
            return set()
        
        value = ord(braille_char) - self.BRAILLE_BASE
        
        # Convert bit positions back to dot numbers
        bit_to_dot = {
            0: 1, 1: 2, 2: 3,
            3: 4, 4: 5, 5: 6
        }
        
        dots = set()
        for bit, dot in bit_to_dot.items():
            if value & (1 << bit):
                dots.add(dot)
        
        return dots
    
    def text_to_dots_notation(self, text):
        """
        Show how text would be represented in dot notation.
        
        Args:
            text: Text to convert (will be converted to braille first)
        
        Returns:
            String with dot notation for each character
        
        Example:
            text_to_dots_notation("hi") → "[1 2 3 4 5 6]|[2 3 4]"
        """
        from braille_engine import text_to_braille
        
        braille = text_to_braille(text, "English")
        result = []
        
        for char in braille:
            if ord(char) >= self.BRAILLE_BASE:
                dots = self.unicode_to_dots(char)
                dot_str = " ".join(str(d) for d in sorted(dots)) if dots else "0"
                result.append(f"[{dot_str}]")
        
        return "|".join(result)
    
    def add_dot(self, dot_num):
        """Add a dot to current pattern."""
        if 1 <= dot_num <= 6:
            self.current_pattern.add(dot_num)
            return True
        return False
    
    def remove_dot(self, dot_num):
        """Remove a dot from current pattern."""
        if dot_num in self.current_pattern:
            self.current_pattern.remove(dot_num)
            return True
        return False
    
    def toggle_dot(self, dot_num):
        """Toggle a dot (add if missing, remove if present)."""
        if dot_num in self.current_pattern:
            self.remove_dot(dot_num)
        else:
            self.add_dot(dot_num)
    
    def get_current_character(self):
        """Get the braille character for current pattern."""
        return self.dots_to_unicode(self.current_pattern)
    
    def get_current_dots(self):
        """Get sorted list of current dots."""
        return sorted(self.current_pattern)
    
    def add_character(self):
        """
        Add current pattern to history and clear for next character.
        
        Returns:
            Braille character that was added
        """
        char = self.get_current_character()
        self.pattern_history.append(self.current_pattern.copy())
        self.current_pattern.clear()
        return char
    
    def undo_character(self):
        """Remove last added character."""
        if self.pattern_history:
            self.pattern_history.pop()
            return True
        return False
    
    def get_braille_string(self):
        """Get the complete braille string from history."""
        result = ""
        for dots in self.pattern_history:
            result += self.dots_to_unicode(dots)
        return result
    
    def clear_all(self):
        """Clear all patterns."""
        self.current_pattern.clear()
        self.pattern_history.clear()
    
    def braille_to_text_input(self, braille_text, language="English"):
        """
        Convert typed/pasted braille text to readable text.
        
        Args:
            braille_text: String of Unicode braille characters
            language: Output language (English, Hindi, Marathi)
        
        Returns:
            Converted text
        """
        try:
            # Filter only braille characters
            braille_filtered = "".join(
                c for c in braille_text 
                if ord(c) >= self.BRAILLE_BASE and ord(c) <= self.BRAILLE_BASE + 256
            )
            
            if not braille_filtered:
                return "❌ No valid braille characters found"
            
            # Convert to text
            text = braille_to_text(braille_filtered, language)
            return text
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def parse_dot_notation(self, notation_str):
        """
        Parse dot notation input.
        
        Supports formats:
        - "1 4" → dots 1 and 4
        - "146" → dots 1, 4, 6
        - "[1 4]" → dots 1 and 4
        - "1,4" → dots 1 and 4
        
        Args:
            notation_str: Dot notation string
        
        Returns:
            Set of valid dot numbers
        """
        # Remove brackets and split
        notation_str = notation_str.replace("[", "").replace("]", "")
        notation_str = notation_str.replace(",", " ")
        
        dots = set()
        for char in notation_str:
            if char.isdigit():
                dot_num = int(char)
                if 1 <= dot_num <= 6:
                    dots.add(dot_num)
        
        return dots
    
    def pattern_to_description(self, dots):
        """Get visual description of dot pattern."""
        dots = set(dots) if dots else set()
        
        # Build 3x2 grid visualization
        grid = [
            [".", "."],
            [".", "."],
            [".", "."]
        ]
        
        # Map dots to grid positions
        dot_positions = {
            1: (0, 0), 4: (0, 1),
            2: (1, 0), 5: (1, 1),
            3: (2, 0), 6: (2, 1)
        }
        
        for dot in dots:
            if dot in dot_positions:
                row, col = dot_positions[dot]
                grid[row][col] = "⠿"  # Filled dot
        
        # Format as string
        result = ""
        for row in grid:
            result += " ".join(row) + "\n"
        
        return result.strip()
    
    def get_help_text(self):
        """Get help text for braille input."""
        return """
🎯 BRAILLE INPUT MODE HELP

Three Ways to Input Braille:

1️⃣ DOT BUILDER (Easiest)
   • Click or type dots 1-6
   • Preview the character
   • Build pattern one character at a time
   • Example: Select dots [1,4] = 'e'

2️⃣ DOT NOTATION (Fast typing)
   • Type dot numbers: "1 4" or "146"
   • Enter to create character
   • Continue for next character
   • Shortcuts: [1 4] = e, [1 2 3 4 5 6] = full

3️⃣ PASTE BRAILLE (For existing)
   • Paste Unicode braille text
   • App converts to readable text
   • Great for processing braille documents

📊 COMMON PATTERNS:
   [0]     = empty cell
   [1 4]   = 'e' (English)
   [1 2 3 4 5 6] = full cell
   [1 2]   = 'a'
   [1 3 4] = 'k'

✅ TIP: Use Tab to move between dots!
✅ TIP: Press Space to complete character!
"""


# Global instance
braille_input_converter = BrailleInputConverter()

def parse_dot_notation(notation_str):
    """Module-level wrapper for parse_dot_notation."""
    return braille_input_converter.parse_dot_notation(notation_str)

def dots_to_unicode(dots):
    """Module-level wrapper for dots_to_unicode."""
    return braille_input_converter.dots_to_unicode(dots)


if __name__ == "__main__":
    print("=" * 70)
    print("BRAILLE INPUT MODE - EXAMPLES")
    print("=" * 70)
    print()
    
    # Example 1: Dot builder
    print("Example 1: Building 'A' (dots 1, 2)")
    print("-" * 70)
    conv = BrailleInputConverter()
    conv.add_dot(1)
    conv.add_dot(2)
    char = conv.add_character()
    print(f"Pattern dots: {conv.get_current_dots()}")
    print(f"Braille character: {char}")
    print(f"Visual:\n{conv.pattern_to_description({1, 2})}")
    print()
    
    # Example 2: Parse dot notation
    print("Example 2: Parse dot notation '1 4 5'")
    print("-" * 70)
    dots = conv.parse_dot_notation("1 4 5")
    print(f"Parsed dots: {sorted(dots)}")
    char = conv.dots_to_unicode(dots)
    print(f"Braille character: {char}")
    print()
    
    # Example 3: Convert braille to text
    print("Example 3: Paste braille and convert to text")
    print("-" * 70)
    braille_text = "⠓⠑⠇⠇⠕"  # "hello"
    text = conv.braille_to_text_input(braille_text, "English")
    print(f"Braille input: {braille_text}")
    print(f"Text output: {text}")
    print()
    
    print("=" * 70)
    print("✅ Braille Input Mode Ready!")
    print("=" * 70)
