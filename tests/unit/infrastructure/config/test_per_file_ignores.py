"""Test per-file ignores functionality."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from pytestee.infrastructure.config.settings import ConfigManager


class TestPerFileIgnores:
    """Test per-file ignores configuration (ruff-like)."""

    def test_get_file_specific_ignores_no_config(self) -> None:
        """Test that empty list is returned when no per-file ignores are defined."""
        config_manager = ConfigManager()
        config_manager._config = {
            "select": ["PTCM001", "PTAS001"],
            "ignore": [],
            "per_file_ignores": {}
        }

        file_path = Path("tests/unit/test_example.py")
        result = config_manager.get_file_specific_ignores(file_path)

        assert result == []

    def test_get_file_specific_ignores_exact_match(self) -> None:
        """Test file-specific ignores with exact file match."""
        config_manager = ConfigManager()
        config_manager._config = {
            "per_file_ignores": {
                "__init__.py": ["E402"],
                "tests/unit/test_example.py": ["PTCM001", "PTAS001"]
            }
        }

        file_path = Path("tests/unit/test_example.py")
        result = config_manager.get_file_specific_ignores(file_path)

        assert result == ["PTCM001", "PTAS001"]

        # Different file should not match
        other_file = Path("tests/integration/test_other.py")
        result = config_manager.get_file_specific_ignores(other_file)
        assert result == []

    def test_get_file_specific_ignores_wildcard_pattern(self) -> None:
        """Test file-specific ignores with wildcard patterns."""
        config_manager = ConfigManager()
        config_manager._config = {
            "per_file_ignores": {
                "tests/**": ["PTCM003"],
                "**/docs/*": ["PTAS005"],
                "**/__init__.py": ["E402"]
            }
        }

        # Should match tests/** pattern
        tests_file = Path("tests/unit/test_example.py")
        result = config_manager.get_file_specific_ignores(tests_file)
        assert "PTCM003" in result

        # Should match __init__.py pattern
        init_file = Path("src/mymodule/__init__.py")
        result = config_manager.get_file_specific_ignores(init_file)
        assert result == ["E402"]

        # Should match docs pattern (note: docs/index.py doesn't match **/docs/* pattern)
        docs_file = Path("project/docs/index.py")
        result = config_manager.get_file_specific_ignores(docs_file)
        assert result == ["PTAS005"]

    def test_get_file_specific_ignores_string_input(self) -> None:
        """Test file-specific ignores with string input (not list)."""
        config_manager = ConfigManager()
        config_manager._config = {
            "per_file_ignores": {
                "**/conftest.py": "PTCM001",  # Single string instead of list
                "tests/**": ["PTAS005"]
            }
        }

        file_path = Path("tests/conftest.py")
        result = config_manager.get_file_specific_ignores(file_path)

        # Should include both the string rule and the pattern match
        assert "PTCM001" in result
        assert "PTAS005" in result

    def test_matches_file_pattern_various_patterns(self) -> None:
        """Test file pattern matching with various patterns."""
        config_manager = ConfigManager()

        # Exact file match
        assert config_manager._matches_file_pattern("__init__.py", "__init__.py")
        assert not config_manager._matches_file_pattern("test.py", "__init__.py")

        # Directory wildcard
        assert config_manager._matches_file_pattern("tests/unit/test_file.py", "tests/**")
        assert config_manager._matches_file_pattern("tests/integration/deep/test_file.py", "tests/**")
        assert not config_manager._matches_file_pattern("src/main.py", "tests/**")

        # Any directory pattern with filename
        assert config_manager._matches_file_pattern("src/tests/unit/test_file.py", "**/test_*.py")
        assert config_manager._matches_file_pattern("tests/test_file.py", "**/test_*.py")
        assert not config_manager._matches_file_pattern("tests/main.py", "**/test_*.py")

        # Any directory pattern with specific file
        assert config_manager._matches_file_pattern("src/mymodule/__init__.py", "**/__init__.py")
        assert config_manager._matches_file_pattern("tests/unit/__init__.py", "**/__init__.py")

    def test_is_rule_enabled_for_file_with_ignores(self) -> None:
        """Test rule enablement check with file-specific ignores."""
        config_manager = ConfigManager()
        config_manager._config = {
            "select": ["PTCM001", "PTAS001", "PTAS005"],
            "ignore": [],
            "per_file_ignores": {
                "tests/unit/**": ["PTCM001"],
                "**/__init__.py": ["PTAS005"],
                "**/conftest.py": ["PTAS001", "PTAS005"]
            }
        }

        # Unit test file should have PTCM001 ignored
        unit_file = Path("tests/unit/test_example.py")
        assert not config_manager.is_rule_enabled_for_file("PTCM001", unit_file)  # Ignored
        assert config_manager.is_rule_enabled_for_file("PTAS001", unit_file)      # Not ignored
        assert config_manager.is_rule_enabled_for_file("PTAS005", unit_file)      # Not ignored

        # __init__.py files should have PTAS005 ignored
        init_file = Path("src/mymodule/__init__.py")
        assert config_manager.is_rule_enabled_for_file("PTCM001", init_file)      # Not ignored
        assert config_manager.is_rule_enabled_for_file("PTAS001", init_file)      # Not ignored
        assert not config_manager.is_rule_enabled_for_file("PTAS005", init_file)  # Ignored

        # conftest.py should have multiple rules ignored
        conftest_file = Path("tests/conftest.py")
        assert config_manager.is_rule_enabled_for_file("PTCM001", conftest_file)  # Not ignored (unit pattern doesn't match conftest.py exactly)
        assert not config_manager.is_rule_enabled_for_file("PTAS001", conftest_file)  # Ignored
        assert not config_manager.is_rule_enabled_for_file("PTAS005", conftest_file)  # Ignored

        # Integration test should have no ignores
        integration_file = Path("tests/integration/test_example.py")
        assert config_manager.is_rule_enabled_for_file("PTCM001", integration_file)
        assert config_manager.is_rule_enabled_for_file("PTAS001", integration_file)
        assert config_manager.is_rule_enabled_for_file("PTAS005", integration_file)

    def test_is_rule_enabled_for_file_global_disabled(self) -> None:
        """Test that globally disabled rules remain disabled even if not in per-file ignores."""
        config_manager = ConfigManager()
        config_manager._config = {
            "select": ["PTCM001"],  # Only PTCM001 is globally enabled
            "ignore": [],
            "per_file_ignores": {
                "tests/**": ["PTCM001"]  # PTCM001 ignored in tests
            }
        }

        test_file = Path("tests/unit/test_example.py")

        # PTCM001 is globally enabled but ignored for this file
        assert not config_manager.is_rule_enabled_for_file("PTCM001", test_file)

        # PTAS001 is not globally enabled, so should be False regardless of per-file ignores
        assert not config_manager.is_rule_enabled_for_file("PTAS001", test_file)

    @patch('pathlib.Path.cwd')
    def test_get_file_specific_ignores_absolute_path_handling(self, mock_cwd: MagicMock) -> None:
        """Test handling of absolute paths and relative path conversion."""
        mock_cwd.return_value = Path("/project/root")

        config_manager = ConfigManager()
        config_manager._config = {
            "per_file_ignores": {
                "tests/unit/**": ["PTCM001"]
            }
        }

        # Test with absolute path that can be made relative
        absolute_file = Path("/project/root/tests/unit/test_example.py")
        result = config_manager.get_file_specific_ignores(absolute_file)
        assert result == ["PTCM001"]  # Should match pattern

        # Test with absolute path outside project root
        outside_file = Path("/other/project/tests/unit/test_example.py")
        result = config_manager.get_file_specific_ignores(outside_file)
        assert result == []  # Should not match pattern

