"""Unit tests for PTCM001 AAA Comment Pattern rule."""

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
from pytestee.domain.rules.comment.aaa_comment_pattern import PTCM001


class TestPTCM001:
    """Test cases for PTCM001 AAA Comment Pattern rule."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.rule = PTCM001(PatternAnalyzer())

    def test_rule_properties(self) -> None:
        """Test rule ID, name, and description."""
        assert self.rule.rule_id == "PTCM001"
        assert self.rule.name == "aaa_pattern_comments"
        assert "AAA (Arrange, Act, Assert)" in self.rule.description

    def test_aaa_pattern_found_returns_success(self) -> None:
        """Test that function with AAA pattern comments returns success."""
        content = """def test_something():
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
        assert "AAA pattern detected in comments" in result.message

    def test_lowercase_aaa_pattern_found_returns_success(self) -> None:
        """Test that function with lowercase AAA pattern comments returns success."""
        content = """def test_lowercase():
    # arrange
    data = [1, 2, 3]

    # act
    length = len(data)

    # assert
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
        assert "AAA pattern detected in comments" in result.message

    def test_mixed_case_aaa_pattern_found_returns_success(self) -> None:
        """Test that function with mixed case AAA pattern comments returns success."""
        content = """def test_mixed_case():
    # ARRANGE
    user = User("test")

    # act
    result = user.get_name()

    # Assert
    assert result == "test\""""

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
        assert "AAA pattern detected in comments" in result.message

    def test_missing_arrange_returns_failure(self) -> None:
        """Test that function missing Arrange comment returns failure."""
        content = """def test_missing_arrange():
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
            name="test_missing_arrange",
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
        assert "AAA pattern not detected in comments" in result.message
        assert "Consider adding # Arrange, # Act, # Assert" in result.message

    def test_missing_act_returns_failure(self) -> None:
        """Test that function missing Act comment returns failure."""
        content = """def test_missing_act():
    # Arrange
    x = 1
    y = 2

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
            name="test_missing_act",
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
        assert "AAA pattern not detected in comments" in result.message

    def test_missing_assert_returns_failure(self) -> None:
        """Test that function missing Assert comment returns failure."""
        content = """def test_missing_assert():
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
            name="test_missing_assert",
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
        assert "AAA pattern not detected in comments" in result.message

    def test_assert_comment_with_word_in_comment_returns_success(self) -> None:
        """Test that assert word in comment counts for assert pattern."""
        content = """def test_assert_in_comment():
    # Arrange
    value = 42

    # Act
    result = str(value)

    # Check assert that result is string
    assert isinstance(result, str)"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_assert_in_comment",
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
        assert "AAA pattern not detected in comments" in result.message

    def test_conflicting_rules(self) -> None:
        """Test that conflicting rules are correctly identified."""
        conflicting = self.rule.get_conflicting_rules()
        expected = {"PTCM003"}
        assert conflicting == expected

    def test_aaa_with_extra_text_returns_success(self) -> None:
        """Test that AAA comments with extra text still work."""
        content = """def test_aaa_with_extra():
    # Arrange - Setup test data
    user_id = 123

    # Act - Perform the operation
    user = get_user(user_id)

    # Assert - Verify the result
    assert user.id == user_id"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_aaa_with_extra",
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

        assert result.rule_id == "PTCM001"
        assert result.checker_name == "aaa_pattern_comments"
        assert result.function_name == "test_metadata"
        assert result.line_number == 42
        assert result.file_path == Path("/test/dummy.py")

    def test_ignores_aaa_patterns_in_strings(self) -> None:
        """Test that AAA patterns inside strings are ignored."""
        content = """def test_with_string_patterns():
    message1 = "This has # Arrange in string"
    message2 = "And # Act here"
    message3 = "Finally # Assert text"
    result = process_messages(message1, message2, message3)
    assert result is not None"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_with_string_patterns",
            lineno=1,
            col_offset=0,
            end_lineno=6,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        # Should fail because there are no actual AAA comments, only strings containing the patterns
        assert isinstance(result, CheckFailure)
        assert "AAA pattern not detected in comments" in result.message

    def test_detects_real_aaa_comments_with_strings_present(self) -> None:
        """Test that real AAA comments are detected even when strings with patterns are present."""
        content = """def test_with_both_strings_and_comments():
    # Arrange
    message = "This string has # Act pattern in it"
    another = "And # Assert too"

    # Act
    result = process_message(message)

    # Assert
    assert result is not None"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_with_both_strings_and_comments",
            lineno=1,
            col_offset=0,
            end_lineno=10,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        # Should succeed because there are real AAA comments present
        assert isinstance(result, CheckSuccess)
        assert "AAA pattern detected in comments" in result.message
