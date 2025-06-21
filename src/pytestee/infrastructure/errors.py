"""Error handling for pytestee infrastructure."""

from pathlib import Path


class PytesteeError(Exception):
    """Base exception for pytestee errors."""

    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


class ParseError(PytesteeError):
    """Error when parsing test files fails."""

    def __init__(self, file_path: Path, original_error: Exception) -> None:
        message = f"Failed to parse file {file_path}: {original_error}"
        super().__init__(message, exit_code=2)
        self.file_path = file_path
        self.original_error = original_error


class CheckerError(PytesteeError):
    """Error when a checker fails to execute."""

    def __init__(self, checker_name: str, original_error: Exception) -> None:
        message = f"Checker '{checker_name}' failed: {original_error}"
        super().__init__(message, exit_code=3)
        self.checker_name = checker_name
        self.original_error = original_error


class ConfigurationError(PytesteeError):
    """Error in configuration setup."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Configuration error: {message}", exit_code=4)
