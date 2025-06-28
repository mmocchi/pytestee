"""PTEC004: Normal/Abnormal Test Ratio Analysis."""

from typing import TYPE_CHECKING, Optional

from pytestee.domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from pytestee.domain.rules.base_rule import BaseRule

if TYPE_CHECKING:
    from pytestee.domain.analyzers.edge_case_analyzer import EdgeCaseAnalyzer


class PTEC004(BaseRule):
    """Rule for analyzing normal vs abnormal test case ratio."""

    def __init__(self, edge_case_analyzer: "EdgeCaseAnalyzer") -> None:
        super().__init__(
            rule_id="PTEC004",
            name="normal_abnormal_test_ratio",
            description="Test function should maintain proper balance between normal and edge case scenarios (recommended 7:3 ratio)",
        )
        self._analyzer = edge_case_analyzer

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """Check if test function has appropriate normal vs edge case ratio."""
        # Get normal vs edge case count
        normal_count, edge_case_count = self._analyzer.calculate_edge_case_ratio(test_function)

        # Skip if no test values detected
        total_values = normal_count + edge_case_count
        if total_values == 0:
            return self._create_success_result(
                "No test values detected - ratio analysis skipped",
                test_file,
                test_function,
            )

        # Get configuration
        target_normal_ratio = 0.7  # Default 70% normal, 30% edge cases
        min_edge_case_ratio = 0.2  # Minimum 20% edge cases
        max_edge_case_ratio = 0.5  # Maximum 50% edge cases

        if config and config.config:
            target_normal_ratio = config.config.get("target_normal_ratio", 0.7)
            min_edge_case_ratio = config.config.get("min_edge_case_ratio", 0.2)
            max_edge_case_ratio = config.config.get("max_edge_case_ratio", 0.5)

        # Calculate actual ratios
        edge_case_ratio = edge_case_count / total_values
        normal_ratio = normal_count / total_values

        # Format percentages for display
        edge_case_percent = int(edge_case_ratio * 100)
        normal_percent = int(normal_ratio * 100)

        # Analyze ratio
        if edge_case_count == 0:
            return self._create_failure_result(
                f"No edge cases detected in test data (ratio: {normal_percent}% normal, {edge_case_percent}% edge cases). "
                f"Consider adding edge case scenarios",
                test_file,
                test_function,
            )
        if edge_case_ratio < min_edge_case_ratio:
            return self._create_failure_result(
                f"Too few edge cases (ratio: {normal_percent}% normal, {edge_case_percent}% edge cases). "
                f"Recommended ratio is {int(target_normal_ratio * 100)}%:{int((1 - target_normal_ratio) * 100)}% (normal:edge)",
                test_file,
                test_function,
            )
        if edge_case_ratio > max_edge_case_ratio:
            return self._create_failure_result(
                f"Too many edge cases, might need more normal scenarios (ratio: {normal_percent}% normal, {edge_case_percent}% edge cases). "
                f"Recommended ratio is {int(target_normal_ratio * 100)}%:{int((1 - target_normal_ratio) * 100)}% (normal:edge)",
                test_file,
                test_function,
            )
        # Good ratio
        return self._create_success_result(
            f"Good balance of normal and edge cases (ratio: {normal_percent}% normal, {edge_case_percent}% edge cases)",
            test_file,
            test_function,
        )

    def get_conflicting_rules(self) -> set[str]:
        """No conflicting rules for ratio analysis."""
        return set()
