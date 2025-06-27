"""PTNM003: Test class method count checker."""

from typing import TYPE_CHECKING, Optional

from pytestee.domain.models import (
    CheckerConfig,
    CheckResult,
    CheckSeverity,
    TestClass,
    TestFile,
)
from pytestee.domain.rules.base_rule import BaseRule

if TYPE_CHECKING:
    from pytestee.domain.models import TestFunction


class PTNM003(BaseRule):
    """Rule for checking the number of test methods in test classes.

    Checks if test classes have an appropriate number of test methods.
    Too many methods might indicate a class that's testing too much
    and should be split into multiple smaller test classes.
    """

    def __init__(self) -> None:
        super().__init__(
            rule_id="PTNM003",
            name="test_class_method_count",
            description="Check the number of test methods in test classes",
        )

    def check_class(
        self,
        test_class: TestClass,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """Check if test class has appropriate number of test methods.

        Args:
            test_class: The test class to check
            test_file: The test file information
            config: Checker configuration (optional)

        Returns:
            Check result

        """
        max_methods = self._get_config_value(config, "max_methods", 10)

        method_count = len(test_class.test_methods) if test_class.test_methods else 0

        if method_count > max_methods:
            return self._create_failure_result(
                f"Test class '{test_class.name}' has too many test methods: {method_count} "
                f"(maximum recommended: {max_methods}). Consider splitting into multiple classes.",
                test_file,
                None,
                severity=CheckSeverity.WARNING,
                line_number=test_class.lineno,
                column=test_class.col_offset,
            )
        return self._create_success_result(
            f"Test class '{test_class.name}' has appropriate number of test methods: {method_count}",
            test_file,
            None,
            line_number=test_class.lineno,
            column=test_class.col_offset,
        )

    def check(
        self,
        test_function: "TestFunction",
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """BaseRule interface compatibility method.

        PTNM003 is a class-level rule, so this method returns a neutral result.
        Use check_class method instead.
        """
        return self._create_success_result(
            "PTNM003 is a class-level rule",
            test_file,
            test_function
        )

    def _get_config_value(
        self, config: Optional[CheckerConfig], key: str, default: int
    ) -> int:
        """Get configuration value with fallback to default."""
        if config and config.config:
            return config.config.get(key, default)
        return default
