"""
dhatu/analyse.py

Implementation of the lemmatisation engine.
As per Spec  (§5.4), this module maps a surface form (tinanta or kṛdanta)
back to its root (dhātu) and grammatical metadata.
"""

from typing import List
from .models import LemmaResult
from ._loader import search_lemma

def analyse(form: str) -> List[LemmaResult]:
    """
    Accepts any conjugated tinanta form or kṛdanta form (in HK) as input.
    Returns a list of LemmaResult objects (one form may be ambiguous).
    
    Args:
        form: Surface string in Harvard-Kyoto.
        
    Returns:
        List of LemmaResult objects found in the pre-computed index.
    """
    if not form:
        return []

    # search_lemma returns a list of match dictionaries from the msgpack index
    matches = search_lemma(form)
    results = []

    for entry in matches:
        # Create LemmaResult for each match.
        # The index entry structure mirrors the LemmaResult fields.
        res = LemmaResult(
            dhatu=entry.get("dhatu", ""),
            # Upasarga is stored as a list in the index
            upasarga=entry.get("upasarga", []),
            form_type=entry.get("form_type", ""),
            
            # Tinanta fields (None if krdanta)
            lakara=entry.get("lakara"),
            pada=entry.get("pada"),
            puruSa=entry.get("puruSa"),
            vacana=entry.get("vacana"),
            
            # Krdanta field (None if tinanta)
            suffix=entry.get("suffix")
        )
        results.append(res)

    return results