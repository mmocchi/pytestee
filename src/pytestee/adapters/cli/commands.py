"""Refactored CLI commands for pytestee."""

from pathlib import Path

import click
from rich.console import Console

from pytestee.adapters.cli.handlers.achievement_rate_handler import (
    AchievementRateCommandHandler,
)
from pytestee.adapters.cli.handlers.check_handler import CheckCommandHandler
from pytestee.adapters.cli.handlers.info_handler import InfoCommandHandler
from pytestee.adapters.cli.handlers.list_checkers_handler import (
    ListCheckersCommandHandler,
)
from pytestee.adapters.cli.handlers.show_config_handler import ShowConfigCommandHandler
from pytestee.domain.rules.rule_validator import RuleConflictError

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="pytestee")
def cli() -> None:
    """Pytestee - pytest test quality checker CLI tool."""
    pass


@cli.command()
@click.argument(
    "target",
    type=click.Path(exists=True, path_type=Path),
    required=False,
    default=".",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["console", "json"]),
    default="console",
    help="Output format",
)
@click.option("--quiet", "-q", is_flag=True, help="Quiet mode - minimal output")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose mode - show all results (warnings, info)",
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.option(
    "--select",
    multiple=True,
    help="Select specific rules to run (comma-separated). Overrides config file settings.",
)
@click.option(
    "--ignore",
    multiple=True,
    help="Ignore specific rules (comma-separated). Overrides config file settings.",
)
def check(
    target: Path,
    output_format: str,
    quiet: bool,
    verbose: bool,
    config: Path,
    select: tuple[str, ...],
    ignore: tuple[str, ...],
) -> None:
    """Check test files for quality issues.

    If no target is specified, checks all Python files in the current directory
    except those matching exclude patterns from configuration.
    """
    try:
        # Build config overrides from CLI arguments
        config_overrides = {}
        if select:
            # Flatten comma-separated values and filter empty strings
            select_rules = []
            for item in select:
                select_rules.extend([rule.strip() for rule in item.split(",") if rule.strip()])
            if select_rules:
                config_overrides["select"] = select_rules

        if ignore:
            # Flatten comma-separated values and filter empty strings
            ignore_rules = []
            for item in ignore:
                ignore_rules.extend([rule.strip() for rule in item.split(",") if rule.strip()])
            if ignore_rules:
                config_overrides["ignore"] = ignore_rules

        handler = CheckCommandHandler()
        result = handler.execute(
            target=target,
            output_format=output_format,
            quiet=quiet,
            verbose=verbose,
            config_overrides=config_overrides,
            config_path=config,
        )

        # Exit with error code if there are errors
        if result.has_errors:
            raise click.ClickException("Quality checks failed")

    except RuleConflictError as e:
        console.print(f"[red]{e}[/red]")
        raise click.ClickException("Rule configuration conflicts detected") from e
    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e!s}[/red]")
        raise click.ClickException(str(e)) from e


@cli.command()
@click.argument(
    "target",
    type=click.Path(exists=True, path_type=Path),
    required=False,
    default=".",
)
def info(target: Path) -> None:
    """Show information about test files.

    If no target is specified, shows information about all Python files
    in the current directory except those matching exclude patterns from configuration.
    """
    try:
        handler = InfoCommandHandler()
        handler.execute(target=target)
    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e!s}[/red]")
        raise click.ClickException(str(e)) from e


@cli.command()
def list_checkers() -> None:
    """List available checkers."""
    try:
        handler = ListCheckersCommandHandler()
        handler.execute()
    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e!s}[/red]")
        raise click.ClickException(str(e)) from e


@cli.command(name="show-config")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["console", "json"]),
    default="console",
    help="Output format",
)
def show_config(output_format: str) -> None:
    """Show current configuration and rule status."""
    try:
        handler = ShowConfigCommandHandler()
        handler.execute(output_format=output_format)
    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e!s}[/red]")
        raise click.ClickException(str(e)) from e


@cli.command(name="achievement-rate")
@click.argument(
    "target",
    type=click.Path(exists=True, path_type=Path),
    required=False,
    default=".",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["console", "json"]),
    default="console",
    help="Output format",
)
@click.option("--quiet", "-q", is_flag=True, help="Quiet mode - minimal output")
@click.option(
    "--select",
    multiple=True,
    help="Select specific rules to run (comma-separated). Overrides config file settings.",
)
@click.option(
    "--ignore",
    multiple=True,
    help="Ignore specific rules (comma-separated). Overrides config file settings.",
)
def achievement_rate(
    target: Path,
    output_format: str,
    quiet: bool,
    select: tuple[str, ...],
    ignore: tuple[str, ...],
) -> None:
    """Show achievement rate for each rule.

    Display the percentage of tests that pass each quality rule.
    This helps track progress when improving test quality.

    If no target is specified, analyzes all Python files in the current directory
    except those matching exclude patterns from configuration.
    """
    try:
        # Build config overrides from CLI arguments
        config_overrides = {}
        if select:
            # Flatten comma-separated values and filter empty strings
            select_rules = []
            for item in select:
                select_rules.extend([rule.strip() for rule in item.split(",") if rule.strip()])
            if select_rules:
                config_overrides["select"] = select_rules

        if ignore:
            # Flatten comma-separated values and filter empty strings
            ignore_rules = []
            for item in ignore:
                ignore_rules.extend([rule.strip() for rule in item.split(",") if rule.strip()])
            if ignore_rules:
                config_overrides["ignore"] = ignore_rules

        handler = AchievementRateCommandHandler()
        handler.execute(
            target=target,
            output_format=output_format,
            quiet=quiet,
            config_overrides=config_overrides,
        )

    except RuleConflictError as e:
        console.print(f"[red]{e}[/red]")
        raise click.ClickException("Rule configuration conflicts detected") from e
    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e!s}[/red]")
        raise click.ClickException(str(e)) from e
