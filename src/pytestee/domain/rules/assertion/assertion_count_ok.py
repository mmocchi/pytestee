"""PTAS005: Assertion Count OK."""

from typing import TYPE_CHECKING, Optional, Union

from pytestee.domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from pytestee.domain.rules.base_rule import BaseRule

if TYPE_CHECKING:
    from pytestee.domain.analyzers.assertion_analyzer import AssertionAnalyzer


class PTAS005(BaseRule):
    """Rule for indicating appropriate assertion count."""

    def __init__(self, assertion_analyzer: "AssertionAnalyzer") -> None:
        super().__init__(
            rule_id="PTAS005",
            name="assertion_count_ok",
            description="Test function has appropriate number of assertions",
        )
        self._analyzer = assertion_analyzer

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """Check if assertion count is appropriate."""
        min_asserts = self._get_config_value(config, "min_asserts", 1)
        max_asserts = self._get_config_value(config, "max_asserts", 3)
        assert_count = self._analyzer.count_assertions(test_function)

        if min_asserts <= assert_count <= max_asserts:
            return self._create_success_result(
                f"Assertion count OK: {assert_count} assertions",
                test_file,
                test_function,
            )
        # Always return a result - indicate why assertion count is not OK
        if assert_count < min_asserts:
            return self._create_failure_result(
                f"Too few assertions: {assert_count} assertions (minimum: {min_asserts})",
                test_file,
                test_function,
            )
        # assert_count > max_asserts
        return self._create_failure_result(
            f"Too many assertions: {assert_count} assertions (maximum: {max_asserts})",
            test_file,
            test_function,
        )

    def _get_config_value(
        self, config: Optional[CheckerConfig], key: str, default: Union[int, float]
    ) -> Union[int, float]:
        """Get configuration value with fallback to default."""
        if config and config.config:
            return config.config.get(key, default)
        return default

    def get_conflicting_rules(self) -> set[str]:
        """PTAS005 conflicts with other assertion count rules."""
        return {"PTAS001", "PTAS004"}  # Conflicts with too few and no assertions
