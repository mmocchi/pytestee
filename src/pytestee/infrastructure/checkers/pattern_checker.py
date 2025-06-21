"""優先度ロジックを使用してパターン検出ルールを適用するパターンチェッカー。"""

from typing import List, Optional

from ...domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from ..rules.ptcm.aaa_comment_pattern import PTCM001
from ..rules.ptcm.gwt_comment_pattern import PTCM002
from ..rules.ptlg.logical_flow_pattern import PTLG001
from ..rules.ptst.pattern_not_detected import PTST002
from ..rules.ptst.structural_pattern import PTST001
from .base_checker import BaseChecker


class PatternChecker(BaseChecker):
    """優先度ベースのルール適用でAAA/GWTパターンをチェックするチェッカー。"""

    def __init__(self) -> None:
        super().__init__("pattern_checker")
        self.ptcm001 = PTCM001()
        self.ptcm002 = PTCM002()
        self.ptst001 = PTST001()
        self.ptst002 = PTST002()
        self.ptlg001 = PTLG001()

    def check_function(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """優先度ロジックでAAA/GWTパターンをチェック。"""
        results = []

        # Priority 1: Comment-based patterns (highest priority)
        comment_aaa_results = self.ptcm001.check(test_function, test_file, config)
        comment_gwt_results = self.ptcm002.check(test_function, test_file, config)

        if comment_aaa_results or comment_gwt_results:
            results.extend(comment_aaa_results)
            results.extend(comment_gwt_results)
            return results  # コメントパターンが見つかった場合はここで停止

        # Priority 2: Structural patterns (empty line separation)
        structural_results = self.ptst001.check(test_function, test_file, config)
        if structural_results:
            results.extend(structural_results)
            return results  # 構造的パターンが見つかった場合はここで停止

        # Priority 3: Logical flow patterns (AST analysis)
        logical_results = self.ptlg001.check(test_function, test_file, config)
        if logical_results:
            results.extend(logical_results)
            return results  # 論理パターンが見つかった場合はここで停止

        # Priority 4: Pattern not detected (warning)
        warning_results = self.ptst002.check(test_function, test_file, config)
        results.extend(warning_results)

        return results
