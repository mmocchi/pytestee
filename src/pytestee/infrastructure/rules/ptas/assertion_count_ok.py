"""PTAS005: Assertion Count OK."""

from typing import List, Optional, Union

from ....domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from ....infrastructure.ast_parser import ASTParser
from ..base_rule import BaseRule


class PTAS005(BaseRule):
    """Rule for indicating appropriate assertion count."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="PTAS005",
            name="assertion_count_ok",
            description="Test function has appropriate number of assertions"
        )
        self._parser = ASTParser()

    def check(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """Check if assertion count is appropriate."""
        min_asserts = self._get_config_value(config, "min_asserts", 1)
        max_asserts = self._get_config_value(config, "max_asserts", 3)
        assert_count = self._parser.count_assert_statements(test_function)

        if min_asserts <= assert_count <= max_asserts:
            return [self._create_result(
                "info",
                f"Assertion count OK: {assert_count} assertions",
                test_file,
                test_function
            )]

        return []

    def _get_config_value(self, config: Optional[CheckerConfig], key: str, default: Union[int, float]) -> Union[int, float]:
        """Get configuration value with fallback to default."""
        if config and config.config:
            return config.config.get(key, default)
        return default
