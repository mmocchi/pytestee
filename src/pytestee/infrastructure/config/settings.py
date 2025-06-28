"""Configuration management for pytestee."""

from pathlib import Path
from typing import Any, Optional, Union

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Python < 3.11

from pytestee.domain.interfaces import IConfigManager
from pytestee.domain.models import CheckerConfig
from pytestee.domain.rules.rule_validator import RuleValidator

# Define type alias for configuration values
ConfigValue = Union[str, int, float, bool, dict[str, Any], list]


class ConfigManager(IConfigManager):
    """Configuration manager for pytestee."""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}
        self._default_config = {
            # File selection configuration
            "exclude": [".venv/**", "venv/**", "**/__pycache__/**"],  # File patterns to exclude
            # Rule selection configuration (ruff-like)
            "select": [
                "PTCM003",
                "PTST001",
                "PTLG001",
                "PTAS005",  # Only PTAS005 to avoid conflicts between assertion rules
                "PTNM001",
                "PTVL001",  # Private access detection
                "PTVL002",  # Time dependency detection
            ],  # Default selection (PTCM003 and PTAS005 to avoid conflicts)
            "ignore": [],  # Rules to ignore
            # Rule severity configuration
            "severity": {},
            # Rule-specific configurations
            "rules": {
                "PTAS005": {
                    "max_asserts": 3,
                    "min_asserts": 1,
                },
                "PTAS001": {
                    "min_asserts": 1,
                },
                "PTAS002": {
                    "max_asserts": 3,
                },
                "PTAS003": {
                    "max_density": 0.5,
                },
                "PTCM001": {
                    "require_comments": False,
                },
                "PTCM002": {
                    "require_comments": False,
                },
                "PTCM003": {
                    "require_comments": False,
                    "allow_gwt": True,
                },
            },
            # Directory-specific rule configuration
            "per_directory_rules": {},
        }

    def load_config(self, config_path: Optional[Path] = None) -> dict[str, Any]:
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

    def _load_from_file(self, file_path: Path) -> Optional[dict[str, Any]]:
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

    def _merge_config(self, new_config: dict[str, Any]) -> None:
        """Merge new configuration with existing."""

        def deep_merge(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
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
        # Environment variable support is disabled to keep configuration simple
        # Use .pytestee.toml or pyproject.toml [tool.pytestee] instead
        pass

    def get_checker_config(self, checker_name: str) -> CheckerConfig:
        """Get configuration for a specific checker."""
        # For rule-specific config, check under rules namespace
        rule_config = self._config.get("rules", {}).get(checker_name, {})

        # Legacy support: also check old structure
        legacy_config = self._config.get(checker_name, {})

        # Merge rule-specific config with legacy config (rule-specific takes precedence)
        merged_config = {}
        if legacy_config:
            merged_config.update(legacy_config.get("config", {}))
        merged_config.update(rule_config)

        return CheckerConfig(
            name=checker_name,
            enabled=legacy_config.get("enabled", True),
            config=merged_config,
        )

    def get_global_config(self) -> dict[str, Any]:
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

    def _matches_patterns(self, rule_id: str, patterns: list[str]) -> bool:
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
        self, rule_instances: Optional[dict[str, Any]] = None
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
                default_patterns = ["PTCM003", "PTST001", "PTLG001", "PTAS005", "PTNM001"]
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

    def _expand_rule_patterns(self, patterns: list[str]) -> set[str]:
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
            "PTNM002",
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
        self, rule_instances: dict[str, Any]
    ) -> None:
        """外部から呼び出し可能なルール選択検証メソッド.

        Args:
            rule_instances: ルールID -> ルールインスタンスのマッピング

        """
        self._validate_rule_selection(rule_instances)

    def get_exclude_patterns(self) -> list[str]:
        """Get file exclude patterns."""
        return self._config.get("exclude", [])

    def get_directory_config(self, file_path: Path) -> dict[str, Any]:
        """Get configuration for a specific file path, considering directory-specific rules.

        Args:
            file_path: Path to the test file being analyzed

        Returns:
            Merged configuration with directory-specific overrides applied

        """
        # Start with global configuration
        config = self._config.copy()

        # Get per-directory rules
        per_dir_rules = self._config.get("per_directory_rules", {})
        if not per_dir_rules:
            return config

        # Find matching directory patterns and apply their configurations
        matching_configs = []

        # Convert file path to relative path from project root
        try:
            # Try to get relative path from current working directory
            relative_path = file_path.relative_to(Path.cwd())
        except ValueError:
            # If file is outside current directory, use absolute path
            relative_path = file_path

        relative_path_str = str(relative_path)

        for pattern, dir_config in per_dir_rules.items():
            if self._matches_directory_pattern(relative_path_str, pattern):
                matching_configs.append((pattern, dir_config))

        # Sort by specificity (longer patterns first for more specific matches)
        matching_configs.sort(key=lambda x: len(x[0]), reverse=True)

        # Apply configurations in order of specificity
        for _pattern, dir_config in matching_configs:
            self._merge_config_deep(config, dir_config)

        return config

    def _matches_directory_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if a file path matches a directory pattern.

        Supports patterns like:
        - "tests/unit" - exact directory match
        - "tests/**" - directory and all subdirectories
        - "**/integration" - any integration directory at any level
        """
        import fnmatch  # noqa: PLC0415

        # Normalize path separators
        file_path = file_path.replace("\\", "/")
        pattern = pattern.replace("\\", "/")

        # Handle directory-only patterns (add /** if needed)
        if not pattern.endswith("/**") and not pattern.endswith("/*") and "**" not in pattern:
            # Check if file is in this directory or subdirectory
            if file_path.startswith(pattern + "/") or file_path == pattern:
                return True
            # Also check the pattern with /** appended
            pattern = pattern + "/**"

        return fnmatch.fnmatch(file_path, pattern)

    def _merge_config_deep(self, base_config: dict[str, Any], override_config: dict[str, Any]) -> None:
        """Deeply merge override configuration into base configuration."""
        for key, value in override_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config_deep(base_config[key], value)
            else:
                base_config[key] = value

    def is_rule_enabled_for_file(self, rule_id: str, file_path: Path) -> bool:
        """Check if a specific rule is enabled for a given file path."""
        # Get directory-specific configuration
        file_config = self.get_directory_config(file_path)

        select_patterns = file_config.get("select", [])
        ignore_patterns = file_config.get("ignore", [])

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

    def get_rule_config_for_file(self, rule_id: str, file_path: Path) -> dict[str, Any]:
        """Get rule-specific configuration for a given file path."""
        file_config = self.get_directory_config(file_path)
        return file_config.get("rules", {}).get(rule_id, {})
