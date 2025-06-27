"""Output formatting service for CLI."""

import json
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pytestee.domain.models import (
    AchievementRateResult,
    AnalysisResult,
    CheckFailure,
    CheckSuccess,
)
from pytestee.domain.rules.rule_validator import RuleConflictError, RuleValidator
from pytestee.infrastructure.config.settings import ConfigManager
from pytestee.registry import CheckerRegistry

console = Console()


class OutputService:
    """Service for formatting and displaying CLI output."""

    @staticmethod
    def present_analysis_json(result: AnalysisResult) -> None:
        """Present analysis results in JSON format."""
        json_result = {
            "summary": {
                "total_files": result.total_files,
                "total_tests": result.total_tests,
                "passed_checks": result.passed_checks,
                "failed_checks": result.failed_checks,
                "success_rate": result.success_rate,
            },
            "results": [
                {
                    "checker": check_result.checker_name,
                    "rule_id": check_result.rule_id,
                    "status": "success" if isinstance(check_result, CheckSuccess) else "failure",
                    "severity": check_result.severity.value if isinstance(check_result, CheckFailure) else None,
                    "message": check_result.message,
                    "file": str(check_result.file_path),
                    "line": check_result.line_number,
                    "column": check_result.column,
                    "function": check_result.function_name,
                }
                for check_result in result.check_results
            ],
        }
        console.print(json.dumps(json_result, indent=2))

    @staticmethod
    def present_achievement_rate_json(result: AchievementRateResult) -> None:
        """Present achievement rate results in JSON format."""
        json_result = {
            "summary": {
                "total_files": result.total_files,
                "total_tests": result.total_tests,
                "overall_rate": result.overall_rate,
            },
            "rule_rates": [
                {
                    "rule_id": rule_rate.rule_id,
                    "checker_name": rule_rate.checker_name,
                    "total_checks": rule_rate.total_checks,
                    "passed_checks": rule_rate.passed_checks,
                    "failed_checks": rule_rate.failed_checks,
                    "achievement_rate": rule_rate.achievement_rate,
                }
                for rule_rate in result.rule_rates
            ],
        }
        console.print(json.dumps(json_result, indent=2))

    @staticmethod
    def show_info_table(test_files_info: list[dict[str, Any]]) -> None:
        """Show test files information in table format."""
        if not test_files_info:
            console.print("[yellow]No test files found.[/yellow]")
            return

        table = Table(title="Test Files Summary")
        table.add_column("File", style="cyan")
        table.add_column("Test Functions", justify="right", style="green")
        table.add_column("Lines", justify="right", style="blue")

        total_tests = 0
        total_lines = 0

        for file_info in test_files_info:
            table.add_row(
                file_info["relative_path"],
                str(file_info["test_count"]),
                str(file_info["line_count"]),
            )
            total_tests += file_info["test_count"]
            total_lines += file_info["line_count"]

        table.add_section()
        table.add_row("Total", str(total_tests), str(total_lines), style="bold")

        console.print(table)

    @staticmethod
    def show_checkers_table(checkers_info: list[dict[str, str]]) -> None:
        """Show available checkers in table format."""
        if not checkers_info:
            console.print("[yellow]No checkers available.[/yellow]")
            return

        table = Table(title="Available Checkers")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")

        for checker_info in checkers_info:
            table.add_row(checker_info["name"], checker_info["description"])

        console.print(table)

    @staticmethod
    def show_config_console(
        config_manager: ConfigManager, checker_registry: CheckerRegistry
    ) -> None:
        """Show configuration in console format."""
        console.print()

        # Header
        header = Panel(
            "[bold blue]pytestee[/bold blue] - Configuration Status", style="blue"
        )
        console.print(header)
        console.print()

        # Get configuration data
        config = config_manager.get_global_config()
        rule_instances = checker_registry.get_all_rule_instances()

        # Show basic configuration
        OutputService._show_basic_config(config)

        # Show rule selection
        OutputService._show_rule_selection(config_manager, rule_instances)

        # Show conflicts
        OutputService._show_rule_conflicts(config_manager, rule_instances)

        # Show severity configuration
        OutputService._show_severity_config(config)

    @staticmethod
    def show_config_json(
        config_manager: ConfigManager, checker_registry: CheckerRegistry
    ) -> None:
        """Show configuration in JSON format."""
        config = config_manager.get_global_config()
        rule_instances = checker_registry.get_all_rule_instances()

        # Get enabled/disabled rules
        all_rules = set(rule_instances.keys())
        enabled_rules = {
            rule_id for rule_id in all_rules if config_manager.is_rule_enabled(rule_id)
        }
        disabled_rules = all_rules - enabled_rules

        # Check for conflicts
        conflict_status = "OK"
        conflict_details = []
        try:
            RuleValidator.validate_rule_selection(enabled_rules, rule_instances)
        except RuleConflictError as e:
            conflict_status = "CONFLICTS_DETECTED"
            conflict_details = str(e).split("\\n")[1:]  # Skip first line

        json_config = {
            "configuration": {
                "select": config.get("select", []),
                "ignore": config.get("ignore", []),
                "rules": config.get("rules", {}),
            },
            "rules": {
                "enabled": sorted(enabled_rules),
                "disabled": sorted(disabled_rules),
                "total_count": len(all_rules),
            },
            "conflicts": {"status": conflict_status, "details": conflict_details},
            "severity": config.get("severity", {}),
        }

        console.print(json.dumps(json_config, indent=2))

    @staticmethod
    def _show_basic_config(config: dict[str, Any]) -> None:
        """Show basic configuration settings."""
        table = Table(title="Basic Configuration", show_header=True)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")

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

        # Show rule-specific configurations
        rule_configs = config.get("rules", {})
        if rule_configs:
            rule_table = Table(title="Rule-Specific Configuration", show_header=True)
            rule_table.add_column("Rule ID", style="cyan")
            rule_table.add_column("Settings", style="white")

            for rule_id, settings in sorted(rule_configs.items()):
                if settings:
                    settings_str = ", ".join(f"{k}={v}" for k, v in settings.items())
                    rule_table.add_row(rule_id, settings_str)

            console.print(rule_table)
            console.print()

    @staticmethod
    def _show_rule_selection(
        config_manager: ConfigManager, rule_instances: dict[str, Any]
    ) -> None:
        """Show rule selection status."""
        all_rules = set(rule_instances.keys())
        enabled_rules = {
            rule_id for rule_id in all_rules if config_manager.is_rule_enabled(rule_id)
        }

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
                severity_color = {"ERROR": "red", "WARNING": "yellow", "INFO": "blue"}.get(
                    severity, "white"
                )
                severity_text = f"[{severity_color}]{severity}[/{severity_color}]"
            else:
                status = "[red]✗ Disabled[/red]"
                severity_text = "[dim]-[/dim]"

            # Get description from rule instance
            description = ""
            if rule_id in rule_instances:
                rule_instance = rule_instances[rule_id]
                if hasattr(rule_instance, "description"):
                    description = rule_instance.description

            table.add_row(rule_id, status, severity_text, description)

        console.print(table)
        console.print()

    @staticmethod
    def _show_rule_conflicts(
        config_manager: ConfigManager, rule_instances: dict[str, Any]
    ) -> None:
        """Show rule conflict analysis."""
        all_rules = set(rule_instances.keys())
        enabled_rules = {
            rule_id for rule_id in all_rules if config_manager.is_rule_enabled(rule_id)
        }

        # Check for conflicts
        try:
            RuleValidator.validate_rule_selection(enabled_rules, rule_instances)
            # No conflicts
            conflict_panel = Panel(
                "[green]✓ No rule conflicts detected[/green]",
                title="Conflict Analysis",
                style="green",
            )
            console.print(conflict_panel)
        except RuleConflictError as e:
            # Conflicts detected
            conflict_text = str(e).replace("Conflicting rules detected:\\n", "")
            conflict_panel = Panel(
                f"[red]✗ Conflicts detected:\\n{conflict_text}[/red]",
                title="Conflict Analysis",
                style="red",
            )
            console.print(conflict_panel)

        console.print()

    @staticmethod
    def _show_severity_config(config: dict[str, Any]) -> None:
        """Show severity configuration."""
        severity_config = config.get("severity", {})

        if not severity_config:
            console.print("[dim]No custom severity configuration[/dim]")
            return

        table = Table(title="Severity Configuration", show_header=True)
        table.add_column("Rule ID", style="cyan")
        table.add_column("Severity", justify="center")

        for rule_id, severity in sorted(severity_config.items()):
            severity_color = {"error": "red", "warning": "yellow", "info": "blue"}.get(
                severity.lower(), "white"
            )

            severity_text = f"[{severity_color}]{severity.upper()}[/{severity_color}]"
            table.add_row(rule_id, severity_text)

        console.print(table)
        console.print()
