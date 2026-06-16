# math_notation.py — Mathematical & Scientific notation in Braille

import re

# ── Math symbols mapping to Braille ────────────────────────────
MATH_SYMBOLS_TO_BRAILLE = {
    # Basic operators
    '+': '⠬',
    '-': '⠤',
    '×': '⠈⠡',
    '÷': '⠈⠢',
    '=': '⠀⠨⠅',
    '<': '⠨⠣',
    '>': '⠨⠜',
    '≤': '⠨⠣⠀⠨⠅',
    '≥': '⠨⠜⠀⠨⠅',
    '±': '⠬⠤',
    '×': '⠈⠡',
    '*': '⠈⠡',
    '/': '⠈⠢',
    
    # Exponents & subscripts
    '²': '⠘⠆⠉',  # superscript 2 (squared)
    '³': '⠘⠆⠒',  # superscript 3 (cubed)
    '⁻¹': '⠘⠘⠤⠁',  # superscript -1 (inverse)
    
    # Functions
    'sin': '⠎⠊⠝',
    'cos': '⠉⠕⠎',
    'tan': '⠞⠁⠝',
    'log': '⠇⠕⠛',
    'ln': '⠇⠝',
    'exp': '⠑⠭⠏',
    'sqrt': '⠜⠡⠗⠞',
    
    # Sets & Logic
    '∈': '⠐⠉',  # element of
    '∉': '⠐⠉⠿',  # not element of
    '∪': '⠐⠥',  # union
    '∩': '⠐⠝',  # intersection
    '∅': '⠐⠚',  # empty set
    '∴': '⠒⠒⠒',  # therefore
    '∵': '⠒⠒⠒',  # because
    
    # Greek letters (common in math)
    'α': '⠐⠁',  # alpha
    'β': '⠐⠃',  # beta
    'γ': '⠐⠛',  # gamma
    'δ': '⠐⠙',  # delta
    'π': '⠐⠏',  # pi
    'Σ': '⠐⠎',  # sigma (sum)
    'μ': '⠐⠍',  # mu
    'θ': '⠐⠾',  # theta
    'λ': '⠐⠇',  # lambda
    'Δ': '⠐⠨⠙',  # delta (capital)
    
    # Chemistry
    'H₂O': '⠓⠆⠕',
    'CO₂': '⠉⠕⠆',
    'NaCl': '⠝⠁⠉⠇',
    
    # Common constants
    'π': '⠐⠏',
    'e': '⠐⠑',  # Euler's number
    'i': '⠐⠊',  # imaginary unit
    'ℏ': '⠐⠓',  # reduced Planck's constant
}

# ── Science notation ─────────────────────────────────────────
SCIENCE_PREFIXES = {
    'k': 'kilo (10³)',
    'M': 'mega (10⁶)',
    'G': 'giga (10⁹)',
    'T': 'tera (10¹²)',
    'm': 'milli (10⁻³)',
    'μ': 'micro (10⁻⁶)',
    'n': 'nano (10⁻⁹)',
    'p': 'pico (10⁻¹²)',
}

UNITS_TO_BRAILLE = {
    'm': '⠍⠑⠞⠻',  # meter
    'kg': '⠅⠛',    # kilogram
    's': '⠎⠑⠉',    # second
    'A': '⠁⠍⠏',    # ampere
    'K': '⠅⠑⠇⠧⠬',  # kelvin
    'mol': '⠍⠕⠇',  # mole
    'Hz': '⠓⠑⠗⠞⠵',  # hertz
    'N': '⠝⠑⠺⠞⠕⠝',  # newton
    'Pa': '⠏⠁⠎⠉⠁⠇',  # pascal
    'J': '⠚⠕⠥⠇⠑',  # joule
    'W': '⠺⠁⠞⠞',  # watt
    'V': '⠧⠕⠇⠞',  # volt
    'Ω': '⠕⠓⠍',    # ohm
    'C': '⠉⠕⠥⠇⠕⠍⠃',  # coulomb
}

class MathNotationConverter:
    """Converts mathematical & scientific expressions to Braille."""
    
    def convert_math_expression(self, expression: str) -> str:
        """
        Convert mathematical expression to Braille.
        Example: "x² + y² = z²" -> "⠭⠘⠆⠉ + ⠽⠘⠆⠉ = ⠵⠘⠆⠉"
        """
        result = expression
        
        # Replace math symbols
        for symbol, braille in MATH_SYMBOLS_TO_BRAILLE.items():
            result = result.replace(symbol, braille)
        
        # Handle superscripts in format: number^power
        result = re.sub(r'(\w)\^(\d+)', lambda m: f'{m.group(1)}⠘⠆{m.group(2)}', result)
        
        return result
    
    def convert_chemistry_formula(self, formula: str) -> str:
        """
        Convert chemical formula to Braille.
        Example: "H2O" -> appropriate braille representation
        """
        if formula in MATH_SYMBOLS_TO_BRAILLE:
            return MATH_SYMBOLS_TO_BRAILLE[formula]
        
        # Parse and convert elements
        result = []
        i = 0
        while i < len(formula):
            if formula[i].isupper():
                element = formula[i]
                i += 1
                while i < len(formula) and formula[i].islower():
                    element += formula[i]
                    i += 1
                
                # Get count if present
                count = ''
                while i < len(formula) and formula[i].isdigit():
                    count += formula[i]
                    i += 1
                
                # Convert element symbol
                result.append(element)
                if count:
                    result.append(f'⠤{count}')  # subscript representation
            else:
                i += 1
        
        return ' '.join(result)
    
    def convert_scientific_notation(self, number_str: str) -> str:
        """
        Convert scientific notation to Braille.
        Example: "1.5e-10" -> braille representation
        """
        # Parse scientific notation
        match = re.match(r'([+-]?\d+\.?\d*)[eE]([+-]?\d+)', number_str)
        if match:
            mantissa = match.group(1)
            exponent = match.group(2)
            return f'{mantissa} × 10^{exponent}'
        return number_str
    
    def convert_fraction(self, numerator: str, denominator: str) -> str:
        """Convert fraction to Braille."""
        return f'{numerator}⠌{denominator}'  # ⠌ is fraction bar in Braille
    
    def convert_units(self, quantity: str, unit: str) -> str:
        """
        Convert physical quantity with units.
        Example: "5 kg" -> "5 ⠅⠛"
        """
        unit_braille = UNITS_TO_BRAILLE.get(unit, unit)
        return f'{quantity} {unit_braille}'
    
    def get_description(self, symbol: str) -> str:
        """Get textual description of a math symbol."""
        descriptions = {
            '+': 'plus',
            '-': 'minus',
            '×': 'multiply',
            '÷': 'divide',
            '=': 'equals',
            '<': 'less than',
            '>': 'greater than',
            '²': 'squared',
            '³': 'cubed',
            '∈': 'element of',
            '∪': 'union',
            '∩': 'intersection',
            'π': 'pi',
            'Σ': 'sum',
        }
        return descriptions.get(symbol, 'unknown symbol')

# Global converter instance
math_converter = MathNotationConverter()
