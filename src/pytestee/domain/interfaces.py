"""Domain interfaces for pytestee."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import AnalysisResult, CheckerConfig, CheckResult, TestFile, TestFunction


class ITestRepository(ABC):
    """Interface for test file repository."""

    @abstractmethod
    def find_test_files(self, path: Path) -> List[Path]:
        """Find all test files in the given path."""
        pass

    @abstractmethod
    def load_test_file(self, file_path: Path) -> TestFile:
        """Load and parse a test file."""
        pass


class IChecker(ABC):
    """Interface for test quality checkers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this checker."""
        pass

    @abstractmethod
    def check(self, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """Check a test file and return results."""
        pass

    @abstractmethod
    def check_function(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """Check a specific test function and return results."""
        pass


class IPresenter(ABC):
    """Interface for presenting analysis results."""

    @abstractmethod
    def present(self, result: AnalysisResult) -> None:
        """Present the analysis result."""
        pass


class IConfigManager(ABC):
    """Interface for configuration management."""

    @abstractmethod
    def load_config(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """Load configuration from file or defaults."""
        pass

    @abstractmethod
    def get_checker_config(self, checker_name: str) -> CheckerConfig:
        """Get configuration for a specific checker."""
        pass

    @abstractmethod
    def get_global_config(self) -> Dict[str, Any]:
        """Get global configuration."""
        pass


class ICheckerRegistry(ABC):
    """Interface for checker registry."""

    @abstractmethod
    def register(self, checker: IChecker) -> None:
        """Register a checker."""
        pass

    @abstractmethod
    def get_checker(self, name: str) -> Optional[IChecker]:
        """Get a checker by name."""
        pass

    @abstractmethod
    def get_all_checkers(self) -> List[IChecker]:
        """Get all registered checkers."""
        pass

    @abstractmethod
    def get_enabled_checkers(self, config: Dict[str, Any]) -> List[IChecker]:
        """Get all enabled checkers based on configuration."""
        pass
