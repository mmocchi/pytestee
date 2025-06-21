"""ルール実装の基底クラス。"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ...domain.models import (
    CheckerConfig,
    CheckResult,
    CheckSeverity,
    TestFile,
    TestFunction,
)


class BaseRule(ABC):
    """個別のルール実装の基底クラス。"""

    def __init__(self, rule_id: str, name: str, description: str) -> None:
        self.rule_id = rule_id
        self.name = name
        self.description = description

    @abstractmethod
    def check(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """このルールに対してテスト関数をチェック。"""
        pass

    def _create_result(
        self,
        severity: str,
        message: str,
        test_file: TestFile,
        test_function: Optional[TestFunction] = None,
        line_number: Optional[int] = None,
        column: Optional[int] = None
    ) -> CheckResult:
        """このルールのIDでCheckResultを作成。"""
        severity_map = {
            "info": CheckSeverity.INFO,
            "warning": CheckSeverity.WARNING,
            "error": CheckSeverity.ERROR
        }

        return CheckResult(
            checker_name=self.name,
            rule_id=self.rule_id,
            severity=severity_map[severity],
            message=message,
            file_path=test_file.path,
            line_number=line_number or (test_function.lineno if test_function else None),
            column=column,
            function_name=test_function.name if test_function else None
        )
