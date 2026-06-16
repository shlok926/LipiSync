# braille_grades.py — Advanced Braille Grades (1, 2, 3) with contractions

# ── Grade 2: Common contractions & abbreviations ────────────────
ENGLISH_GRADE2_CONTRACTIONS = {
    # Common word contractions
    'and': '⠯',
    'the': '⠮',
    'for': '⠿',
    'of': '⠧',
    'with': '⠢',
    'in': '⠬',
    'is': '⠊⠎',
    'you': '⠽',
    'not': '⠝⠕⠞',
    'but': '⠃⠥⠞',
    'was': '⠺⠁⠎',
    'were': '⠺⠻',
    'be': '⠃⠑',
    'have': '⠓⠁⠧⠑',
    'from': '⠋⠗',
    'do': '⠙⠕',
    'go': '⠛⠕',
    'can': '⠉',
    'shall': '⠩',
    'this': '⠮',
    'which': '⠱',
    'their': '⠮⠊⠗',
    'upon': '⠥⠏',
    'about': '⠁⠃',
    'into': '⠬',
    'through': '⠮⠓',
    'young': '⠽',
    'would': '⠢⠙',
    'as': '⠒',
    'were': '⠺⠻',
    'these': '⠮⠑',
    'those': '⠮⠕⠑',
    'could': '⠉⠙',
    'out': '⠳⠞',
    'its': '⠦',
    'come': '⠉⠍',
    'just': '⠯⠞',
    'made': '⠍⠙',
    'much': '⠯⠉⠓',
    'may': '⠍⠽',
    'other': '⠮⠓⠻',
    'people': '⠏⠇',
    'said': '⠎⠙',
    'should': '⠩⠙',
    'such': '⠳⠉⠓',
    'than': '⠾',
    'their': '⠮⠊⠗',
    'time': '⠞⠍',
    'under': '⠥⠝',
    'where': '⠱⠻',
    'world': '⠢⠙',
    # ... can be extended
}

# Grade 2 - Part word contractions
GRADE2_PART_CONTRACTIONS = {
    'ing': '⠬',
    'tion': '⠰⠝',
    'ment': '⠰⠍',
    'ness': '⠰⠝⠑⠎⠎',
    'able': '⠰⠃⠑',
    'ible': '⠰⠊⠃⠇',
    'ful': '⠰⠋',
    'ous': '⠰⠕⠥⠎',
    'ure': '⠰⠥⠗',
    'ture': '⠰⠙⠥⠗⠑',
    'ally': '⠰⠇⠇⠽',
}

# ── Grade 3: Further abbreviations ────────────────────────────
ENGLISH_GRADE3_ABBREVIATIONS = {
    'and': '&',
    'the': 'þ',
    'different': 'diff',
    'information': 'info',
    'morning': 'morn',
    'understand': 'underst',
    'important': 'imp',
    'alphabet': 'alph',
    'about': 'abt',
    'government': 'govt',
}

class BrailleGradeConverter:
    """Converts text to different Braille grades."""
    
    def __init__(self):
        from braille_engine import text_to_braille
        self.text_to_braille_grade1 = text_to_braille
    
    def text_to_grade1(self, text: str) -> str:
        """Grade 1: Direct character-by-character mapping (existing)."""
        return self.text_to_braille_grade1(text)
    
    def text_to_grade2(self, text: str) -> str:
        """
        Grade 2: Includes word contractions and common abbreviations.
        Faster to read but requires knowledge of contractions.
        """
        result = []
        i = 0
        text_lower = text.lower()
        
        while i < len(text):
            matched = False
            
            # Try to match longest contractions first
            for length in range(min(15, len(text_lower) - i), 0, -1):
                word = text_lower[i:i+length]
                
                # Word boundary check
                before_ok = (i == 0 or not text[i-1].isalnum())
                after_ok = (i+length >= len(text) or not text[i+length].isalnum())
                
                if word in ENGLISH_GRADE2_CONTRACTIONS and before_ok and after_ok:
                    result.append(ENGLISH_GRADE2_CONTRACTIONS[word])
                    i += length
                    matched = True
                    break
                
                # Try part word contractions
                if word in GRADE2_PART_CONTRACTIONS and i + length < len(text):
                    result.append(GRADE2_PART_CONTRACTIONS[word])
                    i += length
                    matched = True
                    break
            
            if not matched:
                # Fallback to Grade 1 for this character
                result.append(self.text_to_braille_grade1(text[i]))
                i += 1
        
        return ''.join(result)
    
    def text_to_grade3(self, text: str) -> str:
        """
        Grade 3: Maximum abbreviations - not widely standardized.
        Mainly experimental.
        """
        # Start with Grade 2
        result = self.text_to_grade2(text)
        
        # Apply Grade 3 abbreviations (simplified)
        for word, abbrev in ENGLISH_GRADE3_ABBREVIATIONS.items():
            braille_word = self.text_to_grade2(word)
            # This is a simplified approach; real Grade 3 is more complex
        
        return result

# Global converter instance
grade_converter = BrailleGradeConverter()
