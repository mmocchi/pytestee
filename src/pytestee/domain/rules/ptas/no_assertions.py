"""PTAS004: No Assertions Found."""

from typing import Optional, Set

from ....domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from ....infrastructure.ast_parser import ASTParser
from ..base_rule import BaseRule


class PTAS004(BaseRule):
    """Rule for detecting functions with no assertions."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="PTAS004",
            name="no_assertions",
            description="Test function contains no assertions at all",
        )
        self._parser = ASTParser()

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """Check if test function has no assertions."""
        assert_count = self._parser.count_assert_statements(test_function)

        if assert_count == 0:
            return self._create_result(
                "No assertions found - test function should verify expected behavior",
                test_file,
                test_function,
            )
        return self._create_success_result(
            f"Assertions found: {assert_count} assertions", test_file, test_function
        )

    def get_conflicting_rules(self) -> Set[str]:
        """PTAS004 conflicts with all other assertion count rules."""
        return {"PTAS001", "PTAS002", "PTAS005"}  # Conflicts with all count-based rules
