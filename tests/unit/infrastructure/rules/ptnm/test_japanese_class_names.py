"""Unit tests for PTNM002 Japanese class names rule."""

import ast
from pathlib import Path

from pytestee.domain.analyzers.pattern_analyzer import PatternAnalyzer
from pytestee.domain.models import (
    CheckFailure,
    CheckSeverity,
    CheckSuccess,
    TestClass,
    TestFile,
    TestFunction,
)
from pytestee.domain.rules.naming.japanese_class_names import PTNM002


class TestPTNM002:
    """Test cases for PTNM002 Japanese class names rule."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.rule = PTNM002(PatternAnalyzer())
        self.test_file = TestFile(
            path=Path("/test/dummy.py"),
            content="",
            ast_tree=ast.parse(""),
            test_functions=[],
            test_classes=[],
        )

    def test_rule_properties(self) -> None:
        """Test rule ID, name, and description."""
        assert self.rule.rule_id == "PTNM002"
        assert self.rule.name == "japanese_characters_in_class_name"
        assert "日本語文字" in self.rule.description

    def test_japanese_test_class_returns_success(self) -> None:
        """Test that test class with Japanese characters returns success."""
        test_class = TestClass(
            name="Testユーザー管理",
            lineno=1,
            col_offset=0,
            end_lineno=10,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
            test_methods=["test_create_user"],
        )

        result = self.rule.check_class(test_class, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert result.rule_id == "PTNM002"
        assert "Testユーザー管理" in result.message
        assert "日本語文字が含まれています" in result.message
        assert result.line_number == 1
        assert result.column == 0

    def test_hiragana_test_class_returns_success(self) -> None:
        """Test that test class with hiragana characters returns success."""
        test_class = TestClass(
            name="Testかんり",
            lineno=5,
            col_offset=4,
            end_lineno=15,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
            test_methods=["test_something"],
        )

        result = self.rule.check_class(test_class, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert result.rule_id == "PTNM002"
        assert "Testかんり" in result.message
        assert result.line_number == 5
        assert result.column == 4

    def test_katakana_test_class_returns_success(self) -> None:
        """Test that test class with katakana characters returns success."""
        test_class = TestClass(
            name="Testユーザー",
            lineno=10,
            col_offset=8,
            end_lineno=20,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
            test_methods=["test_method"],
        )

        result = self.rule.check_class(test_class, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert result.rule_id == "PTNM002"
        assert "Testユーザー" in result.message

    def test_english_only_test_class_returns_warning(self) -> None:
        """Test that test class with only English characters returns warning."""
        test_class = TestClass(
            name="TestUserManagement",
            lineno=20,
            col_offset=0,
            end_lineno=30,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
            test_methods=["test_create", "test_delete"],
        )

        result = self.rule.check_class(test_class, self.test_file)

        assert isinstance(result, CheckFailure)
        assert result.severity == CheckSeverity.WARNING
        assert result.rule_id == "PTNM002"
        assert "TestUserManagement" in result.message
        assert "日本語文字が含まれていません" in result.message
        assert "日本語での命名を検討してください" in result.message
        assert result.line_number == 20
        assert result.column == 0

    def test_numbers_and_underscore_test_class_returns_warning(self) -> None:
        """Test that test class with numbers and underscores returns warning."""
        test_class = TestClass(
            name="TestCase123_Example",
            lineno=15,
            col_offset=4,
            end_lineno=25,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
            test_methods=["test_example"],
        )

        result = self.rule.check_class(test_class, self.test_file)

        assert isinstance(result, CheckFailure)
        assert result.severity == CheckSeverity.WARNING
        assert result.rule_id == "PTNM002"
        assert "TestCase123_Example" in result.message
        assert result.line_number == 15
        assert result.column == 4

    def test_non_test_class_returns_failure(self) -> None:
        """Test that non-test class returns failure."""
        test_class = TestClass(
            name="NonTestクラス",
            lineno=25,
            col_offset=0,
            end_lineno=35,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
            test_methods=[],
        )

        result = self.rule.check_class(test_class, self.test_file)

        assert isinstance(result, CheckFailure)
        assert result.rule_id == "PTNM002"
        assert "NonTestクラス" in result.message
        assert "テストクラスではありません" in result.message
        assert result.line_number == 25
        assert result.column == 0

    def test_mixed_characters_test_class_returns_success(self) -> None:
        """Test that test class with mixed Japanese and English returns success."""
        test_class = TestClass(
            name="TestAPIユーザー管理",
            lineno=30,
            col_offset=0,
            end_lineno=40,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
            test_methods=["test_api_call"],
        )

        result = self.rule.check_class(test_class, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert result.rule_id == "PTNM002"
        assert "TestAPIユーザー管理" in result.message
        assert "日本語文字が含まれています" in result.message

    def test_dummy_check_method_returns_success(self) -> None:
        """Test that the dummy check method returns success."""
        test_function = TestFunction(
            name="test_example",
            lineno=1,
            col_offset=0,
            end_lineno=None,
            end_col_offset=None,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert result.rule_id == "PTNM002"
        assert "クラスレベルのルール" in result.message

