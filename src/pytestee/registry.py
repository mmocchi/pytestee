"""Dependency injection container and checker registry."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pytestee.domain.interfaces import IChecker, ICheckerRegistry

if TYPE_CHECKING:
    from pytestee.domain.rules.base_rule import BaseRule


class CheckerRegistry(ICheckerRegistry):
    """Registry for managing test quality checkers."""

    def __init__(self, config_manager: Optional[object] = None) -> None:
        """チェッカーレジストリを初期化します。"""
        self._checkers: Dict[str, IChecker] = {}
        self.config_manager = config_manager
        self._initialize_default_checkers()

    def _initialize_default_checkers(self) -> None:
        """デフォルトチェッカーを初期化します。"""
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

    def get_all_rule_instances(self) -> Dict[str, "BaseRule"]:
        """設定で選択されたルールのインスタンスを作成して返します。

        Returns:
            ルールID -> ルールインスタンスのマッピング

        """
        # Import rules here to avoid circular imports
        from pytestee.domain.rules.assertion.assertion_count_ok import (
            PTAS005,
        )
        from pytestee.domain.rules.assertion.high_assertion_density import (
            PTAS003,
        )
        from pytestee.domain.rules.assertion.no_assertions import (
            PTAS004,
        )
        from pytestee.domain.rules.assertion.too_few_assertions import (
            PTAS001,
        )
        from pytestee.domain.rules.assertion.too_many_assertions import (
            PTAS002,
        )
        from pytestee.domain.rules.comment.aaa_comment_pattern import (
            PTCM001,
        )
        from pytestee.domain.rules.comment.aaa_or_gwt_pattern import (
            PTCM003,
        )
        from pytestee.domain.rules.comment.gwt_comment_pattern import (
            PTCM002,
        )
        from pytestee.domain.rules.logic.logical_flow_pattern import (
            PTLG001,
        )
        from pytestee.domain.rules.naming.japanese_characters import (
            PTNM001,
        )
        from pytestee.domain.rules.structure.structural_pattern import (
            PTST001,
        )

        # Create all available rule instances
        rule_classes = {
            "PTCM001": PTCM001,
            "PTCM002": PTCM002,
            "PTCM003": PTCM003,
            "PTST001": PTST001,
            "PTLG001": PTLG001,
            "PTAS001": PTAS001,
            "PTAS002": PTAS002,
            "PTAS003": PTAS003,
            "PTAS004": PTAS004,
            "PTAS005": PTAS005,
            "PTNM001": PTNM001,
        }

        rule_instances = {}
        for rule_id, rule_class in rule_classes.items():
            instance = rule_class()
            instance.set_config_manager(self.config_manager)
            rule_instances[rule_id] = instance

        return rule_instances

    def _validate_rule_conflicts(self) -> None:
        """ルール競合を検証します。"""
        if self.config_manager and hasattr(
            self.config_manager, "validate_rule_selection_with_instances"
        ):
            all_rule_instances = self.get_all_rule_instances()
            # Only validate conflicts for enabled rules
            enabled_rule_ids = {
                rule_id
                for rule_id in all_rule_instances
                if hasattr(self.config_manager, "is_rule_enabled")
                and self.config_manager.is_rule_enabled(rule_id)
            }
            enabled_rule_instances = {
                rule_id: all_rule_instances[rule_id] for rule_id in enabled_rule_ids
            }
            self.config_manager.validate_rule_selection_with_instances(
                enabled_rule_instances
            )
