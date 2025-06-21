"""Dependency injection container and checker registry."""

from typing import Any, Dict, List, Optional

from .domain.interfaces import IChecker, ICheckerRegistry
from .infrastructure.checkers.aaa_pattern_checker import AAAPatternChecker
from .infrastructure.checkers.assert_density_checker import AssertDensityChecker


class CheckerRegistry(ICheckerRegistry):
    """Registry for managing test quality checkers."""

    def __init__(self) -> None:
        self._checkers: Dict[str, IChecker] = {}
        self._initialize_default_checkers()

    def _initialize_default_checkers(self) -> None:
        """Initialize default checkers."""
        self.register(AAAPatternChecker())
        self.register(AssertDensityChecker())

    def register(self, checker: IChecker) -> None:
        """Register a checker."""
        self._checkers[checker.name] = checker

    def get_checker(self, name: str) -> Optional[IChecker]:
        """Get a checker by name."""
        return self._checkers.get(name)

    def get_all_checkers(self) -> List[IChecker]:
        """Get all registered checkers."""
        return list(self._checkers.values())

    def get_enabled_checkers(self, config: Dict[str, Any]) -> List[IChecker]:
        """Get all enabled checkers based on configuration."""
        enabled_checkers = []

        for checker in self._checkers.values():
            checker_config = config.get(checker.name, {})

            # Check if checker is enabled (default to True)
            if checker_config.get("enabled", True):
                enabled_checkers.append(checker)

        return enabled_checkers

    def unregister(self, name: str) -> bool:
        """Unregister a checker by name."""
        if name in self._checkers:
            del self._checkers[name]
            return True
        return False

    def clear(self) -> None:
        """Clear all registered checkers."""
        self._checkers.clear()

    def list_checker_names(self) -> List[str]:
        """Get list of all registered checker names."""
        return list(self._checkers.keys())
