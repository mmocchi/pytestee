"""CLI commands for pytestee."""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from ...adapters.presenters.console_presenter import ConsolePresenter
from ...adapters.repositories.file_repository import FileRepository
from ...domain.models import AnalysisResult
from ...infrastructure.config.settings import ConfigManager
from ...registry import CheckerRegistry
from ...usecases.analyze_tests import AnalyzeTestsUseCase

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="pytestee")
def cli() -> None:
    """pytestee - pytest test quality checker CLI tool."""
    pass


@cli.command()
@click.argument("target", type=click.Path(exists=True, path_type=Path))
@click.option("--max-asserts", type=int, help="Maximum number of asserts per test")
@click.option("--min-asserts", type=int, help="Minimum number of asserts per test")
@click.option("--require-aaa-comments", is_flag=True, help="Require AAA pattern comments")
@click.option("--format", "output_format", type=click.Choice(["console", "json"]), default="console", help="Output format")
@click.option("--quiet", "-q", is_flag=True, help="Quiet mode - only show errors")
@click.option("--verbose", "-v", is_flag=True, help="Verbose mode - show detailed information")
def check(
    target: Path,
    max_asserts: Optional[int],
    min_asserts: Optional[int],
    require_aaa_comments: bool,
    output_format: str,
    quiet: bool,
    verbose: bool
) -> None:
    """Check test files for quality issues."""

    # Build configuration overrides
    config_overrides = {}
    if max_asserts is not None:
        config_overrides["max_asserts"] = max_asserts
    if min_asserts is not None:
        config_overrides["min_asserts"] = min_asserts
    if require_aaa_comments:
        config_overrides["require_aaa_comments"] = require_aaa_comments

    # Set up dependencies
    test_repository = FileRepository()
    config_manager = ConfigManager()
    checker_registry = CheckerRegistry()

    # Initialize the use case
    analyze_use_case = AnalyzeTestsUseCase(
        test_repository=test_repository,
        checker_registry=checker_registry,
        config_manager=config_manager
    )

    try:
        # Execute analysis
        with console.status("Analyzing test files..."):
            result = analyze_use_case.execute(target, config_overrides)

        # Present results
        if output_format == "console":
            presenter = ConsolePresenter(quiet=quiet, verbose=verbose)
            presenter.present(result)
        elif output_format == "json":
            _present_json(result)

        # Exit with error code if there are errors
        if result.has_errors:
            raise click.ClickException("Quality checks failed")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise click.ClickException(str(e))


@cli.command()
@click.argument("target", type=click.Path(exists=True, path_type=Path))
def info(target: Path) -> None:
    """Show information about test files."""

    test_repository = FileRepository()

    try:
        test_files = test_repository.find_test_files(target)

        if not test_files:
            console.print("[yellow]No test files found.[/yellow]")
            return

        # Create summary table
        table = Table(title="Test Files Summary")
        table.add_column("File", style="cyan")
        table.add_column("Test Functions", justify="right", style="green")
        table.add_column("Lines", justify="right", style="blue")

        total_tests = 0
        total_lines = 0

        for file_path in test_files:
            test_file = test_repository.load_test_file(file_path)
            lines = len(test_file.content.splitlines())

            table.add_row(
                str(file_path.relative_to(target if target.is_dir() else target.parent)),
                str(len(test_file.test_functions)),
                str(lines)
            )

            total_tests += len(test_file.test_functions)
            total_lines += lines

        table.add_section()
        table.add_row("Total", str(total_tests), str(total_lines), style="bold")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise click.ClickException(str(e))


@cli.command()
def list_checkers() -> None:
    """List available checkers."""

    checker_registry = CheckerRegistry()
    checkers = checker_registry.get_all_checkers()

    if not checkers:
        console.print("[yellow]No checkers available.[/yellow]")
        return

    table = Table(title="Available Checkers")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")

    for checker in checkers:
        description = _get_checker_description(checker.name)
        table.add_row(checker.name, description)

    console.print(table)


def _get_checker_description(checker_name: str) -> str:
    """Get description for a checker."""
    descriptions = {
        "aaa_pattern": "Checks for AAA (Arrange, Act, Assert) or GWT (Given, When, Then) patterns",
        "assert_density": "Checks assertion density and count per test function"
    }
    return descriptions.get(checker_name, "No description available")


def _present_json(result: AnalysisResult) -> None:
    """Present results in JSON format."""
    import json

    json_result = {
        "summary": {
            "total_files": result.total_files,
            "total_tests": result.total_tests,
            "passed_checks": result.passed_checks,
            "failed_checks": result.failed_checks,
            "success_rate": result.success_rate
        },
        "results": [
            {
                "checker": check_result.checker_name,
                "severity": check_result.severity.value,
                "message": check_result.message,
                "file": str(check_result.file_path),
                "line": check_result.line_number,
                "column": check_result.column,
                "function": check_result.function_name
            }
            for check_result in result.check_results
        ]
    }

    console.print(json.dumps(json_result, indent=2))
