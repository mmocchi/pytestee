"""Unit tests for ConfigManager."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from pytestee.infrastructure.config.settings import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.config_manager = ConfigManager()


    def test_default_exclude_patterns(self) -> None:
        """Test default exclude patterns."""
        self.config_manager.load_config()
        patterns = self.config_manager.get_exclude_patterns()
        assert patterns == [".venv/**", "venv/**", "**/__pycache__/**"]

    def test_load_config_with_exclude(self) -> None:
        """Test loading configuration with exclude patterns."""
        config_content = """
exclude = ["**/conftest.py", "test_skip_*.py", "**/fixtures/**"]
"""

        with NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(config_content)
            config_path = Path(f.name)

        try:
            self.config_manager.load_config(config_path)

            # Check exclude patterns
            exclude_patterns = self.config_manager.get_exclude_patterns()
            assert exclude_patterns == ["**/conftest.py", "test_skip_*.py", "**/fixtures/**"]

        finally:
            config_path.unlink()


    def test_pyproject_toml_format(self) -> None:
        """Test loading from pyproject.toml format."""
        config_content = """
[tool.pytestee]
exclude = ["skip_*.py"]
"""

        with NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(config_content)
            config_path = Path(f.name)

        try:
            # Simulate pyproject.toml by renaming
            pyproject_path = config_path.parent / "pyproject.toml"
            config_path.rename(pyproject_path)

            self.config_manager.load_config(pyproject_path)

            exclude_patterns = self.config_manager.get_exclude_patterns()
            assert exclude_patterns == ["skip_*.py"]

        finally:
            if pyproject_path.exists():
                pyproject_path.unlink()

    def test_apply_overrides(self) -> None:
        """Test applying configuration overrides."""
        self.config_manager.load_config()

        # Check default select rules
        original_select = self.config_manager.get_config("select", [])
        assert isinstance(original_select, list)
        assert len(original_select) > 0

        # Apply overrides
        overrides = {
            "select": ["PTCM003"],
            "ignore": ["PTAS001", "PTAS002"]
        }
        self.config_manager.apply_overrides(overrides)

        # Check overridden values
        assert self.config_manager.get_config("select") == ["PTCM003"]
        assert self.config_manager.get_config("ignore") == ["PTAS001", "PTAS002"]

    def test_apply_select_override_rule_enablement(self) -> None:
        """Test that select override affects rule enablement."""
        self.config_manager.load_config()

        # Apply select override
        self.config_manager.apply_overrides({"select": ["PTCM003"]})

        # Only PTCM003 should be enabled
        assert self.config_manager.is_rule_enabled("PTCM003") is True
        assert self.config_manager.is_rule_enabled("PTST001") is False
        assert self.config_manager.is_rule_enabled("PTAS005") is False

    def test_apply_ignore_override_rule_enablement(self) -> None:
        """Test that ignore override affects rule enablement."""
        self.config_manager.load_config()

        # Apply ignore override
        self.config_manager.apply_overrides({"ignore": ["PTCM003"]})

        # PTCM003 should be disabled, others from default select should be enabled
        assert self.config_manager.is_rule_enabled("PTCM003") is False
        assert self.config_manager.is_rule_enabled("PTST001") is True

    def test_apply_select_and_ignore_override_rule_enablement(self) -> None:
        """Test that both select and ignore overrides work together."""
        self.config_manager.load_config()

        # Apply both select and ignore overrides
        self.config_manager.apply_overrides({
            "select": ["PTCM"],  # Select all PTCM rules
            "ignore": ["PTCM001"]  # But ignore PTCM001
        })

        # PTCM002 and PTCM003 should be enabled, PTCM001 should be disabled
        assert self.config_manager.is_rule_enabled("PTCM001") is False
        assert self.config_manager.is_rule_enabled("PTCM002") is True
        assert self.config_manager.is_rule_enabled("PTCM003") is True
        # Non-PTCM rules should be disabled
        assert self.config_manager.is_rule_enabled("PTST001") is False
