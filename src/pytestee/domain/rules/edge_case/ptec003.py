"""PTEC003: String Edge Cases Missing."""

from typing import TYPE_CHECKING, Optional

from pytestee.domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from pytestee.domain.rules.base_rule import BaseRule

if TYPE_CHECKING:
    from pytestee.domain.analyzers.edge_case_analyzer import EdgeCaseAnalyzer


class PTEC003(BaseRule):
    """Rule for detecting missing string edge cases in test functions."""

    def __init__(self, edge_case_analyzer: "EdgeCaseAnalyzer") -> None:
        super().__init__(
            rule_id="PTEC003",
            name="string_edge_cases_missing",
            description="Test function is missing critical string edge cases (None, empty, special characters, long strings)",
        )
        self._analyzer = edge_case_analyzer

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """Check if test function covers string edge cases."""
        # Get missing string edge cases
        missing_edge_cases = self._analyzer.get_missing_string_edge_cases(test_function)

        # Check if any string operations are happening
        has_string_operations = self._has_string_operations(test_function)

        # Skip check if no string operations detected
        if not has_string_operations:
            return self._create_success_result(
                "No string operations detected - string edge case check skipped",
                test_file,
                test_function,
            )

        # Get configuration
        min_edge_cases = 1  # Default minimum
        if config and config.config:
            min_edge_cases = config.config.get("min_string_edge_cases", 1)

        # Calculate severity based on missing edge cases
        if len(missing_edge_cases) == 0:
            return self._create_success_result(
                "All critical string edge cases are covered",
                test_file,
                test_function,
            )
        if len(missing_edge_cases) >= min_edge_cases:
            missing_types = [edge_case.value for edge_case in missing_edge_cases]
            return self._create_failure_result(
                f"Missing critical string edge cases: {', '.join(missing_types)}. "
                f"Consider testing: None values, empty strings, special characters (\\n, \\t), Unicode characters, very long strings",
                test_file,
                test_function,
            )
        return self._create_success_result(
            f"Sufficient string edge case coverage (missing only: {len(missing_edge_cases)} cases)",
            test_file,
            test_function,
        )

    def _has_string_operations(self, test_function: TestFunction) -> bool:
        """Check if the test function involves string operations."""
        import ast

        # Look for string literals, operations, or function calls
        for node in ast.walk(ast.Module(body=test_function.body, type_ignores=[])):
            # Check for string literals
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                return True

            # Legacy string literals (older Python versions)
            if isinstance(node, ast.Str):
                return True

            # Check for string operations
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    string_functions = [
                        "str", "len", "ord", "chr", "format", "print",
                        "input", "open"  # file operations often involve strings
                    ]
                    if node.func.id in string_functions:
                        return True
                elif isinstance(node.func, ast.Attribute):
                    string_methods = [
                        "strip", "split", "join", "replace", "find", "index",
                        "upper", "lower", "title", "capitalize", "startswith",
                        "endswith", "isdigit", "isalpha", "isalnum", "encode",
                        "decode", "format", "ljust", "rjust", "center"
                    ]
                    if node.func.attr in string_methods:
                        return True

            # Check for string formatting
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
                return True

            # Check for f-strings (formatted string literals)
            if isinstance(node, ast.JoinedStr):
                return True

            # Check for string comparisons
            if isinstance(node, ast.Compare):
                # Look for string equality/inequality operations
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                        return True

            # Check for variable names that suggest string operations
            if isinstance(node, ast.Name):
                string_indicators = [
                    "text", "message", "content", "string", "str", "name",
                    "title", "description", "path", "url", "email", "word",
                    "sentence", "paragraph", "document", "filename", "data"
                ]
                if any(indicator in node.id.lower() for indicator in string_indicators):
                    return True

        return False

    def get_conflicting_rules(self) -> set[str]:
        """No conflicting rules for string edge case detection."""
        return set()
