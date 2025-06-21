"""Domain models for pytestee."""

import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class CheckSeverity(Enum):
    """Severity levels for check results."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class PatternType(Enum):
    """Test pattern types."""
    AAA = "aaa"  # Arrange, Act, Assert
    GWT = "gwt"  # Given, When, Then


@dataclass
class TestFunction:
    """Represents a test function in the code."""
    name: str
    lineno: int
    col_offset: int
    end_lineno: Optional[int]
    end_col_offset: Optional[int]
    body: List[ast.stmt]
    docstring: Optional[str] = None
    decorators: List[str] = None

    def __post_init__(self) -> None:
        if self.decorators is None:
            self.decorators = []


@dataclass
class TestFile:
    """Represents a test file containing test functions."""
    path: Path
    content: str
    ast_tree: ast.AST
    test_functions: List[TestFunction]

    @property
    def relative_path(self) -> str:
        """Get relative path as string."""
        return str(self.path)


@dataclass
class CheckResult:
    """Result of a quality check."""
    checker_name: str
    severity: CheckSeverity
    message: str
    file_path: Path
    line_number: Optional[int] = None
    column: Optional[int] = None
    function_name: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.context is None:
            self.context = {}


@dataclass
class AnalysisResult:
    """Result of analyzing test files."""
    total_files: int
    total_tests: int
    passed_checks: int
    failed_checks: int
    check_results: List[CheckResult]

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        total = self.passed_checks + self.failed_checks
        if total == 0:
            return 100.0
        return (self.passed_checks / total) * 100.0

    @property
    def has_errors(self) -> bool:
        """Check if there are any error-level issues."""
        return any(result.severity == CheckSeverity.ERROR for result in self.check_results)

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warning-level issues."""
        return any(result.severity == CheckSeverity.WARNING for result in self.check_results)


@dataclass
class CheckerConfig:
    """Configuration for checkers."""
    name: str
    enabled: bool = True
    config: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.config is None:
            self.config = {}
