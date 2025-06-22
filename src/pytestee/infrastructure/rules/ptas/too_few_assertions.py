"""PTAS001: Too Few Assertions."""

from typing import List, Optional, Set, Union

from ....domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from ....infrastructure.ast_parser import ASTParser
from ..base_rule import BaseRule


class PTAS001(BaseRule):
    """Rule for detecting too few assertions."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="PTAS001",
            name="too_few_assertions",
            description="Test function has fewer assertions than minimum recommended"
        )
        self._parser = ASTParser()

    def check(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """Check if test function has too few assertions."""
        min_asserts = self._get_config_value(config, "min_asserts", 1)
        assert_count = self._parser.count_assert_statements(test_function)

        if assert_count < min_asserts:
            return [self._create_result(
                f"Too few assertions: {assert_count} (minimum recommended: {min_asserts})",
                test_file,
                test_function
            )]

        return []

    def _get_config_value(self, config: Optional[CheckerConfig], key: str, default: Union[int, float]) -> Union[int, float]:
        """Get configuration value with fallback to default."""
        if config and config.config:
            return config.config.get(key, default)
        return default

    def get_conflicting_rules(self) -> Set[str]:
        """PTAS001 conflicts with other assertion count rules."""
        return {"PTAS004", "PTAS005"}  # Conflicts with no assertions and assertion count OK
