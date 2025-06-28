"""Unit tests for PTAS003 High Assertion Density rule."""

import ast
from pathlib import Path

from pytestee.domain.analyzers.assertion_analyzer import AssertionAnalyzer
from pytestee.domain.models import (
    CheckerConfig,
    CheckFailure,
    CheckSeverity,
    CheckSuccess,
    TestFile,
    TestFunction,
)
from pytestee.domain.rules.assertion.high_assertion_density import PTAS003


class TestPTAS003:
    """Test cases for PTAS003 High Assertion Density rule."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.rule = PTAS003(AssertionAnalyzer())

    def test_rule_properties(self) -> None:
        """Test rule ID, name, and description."""
        assert self.rule.rule_id == "PTAS003"
        assert self.rule.name == "high_assertion_density"
        assert "High ratio of assertions" in self.rule.description

    def test_low_density_returns_success(self) -> None:
        """Test that function with low assertion density returns success."""
        # Create test content with function having 1 assertion in 4 lines (25% density)
        content = """def test_something():
    x = 1
    y = 2
    z = x + y
    assert z == 3"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        body = [
            ast.Assign(targets=[ast.Name(id="x", ctx=ast.Store())], value=ast.Constant(value=1)),
            ast.Assign(targets=[ast.Name(id="y", ctx=ast.Store())], value=ast.Constant(value=2)),
            ast.Assign(
                targets=[ast.Name(id="z", ctx=ast.Store())],
                value=ast.BinOp(
                    left=ast.Name(id="x", ctx=ast.Load()),
                    op=ast.Add(),
                    right=ast.Name(id="y", ctx=ast.Load()),
                ),
            ),
            ast.Assert(
                test=ast.Compare(
                    left=ast.Name(id="z", ctx=ast.Load()),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=3)],
                ),
                msg=None,
            ),
        ]

        test_function = TestFunction(
            name="test_something",
            lineno=1,
            col_offset=0,
            end_lineno=5,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "Assertion density OK: 0.25" in result.message
        assert "1 assertions in 4 lines" in result.message

    def test_high_density_returns_failure(self) -> None:
        """Test that function with high assertion density returns failure."""
        # Create test content with function having 3 assertions in 3 lines (100% density)
        content = """def test_multiple():
    assert 1 == 1
    assert 2 == 2
    assert 3 == 3"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        body: list[ast.stmt] = [
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=1),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=1)],
                ),
                msg=None,
            ),
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=2),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=2)],
                ),
                msg=None,
            ),
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=3),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=3)],
                ),
                msg=None,
            ),
        ]

        test_function = TestFunction(
            name="test_multiple",
            lineno=1,
            col_offset=0,
            end_lineno=4,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert result.severity == CheckSeverity.ERROR
        assert "High assertion density: 1.00" in result.message
        assert "3 assertions in 3 lines" in result.message

    def test_exactly_at_threshold_returns_success(self) -> None:
        """Test that function exactly at density threshold returns success."""
        # Create test content with function having 1 assertion in 2 lines (50% density)
        content = """def test_threshold():
    x = 5
    assert x == 5"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        body = [
            ast.Assign(targets=[ast.Name(id="x", ctx=ast.Store())], value=ast.Constant(value=5)),
            ast.Assert(
                test=ast.Compare(
                    left=ast.Name(id="x", ctx=ast.Load()),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=5)],
                ),
                msg=None,
            ),
        ]

        test_function = TestFunction(
            name="test_threshold",
            lineno=1,
            col_offset=0,
            end_lineno=3,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "Assertion density OK: 0.50" in result.message

    def test_custom_density_threshold(self) -> None:
        """Test with custom density threshold configuration."""
        config = CheckerConfig(name="test_config", config={"max_density": 0.3})  # 30% threshold

        # Function with 40% density (above custom threshold)
        content = """def test_custom():
    x = 1
    y = 2
    assert x == 1
    assert y == 2"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        body = [
            ast.Assign(targets=[ast.Name(id="x", ctx=ast.Store())], value=ast.Constant(value=1)),
            ast.Assign(targets=[ast.Name(id="y", ctx=ast.Store())], value=ast.Constant(value=2)),
            ast.Assert(
                test=ast.Compare(
                    left=ast.Name(id="x", ctx=ast.Load()),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=1)],
                ),
                msg=None,
            ),
            ast.Assert(
                test=ast.Compare(
                    left=ast.Name(id="y", ctx=ast.Load()),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=2)],
                ),
                msg=None,
            ),
        ]

        test_function = TestFunction(
            name="test_custom",
            lineno=1,
            col_offset=0,
            end_lineno=5,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file, config)

        assert isinstance(result, CheckFailure)
        assert "High assertion density: 0.50" in result.message
        assert "2 assertions in 4 lines" in result.message

    def test_empty_function_returns_success(self) -> None:
        """Test that function with no effective lines returns success."""
        content = """def test_empty():
    pass"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        body: list[ast.stmt] = [ast.Pass()]

        test_function = TestFunction(
            name="test_empty",
            lineno=1,
            col_offset=0,
            end_lineno=2,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        # The function has "pass" which counts as 1 effective line
        assert "Assertion density OK: 0.00" in result.message
        assert "0 assertions in 1 lines" in result.message

    def test_function_with_comments_and_blank_lines(self) -> None:
        """Test that comments and blank lines are excluded from effective line count."""
        content = """def test_comments():
    # This is a comment
    x = 1

    # Another comment
    assert x == 1"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        body = [
            ast.Assign(targets=[ast.Name(id="x", ctx=ast.Store())], value=ast.Constant(value=1)),
            ast.Assert(
                test=ast.Compare(
                    left=ast.Name(id="x", ctx=ast.Load()),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=1)],
                ),
                msg=None,
            ),
        ]

        test_function = TestFunction(
            name="test_comments",
            lineno=1,
            col_offset=0,
            end_lineno=6,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        # Only 2 effective lines: x = 1 and assert x == 1
        assert "Assertion density OK: 0.50" in result.message
        assert "1 assertions in 2 lines" in result.message

    def test_config_fallback_to_default(self) -> None:
        """Test that missing config falls back to default density."""
        config = CheckerConfig(name="test_config", config={})  # Empty config

        # Function with 75% density (above default 50% threshold)
        content = """def test_fallback():
    assert 1 == 1
    assert 2 == 2
    x = 3
    assert x == 3"""

        test_file = TestFile(
            path=Path("/test/dummy.py"),
            content=content,
            ast_tree=ast.parse(content),
            test_functions=[],
            test_classes=[],
        )

        body = [
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=1),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=1)],
                ),
                msg=None,
            ),
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=2),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=2)],
                ),
                msg=None,
            ),
            ast.Assign(targets=[ast.Name(id="x", ctx=ast.Store())], value=ast.Constant(value=3)),
            ast.Assert(
                test=ast.Compare(
                    left=ast.Name(id="x", ctx=ast.Load()),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=3)],
                ),
                msg=None,
            ),
        ]

        test_function = TestFunction(
            name="test_fallback",
            lineno=1,
            col_offset=0,
            end_lineno=5,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, test_file, config)

        assert isinstance(result, CheckFailure)
        assert "High assertion density: 0.75" in result.message
        assert "3 assertions in 4 lines" in result.message
