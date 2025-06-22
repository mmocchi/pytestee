"""Dependency injection container and checker registry."""

from typing import Any, Dict, List, Optional

from pytestee.domain.interfaces import IChecker, ICheckerRegistry
from pytestee.infrastructure.checkers.assertion_checker import AssertionChecker
from pytestee.infrastructure.checkers.naming_checker import NamingChecker
from pytestee.infrastructure.checkers.pattern_checker import PatternChecker
from pytestee.infrastructure.rules.base_rule import BaseRule


class CheckerRegistry(ICheckerRegistry):
    """Registry for managing test quality checkers."""

    def __init__(self, config_manager: Optional[object] = None) -> None:
        """チェッカーレジストリを初期化します。"""
        self._checkers: Dict[str, IChecker] = {}
        self.config_manager = config_manager
        self._initialize_default_checkers()

    def _initialize_default_checkers(self) -> None:
        """デフォルトチェッカーを初期化します。"""
        self.register(PatternChecker(self.config_manager))
        self.register(AssertionChecker(self.config_manager))
        self.register(NamingChecker(self.config_manager))

        # ルール競合検証を実行
        self._validate_rule_conflicts()

    def register(self, checker: IChecker) -> None:
        """チェッカーを登録します。

        Args:
            checker: 登録するチェッカー

        """
        self._checkers[checker.name] = checker

    def get_checker(self, name: str) -> Optional[IChecker]:
        """名前でチェッカーを取得します。

        Args:
            name: チェッカー名

        Returns:
            チェッカーまたはNone

        """
        return self._checkers.get(name)

    def get_all_checkers(self) -> List[IChecker]:
        """登録されているすべてのチェッカーを取得します。

        Returns:
            チェッカーのリスト

        """
        return list(self._checkers.values())

    def get_enabled_checkers(self, config: Dict[str, Any]) -> List[IChecker]:
        """設定に基づいて有効なチェッカーを取得します。

        Args:
            config: 設定

        Returns:
            有効なチェッカーのリスト

        """
        enabled_checkers = []

        for checker in self._checkers.values():
            checker_config = config.get(checker.name, {})

            # Check if checker is enabled (default to True)
            if checker_config.get("enabled", True):
                enabled_checkers.append(checker)

        return enabled_checkers

    def unregister(self, name: str) -> bool:
        """名前でチェッカーの登録を解除します。

        Args:
            name: チェッカー名

        Returns:
            解除に成功した場合True

        """
        if name in self._checkers:
            del self._checkers[name]
            return True
        return False

    def clear(self) -> None:
        """登録されているすべてのチェッカーをクリアします。"""
        self._checkers.clear()

    def list_checker_names(self) -> List[str]:
        """登録されているチェッカー名のリストを取得します。

        Returns:
            チェッカー名のリスト

        """
        return list(self._checkers.keys())

    def get_all_rule_instances(self) -> Dict[str, BaseRule]:
        """すべてのチェッカーからルールインスタンスを収集します。

        Returns:
            ルールID -> ルールインスタンスのマッピング

        """
        rule_instances = {}

        for checker in self._checkers.values():
            # チェッカーからルールインスタンスを取得
            if hasattr(checker, 'get_rule_instances'):
                checker_rules = checker.get_rule_instances()
                rule_instances.update(checker_rules)

        return rule_instances

    def _validate_rule_conflicts(self) -> None:
        """ルール競合を検証します。"""
        if self.config_manager and hasattr(self.config_manager, 'validate_rule_selection_with_instances'):
            rule_instances = self.get_all_rule_instances()
            self.config_manager.validate_rule_selection_with_instances(rule_instances)
