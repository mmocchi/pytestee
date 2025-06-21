"""pytesteeのドメインインターフェース。"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import AnalysisResult, CheckerConfig, CheckResult, TestFile, TestFunction


class ITestRepository(ABC):
    """テストファイルリポジトリのインターフェース。"""

    @abstractmethod
    def find_test_files(self, path: Path) -> List[Path]:
        """指定されたパス内のすべてのテストファイルを検索。"""
        pass

    @abstractmethod
    def load_test_file(self, file_path: Path) -> TestFile:
        """テストファイルを読み込み、解析。"""
        pass


class IChecker(ABC):
    """テスト品質チェッカーのインターフェース。"""

    @property
    @abstractmethod
    def name(self) -> str:
        """このチェッカーの名前を取得。"""
        pass

    @abstractmethod
    def check(self, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """テストファイルをチェックし、結果を返す。"""
        pass

    @abstractmethod
    def check_function(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """特定のテスト関数をチェックし、結果を返す。"""
        pass


class IPresenter(ABC):
    """解析結果を表示するインターフェース。"""

    @abstractmethod
    def present(self, result: AnalysisResult) -> None:
        """解析結果を表示。"""
        pass


class IConfigManager(ABC):
    """設定管理のインターフェース。"""

    @abstractmethod
    def load_config(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """ファイルまたはデフォルトから設定を読み込み。"""
        pass

    @abstractmethod
    def get_checker_config(self, checker_name: str) -> CheckerConfig:
        """特定のチェッカーの設定を取得。"""
        pass

    @abstractmethod
    def get_global_config(self) -> Dict[str, Any]:
        """グローバル設定を取得。"""
        pass


class ICheckerRegistry(ABC):
    """チェッカーレジストリのインターフェース。"""

    @abstractmethod
    def register(self, checker: IChecker) -> None:
        """チェッカーを登録。"""
        pass

    @abstractmethod
    def get_checker(self, name: str) -> Optional[IChecker]:
        """名前でチェッカーを取得。"""
        pass

    @abstractmethod
    def get_all_checkers(self) -> List[IChecker]:
        """登録されたすべてのチェッカーを取得。"""
        pass

    @abstractmethod
    def get_enabled_checkers(self, config: Dict[str, Any]) -> List[IChecker]:
        """設定に基づいて有効なすべてのチェッカーを取得。"""
        pass
