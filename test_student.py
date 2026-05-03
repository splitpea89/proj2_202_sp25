
from __future__ import annotations
import unittest
from proj2 import (
    Row, Node,
    parse_float, parse_row, read_csv_lines,
    listlen, filter_rows, get_field, compare
)

ROW_USA = Row(
    country="USA",
    year=2000,
    electricity_and_heat_co2_emissions=2500.0,
    electricity_and_heat_co2_emissions_per_capita=8.9,
    energy_co2_emissions=5800.0,
    energy_co2_emissions_per_capita=20.5,
    total_co2_emissions_excluding_lucf=6200.0,
    total_co2_emissions_excluding_lucf_per_capita=22.1,
)

ROW_CANADA = Row(
    country="Canada",
    year=2010,
    electricity_and_heat_co2_emissions=130.0,
    electricity_and_heat_co2_emissions_per_capita=3.8,
    energy_co2_emissions=570.0,
    energy_co2_emissions_per_capita=16.6,
    total_co2_emissions_excluding_lucf=640.0,
    total_co2_emissions_excluding_lucf_per_capita=18.7,
)

ROW_GERMANY = Row(
    country="Germany",
    year=2020,
    electricity_and_heat_co2_emissions=280.0,
    electricity_and_heat_co2_emissions_per_capita=3.3,
    energy_co2_emissions=700.0,
    energy_co2_emissions_per_capita=8.4,
    total_co2_emissions_excluding_lucf=850.0,
    total_co2_emissions_excluding_lucf_per_capita=10.2,
)

ROW_MISSING = Row(
    country="Andorra",
    year=2010,
    electricity_and_heat_co2_emissions=None,
    electricity_and_heat_co2_emissions_per_capita=None,
    energy_co2_emissions=None,
    energy_co2_emissions_per_capita=None,
    total_co2_emissions_excluding_lucf=None,
    total_co2_emissions_excluding_lucf_per_capita=None,
)

LIST_THREE = Node(ROW_USA, Node(ROW_CANADA, Node(ROW_GERMANY, None)))

LIST_WITH_MISSING = Node(ROW_CANADA, Node(ROW_MISSING, Node(ROW_GERMANY, None)))


# parse_float 

class TestParseFloat(unittest.TestCase):

    def test_normal_value(self):
        self.assertEqual(parse_float("3.14"), 3.14)

    def test_integer_string(self):
        self.assertEqual(parse_float("42"), 42.0)

    def test_empty_string_returns_none(self):
        self.assertIsNone(parse_float(""))

    def test_zero(self):
        self.assertEqual(parse_float("0.0"), 0.0)


# parse_row 

class TestParseRow(unittest.TestCase):

    def test_complete_row(self):
        fields = ["USA", "2000", "2500.0", "8.9", "5800.0", "20.5", "6200.0", "22.1"]
        self.assertEqual(parse_row(fields), ROW_USA)

    def test_missing_values_become_none(self):
        fields = ["Andorra", "2010", "", "", "", "", "", ""]
        self.assertEqual(parse_row(fields), ROW_MISSING)

    def test_year_is_int(self):
        fields = ["USA", "2000", "2500.0", "8.9", "5800.0", "20.5", "6200.0", "22.1"]
        row = parse_row(fields)
        self.assertIsInstance(row.year, int)


# read_csv_lines 

class TestReadCsvLines(unittest.TestCase):

    def test_returns_node(self):
        result = read_csv_lines("sample.csv")
        self.assertIsInstance(result, Node)

    def test_correct_row_count(self):
        result = read_csv_lines("sample.csv")
        self.assertEqual(listlen(result), 10)

    def test_bad_header_raises(self):
        import tempfile, os
        bad_csv = "wrong,header\nUSA,2000\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(bad_csv)
            fname = f.name
        try:
            with self.assertRaises(ValueError):
                read_csv_lines(fname)
        finally:
            os.unlink(fname)

    def test_missing_values_parsed(self):
        result = read_csv_lines("sample.csv")
        # Walk the list to find Andorra
        node = result
        andorra_row = None
        while node is not None:
            if node.value.country == "Andorra":
                andorra_row = node.value
                break
            node = node.next
        self.assertIsNotNone(andorra_row)
        self.assertIsNone(andorra_row.electricity_and_heat_co2_emissions)
        self.assertIsNone(andorra_row.energy_co2_emissions)


# listlen 

class TestListlen(unittest.TestCase):

    def test_empty_list(self):
        self.assertEqual(listlen(None), 0)

    def test_single_node(self):
        self.assertEqual(listlen(Node(ROW_USA, None)), 1)

    def test_three_nodes(self):
        self.assertEqual(listlen(LIST_THREE), 3)


# get_field 

class TestGetField(unittest.TestCase):

    def test_get_country(self):
        self.assertEqual(get_field(ROW_USA, "country"), "USA")

    def test_get_numeric_field(self):
        self.assertEqual(get_field(ROW_USA, "energy_co2_emissions"), 5800.0)

    def test_get_missing_field_returns_none(self):
        self.assertIsNone(get_field(ROW_USA, "nonexistent_field"))

    def test_get_none_value_field(self):
        self.assertIsNone(get_field(ROW_MISSING, "energy_co2_emissions"))


# compare 

class TestCompare(unittest.TestCase):

    def test_equal_true(self):
        self.assertTrue(compare("USA", "equal", "USA"))

    def test_equal_false(self):
        self.assertFalse(compare("USA", "equal", "Canada"))

    def test_less_than_true(self):
        self.assertTrue(compare(100.0, "less_than", 200.0))

    def test_less_than_false(self):
        self.assertFalse(compare(300.0, "less_than", 200.0))

    def test_greater_than_true(self):
        self.assertTrue(compare(500.0, "greater_than", 100.0))

    def test_greater_than_false(self):
        self.assertFalse(compare(50.0, "greater_than", 100.0))

    def test_unknown_comparison_raises(self):
        with self.assertRaises(ValueError):
            compare(1.0, "not_a_real_comparison", 1.0)


# filter_rows 

class TestFilterRows(unittest.TestCase):

    def test_filter_by_country_equal(self):
        result = filter_rows(LIST_THREE, "country", "equal", "USA")
        self.assertEqual(listlen(result), 1)
        self.assertEqual(result.value.country, "USA")

    def test_filter_by_country_no_match(self):
        result = filter_rows(LIST_THREE, "country", "equal", "Iceland")
        self.assertIsNone(result)

    def test_filter_country_non_equal_raises(self):
        with self.assertRaises(ValueError):
            filter_rows(LIST_THREE, "country", "less_than", "USA")

    def test_filter_greater_than(self):
        result = filter_rows(LIST_THREE, "energy_co2_emissions", "greater_than", 600.0)
        self.assertEqual(listlen(result), 2)

    def test_filter_less_than(self):
        result = filter_rows(LIST_THREE, "total_co2_emissions_excluding_lucf", "less_than", 900.0)
        self.assertEqual(listlen(result), 2)

    def test_filter_equal_numeric(self):
        result = filter_rows(LIST_THREE, "year", "equal", 2010)
        self.assertEqual(listlen(result), 1)
        self.assertEqual(result.value.country, "Canada")

    def test_missing_data_rows_skipped(self):
        result = filter_rows(LIST_WITH_MISSING, "energy_co2_emissions", "greater_than", 0.0)
        self.assertEqual(listlen(result), 2)

    def test_empty_list_returns_none(self):
        result = filter_rows(None, "country", "equal", "USA")
        self.assertIsNone(result)

    def test_filter_preserves_row_data(self):
        result = filter_rows(LIST_THREE, "country", "equal", "Germany")
        self.assertEqual(result.value, ROW_GERMANY)


if __name__ == "__main__":
    unittest.main()