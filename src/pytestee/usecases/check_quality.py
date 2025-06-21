"""Use case for quality checking operations."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..domain.interfaces import IChecker, ITestRepository
from ..domain.models import CheckerConfig, CheckResult


class CheckQualityUseCase:
    """Use case for running specific quality checks on test files."""

    def __init__(self, test_repository: ITestRepository) -> None:
        self._test_repository = test_repository

    def check_single_file(
        self,
        file_path: Path,
        checkers: List[IChecker],
        config: Optional[Dict[str, Any]] = None
    ) -> List[CheckResult]:
        """Check a single test file with specified checkers."""
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
        config: Optional[Dict[str, Any]] = None
    ) -> List[CheckResult]:
        """Check a specific test function with specified checkers."""
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
            raise ValueError(f"Test function '{function_name}' not found in {file_path}")

        # Run all checkers on the specific function
        results = []
        for checker in checkers:
            checker_config = self._create_checker_config(checker.name, config)
            checker_results = checker.check_function(target_function, test_file, checker_config)
            results.extend(checker_results)

        return results

    def _create_checker_config(self, checker_name: str, config: Dict[str, Any]) -> CheckerConfig:
        """Create a checker configuration from global config."""
        checker_config = config.get(checker_name, {})

        return CheckerConfig(
            name=checker_name,
            enabled=checker_config.get("enabled", True),
            config=checker_config.get("config", {})
        )
