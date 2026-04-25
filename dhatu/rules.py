"""
dhatu/rules.py

Edge-case rule layer as per Spec  (§4.3).
Handles phonological changes like internal sandhi.
"""

def apply_internal_sandhi(prefix_slp1: str, stem_slp1: str) -> str:
    """
    Applies phonological rules for joining an upasarga to a stem.
    Example: ni + sad -> niSad.
    """
    if not prefix_slp1:
        return stem_slp1
        
    # Simplified rule for retroflexion (s -> z)
    if prefix_slp1.endswith(('i', 'u', 'e', 'o', 'I', 'U', 'f', 'F')):
        if stem_slp1.startswith('s'):
            return prefix_slp1 + 'z' + stem_slp1[1:]
            
    # Default concatenation
    return prefix_slp1 + stem_slp1

def is_irregular(dhatu_slp1: str) -> bool:
    """Check if a root is in the irregular list."""
    return dhatu_slp1 in {"as", "BU", "vid", "brU", "ah"}