"""Test directory-specific rule configuration functionality."""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from pytestee.infrastructure.config.settings import ConfigManager


class TestDirectorySpecificRules:
    """Test directory-specific rule configuration."""

    def test_get_directory_config_no_per_directory_rules(self) -> None:
        """Test that global config is returned when no per-directory rules are defined."""
        config_manager = ConfigManager()
        config_manager._config = {
            "select": ["PTCM001", "PTAS001"],
            "ignore": [],
            "rules": {"PTAS001": {"min_asserts": 1}},
            "per_directory_rules": {}
        }

        file_path = Path("tests/unit/test_example.py")
        result = config_manager.get_directory_config(file_path)

        assert result["select"] == ["PTCM001", "PTAS001"]
        assert result["ignore"] == []
        assert result["rules"]["PTAS001"]["min_asserts"] == 1

    def test_get_directory_config_with_exact_directory_match(self) -> None:
        """Test directory-specific config with exact directory pattern match."""
        config_manager = ConfigManager()
        config_manager._config = {
            "select": ["PTCM001", "PTAS001"],
            "ignore": [],
            "rules": {"PTAS001": {"min_asserts": 1}},
            "per_directory_rules": {
                "tests/unit": {
                    "select": ["PTCM002"],
                    "rules": {"PTAS001": {"min_asserts": 2}}
                }
            }
        }

        file_path = Path("tests/unit/test_example.py")
        result = config_manager.get_directory_config(file_path)

        # Should have directory-specific overrides
        assert result["select"] == ["PTCM002"]  # Overridden
        assert result["rules"]["PTAS001"]["min_asserts"] == 2  # Overridden

    def test_get_directory_config_with_wildcard_pattern(self) -> None:
        """Test directory-specific config with wildcard pattern matching."""
        config_manager = ConfigManager()
        config_manager._config = {
            "select": ["PTCM001"],
            "ignore": [],
            "rules": {"PTAS001": {"min_asserts": 1}},
            "per_directory_rules": {
                "tests/**": {
                    "ignore": ["PTCM001"],
                    "select": ["PTAS001"]
                }
            }
        }

        file_path = Path("tests/unit/integration/test_example.py")
        result = config_manager.get_directory_config(file_path)

        # Should match wildcard pattern
        assert result["select"] == ["PTAS001"]
        assert result["ignore"] == ["PTCM001"]

    def test_get_directory_config_multiple_patterns_specificity(self) -> None:
        """Test that more specific patterns override less specific ones."""
        config_manager = ConfigManager()
        config_manager._config = {
            "select": ["PTCM001"],
            "ignore": [],
            "rules": {"PTAS001": {"min_asserts": 1}},
            "per_directory_rules": {
                "tests/**": {
                    "select": ["PTAS001"],
                    "rules": {"PTAS001": {"min_asserts": 2}}
                },
                "tests/unit": {
                    "select": ["PTCM002"],
                    "rules": {"PTAS001": {"min_asserts": 3}}
                }
            }
        }

        file_path = Path("tests/unit/test_example.py")
        result = config_manager.get_directory_config(file_path)

        # More specific pattern (tests/unit) should win over less specific (tests/**)
        assert result["select"] == ["PTCM002"]
        assert result["rules"]["PTAS001"]["min_asserts"] == 3

    def test_matches_directory_pattern_exact_match(self) -> None:
        """Test exact directory pattern matching."""
        config_manager = ConfigManager()

        # Exact directory match
        assert config_manager._matches_directory_pattern("tests/unit/test_file.py", "tests/unit")
        assert not config_manager._matches_directory_pattern("tests/integration/test_file.py", "tests/unit")

    def test_matches_directory_pattern_wildcard(self) -> None:
        """Test wildcard directory pattern matching."""
        config_manager = ConfigManager()

        # Wildcard patterns
        assert config_manager._matches_directory_pattern("tests/unit/test_file.py", "tests/**")
        assert config_manager._matches_directory_pattern("tests/integration/deep/test_file.py", "tests/**")
        assert config_manager._matches_directory_pattern("src/tests/unit/test_file.py", "**/unit")
        assert not config_manager._matches_directory_pattern("src/main/test_file.py", "tests/**")

    def test_matches_directory_pattern_auto_wildcard(self) -> None:
        """Test that directory patterns automatically get /** appended."""
        config_manager = ConfigManager()

        # Should auto-append /** for directory-only patterns
        assert config_manager._matches_directory_pattern("tests/unit/test_file.py", "tests")
        assert config_manager._matches_directory_pattern("tests/unit/deep/test_file.py", "tests")

    def test_is_rule_enabled_for_file_global_only(self) -> None:
        """Test rule enablement check when only global config exists."""
        config_manager = ConfigManager()
        config_manager._config = {
            "select": ["PTCM001", "PTAS001"],
            "ignore": [],
            "per_directory_rules": {}
        }

        file_path = Path("tests/unit/test_example.py")

        assert config_manager.is_rule_enabled_for_file("PTCM001", file_path)
        assert config_manager.is_rule_enabled_for_file("PTAS001", file_path)
        assert not config_manager.is_rule_enabled_for_file("PTCM002", file_path)

    def test_is_rule_enabled_for_file_directory_specific(self) -> None:
        """Test rule enablement check with directory-specific config."""
        config_manager = ConfigManager()
        config_manager._config = {
            "select": ["PTCM001"],
            "ignore": [],
            "per_directory_rules": {
                "tests/unit": {
                    "select": ["PTCM002", "PTAS001"],
                    "ignore": ["PTCM001"]
                }
            }
        }

        unit_file = Path("tests/unit/test_example.py")
        integration_file = Path("tests/integration/test_example.py")

        # Unit test directory should use directory-specific rules
        assert not config_manager.is_rule_enabled_for_file("PTCM001", unit_file)  # Ignored
        assert config_manager.is_rule_enabled_for_file("PTCM002", unit_file)  # Selected
        assert config_manager.is_rule_enabled_for_file("PTAS001", unit_file)  # Selected

        # Integration test directory should use global rules
        assert config_manager.is_rule_enabled_for_file("PTCM001", integration_file)  # Global select
        assert not config_manager.is_rule_enabled_for_file("PTCM002", integration_file)  # Not in global select

    def test_get_rule_config_for_file_global_only(self) -> None:
        """Test rule config retrieval when only global config exists."""
        config_manager = ConfigManager()
        config_manager._config = {
            "rules": {
                "PTAS001": {"min_asserts": 1, "max_asserts": 5}
            },
            "per_directory_rules": {}
        }

        file_path = Path("tests/unit/test_example.py")
        config = config_manager.get_rule_config_for_file("PTAS001", file_path)

        assert config == {"min_asserts": 1, "max_asserts": 5}

    def test_get_rule_config_for_file_directory_specific(self) -> None:
        """Test rule config retrieval with directory-specific overrides."""
        config_manager = ConfigManager()
        config_manager._config = {
            "rules": {
                "PTAS001": {"min_asserts": 1, "max_asserts": 5}
            },
            "per_directory_rules": {
                "tests/unit": {
                    "rules": {
                        "PTAS001": {"min_asserts": 2}  # Override min_asserts only
                    }
                }
            }
        }

        unit_file = Path("tests/unit/test_example.py")
        integration_file = Path("tests/integration/test_example.py")

        # Unit test should have directory-specific override
        unit_config = config_manager.get_rule_config_for_file("PTAS001", unit_file)
        assert unit_config == {"min_asserts": 2, "max_asserts": 5}  # Merged config

        # Integration test should use global config
        integration_config = config_manager.get_rule_config_for_file("PTAS001", integration_file)
        assert integration_config == {"min_asserts": 1, "max_asserts": 5}

    def test_merge_config_deep(self) -> None:
        """Test deep configuration merging."""
        config_manager = ConfigManager()

        base_config: dict[str, Any] = {
            "select": ["PTCM001"],
            "rules": {
                "PTAS001": {"min_asserts": 1, "max_asserts": 5}
            },
            "severity": {"PTCM001": "error"}
        }

        override_config = {
            "select": ["PTCM002"],  # Replace
            "rules": {
                "PTAS001": {"min_asserts": 2},  # Partial override
                "PTAS002": {"max_asserts": 3}   # New rule
            },
            "ignore": ["PTCM003"]  # Add new field
        }

        config_manager._merge_config_deep(base_config, override_config)

        # Verify merged result
        assert base_config["select"] == ["PTCM002"]  # Replaced
        assert base_config["ignore"] == ["PTCM003"]  # Added
        assert base_config["rules"]["PTAS001"] == {"min_asserts": 2, "max_asserts": 5}  # Merged
        assert base_config["rules"]["PTAS002"] == {"max_asserts": 3}  # Added
        assert base_config["severity"]["PTCM001"] == "error"  # Preserved

    @patch('pathlib.Path.cwd')
    def test_get_directory_config_absolute_path_handling(self, mock_cwd: MagicMock) -> None:
        """Test handling of absolute paths and relative path conversion."""
        mock_cwd.return_value = Path("/project/root")

        config_manager = ConfigManager()
        config_manager._config = {
            "select": ["PTCM001"],
            "per_directory_rules": {
                "tests/unit": {
                    "select": ["PTAS001"]
                }
            }
        }

        # Test with absolute path that can be made relative
        absolute_file = Path("/project/root/tests/unit/test_example.py")
        result = config_manager.get_directory_config(absolute_file)
        assert result["select"] == ["PTAS001"]  # Should match directory rule

        # Test with absolute path outside project root
        outside_file = Path("/other/project/tests/unit/test_example.py")
        result = config_manager.get_directory_config(outside_file)
        assert result["select"] == ["PTCM001"]  # Should use global config

