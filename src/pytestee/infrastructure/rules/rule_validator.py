"""Rule validation system to prevent conflicting rule configurations."""

from typing import Any, ClassVar, Dict, List, Set


class RuleConflictError(Exception):
    """Raised when conflicting rules are configured simultaneously."""

    pass


class RuleValidator:
    """Validates rule configurations to prevent conflicts."""

    # Define mutually exclusive rule groups
    CONFLICTING_RULE_GROUPS: ClassVar[List[Set[str]]] = [
        # Assertion count rules that could conflict
        {"PTAS001", "PTAS005"},  # too_few vs assertion_count_ok
        {"PTAS002", "PTAS005"},  # too_many vs assertion_count_ok
        {"PTAS004", "PTAS001", "PTAS002", "PTAS005"},  # no_assertions conflicts with all count rules
    ]

    @classmethod
    def validate_rule_selection(cls, selected_rules: Set[str]) -> None:
        """Validate that selected rules don't conflict with each other."""
        conflicts = cls._find_conflicts(selected_rules)

        if conflicts:
            conflict_descriptions = []
            for conflict_group in conflicts:
                rules_str = ", ".join(sorted(conflict_group))
                conflict_descriptions.append(f"Rules {rules_str} are mutually exclusive")

            raise RuleConflictError(
                "Conflicting rules detected:\n" + "\n".join(conflict_descriptions)
            )

    @classmethod
    def validate_config_parameters(cls, config: Dict[str, Any]) -> None:
        """Validate configuration parameters for logical consistency."""
        min_asserts = config.get("min_asserts", 1)
        max_asserts = config.get("max_asserts", 3)

        if min_asserts > max_asserts:
            raise RuleConflictError(
                f"min_asserts ({min_asserts}) cannot be greater than max_asserts ({max_asserts})"
            )

        if min_asserts < 0:
            raise RuleConflictError("min_asserts cannot be negative")

        if max_asserts < 1:
            raise RuleConflictError("max_asserts must be at least 1")

        max_density = config.get("max_density", 0.5)
        if not (0.0 <= max_density <= 1.0):
            raise RuleConflictError("max_density must be between 0.0 and 1.0")

    @classmethod
    def _find_conflicts(cls, selected_rules: Set[str]) -> List[Set[str]]:
        """Find conflicting rule groups in the selected rules."""
        conflicts = []

        for conflict_group in cls.CONFLICTING_RULE_GROUPS:
            # Check if multiple rules from the same conflict group are selected
            intersection = selected_rules.intersection(conflict_group)
            if len(intersection) > 1:
                conflicts.append(intersection)

        return conflicts

    @classmethod
    def get_compatible_rules(cls, base_rule: str) -> Set[str]:
        """Get rules that are compatible with the given base rule."""
        all_rules = {
            "PTCM001", "PTCM002", "PTST001", "PTLG001", "PTST002",
            "PTAS001", "PTAS002", "PTAS003", "PTAS004", "PTAS005"
        }

        # Find which conflict groups the base rule belongs to
        incompatible_rules = set()

        for conflict_group in cls.CONFLICTING_RULE_GROUPS:
            if base_rule in conflict_group:
                # Add all other rules from this conflict group (excluding base rule)
                incompatible_rules.update(conflict_group - {base_rule})

        # Always exclude the base rule itself
        return all_rules - incompatible_rules - {base_rule}
