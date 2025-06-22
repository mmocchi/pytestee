"""テストメソッド名に日本語文字が含まれているかをチェックするルール。"""

import re
from typing import Optional

from pytestee.domain.models import (
    CheckerConfig,
    CheckResult,
    CheckSeverity,
    TestFile,
    TestFunction,
)
from pytestee.domain.rules.base_rule import BaseRule


class PTNM001(BaseRule):
    """テストメソッド名に日本語文字が含まれているかをチェック。

    日本語文字(ひらがな、カタカナ、漢字)がテストメソッド名に含まれている場合は
    適切であることを示すINFOレベルのメッセージを返す。
    含まれていない場合は、日本語での命名を推奨するWARNINGレベルのメッセージを返す。
    """

    def __init__(self) -> None:
        super().__init__(
            rule_id="PTNM001",
            name="japanese_characters_in_name",
            description="テストメソッド名に日本語文字が含まれているかをチェック",
        )

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """テストメソッド名に日本語文字が含まれているかをチェック。

        Args:
            test_function: チェック対象のテスト関数
            test_file: テストファイル情報
            config: チェッカー設定(未使用)

        Returns:
            チェック結果のリスト

        """
        if not test_function.name.startswith("test_"):
            # Skip non-test functions but still return a result
            return self._create_failure_result(
                f"関数 '{test_function.name}' はテスト関数ではありません",
                test_file,
                test_function,
                severity=CheckSeverity.INFO,
            )

        if self._contains_japanese_characters(test_function.name):
            return self._create_failure_result(
                f"テストメソッド名 '{test_function.name}' に日本語文字が含まれています。可読性が良好です。",
                test_file,
                test_function,
                severity=CheckSeverity.INFO,
            )
        return self._create_failure_result(
            f"テストメソッド名 '{test_function.name}' に日本語文字が含まれていません。可読性向上のため日本語での命名を検討してください。",
            test_file,
            test_function,
            severity=CheckSeverity.WARNING,
        )

    def _contains_japanese_characters(self, text: str) -> bool:
        """テキストに日本語文字(ひらがな、カタカナ、漢字)が含まれているかチェック。

        Args:
            text: チェック対象のテキスト

        Returns:
            日本語文字が含まれている場合True

        """
        japanese_pattern = r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]"
        return bool(re.search(japanese_pattern, text))
