"""
tests/test_analyse.py
Tests for dhatu.analyse()

All forms use Harvard-Kyoto (HK) transliteration.
Expected outputs are drawn directly from spec §5.4 examples and §12.
"""

import unittest
from dhatu import analyse
from dhatu.models import LemmaResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_result(results, **kwargs):
    """Return the first LemmaResult whose attributes match all given kwargs."""
    for r in results:
        if all(getattr(r, k, None) == v for k, v in kwargs.items()):
            return r
    return None


# ---------------------------------------------------------------------------
# 1. Return-type & base structure
# ---------------------------------------------------------------------------

class TestAnalyseReturnType(unittest.TestCase):

    def test_returns_list(self):
        self.assertIsInstance(analyse("pacati"), list)

    def test_returns_list_of_lemma_results(self):
        for item in analyse("pacati"):
            with self.subTest(item=item):
                self.assertIsInstance(item, LemmaResult)

    def test_non_existent_form_returns_empty_list(self):
        self.assertEqual(analyse("zzzneveraform"), [])

    def test_non_empty_for_known_form(self):
        self.assertTrue(len(analyse("pacati")) > 0)


# ---------------------------------------------------------------------------
# 2. LemmaResult attribute contract
# ---------------------------------------------------------------------------

class TestLemmaResultAttributes(unittest.TestCase):

    def setUp(self):
        self.results = analyse("pacati")
        self.r = self.results[0]

    def test_has_dhatu(self):
        self.assertTrue(hasattr(self.r, "dhatu"))

    def test_has_upasarga(self):
        self.assertTrue(hasattr(self.r, "upasarga"))

    def test_has_form_type(self):
        self.assertTrue(hasattr(self.r, "form_type"))

    def test_has_lakara(self):
        self.assertTrue(hasattr(self.r, "lakara"))

    def test_has_pada(self):
        self.assertTrue(hasattr(self.r, "pada"))

    def test_has_purusa(self):
        self.assertTrue(hasattr(self.r, "puruSa"))

    def test_has_vacana(self):
        self.assertTrue(hasattr(self.r, "vacana"))

    def test_has_suffix(self):
        self.assertTrue(hasattr(self.r, "suffix"))

    def test_upasarga_is_list(self):
        self.assertIsInstance(self.r.upasarga, list)


# ---------------------------------------------------------------------------
# 3. Tinanta: pacati  (spec §5.4 and §12)
# ---------------------------------------------------------------------------

class TestAnalysePacati(unittest.TestCase):
    """
    Expected:
    LemmaResult(dhatu='pac', upasarga=[], form_type='tinanta',
                lakara='lat', pada='parasmai',
                puruSa='prathama', vacana='eka', suffix=None)
    """

    def setUp(self):
        self.results = analyse("pacati")

    def test_at_least_one_result(self):
        self.assertGreater(len(self.results), 0)

    def test_dhatu_is_pac(self):
        r = find_result(self.results, form_type="tinanta", dhatu="pac")
        self.assertIsNotNone(r, "No tinanta result with dhatu='pac'")

    def test_form_type_is_tinanta(self):
        r = find_result(self.results, form_type="tinanta", dhatu="pac")
        self.assertEqual(r.form_type, "tinanta")

    def test_lakara_is_lat(self):
        r = find_result(self.results, form_type="tinanta", dhatu="pac")
        self.assertEqual(r.lakara, "lat")

    def test_pada_is_parasmai(self):
        r = find_result(self.results, form_type="tinanta", dhatu="pac")
        self.assertEqual(r.pada, "parasmai")

    def test_purusa_is_prathama(self):
        r = find_result(self.results, form_type="tinanta", dhatu="pac")
        self.assertEqual(r.puruSa, "prathama")

    def test_vacana_is_eka(self):
        r = find_result(self.results, form_type="tinanta", dhatu="pac")
        self.assertEqual(r.vacana, "eka")

    def test_suffix_is_none_for_tinanta(self):
        r = find_result(self.results, form_type="tinanta", dhatu="pac")
        self.assertIsNone(r.suffix)

    def test_upasarga_is_empty(self):
        r = find_result(self.results, form_type="tinanta", dhatu="pac")
        self.assertEqual(r.upasarga, [])


# ---------------------------------------------------------------------------
# 4. Tinanta: pacataH (prathama dvi)
# ---------------------------------------------------------------------------

class TestAnalysePacataH(unittest.TestCase):

    def setUp(self):
        self.results = analyse("pacataH")

    def test_dhatu_pac_prathama_dvi(self):
        r = find_result(self.results, dhatu="pac", form_type="tinanta",
                        puruSa="prathama", vacana="dvi")
        self.assertIsNotNone(r)

    def test_lakara_lat(self):
        r = find_result(self.results, dhatu="pac", form_type="tinanta", vacana="dvi")
        self.assertEqual(r.lakara, "lat")


# ---------------------------------------------------------------------------
# 5. Tinanta: pacAmi (uttama eka)
# ---------------------------------------------------------------------------

class TestAnalysePacAmi(unittest.TestCase):

    def test_uttama_eka_lat_parasmai(self):
        results = analyse("pacAmi")
        r = find_result(results, dhatu="pac", form_type="tinanta",
                        puruSa="uttama", vacana="eka", pada="parasmai")
        self.assertIsNotNone(r)


# ---------------------------------------------------------------------------
# 6. Kṛdanta: pakva — kta (spec §5.4)
# ---------------------------------------------------------------------------

class TestAnalysePakva(unittest.TestCase):
    """
    Expected:
    LemmaResult(dhatu='pac', upasarga=[], form_type='krdanta',
                suffix='kta', lakara=None, pada=None, ...)
    """

    def setUp(self):
        self.results = analyse("pakva")

    def test_at_least_one_result(self):
        self.assertGreater(len(self.results), 0)

    def test_form_type_krdanta(self):
        r = find_result(self.results, form_type="krdanta", dhatu="pac")
        self.assertIsNotNone(r)

    def test_suffix_is_kta(self):
        r = find_result(self.results, form_type="krdanta", dhatu="pac")
        self.assertEqual(r.suffix, "kta")

    def test_lakara_is_none(self):
        r = find_result(self.results, form_type="krdanta", dhatu="pac")
        self.assertIsNone(r.lakara)

    def test_pada_is_none(self):
        r = find_result(self.results, form_type="krdanta", dhatu="pac")
        self.assertIsNone(r.pada)

    def test_upasarga_empty(self):
        r = find_result(self.results, form_type="krdanta", dhatu="pac")
        self.assertEqual(r.upasarga, [])


# ---------------------------------------------------------------------------
# 7. Kṛdanta: paktum — tumun (spec §5.4 and §12)
# ---------------------------------------------------------------------------

class TestAnalysePaktum(unittest.TestCase):

    def setUp(self):
        self.results = analyse("paktum")

    def test_form_type_krdanta(self):
        r = find_result(self.results, form_type="krdanta", dhatu="pac")
        self.assertIsNotNone(r, "No krdanta result for 'paktum'")

    def test_suffix_is_tumun(self):
        r = find_result(self.results, form_type="krdanta", dhatu="pac")
        self.assertEqual(r.suffix, "tumun")


# ---------------------------------------------------------------------------
# 8. Kṛdanta: paktvA — ktvA
# ---------------------------------------------------------------------------

class TestAnalysePaktvA(unittest.TestCase):

    def setUp(self):
        self.results = analyse("paktvA")

    def test_dhatu_pac(self):
        r = find_result(self.results, form_type="krdanta", dhatu="pac")
        self.assertIsNotNone(r)

    def test_suffix_ktvA(self):
        r = find_result(self.results, form_type="krdanta", dhatu="pac")
        self.assertEqual(r.suffix, "ktvA")


# ---------------------------------------------------------------------------
# 9. Kṛdanta: sampacya — lyap with upasarga sam (spec §5.4 and §12)
# ---------------------------------------------------------------------------

class TestAnalyseSampacya(unittest.TestCase):
    """
    Expected:
    LemmaResult(dhatu='pac', upasarga=['sam'], form_type='krdanta',
                suffix='lyap', lakara=None, pada=None, ...)
    """

    def setUp(self):
        self.results = analyse("sampacya")

    def test_at_least_one_result(self):
        self.assertGreater(len(self.results), 0)

    def test_form_type_krdanta(self):
        r = find_result(self.results, form_type="krdanta")
        self.assertIsNotNone(r)

    def test_dhatu_is_pac(self):
        r = find_result(self.results, form_type="krdanta")
        self.assertEqual(r.dhatu, "pac")

    def test_suffix_is_lyap(self):
        r = find_result(self.results, form_type="krdanta")
        self.assertEqual(r.suffix, "lyap")

    def test_upasarga_is_sam(self):
        r = find_result(self.results, form_type="krdanta")
        self.assertEqual(r.upasarga, ["sam"])

    def test_lakara_none(self):
        r = find_result(self.results, form_type="krdanta")
        self.assertIsNone(r.lakara)


# ---------------------------------------------------------------------------
# 10. Kṛdanta: paktavat — ktavatu (spec §12)
# ---------------------------------------------------------------------------

class TestAnalysePaktavat(unittest.TestCase):

    def setUp(self):
        self.results = analyse("paktavat")

    def test_form_type_krdanta(self):
        r = find_result(self.results, form_type="krdanta", dhatu="pac")
        self.assertIsNotNone(r)

    def test_suffix_ktavatu(self):
        r = find_result(self.results, form_type="krdanta", dhatu="pac")
        self.assertEqual(r.suffix, "ktavatu")


# ---------------------------------------------------------------------------
# 11. Ambiguous form: pacet — tinanta + krdanta (spec §4.2 / §5.4)
# ---------------------------------------------------------------------------

class TestAnalysePacet(unittest.TestCase):
    """
    Expected two results:
      1. tinanta: lakara=vidhiliG, pada=parasmai, purusa=prathama, vacana=eka
      2. krdanta: suffix=yat
    """

    def setUp(self):
        self.results = analyse("pacet")

    def test_returns_multiple_results(self):
        self.assertGreater(len(self.results), 1)

    def test_contains_tinanta_result(self):
        r = find_result(self.results, form_type="tinanta")
        self.assertIsNotNone(r, "Expected a tinanta result in ambiguous 'pacet'")

    def test_contains_krdanta_result(self):
        r = find_result(self.results, form_type="krdanta")
        self.assertIsNotNone(r, "Expected a krdanta result in ambiguous 'pacet'")

    def test_tinanta_lakara_vidhiliG(self):
        r = find_result(self.results, form_type="tinanta")
        self.assertEqual(r.lakara, "vidhiliG")

    def test_tinanta_pada_parasmai(self):
        r = find_result(self.results, form_type="tinanta")
        self.assertEqual(r.pada, "parasmai")

    def test_tinanta_purusa_prathama(self):
        r = find_result(self.results, form_type="tinanta")
        self.assertEqual(r.puruSa, "prathama")

    def test_tinanta_vacana_eka(self):
        r = find_result(self.results, form_type="tinanta")
        self.assertEqual(r.vacana, "eka")

    def test_krdanta_suffix_yat(self):
        r = find_result(self.results, form_type="krdanta")
        self.assertEqual(r.suffix, "yat")

    def test_both_results_dhatu_pac(self):
        for r in self.results:
            with self.subTest(form_type=r.form_type):
                self.assertEqual(r.dhatu, "pac")


# ---------------------------------------------------------------------------
# 12. Kṛdanta: nItavat — ktavatu (spec §12)
# ---------------------------------------------------------------------------

class TestAnalyseNItavat(unittest.TestCase):

    def setUp(self):
        self.results = analyse("nItavat")

    def test_dhatu_is_nI(self):
        r = find_result(self.results, form_type="krdanta")
        self.assertIsNotNone(r)
        self.assertEqual(r.dhatu, "nI")

    def test_suffix_ktavatu(self):
        r = find_result(self.results, form_type="krdanta", dhatu="nI")
        self.assertEqual(r.suffix, "ktavatu")


# ---------------------------------------------------------------------------
# 13. Ambiguous: jita — krdanta (spec §12)
# ---------------------------------------------------------------------------

class TestAnalyseJita(unittest.TestCase):

    def setUp(self):
        self.results = analyse("jita")

    def test_contains_krdanta_for_ji(self):
        r = find_result(self.results, form_type="krdanta", dhatu="ji")
        self.assertIsNotNone(r)

    def test_krdanta_suffix_kta(self):
        r = find_result(self.results, form_type="krdanta", dhatu="ji")
        self.assertEqual(r.suffix, "kta")


# ---------------------------------------------------------------------------
# 14. Tinanta with upasarga: Agacchati
# ---------------------------------------------------------------------------

class TestAnalyseAgacchati(unittest.TestCase):

    def setUp(self):
        self.results = analyse("Agacchati")

    def test_dhatu_gam(self):
        r = find_result(self.results, form_type="tinanta", dhatu="gam")
        self.assertIsNotNone(r)

    def test_upasarga_A(self):
        r = find_result(self.results, form_type="tinanta", dhatu="gam")
        self.assertEqual(r.upasarga, ["A"])

    def test_lakara_lat(self):
        r = find_result(self.results, form_type="tinanta", dhatu="gam")
        self.assertEqual(r.lakara, "lat")


# ---------------------------------------------------------------------------
# 15. form_type values are exactly "tinanta" or "krdanta"
# ---------------------------------------------------------------------------

class TestFormTypeValues(unittest.TestCase):

    def _check_forms(self, *forms):
        for form in forms:
            for r in analyse(form):
                with self.subTest(form=form, result=r):
                    self.assertIn(r.form_type, ("tinanta", "krdanta"))

    def test_form_type_values(self):
        self._check_forms("pacati", "pakva", "paktum", "sampacya", "pacet")


# ---------------------------------------------------------------------------
# 16. Tinanta fields are None for krdanta results, and vice-versa
# ---------------------------------------------------------------------------

class TestFieldNullability(unittest.TestCase):

    def test_krdanta_tinanta_fields_are_none(self):
        for r in analyse("pakva"):
            if r.form_type == "krdanta":
                self.assertIsNone(r.lakara)
                self.assertIsNone(r.pada)
                self.assertIsNone(r.puruSa)
                self.assertIsNone(r.vacana)

    def test_tinanta_suffix_is_none(self):
        for r in analyse("pacati"):
            if r.form_type == "tinanta":
                self.assertIsNone(r.suffix)

    def test_tinanta_fields_populated(self):
        for r in analyse("pacati"):
            if r.form_type == "tinanta":
                self.assertIsNotNone(r.lakara)
                self.assertIsNotNone(r.pada)
                self.assertIsNotNone(r.puruSa)
                self.assertIsNotNone(r.vacana)


if __name__ == "__main__":
    unittest.main()