"""Tests for rule validation system."""

import pytest

from pytestee.infrastructure.rules.rule_validator import (
    RuleConflictError,
    RuleValidator,
)


class TestRuleValidator:
    """Test rule validation functionality."""

    def test_validate_rule_selection_no_conflicts(self) -> None:
        """Test validation with no conflicting rules."""
        # Compatible rules
        selected_rules = {"PTCM001", "PTAS001", "PTAS003"}

        # Should not raise any exception
        RuleValidator.validate_rule_selection(selected_rules)

    def test_validate_rule_selection_pattern_no_conflicts(self) -> None:
        """Test validation allows multiple pattern rules (priority-based)."""
        # Multiple pattern detection rules are allowed (priority-based, not conflicts)
        selected_rules = {"PTCM001", "PTCM002"}

        # Should not raise any exception
        RuleValidator.validate_rule_selection(selected_rules)

    def test_validate_rule_selection_assertion_conflicts(self) -> None:
        """Test validation detects assertion rule conflicts."""
        # Conflicting assertion count rules
        selected_rules = {"PTAS001", "PTAS005"}  # too_few vs assertion_count_ok

        with pytest.raises(RuleConflictError) as exc_info:
            RuleValidator.validate_rule_selection(selected_rules)

        assert "PTAS001, PTAS005" in str(exc_info.value)

    def test_validate_rule_selection_no_assertion_conflicts(self) -> None:
        """Test validation detects no-assertion rule conflicts."""
        # PTAS004 conflicts with all other assertion count rules
        selected_rules = {"PTAS004", "PTAS001", "PTAS002"}

        with pytest.raises(RuleConflictError) as exc_info:
            RuleValidator.validate_rule_selection(selected_rules)

        assert "PTAS001, PTAS002, PTAS004" in str(exc_info.value)

    def test_validate_config_parameters_valid(self) -> None:
        """Test validation with valid configuration parameters."""
        config = {
            "min_asserts": 1,
            "max_asserts": 5,
            "max_density": 0.7
        }

        # Should not raise any exception
        RuleValidator.validate_config_parameters(config)

    def test_validate_config_parameters_min_max_conflict(self) -> None:
        """Test validation detects min > max conflict."""
        config = {
            "min_asserts": 5,
            "max_asserts": 3  # Invalid: min > max
        }

        with pytest.raises(RuleConflictError) as exc_info:
            RuleValidator.validate_config_parameters(config)

        assert "min_asserts (5) cannot be greater than max_asserts (3)" in str(exc_info.value)

    def test_validate_config_parameters_negative_min(self) -> None:
        """Test validation detects negative min_asserts."""
        config = {
            "min_asserts": -1
        }

        with pytest.raises(RuleConflictError) as exc_info:
            RuleValidator.validate_config_parameters(config)

        assert "min_asserts cannot be negative" in str(exc_info.value)

    def test_validate_config_parameters_invalid_max(self) -> None:
        """Test validation detects invalid max_asserts."""
        config = {
            "min_asserts": 1,
            "max_asserts": 0  # Invalid: must be at least 1
        }

        with pytest.raises(RuleConflictError) as exc_info:
            RuleValidator.validate_config_parameters(config)

        # Will trigger min > max error first
        assert "min_asserts (1) cannot be greater than max_asserts (0)" in str(exc_info.value)

    def test_validate_config_parameters_invalid_density(self) -> None:
        """Test validation detects invalid density range."""
        config = {
            "max_density": 1.5  # Invalid: must be between 0.0 and 1.0
        }

        with pytest.raises(RuleConflictError) as exc_info:
            RuleValidator.validate_config_parameters(config)

        assert "max_density must be between 0.0 and 1.0" in str(exc_info.value)

    def test_get_compatible_rules_pattern_rule(self) -> None:
        """Test getting compatible rules for a pattern detection rule."""
        compatible = RuleValidator.get_compatible_rules("PTCM001")

        # Should include all other rules (pattern rules don't have conflicts)
        assert "PTAS001" in compatible
        assert "PTAS003" in compatible
        assert "PTCM002" in compatible  # Pattern rules don't conflict
        assert "PTST001" in compatible  # Pattern rules don't conflict
        assert "PTCM001" not in compatible  # Excluded (is the base rule)

    def test_get_compatible_rules_assertion_rule(self) -> None:
        """Test getting compatible rules for an assertion rule."""
        compatible = RuleValidator.get_compatible_rules("PTAS001")

        # Should include pattern rules and non-conflicting assertion rules
        assert "PTCM001" in compatible
        assert "PTST001" in compatible
        assert "PTAS003" in compatible  # High density doesn't conflict with too_few
        assert "PTAS005" not in compatible  # Excluded due to conflict
        assert "PTAS004" not in compatible  # Excluded due to conflict
        assert "PTAS001" not in compatible  # Excluded (is the base rule)

    def test_get_compatible_rules_no_assertion_rule(self) -> None:
        """Test getting compatible rules for PTAS004 (no assertions)."""
        compatible = RuleValidator.get_compatible_rules("PTAS004")

        # Should include pattern rules but exclude other assertion count rules
        assert "PTCM001" in compatible
        assert "PTST001" in compatible
        assert "PTAS003" in compatible  # Density is compatible with no assertions
        assert "PTAS001" not in compatible  # Excluded due to conflict
        assert "PTAS002" not in compatible  # Excluded due to conflict
        assert "PTAS005" not in compatible  # Excluded due to conflict
        assert "PTAS004" not in compatible  # Excluded (is the base rule)
