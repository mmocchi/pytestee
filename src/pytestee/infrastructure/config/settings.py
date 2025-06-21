"""Configuration management for pytestee."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import tomllib

from ...domain.interfaces import IConfigManager
from ...domain.models import CheckerConfig


class ConfigManager(IConfigManager):
    """Configuration manager for pytestee."""

    def __init__(self) -> None:
        self._config: Dict[str, Any] = {}
        self._default_config = {
            "max_asserts": 3,
            "min_asserts": 1,
            "require_aaa_comments": False,
            "aaa_pattern": {
                "enabled": True,
                "config": {
                    "require_comments": False,
                    "allow_gwt": True
                }
            },
            "assert_density": {
                "enabled": True,
                "config": {
                    "max_asserts": 3,
                    "min_asserts": 1,
                    "max_density": 0.5
                }
            }
        }

    def load_config(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """Load configuration from file or defaults."""
        # Start with defaults
        self._config = self._default_config.copy()

        # Try to load from various sources
        config_sources = []

        if config_path:
            config_sources.append(config_path)
        else:
            # Look for config files in common locations
            config_sources.extend([
                Path.cwd() / ".pytestee.toml",
                Path.cwd() / "pyproject.toml",
                Path.home() / ".config" / "pytestee" / "config.toml"
            ])

        for source in config_sources:
            if source.exists():
                try:
                    loaded_config = self._load_from_file(source)
                    if loaded_config:
                        self._merge_config(loaded_config)
                        break
                except Exception as e:
                    # Log warning but continue with defaults
                    print(f"Warning: Failed to load config from {source}: {e}")

        # Override with environment variables
        self._load_from_env()

        return self._config

    def _load_from_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load configuration from a TOML file."""
        if not file_path.exists():
            return None

        try:
            with open(file_path, "rb") as f:
                data = tomllib.load(f)

            # Handle pyproject.toml format
            if file_path.name == "pyproject.toml":
                return data.get("tool", {}).get("pytestee", {})

            return data

        except Exception:
            return None

    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration with existing."""
        def deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        deep_merge(self._config, new_config)

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            "PYTESTEE_MAX_ASSERTS": ("max_asserts", int),
            "PYTESTEE_MIN_ASSERTS": ("min_asserts", int),
            "PYTESTEE_REQUIRE_AAA_COMMENTS": ("require_aaa_comments", lambda x: x.lower() == "true")
        }

        for env_var, (config_key, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    self._config[config_key] = converter(value)
                except (ValueError, TypeError):
                    pass  # Ignore invalid values

    def get_checker_config(self, checker_name: str) -> CheckerConfig:
        """Get configuration for a specific checker."""
        checker_config = self._config.get(checker_name, {})

        return CheckerConfig(
            name=checker_name,
            enabled=checker_config.get("enabled", True),
            config=checker_config.get("config", {})
        )

    def get_global_config(self) -> Dict[str, Any]:
        """Get global configuration."""
        return self._config.copy()

    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
