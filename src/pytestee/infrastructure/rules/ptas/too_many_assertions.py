"""PTAS002: Too Many Assertions."""

from typing import List, Optional, Union

from ....domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from ....infrastructure.ast_parser import ASTParser
from ..base_rule import BaseRule


class PTAS002(BaseRule):
    """Rule for detecting too many assertions."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="PTAS002",
            name="too_many_assertions",
            description="Test function has more assertions than maximum recommended"
        )
        self._parser = ASTParser()

    def check(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """Check if test function has too many assertions."""
        max_asserts = self._get_config_value(config, "max_asserts", 3)
        assert_count = self._parser.count_assert_statements(test_function)

        if assert_count > max_asserts:
            return [self._create_result(
                "warning",
                f"Too many assertions: {assert_count} (maximum recommended: {max_asserts})",
                test_file,
                test_function
            )]

        return []

    def _get_config_value(self, config: Optional[CheckerConfig], key: str, default: Union[int, float]) -> Union[int, float]:
        """Get configuration value with fallback to default."""
        if config and config.config:
            return config.config.get(key, default)
        return default
