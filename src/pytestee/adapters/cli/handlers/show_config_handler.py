"""Show config command handler."""

from pytestee.adapters.cli.handlers.base_handler import BaseCommandHandler
from pytestee.adapters.cli.services.output_service import OutputService
from pytestee.domain.rules.rule_validator import RuleConflictError
from pytestee.registry import CheckerRegistry


class ShowConfigCommandHandler(BaseCommandHandler):
    """Handler for the show-config command."""

    def execute(self, output_format: str) -> None:
        """Execute the show-config command.

        Args:
            output_format: Output format (console/json)

        """
        # For show-config, we want to show the configuration even if there are conflicts
        # So we create checker registry without validation if needed
        try:
            registry = self.registry
        except RuleConflictError:
            # If conflicts detected during registry creation, create without validation
            registry = CheckerRegistry(None)  # No config manager to avoid validation

        if output_format == "console":
            OutputService.show_config_console(self.config_manager, registry)
        elif output_format == "json":
            OutputService.show_config_json(self.config_manager, registry)
