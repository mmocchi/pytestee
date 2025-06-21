"""pytesteeのドメインモデル定義。"""

import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class CheckSeverity(Enum):
    """チェック結果の重要度レベル。"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class PatternType(Enum):
    """テストパターンの種類。"""

    AAA = "aaa"  # Arrange, Act, Assert
    GWT = "gwt"  # Given, When, Then


@dataclass
class TestFunction:
    """コード内のテスト関数を表すクラス。"""

    name: str
    lineno: int
    col_offset: int
    end_lineno: Optional[int]
    end_col_offset: Optional[int]
    body: List[ast.stmt]
    docstring: Optional[str] = None
    decorators: Optional[List[str]] = None

    def __post_init__(self) -> None:
        # デコレータがNoneの場合は空のリストで初期化
        if self.decorators is None:
            self.decorators = []


@dataclass
class TestFile:
    """テスト関数を含むテストファイルを表すクラス。"""

    path: Path
    content: str
    ast_tree: ast.AST
    test_functions: List[TestFunction]

    @property
    def relative_path(self) -> str:
        """相対パスを文字列として取得。"""
        return str(self.path)


@dataclass
class CheckResult:
    """品質チェックの結果。"""

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
        # コンテキストがNoneの場合は空の辞書で初期化
        if self.context is None:
            self.context = {}


@dataclass
class AnalysisResult:
    """テストファイル解析の結果。"""

    total_files: int
    total_tests: int
    passed_checks: int
    failed_checks: int
    check_results: List[CheckResult]

    @property
    def success_rate(self) -> float:
        """成功率をパーセンテージで計算。"""
        total = self.passed_checks + self.failed_checks
        if total == 0:
            return 100.0
        return (self.passed_checks / total) * 100.0

    @property
    def has_errors(self) -> bool:
        """エラーレベルの問題があるかをチェック。"""
        return any(result.severity == CheckSeverity.ERROR for result in self.check_results)

    @property
    def has_warnings(self) -> bool:
        """警告レベルの問題があるかをチェック。"""
        return any(result.severity == CheckSeverity.WARNING for result in self.check_results)


@dataclass
class CheckerConfig:
    """チェッカーの設定。"""

    name: str
    enabled: bool = True
    config: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        # 設定がNoneの場合は空の辞書で初期化
        if self.config is None:
            self.config = {}
