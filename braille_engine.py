# braille_engine.py — Conversion logic

from braille_maps import (
    ENGLISH_TO_BRAILLE, BRAILLE_TO_ENGLISH,
    HINDI_TO_BRAILLE, BRAILLE_TO_HINDI,
    MARATHI_TO_BRAILLE, BRAILLE_TO_MARATHI,
    get_dots, dots_to_braille_char
)

LANGUAGE_MAP = {
    'English':  (ENGLISH_TO_BRAILLE,  BRAILLE_TO_ENGLISH),
    'Hindi':    (HINDI_TO_BRAILLE,    BRAILLE_TO_HINDI),
    'Marathi':  (MARATHI_TO_BRAILLE,  BRAILLE_TO_MARATHI),
}

def text_to_braille(text: str, language: str = 'English') -> str:
    t2b, _ = LANGUAGE_MAP.get(language, LANGUAGE_MAP['English'])
    result = []
    for ch in text:
        lower = ch.lower() if language == 'English' else ch
        braille = t2b.get(ch) or t2b.get(lower) or '⠀'
        result.append(braille)
    return ''.join(result)

def braille_to_text(braille: str, language: str = 'English') -> str:
    _, b2t = LANGUAGE_MAP.get(language, LANGUAGE_MAP['English'])
    result = []
    for ch in braille:
        if '\u2800' <= ch <= '\u28ff':
            result.append(b2t.get(ch, '?'))
        else:
            result.append(ch)
    return ''.join(result)

def get_braille_cells(braille_string: str) -> list[dict]:
    """
    Returns a list of cell dicts:
    { 'braille': '⠁', 'dots': [1], 'label': 'a' }
    """
    cells = []
    for ch in braille_string:
        if '\u2800' <= ch <= '\u28ff':
            cells.append({
                'braille': ch,
                'dots': get_dots(ch),
                'label': ch,
            })
    return cells

def get_braille_pattern(braille_string: str) -> list[list[int]]:
    """
    Return a list of active dot lists for each character in a braille string.
    """
    return [get_dots(ch) for ch in braille_string]

