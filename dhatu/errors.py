"""
dhatu/errors.py

Custom exceptions for the dhatu package as defined in Spec  (§8).
"""

class DhatuError(Exception):
    """Base exception for all errors in the dhatu package."""
    pass

class PadaError(DhatuError):
    """Raised when an invalid pada (parasmai/atmane) is requested for a root."""
    pass

class LakAraError(DhatuError):
    """Raised when an unrecognized or unsupported lakāra string is provided."""
    pass

class KrdantaError(DhatuError):
    """
    Raised for invalid kṛdanta requests, such as:
    - Invalid suffix names.
    - 'lyap' requested without an upasarga.
    - 'ktvA' requested with an upasarga.
    """
    pass

class UnknownDhatuError(DhatuError):
    """
    Raised when the requested root is not found in the corpus.
    Includes suggestions for similar-sounding dhātus.
    """
    def __init__(self, dhatu_hk: str, suggestions: list[str] = None):
        self.dhatu_hk = dhatu_hk
        self.suggestions = suggestions or []
        msg = f"Dhātu '{dhatu_hk}' not found in corpus."
        if self.suggestions:
            msg += f" Did you mean: {', '.join(self.suggestions)}?"
        super().__init__(msg)