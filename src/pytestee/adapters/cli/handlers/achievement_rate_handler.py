"""Achievement rate command handler."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pytestee.adapters.cli.handlers.base_handler import BaseCommandHandler
from pytestee.adapters.cli.services.output_service import OutputService
from pytestee.adapters.presenters.achievement_rate_presenter import (
    AchievementRatePresenter,
)
from pytestee.domain.rules.rule_validator import RuleConflictError
from pytestee.usecases.calculate_achievement_rate import CalculateAchievementRateUseCase

if TYPE_CHECKING:
    from pathlib import Path

    from pytestee.domain.models import AchievementRateResult


class AchievementRateCommandHandler(BaseCommandHandler):
    """Handler for the achievement rate command."""

    def execute(
        self,
        target: Path,
        output_format: str,
        quiet: bool,
        config_overrides: dict[str, Any] | None = None,
    ) -> AchievementRateResult:
        """Execute the achievement rate command.

        Args:
            target: Path to analyze
            output_format: Output format (console/json)
            quiet: Quiet mode flag
            config_overrides: Configuration overrides

        Returns:
            Achievement rate result

        Raises:
            RuleConflictError: If rule conflicts are detected

        """
        if config_overrides is None:
            config_overrides = {}

        # Handle potential rule conflicts during registry creation
        try:
            registry = self.registry
        except RuleConflictError as e:
            raise RuleConflictError(
                f"Configuration Error: {e}\\n"
                "Use 'pytestee show-config' to review your configuration."
            ) from e

        # Initialize the use case
        calculate_use_case = CalculateAchievementRateUseCase(
            test_repository=self.repository,
            checker_registry=registry,
            config_manager=self.config_manager,
        )

        # Execute calculation
        result = calculate_use_case.execute(target, config_overrides)

        # Present results
        if output_format == "console":
            presenter = AchievementRatePresenter(quiet=quiet)
            presenter.present(result)
        elif output_format == "json":
            OutputService.present_achievement_rate_json(result)

        return result
