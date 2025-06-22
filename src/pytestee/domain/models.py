"""pytesteeのドメインモデル定義。

このモジュールでは、アプリケーションの中核となるビジネスロジックを
表現するデータモデルを定義します。Clean Architectureに従い、
外部システムに依存しない純粋なビジネスエンティティを提供します。
"""

import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class CheckSeverity(Enum):
    """チェック結果の重要度レベル。

    テスト品質チェックの結果に関する重要度を表します。
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class PatternType(Enum):
    """テストパターンの種類。

    サポートされているテストパターンの種類を定義します。
    """

    AAA = "aaa"  # Arrange, Act, Assert
    GWT = "gwt"  # Given, When, Then


@dataclass
class TestFunction:
    """コード内のテスト関数を表すクラス。

    Python ASTから抽出されたテスト関数の情報をカプセル化し、
    テストの特定と解析に必要なメタデータを保持します。

    Attributes:
        name: テスト関数の名前
        lineno: 関数開始行番号
        col_offset: 関数開始のカラムオフセット
        end_lineno: 関数終了行番号(オプション)
        end_col_offset: 関数終了のカラムオフセット(オプション)
        body: 関数本体のASTステートメントリスト
        docstring: 関数のdocstring(存在する場合)
        decorators: 関数に適用されたデコレーター名のリスト

    """

    name: str
    lineno: int
    col_offset: int
    end_lineno: Optional[int]
    end_col_offset: Optional[int]
    body: List[ast.stmt]
    docstring: Optional[str] = None
    decorators: Optional[List[str]] = None

    def __post_init__(self) -> None:
        """オブジェクト作成後の初期化処理を実行します。"""
        # デコレータがNoneの場合は空のリストで初期化
        if self.decorators is None:
            self.decorators = []


@dataclass
class TestFile:
    """テスト関数を含むテストファイルを表すクラス。

    ファイルシステムから読み込まれたテストファイルの内容と、
    その中に含まれるテスト関数の情報を保持します。

    Attributes:
        path: ファイルのパス
        content: ファイルのソースコード内容
        ast_tree: 解析されたPython AST
        test_functions: ファイル内のテスト関数リスト

    """

    path: Path
    content: str
    ast_tree: ast.AST
    test_functions: List[TestFunction]

    @property
    def relative_path(self) -> str:
        """相対パスを文字列として取得します。

        Returns:
            ファイルパスの文字列表現

        """
        return str(self.path)


@dataclass
class CheckResult:
    """品質チェックの結果。

    個別のチェッカーが実行した品質チェックの結果を表します。
    エラーの種類、位置、メッセージなどの詳細情報を含みます。

    Attributes:
        checker_name: チェックを実行したチェッカーの名前
        rule_id: 違反したルールのID
        severity: 問題の重要度
        message: ユーザー向けメッセージ
        file_path: 問題が発生したファイルのパス
        line_number: 問題が発生した行番号(オプション)
        column: 問題が発生したカラム位置(オプション)
        function_name: 問題が発生した関数名(オプション)
        context: 追加のコンテキスト情報(オプション)

    """

    checker_name: str
    rule_id: str
    severity: CheckSeverity
    message: str
    file_path: Path
    line_number: Optional[int] = None
    column: Optional[int] = None
    function_name: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """オブジェクト作成後の初期化処理を実行します。"""
        # コンテキストがNoneの場合は空の辞書で初期化
        if self.context is None:
            self.context = {}


@dataclass
class AnalysisResult:
    """テストファイル解析の結果。

    複数のテストファイルに対する品質チェックの全体的な結果を
    集約したものです。統計情報と詳細なチェック結果を保持します。

    Attributes:
        total_files: 解析したファイル数
        total_tests: 発見したテスト関数の総数
        passed_checks: 成功したチェック数
        failed_checks: 失敗したチェック数
        check_results: 個別のチェック結果のリスト

    """

    total_files: int
    total_tests: int
    passed_checks: int
    failed_checks: int
    check_results: List[CheckResult]

    @property
    def success_rate(self) -> float:
        """成功率をパーセンテージで計算します。

        Returns:
            成功率(0.0-100.0の範囲)

        """
        total = self.passed_checks + self.failed_checks
        if total == 0:
            return 100.0
        return (self.passed_checks / total) * 100.0

    @property
    def has_errors(self) -> bool:
        """エラーレベルの問題があるかをチェックします。

        Returns:
            エラーレベルの問題が存在する場合True

        """
        return any(
            result.severity == CheckSeverity.ERROR for result in self.check_results
        )

    @property
    def has_warnings(self) -> bool:
        """警告レベルの問題があるかをチェックします。

        Returns:
            警告レベルの問題が存在する場合True

        """
        return any(
            result.severity == CheckSeverity.WARNING for result in self.check_results
        )


@dataclass
class CheckerConfig:
    """チェッカーの設定。

    個別のチェッカーの動作を制御する設定情報を保持します。

    Attributes:
        name: チェッカー名
        enabled: チェッカーが有効かどうか
        config: チェッカー固有の設定パラメーター

    """

    name: str
    enabled: bool = True
    config: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """オブジェクト作成後の初期化処理を実行します。"""
        # 設定がNoneの場合は空の辞書で初期化
        if self.config is None:
            self.config = {}
