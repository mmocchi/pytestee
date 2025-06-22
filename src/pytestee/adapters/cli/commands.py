"""CLI commands for pytestee."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ...adapters.presenters.console_presenter import ConsolePresenter
from ...adapters.repositories.file_repository import FileRepository
from ...domain.checkers.assertion_checker import AssertionChecker
from ...domain.checkers.naming_checker import NamingChecker
from ...domain.checkers.pattern_checker import PatternChecker
from ...domain.models import AnalysisResult
from ...domain.rules.rule_validator import RuleConflictError, RuleValidator
from ...infrastructure.config.settings import ConfigManager
from ...registry import CheckerRegistry
from ...usecases.analyze_tests import AnalyzeTestsUseCase

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="pytestee")
def cli() -> None:
    """Pytestee - pytest test quality checker CLI tool."""
    pass


@cli.command()
@click.argument("target", type=click.Path(exists=True, path_type=Path))
@click.option("--max-asserts", type=int, help="Maximum number of asserts per test")
@click.option("--min-asserts", type=int, help="Minimum number of asserts per test")
@click.option("--require-aaa-comments", is_flag=True, help="Require AAA pattern comments")
@click.option("--format", "output_format", type=click.Choice(["console", "json"]), default="console", help="Output format")
@click.option("--quiet", "-q", is_flag=True, help="Quiet mode - minimal output")
@click.option("--verbose", "-v", is_flag=True, help="Verbose mode - show all results (warnings, info)")
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

    # Handle potential rule conflicts during registry creation
    try:
        checker_registry = CheckerRegistry(config_manager)
    except RuleConflictError as e:
        console.print(f"[red]Configuration Error: {e}[/red]")
        console.print("[yellow]Use 'pytestee show-config' to review your configuration.[/yellow]")
        raise click.ClickException("Rule configuration conflicts detected") from e

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
            raise click.ClickException("Quality checks failed") from None

    except Exception as e:
        console.print(f"[red]Error: {e!s}[/red]")
        raise click.ClickException(str(e)) from e


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
        console.print(f"[red]Error: {e!s}[/red]")
        raise click.ClickException(str(e)) from e


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
        "pattern_checker": "Checks for AAA (Arrange, Act, Assert) or GWT (Given, When, Then) patterns",
        "assertion_checker": "Checks assertion density and count per test function"
    }
    return descriptions.get(checker_name, "No description available")


def _show_config_console(config_manager: ConfigManager, checker_registry: CheckerRegistry) -> None:
    """Show configuration in console format."""
    console.print()

    # Header
    header = Panel(
        "[bold blue]pytestee[/bold blue] - Configuration Status",
        style="blue"
    )
    console.print(header)
    console.print()

    # Get configuration data
    config = config_manager.get_global_config()
    rule_instances = checker_registry.get_all_rule_instances()

    # Show basic configuration
    _show_basic_config(config)

    # Show rule selection
    _show_rule_selection(config_manager, rule_instances)

    # Show conflicts
    _show_rule_conflicts(config_manager, rule_instances)

    # Show severity configuration
    _show_severity_config(config)


def _show_config_json(config_manager: ConfigManager, checker_registry: CheckerRegistry) -> None:
    """Show configuration in JSON format."""
    config = config_manager.get_global_config()
    rule_instances = checker_registry.get_all_rule_instances()

    # Get enabled/disabled rules
    all_rules = set(rule_instances.keys())
    enabled_rules = {rule_id for rule_id in all_rules if config_manager.is_rule_enabled(rule_id)}
    disabled_rules = all_rules - enabled_rules

    # Check for conflicts
    conflict_status = "OK"
    conflict_details = []
    try:
        RuleValidator.validate_rule_selection(enabled_rules, rule_instances)
    except RuleConflictError as e:
        conflict_status = "CONFLICTS_DETECTED"
        conflict_details = str(e).split("\n")[1:]  # Skip first line

    json_config = {
        "configuration": {
            "select": config.get("select", []),
            "ignore": config.get("ignore", []),
            "max_asserts": config.get("max_asserts", 3),
            "min_asserts": config.get("min_asserts", 1),
            "require_aaa_comments": config.get("require_aaa_comments", False)
        },
        "rules": {
            "enabled": sorted(enabled_rules),
            "disabled": sorted(disabled_rules),
            "total_count": len(all_rules)
        },
        "conflicts": {
            "status": conflict_status,
            "details": conflict_details
        },
        "severity": config.get("severity", {})
    }

    console.print(json.dumps(json_config, indent=2))


def _show_basic_config(config: Dict[str, Any]) -> None:
    """Show basic configuration settings."""
    table = Table(title="Basic Configuration", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Max Asserts", str(config.get("max_asserts", 3)))
    table.add_row("Min Asserts", str(config.get("min_asserts", 1)))
    table.add_row("Require AAA Comments", str(config.get("require_aaa_comments", False)))

    select_rules = config.get("select", [])
    if select_rules:
        table.add_row("Selected Rules", ", ".join(select_rules))
    else:
        table.add_row("Selected Rules", "[dim]All rules (default)[/dim]")

    ignore_rules = config.get("ignore", [])
    if ignore_rules:
        table.add_row("Ignored Rules", ", ".join(ignore_rules))
    else:
        table.add_row("Ignored Rules", "[dim]None[/dim]")

    console.print(table)
    console.print()


def _show_rule_selection(config_manager: ConfigManager, rule_instances: Dict[str, Any]) -> None:
    """Show rule selection status."""
    all_rules = set(rule_instances.keys())
    enabled_rules = {rule_id for rule_id in all_rules if config_manager.is_rule_enabled(rule_id)}

    # Create rules table
    table = Table(title="Rule Status", show_header=True)
    table.add_column("Rule ID", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Severity", justify="center")
    table.add_column("Description", style="dim")

    # Sort rules by category and ID
    sorted_rules = sorted(all_rules)

    for rule_id in sorted_rules:
        if rule_id in enabled_rules:
            status = "[green]✓ Enabled[/green]"
            severity = config_manager.get_rule_severity(rule_id).upper()
            severity_color = {
                "ERROR": "red",
                "WARNING": "yellow",
                "INFO": "blue"
            }.get(severity, "white")
            severity_text = f"[{severity_color}]{severity}[/{severity_color}]"
        else:
            status = "[red]✗ Disabled[/red]"
            severity_text = "[dim]-[/dim]"

        # Get description from rule instance
        description = ""
        if rule_id in rule_instances:
            rule_instance = rule_instances[rule_id]
            if hasattr(rule_instance, 'description'):
                description = rule_instance.description

        table.add_row(rule_id, status, severity_text, description)

    console.print(table)
    console.print()


def _show_rule_conflicts(config_manager: ConfigManager, rule_instances: Dict[str, Any]) -> None:
    """Show rule conflict analysis."""
    all_rules = set(rule_instances.keys())
    enabled_rules = {rule_id for rule_id in all_rules if config_manager.is_rule_enabled(rule_id)}

    # Check for conflicts
    try:
        RuleValidator.validate_rule_selection(enabled_rules, rule_instances)
        # No conflicts
        conflict_panel = Panel(
            "[green]✓ No rule conflicts detected[/green]",
            title="Conflict Analysis",
            style="green"
        )
        console.print(conflict_panel)
    except RuleConflictError as e:
        # Conflicts detected
        conflict_text = str(e).replace("Conflicting rules detected:\n", "")
        conflict_panel = Panel(
            f"[red]✗ Conflicts detected:\n{conflict_text}[/red]",
            title="Conflict Analysis",
            style="red"
        )
        console.print(conflict_panel)

    console.print()


def _show_severity_config(config: Dict[str, Any]) -> None:
    """Show severity configuration."""
    severity_config = config.get("severity", {})

    if not severity_config:
        console.print("[dim]No custom severity configuration[/dim]")
        return

    table = Table(title="Severity Configuration", show_header=True)
    table.add_column("Rule ID", style="cyan")
    table.add_column("Severity", justify="center")

    for rule_id, severity in sorted(severity_config.items()):
        severity_color = {
            "error": "red",
            "warning": "yellow",
            "info": "blue"
        }.get(severity.lower(), "white")

        severity_text = f"[{severity_color}]{severity.upper()}[/{severity_color}]"
        table.add_row(rule_id, severity_text)

    console.print(table)
    console.print()


def _present_json(result: AnalysisResult) -> None:
    """Present results in JSON format."""
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
                "rule_id": check_result.rule_id,
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


@cli.command(name="show-config")
@click.option("--format", "output_format", type=click.Choice(["console", "json"]), default="console", help="Output format")
def show_config(output_format: str) -> None:
    """Show current configuration and rule status."""
    try:
        # Set up dependencies
        config_manager = ConfigManager()
        config_manager.load_config()

        # For show-config, we want to show the configuration even if there are conflicts
        # So we create checker registry without validation
        try:
            checker_registry = CheckerRegistry(config_manager)
        except RuleConflictError:
            # If conflicts detected during registry creation, create without validation
            checker_registry = CheckerRegistry(None)  # No config manager to avoid validation
            checker_registry.register(PatternChecker(config_manager))
            checker_registry.register(AssertionChecker(config_manager))
            checker_registry.register(NamingChecker(config_manager))

        if output_format == "console":
            _show_config_console(config_manager, checker_registry)
        elif output_format == "json":
            _show_config_json(config_manager, checker_registry)

    except Exception as e:
        console.print(f"[red]Error: {e!s}[/red]")
        raise click.ClickException(str(e)) from e
