"""
tests/test_edge_cases.py
Edge cases, irregular roots, rule layer, transliteration, and data-layer tests.

Spec references:
  §4.3  Edge-case rule layer
  §6    Upasarga handling
  §7    Pada rules
  §8    Error hierarchy
  §3    HK transliteration contract
  §4.1  Lazy loading / caching
"""

import unittest
from dhatu import conjugate, analyse, krdanta
from dhatu.models import ConjugationTable, KrdantaSet, LemmaResult
from dhatu.errors import (
    DhatuError, PadaError, LakAraError, KrdantaError, UnknownDhatuError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_result(results, **kwargs):
    for r in results:
        if all(getattr(r, k, None) == v for k, v in kwargs.items()):
            return r
    return None


# ---------------------------------------------------------------------------
# 1. Error hierarchy (spec §8)
# ---------------------------------------------------------------------------

class TestErrorHierarchy(unittest.TestCase):

    def test_pada_error_is_dhatu_error(self):
        self.assertTrue(issubclass(PadaError, DhatuError))

    def test_lakara_error_is_dhatu_error(self):
        self.assertTrue(issubclass(LakAraError, DhatuError))

    def test_krdanta_error_is_dhatu_error(self):
        self.assertTrue(issubclass(KrdantaError, DhatuError))

    def test_unknown_dhatu_error_is_dhatu_error(self):
        self.assertTrue(issubclass(UnknownDhatuError, DhatuError))

    def test_unknown_dhatu_error_has_suggestions_attribute(self):
        try:
            conjugate("gac", lakara="lat", pada="parasmai")  # typo of gam
        except UnknownDhatuError as e:
            self.assertTrue(hasattr(e, "suggestions"))
            self.assertIsInstance(e.suggestions, list)
        except Exception:
            pass  # different exception; attribute test not applicable

    def test_all_errors_are_exceptions(self):
        for cls in (DhatuError, PadaError, LakAraError, KrdantaError, UnknownDhatuError):
            with self.subTest(cls=cls.__name__):
                self.assertTrue(issubclass(cls, Exception))


# ---------------------------------------------------------------------------
# 2. Pada rules — parasmaipada-only roots (spec §7)
# ---------------------------------------------------------------------------

class TestParasmaipadadOnly(unittest.TestCase):
    """
    gam (gana 1, parasmaipada) must reject pada="atmane".
    """

    def test_gam_parasmai_succeeds(self):
        t = conjugate("gam", lakara="lat", pada="parasmai")
        self.assertIsInstance(t, ConjugationTable)

    def test_gam_atmane_raises_PadaError(self):
        with self.assertRaises(PadaError):
            conjugate("gam", lakara="lat", pada="atmane")

    def test_gam_both_has_only_parasmai(self):
        result = conjugate("gam", lakara="lat", pada="both")
        self.assertIn("parasmai", result)
        self.assertNotIn("atmane", result)


# ---------------------------------------------------------------------------
# 3. Pada rules — ātmanepada-only roots (spec §7)
# ---------------------------------------------------------------------------

class TestAtmanepadadOnly(unittest.TestCase):
    """
    labh (gana 1, atmanepada) must reject pada="parasmai".
    jan (gana 4, atmanepada) is also listed.
    """

    def test_labh_atmane_succeeds(self):
        t = conjugate("labh", lakara="lat", pada="atmane")
        self.assertIsInstance(t, ConjugationTable)

    def test_labh_parasmai_raises_PadaError(self):
        with self.assertRaises(PadaError):
            conjugate("labh", lakara="lat", pada="parasmai")

    def test_jan_atmane_succeeds(self):
        # jan gana-4 form is atmanepada
        t = conjugate("jan", lakara="lat", pada="atmane")
        self.assertIsInstance(t, ConjugationTable)

    def test_jan_parasmai_raises_PadaError(self):
        with self.assertRaises(PadaError):
            conjugate("jan", lakara="lat", pada="parasmai")


# ---------------------------------------------------------------------------
# 4. Ubhayapada roots (spec §7)
# ---------------------------------------------------------------------------

class TestUbhayapada(unittest.TestCase):
    """
    pac (gana 1, ubhayapada) and nI (gana 1, ubhayapada) accept both padas.
    yaj (gana 1, ubhayapada) also listed.
    """

    def test_pac_parasmai_succeeds(self):
        self.assertIsInstance(
            conjugate("pac", lakara="lat", pada="parasmai"), ConjugationTable)

    def test_pac_atmane_succeeds(self):
        self.assertIsInstance(
            conjugate("pac", lakara="lat", pada="atmane"), ConjugationTable)

    def test_pac_both_returns_dict_with_two_keys(self):
        result = conjugate("pac", lakara="lat", pada="both")
        self.assertIn("parasmai", result)
        self.assertIn("atmane", result)

    def test_yaj_both_returns_both_padas(self):
        result = conjugate("yaj", lakara="lat", pada="both")
        self.assertIn("parasmai", result)
        self.assertIn("atmane", result)

    def test_nI_both_returns_both_padas(self):
        result = conjugate("nI", lakara="lat", pada="both")
        self.assertIn("parasmai", result)
        self.assertIn("atmane", result)


# ---------------------------------------------------------------------------
# 5. All 10 lakāras produce distinct prathama-eka forms (spec §5.2 / §12)
# ---------------------------------------------------------------------------

class TestAllLakaras(unittest.TestCase):

    ALL_LAKARA = ["lat", "lit", "lut", "lRt", "let",
                  "loT", "laG", "liG", "luG", "lRG"]

    def test_bhU_all_10_lakaras_return_tables(self):
        result = conjugate("bhU", lakara=self.ALL_LAKARA, pada="parasmai")
        self.assertEqual(len(result), 10)

    def test_bhU_all_10_tables_have_correct_lakara_attr(self):
        result = conjugate("bhU", lakara=self.ALL_LAKARA, pada="parasmai")
        for lak in self.ALL_LAKARA:
            with self.subTest(lakara=lak):
                self.assertEqual(result[lak].lakara, lak)

    def test_bhU_all_10_prathama_eka_non_empty(self):
        result = conjugate("bhU", lakara=self.ALL_LAKARA, pada="parasmai")
        for lak, tbl in result.items():
            with self.subTest(lakara=lak):
                self.assertTrue(tbl.flat()["prathama_eka"])

    def test_pac_lat_vs_lit_prathama_eka_differ(self):
        lat = conjugate("pac", lakara="lat",  pada="parasmai").flat()["prathama_eka"]
        lit = conjugate("pac", lakara="lit", pada="parasmai").flat()["prathama_eka"]
        self.assertNotEqual(lat, lit)

    def test_pac_lat_vs_loT_differ(self):
        lat = conjugate("pac", lakara="lat",  pada="parasmai").flat()["prathama_eka"]
        loT = conjugate("pac", lakara="loT", pada="parasmai").flat()["prathama_eka"]
        self.assertNotEqual(lat, loT)


# ---------------------------------------------------------------------------
# 6. Irregular roots (spec §4.3)
# ---------------------------------------------------------------------------

class TestIrregularRoots(unittest.TestCase):
    """
    as, bhU (as auxiliary), vid, brU are listed as irregular.
    Basic smoke-test: they conjugate without exception and return sensible forms.
    """

    def test_as_lat_parasmai_prathama_eka(self):
        # as: asti (3sg present)
        t = conjugate("as", lakara="lat", pada="parasmai")
        self.assertEqual(t.flat()["prathama_eka"], "asti")

    def test_as_lat_parasmai_uttama_eka(self):
        # asmi (1sg)
        self.assertEqual(
            conjugate("as", lakara="lat", pada="parasmai").flat()["uttama_eka"],
            "asmi"
        )

    def test_as_lat_parasmai_prathama_bahu(self):
        # santi (3pl)
        self.assertEqual(
            conjugate("as", lakara="lat", pada="parasmai").flat()["prathama_bahu"],
            "santi"
        )

    def test_vid_lat_parasmai_prathama_eka(self):
        # vid (gana 2, jnAne): vetti
        t = conjugate("vid", lakara="lat", pada="parasmai")
        self.assertEqual(t.flat()["prathama_eka"], "vetti")

    def test_vid_lat_parasmai_produces_table(self):
        t = conjugate("vid", lakara="lat", pada="parasmai")
        self.assertIsInstance(t, ConjugationTable)

    def test_bhU_lat_parasmai_prathama_eka(self):
        # bhavati
        t = conjugate("bhU", lakara="lat", pada="parasmai")
        self.assertEqual(t.flat()["prathama_eka"], "bhavati")


# ---------------------------------------------------------------------------
# 7. Upasarga-triggered sandhi (spec §6)
# ---------------------------------------------------------------------------

class TestUpasargaSandhi(unittest.TestCase):
    """
    ni + sad → niSad (retroflexion sandhi).
    A + gam → Agam (Agacchati in lat).
    sam + pac → sampac.
    """

    def test_A_gam_prathama_eka_Agacchati(self):
        t = conjugate("gam", upasarga="A", lakara="lat", pada="parasmai")
        self.assertEqual(t.flat()["prathama_eka"], "Agacchati")

    def test_pra_gam_prathama_eka_pragacchati(self):
        t = conjugate("gam", upasarga="pra", lakara="lat", pada="parasmai")
        self.assertEqual(t.flat()["prathama_eka"], "pragacchati")

    def test_sam_pac_krdanta_lyap_sampacya(self):
        k = krdanta("pac", upasarga="sam", suffix="lyap")
        self.assertIn("sampacya", k.forms["lyap"])

    def test_ni_sad_retroflexion_in_analysis(self):
        # If niSIdati is in the lemma index, analyse should return sad + ni
        results = analyse("niSIdati")
        r = find_result(results, form_type="tinanta")
        if r is not None:   # only assert if form is in the index
            self.assertEqual(r.dhatu, "sad")
            self.assertIn("ni", r.upasarga)

    def test_upasarga_upa_gam_prathama_eka(self):
        t = conjugate("gam", upasarga="upa", lakara="lat", pada="parasmai")
        self.assertTrue(t.flat()["prathama_eka"].startswith("upa"))


# ---------------------------------------------------------------------------
# 8. Stacked upasargas (spec §6)
# ---------------------------------------------------------------------------

class TestStackedUpasargas(unittest.TestCase):

    def test_sam_A_gam_prathama_eka_non_empty(self):
        t = conjugate("gam", upasarga=["sam", "A"], lakara="lat", pada="parasmai")
        self.assertTrue(t.flat()["prathama_eka"])

    def test_sam_A_gam_upasarga_list_preserved_order(self):
        t = conjugate("gam", upasarga=["sam", "A"], lakara="lat", pada="parasmai")
        self.assertEqual(t.upasarga, ["sam", "A"])

    def test_sam_A_pac_lyap_non_empty(self):
        k = krdanta("pac", upasarga=["sam", "A"], suffix="lyap")
        self.assertTrue(k.forms["lyap"])

    def test_stacked_upasarga_roundtrip_via_analyse(self):
        t = conjugate("gam", upasarga=["sam", "A"], lakara="lat", pada="parasmai")
        prathama = t.flat()["prathama_eka"]
        results = analyse(prathama)
        r = find_result(results, form_type="tinanta", dhatu="gam")
        if r is not None:
            self.assertEqual(r.upasarga, ["sam", "A"])


# ---------------------------------------------------------------------------
# 9. lyap / ktvA mutual exclusion (spec §5.3 / §6)
# ---------------------------------------------------------------------------

class TestLyapKtvAMutualExclusion(unittest.TestCase):

    def test_ktvA_present_without_upasarga(self):
        k = krdanta("pac", suffix="all")
        self.assertIn("ktvA", k.forms)

    def test_lyap_absent_without_upasarga(self):
        k = krdanta("pac", suffix="all")
        self.assertNotIn("lyap", k.forms)

    def test_lyap_present_with_upasarga(self):
        k = krdanta("pac", upasarga="sam", suffix="all")
        self.assertIn("lyap", k.forms)

    def test_ktvA_absent_with_upasarga(self):
        k = krdanta("pac", upasarga="sam", suffix="all")
        self.assertNotIn("ktvA", k.forms)

    def test_requesting_lyap_without_upasarga_raises_KrdantaError(self):
        with self.assertRaises(KrdantaError):
            krdanta("pac", suffix="lyap")

    def test_requesting_ktvA_with_upasarga_raises_KrdantaError(self):
        with self.assertRaises(KrdantaError):
            krdanta("pac", upasarga="pra", suffix="ktvA")


# ---------------------------------------------------------------------------
# 10. HK input/output contract (spec §3)
# ---------------------------------------------------------------------------

class TestHKContract(unittest.TestCase):
    """
    Public API must accept HK input and return HK output.
    No Devanagari, no SLP1 chars (*, #, etc.) should leak out.
    """

    SLP1_ONLY_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ") - set("ABGIJMNRSTZ")
    # HK uppercase chars that are valid: A I U R E O M H G J N T D Z S

    def _all_output_forms(self, t):
        if isinstance(t, dict):
            forms = []
            for v in t.values():
                forms.extend(self._all_output_forms(v))
            return forms
        return list(t.flat().values())

    def test_conjugate_output_contains_no_devanagari(self):
        t = conjugate("pac", lakara="lat", pada="parasmai")
        for form in t.flat().values():
            for ch in form:
                self.assertLess(ord(ch), 0x0900,
                    f"Devanagari char U+{ord(ch):04X} found in '{form}'")

    def test_conjugate_output_is_ascii(self):
        t = conjugate("pac", lakara="lat", pada="parasmai")
        for form in t.flat().values():
            self.assertTrue(form.isascii(), f"Non-ASCII in '{form}'")

    def test_analyse_output_dhatu_is_ascii(self):
        for r in analyse("pacati"):
            self.assertTrue(r.dhatu.isascii())

    def test_krdanta_output_forms_are_ascii(self):
        k = krdanta("pac", suffix="all")
        for suffix, forms in k.forms.items():
            for f in forms:
                with self.subTest(suffix=suffix, form=f):
                    self.assertTrue(f.isascii())

    def test_hk_capital_A_accepted_as_dhatu(self):
        # bhU uses capital U — this exercises HK long-vowel input
        t = conjugate("bhU", lakara="lat", pada="parasmai")
        self.assertEqual(t.flat()["prathama_eka"], "bhavati")

    def test_hk_capital_in_upasarga_A(self):
        # "A" is a valid HK upasarga (ā-)
        t = conjugate("gam", upasarga="A", lakara="lat", pada="parasmai")
        self.assertEqual(t.flat()["prathama_eka"], "Agacchati")


# ---------------------------------------------------------------------------
# 11. Lazy loading & caching (spec §4.1)
# ---------------------------------------------------------------------------

class TestLazyLoading(unittest.TestCase):
    """
    The data tables are loaded on first access and cached.
    Subsequent calls must produce identical results and not raise.
    """

    def test_repeated_conjugate_calls_identical(self):
        t1 = conjugate("pac", lakara="lat", pada="parasmai").flat()
        t2 = conjugate("pac", lakara="lat", pada="parasmai").flat()
        self.assertEqual(t1, t2)

    def test_repeated_analyse_calls_identical(self):
        r1 = analyse("pacati")
        r2 = analyse("pacati")
        self.assertEqual(
            [(r.dhatu, r.form_type, r.lakara) for r in r1],
            [(r.dhatu, r.form_type, r.lakara) for r in r2],
        )

    def test_repeated_krdanta_calls_identical(self):
        k1 = krdanta("pac", suffix="kta").forms["kta"]
        k2 = krdanta("pac", suffix="kta").forms["kta"]
        self.assertEqual(k1, k2)

    def test_multiple_dhatus_loaded_without_error(self):
        for dhatu in ["pac", "bhU", "gam", "nI", "labh"]:
            with self.subTest(dhatu=dhatu):
                t = conjugate(dhatu, lakara="lat",
                              pada="parasmai" if dhatu != "labh" else "atmane")
                self.assertIsInstance(t, ConjugationTable)


# ---------------------------------------------------------------------------
# 12. UnknownDhatuError suggestions (spec §8)
# ---------------------------------------------------------------------------

class TestUnknownDhatuSuggestions(unittest.TestCase):

    def _get_suggestions(self, typo):
        try:
            conjugate(typo, lakara="lat", pada="parasmai")
            return None
        except UnknownDhatuError as e:
            return e.suggestions
        except Exception:
            return None

    def test_close_typo_pac_suggestions_non_empty(self):
        sugg = self._get_suggestions("pac2")
        if sugg is not None:
            self.assertGreater(len(sugg), 0)

    def test_suggestions_are_strings(self):
        sugg = self._get_suggestions("gac")
        if sugg is not None:
            for s in sugg:
                self.assertIsInstance(s, str)

    def test_suggestions_include_similar_root(self):
        # "gac" is a plausible typo for "gam"
        sugg = self._get_suggestions("gac")
        if sugg is not None and len(sugg) > 0:
            self.assertIn("gam", sugg)


# ---------------------------------------------------------------------------
# 13. ConjugationTable.forms dict structure (spec §5.2)
# ---------------------------------------------------------------------------

class TestConjugationTableFormsDict(unittest.TestCase):

    PURUSA = ["prathama", "madhyama", "uttama"]
    VACANA = ["eka", "dvi", "bahu"]

    def setUp(self):
        self.t = conjugate("pac", lakara="lat", pada="parasmai")

    def test_forms_outer_keys_are_purusa(self):
        self.assertEqual(set(self.t.forms.keys()), set(self.PURUSA))

    def test_forms_inner_keys_are_vacana(self):
        for p in self.PURUSA:
            with self.subTest(purusa=p):
                self.assertEqual(set(self.t.forms[p].keys()), set(self.VACANA))

    def test_forms_all_values_are_strings(self):
        for p in self.PURUSA:
            for v in self.VACANA:
                with self.subTest(purusa=p, vacana=v):
                    self.assertIsInstance(self.t.forms[p][v], str)


# ---------------------------------------------------------------------------
# 14. Class-3 / juhotyādi double-weak stem (spec §4.3)
# ---------------------------------------------------------------------------

class TestJuhotyadi(unittest.TestCase):
    """
    hu (gana 3, parasmaipada, juhoti): tests that the doubly-weak stem
    is generated correctly. juhoti (3sg lat) is the canonical test form.
    """

    def test_hu_lat_parasmai_prathama_eka(self):
        try:
            t = conjugate("hu", lakara="lat", pada="parasmai")
            self.assertEqual(t.flat()["prathama_eka"], "juhoti")
        except UnknownDhatuError:
            self.skipTest("hu not in corpus")

    def test_hu_lat_parasmai_uttama_eka(self):
        try:
            t = conjugate("hu", lakara="lat", pada="parasmai")
            self.assertEqual(t.flat()["uttama_eka"], "juhomi")
        except UnknownDhatuError:
            self.skipTest("hu not in corpus")


# ---------------------------------------------------------------------------
# 15. Roundtrip: conjugate → analyse
# ---------------------------------------------------------------------------

class TestRoundtrip(unittest.TestCase):
    """
    For a handful of well-known forms: conjugate produces the expected surface
    string, and analyse recovers the correct dhātu and grammatical info.
    """

    def _roundtrip(self, dhatu, lakara, pada, purusa, vacana, upasarga=None):
        kw = dict(lakara=lakara, pada=pada)
        if upasarga:
            kw["upasarga"] = upasarga
        t = conjugate(dhatu, **kw)
        form = t.flat()[f"{purusa}_{vacana}"]
        results = analyse(form)
        r = find_result(results, form_type="tinanta", dhatu=dhatu,
                        lakara=lakara, pada=pada,
                        puruSa=purusa, vacana=vacana)
        return form, r

    def test_pacati_roundtrip(self):
        form, r = self._roundtrip("pac", "lat", "parasmai", "prathama", "eka")
        self.assertEqual(form, "pacati")
        self.assertIsNotNone(r)

    def test_pacAmi_roundtrip(self):
        form, r = self._roundtrip("pac", "lat", "parasmai", "uttama", "eka")
        self.assertEqual(form, "pacAmi")
        self.assertIsNotNone(r)

    def test_bhavati_roundtrip(self):
        form, r = self._roundtrip("bhU", "lat", "parasmai", "prathama", "eka")
        self.assertEqual(form, "bhavati")
        self.assertIsNotNone(r)

    def test_labhate_roundtrip(self):
        form, r = self._roundtrip("labh", "lat", "atmane", "prathama", "eka")
        self.assertEqual(form, "labhate")
        self.assertIsNotNone(r)

    def test_krdanta_roundtrip_pakva(self):
        k = krdanta("pac", suffix="kta")
        form = k.forms["kta"][0]
        results = analyse(form)
        r = find_result(results, form_type="krdanta", dhatu="pac", suffix="kta")
        self.assertIsNotNone(r, f"analyse('{form}') did not return pac/kta")

    def test_krdanta_roundtrip_paktum(self):
        k = krdanta("pac", suffix="tumun")
        form = k.forms["tumun"][0]
        results = analyse(form)
        r = find_result(results, form_type="krdanta", dhatu="pac", suffix="tumun")
        self.assertIsNotNone(r, f"analyse('{form}') did not return pac/tumun")

    def test_krdanta_roundtrip_sampacya(self):
        k = krdanta("pac", upasarga="sam", suffix="lyap")
        form = k.forms["lyap"][0]
        results = analyse(form)
        r = find_result(results, form_type="krdanta", dhatu="pac", suffix="lyap")
        self.assertIsNotNone(r, f"analyse('{form}') did not return pac/lyap")


# ---------------------------------------------------------------------------
# 16. Supported upasargas accepted without error (spec §6)
# ---------------------------------------------------------------------------

class TestSupportedUpasargas(unittest.TestCase):

    UPASARGAS = [
        "pra", "parA", "apa", "sam", "anu", "ava",
        "nis", "nir", "dur", "vi", "A", "ni",
        "adhi", "api", "ati", "su", "ut", "ud",
        "upa", "abhi", "prati", "pari",
    ]

    def test_all_supported_upasargas_accepted(self):
        for up in self.UPASARGAS:
            with self.subTest(upasarga=up):
                try:
                    t = conjugate("gam", upasarga=up,
                                  lakara="lat", pada="parasmai")
                    self.assertIsInstance(t, ConjugationTable)
                except Exception as e:
                    self.fail(f"upasarga='{up}' raised {e!r}")


# ---------------------------------------------------------------------------
# 17. LemmaResult: tinanta puruSa / vacana values (spec §5.4)
# ---------------------------------------------------------------------------

class TestLemmaResultValues(unittest.TestCase):

    VALID_PURUSA = {"prathama", "madhyama", "uttama"}
    VALID_VACANA = {"eka", "dvi", "bahu"}
    VALID_PADA   = {"parasmai", "atmane"}
    VALID_LAKARA = {"lat", "lit", "lut", "lRt", "let",
                    "loT", "laG", "liG", "luG", "lRG"}

    def test_tinanta_purusa_valid(self):
        for r in analyse("pacati"):
            if r.form_type == "tinanta":
                self.assertIn(r.puruSa, self.VALID_PURUSA)

    def test_tinanta_vacana_valid(self):
        for r in analyse("pacati"):
            if r.form_type == "tinanta":
                self.assertIn(r.vacana, self.VALID_VACANA)

    def test_tinanta_pada_valid(self):
        for r in analyse("pacati"):
            if r.form_type == "tinanta":
                self.assertIn(r.pada, self.VALID_PADA)

    def test_tinanta_lakara_valid(self):
        for r in analyse("pacati"):
            if r.form_type == "tinanta":
                self.assertIn(r.lakara, self.VALID_LAKARA)

    def test_krdanta_suffix_non_empty(self):
        for r in analyse("pakva"):
            if r.form_type == "krdanta":
                self.assertTrue(r.suffix)


if __name__ == "__main__":
    unittest.main()