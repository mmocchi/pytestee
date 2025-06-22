"""File repository implementation."""

from pathlib import Path
from typing import List

from pytestee.domain.interfaces import ITestRepository
from pytestee.domain.models import TestFile
from pytestee.infrastructure.ast_parser import ASTParser


class FileRepository(ITestRepository):
    """Repository for accessing test files from filesystem."""

    def __init__(self) -> None:
        """ファイルリポジトリを初期化します。"""
        self._parser = ASTParser()

    def find_test_files(self, path: Path) -> List[Path]:
        """指定されたパス内のすべてのテストファイルを検索します。

        Args:
            path: 検索対象のディレクトリパス

        Returns:
            発見されたテストファイルのパスリスト

        """
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

        if not self._is_test_file(file_path):
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
        return name.startswith("test_") or name.endswith("_test.py")
