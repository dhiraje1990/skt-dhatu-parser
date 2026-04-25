"""
dhatu/_loader.py

Lazy loader for pre-computed msgpack binary tables.
As per Specification  (§4.1), data is stored in msgpack format under dhatu/data/
and loaded into memory only on first access.
"""

import os
import threading
from typing import Any, Dict, Optional
import msgpack

# Global cache for data tables
_CACHE: Dict[str, Any] = {}
_LOCK = threading.Lock()

# Directory where msgpack files are stored
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def _load_table(filename: str) -> Any:
    """
    Reads a msgpack file and returns the deserialized data.
    """
    path = os.path.join(DATA_DIR, f"{filename}.msgpack")
    
    # In a real environment, the data files must exist.
    # If the file is missing (e.g. before the build script runs), we return an empty dict
    # to prevent immediate crashes, though the app relies on this data.
    if not os.path.exists(path):
        return {}

    with open(path, "rb") as f:
        return msgpack.unpackb(f.read())

def get_data(table_name: str) -> Any:
    """
    Provides thread-safe lazy access to the requested data table.
    
    Available tables:
    - 'forms': Conjugation dict keyed by "dhatu|upasarga" (SLP1)
    - 'krdanta': Krdanta dict keyed by "dhatu|upasarga" (SLP1)
    - 'lemma_index': Inverted index keyed by surface form (HK)
    - 'meta': Metadata (gana, pada) keyed by dhatu (SLP1)
    """
    if table_name not in _CACHE:
        with _LOCK:
            if table_name not in _CACHE:
                _CACHE[table_name] = _load_table(table_name)
    return _CACHE[table_name]

def get_dhatu_meta(dhatu_slp1: str) -> Optional[Dict[str, Any]]:
    """
    Helper to fetch metadata for a specific dhātu.
    Returns dict with keys: 'gana', 'pada', 'meaning'.
    """
    meta = get_data("meta")
    return meta.get(dhatu_slp1)

def get_forms_for(dhatu_slp1: str, upasarga_slp1: str = "") -> Optional[Dict[str, Any]]:
    """
    Helper to fetch conjugated forms.
    Key format in msgpack is "dhatu|upasarga".
    """
    forms = get_data("forms")
    key = f"{dhatu_slp1}|{upasarga_slp1}"
    return forms.get(key)

def get_krdanta_for(dhatu_slp1: str, upasarga_slp1: str = "") -> Optional[Dict[str, Any]]:
    """
    Helper to fetch kṛdanta forms.
    Key format in msgpack is "dhatu|upasarga".
    """
    krdanta = get_data("krdanta")
    key = f"{dhatu_slp1}|{upasarga_slp1}"
    return krdanta.get(key)

def search_lemma(hk_form: str) -> list:
    """
    Helper to lookup a surface form in the inverted index.
    Returns a list of match dictionaries.
    """
    index = get_data("lemma_index")
    return index.get(hk_form, [])

def get_all_dhatu_keys() -> list:
    """
    Returns all SLP1 dhatu keys available in the metadata.
    Useful for 'UnknownDhatuError' suggestions.
    """
    meta = get_data("meta")
    return list(meta.keys())