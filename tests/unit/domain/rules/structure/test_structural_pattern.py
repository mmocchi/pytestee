"""Unit tests for PTST001 Structural Pattern rule."""

import ast
from pathlib import Path

from pytestee.domain.models import (
    CheckFailure,
    CheckSeverity,
    CheckSuccess,
    TestFile,
    TestFunction,
)
from pytestee.domain.rules.structure.structural_pattern import PTST001


class TestPTST001:
    """Test cases for PTST001 Structural Pattern rule."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.rule = PTST001()

    def test_rule_properties(self) -> None:
        """Test rule ID, name, and description."""
        assert self.rule.rule_id == "PTST001"
        assert self.rule.name == "aaa_pattern_structural"
        assert "empty lines separating code sections" in self.rule.description

    def test_clear_aaa_structure_returns_success(self) -> None:
        """Test that function with clear AAA structure returns success."""
        content = """def test_clear_structure():
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
            name="test_clear_structure",
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
        assert "AAA pattern detected through structural separation" in result.message

    def test_three_sections_without_comments_returns_success(self) -> None:
        """Test that function with three sections separated by empty lines returns success."""
        content = """def test_three_sections():
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
            name="test_three_sections",
            lineno=1,
            col_offset=0,
            end_lineno=7,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "AAA pattern detected through structural separation" in result.message

    def test_two_sections_with_assert_returns_success(self) -> None:
        """Test that function with two sections where last has assert returns success."""
        content = """def test_two_sections():
    x = 1
    result = x + 1
    
    # Second section
    
    assert result == 2"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_two_sections",
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
        assert "AAA pattern detected through structural separation" in result.message

    def test_no_empty_lines_returns_failure(self) -> None:
        """Test that function without empty lines returns failure."""
        content = """def test_no_empty_lines():
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
            name="test_no_empty_lines",
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
        assert result.severity == CheckSeverity.ERROR
        assert "AAA pattern not detected through structural separation" in result.message
        assert "Consider using empty lines to separate Arrange, Act, Assert sections" in result.message

    def test_one_empty_line_only_returns_failure(self) -> None:
        """Test that function with only one empty line returns failure."""
        content = """def test_one_empty_line():
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
            name="test_one_empty_line",
            lineno=1,
            col_offset=0,
            end_lineno=6,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "AAA pattern not detected through structural separation" in result.message

    def test_empty_lines_but_no_assert_returns_failure(self) -> None:
        """Test that function with empty lines but no assert returns failure."""
        content = """def test_no_assert():
    x = 1
    y = 2
    
    result = x + y
    
    print(result)"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_no_assert",
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
        assert "AAA pattern not detected through structural separation" in result.message

    def test_multiple_empty_lines_returns_success(self) -> None:
        """Test that function with multiple empty lines still works."""
        content = """def test_multiple_empty():
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
            name="test_multiple_empty",
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
        assert "AAA pattern detected through structural separation" in result.message

    def test_assert_in_middle_section_returns_success(self) -> None:
        """Test that assert in any section counts for pattern detection."""
        content = """def test_assert_middle():
    x = 1
    
    assert x == 1
    result = x + 1
    
    print(result)
    assert result == 2"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_assert_middle",
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
        assert "AAA pattern detected through structural separation" in result.message

    def test_empty_function_returns_failure(self) -> None:
        """Test that empty function returns failure."""
        content = """def test_empty():
    pass"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_empty",
            lineno=1,
            col_offset=0,
            end_lineno=2,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "AAA pattern not detected through structural separation" in result.message

    def test_function_with_only_empty_lines_returns_failure(self) -> None:
        """Test that function with only empty lines returns failure."""
        content = """def test_only_empty():
    pass
    
    """

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_only_empty",
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
        assert "AAA pattern not detected through structural separation" in result.message

    def test_sections_analysis_with_complex_structure(self) -> None:
        """Test section analysis with complex structure."""
        content = """def test_complex():
    # Setup data
    data = [1, 2, 3]
    processor = DataProcessor()
    
    # Process the data
    result = processor.process(data)
    processed = result.get_values()
    
    # Verify results
    assert len(processed) == 3
    assert all(x > 0 for x in processed)"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        test_function = TestFunction(
            name="test_complex",
            lineno=1,
            col_offset=0,
            end_lineno=11,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "AAA pattern detected through structural separation" in result.message

    def test_analyze_sections_method(self) -> None:
        """Test the _analyze_sections method directly."""
        function_lines = [
            "def test_sections():",
            "    x = 1",
            "    y = 2",
            "",  # empty line at index 3
            "    result = x + y",
            "",  # empty line at index 5
            "    assert result == 3"
        ]
        empty_line_indices = [3, 5]
        
        sections = self.rule._analyze_sections(function_lines, empty_line_indices)
        
        assert len(sections) == 3
        assert "x = 1" in sections[0][0]
        assert "y = 2" in sections[0][1]
        assert "result = x + y" in sections[1][0]
        assert "assert result == 3" in sections[2][0]

    def test_looks_like_aaa_structure_method(self) -> None:
        """Test the _looks_like_aaa_structure method directly."""
        # Valid AAA structure
        sections_with_assert = [
            ["x = 1", "y = 2"],
            ["result = x + y"],
            ["assert result == 3"]
        ]
        assert self.rule._looks_like_aaa_structure(sections_with_assert) is True
        
        # No assert in any section
        sections_no_assert = [
            ["x = 1", "y = 2"],
            ["result = x + y"],
            ["print(result)"]
        ]
        assert self.rule._looks_like_aaa_structure(sections_no_assert) is False
        
        # Only one section
        sections_one = [["x = 1"]]
        assert self.rule._looks_like_aaa_structure(sections_one) is False
        
        # Two sections with assert
        sections_two_with_assert = [
            ["x = 1", "result = x + 1"],
            ["assert result == 2"]
        ]
        assert self.rule._looks_like_aaa_structure(sections_two_with_assert) is True

    def test_result_contains_correct_metadata(self) -> None:
        """Test that results contain correct metadata."""
        content = """def test_metadata():
    x = 1
    
    result = x + 1
    
    assert result == 2"""

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

        assert result.rule_id == "PTST001"
        assert result.checker_name == "aaa_pattern_structural"
        assert result.function_name == "test_metadata"
        assert result.line_number == 42
        assert result.file_path == Path("/test/dummy.py")