"""pytesteeのドメインインターフェース。

このモジュールでは、アプリケーションの中核となるビジネスロジックの
インターフェースを定義します。Clean Architectureに従い、外部の実装
詳細に依存しない抽象的な契約を提供します。
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from pytestee.domain.models import (
    AnalysisResult,
    CheckerConfig,
    CheckResult,
    TestFile,
    TestFunction,
)

if TYPE_CHECKING:
    from pytestee.domain.rules.base_rule import BaseRule


class ITestRepository(ABC):
    """テストファイルリポジトリのインターフェース。

    テストファイルの検索と読み込みを行うリポジトリの抽象定義です。
    """

    @abstractmethod
    def find_test_files(self, path: Path) -> list[Path]:
        """指定されたパス内のすべてのテストファイルを検索します。

        Args:
            path: 検索対象のディレクトリパス

        Returns:
            発見されたテストファイルのパスリスト

        """
        pass

    @abstractmethod
    def load_test_file(self, file_path: Path) -> TestFile:
        """テストファイルを読み込み、解析します。

        Args:
            file_path: 読み込み対象のファイルパス

        Returns:
            解析されたテストファイル

        Raises:
            ParseError: ファイル解析に失敗した場合

        """
        pass


class IChecker(ABC):
    """テスト品質チェッカーのインターフェース。

    テストコードの品質をチェックするチェッカーの抽象定義です。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """このチェッカーの名前を取得します。

        Returns:
            チェッカーの一意な名前

        """
        pass

    @abstractmethod
    def check(
        self, test_file: TestFile, config: Optional[CheckerConfig] = None
    ) -> list[CheckResult]:
        """テストファイルをチェックし、結果を返します。

        Args:
            test_file: チェック対象のテストファイル
            config: チェッカー設定(オプション)

        Returns:
            チェック結果のリスト

        """
        pass

    @abstractmethod
    def check_function(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> list[CheckResult]:
        """特定のテスト関数をチェックし、結果を返します。

        Args:
            test_function: チェック対象のテスト関数
            test_file: テスト関数を含むファイル
            config: チェッカー設定(オプション)

        Returns:
            チェック結果のリスト

        """
        pass


class IPresenter(ABC):
    """解析結果を表示するインターフェース。

    分析結果をユーザーに提示するプレゼンター層の抽象定義です。
    """

    @abstractmethod
    def present(self, result: AnalysisResult) -> None:
        """解析結果を表示します。

        Args:
            result: 表示する解析結果

        """
        pass


class IConfigManager(ABC):
    """設定管理のインターフェース。

    アプリケーション設定の読み込みと管理を行うマネージャーの抽象定義です。
    """

    @abstractmethod
    def load_config(self, config_path: Optional[Path] = None) -> dict[str, Any]:
        """ファイルまたはデフォルトから設定を読み込みます。

        Args:
            config_path: 設定ファイルのパス(オプション)

        Returns:
            読み込まれた設定

        """
        pass

    @abstractmethod
    def get_checker_config(self, checker_name: str) -> CheckerConfig:
        """特定のチェッカーの設定を取得します。

        Args:
            checker_name: チェッカー名

        Returns:
            チェッカーの設定

        """
        pass

    @abstractmethod
    def get_global_config(self) -> dict[str, Any]:
        """グローバル設定を取得します。

        Returns:
            グローバル設定

        """
        pass

    @abstractmethod
    def is_rule_enabled(self, rule_id: str) -> bool:
        """特定のルールが有効かどうかをチェックします。

        Args:
            rule_id: ルールID

        Returns:
            ルールが有効な場合True

        """
        pass

    @abstractmethod
    def is_rule_enabled_for_file(self, rule_id: str, file_path: Path) -> bool:
        """特定のファイルパスに対してルールが有効かどうかをチェックします。

        Args:
            rule_id: ルールID
            file_path: ファイルパス

        Returns:
            ルールが有効な場合True

        """
        pass

    @abstractmethod
    def get_rule_config_for_file(self, rule_id: str, file_path: Path) -> dict[str, Any]:
        """特定のファイルパスに対するルール固有の設定を取得します。

        Args:
            rule_id: ルールID
            file_path: ファイルパス

        Returns:
            ルール固有の設定

        """
        pass


class ICheckerRegistry(ABC):
    """チェッカーレジストリのインターフェース。

    利用可能なチェッカーの登録と管理を行うレジストリの抽象定義です。
    """

    @abstractmethod
    def register(self, checker: IChecker) -> None:
        """チェッカーを登録します。

        Args:
            checker: 登録するチェッカー

        """
        pass

    @abstractmethod
    def get_checker(self, name: str) -> Optional[IChecker]:
        """名前でチェッカーを取得します。

        Args:
            name: チェッカー名

        Returns:
            チェッカーまたはNone

        """
        pass

    @abstractmethod
    def get_all_checkers(self) -> list[IChecker]:
        """登録されたすべてのチェッカーを取得します。

        Returns:
            チェッカーのリスト

        """
        pass

    @abstractmethod
    def get_enabled_checkers(self, config: dict[str, Any]) -> list[IChecker]:
        """設定に基づいて有効なすべてのチェッカーを取得します。

        Args:
            config: 設定

        Returns:
            有効なチェッカーのリスト

        """
        pass

    @abstractmethod
    def get_all_rule_instances(self) -> dict[str, "BaseRule"]:
        """すべてのルールインスタンスを取得します。

        Returns:
            ルールID -> ルールインスタンスのマッピング

        """
        pass
