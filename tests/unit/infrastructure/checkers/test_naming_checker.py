"""Unit tests for NamingChecker."""

import ast
from pathlib import Path

from pytestee.domain.models import CheckSeverity, TestFile, TestFunction
from pytestee.infrastructure.checkers.naming_checker import NamingChecker


class TestNamingChecker:
    """Test cases for NamingChecker."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.checker = NamingChecker()
        self.test_file = TestFile(
            path=Path("/test/dummy.py"),
            content="",
            ast_tree=ast.parse(""),
            test_functions=[]
        )

    def test_checker_name(self) -> None:
        """Test checker name is correct."""
        assert self.checker.name == "naming_checker"

    def test_check_function_with_japanese_name(self) -> None:
        """Test checking function with Japanese characters in name."""
        test_function = TestFunction(
            name="test_ユーザー登録",
            lineno=1,
            col_offset=0,
            end_lineno=None,
            end_col_offset=None,
            body=[],
            decorators=[],
            docstring=None
        )

        results = self.checker.check_function(test_function, self.test_file)

        assert len(results) == 1
        assert results[0].severity == CheckSeverity.INFO
        assert results[0].rule_id == "PTNM001"
        assert "日本語文字が含まれています" in results[0].message

    def test_check_function_with_english_name(self) -> None:
        """Test checking function with English name."""
        test_function = TestFunction(
            name="test_user_registration",
            lineno=1,
            col_offset=0,
            end_lineno=None,
            end_col_offset=None,
            body=[],
            decorators=[],
            docstring=None
        )

        results = self.checker.check_function(test_function, self.test_file)

        assert len(results) == 1
        assert results[0].severity == CheckSeverity.WARNING
        assert results[0].rule_id == "PTNM001"
        assert "日本語文字が含まれていません" in results[0].message

    def test_check_function_non_test_method(self) -> None:
        """Test checking non-test method."""
        test_function = TestFunction(
            name="helper_method",
            lineno=1,
            col_offset=0,
            end_lineno=None,
            end_col_offset=None,
            body=[],
            decorators=[],
            docstring=None
        )

        results = self.checker.check_function(test_function, self.test_file)

        assert len(results) == 0

    def test_check_file_with_multiple_functions(self) -> None:
        """Test checking entire file with multiple test functions."""
        test_functions = [
            TestFunction(
                name="test_日本語メソッド",
                lineno=1,
                col_offset=0,
                end_lineno=None,
                end_col_offset=None,
                body=[],
                decorators=[],
                docstring=None
            ),
            TestFunction(
                name="test_english_method",
                lineno=5,
                col_offset=0,
                end_lineno=None,
                end_col_offset=None,
                body=[],
                decorators=[],
                docstring=None
            ),
            TestFunction(
                name="helper_method",  # Non-test method
                lineno=9,
                col_offset=0,
                end_lineno=None,
                end_col_offset=None,
                body=[],
                decorators=[],
                docstring=None
            )
        ]

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content="",
            ast_tree=ast.parse(""),
            test_functions=test_functions
        )

        results = self.checker.check(test_file)

        # Should have 2 results (2 test methods)
        assert len(results) == 2

        # Check individual results
        japanese_result = next(r for r in results if r.function_name == "test_日本語メソッド")
        assert japanese_result.severity == CheckSeverity.INFO

        english_result = next(r for r in results if r.function_name == "test_english_method")
        assert english_result.severity == CheckSeverity.WARNING
