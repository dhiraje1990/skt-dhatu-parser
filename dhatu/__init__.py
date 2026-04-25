"""
dhatu/__init__.py

Public API for the skt-dhatu-parser package.
"""

from .conjugate import conjugate
from .krdanta import krdanta
from .analyse import analyse
from .models import (
    ConjugationTable, 
    KrdantaSet, 
    LemmaResult
)
from .errors import (
    DhatuError,
    PadaError,
    LakAraError,
    KrdantaError,
    UnknownDhatuError
)

__version__ = "1.0.0"
__all__ = [
    "conjugate",
    "krdanta",
    "analyse",
    "ConjugationTable",
    "KrdantaSet",
    "LemmaResult",
    "DhatuError",
    "PadaError",
    "LakAraError",
    "KrdantaError",
    "UnknownDhatuError",
]