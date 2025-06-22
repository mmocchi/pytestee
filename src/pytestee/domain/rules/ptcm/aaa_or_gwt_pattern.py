"""PTCM003: AAA or GWT Pattern Detected in Comments (Composite Rule)."""

from typing import Optional, Set

from ....domain.models import (
    CheckerConfig,
    CheckResult,
    CheckSeverity,
    TestFile,
    TestFunction,
)
from ..base_rule import BaseRule
from .aaa_comment_pattern import PTCM001
from .gwt_comment_pattern import PTCM002


class PTCM003(BaseRule):
    """Composite rule for detecting either AAA or GWT pattern in comments."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="PTCM003",
            name="aaa_or_gwt_pattern_comments",
            description="AAA or GWT pattern detected through comment analysis (either pattern is acceptable)",
        )
        # Create instances of the component rules
        self._aaa_rule = PTCM001()
        self._gwt_rule = PTCM002()

    def set_config_manager(self, config_manager: Optional[object]) -> None:
        """Set config manager for this rule and component rules."""
        super().set_config_manager(config_manager)
        self._aaa_rule.set_config_manager(config_manager)
        self._gwt_rule.set_config_manager(config_manager)

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """Check for either AAA or GWT pattern in comments."""
        # Check AAA pattern
        aaa_result = self._aaa_rule.check(test_function, test_file, config)
        aaa_found = self._is_success_result(aaa_result)

        # Check GWT pattern
        gwt_result = self._gwt_rule.check(test_function, test_file, config)
        gwt_found = self._is_success_result(gwt_result)

        if aaa_found or gwt_found:
            # Either pattern found - return success (INFO)
            pattern_type = "AAA" if aaa_found else "GWT"
            if aaa_found and gwt_found:
                pattern_type = "AAA and GWT"

            return self._create_success_result(
                f"{pattern_type} pattern detected in comments", test_file, test_function
            )
        # Neither pattern found - return failure (ERROR/WARNING based on config)
        return self._create_failure_result(
            "Neither AAA nor GWT pattern detected in comments. Consider adding pattern comments (# Arrange, # Act, # Assert or # Given, # When, # Then).",
            test_file,
            test_function,
        )

    def _is_success_result(self, result: CheckResult) -> bool:
        """Check if a result indicates success (pattern found)."""
        # Success results have INFO severity and contain "detected" in the message
        return (
            result.severity == CheckSeverity.INFO
            and "detected" in result.message.lower()
        )

    def get_conflicting_rules(self) -> Set[str]:
        """PTCM003はPTCM001とPTCM002と競合する。"""
        return {"PTCM001", "PTCM002"}
