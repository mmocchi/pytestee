"""Use case for analyzing test files."""

from pathlib import Path
from typing import Any, Dict, List

from ..domain.interfaces import ICheckerRegistry, IConfigManager, ITestRepository
from ..domain.models import AnalysisResult, CheckResult, CheckSeverity, TestFile


class AnalyzeTestsUseCase:
    """Use case for analyzing test files and running quality checks."""

    def __init__(
        self,
        test_repository: ITestRepository,
        checker_registry: ICheckerRegistry,
        config_manager: IConfigManager
    ) -> None:
        self._test_repository = test_repository
        self._checker_registry = checker_registry
        self._config_manager = config_manager

    def execute(self, target_path: Path, config_overrides: Dict[str, Any] = None) -> AnalysisResult:
        """Execute the test analysis."""
        if config_overrides is None:
            config_overrides = {}

        # Load configuration
        config = self._config_manager.load_config()
        config.update(config_overrides)

        # Find test files
        test_file_paths = self._test_repository.find_test_files(target_path)

        if not test_file_paths:
            return AnalysisResult(
                total_files=0,
                total_tests=0,
                passed_checks=0,
                failed_checks=0,
                check_results=[]
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
                # Create error result for files that couldn't be parsed
                error_result = CheckResult(
                    checker_name="file_parser",
                    severity=CheckSeverity.ERROR,
                    message=f"Failed to parse file: {str(e)}",
                    file_path=file_path
                )
                all_results.append(error_result)

        # Count passed and failed checks
        passed_checks, failed_checks = self._count_results(all_results)

        return AnalysisResult(
            total_files=len(test_file_paths),
            total_tests=total_tests,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            check_results=all_results
        )

    def _analyze_test_file(self, test_file: TestFile, config: Dict[str, Any]) -> List[CheckResult]:
        """Analyze a single test file with all enabled checkers."""
        results = []

        # Get enabled checkers
        enabled_checkers = self._checker_registry.get_enabled_checkers(config)

        for checker in enabled_checkers:
            checker_config = self._config_manager.get_checker_config(checker.name)

            try:
                checker_results = checker.check(test_file, checker_config)
                results.extend(checker_results)
            except Exception as e:
                # Create error result for checker failures
                error_result = CheckResult(
                    checker_name=checker.name,
                    severity=CheckSeverity.ERROR,
                    message=f"Checker failed: {str(e)}",
                    file_path=test_file.path
                )
                results.append(error_result)

        return results

    def _count_results(self, results: List[CheckResult]) -> tuple[int, int]:
        """Count passed and failed checks."""
        passed = 0
        failed = 0

        for result in results:
            if result.severity == CheckSeverity.INFO:
                passed += 1
            else:
                failed += 1

        return passed, failed
