"""ルール実装の基底クラス。"""

from abc import ABC, abstractmethod
from typing import Optional

from pytestee.domain.models import (
    CheckerConfig,
    CheckFailure,
    CheckResult,
    CheckSeverity,
    CheckSuccess,
    TestFile,
    TestFunction,
)


class BaseRule(ABC):
    """個別のルール実装の基底クラス。"""

    def __init__(self, rule_id: str, name: str, description: str) -> None:
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.config_manager: Optional[object] = None

    @abstractmethod
    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """このルールに対してテスト関数をチェック。"""
        pass

    def is_enabled(self, config_manager: Optional[object]) -> bool:
        """Check if this rule is enabled in configuration."""
        if config_manager is not None and hasattr(config_manager, "is_rule_enabled"):
            return config_manager.is_rule_enabled(self.rule_id)
        return True

    def is_enabled_for_file(self, test_file: TestFile, config_manager: Optional[object]) -> bool:
        """Check if this rule is enabled for a specific file."""
        if config_manager is not None and hasattr(config_manager, "is_rule_enabled_for_file"):
            return config_manager.is_rule_enabled_for_file(self.rule_id, test_file.path)
        return self.is_enabled(config_manager)


    def _create_failure_result(
        self,
        message: str,
        test_file: TestFile,
        test_function: Optional[TestFunction] = None,
        line_number: Optional[int] = None,
        column: Optional[int] = None,
        severity: Optional[CheckSeverity] = None,
    ) -> CheckFailure:
        """ルール違反時のCheckFailureを作成。"""
        # デフォルト重要度は設定から取得、なければERROR
        if severity is None:
            severity = self._get_severity_from_config()

        return CheckFailure(
            checker_name=self.name,
            rule_id=self.rule_id,
            severity=severity,
            message=message,
            file_path=test_file.path,
            line_number=line_number
            or (test_function.lineno if test_function else None),
            column=column,
            function_name=test_function.name if test_function else None,
        )

    def _get_severity_from_config(self) -> CheckSeverity:
        """設定から重要度を取得、デフォルトはERROR。"""
        if self.config_manager is not None and hasattr(
            self.config_manager, "get_rule_severity"
        ):
            severity_str = self.config_manager.get_rule_severity(self.rule_id)
            severity_map = {
                "info": CheckSeverity.INFO,
                "warning": CheckSeverity.WARNING,
                "error": CheckSeverity.ERROR,
            }
            return severity_map.get(severity_str.lower(), CheckSeverity.ERROR)

        return CheckSeverity.ERROR

    def set_config_manager(self, config_manager: Optional[object]) -> None:
        """設定管理を設定する。"""
        self.config_manager = config_manager

    def get_conflicting_rules(self) -> set[str]:
        """このルールと競合するルールIDのセットを返す。

        サブクラスでオーバーライドして競合ルールを定義。
        デフォルトでは競合ルールなし。
        """
        return set()

    def _create_success_result(
        self,
        message: str,
        test_file: TestFile,
        test_function: Optional[TestFunction] = None,
        line_number: Optional[int] = None,
        column: Optional[int] = None,
    ) -> CheckSuccess:
        """ルール適合時のCheckSuccessを作成。"""
        return CheckSuccess(
            checker_name=self.name,
            rule_id=self.rule_id,
            message=message,
            file_path=test_file.path,
            line_number=line_number
            or (test_function.lineno if test_function else None),
            column=column,
            function_name=test_function.name if test_function else None,
        )
