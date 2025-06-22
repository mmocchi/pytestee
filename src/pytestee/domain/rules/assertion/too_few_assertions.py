"""PTAS001: Too Few Assertions."""

from typing import TYPE_CHECKING, Optional, Set, Union

from pytestee.domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from pytestee.domain.rules.base_rule import BaseRule

if TYPE_CHECKING:
    from pytestee.domain.analyzers.assertion_analyzer import AssertionAnalyzer


class PTAS001(BaseRule):
    """Rule for detecting too few assertions."""

    def __init__(self, assertion_analyzer: Optional["AssertionAnalyzer"] = None) -> None:
        super().__init__(
            rule_id="PTAS001",
            name="too_few_assertions",
            description="Test function has fewer assertions than minimum recommended",
        )
        if assertion_analyzer is None:
            from pytestee.domain.analyzers.assertion_analyzer import AssertionAnalyzer
            assertion_analyzer = AssertionAnalyzer()
        self._analyzer = assertion_analyzer

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """Check if test function has too few assertions."""
        min_asserts = self._get_config_value(config, "min_asserts", 1)
        assert_count = self._analyzer.count_assertions(test_function)

        if assert_count < min_asserts:
            return self._create_failure_result(
                f"Too few assertions: {assert_count} (minimum recommended: {min_asserts})",
                test_file,
                test_function,
            )
        return self._create_success_result(
            f"Assertion count OK: {assert_count} assertions (minimum: {min_asserts})",
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

    def get_conflicting_rules(self) -> Set[str]:
        """PTAS001 conflicts with other assertion count rules."""
        return {
            "PTAS004",
            "PTAS005",
        }  # Conflicts with no assertions and assertion count OK
