# braille_maps.py — Braille character mappings
# English Grade 1 + Bharati Braille (Hindi & Marathi)

# ── English Grade 1 ────────────────────────────────────────────
ENGLISH_TO_BRAILLE = {
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
    'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
    'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
    'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽',
    'z': '⠵',
    'A': '⠠⠁', 'B': '⠠⠃', 'C': '⠠⠉', 'D': '⠠⠙', 'E': '⠠⠑',
    'F': '⠠⠋', 'G': '⠠⠛', 'H': '⠠⠓', 'I': '⠠⠊', 'J': '⠠⠚',
    'K': '⠠⠅', 'L': '⠠⠇', 'M': '⠠⠍', 'N': '⠠⠝', 'O': '⠠⠕',
    'P': '⠠⠏', 'Q': '⠠⠟', 'R': '⠠⠗', 'S': '⠠⠎', 'T': '⠠⠞',
    'U': '⠠⠥', 'V': '⠠⠧', 'W': '⠠⠺', 'X': '⠠⠭', 'Y': '⠠⠽',
    'Z': '⠠⠵',
    '1': '⠁', '2': '⠃', '3': '⠉', '4': '⠙', '5': '⠑',
    '6': '⠋', '7': '⠛', '8': '⠓', '9': '⠊', '0': '⠚',
    ' ': '⠀', '.': '⠲', ',': '⠂', '?': '⠦', '!': '⠖',
    ';': '⠆', ':': '⠒', "'": '⠄', '-': '⠤', '"': '⠶',
    '(': '⠐⠣', ')': '⠐⠜',
}

BRAILLE_TO_ENGLISH = {}
for k, v in ENGLISH_TO_BRAILLE.items():
    if len(v) == 1 and v not in BRAILLE_TO_ENGLISH:
        BRAILLE_TO_ENGLISH[v] = k

# ── Bharati Braille — Hindi (Devanagari) ───────────────────────
HINDI_TO_BRAILLE = {
    # Vowels (Swar)
    'अ': '⠁', 'आ': '⠜', 'इ': '⠊', 'ई': '⠔',
    'उ': '⠥', 'ऊ': '⠳', 'ए': '⠑', 'ऐ': '⠌',
    'ओ': '⠕', 'औ': '⠪', 'ऋ': '⠐⠗', 'ॠ': '⠐⠗',
    # Matras (dependent vowel signs)
    'ा': '⠜', 'ि': '⠊', 'ी': '⠔',
    'ु': '⠥', 'ू': '⠳', 'े': '⠑', 'ै': '⠌',
    'ो': '⠕', 'ौ': '⠪', 'ृ': '⠐⠗',
    # Consonants (Vyanjan) — Ka-varga
    'क': '⠅', 'ख': '⠨', 'ग': '⠛', 'घ': '⠣', 'ङ': '⠬',
    # Cha-varga
    'च': '⠉', 'छ': '⠡', 'ज': '⠚', 'झ': '⠴', 'ञ': '⠯',
    # Ta-varga
    'ट': '⠾', 'ठ': '⠿', 'ड': '⠮', 'ढ': '⠸', 'ण': '⠼',
    # Ta-varga (soft)
    'त': '⠞', 'थ': '⠹', 'द': '⠙', 'ध': '⠮', 'न': '⠝',
    # Pa-varga
    'प': '⠏', 'फ': '⠋', 'ब': '⠃', 'भ': '⠘', 'म': '⠍',
    # Others
    'य': '⠽', 'र': '⠗', 'ल': '⠇', 'व': '⠧',
    'श': '⠩', 'ष': '⠯', 'स': '⠎', 'ह': '⠓',
    # Special marks
    'ं': '⠰', 'ँ': '⠰', 'ः': '⠠⠂', '्': '⠈', 'ऽ': '⠈⠁',
    ' ': '⠀', '।': '⠲', '॥': '⠲⠲',
}

BRAILLE_TO_HINDI = {}
for k, v in HINDI_TO_BRAILLE.items():
    if v not in BRAILLE_TO_HINDI:
        BRAILLE_TO_HINDI[v] = k

# ── Bharati Braille — Marathi (same base + Marathi-specific) ───
MARATHI_TO_BRAILLE = HINDI_TO_BRAILLE.copy()
MARATHI_TO_BRAILLE.update({
    'ळ': '⠯⠇',
    'ऴ': '⠯⠮',
})

BRAILLE_TO_MARATHI = {}
for k, v in MARATHI_TO_BRAILLE.items():
    if v not in BRAILLE_TO_MARATHI:
        BRAILLE_TO_MARATHI[v] = k

# ── Helper: get active dot positions from braille unicode char ──
def get_dots(braille_char: str) -> list[int]:
    """Return list of active dot numbers (1-6) for a braille unicode char."""
    if not braille_char or ord(braille_char) < 0x2800 or ord(braille_char) > 0x28FF:
        return []
    code = ord(braille_char) - 0x2800
    return [i + 1 for i in range(6) if code & (1 << i)]

def dots_to_braille_char(dots: list[int]) -> str:
    """Convert list of dot numbers to braille unicode character."""
    code = 0
    for d in dots:
        if 1 <= d <= 6:
            code |= (1 << (d - 1))
    return chr(0x2800 + code)

# ── Bharati Braille — Tamil ────────────────────────────────────
TAMIL_TO_BRAILLE = {
    # Tamil vowels
    'அ': '⠁', 'ஆ': '⠜', 'இ': '⠊', 'ஈ': '⠔',
    'உ': '⠥', 'ஊ': '⠳', 'எ': '⠑', 'ஏ': '⠌',
    'ஐ': '⠡', 'ஒ': '⠕', 'ஓ': '⠪', 'ஔ': '⠺',
    # Tamil vowel marks (maatras)
    'ா': '⠜', 'ி': '⠊', 'ீ': '⠔', 'ு': '⠥', 'ூ': '⠳',
    'ெ': '⠑', 'ே': '⠌', 'ை': '⠡', 'ொ': '⠕', 'ோ': '⠪',
    'ௌ': '⠺', 'ௌ': '⠪',
    # Tamil consonants (hard sounds)
    'க': '⠅', 'ங': '⠬', 'ச': '⠉', 'ஞ': '⠯',
    'ட': '⠾', 'ண': '⠼', 'த': '⠞', 'ந': '⠝',
    'প': '⠏', 'ம': '⠍', 'য': '⠽', 'ர': '⠗',
    'ல': '⠇', 'ள': '⠣', 'வ': '⠧', 'ஷ': '⠩',
    'ஸ': '⠎', 'ஹ': '⠓', 'ஷ': '⠯⠊',
    # Tamil numerals
    '௦': '⠚', '௧': '⠁', '௨': '⠃', '௩': '⠉', '௪': '⠙',
    '௫': '⠑', '௬': '⠋', '௭': '⠛', '௮': '⠓', '௯': '⠊',
    # Special marks
    '्': '⠈', ' ': '⠀', '।': '⠲', '॥': '⠲⠲',
}

BRAILLE_TO_TAMIL = {}
for k, v in TAMIL_TO_BRAILLE.items():
    if v not in BRAILLE_TO_TAMIL:
        BRAILLE_TO_TAMIL[v] = k

# ── Bharati Braille — Telugu ───────────────────────────────────
TELUGU_TO_BRAILLE = {
    # Telugu vowels
    'అ': '⠁', 'ఆ': '⠜', 'ఇ': '⠊', 'ఈ': '⠔',
    'ఉ': '⠥', 'ఊ': '⠳', 'ఎ': '⠑', 'ఏ': '⠌',
    'ఐ': '⠡', 'ఒ': '⠕', 'ఓ': '⠪', 'ఔ': '⠺',
    # Telugu vowel marks
    'ా': '⠜', 'ి': '⠊', 'ీ': '⠔', 'ు': '⠥', 'ూ': '⠳',
    'െ': '⠑', 'ే': '⠌', 'ై': '⠡', 'ొ': '⠕', 'ో': '⠪',
    # Telugu consonants
    'క': '⠅', 'ఖ': '⠨', 'గ': '⠛', 'ఘ': '⠣', 'ఙ': '⠬',
    'చ': '⠉', 'ఛ': '⠡', 'జ': '⠚', 'ఝ': '⠴', 'ఞ': '⠯',
    'ట': '⠾', 'ఠ': '⠿', 'డ': '⠮', 'ఢ': '⠸', 'ణ': '⠼',
    'త': '⠞', 'థ': '⠹', 'ద': '⠙', 'ధ': '⠮', 'న': '⠝',
    'প': '⠏', 'ఫ': '⠋', 'బ': '⠃', 'భ': '⠘', 'మ': '⠍',
    'య': '⠽', 'ర': '⠗', 'ల': '⠇', 'వ': '⠧',
    'శ': '⠩', 'ష': '⠯', 'స': '⠎', 'హ': '⠓',
    # Special marks
    '్': '⠈', ' ': '⠀', '।': '⠲',
}

BRAILLE_TO_TELUGU = {}
for k, v in TELUGU_TO_BRAILLE.items():
    if v not in BRAILLE_TO_TELUGU:
        BRAILLE_TO_TELUGU[v] = k

# ── Bharati Braille — Kannada ──────────────────────────────────
KANNADA_TO_BRAILLE = {
    # Kannada vowels
    'ಅ': '⠁', 'ಆ': '⠜', 'ಇ': '⠊', 'ಈ': '⠔',
    'ಉ': '⠥', 'ಊ': '⠳', 'ಎ': '⠑', 'ಏ': '⠌',
    'ಐ': '⠡', 'ಒ': '⠕', 'ಓ': '⠪', 'ಔ': '⠺',
    # Kannada vowel signs
    'ಾ': '⠜', 'ಿ': '⠊', 'ೀ': '⠔', 'ು': '⠥', 'ೂ': '⠳',
    'ೆ': '⠑', 'ೇ': '⠌', 'ೈ': '⠡', 'ೊ': '⠕', 'ೋ': '⠪',
    # Kannada consonants
    'ಕ': '⠅', 'ಖ': '⠨', 'ಗ': '⠛', 'ಘ': '⠣', 'ಙ': '⠬',
    'ಚ': '⠉', 'ಛ': '⠡', 'ಜ': '⠚', 'ಝ': '⠴', 'ಞ': '⠯',
    'ಟ': '⠾', 'ಠ': '⠿', 'ಡ': '⠮', 'ಢ': '⠸', 'ಣ': '⠼',
    'ತ': '⠞', 'ಥ': '⠹', 'ದ': '⠙', 'ಧ': '⠮', 'ನ': '⠝',
    'ಪ': '⠏', 'ಫ': '⠋', 'ಬ': '⠃', 'ಭ': '⠘', 'ಮ': '⠍',
    'ಯ': '⠽', 'ರ': '⠗', 'ಲ': '⠇', 'ವ': '⠧',
    'ಶ': '⠩', 'ಷ': '⠯', 'ಸ': '⠎', 'ಹ': '⠓',
    'ಳ': '⠯⠇', 'ೞ': '⠯⠮',
    # Special marks
    '್': '⠈', ' ': '⠀', '।': '⠲',
}

BRAILLE_TO_KANNADA = {}
for k, v in KANNADA_TO_BRAILLE.items():
    if v not in BRAILLE_TO_KANNADA:
        BRAILLE_TO_KANNADA[v] = k

# ── French Grade 1 (with accented characters) ───────────────────
FRENCH_TO_BRAILLE = {
    # Standard English letters
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
    'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
    'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
    'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽',
    'z': '⠵',
    'A': '⠠⠁', 'B': '⠠⠃', 'C': '⠠⠉', 'D': '⠠⠙', 'E': '⠠⠑',
    'F': '⠠⠋', 'G': '⠠⠛', 'H': '⠠⠓', 'I': '⠠⠊', 'J': '⠠⠚',
    'K': '⠠⠅', 'L': '⠠⠇', 'M': '⠠⠍', 'N': '⠠⠝', 'O': '⠠⠕',
    'P': '⠠⠏', 'Q': '⠠⠟', 'R': '⠠⠗', 'S': '⠠⠎', 'T': '⠠⠞',
    'U': '⠠⠥', 'V': '⠠⠧', 'W': '⠠⠺', 'X': '⠠⠭', 'Y': '⠠⠽',
    'Z': '⠠⠵',
    # French accented vowels
    'à': '⠐⠁', 'â': '⠂⠁', 'ä': '⠣⠁', 'ã': '⠘⠁',
    'é': '⠐⠑', 'è': '⠂⠑', 'ê': '⠈⠑', 'ë': '⠣⠑',
    'î': '⠂⠊', 'ï': '⠣⠊',
    'ô': '⠂⠕', 'ö': '⠣⠕',
    'ù': '⠐⠥', 'û': '⠂⠥', 'ü': '⠣⠥',
    'ç': '⠐⠉',
    'À': '⠠⠐⠁', 'Â': '⠠⠂⠁', 'Ä': '⠠⠣⠁',
    'É': '⠠⠐⠑', 'È': '⠠⠂⠑', 'Ê': '⠠⠈⠑', 'Ë': '⠠⠣⠑',
    'Î': '⠠⠂⠊', 'Ï': '⠠⠣⠊',
    'Ô': '⠠⠂⠕', 'Ö': '⠠⠣⠕',
    'Ù': '⠠⠐⠥', 'Û': '⠠⠂⠥', 'Ü': '⠠⠣⠥',
    'Ç': '⠠⠐⠉',
    # Numbers and punctuation
    '1': '⠁', '2': '⠃', '3': '⠉', '4': '⠙', '5': '⠑',
    '6': '⠋', '7': '⠛', '8': '⠓', '9': '⠊', '0': '⠚',
    ' ': '⠀', '.': '⠲', ',': '⠂', '?': '⠦', '!': '⠖',
    ';': '⠆', ':': '⠒', "'": '⠄', '-': '⠤', '"': '⠶',
    '(': '⠐⠣', ')': '⠐⠜',
}

BRAILLE_TO_FRENCH = {}
for k, v in FRENCH_TO_BRAILLE.items():
    if len(v) == 1 and v not in BRAILLE_TO_FRENCH:
        BRAILLE_TO_FRENCH[v] = k

# ── Spanish Grade 1 (with accented characters) ──────────────────
SPANISH_TO_BRAILLE = {
    # Standard letters
    'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑',
    'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚',
    'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
    'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞',
    'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽',
    'z': '⠵',
    'A': '⠠⠁', 'B': '⠠⠃', 'C': '⠠⠉', 'D': '⠠⠙', 'E': '⠠⠑',
    'F': '⠠⠋', 'G': '⠠⠛', 'H': '⠠⠓', 'I': '⠠⠊', 'J': '⠠⠚',
    'K': '⠠⠅', 'L': '⠠⠇', 'M': '⠠⠍', 'N': '⠠⠝', 'O': '⠠⠕',
    'P': '⠠⠏', 'Q': '⠠⠟', 'R': '⠠⠗', 'S': '⠠⠎', 'T': '⠠⠞',
    'U': '⠠⠥', 'V': '⠠⠧', 'W': '⠠⠺', 'X': '⠠⠭', 'Y': '⠠⠽',
    'Z': '⠠⠵',
    # Spanish accented vowels
    'á': '⠐⠁', 'à': '⠂⠁',
    'é': '⠐⠑', 'è': '⠂⠑',
    'í': '⠐⠊', 'ì': '⠂⠊',
    'ó': '⠐⠕', 'ò': '⠂⠕',
    'ú': '⠐⠥', 'ù': '⠂⠥',
    # Spanish ñ
    'ñ': '⠐⠝', 'Ñ': '⠠⠐⠝',
    # Uppercase accented
    'Á': '⠠⠐⠁', 'À': '⠠⠂⠁',
    'É': '⠠⠐⠑', 'È': '⠠⠂⠑',
    'Í': '⠠⠐⠊', 'Ì': '⠠⠂⠊',
    'Ó': '⠠⠐⠕', 'Ò': '⠠⠂⠕',
    'Ú': '⠠⠐⠥', 'Ù': '⠠⠂⠥',
    # Numbers and punctuation
    '1': '⠁', '2': '⠃', '3': '⠉', '4': '⠙', '5': '⠑',
    '6': '⠋', '7': '⠛', '8': '⠓', '9': '⠊', '0': '⠚',
    ' ': '⠀', '.': '⠲', ',': '⠂', '?': '⠦', '!': '⠖',
    ';': '⠆', ':': '⠒', "'": '⠄', '-': '⠤', '"': '⠶',
    '(': '⠐⠣', ')': '⠐⠜',
}

BRAILLE_TO_SPANISH = {}
for k, v in SPANISH_TO_BRAILLE.items():
    if len(v) == 1 and v not in BRAILLE_TO_SPANISH:
        BRAILLE_TO_SPANISH[v] = k

# ── Language Support Dictionary ────────────────────────────────
SUPPORTED_LANGUAGES = {
    'English': {'to_braille': ENGLISH_TO_BRAILLE, 'from_braille': BRAILLE_TO_ENGLISH},
    'Hindi': {'to_braille': HINDI_TO_BRAILLE, 'from_braille': BRAILLE_TO_HINDI},
    'Marathi': {'to_braille': MARATHI_TO_BRAILLE, 'from_braille': BRAILLE_TO_MARATHI},
    'Tamil': {'to_braille': TAMIL_TO_BRAILLE, 'from_braille': BRAILLE_TO_TAMIL},
    'Telugu': {'to_braille': TELUGU_TO_BRAILLE, 'from_braille': BRAILLE_TO_TELUGU},
    'Kannada': {'to_braille': KANNADA_TO_BRAILLE, 'from_braille': BRAILLE_TO_KANNADA},
    'French': {'to_braille': FRENCH_TO_BRAILLE, 'from_braille': BRAILLE_TO_FRENCH},
    'Spanish': {'to_braille': SPANISH_TO_BRAILLE, 'from_braille': BRAILLE_TO_SPANISH},
}
