"""PTST002: AAA/GWT Pattern Not Clearly Detected."""

from typing import List, Optional

from ....domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from ..base_rule import BaseRule


class PTST002(BaseRule):
    """Rule for warning when no clear pattern structure is found."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="PTST002",
            name="pattern_not_detected",
            description="No clear pattern structure found, consider improving test organization"
        )

    def check(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """Check if no clear pattern is detected (this is typically called as fallback)."""
        # This rule is typically used as a fallback when no other pattern is detected
        # The logic for when to apply this rule is handled by the checker orchestration
        return [self._create_result(
            "warning",
            "AAA/GWT pattern not clearly detected. Consider using comments or structural separation.",
            test_file,
            test_function
        )]
