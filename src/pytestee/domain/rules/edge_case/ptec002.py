"""PTEC002: Collection Edge Cases Missing."""

from typing import TYPE_CHECKING, Optional

from pytestee.domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from pytestee.domain.rules.base_rule import BaseRule

if TYPE_CHECKING:
    from pytestee.domain.analyzers.edge_case_analyzer import EdgeCaseAnalyzer


class PTEC002(BaseRule):
    """Rule for detecting missing collection edge cases in test functions."""

    def __init__(self, edge_case_analyzer: "EdgeCaseAnalyzer") -> None:
        super().__init__(
            rule_id="PTEC002",
            name="collection_edge_cases_missing",
            description="Test function is missing critical collection edge cases (empty, single element, large collections)",
        )
        self._analyzer = edge_case_analyzer

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """Check if test function covers collection edge cases."""
        # Get missing collection edge cases
        missing_edge_cases = self._analyzer.get_missing_collection_edge_cases(test_function)

        # Check if any collection operations are happening
        has_collection_operations = self._has_collection_operations(test_function)

        # Skip check if no collection operations detected
        if not has_collection_operations:
            return self._create_success_result(
                "No collection operations detected - collection edge case check skipped",
                test_file,
                test_function,
            )

        # Get configuration
        min_edge_cases = 1  # Default minimum
        if config and config.config:
            min_edge_cases = config.config.get("min_collection_edge_cases", 1)

        # Calculate severity based on missing edge cases
        if len(missing_edge_cases) == 0:
            return self._create_success_result(
                "All critical collection edge cases are covered",
                test_file,
                test_function,
            )
        if len(missing_edge_cases) >= min_edge_cases:
            missing_types = [edge_case.value for edge_case in missing_edge_cases]
            return self._create_failure_result(
                f"Missing critical collection edge cases: {', '.join(missing_types)}. "
                f"Consider testing: empty collections, single-element collections, large collections",
                test_file,
                test_function,
            )
        return self._create_success_result(
            f"Sufficient collection edge case coverage (missing only: {len(missing_edge_cases)} cases)",
            test_file,
            test_function,
        )

    def _has_collection_operations(self, test_function: TestFunction) -> bool:
        """Check if the test function involves collection operations."""
        import ast

        # Look for collection literals, operations, or function calls
        for node in ast.walk(ast.Module(body=test_function.body, type_ignores=[])):
            # Check for collection literals
            if isinstance(node, (ast.List, ast.Dict, ast.Set, ast.Tuple)):
                return True

            # Check for collection operations
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    collection_functions = [
                        "list", "dict", "set", "tuple", "len", "range",
                        "sorted", "reversed", "filter", "map", "zip"
                    ]
                    if node.func.id in collection_functions:
                        return True
                elif isinstance(node.func, ast.Attribute):
                    collection_methods = [
                        "append", "extend", "insert", "remove", "pop", "clear",
                        "keys", "values", "items", "get", "update",
                        "add", "discard", "union", "intersection"
                    ]
                    if node.func.attr in collection_methods:
                        return True

            # Check for collection subscripting
            if isinstance(node, ast.Subscript):
                return True

            # Check for iteration
            if isinstance(node, (ast.For, ast.ListComp, ast.DictComp, ast.SetComp)):
                return True

            # Check for collection membership testing
            if isinstance(node, ast.Compare):
                for op in node.ops:
                    if isinstance(op, (ast.In, ast.NotIn)):
                        return True

            # Check for variable names that suggest collection operations
            if isinstance(node, ast.Name):
                collection_indicators = [
                    "list", "array", "items", "elements", "data", "collection",
                    "queue", "stack", "dict", "map", "set", "tuple", "records"
                ]
                if any(indicator in node.id.lower() for indicator in collection_indicators):
                    return True

        return False

    def get_conflicting_rules(self) -> set[str]:
        """No conflicting rules for collection edge case detection."""
        return set()
