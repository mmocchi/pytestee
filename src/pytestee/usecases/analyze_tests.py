"""Use case for analyzing test files."""

from pathlib import Path
from typing import Any, Optional

from pytestee.domain.interfaces import (
    ICheckerRegistry,
    IConfigManager,
    ITestRepository,
)
from pytestee.domain.models import (
    AnalysisResult,
    CheckFailure,
    CheckResult,
    CheckSuccess,
    TestFile,
)
from pytestee.infrastructure.errors import CheckerError, ParseError


class AnalyzeTestsUseCase:
    """Use case for analyzing test files and running quality checks."""

    def __init__(
        self,
        test_repository: ITestRepository,
        checker_registry: ICheckerRegistry,
        config_manager: IConfigManager,
    ) -> None:
        """テスト分析ユースケースを初期化します。

        Args:
            test_repository: テストリポジトリインターフェース
            checker_registry: チェッカーレジストリインターフェース
            config_manager: 設定管理インターフェース

        """
        self._test_repository = test_repository
        self._checker_registry = checker_registry
        self._config_manager = config_manager

    def execute(
        self, target_path: Path, config_overrides: Optional[dict[str, Any]] = None
    ) -> AnalysisResult:
        """テスト分析を実行します。

        Args:
            target_path: 分析対象のパス
            config_overrides: 設定オーバーライド

        Returns:
            分析結果

        Raises:
            ParseError: ファイル解析エラー

        """
        if config_overrides is None:
            config_overrides = {}

        # Load configuration
        config = self._config_manager.load_config()

        # Apply overrides to the config manager
        if config_overrides:
            self._config_manager.apply_overrides(config_overrides)

        # Find test files
        test_file_paths = self._test_repository.find_test_files(target_path)

        if not test_file_paths:
            return AnalysisResult(
                total_files=0,
                total_tests=0,
                passed_checks=0,
                failed_checks=0,
                check_results=[],
            )

        # Load and analyze test files
        all_results = []
        total_tests = 0

        for file_path in test_file_paths:
            try:
                test_file = self._test_repository.load_test_file(file_path)
                total_tests += len(test_file.test_functions)

                file_results = self._analyze_test_file(test_file, config)
                all_results.extend(file_results)
            except Exception as e:
                # Log parse error and continue with other files
                raise ParseError(file_path, e) from e

        # Count passed and failed checks
        passed_checks, failed_checks = self._count_results(all_results)

        return AnalysisResult(
            total_files=len(test_file_paths),
            total_tests=total_tests,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            check_results=all_results,
        )

    def _analyze_test_file(
        self, test_file: TestFile, config: dict[str, Any]
    ) -> list[CheckResult]:
        """単一のテストファイルを有効なチェッカーで分析します。

        Args:
            test_file: テストファイル
            config: 設定

        Returns:
            チェック結果のリスト

        Raises:
            CheckerError: チェッカーエラー

        """
        results = []

        # Get all rule instances from registry
        all_rule_instances = self._checker_registry.get_all_rule_instances()

        # Run rules on each test function (with file-specific rule filtering)
        for test_function in test_file.test_functions:
            for rule_id, rule in all_rule_instances.items():
                # Check if rule is enabled for this specific file
                if rule.is_enabled_for_file(test_file, self._config_manager):
                    try:
                        # Use global checker config (no file-specific overrides needed)
                        checker_config = self._config_manager.get_checker_config(rule.name)
                        rule_result = rule.check(test_function, test_file, checker_config)
                        results.append(rule_result)
                    except Exception as e:
                        # Log rule error and continue with other rules
                        raise CheckerError(rule_id, e) from e

        # Run rules on each test class (with file-specific rule filtering)
        for test_class in test_file.test_classes:
            for rule_id, rule in all_rule_instances.items():
                # Check if rule is enabled for this specific file and has check_class method
                if rule.is_enabled_for_file(test_file, self._config_manager) and hasattr(rule, 'check_class'):
                    try:
                        # Use global checker config (no file-specific overrides needed)
                        checker_config = self._config_manager.get_checker_config(rule.name)
                        rule_result = rule.check_class(test_class, test_file, checker_config)
                        results.append(rule_result)
                    except Exception as e:
                        # Log rule error and continue with other rules
                        raise CheckerError(rule_id, e) from e

        return results

    def _count_results(self, results: list[CheckResult]) -> tuple[int, int]:
        """成功と失敗のチェック数をカウントします。

        Args:
            results: チェック結果のリスト

        Returns:
            成功数と失敗数のタプル

        """
        passed = 0
        failed = 0

        for result in results:
            if isinstance(result, CheckSuccess):
                passed += 1
            elif isinstance(result, CheckFailure):
                failed += 1

        return passed, failed
