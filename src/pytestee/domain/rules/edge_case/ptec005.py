"""PTEC005: Overall Edge Case Coverage Score."""

from typing import TYPE_CHECKING, Optional

from pytestee.domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from pytestee.domain.rules.base_rule import BaseRule

if TYPE_CHECKING:
    from pytestee.domain.analyzers.edge_case_analyzer import (
        EdgeCaseAnalyzer,
        EdgeCaseType,
    )


class PTEC005(BaseRule):
    """Rule for calculating overall edge case coverage score."""

    def __init__(self, edge_case_analyzer: "EdgeCaseAnalyzer") -> None:
        super().__init__(
            rule_id="PTEC005",
            name="overall_edge_case_coverage",
            description="Test function should achieve sufficient overall edge case coverage across all categories",
        )
        self._analyzer = edge_case_analyzer

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """Check overall edge case coverage score."""
        # Get all edge cases analysis
        edge_cases_found = self._analyzer.analyze_test_values(test_function)

        # Calculate coverage score
        coverage_score, coverage_details = self._calculate_coverage_score(
            test_function, edge_cases_found
        )

        # Get configuration
        min_coverage_score = 0.3  # Default 30% minimum coverage
        good_coverage_score = 0.6  # Default 60% for good coverage

        if config and config.config:
            min_coverage_score = config.config.get("min_edge_case_coverage", 0.3)
            good_coverage_score = config.config.get("good_edge_case_coverage", 0.6)

        # Format score as percentage
        score_percent = int(coverage_score * 100)

        # Determine result based on score
        if coverage_score == 0:
            return self._create_success_result(
                "No edge case analysis needed - function doesn't appear to process data that requires edge case testing",
                test_file,
                test_function,
            )
        if coverage_score < min_coverage_score:
            return self._create_failure_result(
                f"Low edge case coverage: {score_percent}% ({coverage_details}). "
                f"Consider adding more edge case scenarios to improve test robustness",
                test_file,
                test_function,
            )
        if coverage_score < good_coverage_score:
            return self._create_success_result(
                f"Adequate edge case coverage: {score_percent}% ({coverage_details}). "
                f"Consider adding more edge cases for comprehensive testing",
                test_file,
                test_function,
            )
        return self._create_success_result(
            f"Excellent edge case coverage: {score_percent}% ({coverage_details})",
            test_file,
            test_function,
        )

    def _calculate_coverage_score(
        self,
        test_function: TestFunction,
        edge_cases_found: dict["EdgeCaseType", bool]
    ) -> tuple[float, str]:
        """Calculate overall edge case coverage score."""
        from pytestee.domain.analyzers.edge_case_analyzer import EdgeCaseType

        # Determine which categories are relevant for this test function
        has_numeric = self._has_numeric_operations(test_function)
        has_collection = self._has_collection_operations(test_function)
        has_string = self._has_string_operations(test_function)

        # Skip if no relevant operations detected
        if not (has_numeric or has_collection or has_string):
            return 0.0, "no relevant operations detected"

        # Define edge case categories
        numeric_cases = [
            EdgeCaseType.NUMERIC_ZERO,
            EdgeCaseType.NUMERIC_NEGATIVE,
            EdgeCaseType.NUMERIC_MAX_MIN,
        ]
        collection_cases = [
            EdgeCaseType.COLLECTION_EMPTY,
            EdgeCaseType.COLLECTION_SINGLE,
        ]
        string_cases = [
            EdgeCaseType.STRING_NONE,
            EdgeCaseType.STRING_EMPTY,
            EdgeCaseType.STRING_SPECIAL_CHARS,
        ]

        # Calculate coverage for each relevant category
        total_weight = 0.0
        covered_weight = 0.0
        coverage_summary = []

        if has_numeric:
            numeric_covered = sum(1 for case in numeric_cases if edge_cases_found.get(case, False))
            numeric_total = len(numeric_cases)
            numeric_weight = 1.0

            total_weight += numeric_weight
            covered_weight += (numeric_covered / numeric_total) * numeric_weight
            coverage_summary.append(f"numeric: {numeric_covered}/{numeric_total}")

        if has_collection:
            collection_covered = sum(1 for case in collection_cases if edge_cases_found.get(case, False))
            collection_total = len(collection_cases)
            collection_weight = 1.0

            total_weight += collection_weight
            covered_weight += (collection_covered / collection_total) * collection_weight
            coverage_summary.append(f"collection: {collection_covered}/{collection_total}")

        if has_string:
            string_covered = sum(1 for case in string_cases if edge_cases_found.get(case, False))
            string_total = len(string_cases)
            string_weight = 1.0

            total_weight += string_weight
            covered_weight += (string_covered / string_total) * string_weight
            coverage_summary.append(f"string: {string_covered}/{string_total}")

        # Calculate final score
        if total_weight == 0:
            return 0.0, "no applicable categories"

        coverage_score = covered_weight / total_weight
        coverage_details = ", ".join(coverage_summary)

        return coverage_score, coverage_details

    def _has_numeric_operations(self, test_function: TestFunction) -> bool:
        """Check if function has numeric operations (from PTEC001)."""
        import ast

        for node in ast.walk(ast.Module(body=test_function.body, type_ignores=[])):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return True
            if isinstance(node, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow)):
                return True
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ["int", "float", "abs", "min", "max", "sum"]:
                    return True
        return False

    def _has_collection_operations(self, test_function: TestFunction) -> bool:
        """Check if function has collection operations (from PTEC002)."""
        import ast

        for node in ast.walk(ast.Module(body=test_function.body, type_ignores=[])):
            if isinstance(node, (ast.List, ast.Dict, ast.Set, ast.Tuple)):
                return True
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ["list", "dict", "set", "tuple", "len"]:
                    return True
        return False

    def _has_string_operations(self, test_function: TestFunction) -> bool:
        """Check if function has string operations (from PTEC003)."""
        import ast

        for node in ast.walk(ast.Module(body=test_function.body, type_ignores=[])):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                return True
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ["str", "format", "print"]:
                    return True
        return False

    def get_conflicting_rules(self) -> set[str]:
        """No conflicting rules for overall coverage scoring."""
        return set()
