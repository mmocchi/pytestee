"""Check command handler."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pytestee.adapters.cli.handlers.base_handler import BaseCommandHandler
from pytestee.adapters.cli.services.output_service import OutputService
from pytestee.adapters.presenters.console_presenter import ConsolePresenter
from pytestee.domain.rules.rule_validator import RuleConflictError
from pytestee.usecases.analyze_tests import AnalyzeTestsUseCase

if TYPE_CHECKING:
    from pathlib import Path

    from pytestee.domain.models import AnalysisResult


class CheckCommandHandler(BaseCommandHandler):
    """Handler for the check command."""

    def execute(
        self,
        target: Path,
        output_format: str,
        quiet: bool,
        verbose: bool,
        config_overrides: dict[str, Any] | None = None,
        config_path: Path | None = None,
    ) -> AnalysisResult:
        """Execute the check command.

        Args:
            target: Path to analyze
            output_format: Output format (console/json)
            quiet: Quiet mode flag
            verbose: Verbose mode flag
            config_overrides: Configuration overrides
            config_path: Path to configuration file

        Returns:
            Analysis result

        Raises:
            RuleConflictError: If rule conflicts are detected

        """
        if config_overrides is None:
            config_overrides = {}

        # Handle potential rule conflicts during registry creation
        try:
            # Override config manager if config_path is provided
            if config_path:
                from pytestee.infrastructure.config.settings import ConfigManager
                self._config_manager = ConfigManager()
                self._config_manager.load_config(config_path)
                # Reset dependencies to use new config
                self._registry = None
                self._repository = None
            
            registry = self.registry
        except RuleConflictError as e:
            raise RuleConflictError(
                f"Configuration Error: {e}\\n"
                "Use 'pytestee show-config' to review your configuration."
            ) from e

        # Initialize the use case
        analyze_use_case = AnalyzeTestsUseCase(
            test_repository=self.repository,
            checker_registry=registry,
            config_manager=self.config_manager,
        )

        # Execute analysis
        result = analyze_use_case.execute(target, config_overrides)

        # Present results
        if output_format == "console":
            presenter = ConsolePresenter(quiet=quiet, verbose=verbose)
            presenter.present(result)
        elif output_format == "json":
            OutputService.present_analysis_json(result)

        return result
