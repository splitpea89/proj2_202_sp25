from __future__ import annotations
import sys
import csv
from typing import *
from dataclasses import dataclass
import unittest
import math

sys.setrecursionlimit(10_000)

# Data Definitions

@dataclass(frozen=True)
class Row:
    country: str
    year: int
    electricity_and_heat_co2_emissions: Optional[float]
    electricity_and_heat_co2_emissions_per_capita: Optional[float]
    energy_co2_emissions: Optional[float]
    energy_co2_emissions_per_capita: Optional[float]
    total_co2_emissions_excluding_lucf: Optional[float]
    total_co2_emissions_excluding_lucf_per_capita: Optional[float]

@dataclass(frozen=True)
class Node:
    value: Row
    next: Optional[Node]

# Constants

EXPECTED_HEADER = [
    "country",
    "year",
    "electricity_and_heat_co2_emissions",
    "electricity_and_heat_co2_emissions_per_capita",
    "energy_co2_emissions",
    "energy_co2_emissions_per_capita",
    "total_co2_emissions_excluding_lucf",
    "total_co2_emissions_excluding_lucf_per_capita",
]

NUMERIC_FIELDS = [
    "electricity_and_heat_co2_emissions",
    "electricity_and_heat_co2_emissions_per_capita",
    "energy_co2_emissions",
    "energy_co2_emissions_per_capita",
    "total_co2_emissions_excluding_lucf",
    "total_co2_emissions_excluding_lucf_per_capita",
]

# Read CSV

def parse_float(s: str) -> Optional[float]:
    """Returns a float parsed from s, or None if s is empty."""
    if s == "":
        return None
    return float(s)

def parse_row(fields: list[str]) -> Row:
    """
    Purpose: Convert a list of string fields from a CSV line into a Row object,
    converting numeric strings to float (or None for missing values).
    """
    return Row(
        country=fields[0],
        year=int(fields[1]),
        electricity_and_heat_co2_emissions=parse_float(fields[2]),
        electricity_and_heat_co2_emissions_per_capita=parse_float(fields[3]),
        energy_co2_emissions=parse_float(fields[4]),
        energy_co2_emissions_per_capita=parse_float(fields[5]),
        total_co2_emissions_excluding_lucf=parse_float(fields[6]),
        total_co2_emissions_excluding_lucf_per_capita=parse_float(fields[7]),
    )

def build_list(rows: list[list[str]], index: int) -> Optional[Node]:
    """
    Purpose: Recursively build a linked list of Nodes from a list of CSV rows,
    starting at the given index. Returns None when all rows are consumed.
    """
    if index >= len(rows):
        return None
    return Node(
        value=parse_row(rows[index]),
        next=build_list(rows, index + 1)
    )

def read_csv_lines(filename: str) -> Optional[Node]:
    """
    Purpose: Open a CSV file, validate its header, and return a linked list
    of Row objects — one Node per data row.
    Raises ValueError if the header does not match EXPECTED_HEADER.
    """
    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        if header != EXPECTED_HEADER:
            raise ValueError("Unexpected header: got {}".format(header))
        all_rows = list(reader)
    return build_list(all_rows, 0)

# Count Rows 

def listlen(data: Optional[Node]) -> int:
    """
    Purpose: Recursively count and return the number of Nodes in the linked list.
    Returns 0 for an empty list.
    """
    if data is None:
        return 0
    return 1 + listlen(data.next)

# General Filtering 

def get_field(row: Row, field_name: str) -> Optional[Union[str, float, int]]:
    """
    Purpose: Return the value of the named field from a Row using getattr.
    Returns None if the field does not exist on the Row.
    """
    return getattr(row, field_name, None)

def compare(row_value: Union[str, float, int],
            comparison: str,
            target: Union[str, float, int]) -> bool:
    """
    Purpose: Compare row_value against target using the given comparison string.
    Supported comparisons: "equal", "less_than", "greater_than".
    Raises ValueError for unsupported comparison strings.
    """
    if comparison == "equal":
        return row_value == target
    elif comparison == "less_than":
        return row_value < target
    elif comparison == "greater_than":
        return row_value > target
    else:
        raise ValueError("Unknown comparison: {}".format(comparison))

def filter_rows(
    data: Optional[Node],
    field_name: str,
    comparison: str,
    value: Union[str, float, int]
) -> Optional[Node]:
    """
    Purpose: Recursively filter a linked list, keeping only Nodes whose Row
    satisfies the given field/comparison/value condition.
    - Only "equal" is allowed for the "country" field.
    - Rows with None in the target field are skipped.
    Raises ValueError if a non-equal comparison is used on "country".
    """
    if field_name == "country" and comparison != "equal":
        raise ValueError('Only "equal" comparison is allowed for the "country" field.')

    if data is None:
        return None

    rest = filter_rows(data.next, field_name, comparison, value)
    field_value = get_field(data.value, field_name)

    # Skip rows with missing data in the target field
    if field_value is None:
        return rest

    if compare(field_value, comparison, value):
        return Node(value=data.value, next=rest)
    else:
        return rest