"""
dhatu/krdanta.py
Logic for kṛdanta retrieval with automatic lyap/ktvA filtering.
"""
from typing import Union, List, Dict
import difflib

from .models import KrdantaSet
from ._loader import get_krdanta_for, get_dhatu_meta, get_all_dhatu_keys
from ._transliterate import hk_to_slp1, slp1_to_hk
from .errors import KrdantaError, UnknownDhatuError

VALID_SUFFIXES = {
    "SatR", "SAnac", "kta", "ktavatu", "tumun", 
    "ktvA", "lyap", "anIyar", "tavya", "yat"
}

def _get_suggestions(dhatu_hk: str) -> List[str]:
    all_hk = [slp1_to_hk(k) for k in get_all_dhatu_keys()]
    return difflib.get_close_matches(dhatu_hk, all_hk, n=3, cutoff=0.6)

def krdanta(
    dhatu: str,
    *,
    upasarga: Union[str, List[str]] = "",
    suffix: Union[str, List[str]] = "all",
) -> KrdantaSet:
    dhatu_slp1 = hk_to_slp1(dhatu)
    if isinstance(upasarga, str):
        upasarga_list = [upasarga] if upasarga else []
    else:
        upasarga_list = upasarga
    
    has_upasarga = len(upasarga_list) > 0
    upasarga_slp1 = "".join(hk_to_slp1(u) for u in upasarga_list)

    if suffix == "all":
        requested_suffixes = list(VALID_SUFFIXES)
        if has_upasarga:
            if "ktvA" in requested_suffixes: requested_suffixes.remove("ktvA")
        else:
            if "lyap" in requested_suffixes: requested_suffixes.remove("lyap")
    elif isinstance(suffix, str):
        requested_suffixes = [suffix]
    else:
        requested_suffixes = suffix

    for s in requested_suffixes:
        if s not in VALID_SUFFIXES:
            raise KrdantaError(f"Invalid kṛdanta suffix: {s}")
        if s == "lyap" and not has_upasarga:
            raise KrdantaError("Suffix 'lyap' requires an upasarga.")
        if s == "ktvA" and has_upasarga:
            raise KrdantaError("Suffix 'ktvA' cannot be used with an upasarga (use 'lyap').")

    meta = get_dhatu_meta(dhatu_slp1)
    if not meta:
        raise UnknownDhatuError(dhatu, _get_suggestions(dhatu))

    all_krdanta_data = get_krdanta_for(dhatu_slp1, upasarga_slp1) or {}

    result_forms = {}
    for s_name in requested_suffixes:
        forms_slp1 = all_krdanta_data.get(s_name)
        if forms_slp1:
            if isinstance(forms_slp1, list):
                result_forms[s_name] = [slp1_to_hk(f) for f in forms_slp1]
            else:
                result_forms[s_name] = [slp1_to_hk(forms_slp1)]
        else:
            if suffix != "all": result_forms[s_name] = []

    return KrdantaSet(dhatu=dhatu, upasarga=upasarga_list, forms=result_forms)