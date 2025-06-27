"""Achievement rate presenter for displaying results."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pytestee.domain.models import AchievementRateResult


class AchievementRatePresenter:
    """Presenter for achievement rate results using Rich."""

    def __init__(self, quiet: bool = False) -> None:
        """Initialize the presenter.

        Args:
            quiet: Quiet mode flag

        """
        self.console = Console()
        self.quiet = quiet

    def present(self, result: AchievementRateResult) -> None:
        """Present the achievement rate results to console.

        Args:
            result: Achievement rate result to display

        """
        if not self.quiet:
            self._show_header()
            self._show_summary(result)

        self._show_rule_rates(result)

        if not self.quiet:
            self._show_footer(result)

    def _show_header(self) -> None:
        """Show header information."""
        header = Panel(
            "[bold blue]pytestee[/bold blue] - Achievement Rate Report",
            style="blue",
        )
        self.console.print(header)
        self.console.print()

    def _show_summary(self, result: AchievementRateResult) -> None:
        """Show summary statistics.

        Args:
            result: Achievement rate result

        """
        table = Table(title="Summary", show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="white")

        table.add_row("Test Files", str(result.total_files))
        table.add_row("Test Functions", str(result.total_tests))
        table.add_row("Overall Achievement Rate", f"{result.overall_rate:.1f}%")

        self.console.print(table)
        self.console.print()

    def _show_rule_rates(self, result: AchievementRateResult) -> None:
        """Show achievement rates for each rule.

        Args:
            result: Achievement rate result

        """
        table = Table(title="Rule Achievement Rates")
        table.add_column("Rule ID", style="cyan", width=12)
        table.add_column("Checker", style="dim", width=20)
        table.add_column("Passed", justify="right", style="green", width=8)
        table.add_column("Failed", justify="right", style="red", width=8)
        table.add_column("Total", justify="right", style="white", width=8)
        table.add_column("Rate", justify="right", style="bold", width=10)

        for rule_rate in result.rule_rates:
            # Color code the achievement rate
            rate_str = f"{rule_rate.achievement_rate:.1f}%"
            if rule_rate.achievement_rate >= 90:
                rate_color = "green"
            elif rule_rate.achievement_rate >= 70:
                rate_color = "yellow"
            else:
                rate_color = "red"

            table.add_row(
                rule_rate.rule_id,
                rule_rate.checker_name,
                str(rule_rate.passed_checks),
                str(rule_rate.failed_checks),
                str(rule_rate.total_checks),
                f"[{rate_color}]{rate_str}[/{rate_color}]",
            )

        self.console.print(table)
        self.console.print()

    def _show_footer(self, result: AchievementRateResult) -> None:
        """Show footer with interpretation guide.

        Args:
            result: Achievement rate result

        """
        footer_text = """
[dim]Rate Guide:[/dim]
[green]≥90%[/green] Excellent  [yellow]70-89%[/yellow] Good  [red]<70%[/red] Needs Improvement
"""
        footer = Panel(footer_text.strip(), style="dim")
        self.console.print(footer)
