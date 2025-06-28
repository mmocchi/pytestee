"""Unit tests for PTAS002 Too Many Assertions rule."""

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
from pytestee.domain.rules.assertion.too_many_assertions import PTAS002


class TestPTAS002:
    """Test cases for PTAS002 Too Many Assertions rule."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.rule = PTAS002(AssertionAnalyzer())
        self.test_file = TestFile(
            path=Path("/test/dummy.py"),
            content="",
            ast_tree=ast.parse(""),
            test_functions=[],
            test_classes=[],
        )

    def test_rule_properties(self) -> None:
        """Test rule ID, name, and description."""
        assert self.rule.rule_id == "PTAS002"
        assert self.rule.name == "too_many_assertions"
        assert "more assertions" in self.rule.description

    def test_within_limit_returns_success(self) -> None:
        """Test that function within assertion limit returns success."""
        # 3 assertions (default maximum)
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
            name="test_within_limit",
            lineno=1,
            col_offset=0,
            end_lineno=4,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert "Assertion count OK: 3 assertions" in result.message
        assert "maximum: 3" in result.message

    def test_exceeds_limit_returns_failure(self) -> None:
        """Test that function exceeding assertion limit returns failure."""
        # 4 assertions (exceeds default maximum of 3)
        body: list[ast.stmt] = [
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=i),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=i)],
                ),
                msg=None,
            )
            for i in range(4)
        ]

        test_function = TestFunction(
            name="test_exceeds_limit",
            lineno=1,
            col_offset=0,
            end_lineno=5,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckFailure)
        assert result.severity == CheckSeverity.ERROR
        assert "Too many assertions: 4" in result.message
        assert "maximum recommended: 3" in result.message

    def test_custom_maximum_config(self) -> None:
        """Test with custom maximum configuration."""
        config = CheckerConfig(name="test_config", config={"max_asserts": 2})

        # Function with 3 assertions (exceeds maximum of 2)
        body: list[ast.stmt] = [
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=i),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=i)],
                ),
                msg=None,
            )
            for i in range(3)
        ]

        test_function = TestFunction(
            name="test_custom_max",
            lineno=1,
            col_offset=0,
            end_lineno=4,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file, config)

        assert isinstance(result, CheckFailure)
        assert "Too many assertions: 3" in result.message
        assert "maximum recommended: 2" in result.message

    def test_custom_maximum_success(self) -> None:
        """Test success with custom maximum configuration."""
        config = CheckerConfig(name="test_config", config={"max_asserts": 5})

        # Function with 3 assertions (within maximum of 5)
        body: list[ast.stmt] = [
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=i),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=i)],
                ),
                msg=None,
            )
            for i in range(3)
        ]

        test_function = TestFunction(
            name="test_custom_max_success",
            lineno=1,
            col_offset=0,
            end_lineno=4,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file, config)

        assert isinstance(result, CheckSuccess)
        assert "Assertion count OK: 3 assertions" in result.message
        assert "maximum: 5" in result.message

    def test_zero_assertions_returns_success(self) -> None:
        """Test that zero assertions is within limit."""
        body: list[ast.stmt] = [ast.Expr(value=ast.Constant(value="no assertions"))]
        test_function = TestFunction(
            name="test_zero",
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
        assert "Assertion count OK: 0 assertions" in result.message
        assert "maximum: 3" in result.message

    def test_config_fallback_to_default(self) -> None:
        """Test that missing config falls back to default."""
        config = CheckerConfig(name="test_config", config={})  # Empty config

        # 4 assertions (exceeds default maximum of 3)
        body: list[ast.stmt] = [
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=i),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=i)],
                ),
                msg=None,
            )
            for i in range(4)
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

        result = self.rule.check(test_function, self.test_file, config)

        assert isinstance(result, CheckFailure)
        assert "maximum recommended: 3" in result.message  # Default value

    def test_conflicting_rules(self) -> None:
        """Test that conflicting rules are correctly identified."""
        conflicting = self.rule.get_conflicting_rules()
        expected = {"PTAS004"}
        assert conflicting == expected

    def test_mixed_assertion_types(self) -> None:
        """Test with mix of assert statements and pytest.raises."""
        body = [
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=1),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=1)],
                ),
                msg=None,
            ),
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
            name="test_mixed",
            lineno=1,
            col_offset=0,
            end_lineno=5,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert "Assertion count OK: 3 assertions" in result.message
