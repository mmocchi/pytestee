"""Console presenter for displaying analysis results."""

from typing import Dict, List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from ...domain.interfaces import IPresenter
from ...domain.models import AnalysisResult, CheckResult, CheckSeverity


class ConsolePresenter(IPresenter):
    """Presenter for console output using Rich."""

    def __init__(self, quiet: bool = False, verbose: bool = False) -> None:
        self.console = Console()
        self.quiet = quiet
        self.verbose = verbose

    def present(self, result: AnalysisResult) -> None:
        """Present the analysis results to console."""
        if not self.quiet:
            self._show_header()
            self._show_summary(result)

        if result.check_results:
            self._show_results(result.check_results)

        if not self.quiet:
            self._show_footer(result)

    def _show_header(self) -> None:
        """Show header information."""
        header = Panel(
            "[bold blue]pytestee[/bold blue] - pytest test quality checker",
            style="blue"
        )
        self.console.print(header)
        self.console.print()

    def _show_summary(self, result: AnalysisResult) -> None:
        """Show analysis summary."""
        table = Table(title="Analysis Summary", show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="white")

        table.add_row("Test Files", str(result.total_files))
        table.add_row("Test Functions", str(result.total_tests))
        table.add_row("Passed Checks", f"[green]{result.passed_checks}[/green]")
        table.add_row("Failed Checks", f"[red]{result.failed_checks}[/red]")
        table.add_row("Success Rate", f"{result.success_rate:.1f}%")

        self.console.print(table)
        self.console.print()

    def _show_results(self, results: List[CheckResult]) -> None:
        """Show detailed check results."""
        # Show all results from enabled rules (filtered by select/ignore at rule level)
        if not results:
            if not self.quiet:
                self.console.print("[green]✅ All checks passed![/green]")
            return

        # Group results by file
        results_by_file = self._group_results_by_file(results)

        for file_path, file_results in results_by_file.items():
            self._show_file_results(file_path, file_results)

    def _group_results_by_file(self, results: List[CheckResult]) -> Dict[str, List[CheckResult]]:
        """Group check results by file path."""
        grouped: Dict[str, List[CheckResult]] = {}

        for result in results:
            file_key = str(result.file_path)
            if file_key not in grouped:
                grouped[file_key] = []
            grouped[file_key].append(result)

        return grouped

    def _show_file_results(self, file_path: str, results: List[CheckResult]) -> None:
        """Show results for a specific file."""
        # Create tree structure for file results
        tree = Tree(f"📁 [bold]{file_path}[/bold]")

        # Group by function
        results_by_function: Dict[str, List[CheckResult]] = {}
        file_level_results = []

        for result in results:
            if result.function_name:
                if result.function_name not in results_by_function:
                    results_by_function[result.function_name] = []
                results_by_function[result.function_name].append(result)
            else:
                file_level_results.append(result)

        # Add file-level results
        for result in file_level_results:
            icon, color = self._get_severity_style(result.severity)
            rule_id = f"[dim]{result.rule_id}[/dim] " if result.rule_id else ""
            tree.add(f"{icon} {rule_id}[{color}]{result.message}[/{color}]")

        # Add function-level results
        for function_name, function_results in results_by_function.items():
            function_branch = tree.add(f"🔧 [bold cyan]{function_name}[/bold cyan]")

            for result in function_results:
                icon, color = self._get_severity_style(result.severity)
                location = f" (line {result.line_number})" if result.line_number else ""
                rule_id = f"[dim]{result.rule_id}[/dim] " if result.rule_id else ""
                message = f"{icon} {rule_id}[{color}]{result.message}{location}[/{color}]"

                if self.verbose and result.context:
                    message += f"\n   [dim]{result.context}[/dim]"

                function_branch.add(message)

        self.console.print(tree)
        self.console.print()

    def _get_severity_style(self, severity: CheckSeverity) -> Tuple[str, str]:
        """Get icon and color for severity level."""
        if severity == CheckSeverity.ERROR:
            return "❌", "red"
        if severity == CheckSeverity.WARNING:
            return "⚠️", "yellow"
        return "ℹ️", "blue"

    def _show_footer(self, result: AnalysisResult) -> None:
        """Show footer with overall status."""
        if result.has_errors:
            status = Panel(
                "[red]❌ Quality checks failed - please fix the errors above[/red]",
                style="red"
            )
        elif result.has_warnings:
            status = Panel(
                "[yellow]⚠️ Quality checks completed with warnings[/yellow]",
                style="yellow"
            )
        else:
            status = Panel(
                "[green]✅ All quality checks passed![/green]",
                style="green"
            )

        self.console.print(status)
