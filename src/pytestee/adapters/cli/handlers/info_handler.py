"""Info command handler."""

from pathlib import Path
from typing import Any

from pytestee.adapters.cli.handlers.base_handler import BaseCommandHandler
from pytestee.adapters.cli.services.output_service import OutputService


class InfoCommandHandler(BaseCommandHandler):
    """Handler for the info command."""

    def execute(self, target: Path) -> list[dict[str, Any]]:
        """Execute the info command.

        Args:
            target: Path to analyze

        Returns:
            List of file information dictionaries

        """
        test_files = self.repository.find_test_files(target)

        files_info = []
        for file_path in test_files:
            test_file = self.repository.load_test_file(file_path)
            lines = len(test_file.content.splitlines())

            relative_path = str(
                file_path.relative_to(target if target.is_dir() else target.parent)
            )

            files_info.append({
                "path": file_path,
                "relative_path": relative_path,
                "test_count": len(test_file.test_functions),
                "line_count": lines,
            })

        # Display the information
        OutputService.show_info_table(files_info)

        return files_info
