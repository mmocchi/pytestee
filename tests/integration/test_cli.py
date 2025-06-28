"""Integration tests for CLI commands."""

from pathlib import Path

from click.testing import CliRunner

from pytestee.adapters.cli.commands import cli


class TestCLI:
    """Integration tests for CLI functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures"

    def test_check_command_with_good_file(self) -> None:
        """Test check command with a good test file."""
        result = self.runner.invoke(
            cli, ["check", str(self.fixtures_dir / "good_aaa_test.py"), "--config", ".pytestee-test.toml"]
        )

        assert result.exit_code == 0
        assert "Analysis Summary" in result.output

    def test_check_command_with_bad_file(self) -> None:
        """Test check command with a bad test file."""
        result = self.runner.invoke(
            cli, ["check", str(self.fixtures_dir / "bad_test.py")]
        )

        # Should exit with error code due to quality issues
        assert result.exit_code != 0
        assert "Analysis Summary" in result.output

    def test_check_command_with_options(self) -> None:
        """Test check command with various options."""
        result = self.runner.invoke(
            cli,
            [
                "check",
                str(self.fixtures_dir / "good_aaa_test.py"),
                "--verbose",
                "--config", ".pytestee-test.toml"
            ],
        )

        assert result.exit_code == 0

    def test_info_command(self) -> None:
        """Test info command."""
        result = self.runner.invoke(cli, ["info", str(self.fixtures_dir)])

        assert result.exit_code == 0
        assert "Test Files Summary" in result.output

    def test_list_checkers_command(self) -> None:
        """Test list-checkers command."""
        result = self.runner.invoke(cli, ["list-checkers"])

        assert result.exit_code == 0
        # Registry is currently empty as we moved to rule-based system
        assert (
            "No checkers available" in result.output
            or "Available Checkers" in result.output
        )

    def test_check_nonexistent_file(self) -> None:
        """Test check command with nonexistent file."""
        result = self.runner.invoke(cli, ["check", "/nonexistent/file.py"])

        assert result.exit_code != 0

    def test_check_directory(self) -> None:
        """Test check command with directory."""
        result = self.runner.invoke(cli, ["check", str(self.fixtures_dir)])

        # Should process multiple files in directory
        assert "Analysis Summary" in result.output

    def test_quiet_mode(self) -> None:
        """Test check command in quiet mode."""
        result = self.runner.invoke(
            cli, ["check", str(self.fixtures_dir / "bad_test.py"), "--quiet"]
        )

        # Should have less output in quiet mode
        assert len(result.output) < 4000  # Arbitrary threshold for "less output" (updated for PTEC rules)

    def test_json_output_format(self) -> None:
        """Test check command with JSON output."""
        result = self.runner.invoke(
            cli,
            ["check", str(self.fixtures_dir / "good_aaa_test.py"), "--format", "json", "--config", ".pytestee-test.toml"],
        )

        assert result.exit_code == 0
        # Should contain JSON structure
        assert "{" in result.output
        assert "summary" in result.output
