"""File repository implementation."""

from pathlib import Path
from typing import List

from ...domain.interfaces import ITestRepository
from ...domain.models import TestFile
from ...infrastructure.ast_parser import ASTParser


class FileRepository(ITestRepository):
    """Repository for accessing test files from filesystem."""

    def __init__(self) -> None:
        self._parser = ASTParser()

    def find_test_files(self, path: Path) -> List[Path]:
        """Find all test files in the given path."""
        test_files = []

        if path.is_file():
            if self._is_test_file(path):
                test_files.append(path)
        elif path.is_dir():
            # Recursively find test files
            for pattern in ["test_*.py", "*_test.py"]:
                test_files.extend(path.rglob(pattern))

        return sorted(test_files)

    def load_test_file(self, file_path: Path) -> TestFile:
        """Load and parse a test file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Test file not found: {file_path}")

        if not self._is_test_file(file_path):
            raise ValueError(f"Not a test file: {file_path}")

        return self._parser.parse_file(file_path)

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if a file is a test file."""
        if file_path.suffix != ".py":
            return False

        name = file_path.name
        return name.startswith("test_") or name.endswith("_test.py")
