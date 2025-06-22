"""Unit tests for FileRepository."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from pytestee.adapters.repositories.file_repository import FileRepository


class TestFileRepository:
    """Test cases for FileRepository."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.repo = FileRepository()
        self.repo_with_patterns = FileRepository(
            exclude_patterns=["**/conftest.py", "test_skip_*.py"],
        )

    def test_find_test_files_all_python_files(self) -> None:
        """Test finding all Python files by default."""
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # Create test files
            (test_dir / "test_example.py").write_text("def test_example(): pass")
            (test_dir / "check_something.py").write_text("def test_check(): pass")
            (test_dir / "helper.py").write_text("def helper(): pass")
            (test_dir / "example_test.py").write_text("def test_ex(): pass")

            # Test with directory - should find all .py files
            result = self.repo.find_test_files(test_dir)
            file_names = sorted([f.name for f in result])

            # Should include all .py files
            assert file_names == ["check_something.py", "example_test.py", "helper.py", "test_example.py"]

    def test_find_test_files_with_exclude_patterns(self) -> None:
        """Test finding test files with exclude patterns."""
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # Create test files
            (test_dir / "test_example.py").write_text("def test_example(): pass")
            (test_dir / "test_skip_this.py").write_text("def test_skip(): pass")
            (test_dir / "conftest.py").write_text("# pytest config")

            # Test with directory
            result = self.repo_with_patterns.find_test_files(test_dir)
            file_names = [f.name for f in result]

            # Should exclude conftest.py and test_skip_*.py but include all other .py files
            assert file_names == ["test_example.py"]

    def test_find_test_files_with_file_path(self) -> None:
        """Test finding test files when given a file path."""
        # Create temporary test files
        test_file = Path("test_temp.py")
        helper_file = Path("helper_temp.py")
        test_file.write_text("def test_example(): pass")
        helper_file.write_text("def helper(): pass")

        try:
            # Default repository should find any .py file
            result = self.repo.find_test_files(test_file)
            assert result == [test_file]

            result = self.repo.find_test_files(helper_file)
            assert result == [helper_file]

            # Repository with exclude patterns should still find it if not excluded
            result = self.repo_with_patterns.find_test_files(test_file)
            assert result == [test_file]

        finally:
            test_file.unlink()
            helper_file.unlink()

    def test_find_test_files_excludes_non_python_file(self) -> None:
        """Test that non-Python files are excluded."""
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # Create a non-Python file
            non_python_file = test_dir / "example.txt"
            non_python_file.write_text("Not a Python file")

            # Should not find non-Python file
            result = self.repo.find_test_files(non_python_file)
            assert result == []

    def test_should_include_file_method(self) -> None:
        """Test the _should_include_file method directly."""
        # Default repo (no excludes) should include everything
        assert self.repo._should_include_file(Path("test_example.py")) is True
        assert self.repo._should_include_file(Path("helper.py")) is True
        assert self.repo._should_include_file(Path("conftest.py")) is True

        # Repo with exclude patterns
        repo = self.repo_with_patterns
        # Any .py file not matching exclude patterns should be included
        assert repo._should_include_file(Path("test_example.py")) is True
        assert repo._should_include_file(Path("check_something.py")) is True
        assert repo._should_include_file(Path("helper.py")) is True
        assert repo._should_include_file(Path("any_file.py")) is True

        # Files matching exclude patterns should be excluded
        assert repo._should_include_file(Path("test_skip_this.py")) is False
        assert repo._should_include_file(Path("conftest.py")) is True  # conftest.py by itself doesn't match **/conftest.py when checked as file name only
        assert repo._should_include_file(Path("src/conftest.py")) is False  # This matches **/conftest.py pattern

    def test_load_test_file_error_handling(self) -> None:
        """Test error handling in load_test_file."""
        # Non-existent file
        with pytest.raises(FileNotFoundError):
            self.repo.load_test_file(Path("non_existent.py"))

        # Non-Python file
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            non_python = test_dir / "not_python.txt"
            non_python.write_text("Not a Python file")

            with pytest.raises(ValueError, match="Not a test file"):
                self.repo.load_test_file(non_python)
