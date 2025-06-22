"""Rule validation system to prevent conflicting rule configurations."""

from typing import Any, Dict, List, Optional, Set

from .base_rule import BaseRule


class RuleConflictError(Exception):
    """Raised when conflicting rules are configured simultaneously."""

    pass


class RuleValidator:
    """Validates rule configurations to prevent conflicts."""

    # Note: Conflict definitions have been moved to individual rules via get_conflicting_rules() method
    # This provides better encapsulation and maintainability

    @classmethod
    def validate_rule_selection(cls, selected_rules: Set[str], rule_instances: Optional[Dict[str, BaseRule]] = None) -> None:
        """Validate that selected rules don't conflict with each other.

        Args:
            selected_rules: Set of rule IDs that are selected
            rule_instances: Optional dict mapping rule IDs to rule instances for dynamic conflict checking

        """
        if rule_instances:
            # Use dynamic conflicts from rule instances
            conflicts = cls._find_dynamic_conflicts(selected_rules, rule_instances)
        else:
            # No rule instances provided - cannot perform conflict checking
            conflicts = []

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
    def _find_dynamic_conflicts(cls, selected_rules: Set[str], rule_instances: Dict[str, BaseRule]) -> List[Set[str]]:
        """Find conflicting rule groups using dynamic conflicts from rule instances."""
        conflicts = []
        checked_pairs = set()

        # Check all pairs of selected rules for conflicts
        selected_list = list(selected_rules)
        for i, rule_id in enumerate(selected_list):
            if rule_id not in rule_instances:
                continue

            rule_instance = rule_instances[rule_id]
            conflicting_rules = rule_instance.get_conflicting_rules()

            # Check remaining rules for conflicts
            for other_rule_id in selected_list[i+1:]:
                if other_rule_id in conflicting_rules:
                    # Found a conflict between two selected rules
                    conflict_pair = {rule_id, other_rule_id}
                    conflict_key = tuple(sorted(conflict_pair))

                    if conflict_key not in checked_pairs:
                        conflicts.append(conflict_pair)
                        checked_pairs.add(conflict_key)

        return conflicts

    @classmethod
    def get_compatible_rules(cls, base_rule: str, rule_instances: Dict[str, BaseRule]) -> Set[str]:
        """Get rules that are compatible with the given base rule using dynamic conflicts."""
        if base_rule not in rule_instances:
            return set()

        all_rules = set(rule_instances.keys())
        rule_instance = rule_instances[base_rule]
        conflicting_rules = rule_instance.get_conflicting_rules()

        # Return all rules except the base rule and its conflicting rules
        return all_rules - conflicting_rules - {base_rule}
