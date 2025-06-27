"""pytesteeのドメインモデル定義。

このモジュールでは、アプリケーションの中核となるビジネスロジックを
表現するデータモデルを定義します。Clean Architectureに従い、
外部システムに依存しない純粋なビジネスエンティティを提供します。
"""

import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union


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
    body: list[ast.stmt]
    docstring: Optional[str] = None
    decorators: Optional[list[str]] = None

    def __post_init__(self) -> None:
        """オブジェクト作成後の初期化処理を実行します。"""
        # デコレータがNoneの場合は空のリストで初期化
        if self.decorators is None:
            self.decorators = []


@dataclass
class TestClass:
    """コード内のテストクラスを表すクラス。

    Python ASTから抽出されたテストクラスの情報をカプセル化し、
    テストクラスの特定と解析に必要なメタデータを保持します。

    Attributes:
        name: テストクラスの名前
        lineno: クラス開始行番号
        col_offset: クラス開始のカラムオフセット
        end_lineno: クラス終了行番号(オプション)
        end_col_offset: クラス終了のカラムオフセット(オプション)
        body: クラス本体のASTステートメントリスト
        docstring: クラスのdocstring(存在する場合)
        decorators: クラスに適用されたデコレーター名のリスト
        test_methods: クラス内のテストメソッドリスト

    """

    name: str
    lineno: int
    col_offset: int
    end_lineno: Optional[int]
    end_col_offset: Optional[int]
    body: list[ast.stmt]
    docstring: Optional[str] = None
    decorators: Optional[list[str]] = None
    test_methods: Optional[list[str]] = None

    def __post_init__(self) -> None:
        """オブジェクト作成後の初期化処理を実行します。"""
        # デコレータがNoneの場合は空のリストで初期化
        if self.decorators is None:
            self.decorators = []
        # テストメソッドがNoneの場合は空のリストで初期化
        if self.test_methods is None:
            self.test_methods = []


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
        test_classes: ファイル内のテストクラスリスト

    """

    path: Path
    content: str
    ast_tree: ast.AST
    test_functions: list[TestFunction]
    test_classes: list[TestClass]

    @property
    def relative_path(self) -> str:
        """相対パスを文字列として取得します。

        Returns:
            ファイルパスの文字列表現

        """
        return str(self.path)


@dataclass
class CheckResultBase:
    """品質チェック結果の基底クラス。

    チェック成功・失敗に共通する属性を定義します。
    Returnオブジェクトパターンに基づいて成功・失敗を明確に区別します。

    Attributes:
        checker_name: チェックを実行したチェッカーの名前
        rule_id: 実行したルールのID
        message: ユーザー向けメッセージ
        file_path: チェック対象ファイルのパス
        line_number: 対象行番号(オプション)
        column: 対象カラム位置(オプション)
        function_name: 対象関数名(オプション)
        context: 追加のコンテキスト情報(オプション)

    """

    checker_name: str
    rule_id: str
    message: str
    file_path: Path
    line_number: Optional[int] = None
    column: Optional[int] = None
    function_name: Optional[str] = None
    context: Optional[dict[str, Any]] = None

    def __post_init__(self) -> None:
        """オブジェクト作成後の初期化処理を実行します。"""
        # コンテキストがNoneの場合は空の辞書で初期化
        if self.context is None:
            self.context = {}


@dataclass
class CheckSuccess(CheckResultBase):
    """品質チェック成功結果。

    ルールに適合している場合の結果を表します。
    """

    pass


@dataclass
class CheckFailure(CheckResultBase):
    """品質チェック失敗結果。

    ルールに違反している場合の結果を表します。
    severityでエラーレベル(ERROR/WARNING)を指定します。

    Attributes:
        severity: 問題の重要度(ERRORまたはWARNING)

    """

    severity: CheckSeverity = CheckSeverity.ERROR


# チェック結果のUnion型定義 - Returnオブジェクトパターンを実装
CheckResult = Union[CheckSuccess, CheckFailure]


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
    check_results: list[CheckResult]

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
            isinstance(result, CheckFailure) and result.severity == CheckSeverity.ERROR
            for result in self.check_results
        )

    @property
    def has_warnings(self) -> bool:
        """警告レベルの問題があるかをチェックします。

        Returns:
            警告レベルの問題が存在する場合True

        """
        return any(
            isinstance(result, CheckFailure) and result.severity == CheckSeverity.WARNING
            for result in self.check_results
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
    config: Optional[dict[str, Any]] = None

    def __post_init__(self) -> None:
        """オブジェクト作成後の初期化処理を実行します。"""
        # 設定がNoneの場合は空の辞書で初期化
        if self.config is None:
            self.config = {}


@dataclass
class RuleAchievementRate:
    """個別ルールの達成率。

    各ルールごとの達成率(成功率)とその詳細情報を保持します。

    Attributes:
        rule_id: ルールID(例: PTAS001)
        checker_name: チェッカー名
        total_checks: 総チェック数
        passed_checks: 成功したチェック数
        failed_checks: 失敗したチェック数

    """

    rule_id: str
    checker_name: str
    total_checks: int
    passed_checks: int
    failed_checks: int

    @property
    def achievement_rate(self) -> float:
        """達成率をパーセンテージで計算します。

        Returns:
            達成率(0.0-100.0の範囲)

        """
        if self.total_checks == 0:
            return 100.0
        return (self.passed_checks / self.total_checks) * 100.0


@dataclass
class AchievementRateResult:
    """全体の達成率結果。

    全ルールの達成率と統計情報を集約したものです。

    Attributes:
        total_files: 解析したファイル数
        total_tests: 発見したテスト関数の総数
        rule_rates: 各ルールの達成率リスト
        overall_rate: 全体の達成率

    """

    total_files: int
    total_tests: int
    rule_rates: list[RuleAchievementRate]
    overall_rate: float
