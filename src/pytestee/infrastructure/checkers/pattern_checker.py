"""優先度ロジックを使用してパターン検出ルールを適用するパターンチェッカー。"""

from typing import Dict, List, Optional

from ...domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from ..rules.ptcm.aaa_comment_pattern import PTCM001
from ..rules.ptcm.aaa_or_gwt_pattern import PTCM003
from ..rules.ptcm.gwt_comment_pattern import PTCM002
from ..rules.ptlg.logical_flow_pattern import PTLG001
from ..rules.ptst.structural_pattern import PTST001
from .base_checker import BaseChecker


class PatternChecker(BaseChecker):
    """優先度ベースのルール適用でAAA/GWTパターンをチェックするチェッカー。"""

    def __init__(self, config_manager: Optional[object] = None) -> None:
        super().__init__("pattern_checker")
        self.config_manager = config_manager
        self.ptcm001 = PTCM001()
        self.ptcm002 = PTCM002()
        self.ptcm003 = PTCM003()
        self.ptst001 = PTST001()
        self.ptlg001 = PTLG001()

        # Set config_manager for all rules
        for rule in [self.ptcm001, self.ptcm002, self.ptcm003, self.ptst001, self.ptlg001]:
            rule.set_config_manager(config_manager)

    def check_function(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """優先度ロジックでAAA/GWTパターンをチェック。"""
        results: List[CheckResult] = []

        # Rules in priority order (highest to lowest)
        priority_rules = [
            (self.ptcm003, "PTCM003 (AAA or GWT)"),    # Priority 1: Composite comment patterns
            (self.ptcm001, "PTCM001 (AAA comments)"),  # Priority 2: AAA comment patterns
            (self.ptcm002, "PTCM002 (GWT comments)"),  # Priority 2: GWT comment patterns
            (self.ptst001, "PTST001 (structural)"),    # Priority 3: Structural patterns
            (self.ptlg001, "PTLG001 (logical flow)")   # Priority 4: Logical flow patterns
        ]

        # Find the highest priority pattern that is enabled and has results
        for rule, _description in priority_rules:
            if rule.is_enabled(self.config_manager):
                rule_results = rule.check(test_function, test_file, config)
                if rule_results:
                    # Return the first (and only) result from the highest priority rule
                    return [rule_results[0]]

        # If no enabled rules found any results, this shouldn't happen with the new self-contained approach
        # But as fallback, return empty list
        return results

    def get_rule_instances(self) -> Dict[str, object]:
        """このチェッカーが持つルールインスタンスを返す。"""
        return {
            "PTCM001": self.ptcm001,
            "PTCM002": self.ptcm002,
            "PTCM003": self.ptcm003,
            "PTST001": self.ptst001,
            "PTLG001": self.ptlg001
        }
