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
