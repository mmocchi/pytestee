"""Unit tests for AAA pattern checker."""

from pathlib import Path

import pytest

from pytestee.infrastructure.checkers.aaa_pattern_checker import AAAPatternChecker
from pytestee.infrastructure.ast_parser import ASTParser
from pytestee.domain.models import CheckSeverity


class TestAAAPatternChecker:
    """Test cases for AAA pattern checker."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.checker = AAAPatternChecker()
        self.parser = ASTParser()
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures"
    
    def test_checker_name(self):
        """Test checker name is correct."""
        assert self.checker.name == "aaa_pattern"
    
    def test_check_good_aaa_pattern_with_comments(self):
        """Test detection of good AAA pattern with comments."""
        test_file_path = self.fixtures_dir / "good_aaa_test.py"
        test_file = self.parser.parse_file(test_file_path)
        
        # Find the function with AAA comments
        target_function = None
        for func in test_file.test_functions:
            if func.name == "test_user_creation_with_aaa_comments":
                target_function = func
                break
        
        assert target_function is not None
        results = self.checker.check_function(target_function, test_file)
        
        # Should have at least one positive result
        info_results = [r for r in results if r.severity == CheckSeverity.INFO]
        assert len(info_results) > 0
        assert any("AAA pattern detected" in result.message for result in info_results)
    
    def test_check_structural_aaa_pattern(self):
        """Test detection of structural AAA pattern."""
        test_file_path = self.fixtures_dir / "good_aaa_test.py"
        test_file = self.parser.parse_file(test_file_path)
        
        # Find the function with structural separation
        target_function = None
        for func in test_file.test_functions:
            if func.name == "test_user_creation_with_structural_separation":
                target_function = func
                break
        
        assert target_function is not None
        results = self.checker.check_function(target_function, test_file)
        
        # Should detect some form of pattern
        assert len(results) > 0
    
    def test_check_no_clear_pattern(self):
        """Test detection when no clear pattern exists."""
        test_file_path = self.fixtures_dir / "bad_test.py"
        test_file = self.parser.parse_file(test_file_path)
        
        # Find the function without clear pattern
        target_function = None
        for func in test_file.test_functions:
            if func.name == "test_no_clear_pattern":
                target_function = func
                break
        
        assert target_function is not None
        results = self.checker.check_function(target_function, test_file)
        
        # This function actually has logical flow pattern detected, so should have some results
        assert len(results) > 0
        # Should detect logical pattern (info result)
        info_results = [r for r in results if r.severity == CheckSeverity.INFO]
        assert len(info_results) > 0
    
    def test_check_patterns_in_comments(self):
        """Test pattern detection in comments."""
        comments = [
            (1, "# Arrange some data"),
            (2, "# Act on the data"),
            (3, "# Assert the results")
        ]
        
        aaa_patterns = [r'#\s*arrange', r'#\s*act', r'#\s*assert']
        found = self.checker._check_patterns_in_comments(comments, aaa_patterns)
        assert found == 3
    
    def test_looks_like_aaa_structure(self):
        """Test AAA structure detection."""
        # Structure with assert in last section
        good_sections = [
            ["user = User()"],
            ["result = user.process()"],
            ["assert result is True"]
        ]
        assert self.checker._looks_like_aaa_structure(good_sections)
        
        # Structure without assert
        bad_sections = [
            ["user = User()"],
            ["result = user.process()"],
            ["print(result)"]
        ]
        assert not self.checker._looks_like_aaa_structure(bad_sections)
    
    def test_check_file_with_multiple_functions(self):
        """Test checking entire file with multiple functions."""
        test_file_path = self.fixtures_dir / "good_aaa_test.py"
        test_file = self.parser.parse_file(test_file_path)
        
        results = self.checker.check(test_file)
        
        # Should have results for all test functions
        assert len(results) >= len(test_file.test_functions)
        
        # Check that results are associated with correct functions
        function_names = {result.function_name for result in results}
        expected_names = {func.name for func in test_file.test_functions}
        assert function_names == expected_names