"""Integration tests for directory-specific rule configuration."""

import os
import tempfile
from pathlib import Path

import pytest

from pytestee.adapters.cli.handlers.check_handler import CheckCommandHandler
from pytestee.adapters.repositories.file_repository import FileRepository
from pytestee.infrastructure.config.settings import ConfigManager


class TestDirectorySpecificRulesIntegration:
    """Integration tests for directory-specific rule configuration."""

    def test_directory_specific_rules_with_real_files(self) -> None:
        """Test directory-specific rules with actual test files."""
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
    # Arrange
    value = 1

    # Act
    result = value + 1

    # Assert
    assert result == 2
""")

            integration_test_file = integration_dir / "test_integration_example.py"
            integration_test_file.write_text("""
def test_integration_function():
    # This test doesn't follow AAA pattern
    value = 1
    result = value + 1
    assert result == 2
""")

            # Create config file with directory-specific rules
            config_file = temp_path / ".pytestee.toml"
            config_file.write_text("""
# Global configuration
select = ["PTCM003", "PTAS005"]

[rules.PTCM003]
require_comments = false
allow_gwt = true

[rules.PTAS005]
min_asserts = 1
max_asserts = 3

# Directory-specific rules
[per_directory_rules."tests/unit"]
select = ["PTCM001"]  # Stricter comment requirements for unit tests

[per_directory_rules."tests/unit".rules.PTCM001]
require_comments = true

[per_directory_rules."tests/integration"]
select = ["PTAS005"]  # Only assertion count checks for integration tests
ignore = ["PTCM003"]

[per_directory_rules."tests/integration".rules.PTAS005]
min_asserts = 1
max_asserts = 5  # More lenient for integration tests
""")

            # Initialize components
            config_manager = ConfigManager()
            config_manager.load_config(config_file)

            file_repository = FileRepository(config_manager.get_exclude_patterns())

            # Test unit directory rules
            unit_test_files = file_repository.find_test_files(unit_dir)
            assert len(unit_test_files) == 1

            unit_test_file_obj = file_repository.load_test_file(unit_test_files[0])

            # Check that unit tests use stricter comment rules
            assert config_manager.is_rule_enabled_for_file("PTCM001", unit_test_file_obj.path)
            assert not config_manager.is_rule_enabled_for_file("PTCM003", unit_test_file_obj.path)
            assert not config_manager.is_rule_enabled_for_file("PTAS005", unit_test_file_obj.path)

            unit_ptcm001_config = config_manager.get_rule_config_for_file("PTCM001", unit_test_file_obj.path)
            assert unit_ptcm001_config["require_comments"] is True

            # Test integration directory rules
            integration_test_files = file_repository.find_test_files(integration_dir)
            assert len(integration_test_files) == 1

            integration_test_file_obj = file_repository.load_test_file(integration_test_files[0])

            # Check that integration tests use lenient rules
            assert not config_manager.is_rule_enabled_for_file("PTCM001", integration_test_file_obj.path)
            assert not config_manager.is_rule_enabled_for_file("PTCM003", integration_test_file_obj.path)  # Ignored
            assert config_manager.is_rule_enabled_for_file("PTAS005", integration_test_file_obj.path)

            integration_ptas005_config = config_manager.get_rule_config_for_file("PTAS005", integration_test_file_obj.path)
            assert integration_ptas005_config["max_asserts"] == 5
            assert integration_ptas005_config["min_asserts"] == 1

    def test_hierarchical_directory_rules(self) -> None:
        """Test hierarchical directory-specific rule inheritance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create nested directory structure
            nested_dir = temp_path / "tests" / "unit" / "deep" / "nested"
            nested_dir.mkdir(parents=True)

            # Create test file
            test_file = nested_dir / "test_nested.py"
            test_file.write_text("""
def test_nested_function():
    assert True
""")

            # Create config with hierarchical rules
            config_file = temp_path / ".pytestee.toml"
            config_file.write_text("""
select = ["PTCM003", "PTAS005"]

# Broad pattern
[per_directory_rules."tests/**"]
select = ["PTCM001", "PTAS001"]

[per_directory_rules."tests/**".rules.PTAS001]
min_asserts = 1

# More specific pattern (should override)
[per_directory_rules."tests/unit/deep"]
select = ["PTCM002", "PTAS002"]

[per_directory_rules."tests/unit/deep".rules.PTAS002]
max_asserts = 2
""")

            # Initialize components
            config_manager = ConfigManager()
            config_manager.load_config(config_file)

            file_repository = FileRepository(config_manager.get_exclude_patterns())

            # Load test file
            test_files = file_repository.find_test_files(nested_dir)
            assert len(test_files) == 1

            test_file_obj = file_repository.load_test_file(test_files[0])

            # More specific pattern should win
            assert not config_manager.is_rule_enabled_for_file("PTCM001", test_file_obj.path)  # From broad pattern
            assert config_manager.is_rule_enabled_for_file("PTCM002", test_file_obj.path)     # From specific pattern
            assert not config_manager.is_rule_enabled_for_file("PTAS001", test_file_obj.path)  # From broad pattern
            assert config_manager.is_rule_enabled_for_file("PTAS002", test_file_obj.path)     # From specific pattern

            # Config should be from more specific pattern
            ptas002_config = config_manager.get_rule_config_for_file("PTAS002", test_file_obj.path)
            assert ptas002_config["max_asserts"] == 2

    def test_end_to_end_with_check_command(self) -> None:
        """Test end-to-end directory-specific rules with check command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files with different patterns
            unit_dir = temp_path / "tests" / "unit"
            unit_dir.mkdir(parents=True)

            # Unit test with good AAA pattern
            unit_good_file = unit_dir / "test_good_unit.py"
            unit_good_file.write_text("""
def test_good_unit_function():
    # Arrange
    value = 1

    # Act
    result = value + 1

    # Assert
    assert result == 2
""")

            # Unit test with bad pattern (should be caught by stricter rules)
            unit_bad_file = unit_dir / "test_bad_unit.py"
            unit_bad_file.write_text("""
def test_bad_unit_function():
    value = 1
    result = value + 1
    assert result == 2
""")

            e2e_dir = temp_path / "tests" / "e2e"
            e2e_dir.mkdir(parents=True)

            # E2E test that would fail unit test rules but should pass E2E rules
            e2e_file = e2e_dir / "test_e2e.py"
            e2e_file.write_text("""
def test_e2e_function():
    value = 1
    result = value + 1
    assert result == 2
""")

            # Create config with directory-specific rules
            config_file = temp_path / ".pytestee.toml"
            config_file.write_text("""
# Global rules
select = ["PTCM003"]

# Strict rules for unit tests
[per_directory_rules."tests/unit"]
select = ["PTCM001"]  # Require AAA comments

[per_directory_rules."tests/unit".rules.PTCM001]
require_comments = true

# Lenient rules for E2E tests
[per_directory_rules."tests/e2e"]
select = ["PTAS005"]  # Only check assertion count

[per_directory_rules."tests/e2e".rules.PTAS005]
min_asserts = 1
max_asserts = 10
""")

            # Initialize components
            config_manager = ConfigManager()
            config_manager.load_config(config_file)

            # Change to temp directory to make relative paths work
            original_cwd = str(Path.cwd())
            try:
                os.chdir(temp_dir)

                # Test unit directory (should find violations)
                handler = CheckCommandHandler()
                unit_result = handler.execute(unit_dir, "console", False, False, None, config_file)

                # Should find issues in bad unit test but not good unit test
                unit_failures = [r for r in unit_result.check_results if hasattr(r, 'severity')]
                unit_violations = [f for f in unit_failures if f.file_path.name == "test_bad_unit.py"]
                assert len(unit_violations) > 0  # Should find PTCM001 violations

                # Test E2E directory (should pass)
                e2e_result = handler.execute(e2e_dir, "console", False, False, None, config_file)

                # Should not find comment-related issues (only checking PTAS005)
                e2e_failures = [r for r in e2e_result.check_results if hasattr(r, 'severity')]
                assert len(e2e_failures) == 0  # Should pass PTAS005 (has 1 assert)

            finally:
                os.chdir(original_cwd)

    def test_config_merging_with_existing_fixtures(self) -> None:
        """Test directory-specific rules with existing test fixtures."""
        # Use existing fixtures
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        if not fixtures_dir.exists():
            pytest.skip("Fixtures directory not found")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create config with directory-specific rules for fixtures
            config_file = temp_path / ".pytestee.toml"
            config_file.write_text("""
select = ["PTCM003", "PTAS005"]

# Special rules for fixtures (if they were in a fixtures directory)
[per_directory_rules."**/fixtures"]
select = ["PTAS001", "PTAS002", "PTAS003", "PTAS004", "PTAS005"]
ignore = ["PTCM003"]  # Don't check comment patterns in fixtures

[per_directory_rules."**/fixtures".rules.PTAS005]
min_asserts = 0
max_asserts = 10
""")

            # Initialize components
            config_manager = ConfigManager()
            config_manager.load_config(config_file)

            # Test with a fixture file path
            fake_fixture_path = Path("tests/fixtures/good_aaa_test.py")

            # Should use fixture-specific rules
            assert config_manager.is_rule_enabled_for_file("PTAS001", fake_fixture_path)
            assert not config_manager.is_rule_enabled_for_file("PTCM003", fake_fixture_path)  # Ignored

            ptas005_config = config_manager.get_rule_config_for_file("PTAS005", fake_fixture_path)
            assert ptas005_config["min_asserts"] == 0
            assert ptas005_config["max_asserts"] == 10

