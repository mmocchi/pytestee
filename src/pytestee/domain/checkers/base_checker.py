"""Base checker implementation."""

from abc import abstractmethod
from typing import List, Optional

from ...domain.interfaces import IChecker
from ...domain.models import (
    CheckerConfig,
    CheckResult,
    CheckSeverity,
    TestFile,
    TestFunction,
)


class BaseChecker(IChecker):
    """Base implementation for all checkers."""

    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        """Get the name of this checker."""
        return self._name

    def check(self, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """Check a test file and return results."""
        results = []

        for test_function in test_file.test_functions:
            function_results = self.check_function(test_function, test_file, config)
            results.extend(function_results)

        return results

    @abstractmethod
    def check_function(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """Check a specific test function and return results."""
        pass

    def _create_result(
        self,
        rule_id: str,
        severity: str,
        message: str,
        test_file: TestFile,
        test_function: Optional[TestFunction] = None,
        line_number: Optional[int] = None,
        column: Optional[int] = None
    ) -> CheckResult:
        """Create a CheckResult."""
        return CheckResult(
            checker_name=self.name,
            rule_id=rule_id,
            severity=CheckSeverity(severity),
            message=message,
            file_path=test_file.path,
            line_number=line_number or (test_function.lineno if test_function else None),
            column=column or (test_function.col_offset if test_function else None),
            function_name=test_function.name if test_function else None
        )
