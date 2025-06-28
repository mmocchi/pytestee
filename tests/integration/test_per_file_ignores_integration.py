"""Integration tests for per-file ignores configuration."""

import os
import tempfile
from pathlib import Path

from pytestee.adapters.cli.handlers.check_handler import CheckCommandHandler
from pytestee.adapters.repositories.file_repository import FileRepository
from pytestee.infrastructure.config.settings import ConfigManager


class TestPerFileIgnoresIntegration:
    """Integration tests for per-file ignores configuration."""

    def test_per_file_ignores_with_real_files(self) -> None:
        """Test per-file ignores with actual test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test directory structure
            unit_dir = temp_path / "tests" / "unit"
            integration_dir = temp_path / "tests" / "integration"
            unit_dir.mkdir(parents=True)
            integration_dir.mkdir(parents=True)

            # Create test files
            unit_test_file = unit_dir / "test_unit_example.py"
            unit_test_file.write_text("""
def test_unit_function():
    # This test doesn't follow AAA pattern but should be ignored
    value = 1
    result = value + 1
    assert result == 2
""")

            integration_test_file = integration_dir / "test_integration_example.py"
            integration_test_file.write_text("""
def test_integration_function():
    # This test doesn't follow AAA pattern and should be flagged
    value = 1
    result = value + 1
    assert result == 2
""")

            # Create conftest.py that would normally trigger assertion rules
            conftest_file = unit_dir / "conftest.py"
            conftest_file.write_text("""
# This file has no test functions but might trigger naming rules
def helper_function():
    pass
""")

            # Create config file with per-file ignores
            config_file = temp_path / ".pytestee.toml"
            config_file.write_text("""
# Global configuration - enable strict rules
select = ["PTCM001", "PTAS005"]

[rules.PTCM001]
require_comments = true

[rules.PTAS005]
min_asserts = 1
max_asserts = 3

# Per-file ignores (ruff-like)
[per_file_ignores]
"tests/unit/**" = ["PTCM001"]  # Ignore comment requirements in unit tests
"**/conftest.py" = ["PTCM001", "PTAS005"]  # Ignore multiple rules in conftest files
""")

            # Initialize components
            config_manager = ConfigManager()
            config_manager.load_config(config_file)

            file_repository = FileRepository(config_manager.get_exclude_patterns())

            # Test unit directory rules
            unit_test_files = file_repository.find_test_files(unit_dir)
            assert len(unit_test_files) == 1  # Only the .py test file, not conftest.py

            unit_test_file_obj = file_repository.load_test_file(unit_test_files[0])

            # Check that unit tests have PTCM001 ignored but PTAS005 still enabled
            assert not config_manager.is_rule_enabled_for_file("PTCM001", unit_test_file_obj.path)  # Ignored
            assert config_manager.is_rule_enabled_for_file("PTAS005", unit_test_file_obj.path)      # Not ignored

            # Test integration directory rules (no ignores)
            integration_test_files = file_repository.find_test_files(integration_dir)
            assert len(integration_test_files) == 1

            integration_test_file_obj = file_repository.load_test_file(integration_test_files[0])

            # Check that integration tests have all rules enabled
            assert config_manager.is_rule_enabled_for_file("PTCM001", integration_test_file_obj.path)  # Not ignored
            assert config_manager.is_rule_enabled_for_file("PTAS005", integration_test_file_obj.path)  # Not ignored

            # Test conftest.py rules (multiple ignores)
            conftest_ignores = config_manager.get_file_specific_ignores(conftest_file)
            assert "PTCM001" in conftest_ignores
            assert "PTAS005" in conftest_ignores

    def test_init_files_ignores(self) -> None:
        """Test that __init__.py files can have specific ignores."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create package structure with __init__.py files
            package_dir = temp_path / "src" / "mypackage"
            package_dir.mkdir(parents=True)

            init_file = package_dir / "__init__.py"
            init_file.write_text("""
# This __init__.py file might not follow normal test patterns
from .module import function

def exported_function():
    return function()
""")

            regular_file = package_dir / "module.py"
            regular_file.write_text("""
def test_function():
    assert True
""")

            # Create config that ignores import-related rules in __init__.py
            config_file = temp_path / ".pytestee.toml"
            config_file.write_text("""
select = ["PTCM001", "PTAS005", "PTVL001"]

[per_file_ignores]
"**/__init__.py" = ["PTVL001"]  # Ignore private access rules in __init__.py files
""")

            config_manager = ConfigManager()
            config_manager.load_config(config_file)

            # __init__.py should have PTVL001 ignored
            assert not config_manager.is_rule_enabled_for_file("PTVL001", init_file)
            assert config_manager.is_rule_enabled_for_file("PTCM001", init_file)
            assert config_manager.is_rule_enabled_for_file("PTAS005", init_file)

            # Regular files should have all rules enabled
            assert config_manager.is_rule_enabled_for_file("PTVL001", regular_file)
            assert config_manager.is_rule_enabled_for_file("PTCM001", regular_file)
            assert config_manager.is_rule_enabled_for_file("PTAS005", regular_file)

    def test_multiple_directory_patterns(self) -> None:
        """Test complex directory patterns like ruff's **/{tests,docs,tools}/*."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create multiple directory structures
            tests_dir = temp_path / "tests"
            docs_dir = temp_path / "docs"
            tools_dir = temp_path / "tools"
            src_dir = temp_path / "src"

            for dir_path in [tests_dir, docs_dir, tools_dir, src_dir]:
                dir_path.mkdir(parents=True)

            # Create files in each directory
            test_file = tests_dir / "test_example.py"
            doc_file = docs_dir / "example.py"
            tool_file = tools_dir / "build.py"
            src_file = src_dir / "main.py"

            for file_path in [test_file, doc_file, tool_file, src_file]:
                file_path.write_text("def test_function(): assert True")

            # Create config with multiple directory pattern
            config_file = temp_path / ".pytestee.toml"
            config_file.write_text("""
select = ["PTCM001", "PTAS005"]

[per_file_ignores]
"tests/**" = ["PTCM001"]   # Ignore comment rules in tests
"docs/**" = ["PTCM001"]    # Ignore comment rules in docs
"tools/**" = ["PTCM001"]   # Ignore comment rules in tools
""")

            config_manager = ConfigManager()
            config_manager.load_config(config_file)

            # Files in tests, docs, tools should have PTCM001 ignored
            assert not config_manager.is_rule_enabled_for_file("PTCM001", test_file)
            assert not config_manager.is_rule_enabled_for_file("PTCM001", doc_file)
            assert not config_manager.is_rule_enabled_for_file("PTCM001", tool_file)

            # Files in src should have all rules enabled
            assert config_manager.is_rule_enabled_for_file("PTCM001", src_file)

            # PTAS005 should be enabled everywhere (not ignored)
            assert config_manager.is_rule_enabled_for_file("PTAS005", test_file)
            assert config_manager.is_rule_enabled_for_file("PTAS005", doc_file)
            assert config_manager.is_rule_enabled_for_file("PTAS005", tool_file)
            assert config_manager.is_rule_enabled_for_file("PTAS005", src_file)

    def test_end_to_end_with_check_command(self) -> None:
        """Test end-to-end per-file ignores with check command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files with different patterns
            unit_dir = temp_path / "tests" / "unit"
            integration_dir = temp_path / "tests" / "integration"
            unit_dir.mkdir(parents=True)
            integration_dir.mkdir(parents=True)

            # Unit test without AAA comments (should be ignored)
            unit_test_file = unit_dir / "test_unit_example.py"
            unit_test_file.write_text("""
def test_unit_function():
    value = 1
    result = value + 1
    assert result == 2
""")

            # Integration test without AAA comments (should be flagged)
            integration_test_file = integration_dir / "test_integration_example.py"
            integration_test_file.write_text("""
def test_integration_function():
    value = 1
    result = value + 1
    assert result == 2
""")

            # Create config with per-file ignores
            config_file = temp_path / ".pytestee.toml"
            config_file.write_text("""
# Global rules - require AAA comments
select = ["PTCM001"]

[rules.PTCM001]
require_comments = true

# Per-file ignores
[per_file_ignores]
"tests/unit/**" = ["PTCM001"]  # Unit tests don't need AAA comments
""")

            # Initialize components
            config_manager = ConfigManager()
            config_manager.load_config(config_file)

            # Change to temp directory to make relative paths work
            original_cwd = str(Path.cwd())
            try:
                os.chdir(temp_dir)

                # Test unit directory (should pass due to ignores)
                handler = CheckCommandHandler()
                unit_result = handler.execute(unit_dir, "console", False, False, None, config_file)

                # Should find no violations (PTCM001 is ignored)
                unit_failures = [r for r in unit_result.check_results if hasattr(r, 'severity')]
                assert len(unit_failures) == 0  # No violations expected

                # Test integration directory (should find violations)
                integration_result = handler.execute(integration_dir, "console", False, False, None, config_file)

                # Should find PTCM001 violations (not ignored)
                integration_failures = [r for r in integration_result.check_results if hasattr(r, 'severity')]
                assert len(integration_failures) > 0  # Should find PTCM001 violations

            finally:
                os.chdir(original_cwd)

