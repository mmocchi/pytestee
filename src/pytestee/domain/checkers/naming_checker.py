"""テストメソッドの命名規則をチェックするチェッカー。"""

from typing import List, Optional

from ...domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from ..rules.ptnm.japanese_characters import PTNM001
from .base_checker import BaseChecker


class NamingChecker(BaseChecker):
    """テストメソッドの命名規則をチェックするチェッカー。"""

    def __init__(self, config_manager: Optional[object] = None) -> None:
        super().__init__("naming_checker")
        self.config_manager = config_manager
        self.ptnm001 = PTNM001()

        # Set config_manager for all rules
        self.ptnm001.set_config_manager(config_manager)

    def check_function(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """テストメソッドの命名規則をチェック。

        Args:
            test_function: チェック対象のテスト関数
            test_file: テストファイル情報
            config: チェッカー設定

        Returns:
            チェック結果のリスト

        """
        results = []

        # Run PTNM001 rule if enabled
        if self.ptnm001.is_enabled(self.config_manager):
            ptnm001_results = self.ptnm001.check(test_function, test_file, config)
            results.extend(ptnm001_results)

        return results
