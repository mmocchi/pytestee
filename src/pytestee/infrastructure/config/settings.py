"""Configuration management for pytestee."""

import contextlib
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Python < 3.11

from ...domain.interfaces import IConfigManager
from ...domain.models import CheckerConfig
from ...domain.rules.rule_validator import RuleValidator

# Define type alias for configuration values
ConfigValue = Union[str, int, float, bool, Dict[str, Any], list]


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
                "config": {"require_comments": False, "allow_gwt": True},
            },
            "assert_density": {
                "enabled": True,
                "config": {"max_asserts": 3, "min_asserts": 1, "max_density": 0.5},
            },
            # Rule selection configuration (ruff-like)
            "select": [
                "PTCM003",
                "PTST001",
                "PTLG001",
                "PTAS",
                "PTNM001",
            ],  # Default selection (PTCM003 instead of PTCM001/PTCM002 to avoid conflicts)
            "ignore": [],  # Rules to ignore
            # Rule severity configuration
            "severity": {},
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
            config_sources.extend(
                [
                    Path.cwd() / ".pytestee.toml",
                    Path.cwd() / "pyproject.toml",
                    Path.home() / ".config" / "pytestee" / "config.toml",
                ]
            )

        for source in config_sources:
            if source.exists():
                try:
                    loaded_config = self._load_from_file(source)
                    if loaded_config:
                        # Merge loaded config with defaults (loaded config takes precedence)
                        self._merge_config(loaded_config)
                        break
                except Exception as e:
                    # Log warning but continue with defaults
                    print(f"Warning: Failed to load config from {source}: {e}")

        # Override with environment variables (always apply)
        self._load_from_env()

        # Note: Rule validation will be performed later when checker registry is available

        return self._config

    def _load_from_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load configuration from a TOML file."""
        if not file_path.exists():
            return None

        try:
            with Path(file_path).open("rb") as f:
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
                if (
                    key in base
                    and isinstance(base[key], dict)
                    and isinstance(value, dict)
                ):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        deep_merge(self._config, new_config)

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mappings: Dict[str, Tuple[str, Callable[[str], Any]]] = {
            "PYTESTEE_MAX_ASSERTS": ("max_asserts", int),
            "PYTESTEE_MIN_ASSERTS": ("min_asserts", int),
            "PYTESTEE_REQUIRE_AAA_COMMENTS": (
                "require_aaa_comments",
                lambda x: x.lower() == "true",
            ),
        }

        for env_var, (config_key, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                with contextlib.suppress(ValueError, TypeError):
                    self._config[config_key] = converter(value)

    def get_checker_config(self, checker_name: str) -> CheckerConfig:
        """Get configuration for a specific checker."""
        checker_config = self._config.get(checker_name, {})

        return CheckerConfig(
            name=checker_name,
            enabled=checker_config.get("enabled", True),
            config=checker_config.get("config", {}),
        )

    def get_global_config(self) -> Dict[str, Any]:
        """Get global configuration."""
        return self._config.copy()

    def set_config(self, key: str, value: ConfigValue) -> None:
        """Set a configuration value."""
        self._config[key] = value

    def get_config(
        self, key: str, default: Optional[ConfigValue] = None
    ) -> Optional[ConfigValue]:
        """Get a configuration value."""
        return self._config.get(key, default)

    def is_rule_enabled(self, rule_id: str) -> bool:
        """Check if a specific rule is enabled using select/ignore patterns."""
        select_patterns = self._config.get("select", [])
        ignore_patterns = self._config.get("ignore", [])

        # If select is specified and not empty, only selected rules are enabled
        if select_patterns:
            is_selected = self._matches_patterns(rule_id, select_patterns)
            if not is_selected:
                return False

        # Check if rule is ignored
        if ignore_patterns:
            is_ignored = self._matches_patterns(rule_id, ignore_patterns)
            if is_ignored:
                return False

        return True

    def _matches_patterns(self, rule_id: str, patterns: List[str]) -> bool:
        """Check if rule_id matches any pattern in the list."""
        return any(self._matches_pattern(rule_id, pattern) for pattern in patterns)

    def _matches_pattern(self, rule_id: str, pattern: str) -> bool:
        """Check if rule_id matches a single pattern."""
        # Exact match
        if rule_id == pattern:
            return True

        # Prefix match (e.g., "PTCM" matches "PTCM001", "PTCM002")
        return bool(rule_id.startswith(pattern))

    def get_rule_severity(self, rule_id: str) -> str:
        """Get severity level for a specific rule from configuration."""
        severity_config = self._config.get("severity", {})
        return severity_config.get(rule_id, "error")  # Default to error

    def _validate_rule_selection(
        self, rule_instances: Optional[Dict[str, Any]] = None
    ) -> None:
        """Validate that selected rules don't conflict with each other.

        Args:
            rule_instances: Optional mapping of rule IDs to rule instances for dynamic conflict checking

        """
        select_patterns = self._config.get("select", [])

        if not select_patterns:
            # If no select patterns, use default rules (avoiding conflicts)
            selected_rules = set(self._config.get("select", []))
            if not selected_rules:
                # If still empty, expand default patterns
                default_patterns = ["PTCM003", "PTST001", "PTLG001", "PTAS", "PTNM001"]
                selected_rules = self._expand_rule_patterns(default_patterns)
        else:
            # Expand patterns to actual rule IDs
            selected_rules = self._expand_rule_patterns(select_patterns)

        # Remove ignored rules
        ignore_patterns = self._config.get("ignore", [])
        if ignore_patterns:
            ignored_rules = self._expand_rule_patterns(ignore_patterns)
            selected_rules = selected_rules - ignored_rules

        # Validate the final rule selection
        RuleValidator.validate_rule_selection(selected_rules, rule_instances)

    def _expand_rule_patterns(self, patterns: List[str]) -> Set[str]:
        """Expand rule patterns like 'PTCM' to actual rule IDs like 'PTCM001', 'PTCM002'."""
        all_rules = {
            "PTCM001",
            "PTCM002",
            "PTCM003",
            "PTST001",
            "PTLG001",
            "PTAS001",
            "PTAS002",
            "PTAS003",
            "PTAS004",
            "PTAS005",
            "PTNM001",
        }

        expanded_rules = set()
        for pattern in patterns:
            # Exact matches
            if pattern in all_rules:
                expanded_rules.add(pattern)
            else:
                # Prefix matches
                for rule_id in all_rules:
                    if rule_id.startswith(pattern):
                        expanded_rules.add(rule_id)

        return expanded_rules

    def validate_rule_selection_with_instances(
        self, rule_instances: Dict[str, Any]
    ) -> None:
        """外部から呼び出し可能なルール選択検証メソッド.

        Args:
            rule_instances: ルールID -> ルールインスタンスのマッピング

        """
        self._validate_rule_selection(rule_instances)
