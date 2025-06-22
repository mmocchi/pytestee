"""List checkers command handler."""

from pytestee.adapters.cli.handlers.base_handler import BaseCommandHandler
from pytestee.adapters.cli.services.output_service import OutputService
from pytestee.registry import CheckerRegistry


class ListCheckersCommandHandler(BaseCommandHandler):
    """Handler for the list-checkers command."""

    def execute(self) -> list[dict[str, str]]:
        """Execute the list-checkers command.

        Returns:
            List of checker information dictionaries

        """
        # Create a registry without config manager to avoid conflicts
        registry = CheckerRegistry()
        checkers = registry.get_all_checkers()

        checkers_info = []
        for checker in checkers:
            description = self._get_checker_description(checker.name)
            checkers_info.append({
                "name": checker.name,
                "description": description,
            })

        # Display the information
        OutputService.show_checkers_table(checkers_info)

        return checkers_info

    def _get_checker_description(self, checker_name: str) -> str:
        """Get description for a checker.

        Args:
            checker_name: Name of the checker

        Returns:
            Description string

        """
        descriptions = {
            "pattern_checker": "Checks for AAA (Arrange, Act, Assert) or GWT (Given, When, Then) patterns",
            "assertion_checker": "Checks assertion density and count per test function",
        }
        return descriptions.get(checker_name, "No description available")
