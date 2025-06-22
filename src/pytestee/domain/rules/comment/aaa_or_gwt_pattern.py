"""PTCM003: AAA or GWT Pattern Detected in Comments (Composite Rule)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pytestee.domain.rules.base_rule import BaseRule

if TYPE_CHECKING:
    from pytestee.domain.analyzers.pattern_analyzer import PatternAnalyzer
    from pytestee.domain.models import (
        CheckerConfig,
        CheckResult,
        TestFile,
        TestFunction,
    )


class PTCM003(BaseRule):
    """Composite rule for detecting either AAA or GWT pattern in comments."""

    def __init__(self, pattern_analyzer: PatternAnalyzer) -> None:
        super().__init__(
            rule_id="PTCM003",
            name="aaa_or_gwt_pattern_comments",
            description="AAA or GWT pattern detected through comment analysis (either pattern is acceptable)",
        )
        self._analyzer = pattern_analyzer

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: CheckerConfig | None = None,
    ) -> CheckResult:
        """Check for either AAA or GWT pattern in comments."""
        has_pattern, pattern_type = self._analyzer.find_aaa_or_gwt_comments(
            test_function, test_file.content
        )

        if has_pattern and pattern_type:
            # Pattern found - return success (INFO)
            return self._create_success_result(
                f"{pattern_type} pattern detected in comments", test_file, test_function
            )
        # Neither pattern found - return failure (ERROR/WARNING based on config)
        return self._create_failure_result(
            "Neither AAA nor GWT pattern detected in comments. Consider adding pattern comments (# Arrange, # Act, # Assert or # Given, # When, # Then).",
            test_file,
            test_function,
        )

    def get_conflicting_rules(self) -> set[str]:
        """PTCM003はPTCM001とPTCM002と競合する。"""
        return {"PTCM001", "PTCM002"}
