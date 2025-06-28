"""Unit tests for PTCM003 AAA or GWT Comment Pattern rule."""

import ast
from pathlib import Path

from pytestee.domain.analyzers.pattern_analyzer import PatternAnalyzer
from pytestee.domain.models import (
    CheckFailure,
    CheckSeverity,
    CheckSuccess,
    TestFile,
    TestFunction,
)
from pytestee.domain.rules.comment.aaa_or_gwt_pattern import PTCM003


class TestPTCM003:
    """Test cases for PTCM003 AAA or GWT Comment Pattern rule."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.rule = PTCM003(PatternAnalyzer())

    def test_rule_properties(self) -> None:
        """Test rule ID, name, and description."""
        assert self.rule.rule_id == "PTCM003"
        assert self.rule.name == "aaa_or_gwt_pattern_comments"
        assert "AAA or GWT pattern" in self.rule.description
        assert "either pattern is acceptable" in self.rule.description

    def test_aaa_pattern_found_returns_success(self) -> None:
        """Test that function with AAA pattern comments returns success."""
        content = """def test_aaa_pattern():
    # Arrange
    x = 1
    y = 2

    # Act
    result = x + y

    # Assert
    assert result == 3"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_aaa_pattern",
            lineno=1,
            col_offset=0,
            end_lineno=9,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "AAA pattern detected in comments" in result.message

    def test_gwt_pattern_found_returns_success(self) -> None:
        """Test that function with GWT pattern comments returns success."""
        content = """def test_gwt_pattern():
    # Given
    user = User("test")

    # When
    result = user.get_name()

    # Then
    assert result == "test\""""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_gwt_pattern",
            lineno=1,
            col_offset=0,
            end_lineno=8,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "GWT pattern detected in comments" in result.message

    def test_aaa_pattern_precedence_over_gwt(self) -> None:
        """Test that AAA pattern takes precedence when both patterns exist."""
        content = """def test_both_patterns():
    # Arrange (Given)
    x = 1
    y = 2

    # Act (When)
    result = x + y

    # Assert (Then)
    assert result == 3"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_both_patterns",
            lineno=1,
            col_offset=0,
            end_lineno=9,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        # AAA should take precedence per the analyzer implementation
        assert "AAA pattern detected in comments" in result.message

    def test_no_pattern_returns_failure(self) -> None:
        """Test that function with no recognizable pattern returns failure."""
        content = """def test_no_pattern():
    # Setup
    x = 1
    y = 2

    # Execute
    result = x + y

    # Verify
    assert result == 3"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_no_pattern",
            lineno=1,
            col_offset=0,
            end_lineno=9,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert result.severity == CheckSeverity.ERROR
        assert "Neither AAA nor GWT pattern detected" in result.message
        assert "Consider adding pattern comments" in result.message
        assert "# Arrange, # Act, # Assert" in result.message
        assert "# Given, # When, # Then" in result.message

    def test_partial_aaa_pattern_returns_failure(self) -> None:
        """Test that partial AAA pattern is not accepted."""
        content = """def test_partial_aaa():
    # Arrange
    x = 1
    y = 2

    # Act
    result = x + y

    assert result == 3"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_partial_aaa",
            lineno=1,
            col_offset=0,
            end_lineno=8,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Neither AAA nor GWT pattern detected" in result.message

    def test_partial_gwt_pattern_returns_failure(self) -> None:
        """Test that partial GWT pattern is not accepted."""
        content = """def test_partial_gwt():
    # Given
    user = User("test")

    # When
    result = user.get_name()

    assert result == "test\""""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_partial_gwt",
            lineno=1,
            col_offset=0,
            end_lineno=7,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Neither AAA nor GWT pattern detected" in result.message

    def test_no_comments_returns_failure(self) -> None:
        """Test that function with no comments returns failure."""
        content = """def test_no_comments():
    x = 1
    y = 2
    result = x + y
    assert result == 3"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_no_comments",
            lineno=1,
            col_offset=0,
            end_lineno=5,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Neither AAA nor GWT pattern detected" in result.message

    def test_conflicting_rules(self) -> None:
        """Test that conflicting rules are correctly identified."""
        conflicting = self.rule.get_conflicting_rules()
        expected = {"PTCM001", "PTCM002"}
        assert conflicting == expected

    def test_case_insensitive_aaa_pattern(self) -> None:
        """Test that AAA pattern detection is case insensitive."""
        content = """def test_case_insensitive():
    # ARRANGE
    value = 42

    # act
    result = str(value)

    # Assert
    assert isinstance(result, str)"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_case_insensitive",
            lineno=1,
            col_offset=0,
            end_lineno=8,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "AAA pattern detected in comments" in result.message

    def test_case_insensitive_gwt_pattern(self) -> None:
        """Test that GWT pattern detection is case insensitive."""
        content = """def test_gwt_case_insensitive():
    # GIVEN
    calculator = Calculator()

    # when
    result = calculator.add(2, 3)

    # Then
    assert result == 5"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_gwt_case_insensitive",
            lineno=1,
            col_offset=0,
            end_lineno=8,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "GWT pattern detected in comments" in result.message

    def test_mixed_patterns_in_comments(self) -> None:
        """Test behavior when comments contain mixed pattern keywords."""
        content = """def test_mixed_patterns():
    # Arrange (Given setup)
    x = 1

    # Act
    result = x + 1

    # Assert (Then verify)
    assert result == 2"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_mixed_patterns",
            lineno=1,
            col_offset=0,
            end_lineno=8,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        # Should detect AAA pattern since it takes precedence
        assert "AAA pattern detected in comments" in result.message

    def test_result_contains_correct_metadata(self) -> None:
        """Test that results contain correct metadata."""
        content = """def test_metadata():
    # Arrange
    x = 1
    # Act
    y = x + 1
    # Assert
    assert y == 2"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_metadata",
            lineno=42,
            col_offset=4,
            end_lineno=48,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert result.rule_id == "PTCM003"
        assert result.checker_name == "aaa_or_gwt_pattern_comments"
        assert result.function_name == "test_metadata"
        assert result.line_number == 42
        assert result.file_path == Path("/test/dummy.py")
