"""Unit tests for PTAS004 No Assertions rule."""

import ast
from pathlib import Path

from pytestee.domain.analyzers.assertion_analyzer import AssertionAnalyzer
from pytestee.domain.models import (
    CheckFailure,
    CheckSeverity,
    CheckSuccess,
    TestFile,
    TestFunction,
)
from pytestee.domain.rules.assertion.no_assertions import PTAS004


class TestPTAS004:
    """Test cases for PTAS004 No Assertions rule."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.rule = PTAS004(AssertionAnalyzer())
        self.test_file = TestFile(
            path=Path("/test/dummy.py"),
            content="",
            ast_tree=ast.parse(""),
            test_functions=[],
            test_classes=[],
        )

    def test_rule_properties(self) -> None:
        """Test rule ID, name, and description."""
        assert self.rule.rule_id == "PTAS004"
        assert self.rule.name == "no_assertions"
        assert "no assertions" in self.rule.description.lower()

    def test_no_assertions_returns_failure(self) -> None:
        """Test that function with no assertions returns failure."""
        # Create function with no assertions
        body = [ast.Expr(value=ast.Constant(value="some code"))]
        test_function = TestFunction(
            name="test_something",
            lineno=1,
            col_offset=0,
            end_lineno=2,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckFailure)
        assert result.severity == CheckSeverity.ERROR
        assert "No assertions found" in result.message
        assert "should verify expected behavior" in result.message

    def test_with_assert_statement_returns_success(self) -> None:
        """Test that function with assert statement returns success."""
        # Create function with assert statement
        body = [
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=1),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=1)],
                ),
                msg=None,
            )
        ]
        test_function = TestFunction(
            name="test_something",
            lineno=1,
            col_offset=0,
            end_lineno=2,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert "Assertions found: 1 assertions" in result.message

    def test_with_pytest_raises_returns_success(self) -> None:
        """Test that function with pytest.raises returns success."""
        # Create function with pytest.raises
        body = [
            ast.With(
                items=[
                    ast.withitem(
                        context_expr=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id="pytest", ctx=ast.Load()),
                                attr="raises",
                                ctx=ast.Load(),
                            ),
                            args=[ast.Name(id="ValueError", ctx=ast.Load())],
                            keywords=[],
                        ),
                        optional_vars=None,
                    )
                ],
                body=[ast.Expr(value=ast.Constant(value="raise ValueError()"))],
            )
        ]
        test_function = TestFunction(
            name="test_exception",
            lineno=1,
            col_offset=0,
            end_lineno=3,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert "Assertions found: 1 assertions" in result.message

    def test_multiple_assertions_returns_success(self) -> None:
        """Test that function with multiple assertions returns success."""
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
        ]
        test_function = TestFunction(
            name="test_multiple",
            lineno=1,
            col_offset=0,
            end_lineno=3,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert "Assertions found: 2 assertions" in result.message

    def test_conflicting_rules(self) -> None:
        """Test that conflicting rules are correctly identified."""
        conflicting = self.rule.get_conflicting_rules()
        expected = {"PTAS001", "PTAS002", "PTAS005"}
        assert conflicting == expected

    def test_result_contains_correct_metadata(self) -> None:
        """Test that results contain correct metadata."""
        body = [ast.Expr(value=ast.Constant(value="no assertions"))]
        test_function = TestFunction(
            name="test_metadata",
            lineno=42,
            col_offset=4,
            end_lineno=43,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert result.rule_id == "PTAS004"
        assert result.checker_name == "no_assertions"
        assert result.function_name == "test_metadata"
        assert result.line_number == 42
        assert result.file_path == Path("/test/dummy.py")