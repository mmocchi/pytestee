"""Rule-based checker that orchestrates individual rule modules."""

from typing import List, Optional

from ...domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from ..errors import CheckerError
from ..rules.base_rule import BaseRule
from .base_checker import BaseChecker


class RuleBasedChecker(BaseChecker):
    """Checker that executes a collection of individual rules."""

    def __init__(self, name: str, rules: List[BaseRule]) -> None:
        super().__init__(name)
        self.rules = rules

    def check_function(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """Check a test function against all configured rules."""
        results = []

        for rule in self.rules:
            try:
                rule_results = rule.check(test_function, test_file, config)
                results.extend(rule_results)
            except Exception as e:
                # Re-raise as CheckerError for proper error handling
                raise CheckerError(f"rule_{rule.rule_id}", e) from e

        return results
