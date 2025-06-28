"""File repository implementation."""

import fnmatch
from pathlib import Path
from typing import Optional

from pytestee.domain.interfaces import ITestRepository
from pytestee.domain.models import TestFile
from pytestee.infrastructure.ast_parser import ASTParser


class FileRepository(ITestRepository):
    """Repository for accessing test files from filesystem."""

    def __init__(
        self,
        exclude_patterns: Optional[list[str]] = None,
    ) -> None:
        """ファイルリポジトリを初期化します。

        Args:
            exclude_patterns: 除外するファイルパターンのリスト

        """
        self._parser = ASTParser()
        self._exclude_patterns = exclude_patterns or []

    def find_test_files(self, path: Path) -> list[Path]:
        """指定されたパス内のすべてのテストファイルを検索します。

        Args:
            path: 検索対象のディレクトリパス

        Returns:
            発見されたテストファイルのパスリスト

        """
        test_files = []

        if path.is_file():
            if path.suffix == ".py" and self._should_include_file(path):
                test_files.append(path)
        elif path.is_dir():
            # Find all Python files first
            all_py_files = list(path.rglob("*.py"))

            # Filter based on include/exclude patterns
            test_files.extend(
                file_path for file_path in all_py_files
                if self._should_include_file(file_path)
            )

        return sorted(test_files)

    def load_test_file(self, file_path: Path) -> TestFile:
        """テストファイルを読み込み、解析します。

        Args:
            file_path: 読み込み対象のファイルパス

        Returns:
            解析されたテストファイル

        Raises:
            FileNotFoundError: ファイルが見つからない場合
            ValueError: テストファイルではない場合

        """
        if not file_path.exists():
            raise FileNotFoundError(f"Test file not found: {file_path}")

        if not file_path.suffix == ".py":
            raise ValueError(f"Not a test file: {file_path}")

        return self._parser.parse_file(file_path)

    def _is_test_file(self, file_path: Path) -> bool:
        """ファイルがテストファイルかどうかを判定します。

        Args:
            file_path: チェック対象のファイルパス

        Returns:
            テストファイルの場合True

        """
        if file_path.suffix != ".py":
            return False

        name = file_path.name

        # First check naming conventions
        if name.startswith("test_") or name.endswith("_test.py"):
            return True

        # Special case: conftest.py is not a test file (it's a configuration file)
        if name == "conftest.py":
            return False

        # For other files, check if they contain test functions
        try:
            test_file = self._parser.parse_file(file_path)
            return len(test_file.test_functions) > 0 or len(test_file.test_classes) > 0
        except Exception:
            # If parsing fails, fall back to naming convention
            return False

    def _should_include_file(self, file_path: Path) -> bool:
        """ファイルがexcludeパターンに基づいて含まれるべきかを判定します。

        Args:
            file_path: チェック対象のファイルパス

        Returns:
            ファイルを含めるべき場合True

        """
        file_name = file_path.name

        # Always exclude conftest.py files as they are configuration files, not test files
        if file_name == "conftest.py":
            return False

        if not self._exclude_patterns:
            return True

        # Check if file matches any exclude pattern
        matches_exclude = any(
            fnmatch.fnmatch(file_name, pattern) for pattern in self._exclude_patterns
        )

        # Also check full path patterns for exclude (e.g., "**/conftest.py")
        if not matches_exclude:
            relative_path = str(file_path)
            matches_exclude = any(
                fnmatch.fnmatch(relative_path, pattern) or
                fnmatch.fnmatch(file_path.as_posix(), pattern)
                for pattern in self._exclude_patterns
            )

        return not matches_exclude
