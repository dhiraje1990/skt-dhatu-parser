import re

# Mapping: HK -> SLP1
# Note: We order long strings first (like 'RR') to ensure they match before 'R'
HK_TO_SLP1_MAP = {
    "RR": "F", "R": "f",
    "lRR": "X", "lR": "x",
    "ai": "E", "au": "O",
    "kh": "K", "gh": "G", "G": "N",
    "ch": "C", "jh": "J", "J": "Y",
    "Th": "W", "Dh": "Q", "T": "w", "D": "q", "N": "R",
    "th": "T", "dh": "D",
    "ph": "P", "bh": "B",
    "z": "S", "S": "z",
    "M": "M", "H": "H",
    "A": "A", "I": "I", "U": "U",
}

# Mapping: SLP1 -> HK
SLP1_TO_HK_MAP = {v: k for k, v in HK_TO_SLP1_MAP.items()}

# Regex patterns for fast replacement
_HK_PATTERN = re.compile("|".join(sorted(HK_TO_SLP1_MAP.keys(), key=len, reverse=True)))
_SLP1_PATTERN = re.compile("|".join(sorted(SLP1_TO_HK_MAP.keys(), key=len, reverse=True)))

def hk_to_slp1(text: str) -> str:
    """
    Converts Harvard-Kyoto to SLP1.
    Example: 'pacanti' -> 'pacanti', 'bhavati' -> 'bhavati', 'RRSi' -> 'fzi'
    """
    if not text:
        return ""
    return _HK_PATTERN.sub(lambda m: HK_TO_SLP1_MAP[m.group(0)], text)

def slp1_to_hk(text: str) -> str:
    """
    Converts SLP1 to Harvard-Kyoto.
    Example: 'fzi' -> 'RRSi', 'aGat' -> 'aghat'
    """
    if not text:
        return ""
    return _SLP1_PATTERN.sub(lambda m: SLP1_TO_HK_MAP[m.group(0)], text)

# Convenience aliases
to_slp1 = hk_to_slp1
from_slp1 = slp1_to_hk