"""
tests/test_krdanta.py
Tests for dhatu.krdanta()

All forms in HK.  Primary test dhātu: pac (gana 1, ubhayapada).
Spec reference: §5.3.
"""

import unittest
from dhatu import krdanta
from dhatu.models import KrdantaSet
from dhatu.errors import KrdantaError, UnknownDhatuError


ALL_SUFFIXES = [
    "SatR", "SAnac", "kta", "ktavatu",
    "tumun", "ktvA", "lyap",
    "anIyar", "tavya", "yat",
]


# ---------------------------------------------------------------------------
# 1. Return type
# ---------------------------------------------------------------------------

class TestKrdantaReturnType(unittest.TestCase):

    def test_returns_krdanta_set(self):
        k = krdanta("pac")
        self.assertIsInstance(k, KrdantaSet)

    def test_krdanta_set_has_dhatu(self):
        k = krdanta("pac")
        self.assertEqual(k.dhatu, "pac")

    def test_krdanta_set_has_upasarga(self):
        k = krdanta("pac")
        self.assertIsInstance(k.upasarga, list)

    def test_krdanta_set_upasarga_empty_default(self):
        k = krdanta("pac")
        self.assertEqual(k.upasarga, [])

    def test_krdanta_set_has_forms_dict(self):
        k = krdanta("pac")
        self.assertIsInstance(k.forms, dict)


# ---------------------------------------------------------------------------
# 2. suffix="all" returns all supported suffixes
# ---------------------------------------------------------------------------

class TestSuffixAll(unittest.TestCase):

    def setUp(self):
        # Without upasarga: lyap should not appear; ktvA should appear
        self.k = krdanta("pac", suffix="all")

    def test_suffix_all_contains_kta(self):
        self.assertIn("kta", self.k.forms)

    def test_suffix_all_contains_tumun(self):
        self.assertIn("tumun", self.k.forms)

    def test_suffix_all_contains_SatR(self):
        self.assertIn("SatR", self.k.forms)

    def test_suffix_all_contains_ktavatu(self):
        self.assertIn("ktavatu", self.k.forms)

    def test_suffix_all_contains_anIyar(self):
        self.assertIn("anIyar", self.k.forms)

    def test_suffix_all_contains_tavya(self):
        self.assertIn("tavya", self.k.forms)

    def test_suffix_all_contains_yat(self):
        self.assertIn("yat", self.k.forms)

    def test_suffix_all_contains_ktvA_without_upasarga(self):
        self.assertIn("ktvA", self.k.forms)

    def test_suffix_all_no_lyap_without_upasarga(self):
        # lyap is only generated when upasarga is present
        self.assertNotIn("lyap", self.k.forms)


# ---------------------------------------------------------------------------
# 3. suffix="all" with upasarga: lyap present, ktvA absent
# ---------------------------------------------------------------------------

class TestSuffixAllWithUpasarga(unittest.TestCase):

    def setUp(self):
        self.k = krdanta("pac", upasarga="sam", suffix="all")

    def test_lyap_present_with_upasarga(self):
        self.assertIn("lyap", self.k.forms)

    def test_ktvA_absent_with_upasarga(self):
        self.assertNotIn("ktvA", self.k.forms)


# ---------------------------------------------------------------------------
# 4. Specific forms — pac, no upasarga (spec §5.3 examples)
# ---------------------------------------------------------------------------

class TestPacKrdantaForms(unittest.TestCase):

    def setUp(self):
        self.k = krdanta("pac", suffix="all")

    def test_kta_pakva(self):
        self.assertIn("pakva", self.k.forms["kta"])

    def test_ktavatu_paktavat(self):
        self.assertIn("paktavat", self.k.forms["ktavatu"])

    def test_tumun_paktum(self):
        self.assertIn("paktum", self.k.forms["tumun"])

    def test_ktvA_paktvA(self):
        self.assertIn("paktvA", self.k.forms["ktvA"])

    def test_SatR_contains_pacat(self):
        # Nominative singular (stem form) is pacat
        self.assertIn("pacat", self.k.forms["SatR"])

    def test_SatR_multiple_forms(self):
        # SatR has gender/case variants
        self.assertGreater(len(self.k.forms["SatR"]), 1)


# ---------------------------------------------------------------------------
# 5. pac + sam: lyap and kta (spec §12)
# ---------------------------------------------------------------------------

class TestPacSamUpasarga(unittest.TestCase):

    def setUp(self):
        self.k = krdanta("pac", upasarga="sam")

    def test_lyap_sampacya(self):
        self.assertIn("sampacya", self.k.forms["lyap"])

    def test_kta_sampakva(self):
        self.assertIn("sampakva", self.k.forms["kta"])

    def test_upasarga_recorded(self):
        self.assertEqual(self.k.upasarga, ["sam"])


# ---------------------------------------------------------------------------
# 6. suffix as list
# ---------------------------------------------------------------------------

class TestSuffixList(unittest.TestCase):

    def test_suffix_list_returns_only_requested_keys(self):
        k = krdanta("pac", suffix=["kta", "tumun"])
        self.assertEqual(set(k.forms.keys()), {"kta", "tumun"})

    def test_suffix_list_single_item(self):
        k = krdanta("pac", suffix=["ktvA"])
        self.assertIn("ktvA", k.forms)
        self.assertIn("paktvA", k.forms["ktvA"])

    def test_suffix_list_three_items(self):
        k = krdanta("pac", suffix=["kta", "tumun", "SatR"])
        self.assertEqual(set(k.forms.keys()), {"kta", "tumun", "SatR"})


# ---------------------------------------------------------------------------
# 7. suffix as single string (not "all")
# ---------------------------------------------------------------------------

class TestSuffixSingleString(unittest.TestCase):

    def test_single_suffix_kta(self):
        k = krdanta("pac", suffix="kta")
        self.assertIn("kta", k.forms)

    def test_single_suffix_tumun(self):
        k = krdanta("pac", suffix="tumun")
        self.assertIn("tumun", k.forms)
        self.assertIn("paktum", k.forms["tumun"])


# ---------------------------------------------------------------------------
# 8. Forms are non-empty lists of HK strings
# ---------------------------------------------------------------------------

class TestFormValues(unittest.TestCase):

    def test_all_forms_are_lists(self):
        k = krdanta("pac", suffix="all")
        for suffix, forms in k.forms.items():
            with self.subTest(suffix=suffix):
                self.assertIsInstance(forms, list)

    def test_all_forms_non_empty(self):
        k = krdanta("pac", suffix="all")
        for suffix, forms in k.forms.items():
            with self.subTest(suffix=suffix):
                self.assertTrue(len(forms) > 0)

    def test_all_forms_are_strings(self):
        k = krdanta("pac", suffix="all")
        for suffix, forms in k.forms.items():
            for f in forms:
                with self.subTest(suffix=suffix, form=f):
                    self.assertIsInstance(f, str)
                    self.assertTrue(f.strip())


# ---------------------------------------------------------------------------
# 9. SAnac — ātmane present participle
# ---------------------------------------------------------------------------

class TestSAnac(unittest.TestCase):

    def test_SAnac_present(self):
        k = krdanta("pac", suffix="SAnac")
        self.assertIn("SAnac", k.forms)

    def test_SAnac_contains_pacamAna(self):
        k = krdanta("pac", suffix="SAnac")
        self.assertIn("pacamAna", k.forms["SAnac"])


# ---------------------------------------------------------------------------
# 10. Gerundives: anIyar, tavya, yat
# ---------------------------------------------------------------------------

class TestGerundives(unittest.TestCase):

    def test_anIyar_pacanIya(self):
        k = krdanta("pac", suffix="anIyar")
        self.assertIn("pacanIya", k.forms["anIyar"])

    def test_tavya_paktavya(self):
        k = krdanta("pac", suffix="tavya")
        self.assertIn("paktavya", k.forms["tavya"])

    def test_yat_pAcya(self):
        k = krdanta("pac", suffix="yat")
        self.assertIn("pAcya", k.forms["yat"])


# ---------------------------------------------------------------------------
# 11. nI with upasarga anu — lyap
# ---------------------------------------------------------------------------

class TestNIAnuLyap(unittest.TestCase):

    def test_lyap_present_for_anu_nI(self):
        k = krdanta("nI", upasarga="anu", suffix="lyap")
        self.assertIn("lyap", k.forms)
        self.assertTrue(len(k.forms["lyap"]) > 0)


# ---------------------------------------------------------------------------
# 12. Error cases
# ---------------------------------------------------------------------------

class TestKrdantaErrors(unittest.TestCase):

    def test_lyap_without_upasarga_raises_KrdantaError(self):
        with self.assertRaises(KrdantaError):
            krdanta("pac", suffix="lyap")   # lyap requires upasarga

    def test_ktvA_with_upasarga_raises_KrdantaError(self):
        with self.assertRaises(KrdantaError):
            krdanta("pac", upasarga="sam", suffix="ktvA")  # ktvA suppressed with upasarga

    def test_invalid_suffix_name_raises_KrdantaError(self):
        with self.assertRaises(KrdantaError):
            krdanta("pac", suffix="foobar")

    def test_invalid_suffix_in_list_raises_KrdantaError(self):
        with self.assertRaises(KrdantaError):
            krdanta("pac", suffix=["kta", "notasuffix"])

    def test_unknown_dhatu_raises_UnknownDhatuError(self):
        with self.assertRaises(UnknownDhatuError):
            krdanta("zzz", suffix="kta")

    def test_unknown_dhatu_has_suggestions(self):
        try:
            krdanta("pac2", suffix="kta")
        except UnknownDhatuError as e:
            self.assertIsInstance(e.suggestions, list)


# ---------------------------------------------------------------------------
# 13. Stacked upasargas
# ---------------------------------------------------------------------------

class TestStackedUpasargasKrdanta(unittest.TestCase):

    def test_stacked_upasarga_lyap(self):
        k = krdanta("gam", upasarga=["sam", "A"], suffix="lyap")
        self.assertIn("lyap", k.forms)
        self.assertTrue(len(k.forms["lyap"]) > 0)

    def test_upasarga_list_recorded(self):
        k = krdanta("gam", upasarga=["sam", "A"], suffix="lyap")
        self.assertEqual(k.upasarga, ["sam", "A"])


# ---------------------------------------------------------------------------
# 14. bhU — common root, all suffixes
# ---------------------------------------------------------------------------

class TestBhUKrdanta(unittest.TestCase):

    def test_bhu_kta_bhUta(self):
        k = krdanta("bhU", suffix="kta")
        self.assertIn("bhUta", k.forms["kta"])

    def test_bhu_tumun_bhavitum(self):
        k = krdanta("bhU", suffix="tumun")
        self.assertIn("bhavitum", k.forms["tumun"])

    def test_bhu_ktvA_bhUtvA(self):
        k = krdanta("bhU", suffix="ktvA")
        self.assertIn("bhUtvA", k.forms["ktvA"])


if __name__ == "__main__":
    unittest.main()