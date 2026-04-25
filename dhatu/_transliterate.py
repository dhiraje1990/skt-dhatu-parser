"""
dhatu/_transliterate.py

Internal module for converting between Harvard-Kyoto (HK) and SLP1
transliteration schemes. 

As per Specification  (§3), the library uses SLP1 internally for 
computation and lookup tables, but the public API strictly speaks HK.
"""

import re

# Core mapping from Harvard-Kyoto (HK) to SLP1.
# Based on the exact transliteration convention provided in the spec.
_HK_TO_SLP1_DICT = {
    # Vowels
    'a': 'a', 'A': 'A',
    'i': 'i', 'I': 'I',
    'u': 'u', 'U': 'U',
    'RR': 'F', 'R': 'f',
    'lRR': 'X', 'lR': 'x',  # Included for completeness beyond basic spec table
    'e': 'e', 'ai': 'E',
    'o': 'o', 'au': 'O',

    # Gutturals (Kanthya)
    'kh': 'K', 'k': 'k',
    'gh': 'G', 'g': 'g',
    'G': 'N',

    # Palatals (Talavya)
    'ch': 'C', 'c': 'c',
    'jh': 'J', 'j': 'j',
    'J': 'Y',

    # Cerebrals (Murdhanya)
    'Th': 'W', 'T': 'w',
    'Dh': 'Q', 'D': 'q',
    'N': 'R',

    # Dentals (Dantya)
    'th': 'T', 't': 't',
    'dh': 'D', 'd': 'd',
    'n': 'n',

    # Labials (Oshthya)
    'ph': 'P', 'p': 'p',
    'bh': 'B', 'b': 'b',
    'm': 'm',

    # Semivowels, Sibilants, Aspirate
    'y': 'y', 'r': 'r', 'l': 'l', 'v': 'v',
    'z': 'S',  # HK ś -> SLP1 ś
    'S': 'z',  # HK ṣ -> SLP1 ṣ
    's': 's',
    'h': 'h',

    # Modifiers
    'M': 'M',  # Anusvāra
    'H': 'H',  # Visarga
}

# Pre-compile the regex pattern for HK -> SLP1.
# Sort keys by length descending to ensure multi-char tokens (e.g. 'kh', 'RR') 
# are matched greedily before single-char tokens (e.g. 'k', 'R').
_HK_KEYS_SORTED = sorted(_HK_TO_SLP1_DICT.keys(), key=len, reverse=True)
_HK_PATTERN = re.compile('|'.join(re.escape(k) for k in _HK_KEYS_SORTED))

# Pre-build translation table for SLP1 -> HK.
# Since SLP1 uses exactly one ASCII character per phoneme, 
# a fast C-level string translation table is perfectly safe and robust.
# (This naturally solves the z<->S swap issue).
_SLP1_TO_HK_TRANS = str.maketrans({v: k for k, v in _HK_TO_SLP1_DICT.items()})


def hk_to_slp1(text: str) -> str:
    """
    Convert a Harvard-Kyoto (HK) transliterated string to SLP1.
    Characters not belonging to the schema (e.g., spaces) are left unchanged.
    
    Args:
        text (str): Input string in Harvard-Kyoto.
        
    Returns:
        str: Transliterated string in SLP1.
    """
    if not text:
        return ""
    return _HK_PATTERN.sub(lambda m: _HK_TO_SLP1_DICT[m.group(0)], text)


def slp1_to_hk(text: str) -> str:
    """
    Convert an SLP1 transliterated string to Harvard-Kyoto (HK).
    Characters not belonging to the schema (e.g., spaces) are left unchanged.
    
    Args:
        text (str): Input string in SLP1.
        
    Returns:
        str: Transliterated string in Harvard-Kyoto.
    """
    if not text:
        return ""
    return text.translate(_SLP1_TO_HK_TRANS)

# ADD THESE TWO LINES AT THE END:
slp_to_hk = slp1_to_hk
hk_to_slp = hk_to_slp1