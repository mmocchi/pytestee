"""Base handler for CLI commands."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pytestee.adapters.repositories.file_repository import FileRepository
from pytestee.infrastructure.config.settings import ConfigManager
from pytestee.registry import CheckerRegistry


class BaseCommandHandler(ABC):
    """Base class for CLI command handlers."""

    def __init__(self) -> None:
        """Initialize base handler."""
        self._config_manager: ConfigManager | None = None
        self._repository: FileRepository | None = None
        self._registry: CheckerRegistry | None = None

    @property
    def config_manager(self) -> ConfigManager:
        """Get or create config manager."""
        if self._config_manager is None:
            self._config_manager = ConfigManager()
            self._config_manager.load_config()
        return self._config_manager

    @property
    def repository(self) -> FileRepository:
        """Get or create file repository."""
        if self._repository is None:
            self._repository = FileRepository(
                exclude_patterns=self.config_manager.get_exclude_patterns()
            )
        return self._repository

    @property
    def registry(self) -> CheckerRegistry:
        """Get or create checker registry."""
        if self._registry is None:
            self._registry = CheckerRegistry(self.config_manager)
        return self._registry

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        """Execute the command.

        Args:
            *args: Variable positional arguments
            **kwargs: Command-specific arguments

        Returns:
            Command execution result

        """
