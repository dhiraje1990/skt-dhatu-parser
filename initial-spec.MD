# `skt-dhatu-parser` — Sanskrit Verb Conjugation Python Package
## Specification v1.1

---

## 1. Overview

`dhatu` is a Python library for Sanskrit verb conjugation and dhātu analysis.
Given a dhātu (verb root) and a grammatical specification, it returns all
conjugated forms. Given a conjugated form or kṛdanta, it returns the dhātu
(and upasarga, if any). All input/output uses **Harvard-Kyoto (HK)** transliteration.
Data is stored as pre-computed binary (msgpack) tables for fast loading and a
minimal footprint, with a rule layer to handle edge cases.

---

## 2. Scope

### In scope for v1
| Feature | Detail |
|---|---|
| Conjugation | All 10 lakāras, parasmaipada + ātmanepada |
| Kṛdanta | śatṛ/śānac, kta/ktavatu, tumun, lyap/ktvā, + other common kṛt suffixes |
| Dhātu lookup | ~2000 dhātus from Dhātupāṭha + common upasargas |
| Lemmatisation | Conjugated form or kṛdanta → root dhātu (+ upasarga) |
| Sandhi | Internal sandhi only (within generated forms) |
| Transliteration | HK input/output |

### Out of scope for v1
- External sandhi joining between words
- Nominal declension (subanta)
- Taddhita suffixes
- Vedic-only / rare dhātus
- Pāṇini sūtra references in output
- GUI / web API

---

## 3. Transliteration Convention (HK)

All strings accepted and returned by the public API are in Harvard-Kyoto.

| Sanskrit | HK |
|---|---|
| अ आ | a A |
| इ ई | i I |
| उ ऊ | u U |
| ऋ ॠ | R RR |
| ए ऐ | e ai |
| ओ औ | o au |
| क ख ग घ ङ | k kh g gh G |
| च छ ज झ ञ | c ch j jh J |
| ट ठ ड ढ ण | T Th D Dh N |
| त थ द ध न | t th d dh n |
| प फ ब भ म | p ph b bh m |
| य र ल व | y r l v |
| श ष स ह | z S s h |
| anusvāra / visarga | M H |

Internally the library may use SLP1 for computation; the public API always speaks HK.

---

## 4. Data Architecture

### 4.1 Pre-computed binary tables

All conjugated forms are stored in **msgpack** files bundled inside the package
under `dhatu/data/`. The data is loaded lazily on first access and cached in
memory for the lifetime of the process.

```
dhatu/data/
    forms.msgpack       # conjugation table
    krdanta.msgpack     # kṛdanta table
    lemma_index.msgpack # reverse lookup: tinanta OR kṛdanta form → LemmaResult list
    meta.msgpack        # dhātu metadata: gaṇa, pada, class
```

### 4.2 Table schema

**forms.msgpack** — top-level dict keyed by `(dhatu_slp1, upasarga_slp1_or_empty)`,
value is a nested dict:

```
{
  (dhatu, upasarga): {
    lakara: {          # e.g. "lat"
      pada: {          # "parasmai" | "atmane"
        puruSa_vacana: str   # e.g. "prathamapuruSaekavacana" → form string
      }
    }
  }
}
```

**lemma_index.msgpack** — unified inverted index keyed by HK form string, value
is a list of match dicts (one form may be ambiguous across tinanta and kṛdanta):

```
{
  # tinanta entry
  "pacati": [
    { "form_type": "tinanta", "dhatu": "pac", "upasarga": "",
      "lakara": "lat", "pada": "parasmai",
      "puruSa": "prathama", "vacana": "eka" }
  ],
  # krdanta entry
  "paktvA": [
    { "form_type": "krdanta", "dhatu": "pac", "upasarga": "",
      "suffix": "ktvA" }
  ],
  # ambiguous: same surface form can be tinanta or krdanta
  "pacet": [
    { "form_type": "tinanta", "dhatu": "pac", "upasarga": "",
      "lakara": "vidhiliG", "pada": "parasmai",
      "puruSa": "prathama", "vacana": "eka" },
    { "form_type": "krdanta", "dhatu": "pac", "upasarga": "",
      "suffix": "yat" }
  ]
}
```

**krdanta.msgpack** — keyed by `(dhatu_slp1, upasarga_slp1_or_empty)`, value is
a dict keyed by kṛt suffix name → list of forms (gender/case variants where applicable):

```
{
  (dhatu, upasarga): {
    "SatR":    ["pacat", "pacantam", ...],  # nom/acc/… where relevant
    "SAnac":   [...],
    "kta":     ["pakva"],
    "ktavatu": ["paktavat"],
    "tumun":   ["paktum"],
    "ktvA":    ["paktvA"],
    "lyap":    ["sampacya"],   # only when upasarga present
    ...
  }
}
```

### 4.3 Edge-case rule layer

A small Python rule module `dhatu/rules.py` handles:
- Doubly-weak stems (e.g. class 3 / juhotyādi)
- Roots with multiple ablaut grades
- Ātmanepada-only roots (e.g. *śubh*, *jan*)
- Parasmaipada-only roots
- Ubhayapada roots with semantic pada distinction
- Irregular roots: *as*, *bhū* as auxiliaries, *vid*, *brū*, *ah*
- Upasarga-triggered phonological changes (e.g. *ni + sad* → *niṣad*)

The rule layer is invoked at **build time** (when generating the msgpack tables)
and at **query time** only for forms absent from the table (cache-miss path).

---

## 5. Public API

### 5.1 Module layout

```
dhatu/
    __init__.py          # re-exports top-level symbols
    conjugate.py         # conjugate()
    analyse.py           # analyse()
    models.py            # dataclasses: ConjugationTable, KrdantaSet, LemmaResult
    data/                # bundled msgpack files
    rules.py             # edge-case rule layer
    _loader.py           # lazy msgpack loader + cache
    _transliterate.py    # HK ↔ SLP1 conversion (internal)
```

### 5.2 `conjugate()`

```python
def conjugate(
    dhatu: str,
    *,
    upasarga: str | list[str] = "",
    lakara: str | list[str] = "lat",
    pada: str = "both",            # "parasmai" | "atmane" | "both"
    script: str = "hk",            # always "hk" in v1
) -> ConjugationTable:
    ...
```

**Parameters**

| Name | Type | Description |
|---|---|---|
| `dhatu` | `str` | Root in HK, e.g. `"pac"`, `"bhU"`, `"nI"` |
| `upasarga` | `str \| list[str]` | Single prefix or ordered list, e.g. `["sam", "A"]` |
| `lakara` | `str \| list[str]` | One or more of: `lat lit lut lRt let loT laG liG luG lRG` |
| `pada` | `str` | `"parasmai"`, `"atmane"`, or `"both"` |

**Returns: `ConjugationTable`**

```python
@dataclass
class ConjugationTable:
    dhatu:    str                  # HK, root as given
    upasarga: list[str]            # HK list, may be empty
    pada:     str                  # "parasmai" | "atmane" | "both"
    lakara:   str                  # e.g. "lat"
    forms:    dict[str, dict[str, str]]
    # forms[puruSa][vacana] = form_string
    # puruSa: "prathama" | "madhyama" | "uttama"
    # vacana:  "eka"      | "dvi"     | "bahu"

    def table(self) -> list[list[str]]:
        """3×3 grid: rows=puruSa (prathama→uttama), cols=vacana (eka dvi bahu)."""

    def flat(self) -> dict[str, str]:
        """{'prathama_eka': 'pacati', ...} — 9 entries per pada."""
```

When `pada="both"`, the return value is a `dict[str, ConjugationTable]` keyed
by `"parasmai"` and `"atmane"` (only the padas the root actually takes).

When `lakara` is a list, the return value is a `dict[str, ConjugationTable | dict]`
keyed by lakāra name.

**Example**

```python
from dhatu import conjugate

# Present tense, parasmaipada
t = conjugate("pac", lakara="lat", pada="parasmai")
print(t.table())
# [['pacati',  'pacataH',  'pacanti'],
#  ['pacasi',  'pacathaH', 'pacatha'],
#  ['pacAmi',  'pacAvaH',  'pacAmaH']]

# With upasarga
t2 = conjugate("gam", upasarga="A", lakara="lat", pada="parasmai")
# → Agacchati, Agacchataḥ …

# All lakāras at once
all_t = conjugate("bhU", lakara=["lat","laG","loT"], pada="parasmai")
# all_t["lat"].table(), all_t["laG"].table(), …
```

---

### 5.3 `krdanta()`

```python
def krdanta(
    dhatu: str,
    *,
    upasarga: str | list[str] = "",
    suffix: str | list[str] = "all",
) -> KrdantaSet:
    ...
```

**Supported suffix names**

| Name | Meaning | Example |
|---|---|---|
| `SatR` | present active participle (parasmai) | *pacat* |
| `SAnac` | present active participle (ātmane) | *pacamāna* |
| `kta` | past passive participle | *pakva* / *pacita* |
| `ktavatu` | past active participle | *paktavat* |
| `tumun` | infinitive | *paktum* |
| `ktvA` | indeclinable (no upasarga) | *paktvā* |
| `lyap` | indeclinable (with upasarga) | *sampacya* |
| `anIyar` | gerundive (-anīya) | *pacanīya* |
| `tavya` | gerundive (-tavya) | *paktavya* |
| `yat` | gerundive (-ya) | *pācya* |

**Returns: `KrdantaSet`**

```python
@dataclass
class KrdantaSet:
    dhatu:    str
    upasarga: list[str]
    forms:    dict[str, list[str]]
    # forms[suffix_name] = list of HK strings
    # (list because participles have gender/case variants)
```

**Example**

```python
from dhatu import krdanta

k = krdanta("pac", suffix=["kta", "tumun", "SatR"])
print(k.forms["kta"])    # ['pakva']
print(k.forms["tumun"])  # ['paktum']
print(k.forms["SatR"])   # ['pacat', 'pacantam', 'pacatA', ...]
```

---

### 5.4 `analyse()`

```python
def analyse(
    form: str,
) -> list[LemmaResult]:
    ...
```

Accepts any conjugated tinanta form **or any kṛdanta form** (in HK) as input.
Returns a list because a single surface form can be ambiguous — e.g. it may
parse as both a tinanta and a kṛdanta, or as two different dhātus.

**Returns: `list[LemmaResult]`**

```python
@dataclass
class LemmaResult:
    dhatu:    str            # HK root, e.g. "pac"
    upasarga: list[str]      # HK list, e.g. ["sam"] or []
    form_type: str           # "tinanta" | "krdanta"

    # If tinanta:
    lakara:  str | None      # e.g. "lat"
    pada:    str | None      # "parasmai" | "atmane"
    puruSa:  str | None      # "prathama" | "madhyama" | "uttama"
    vacana:  str | None      # "eka" | "dvi" | "bahu"

    # If kṛdanta:
    suffix:  str | None      # e.g. "kta", "SatR"
```

**Example**

```python
from dhatu import analyse

# tinanta input
results = analyse("pacati")
# [LemmaResult(dhatu='pac', upasarga=[], form_type='tinanta',
#              lakara='lat', pada='parasmai',
#              puruSa='prathama', vacana='eka', suffix=None)]

# krdanta input — indeclinable (lyap)
results2 = analyse("sampacya")
# [LemmaResult(dhatu='pac', upasarga=['sam'], form_type='krdanta',
#              suffix='lyap', lakara=None, pada=None,
#              puruSa=None, vacana=None)]

# krdanta input — past passive participle (kta)
results3 = analyse("pakva")
# [LemmaResult(dhatu='pac', upasarga=[], form_type='krdanta',
#              suffix='kta', lakara=None, pada=None,
#              puruSa=None, vacana=None)]

# krdanta input — infinitive (tumun)
results4 = analyse("paktum")
# [LemmaResult(dhatu='pac', upasarga=[], form_type='krdanta',
#              suffix='tumun', lakara=None, pada=None,
#              puruSa=None, vacana=None)]

# ambiguous form — same surface as both tinanta and krdanta
results5 = analyse("pacet")
# [LemmaResult(..., form_type='tinanta', lakara='vidhiliG', ...),
#  LemmaResult(..., form_type='krdanta', suffix='yat', ...)]
```

---

### 5.5 Convenience: `ConjugationTable.display()`

```python
t = conjugate("pac", lakara="lat", pada="parasmai")
t.display()
```

Prints a Unicode table to stdout (using HK strings). No external dependency needed.

```
          eka           dvi           bahu
prathama  pacati        pacataH       pacanti
madhyama  pacasi        pacathaH      pacatha
uttama    pacAmi        pacAvaH       pacAmaH
```

---

## 6. Upasarga Handling

Supported upasargas (v1):

`pra  parA  apa  sam  anu  ava  nis  nir  dur  dur  vi  AA  ni  adhi  api  ati  su  ut  ud  upa  abhi  prati  pari  upa`

Rules:
- Single upasarga: `upasarga="pra"`
- Stacked upasargas: `upasarga=["sam", "A"]` → *samā-* (applied left to right)
- Internal sandhi between upasarga and dhātu is handled automatically within the stored forms
- `lyap` kṛdanta is generated only when at least one upasarga is present; `ktvā` is suppressed in that case

---

## 7. Pada Rules

| Category | Behaviour |
|---|---|
| Parasmaipada-only (*pac*, *gam*, *kR*, …) | `pada="atmane"` raises `PadaError` |
| Ātmanepada-only (*zubh*, *jan*, *kamp*, …) | `pada="parasmai"` raises `PadaError` |
| Ubhayapada (*labh*, *yaj*, *vac*, …) | Both padas available; `pada="both"` returns both |
| Causative / Ṇic | Treated as separate dhātu entries suffixed `_Nic` in the table |

---

## 8. Error Handling

```python
class DhatuError(Exception): ...
class PadaError(DhatuError): ...      # wrong pada for this root
class LakAraError(DhatuError): ...    # unrecognised lakāra string
class KrdantaError(DhatuError): ...   # invalid suffix name, or lyap without upasarga / ktvA with upasarga
class UnknownDhatuError(DhatuError):  # root not in corpus
    suggestions: list[str]            # closest matches
```

---

## 9. Data Build Pipeline

The msgpack tables are **pre-built** and shipped with the package. The build
script is kept in `scripts/build_data.py` for reproducibility but is not
required at install time.

```
scripts/
    build_data.py        # reads source TSV → applies rules → writes msgpack
    sources/
        dhatupatha.tsv   # dhātu, gaṇa, pada, meaning (HK)
        upasarga_map.tsv # upasarga + dhātu → sandhi-applied prefix string
        irregular.py     # hand-coded irregular forms
```

### 9.0 Acquiring `dhatupatha.tsv`

Assemble the TSV once before running the build script using any of the
following sources. Multiple sources can be merged for better coverage.

---

**Option A — Inria Heritage Resources** *(GPL)*
```
git clone https://gitlab.inria.fr/huet/Heritage_Resources
```
Dhātu data lives under `ML/DATA/`. Convert to TSV with columns:
`dhatu_hk | gaNa | pada | meaning_en`. Best source for gaṇa and pada
accuracy.

---

**Option B — SanskritVerb by Dhaval Patel** *(MIT)*
```
git clone https://github.com/drdhaval2785/SanskritVerb
```
Well-structured dhātu list with gaṇa, pada, and meaning already separated.
Easiest to parse and most permissively licensed. Good starting point if you
want to bundle the TSV in the repo later.

---

**Option C — University of Hyderabad morphological data** *(license varies)*
```
git clone https://github.com/sanskrit/morphological_data
```
Useful for filling coverage gaps and cross-checking gaṇa/pada assignments for
the ~300 most common roots.

---

**Option D — Ashtadhyayi.com source** *(check repo license)*
```
git clone https://github.com/ashtadhyayi/ashtadhyayi
```
Dhātu list is embedded in the site data. Requires extraction but useful for
cross-validation of conjugated forms.

---

**Option E — Monier-Williams (Cologne)** *(digitisation terms apply)*
Download `mw.xml` from `www.sanskrit-lexicon.uni-koeln.de`. Join on the HK
root key to enrich `meta.msgpack` with English meanings. Use as a supplement
to any of the above, not as a standalone dhātu source.

---

**Recommended approach**
Use **Option B** as the base (clean structure, MIT), fill gaps with **Option C**,
validate gaṇa/pada against **Option A**, and spot-check conjugated forms against
`ashtadhyayi.com` and `sanskritabhyas.in` for the 50 most common dhātus.

The final `dhatupatha.tsv` should have ~2000 rows and live at
`scripts/sources/dhatupatha.tsv`.

---

Build steps:
1. Parse `dhatupatha.tsv` (~2000 entries)
2. For each dhātu × upasarga combination, compute all 10 lakāras × 2 padas × 9 cells = 180 forms
3. Apply rule layer for edge cases and irregulars
4. Build inverted lemma index
5. Serialise all tables to msgpack with `msgpack.packb(data, use_bin_type=True)`

Estimated compressed table size: **< 15 MB** for full corpus.

---

## 10. Dependencies

| Package | Use | Required |
|---|---|---|
| `msgpack` | Binary data deserialisation | Yes |
| `numpy` | Optional fast array ops in build script | Build-only (optional) |

No runtime dependency on numpy. Install footprint is `msgpack` only.

---

## 11. Package Structure

```
dhatu/
    __init__.py
    conjugate.py
    analyse.py
    krdanta.py
    models.py
    rules.py
    _loader.py
    _transliterate.py
    data/
        forms.msgpack
        krdanta.msgpack
        lemma_index.msgpack
        meta.msgpack
pyproject.toml
README.md
scripts/
    build_data.py
    sources/
tests/
    test_conjugate.py
    test_analyse.py
    test_krdanta.py
    test_edge_cases.py
```

---

## 12. Example Session

```python
from dhatu import conjugate, analyse, krdanta

# 1. Conjugate bhU in all 10 lakāras, parasmaipada
all_forms = conjugate("bhU", lakara=[
    "lat","lit","lut","lRt","let","loT","laG","liG","luG","lRG"
], pada="parasmai")
for lak, tbl in all_forms.items():
    print(f"--- {lak} ---")
    tbl.display()

# 2. Conjugate nI with upasarga anu, ātmanepada
t = conjugate("nI", upasarga="anu", lakara="lat", pada="atmane")
t.display()

# 3. Analyse a tinanta
for r in analyse("pacati"):
    print(r.dhatu, r.form_type, r.lakara)   # pac  tinanta  lat

# 4. Analyse a kṛdanta — ktavatu
for r in analyse("nItavat"):
    print(r.dhatu, r.form_type, r.suffix)   # nI  krdanta  ktavatu

# 5. Analyse a kṛdanta — lyap (with upasarga)
for r in analyse("sampacya"):
    print(r.dhatu, r.upasarga, r.suffix)    # pac  ['sam']  lyap

# 6. Analyse a kṛdanta — tumun
for r in analyse("paktum"):
    print(r.dhatu, r.suffix)                # pac  tumun

# 7. All kṛdantas of pac with sam
k = krdanta("pac", upasarga="sam")
print(k.forms["lyap"])    # ['sampacya']
print(k.forms["kta"])     # ['sampakva']

# 8. Ambiguous form (tinanta + krdanta)
for r in analyse("jita"):
    print(r.dhatu, r.form_type, r.suffix or r.lakara)
    # ji  krdanta  kta
```
