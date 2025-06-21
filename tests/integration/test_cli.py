"""Integration tests for CLI commands."""

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from pytestee.adapters.cli.commands import cli


class TestCLI:
    """Integration tests for CLI functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures"
    
    def test_check_command_with_good_file(self):
        """Test check command with a good test file."""
        result = self.runner.invoke(cli, [
            "check", 
            str(self.fixtures_dir / "good_aaa_test.py")
        ])
        
        assert result.exit_code == 0
        assert "Analysis Summary" in result.output
    
    def test_check_command_with_bad_file(self):
        """Test check command with a bad test file."""
        result = self.runner.invoke(cli, [
            "check", 
            str(self.fixtures_dir / "bad_test.py")
        ])
        
        # Should exit with error code due to quality issues
        assert result.exit_code != 0
        assert "Analysis Summary" in result.output
    
    def test_check_command_with_options(self):
        """Test check command with various options."""
        result = self.runner.invoke(cli, [
            "check", 
            str(self.fixtures_dir / "good_aaa_test.py"),
            "--max-asserts", "5",
            "--min-asserts", "1",
            "--verbose"
        ])
        
        assert result.exit_code == 0
    
    def test_info_command(self):
        """Test info command."""
        result = self.runner.invoke(cli, [
            "info", 
            str(self.fixtures_dir)
        ])
        
        assert result.exit_code == 0
        assert "Test Files Summary" in result.output
    
    def test_list_checkers_command(self):
        """Test list-checkers command."""
        result = self.runner.invoke(cli, ["list-checkers"])
        
        assert result.exit_code == 0
        assert "Available Checkers" in result.output
        assert "aaa_pattern" in result.output
        assert "assert_density" in result.output
    
    def test_check_nonexistent_file(self):
        """Test check command with nonexistent file."""
        result = self.runner.invoke(cli, [
            "check", 
            "/nonexistent/file.py"
        ])
        
        assert result.exit_code != 0
    
    def test_check_directory(self):
        """Test check command with directory."""
        result = self.runner.invoke(cli, [
            "check", 
            str(self.fixtures_dir)
        ])
        
        # Should process multiple files in directory
        assert "Analysis Summary" in result.output
    
    def test_quiet_mode(self):
        """Test check command in quiet mode."""
        result = self.runner.invoke(cli, [
            "check", 
            str(self.fixtures_dir / "bad_test.py"),
            "--quiet"
        ])
        
        # Should have less output in quiet mode
        assert len(result.output) < 1000  # Arbitrary threshold for "less output"
    
    def test_json_output_format(self):
        """Test check command with JSON output."""
        result = self.runner.invoke(cli, [
            "check", 
            str(self.fixtures_dir / "good_aaa_test.py"),
            "--format", "json"
        ])
        
        assert result.exit_code == 0
        # Should contain JSON structure
        assert "{" in result.output
        assert "summary" in result.output