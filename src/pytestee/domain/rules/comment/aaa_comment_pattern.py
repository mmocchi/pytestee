"""PTCM001: AAA Pattern Detected in Comments."""
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


class PTCM001(BaseRule):
    """Rule for detecting AAA pattern in comments."""

    def __init__(self, pattern_analyzer: PatternAnalyzer) -> None:
        super().__init__(
            rule_id="PTCM001",
            name="aaa_pattern_comments",
            description="AAA (Arrange, Act, Assert) pattern detected through comment analysis",
        )
        self._analyzer = pattern_analyzer

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: CheckerConfig | None = None,
    ) -> CheckResult:
        """Check for AAA pattern in comments."""
        has_aaa = self._analyzer.find_aaa_comments(test_function, test_file.content)

        if has_aaa:
            # Pattern found - return success (INFO)
            return self._create_success_result(
                "AAA pattern detected in comments", test_file, test_function
            )
        # Pattern not found - return failure (ERROR/WARNING based on config)
        return self._create_failure_result(
            "AAA pattern not detected in comments. Consider adding # Arrange, # Act, # Assert comments.",
            test_file,
            test_function,
        )

    def get_conflicting_rules(self) -> set[str]:
        """PTCM001はPTCM003と競合する。"""
        return {"PTCM003"}
