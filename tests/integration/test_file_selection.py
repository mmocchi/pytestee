"""Integration tests for file selection with include/exclude patterns."""

from pathlib import Path
from tempfile import TemporaryDirectory

from pytestee.adapters.repositories.file_repository import FileRepository


class TestFileSelectionIntegration:
    """Integration tests for file include/exclude functionality."""

    def test_exclude_conftest_files(self) -> None:
        """Test that conftest.py files can be excluded."""
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # Create test files
            (test_dir / "test_example.py").write_text("def test_foo(): pass")
            (test_dir / "conftest.py").write_text("# pytest config")
            (test_dir / "tests").mkdir()
            (test_dir / "tests" / "test_another.py").write_text("def test_bar(): pass")
            (test_dir / "tests" / "conftest.py").write_text("# pytest config")

            # Repository with conftest exclusion
            repo = FileRepository(
                exclude_patterns=["**/conftest.py"],
            )

            files = repo.find_test_files(test_dir)
            file_names = [f.name for f in files]

            # Should find all .py files except conftest
            assert "test_example.py" in file_names
            assert "test_another.py" in file_names
            assert "conftest.py" not in file_names

    def test_no_exclude_patterns(self) -> None:
        """Test that all .py files are found with no exclude patterns."""
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # Create various files
            (test_dir / "test_unit.py").write_text("def test_unit(): pass")
            (test_dir / "check_integration.py").write_text("def test_integration(): pass")
            (test_dir / "spec_feature.py").write_text("def test_feature(): pass")
            (test_dir / "example.py").write_text("def example(): pass")

            # Repository with no exclude patterns
            repo = FileRepository(
                exclude_patterns=[],
            )

            files = repo.find_test_files(test_dir)
            file_names = sorted([f.name for f in files])

            # Should find all .py files
            assert file_names == ["check_integration.py", "example.py", "spec_feature.py", "test_unit.py"]

    def test_exclude_directory_pattern(self) -> None:
        """Test excluding entire directories."""
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # Create directory structure
            (test_dir / "tests").mkdir()
            (test_dir / "tests" / "test_main.py").write_text("def test_main(): pass")
            (test_dir / "tests" / "fixtures").mkdir()
            (test_dir / "tests" / "fixtures" / "test_fixture.py").write_text("def test_fixture(): pass")
            (test_dir / "tests" / "integration").mkdir()
            (test_dir / "tests" / "integration" / "test_integration.py").write_text("def test_integration(): pass")

            # Repository excluding fixtures and integration directories
            repo = FileRepository(
                exclude_patterns=["**/fixtures/**", "**/integration/**"],
            )

            files = repo.find_test_files(test_dir)
            file_paths = [str(f.relative_to(test_dir)) for f in files]

            # Should only find main test
            assert len(files) == 1
            assert "tests/test_main.py" in file_paths
            assert "fixtures" not in str(files[0])
            assert "integration" not in str(files[0])

    def test_complex_exclude_patterns(self) -> None:
        """Test complex exclude patterns."""
        with TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # Create files
            (test_dir / "test_unit.py").write_text("def test_unit(): pass")
            (test_dir / "test_integration.py").write_text("def test_integration(): pass")
            (test_dir / "test_e2e.py").write_text("def test_e2e(): pass")
            (test_dir / "test_skip_this.py").write_text("def test_skip(): pass")
            (test_dir / "test_wip_feature.py").write_text("def test_wip(): pass")

            # Repository with multiple exclude patterns
            repo = FileRepository(
                exclude_patterns=["*_integration.py", "*_e2e.py", "test_skip_*.py", "test_wip_*.py"],
            )

            files = repo.find_test_files(test_dir)
            file_names = [f.name for f in files]

            # Should only find unit test
            assert len(files) == 1
            assert file_names == ["test_unit.py"]
