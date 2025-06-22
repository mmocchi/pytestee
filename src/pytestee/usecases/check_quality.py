"""Use case for quality checking operations."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pytestee.domain.interfaces import IChecker, ITestRepository
from pytestee.domain.models import CheckerConfig, CheckResult


class CheckQualityUseCase:
    """Use case for running specific quality checks on test files."""

    def __init__(self, test_repository: ITestRepository) -> None:
        """品質チェックユースケースを初期化します。

        Args:
            test_repository: テストリポジトリインターフェース

        """
        self._test_repository = test_repository

    def check_single_file(
        self,
        file_path: Path,
        checkers: List[IChecker],
        config: Optional[Dict[str, Any]] = None,
    ) -> List[CheckResult]:
        """指定されたチェッカーで単一のテストファイルをチェックします。

        Args:
            file_path: チェック対象のファイルパス
            checkers: 使用するチェッカーのリスト
            config: 設定(オプション)

        Returns:
            チェック結果のリスト

        """
        if config is None:
            config = {}

        # Load the test file
        test_file = self._test_repository.load_test_file(file_path)

        # Run all checkers on the file
        results = []
        for checker in checkers:
            checker_config = self._create_checker_config(checker.name, config)
            checker_results = checker.check(test_file, checker_config)
            results.extend(checker_results)

        return results

    def check_specific_function(
        self,
        file_path: Path,
        function_name: str,
        checkers: List[IChecker],
        config: Optional[Dict[str, Any]] = None,
    ) -> List[CheckResult]:
        """指定されたチェッカーで特定のテスト関数をチェックします。

        Args:
            file_path: チェック対象のファイルパス
            function_name: チェック対象の関数名
            checkers: 使用するチェッカーのリスト
            config: 設定(オプション)

        Returns:
            チェック結果のリスト

        Raises:
            ValueError: 指定された関数が見つからない場合

        """
        if config is None:
            config = {}

        # Load the test file
        test_file = self._test_repository.load_test_file(file_path)

        # Find the specific function
        target_function = None
        for test_function in test_file.test_functions:
            if test_function.name == function_name:
                target_function = test_function
                break

        if not target_function:
            raise ValueError(
                f"Test function '{function_name}' not found in {file_path}"
            )

        # Run all checkers on the specific function
        results = []
        for checker in checkers:
            checker_config = self._create_checker_config(checker.name, config)
            checker_results = checker.check_function(
                target_function, test_file, checker_config
            )
            results.extend(checker_results)

        return results

    def _create_checker_config(
        self, checker_name: str, config: Dict[str, Any]
    ) -> CheckerConfig:
        """グローバル設定からチェッカー設定を作成します。

        Args:
            checker_name: チェッカー名
            config: グローバル設定

        Returns:
            チェッカー設定

        """
        checker_config = config.get(checker_name, {})

        return CheckerConfig(
            name=checker_name,
            enabled=checker_config.get("enabled", True),
            config=checker_config.get("config", {}),
        )
