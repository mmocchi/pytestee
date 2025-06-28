"""Unit tests for PTCM002 GWT Comment Pattern rule."""

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
from pytestee.domain.rules.comment.gwt_comment_pattern import PTCM002


class TestPTCM002:
    """Test cases for PTCM002 GWT Comment Pattern rule."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.rule = PTCM002(PatternAnalyzer())

    def test_rule_properties(self) -> None:
        """Test rule ID, name, and description."""
        assert self.rule.rule_id == "PTCM002"
        assert self.rule.name == "gwt_pattern_comments"
        assert "GWT (Given, When, Then)" in self.rule.description

    def test_gwt_pattern_found_returns_success(self) -> None:
        """Test that function with GWT pattern comments returns success."""
        content = """def test_something():
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
            name="test_something",
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
        assert "GWT pattern detected in comments" in result.message

    def test_lowercase_gwt_pattern_found_returns_success(self) -> None:
        """Test that function with lowercase GWT pattern comments returns success."""
        content = """def test_lowercase():
    # given
    data = [1, 2, 3]
    
    # when
    length = len(data)
    
    # then
    assert length == 3"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_lowercase",
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

    def test_mixed_case_gwt_pattern_found_returns_success(self) -> None:
        """Test that function with mixed case GWT pattern comments returns success."""
        content = """def test_mixed_case():
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
            name="test_mixed_case",
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

    def test_missing_given_returns_failure(self) -> None:
        """Test that function missing Given comment returns failure."""
        content = """def test_missing_given():
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
            name="test_missing_given",
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
        assert result.severity == CheckSeverity.ERROR
        assert "GWT pattern not detected in comments" in result.message
        assert "Consider adding # Given, # When, # Then" in result.message

    def test_missing_when_returns_failure(self) -> None:
        """Test that function missing When comment returns failure."""
        content = """def test_missing_when():
    # Given
    user = User("test")
    
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
            name="test_missing_when",
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
        assert "GWT pattern not detected in comments" in result.message

    def test_missing_then_returns_failure(self) -> None:
        """Test that function missing Then comment returns failure."""
        content = """def test_missing_then():
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
            name="test_missing_then",
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
        assert "GWT pattern not detected in comments" in result.message

    def test_when_and_then_words_in_comments_returns_success(self) -> None:
        """Test that when/then words in comments count for pattern detection."""
        content = """def test_words_in_comments():
    # Given
    value = 42
    
    # Check when value is processed
    result = process(value)
    
    # Verify then result is correct
    assert result is not None"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_words_in_comments",
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

    def test_no_comments_returns_failure(self) -> None:
        """Test that function with no comments returns failure."""
        content = """def test_no_comments():
    user = User("test")
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
            name="test_no_comments",
            lineno=1,
            col_offset=0,
            end_lineno=4,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "GWT pattern not detected in comments" in result.message

    def test_conflicting_rules(self) -> None:
        """Test that conflicting rules are correctly identified."""
        conflicting = self.rule.get_conflicting_rules()
        expected = {"PTCM003"}
        assert conflicting == expected

    def test_gwt_with_extra_text_returns_success(self) -> None:
        """Test that GWT comments with extra text still work."""
        content = """def test_gwt_with_extra():
    # Given - Setup test data
    account_id = 123
    
    # When - Perform the withdrawal
    result = withdraw_money(account_id, 50)
    
    # Then - Verify the operation
    assert result.success is True"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_gwt_with_extra",
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

    def test_partial_gwt_patterns_return_failure(self) -> None:
        """Test that partial GWT patterns are not accepted."""
        test_cases = [
            (
                """def test_only_given_when():
    # Given
    x = 1
    # When
    y = x + 1
    assert y == 2""",
                "only_given_when"
            ),
            (
                """def test_only_given_then():
    # Given
    x = 1
    y = x + 1
    # Then
    assert y == 2""",
                "only_given_then"
            ),
            (
                """def test_only_when_then():
    x = 1
    # When
    y = x + 1
    # Then
    assert y == 2""",
                "only_when_then"
            ),
        ]

        for content, test_name in test_cases:
            test_file = TestFile(
                path=Path("/test/dummy.py"),
                content=content,
                ast_tree=ast.parse(content),
                test_functions=[],
                test_classes=[],
            )

            test_function = TestFunction(
                name=test_name,
                lineno=1,
                col_offset=0,
                end_lineno=6,
                end_col_offset=0,
                body=[],
                decorators=[],
                docstring=None,
            )

            result = self.rule.check(test_function, test_file)

            assert isinstance(result, CheckFailure), f"Failed for {test_name}"
            assert "GWT pattern not detected in comments" in result.message

    def test_result_contains_correct_metadata(self) -> None:
        """Test that results contain correct metadata."""
        content = """def test_metadata():
    # Given
    x = 1
    # When
    y = x + 1
    # Then
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

        assert result.rule_id == "PTCM002"
        assert result.checker_name == "gwt_pattern_comments"
        assert result.function_name == "test_metadata"
        assert result.line_number == 42
        assert result.file_path == Path("/test/dummy.py")