"""Dependency injection container and checker registry."""

from typing import TYPE_CHECKING, Any, Optional

from pytestee.domain.interfaces import IChecker, ICheckerRegistry

if TYPE_CHECKING:
    from pytestee.domain.rules.base_rule import BaseRule


class CheckerRegistry(ICheckerRegistry):
    """Registry for managing test quality checkers."""

    def __init__(self, config_manager: Optional[object] = None) -> None:
        """チェッカーレジストリを初期化します。"""
        self._checkers: dict[str, IChecker] = {}
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

    def get_all_checkers(self) -> list[IChecker]:
        """登録されているすべてのチェッカーを取得します。

        Returns:
            チェッカーのリスト

        """
        return list(self._checkers.values())

    def get_enabled_checkers(self, config: dict[str, Any]) -> list[IChecker]:
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

    def list_checker_names(self) -> list[str]:
        """登録されているチェッカー名のリストを取得します。

        Returns:
            チェッカー名のリスト

        """
        return list(self._checkers.keys())

    def get_all_rule_instances(self) -> dict[str, "BaseRule"]:
        """設定で有効化されたルールのインスタンスのみを作成して返します。

        Returns:
            ルールID -> ルールインスタンスのマッピング

        """
        rule_instances = {}

        # Get enabled rule IDs from config
        enabled_rule_ids = self._get_enabled_rule_ids()

        # Create only enabled rule instances
        for rule_id in enabled_rule_ids:
            rule_instance = self._create_rule_instance(rule_id)
            if rule_instance:
                rule_instance.set_config_manager(self.config_manager)
                rule_instances[rule_id] = rule_instance

        return rule_instances

    def _get_enabled_rule_ids(self) -> list[str]:
        """設定に基づいて有効化されたルールIDのリストを取得します。"""
        if not self.config_manager or not hasattr(self.config_manager, "is_rule_enabled"):
            # No config manager or no rule filtering - return default rules
            return [
                "PTCM003", "PTST001", "PTLG001", "PTAS005", "PTNM001",
                "PTEC001", "PTEC002", "PTEC003", "PTEC004", "PTEC005"
            ]

        all_possible_rules = [
            "PTCM001", "PTCM002", "PTCM003",
            "PTST001",
            "PTLG001",
            "PTAS001", "PTAS002", "PTAS003", "PTAS004", "PTAS005",
            "PTNM001", "PTNM002", "PTNM003",
            "PTVL001", "PTVL002", "PTVL003", "PTVL004", "PTVL005",
            "PTEC001", "PTEC002", "PTEC003", "PTEC004", "PTEC005"
        ]

        return [
            rule_id for rule_id in all_possible_rules
            if self.config_manager.is_rule_enabled(rule_id)
        ]

    def _create_rule_instance(self, rule_id: str) -> Optional["BaseRule"]:
        """指定されたルールIDのインスタンスを作成します。"""
        # Rule factory mapping to avoid too many return statements
        rule_factories = {
            # Assertion rules
            "PTAS001": self._create_ptas001,
            "PTAS002": self._create_ptas002,
            "PTAS003": self._create_ptas003,
            "PTAS004": self._create_ptas004,
            "PTAS005": self._create_ptas005,
            # Comment pattern rules
            "PTCM001": self._create_ptcm001,
            "PTCM002": self._create_ptcm002,
            "PTCM003": self._create_ptcm003,
            # Naming rules
            "PTNM001": self._create_ptnm001,
            "PTNM002": self._create_ptnm002,
            "PTNM003": self._create_ptnm003,
            # Structure rules
            "PTST001": self._create_ptst001,
            # Logic rules
            "PTLG001": self._create_ptlg001,
            # Vulnerability rules
            "PTVL001": self._create_ptvl001,
            "PTVL002": self._create_ptvl002,
            "PTVL003": self._create_ptvl003,
            "PTVL004": self._create_ptvl004,
            "PTVL005": self._create_ptvl005,
            # Edge case rules
            "PTEC001": self._create_ptec001,
            "PTEC002": self._create_ptec002,
            "PTEC003": self._create_ptec003,
            "PTEC004": self._create_ptec004,
            "PTEC005": self._create_ptec005,
        }

        factory = rule_factories.get(rule_id)
        return factory() if factory else None

    def _create_ptas001(self) -> "BaseRule":
        """Create PTAS001 rule instance."""
        from pytestee.domain.analyzers.assertion_analyzer import AssertionAnalyzer
        from pytestee.domain.rules.assertion.too_few_assertions import PTAS001
        return PTAS001(AssertionAnalyzer())

    def _create_ptas002(self) -> "BaseRule":
        """Create PTAS002 rule instance."""
        from pytestee.domain.analyzers.assertion_analyzer import AssertionAnalyzer
        from pytestee.domain.rules.assertion.too_many_assertions import PTAS002
        return PTAS002(AssertionAnalyzer())

    def _create_ptas003(self) -> "BaseRule":
        """Create PTAS003 rule instance."""
        from pytestee.domain.analyzers.assertion_analyzer import AssertionAnalyzer
        from pytestee.domain.rules.assertion.high_assertion_density import PTAS003
        return PTAS003(AssertionAnalyzer())

    def _create_ptas004(self) -> "BaseRule":
        """Create PTAS004 rule instance."""
        from pytestee.domain.analyzers.assertion_analyzer import AssertionAnalyzer
        from pytestee.domain.rules.assertion.no_assertions import PTAS004
        return PTAS004(AssertionAnalyzer())

    def _create_ptas005(self) -> "BaseRule":
        """Create PTAS005 rule instance."""
        from pytestee.domain.analyzers.assertion_analyzer import AssertionAnalyzer
        from pytestee.domain.rules.assertion.assertion_count_ok import PTAS005
        return PTAS005(AssertionAnalyzer())

    def _create_ptcm001(self) -> "BaseRule":
        """Create PTCM001 rule instance."""
        from pytestee.domain.analyzers.pattern_analyzer import PatternAnalyzer
        from pytestee.domain.rules.comment.aaa_comment_pattern import PTCM001
        return PTCM001(PatternAnalyzer())

    def _create_ptcm002(self) -> "BaseRule":
        """Create PTCM002 rule instance."""
        from pytestee.domain.analyzers.pattern_analyzer import PatternAnalyzer
        from pytestee.domain.rules.comment.gwt_comment_pattern import PTCM002
        return PTCM002(PatternAnalyzer())

    def _create_ptcm003(self) -> "BaseRule":
        """Create PTCM003 rule instance."""
        from pytestee.domain.analyzers.pattern_analyzer import PatternAnalyzer
        from pytestee.domain.rules.comment.aaa_or_gwt_pattern import PTCM003
        return PTCM003(PatternAnalyzer())

    def _create_ptnm001(self) -> "BaseRule":
        """Create PTNM001 rule instance."""
        from pytestee.domain.analyzers.pattern_analyzer import PatternAnalyzer
        from pytestee.domain.rules.naming.japanese_characters import PTNM001
        return PTNM001(PatternAnalyzer())

    def _create_ptnm002(self) -> "BaseRule":
        """Create PTNM002 rule instance."""
        from pytestee.domain.analyzers.pattern_analyzer import PatternAnalyzer
        from pytestee.domain.rules.naming.japanese_class_names import PTNM002
        return PTNM002(PatternAnalyzer())

    def _create_ptnm003(self) -> "BaseRule":
        """Create PTNM003 rule instance."""
        from pytestee.domain.rules.naming.test_class_method_count import PTNM003
        return PTNM003()

    def _create_ptst001(self) -> "BaseRule":
        """Create PTST001 rule instance."""
        from pytestee.domain.rules.structure.structural_pattern import PTST001
        return PTST001()

    def _create_ptlg001(self) -> "BaseRule":
        """Create PTLG001 rule instance."""
        from pytestee.domain.rules.logic.logical_flow_pattern import PTLG001
        return PTLG001()

    def _create_ptvl001(self) -> "BaseRule":
        """Create PTVL001 rule instance."""
        from pytestee.domain.rules.vulnerability.ptvl001 import PTVL001
        return PTVL001()

    def _create_ptvl002(self) -> "BaseRule":
        """Create PTVL002 rule instance."""
        from pytestee.domain.rules.vulnerability.ptvl002 import PTVL002
        return PTVL002()

    def _create_ptvl003(self) -> "BaseRule":
        """Create PTVL003 rule instance."""
        from pytestee.domain.rules.vulnerability.ptvl003 import PTVL003
        return PTVL003()

    def _create_ptvl004(self) -> "BaseRule":
        """Create PTVL004 rule instance."""
        from pytestee.domain.rules.vulnerability.ptvl004 import PTVL004
        return PTVL004()

    def _create_ptvl005(self) -> "BaseRule":
        """Create PTVL005 rule instance."""
        from pytestee.domain.rules.vulnerability.ptvl005 import PTVL005
        return PTVL005()

    def _create_ptec001(self) -> "BaseRule":
        """Create PTEC001 rule instance."""
        from pytestee.domain.analyzers.edge_case_analyzer import EdgeCaseAnalyzer
        from pytestee.domain.rules.edge_case.ptec001 import PTEC001
        return PTEC001(EdgeCaseAnalyzer())

    def _create_ptec002(self) -> "BaseRule":
        """Create PTEC002 rule instance."""
        from pytestee.domain.analyzers.edge_case_analyzer import EdgeCaseAnalyzer
        from pytestee.domain.rules.edge_case.ptec002 import PTEC002
        return PTEC002(EdgeCaseAnalyzer())

    def _create_ptec003(self) -> "BaseRule":
        """Create PTEC003 rule instance."""
        from pytestee.domain.analyzers.edge_case_analyzer import EdgeCaseAnalyzer
        from pytestee.domain.rules.edge_case.ptec003 import PTEC003
        return PTEC003(EdgeCaseAnalyzer())

    def _create_ptec004(self) -> "BaseRule":
        """Create PTEC004 rule instance."""
        from pytestee.domain.analyzers.edge_case_analyzer import EdgeCaseAnalyzer
        from pytestee.domain.rules.edge_case.ptec004 import PTEC004
        return PTEC004(EdgeCaseAnalyzer())

    def _create_ptec005(self) -> "BaseRule":
        """Create PTEC005 rule instance."""
        from pytestee.domain.analyzers.edge_case_analyzer import EdgeCaseAnalyzer
        from pytestee.domain.rules.edge_case.ptec005 import PTEC005
        return PTEC005(EdgeCaseAnalyzer())

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
