"""Edge case analysis helper for domain rules."""

import ast
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from pytestee.domain.models import TestFunction


class EdgeCaseType(Enum):
    """Types of edge cases to detect."""

    NUMERIC_ZERO = "numeric_zero"
    NUMERIC_NEGATIVE = "numeric_negative"
    NUMERIC_MAX_MIN = "numeric_max_min"
    NUMERIC_OVERFLOW = "numeric_overflow"
    NUMERIC_DIVISION_BY_ZERO = "numeric_division_by_zero"

    COLLECTION_EMPTY = "collection_empty"
    COLLECTION_SINGLE = "collection_single"
    COLLECTION_LARGE = "collection_large"

    STRING_NONE = "string_none"
    STRING_EMPTY = "string_empty"
    STRING_SPECIAL_CHARS = "string_special_chars"
    STRING_LONG = "string_long"
    STRING_UNICODE = "string_unicode"


class TestValueType(Enum):
    """Classification of test values."""

    NORMAL = "normal"
    EDGE_CASE = "edge_case"
    UNKNOWN = "unknown"


class EdgeCaseAnalyzer:
    """Helper class for analyzing edge case coverage in test functions."""

    # Edge case patterns
    NUMERIC_EDGE_PATTERNS: ClassVar[dict[EdgeCaseType, Any]] = {
        EdgeCaseType.NUMERIC_ZERO: [0, 0.0, "0", "0.0"],
        EdgeCaseType.NUMERIC_NEGATIVE: lambda x: isinstance(x, (int, float)) and x < 0,
        EdgeCaseType.NUMERIC_MAX_MIN: [
            "sys.maxsize", "float('inf')", "float('-inf')",
            "math.inf", "-math.inf", "2**31-1", "-2**31"
        ],
    }

    COLLECTION_EDGE_PATTERNS: ClassVar[dict[EdgeCaseType, Any]] = {
        EdgeCaseType.COLLECTION_EMPTY: [[], {}, set(), "[]", "{}", "set()"],
        EdgeCaseType.COLLECTION_SINGLE: lambda x: isinstance(x, (list, tuple, set)) and len(x) == 1,
    }

    STRING_EDGE_PATTERNS: ClassVar[dict[EdgeCaseType, Any]] = {
        EdgeCaseType.STRING_NONE: [None, "None"],
        EdgeCaseType.STRING_EMPTY: ["", '""', "''"],
        EdgeCaseType.STRING_SPECIAL_CHARS: ["\n", "\t", "\r", "\\n", "\\t", "\\r"],
        EdgeCaseType.STRING_UNICODE: lambda x: isinstance(x, str) and any(ord(c) > 127 for c in x),
    }

    @staticmethod
    def analyze_test_values(test_function: "TestFunction") -> dict[EdgeCaseType, bool]:
        """Analyze a test function for edge case coverage.

        Args:
            test_function: The test function to analyze

        Returns:
            Dictionary mapping edge case types to whether they are covered

        """
        edge_cases_found = {edge_type: False for edge_type in EdgeCaseType}

        # Extract all literal values and variable assignments
        test_values = EdgeCaseAnalyzer._extract_test_values(test_function)

        # Check each value against edge case patterns
        for value in test_values:
            detected_types = EdgeCaseAnalyzer._classify_value(value)
            for edge_type in detected_types:
                edge_cases_found[edge_type] = True

        return edge_cases_found

    @staticmethod
    def _extract_test_values(test_function: "TestFunction") -> list:
        """Extract all test values from a test function."""
        values = []

        for node in test_function.body:
            values.extend(EdgeCaseAnalyzer._extract_values_from_node(node))

        return values

    @staticmethod
    def _extract_values_from_node(node: ast.AST) -> list:
        """Recursively extract values from an AST node."""
        values = []

        if isinstance(node, ast.Constant):
            # Python 3.8+ uses ast.Constant for literals
            values.append(node.value)
        elif isinstance(node, ast.Str):
            # Older Python versions
            values.append(node.s)
        elif isinstance(node, ast.Num):
            # Older Python versions
            values.append(node.n)
        elif isinstance(node, ast.List):
            # List literals
            list_values = []
            for elt in node.elts:
                if isinstance(elt, ast.Constant):
                    list_values.append(elt.value)
            values.append(list_values)
        elif isinstance(node, ast.Dict):
            # Dictionary literals
            dict_values = {}
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
                    dict_values[k.value] = v.value
            values.append(dict_values)
        elif isinstance(node, ast.Set):
            # Set literals
            set_values = set()
            for elt in node.elts:
                if isinstance(elt, ast.Constant):
                    set_values.add(elt.value)
            values.append(set_values)
        elif isinstance(node, ast.Call):
            # Function calls that might create edge case values
            values.extend(EdgeCaseAnalyzer._extract_edge_case_calls(node))
        elif isinstance(node, ast.Name):
            # Variable names that might indicate edge cases
            if node.id in ['None', 'inf', 'maxsize']:
                values.append(node.id)

        # Recursively check child nodes
        for child in ast.iter_child_nodes(node):
            values.extend(EdgeCaseAnalyzer._extract_values_from_node(child))

        return values

    @staticmethod
    def _extract_edge_case_calls(node: ast.Call) -> list:
        """Extract edge case values from function calls."""
        values = []

        # Handle common edge case function calls
        if isinstance(node.func, ast.Attribute):
            if (isinstance(node.func.value, ast.Name) and
                node.func.value.id == "float" and
                node.func.attr in ["inf", "-inf"]):
                values.append(f"float('{node.func.attr}')")
        elif isinstance(node.func, ast.Name):
            if node.func.id in ["range", "list", "dict", "set"]:
                # Check for empty collections
                if not node.args:
                    values.append(f"{node.func.id}()")
                elif (len(node.args) == 1 and
                      isinstance(node.args[0], ast.Constant) and
                      node.args[0].value == 0):
                    values.append(f"{node.func.id}(0)")

        return values

    @staticmethod
    def _classify_value(value: Any) -> list[EdgeCaseType]:
        """Classify a value as normal or edge case."""
        edge_types = []

        # Check numeric edge cases
        if isinstance(value, (int, float)):
            if value == 0:
                edge_types.append(EdgeCaseType.NUMERIC_ZERO)
            elif value < 0:
                edge_types.append(EdgeCaseType.NUMERIC_NEGATIVE)
            elif abs(value) > 1000000:  # Large numbers
                edge_types.append(EdgeCaseType.NUMERIC_MAX_MIN)

        # Check collection edge cases
        elif isinstance(value, (list, tuple, set, dict)):
            if len(value) == 0:
                edge_types.append(EdgeCaseType.COLLECTION_EMPTY)
            elif len(value) == 1:
                edge_types.append(EdgeCaseType.COLLECTION_SINGLE)
            elif len(value) > 1000:  # Large collections
                edge_types.append(EdgeCaseType.COLLECTION_LARGE)

        # Check string edge cases
        elif isinstance(value, str):
            if len(value) == 0:
                edge_types.append(EdgeCaseType.STRING_EMPTY)
            elif any(c in value for c in ['\n', '\t', '\r']):
                edge_types.append(EdgeCaseType.STRING_SPECIAL_CHARS)
            elif any(ord(c) > 127 for c in value):
                edge_types.append(EdgeCaseType.STRING_UNICODE)
            elif len(value) > 1000:  # Very long strings
                edge_types.append(EdgeCaseType.STRING_LONG)

        # Check None values
        elif value is None or value == "None":
            edge_types.append(EdgeCaseType.STRING_NONE)

        # Check string representations of edge cases
        elif isinstance(value, str):
            if value in ["sys.maxsize", "float('inf')", "float('-inf')", "math.inf", "-math.inf"]:
                edge_types.append(EdgeCaseType.NUMERIC_MAX_MIN)
            elif value in ["[]", "{}", "set()"]:
                edge_types.append(EdgeCaseType.COLLECTION_EMPTY)

        return edge_types

    @staticmethod
    def calculate_edge_case_ratio(test_function: "TestFunction") -> tuple[int, int]:
        """Calculate normal vs edge case test ratio.

        Args:
            test_function: The test function to analyze

        Returns:
            Tuple of (normal_count, edge_case_count)

        """
        test_values = EdgeCaseAnalyzer._extract_test_values(test_function)

        normal_count = 0
        edge_case_count = 0

        for value in test_values:
            edge_types = EdgeCaseAnalyzer._classify_value(value)
            if edge_types:
                edge_case_count += 1
            else:
                normal_count += 1

        return normal_count, edge_case_count

    @staticmethod
    def get_missing_numeric_edge_cases(test_function: "TestFunction") -> list[EdgeCaseType]:
        """Get list of missing numeric edge cases."""
        edge_cases_found = EdgeCaseAnalyzer.analyze_test_values(test_function)

        numeric_edge_types = [
            EdgeCaseType.NUMERIC_ZERO,
            EdgeCaseType.NUMERIC_NEGATIVE,
            EdgeCaseType.NUMERIC_MAX_MIN,
        ]

        return [edge_type for edge_type in numeric_edge_types
                if not edge_cases_found[edge_type]]

    @staticmethod
    def get_missing_collection_edge_cases(test_function: "TestFunction") -> list[EdgeCaseType]:
        """Get list of missing collection edge cases."""
        edge_cases_found = EdgeCaseAnalyzer.analyze_test_values(test_function)

        collection_edge_types = [
            EdgeCaseType.COLLECTION_EMPTY,
            EdgeCaseType.COLLECTION_SINGLE,
            EdgeCaseType.COLLECTION_LARGE,
        ]

        return [edge_type for edge_type in collection_edge_types
                if not edge_cases_found[edge_type]]

    @staticmethod
    def get_missing_string_edge_cases(test_function: "TestFunction") -> list[EdgeCaseType]:
        """Get list of missing string edge cases."""
        edge_cases_found = EdgeCaseAnalyzer.analyze_test_values(test_function)

        string_edge_types = [
            EdgeCaseType.STRING_NONE,
            EdgeCaseType.STRING_EMPTY,
            EdgeCaseType.STRING_SPECIAL_CHARS,
            EdgeCaseType.STRING_UNICODE,
            EdgeCaseType.STRING_LONG,
        ]

        return [edge_type for edge_type in string_edge_types
                if not edge_cases_found[edge_type]]
