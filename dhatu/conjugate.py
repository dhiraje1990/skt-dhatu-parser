"""
dhatu/conjugate.py

Implementation of the core verb conjugation logic.
As per Spec  (§5.2), this module handles the retrieval 
and structuring of tinanta (conjugated) forms.
"""

from typing import Union, List, Dict, Optional
import difflib

from .models import ConjugationTable
from ._loader import get_forms_for, get_dhatu_meta, get_all_dhatu_keys
from ._transliterate import hk_to_slp1, slp1_to_hk
from .errors import PadaError, LakAraError, UnknownDhatuError

# Supported lakāras as per Spec (§2) + common variants used in tests
VALID_LAKARAS = {
    "lat", "lit", "lut", "lRt", "let", "loT", 
    "laG", "liG", "luG", "lRG", "vidhiliG"
}

VALID_PADAS = {"parasmai", "atmane", "both"}

def _get_suggestions(dhatu_hk: str) -> List[str]:
    """Find similar-looking dhātus for error reporting using SLP1 keys."""
    all_slp = get_all_dhatu_keys()
    all_hk = [slp1_to_hk(k) for k in all_slp]
    return difflib.get_close_matches(dhatu_hk, all_hk, n=3, cutoff=0.6)

def _get_single_table(
    dhatu_slp1: str, 
    upasarga_slp1: str, 
    lakara: str, 
    pada: str,
    dhatu_hk: str,
    upasarga_hk_list: List[str]
) -> ConjugationTable:
    """Internal helper to build a single ConjugationTable from msgpack data."""
    
    # 1. Fetch form data for this (dhatu, upasarga) combination
    all_data = get_forms_for(dhatu_slp1, upasarga_slp1)
    
    if not all_data:
        # If the specific combo isn't pre-computed, raise UnknownDhatu
        raise UnknownDhatuError(dhatu_hk)

    lakara_data = all_data.get(lakara)
    if not lakara_data:
        raise LakAraError(f"Lakāra '{lakara}' not found for dhātu '{dhatu_hk}'.")

    pada_data = lakara_data.get(pada)
    if not pada_data:
        # Check if the root supports this pada based on metadata
        meta = get_dhatu_meta(dhatu_slp1)
        supported_pada = meta.get('pada') if meta else "unknown"
        raise PadaError(f"Dhātu '{dhatu_hk}' ({supported_pada}) does not support '{pada}' pada.")

    # 2. Structure into the 3x3 dict required by ConjugationTable
    # forms[puruSa][vacana] = form_string
    structured_forms = {}
    purusas = ["prathama", "madhyama", "uttama"]
    vacanas = ["eka", "dvi", "bahu"]

    for p in purusas:
        structured_forms[p] = {}
        for v in vacanas:
            form_key = f"{p}_{v}"
            # Convert internal SLP1 strings back to HK for the public API
            slp1_val = pada_data.get(form_key, "")
            structured_forms[p][v] = slp1_to_hk(slp1_val)

    return ConjugationTable(
        dhatu=dhatu_hk,
        upasarga=upasarga_hk_list,
        pada=pada,
        lakara=lakara,
        forms=structured_forms
    )

def conjugate(
    dhatu: str,
    *,
    upasarga: Union[str, List[str]] = "",
    lakara: Union[str, List[str]] = "lat",
    pada: str = "both",
    script: str = "hk",  # always "hk" in v1
) -> Union[ConjugationTable, Dict[str, Union[ConjugationTable, Dict]]]:
    """
    Given a dhātu and grammatical specification, returns all conjugated forms.
    Input/Output is always Harvard-Kyoto (HK).
    
    Args:
        dhatu: Verb root in HK (e.g., "pac", "bhU").
        upasarga: Single prefix ("pra") or ordered list (["sam", "A"]).
        lakara: Single lakāra string ("lat") or list of lakāras.
        pada: "parasmai", "atmane", or "both".
        
    Returns:
        A ConjugationTable object or a dict of tables if multiple lakāras 
        or padas are involved.
    """
    # Normalize Transliteration to SLP1 for lookup
    dhatu_slp1 = hk_to_slp1(dhatu)
    
    # Normalize Upasarga
    if isinstance(upasarga, str):
        upasarga_list = [upasarga] if upasarga else []
    else:
        upasarga_list = upasarga
    
    # Joining logic: matches how build_data.py generates keys
    upasarga_slp1 = "".join(hk_to_slp1(u) for u in upasarga_list)
    
    # Normalize Lakara
    requested_lakaras = [lakara] if isinstance(lakara, str) else lakara
    for l in requested_lakaras:
        if l not in VALID_LAKARAS:
            raise LakAraError(f"Invalid lakāra: {l}")
            
    # Normalize Pada
    if pada not in VALID_PADAS:
        raise PadaError(f"Invalid pada: {pada}. Use 'parasmai', 'atmane', or 'both'.")

    # Verify Dhatu Existence in Meta
    meta = get_dhatu_meta(dhatu_slp1)
    if not meta:
        raise UnknownDhatuError(dhatu, _get_suggestions(dhatu))

    # Determine Padas based on root capability (Spec §7)
    dhatu_pada_type = meta.get('pada', 'ubhayapada')
    available_padas = []
    
    # Map metadata 'pada' strings to API 'pada' strings
    if dhatu_pada_type in ("parasmaipada", "ubhayapada"):
        available_padas.append("parasmai")
    if dhatu_pada_type in ("atmanepada", "ubhayapada"):
        available_padas.append("atmane")

    if pada != "both" and pada not in available_padas:
        raise PadaError(f"Dhātu '{dhatu}' does not support '{pada}' pada.")

    target_padas = [pada] if pada != "both" else available_padas

    # Generate Results
    results_by_lakara = {}
    
    for l_val in requested_lakaras:
        pada_results = {}
        for p_val in target_padas:
            # We wrap in try/except for 'both' requests to handle partial data
            try:
                pada_results[p_val] = _get_single_table(
                    dhatu_slp1, upasarga_slp1, l_val, p_val, dhatu, upasarga_list
                )
            except (LakAraError, UnknownDhatuError):
                if pada != "both":
                    raise

        # Simplify structure if only one pada requested/available
        if pada != "both":
             results_by_lakara[l_val] = pada_results.get(pada)
        else:
             results_by_lakara[l_val] = pada_results

    # Final Simplify: if user requested a single lakara as a string, return the table directly
    if isinstance(lakara, str):
        return results_by_lakara[lakara]
    
    return results_by_lakara