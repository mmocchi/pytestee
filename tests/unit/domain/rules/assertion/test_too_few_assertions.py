"""Unit tests for PTAS001 Too Few Assertions rule."""

import ast
from pathlib import Path

from pytestee.domain.analyzers.assertion_analyzer import AssertionAnalyzer
from pytestee.domain.models import (
    CheckFailure,
    CheckerConfig,
    CheckSeverity,
    CheckSuccess,
    TestFile,
    TestFunction,
)
from pytestee.domain.rules.assertion.too_few_assertions import PTAS001


class TestPTAS001:
    """Test cases for PTAS001 Too Few Assertions rule."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.rule = PTAS001(AssertionAnalyzer())
        self.test_file = TestFile(
            path=Path("/test/dummy.py"),
            content="",
            ast_tree=ast.parse(""),
            test_functions=[],
            test_classes=[],
        )

    def test_rule_properties(self) -> None:
        """Test rule ID, name, and description."""
        assert self.rule.rule_id == "PTAS001"
        assert self.rule.name == "too_few_assertions"
        assert "fewer assertions" in self.rule.description

    def test_no_assertions_returns_failure(self) -> None:
        """Test that function with no assertions returns failure."""
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
        assert "Too few assertions: 0" in result.message
        assert "minimum recommended: 1" in result.message

    def test_one_assertion_returns_success(self) -> None:
        """Test that function with one assertion returns success."""
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
        assert "Assertion count OK: 1 assertions" in result.message
        assert "minimum: 1" in result.message

    def test_custom_minimum_config(self) -> None:
        """Test with custom minimum configuration."""
        config = CheckerConfig(name="test_config", config={"min_asserts": 3})
        
        # Function with 2 assertions (below minimum of 3)
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
            name="test_custom_min",
            lineno=1,
            col_offset=0,
            end_lineno=3,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file, config)

        assert isinstance(result, CheckFailure)
        assert "Too few assertions: 2" in result.message
        assert "minimum recommended: 3" in result.message

    def test_custom_minimum_success(self) -> None:
        """Test success with custom minimum configuration."""
        config = CheckerConfig(name="test_config", config={"min_asserts": 2})
        
        # Function with 2 assertions (meets minimum of 2)
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
            name="test_custom_min_success",
            lineno=1,
            col_offset=0,
            end_lineno=3,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file, config)

        assert isinstance(result, CheckSuccess)
        assert "Assertion count OK: 2 assertions" in result.message
        assert "minimum: 2" in result.message

    def test_config_fallback_to_default(self) -> None:
        """Test that missing config falls back to default."""
        config = CheckerConfig(name="test_config", config={})  # Empty config
        
        body = [ast.Expr(value=ast.Constant(value="no assertions"))]
        test_function = TestFunction(
            name="test_fallback",
            lineno=1,
            col_offset=0,
            end_lineno=2,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file, config)

        assert isinstance(result, CheckFailure)
        assert "minimum recommended: 1" in result.message  # Default value

    def test_conflicting_rules(self) -> None:
        """Test that conflicting rules are correctly identified."""
        conflicting = self.rule.get_conflicting_rules()
        expected = {"PTAS004", "PTAS005"}
        assert conflicting == expected

    def test_with_pytest_raises(self) -> None:
        """Test that pytest.raises counts as assertion."""
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
        assert "Assertion count OK: 1 assertions" in result.message