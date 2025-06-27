"""テストクラス名に日本語文字が含まれているかをチェックするルール。"""

from typing import TYPE_CHECKING, Optional

from pytestee.domain.models import (
    CheckerConfig,
    CheckResult,
    CheckSeverity,
    TestClass,
    TestFile,
)
from pytestee.domain.rules.base_rule import BaseRule

if TYPE_CHECKING:
    from pytestee.domain.analyzers.pattern_analyzer import PatternAnalyzer
    from pytestee.domain.models import TestFunction


class PTNM002(BaseRule):
    """テストクラス名に日本語文字が含まれているかをチェック。

    日本語文字(ひらがな、カタカナ、漢字)がテストクラス名に含まれている場合は
    適切であることを示すINFOレベルのメッセージを返す。
    含まれていない場合は、日本語での命名を推奨するWARNINGレベルのメッセージを返す。
    """

    def __init__(self, pattern_analyzer: "PatternAnalyzer") -> None:
        super().__init__(
            rule_id="PTNM002",
            name="japanese_characters_in_class_name",
            description="テストクラス名に日本語文字が含まれているかをチェック",
        )
        self._analyzer = pattern_analyzer

    def check_class(
        self,
        test_class: TestClass,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """テストクラス名に日本語文字が含まれているかをチェック。

        Args:
            test_class: チェック対象のテストクラス
            test_file: テストファイル情報
            config: チェッカー設定(未使用)

        Returns:
            チェック結果

        """
        if not test_class.name.startswith("Test"):
            # Skip non-test classes but still return a result
            return self._create_failure_result(
                f"クラス '{test_class.name}' はテストクラスではありません",
                test_file,
                None,
                line_number=test_class.lineno,
                column=test_class.col_offset,
            )

        if self._analyzer.has_japanese_characters_in_class(test_class):
            return self._create_success_result(
                f"テストクラス名 '{test_class.name}' に日本語文字が含まれています。可読性が良好です。",
                test_file,
                None,
                line_number=test_class.lineno,
                column=test_class.col_offset,
            )
        return self._create_failure_result(
            f"テストクラス名 '{test_class.name}' に日本語文字が含まれていません。可読性向上のため日本語での命名を検討してください。",
            test_file,
            None,
            severity=CheckSeverity.WARNING,
            line_number=test_class.lineno,
            column=test_class.col_offset,
        )

    def check(
        self,
        test_function: "TestFunction",
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """BaseRuleインターフェース互換のためのダミーメソッド。

        PTNM002は関数レベルではなくクラスレベルのルールなので、
        この方法では使用されません。check_classメソッドを使用してください。
        """
        # This rule operates on classes, not functions
        # Return a neutral result indicating this rule doesn't apply to functions
        return self._create_success_result(
            "PTNM002はクラスレベルのルールです",
            test_file,
            test_function
        )

