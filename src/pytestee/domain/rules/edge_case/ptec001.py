"""PTEC001: Numeric Edge Cases Missing."""

from typing import TYPE_CHECKING, Optional

from pytestee.domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from pytestee.domain.rules.base_rule import BaseRule

if TYPE_CHECKING:
    from pytestee.domain.analyzers.edge_case_analyzer import EdgeCaseAnalyzer


class PTEC001(BaseRule):
    """Rule for detecting missing numeric edge cases in test functions."""

    def __init__(self, edge_case_analyzer: "EdgeCaseAnalyzer") -> None:
        super().__init__(
            rule_id="PTEC001",
            name="numeric_edge_cases_missing",
            description="Test function is missing critical numeric edge cases (zero, negative, max/min values)",
        )
        self._analyzer = edge_case_analyzer

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """Check if test function covers numeric edge cases."""
        # Get missing numeric edge cases
        missing_edge_cases = self._analyzer.get_missing_numeric_edge_cases(test_function)

        # Check if any numeric processing is happening
        has_numeric_operations = self._has_numeric_operations(test_function)

        # Skip check if no numeric operations detected
        if not has_numeric_operations:
            return self._create_success_result(
                "No numeric operations detected - numeric edge case check skipped",
                test_file,
                test_function,
            )

        # Get configuration
        min_edge_cases = 1  # Default minimum
        if config and config.config:
            min_edge_cases = config.config.get("min_numeric_edge_cases", 1)

        # Calculate severity based on missing edge cases
        if len(missing_edge_cases) == 0:
            return self._create_success_result(
                "All critical numeric edge cases are covered",
                test_file,
                test_function,
            )
        if len(missing_edge_cases) >= min_edge_cases:
            missing_types = [edge_case.value for edge_case in missing_edge_cases]
            return self._create_failure_result(
                f"Missing critical numeric edge cases: {', '.join(missing_types)}. "
                f"Consider testing: zero values, negative numbers, max/min values",
                test_file,
                test_function,
            )
        return self._create_success_result(
            f"Sufficient numeric edge case coverage (missing only: {len(missing_edge_cases)} cases)",
            test_file,
            test_function,
        )

    def _has_numeric_operations(self, test_function: TestFunction) -> bool:
        """Check if the test function involves numeric operations."""
        import ast

        # Look for numeric literals, arithmetic operations, or numeric function calls
        for node in ast.walk(ast.Module(body=test_function.body, type_ignores=[])):
            # Check for numeric constants
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return True

            # Check for arithmetic operations
            if isinstance(node, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow)):
                return True

            # Check for comparison operations with numbers
            if isinstance(node, ast.Compare):
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant) and isinstance(comparator.value, (int, float)):
                        return True

            # Check for numeric function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ["int", "float", "abs", "min", "max", "sum", "len"]:
                        return True
                elif isinstance(node.func, ast.Attribute):
                    # Check for math module functions
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "math":
                        return True

            # Check for variable names that suggest numeric operations
            if isinstance(node, ast.Name):
                numeric_indicators = [
                    "count", "size", "length", "total", "sum", "average", "min", "max",
                    "value", "number", "amount", "quantity", "index", "id"
                ]
                if any(indicator in node.id.lower() for indicator in numeric_indicators):
                    return True

        return False

    def get_conflicting_rules(self) -> set[str]:
        """No conflicting rules for numeric edge case detection."""
        return set()
