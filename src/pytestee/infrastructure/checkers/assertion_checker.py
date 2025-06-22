"""アサーション関連のルールを適用するアサーションチェッカー。"""

from typing import List, Optional

from ...domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from ..rules.ptas.assertion_count_ok import PTAS005
from ..rules.ptas.high_assertion_density import PTAS003
from ..rules.ptas.no_assertions import PTAS004
from ..rules.ptas.too_few_assertions import PTAS001
from ..rules.ptas.too_many_assertions import PTAS002
from .base_checker import BaseChecker


class AssertionChecker(BaseChecker):
    """アサーション関連ルールのチェッカー。"""

    def __init__(self, config_manager: Optional[object] = None) -> None:
        super().__init__("assertion_checker")
        self.config_manager = config_manager
        self.ptas001 = PTAS001()
        self.ptas002 = PTAS002()
        self.ptas003 = PTAS003()
        self.ptas004 = PTAS004()
        self.ptas005 = PTAS005()

        # Set config_manager for all rules
        for rule in [self.ptas001, self.ptas002, self.ptas003, self.ptas004, self.ptas005]:
            rule.set_config_manager(config_manager)

    def check_function(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """アサーション関連ルールをチェック。"""
        results = []

        # First check for no assertions (highest priority error)
        if self.ptas004.is_enabled(self.config_manager):
            no_assertions_results = self.ptas004.check(test_function, test_file, config)
            if no_assertions_results:
                results.extend(no_assertions_results)
                return results  # アサーションが見つからない場合はここで停止

        # アサーション数の制限をチェック
        if self.ptas001.is_enabled(self.config_manager):
            too_few_results = self.ptas001.check(test_function, test_file, config)
            results.extend(too_few_results)

        if self.ptas002.is_enabled(self.config_manager):
            too_many_results = self.ptas002.check(test_function, test_file, config)
            results.extend(too_many_results)

        # アサーション密度をチェック
        if self.ptas003.is_enabled(self.config_manager):
            density_results = self.ptas003.check(test_function, test_file, config)
            results.extend(density_results)

        # 問題が見つからない場合は程性的結果を追加
        if not results and self.ptas005.is_enabled(self.config_manager):
            ok_results = self.ptas005.check(test_function, test_file, config)
            results.extend(ok_results)

        return results
