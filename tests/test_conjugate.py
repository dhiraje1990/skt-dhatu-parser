"""
tests/test_conjugate.py
Tests for dhatu.conjugate()

All forms use Harvard-Kyoto (HK) transliteration.
Reference dhātus drawn from dhatupatha.tsv:
  pac  – gana 1, ubhayapada  (pAke)
  bhU  – gana 1, parasmaipada (sattAyAm)
  gam  – gana 1, parasmaipada (gatau)
  nI   – gana 1, ubhayapada  (prApaNe)
  labh – gana 1, atmanepada  (prAptau)
"""

import unittest
from dhatu import conjugate
from dhatu.models import ConjugationTable
from dhatu.errors import PadaError, LakAraError, UnknownDhatuError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ALL_LAKARA = ["lat", "lit", "lut", "lRt", "let", "loT", "laG", "liG", "luG", "lRG"]
PURUSA     = ["prathama", "madhyama", "uttama"]
VACANA     = ["eka", "dvi", "bahu"]


# ---------------------------------------------------------------------------
# 1. Return-type & structural tests
# ---------------------------------------------------------------------------

class TestConjugateReturnType(unittest.TestCase):

    def test_returns_conjugation_table(self):
        t = conjugate("pac", lakara="lat", pada="parasmai")
        self.assertIsInstance(t, ConjugationTable)

    def test_table_attribute_dhatu(self):
        t = conjugate("pac", lakara="lat", pada="parasmai")
        self.assertEqual(t.dhatu, "pac")

    def test_table_attribute_lakara(self):
        t = conjugate("pac", lakara="lat", pada="parasmai")
        self.assertEqual(t.lakara, "lat")

    def test_table_attribute_pada(self):
        t = conjugate("pac", lakara="lat", pada="parasmai")
        self.assertEqual(t.pada, "parasmai")

    def test_table_attribute_upasarga_empty_list(self):
        t = conjugate("pac", lakara="lat", pada="parasmai")
        self.assertEqual(t.upasarga, [])

    def test_table_attribute_upasarga_single(self):
        t = conjugate("gam", upasarga="A", lakara="lat", pada="parasmai")
        self.assertEqual(t.upasarga, ["A"])

    def test_table_attribute_upasarga_list(self):
        t = conjugate("pac", upasarga=["sam", "A"], lakara="lat", pada="parasmai")
        self.assertEqual(t.upasarga, ["sam", "A"])


# ---------------------------------------------------------------------------
# 2. .table() shape
# ---------------------------------------------------------------------------

class TestConjugateTableMethod(unittest.TestCase):

    def setUp(self):
        self.t = conjugate("pac", lakara="lat", pada="parasmai")

    def test_table_is_list(self):
        self.assertIsInstance(self.t.table(), list)

    def test_table_has_three_rows(self):
        self.assertEqual(len(self.t.table()), 3)

    def test_each_row_has_three_cells(self):
        for row in self.t.table():
            with self.subTest(row=row):
                self.assertEqual(len(row), 3)

    def test_all_cells_are_non_empty_strings(self):
        for row in self.t.table():
            for cell in row:
                with self.subTest(cell=cell):
                    self.assertIsInstance(cell, str)
                    self.assertTrue(cell.strip())

    def test_table_row_order_prathama_madhyama_uttama(self):
        # spot-check: uttama eka (1st person singular) ends in -mi
        uttama_eka = self.t.table()[2][0]
        self.assertTrue(uttama_eka.endswith("mi"),
                        f"Expected uttama-eka to end with 'mi', got '{uttama_eka}'")


# ---------------------------------------------------------------------------
# 3. .flat() shape
# ---------------------------------------------------------------------------

class TestConjugateFlatMethod(unittest.TestCase):

    def setUp(self):
        self.flat = conjugate("pac", lakara="lat", pada="parasmai").flat()

    def test_flat_returns_dict(self):
        self.assertIsInstance(self.flat, dict)

    def test_flat_has_nine_entries(self):
        self.assertEqual(len(self.flat), 9)

    def test_flat_keys_format(self):
        expected_keys = {
            f"{p}_{v}" for p in PURUSA for v in VACANA
        }
        self.assertEqual(set(self.flat.keys()), expected_keys)

    def test_flat_values_are_non_empty_strings(self):
        for k, v in self.flat.items():
            with self.subTest(key=k):
                self.assertIsInstance(v, str)
                self.assertTrue(v.strip())


# ---------------------------------------------------------------------------
# 4. Specific conjugated forms — pac lat parasmai
#    Reference: spec §5.2 example
# ---------------------------------------------------------------------------

class TestPacLatParasmai(unittest.TestCase):
    """
    Expected table (spec §5.2):
        prathama : pacati   pacataH   pacanti
        madhyama : pacasi   pacathaH  pacatha
        uttama   : pacAmi   pacAvaH   pacAmaH
    """

    def setUp(self):
        self.t = conjugate("pac", lakara="lat", pada="parasmai")

    def test_prathama_eka(self):
        self.assertEqual(self.t.flat()["prathama_eka"], "pacati")

    def test_prathama_dvi(self):
        self.assertEqual(self.t.flat()["prathama_dvi"], "pacataH")

    def test_prathama_bahu(self):
        self.assertEqual(self.t.flat()["prathama_bahu"], "pacanti")

    def test_madhyama_eka(self):
        self.assertEqual(self.t.flat()["madhyama_eka"], "pacasi")

    def test_madhyama_dvi(self):
        self.assertEqual(self.t.flat()["madhyama_dvi"], "pacathaH")

    def test_madhyama_bahu(self):
        self.assertEqual(self.t.flat()["madhyama_bahu"], "pacatha")

    def test_uttama_eka(self):
        self.assertEqual(self.t.flat()["uttama_eka"], "pacAmi")

    def test_uttama_dvi(self):
        self.assertEqual(self.t.flat()["uttama_dvi"], "pacAvaH")

    def test_uttama_bahu(self):
        self.assertEqual(self.t.flat()["uttama_bahu"], "pacAmaH")

    def test_table_grid_matches_flat(self):
        flat = self.t.flat()
        grid = self.t.table()
        self.assertEqual(grid[0][0], flat["prathama_eka"])
        self.assertEqual(grid[1][1], flat["madhyama_dvi"])
        self.assertEqual(grid[2][2], flat["uttama_bahu"])


# ---------------------------------------------------------------------------
# 5. pada="both" behaviour
# ---------------------------------------------------------------------------

class TestPadaBoth(unittest.TestCase):

    def setUp(self):
        # pac is ubhayapada — both padas available
        self.result = conjugate("pac", lakara="lat", pada="both")

    def test_returns_dict_when_pada_both(self):
        self.assertIsInstance(self.result, dict)

    def test_dict_has_parasmai_key(self):
        self.assertIn("parasmai", self.result)

    def test_dict_has_atmane_key(self):
        self.assertIn("atmane", self.result)

    def test_parasmai_value_is_conjugation_table(self):
        self.assertIsInstance(self.result["parasmai"], ConjugationTable)

    def test_atmane_value_is_conjugation_table(self):
        self.assertIsInstance(self.result["atmane"], ConjugationTable)

    def test_parasmai_forms_non_empty(self):
        self.assertTrue(self.result["parasmai"].flat())

    def test_atmane_forms_non_empty(self):
        self.assertTrue(self.result["atmane"].flat())

    def test_atmane_prathama_eka_form(self):
        # pac ātmane lat 3sg: pacate
        self.assertEqual(
            self.result["atmane"].flat()["prathama_eka"], "pacate"
        )


# ---------------------------------------------------------------------------
# 6. lakara as list → dict of ConjugationTable
# ---------------------------------------------------------------------------

class TestLakaraList(unittest.TestCase):

    def setUp(self):
        self.result = conjugate("bhU", lakara=["lat", "laG", "loT"], pada="parasmai")

    def test_returns_dict_when_lakara_is_list(self):
        self.assertIsInstance(self.result, dict)

    def test_dict_keys_match_requested_lakaras(self):
        self.assertEqual(set(self.result.keys()), {"lat", "laG", "loT"})

    def test_each_value_is_conjugation_table(self):
        for lak, tbl in self.result.items():
            with self.subTest(lakara=lak):
                self.assertIsInstance(tbl, ConjugationTable)

    def test_each_table_has_correct_lakara_attribute(self):
        for lak, tbl in self.result.items():
            with self.subTest(lakara=lak):
                self.assertEqual(tbl.lakara, lak)

    def test_all_10_lakaras_parasmai(self):
        result = conjugate("bhU", lakara=ALL_LAKARA, pada="parasmai")
        self.assertEqual(set(result.keys()), set(ALL_LAKARA))


# ---------------------------------------------------------------------------
# 7. bhU lat parasmai spot-checks
# ---------------------------------------------------------------------------

class TestBhuLatParasmai(unittest.TestCase):

    def setUp(self):
        self.flat = conjugate("bhU", lakara="lat", pada="parasmai").flat()

    def test_prathama_eka(self):
        self.assertEqual(self.flat["prathama_eka"], "bhavati")

    def test_uttama_eka(self):
        self.assertEqual(self.flat["uttama_eka"], "bhavAmi")

    def test_prathama_bahu(self):
        self.assertEqual(self.flat["prathama_bahu"], "bhavanti")


# ---------------------------------------------------------------------------
# 8. gam with upasarga A
# ---------------------------------------------------------------------------

class TestGamWithUpasarga(unittest.TestCase):

    def setUp(self):
        self.t = conjugate("gam", upasarga="A", lakara="lat", pada="parasmai")

    def test_prathama_eka_is_Agacchati(self):
        self.assertEqual(self.t.flat()["prathama_eka"], "Agacchati")

    def test_upasarga_recorded_as_list(self):
        self.assertEqual(self.t.upasarga, ["A"])

    def test_dhatu_recorded_without_upasarga(self):
        self.assertEqual(self.t.dhatu, "gam")


# ---------------------------------------------------------------------------
# 9. labh — ātmanepada-only root
# ---------------------------------------------------------------------------

class TestLabhAtmanepada(unittest.TestCase):

    def test_labh_atmane_prathama_eka_lat(self):
        t = conjugate("labh", lakara="lat", pada="atmane")
        self.assertEqual(t.flat()["prathama_eka"], "labhate")

    def test_labh_pada_both_has_only_atmane(self):
        result = conjugate("labh", lakara="lat", pada="both")
        # labh is atmanepada-only; "both" should return only atmane
        self.assertIn("atmane", result)
        self.assertNotIn("parasmai", result)


# ---------------------------------------------------------------------------
# 10. nI ubhayapada with explicit ātmanepada
# ---------------------------------------------------------------------------

class TestNIAtmanepada(unittest.TestCase):

    def test_nI_atmane_prathama_eka(self):
        t = conjugate("nI", lakara="lat", pada="atmane")
        self.assertEqual(t.flat()["prathama_eka"], "nayate")

    def test_nI_parasmai_prathama_eka(self):
        t = conjugate("nI", lakara="lat", pada="parasmai")
        self.assertEqual(t.flat()["prathama_eka"], "nayati")


# ---------------------------------------------------------------------------
# 11. nI with upasarga anu, ātmanepada (spec §12)
# ---------------------------------------------------------------------------

class TestNIWithUpasargaAnu(unittest.TestCase):

    def test_anunI_atmane_prathama_eka(self):
        t = conjugate("nI", upasarga="anu", lakara="lat", pada="atmane")
        self.assertEqual(t.flat()["prathama_eka"], "anunayate")

    def test_upasarga_is_list(self):
        t = conjugate("nI", upasarga="anu", lakara="lat", pada="atmane")
        self.assertIsInstance(t.upasarga, list)


# ---------------------------------------------------------------------------
# 12. Stacked upasargas
# ---------------------------------------------------------------------------

class TestStackedUpasargas(unittest.TestCase):

    def test_two_upasargas_recorded_in_order(self):
        t = conjugate("pac", upasarga=["sam", "A"], lakara="lat", pada="parasmai")
        self.assertEqual(t.upasarga, ["sam", "A"])

    def test_stacked_upasarga_prathama_eka_non_empty(self):
        t = conjugate("pac", upasarga=["sam", "A"], lakara="lat", pada="parasmai")
        self.assertTrue(t.flat()["prathama_eka"])


# ---------------------------------------------------------------------------
# 13. .display() prints to stdout
# ---------------------------------------------------------------------------

class TestDisplayMethod(unittest.TestCase):

    def test_display_runs_without_error(self):
        import io, sys
        t = conjugate("pac", lakara="lat", pada="parasmai")
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            t.display()
        finally:
            sys.stdout = old
        output = buf.getvalue()
        self.assertIn("pacati", output)

    def test_display_output_has_column_header(self):
        import io, sys
        t = conjugate("pac", lakara="lat", pada="parasmai")
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            t.display()
        finally:
            sys.stdout = old
        output = buf.getvalue()
        self.assertIn("eka", output)


# ---------------------------------------------------------------------------
# 14. Error cases
# ---------------------------------------------------------------------------

class TestConjugateErrors(unittest.TestCase):

    def test_unknown_dhatu_raises_UnknownDhatuError(self):
        from dhatu.errors import UnknownDhatuError
        with self.assertRaises(UnknownDhatuError):
            conjugate("zzz", lakara="lat", pada="parasmai")

    def test_unknown_dhatu_has_suggestions(self):
        from dhatu.errors import UnknownDhatuError
        try:
            conjugate("pac2", lakara="lat", pada="parasmai")
        except UnknownDhatuError as e:
            self.assertIsInstance(e.suggestions, list)

    def test_invalid_lakara_raises_LakAraError(self):
        with self.assertRaises(LakAraError):
            conjugate("pac", lakara="xyz", pada="parasmai")

    def test_parasmai_only_root_with_atmane_raises_PadaError(self):
        # gam is parasmaipada-only
        with self.assertRaises(PadaError):
            conjugate("gam", lakara="lat", pada="atmane")

    def test_atmane_only_root_with_parasmai_raises_PadaError(self):
        # labh is atmanepada-only
        with self.assertRaises(PadaError):
            conjugate("labh", lakara="lat", pada="parasmai")

    def test_invalid_pada_string_raises_value_error(self):
        with self.assertRaises((ValueError, PadaError)):
            conjugate("pac", lakara="lat", pada="notapada")

    def test_invalid_lakara_in_list_raises_LakAraError(self):
        with self.assertRaises(LakAraError):
            conjugate("pac", lakara=["lat", "badlakara"], pada="parasmai")


# ---------------------------------------------------------------------------
# 15. Consistency checks
# ---------------------------------------------------------------------------

class TestConjugateConsistency(unittest.TestCase):

    def test_flat_and_table_agree_for_all_cells(self):
        t = conjugate("pac", lakara="lat", pada="parasmai")
        flat  = t.flat()
        grid  = t.table()
        for ri, p in enumerate(PURUSA):
            for ci, v in enumerate(VACANA):
                with self.subTest(purusa=p, vacana=v):
                    self.assertEqual(grid[ri][ci], flat[f"{p}_{v}"])

    def test_forms_dict_keys_are_purusa(self):
        t = conjugate("pac", lakara="lat", pada="parasmai")
        self.assertEqual(set(t.forms.keys()), set(PURUSA))

    def test_forms_dict_inner_keys_are_vacana(self):
        t = conjugate("pac", lakara="lat", pada="parasmai")
        for p, inner in t.forms.items():
            with self.subTest(purusa=p):
                self.assertEqual(set(inner.keys()), set(VACANA))

    def test_lat_and_laG_give_different_prathama_eka(self):
        lat = conjugate("pac", lakara="lat",  pada="parasmai").flat()["prathama_eka"]
        laG = conjugate("pac", lakara="laG", pada="parasmai").flat()["prathama_eka"]
        self.assertNotEqual(lat, laG)

    def test_default_lakara_is_lat(self):
        t_explicit = conjugate("pac", lakara="lat", pada="parasmai")
        t_default  = conjugate("pac", pada="parasmai")      # lakara default = "lat"
        self.assertEqual(t_explicit.flat(), t_default.flat())


if __name__ == "__main__":
    unittest.main()