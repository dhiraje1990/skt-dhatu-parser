"""
dhatu/models.py

Data models for the skt-dhatu-parser package.
These classes define the structure of the data returned by the public API.
As per Spec , all strings in these models are in Harvard-Kyoto (HK).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Constants used for ordering and keys in ConjugationTable
PURUSA_ORDER = ["prathama", "madhyama", "uttama"]
VACANA_ORDER = ["eka", "dvi", "bahu"]

@dataclass
class ConjugationTable:
    """
    Represents the full 3x3 conjugation grid for a specific lakāra and pada.
    See Spec §5.2.
    """
    dhatu: str
    upasarga: List[str]
    pada: str
    lakara: str
    # forms[puruSa][vacana] = form_string
    forms: Dict[str, Dict[str, str]]

    def table(self) -> List[List[str]]:
        """
        Returns a 3x3 grid: rows = puruSa (prathama -> uttama), 
        cols = vacana (eka -> dvi -> bahu).
        """
        grid = []
        for p in PURUSA_ORDER:
            row = []
            for v in VACANA_ORDER:
                row.append(self.forms.get(p, {}).get(v, ""))
            grid.append(row)
        return grid

    def flat(self) -> Dict[str, str]:
        """
        Returns a flat dictionary mapping 'puruSa_vacana' keys to form strings.
        Example: {'prathama_eka': 'pacati', ...}
        """
        flat_dict = {}
        for p in PURUSA_ORDER:
            for v in VACANA_ORDER:
                key = f"{p}_{v}"
                flat_dict[key] = self.forms.get(p, {}).get(v, "")
        return flat_dict

    def display(self) -> None:
        """
        Prints a formatted Unicode table to stdout.
        See Spec §5.5.
        """
        grid = self.table()
        
        # Calculate column widths for pretty printing
        # Start with header widths
        col_widths = [max(len(v), 8) for v in VACANA_ORDER]
        
        # Check widths of actual forms
        for row in grid:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(cell))

        # Header row
        header = f"{'':10} " + " ".join(f"{VACANA_ORDER[i]:<{col_widths[i]}}" for i in range(3))
        print(header)

        # Content rows
        for i, p_name in enumerate(PURUSA_ORDER):
            row_str = f"{p_name:10} " + " ".join(f"{grid[i][j]:<{col_widths[j]}}" for j in range(3))
            print(row_str)


@dataclass
class KrdantaSet:
    """
    Represents a set of kṛdanta forms for a dhātu.
    See Spec §5.3.
    """
    dhatu: str
    upasarga: List[str]
    # forms[suffix_name] = list of HK strings (e.g., 'kta': ['pakva'])
    forms: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class LemmaResult:
    """
    Represents a single analysis result for a given surface form.
    A single form can return multiple LemmaResults if ambiguous.
    See Spec §5.4.
    """
    dhatu: str
    upasarga: List[str]
    form_type: str  # "tinanta" | "krdanta"

    # Fields populated if form_type == "tinanta"
    lakara: Optional[str] = None
    pada: Optional[str] = None
    puruSa: Optional[str] = None
    vacana: Optional[str] = None

    # Fields populated if form_type == "krdanta"
    suffix: Optional[str] = None

    def __post_init__(self):
        """Ensure upasarga is always a list even if passed as None or a string."""
        if self.upasarga is None:
            self.upasarga = []
        elif isinstance(self.upasarga, str):
            self.upasarga = [self.upasarga] if self.upasarga else []