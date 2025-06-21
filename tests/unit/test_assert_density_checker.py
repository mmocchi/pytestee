"""Unit tests for assert density checker."""

from pathlib import Path

import pytest

from pytestee.infrastructure.checkers.assert_density_checker import AssertDensityChecker
from pytestee.infrastructure.ast_parser import ASTParser
from pytestee.domain.models import CheckSeverity, CheckerConfig


class TestAssertDensityChecker:
    """Test cases for assert density checker."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.checker = AssertDensityChecker()
        self.parser = ASTParser()
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures"
    
    def test_checker_name(self):
        """Test checker name is correct."""
        assert self.checker.name == "assert_density"
    
    def test_check_no_assertions(self):
        """Test detection of functions with no assertions."""
        test_file_path = self.fixtures_dir / "bad_test.py"
        test_file = self.parser.parse_file(test_file_path)
        
        # Find the function with no assertions
        target_function = None
        for func in test_file.test_functions:
            if func.name == "test_no_assertions":
                target_function = func
                break
        
        assert target_function is not None
        results = self.checker.check_function(target_function, test_file)
        
        # Should have error for no assertions
        error_results = [r for r in results if r.severity == CheckSeverity.ERROR]
        assert len(error_results) > 0
        assert any("No assertions found" in result.message for result in error_results)
    
    def test_check_too_many_assertions(self):
        """Test detection of functions with too many assertions."""
        test_file_path = self.fixtures_dir / "bad_test.py"
        test_file = self.parser.parse_file(test_file_path)
        
        # Find the function with too many assertions
        target_function = None
        for func in test_file.test_functions:
            if func.name == "test_too_many_assertions":
                target_function = func
                break
        
        assert target_function is not None
        results = self.checker.check_function(target_function, test_file)
        
        # Should have warning for too many assertions
        warning_results = [r for r in results if r.severity == CheckSeverity.WARNING]
        assert len(warning_results) > 0
        assert any("Too many assertions" in result.message for result in warning_results)
    
    def test_check_good_assertion_count(self):
        """Test detection of functions with good assertion count."""
        test_file_path = self.fixtures_dir / "good_aaa_test.py"
        test_file = self.parser.parse_file(test_file_path)
        
        target_function = test_file.test_functions[0]  # Use first function
        results = self.checker.check_function(target_function, test_file)
        
        # Should have at least one positive result
        info_results = [r for r in results if r.severity == CheckSeverity.INFO]
        assert len(info_results) > 0
        assert any("Assertion count OK" in result.message for result in info_results)
    
    def test_custom_config(self):
        """Test checker with custom configuration."""
        test_file_path = self.fixtures_dir / "good_aaa_test.py"
        test_file = self.parser.parse_file(test_file_path)
        
        config = CheckerConfig(
            name="assert_density",
            enabled=True,
            config={
                "max_asserts": 1,  # Very strict
                "min_asserts": 1
            }
        )
        
        target_function = test_file.test_functions[0]
        results = self.checker.check_function(target_function, test_file, config)
        
        # With strict config, might get warnings for functions with 2+ assertions
        assert len(results) > 0
    
    def test_count_effective_lines(self):
        """Test counting effective lines of code."""
        test_file_path = self.fixtures_dir / "good_aaa_test.py"
        test_file = self.parser.parse_file(test_file_path)
        
        target_function = test_file.test_functions[0]
        effective_lines = self.checker._count_effective_lines(target_function, test_file)
        
        assert effective_lines > 0
        # Should exclude blank lines and comments
        assert effective_lines < len(test_file.content.split('\n'))
    
    def test_analyze_test_complexity(self):
        """Test test complexity analysis."""
        test_file_path = self.fixtures_dir / "good_aaa_test.py"
        test_file = self.parser.parse_file(test_file_path)
        
        target_function = test_file.test_functions[0]
        analysis = self.checker.analyze_test_complexity(target_function, test_file)
        
        assert "assert_count" in analysis
        assert "effective_lines" in analysis
        assert "total_lines" in analysis
        assert "assert_density" in analysis
        assert "complexity_score" in analysis
        assert "recommendations" in analysis
        
        assert analysis["assert_count"] >= 0
        assert analysis["effective_lines"] >= 0
        assert analysis["complexity_score"] >= 1
        assert isinstance(analysis["recommendations"], list)
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        # Test with no assertions
        recommendations = self.checker._generate_recommendations(0, 10, 1)
        assert "Add assertions" in str(recommendations)
        
        # Test with too many assertions
        recommendations = self.checker._generate_recommendations(10, 10, 1)
        assert "splitting" in str(recommendations).lower()
        
        # Test with high complexity
        recommendations = self.checker._generate_recommendations(2, 10, 5)
        assert "complexity" in str(recommendations).lower()
    
    def test_check_file_with_multiple_functions(self):
        """Test checking entire file with multiple functions."""
        test_file_path = self.fixtures_dir / "bad_test.py"
        test_file = self.parser.parse_file(test_file_path)
        
        results = self.checker.check(test_file)
        
        # Should have results for all test functions
        assert len(results) > 0
        
        # Should have at least some error/warning results for the bad test file
        problematic_results = [r for r in results if r.severity != CheckSeverity.INFO]
        assert len(problematic_results) > 0