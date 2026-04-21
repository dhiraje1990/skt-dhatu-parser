from dataclasses import dataclass, field
from typing import Optional, List, Dict

# --- Error Classes ---

class DhatuError(Exception):
    """Base error for the dhatu package."""
    pass

class PadaError(DhatuError):
    """Raised when an invalid pada is requested for a specific root."""
    pass

class LakAraError(DhatuError):
    """Raised when an unrecognized lakara string is provided."""
    pass

class KrdantaError(DhatuError):
    """Raised for invalid suffixes or incompatible prefix/suffix combinations."""
    pass

class UnknownDhatuError(DhatuError):
    """Raised when a root is not found in the corpus."""
    def __init__(self, message: str, suggestions: List[str] = None):
        super().__init__(message)
        self.suggestions = suggestions or []

# --- Data Models ---

@dataclass
class ConjugationTable:
    dhatu: str                  # HK
    upasarga: List[str]         # HK
    pada: str                   # "parasmai" | "atmane"
    lakara: str                 # e.g., "lat"
    # forms[puruSa][vacana] = form_string
    forms: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def table(self) -> List[List[str]]:
        """Returns a 3x3 grid: rows=puruSa (prathama to uttama), cols=vacana (eka, dvi, bahu)."""
        purusas = ["prathama", "madhyama", "uttama"]
        vacanas = ["eka", "dvi", "bahu"]
        
        grid = []
        for p in purusas:
            row = []
            for v in vacanas:
                row.append(self.forms.get(p, {}).get(v, ""))
            grid.append(row)
        return grid

    def flat(self) -> Dict[str, str]:
        """Returns a flat dictionary: {'prathama_eka': 'pacati', ...}"""
        flat_map = {}
        for p, vacs in self.forms.items():
            for v, form in vacs.items():
                flat_map[f"{p}_{v}"] = form
        return flat_map

    def display(self):
        """Prints a Unicode table to stdout."""
        rows = self.table()
        headers = ["", "eka", "dvi", "bahu"]
        labels = ["prathama", "madhyama", "uttama"]
        
        # Calculate column widths
        col_widths = [10, 15, 15, 15]
        
        # Print Header
        header_line = "".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
        print(header_line)
        
        # Print Rows
        for i, row in enumerate(rows):
            line = labels[i].ljust(col_widths[0])
            for j, cell in enumerate(row):
                line += cell.ljust(col_widths[j+1])
            print(line)

@dataclass
class KrdantaSet:
    dhatu: str
    upasarga: List[str]
    # forms[suffix_name] = list of HK strings
    forms: Dict[str, List[str]] = field(default_factory=dict)

@dataclass
class LemmaResult:
    dhatu: str            # HK root
    upasarga: List[str]   # HK list
    form_type: str        # "tinanta" | "krdanta"

    # Tinanta specific fields
    lakara: Optional[str] = None
    pada: Optional[str] = None
    puruSa: Optional[str] = None
    vacana: Optional[str] = None

    # Krdanta specific fields
    suffix: Optional[str] = None