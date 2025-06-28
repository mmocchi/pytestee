"""Unit tests for PTAS005 Assertion Count OK rule."""

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
from pytestee.domain.rules.assertion.assertion_count_ok import PTAS005


class TestPTAS005:
    """Test cases for PTAS005 Assertion Count OK rule."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.rule = PTAS005(AssertionAnalyzer())
        self.test_file = TestFile(
            path=Path("/test/dummy.py"),
            content="",
            ast_tree=ast.parse(""),
            test_functions=[],
            test_classes=[],
        )

    def test_rule_properties(self) -> None:
        """Test rule ID, name, and description."""
        assert self.rule.rule_id == "PTAS005"
        assert self.rule.name == "assertion_count_ok"
        assert "appropriate number" in self.rule.description

    def test_optimal_assertion_count_returns_success(self) -> None:
        """Test that function with optimal assertion count returns success."""
        # 2 assertions (within default range 1-3)
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
        ]
        test_function = TestFunction(
            name="test_optimal",
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
        assert "Assertion count OK: 2 assertions" in result.message

    def test_minimum_assertions_returns_success(self) -> None:
        """Test that function with minimum assertions returns success."""
        # 1 assertion (minimum default)
        body: list[ast.stmt] = [
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
            name="test_minimum",
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

    def test_maximum_assertions_returns_success(self) -> None:
        """Test that function with maximum assertions returns success."""
        # 3 assertions (maximum default)
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
            name="test_maximum",
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

    def test_too_few_assertions_returns_failure(self) -> None:
        """Test that function with too few assertions returns failure."""
        # 0 assertions (below minimum of 1)
        body: list[ast.stmt] = [ast.Expr(value=ast.Constant(value="no assertions"))]
        test_function = TestFunction(
            name="test_too_few",
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
        assert "Too few assertions: 0 assertions" in result.message
        assert "minimum: 1" in result.message

    def test_too_many_assertions_returns_failure(self) -> None:
        """Test that function with too many assertions returns failure."""
        # 4 assertions (above maximum of 3)
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
            name="test_too_many",
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
        assert "Too many assertions: 4 assertions" in result.message
        assert "maximum: 3" in result.message

    def test_custom_range_config(self) -> None:
        """Test with custom min/max configuration."""
        config = CheckerConfig(name="test_config", config={"min_asserts": 2, "max_asserts": 5})

        # Function with 3 assertions (within custom range 2-5)
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
            name="test_custom_range",
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

    def test_custom_range_too_few(self) -> None:
        """Test failure with custom range - too few."""
        config = CheckerConfig(name="test_config", config={"min_asserts": 3, "max_asserts": 5})

        # Function with 2 assertions (below custom minimum of 3)
        body: list[ast.stmt] = [
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=i),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=i)],
                ),
                msg=None,
            )
            for i in range(2)
        ]

        test_function = TestFunction(
            name="test_custom_too_few",
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
        assert "Too few assertions: 2 assertions" in result.message
        assert "minimum: 3" in result.message

    def test_custom_range_too_many(self) -> None:
        """Test failure with custom range - too many."""
        config = CheckerConfig(name="test_config", config={"min_asserts": 1, "max_asserts": 2})

        # Function with 4 assertions (above custom maximum of 2)
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
            name="test_custom_too_many",
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
        assert "Too many assertions: 4 assertions" in result.message
        assert "maximum: 2" in result.message

    def test_conflicting_rules(self) -> None:
        """Test that conflicting rules are correctly identified."""
        conflicting = self.rule.get_conflicting_rules()
        expected = {"PTAS001", "PTAS004"}
        assert conflicting == expected

    def test_config_fallback_to_defaults(self) -> None:
        """Test that missing config values fall back to defaults."""
        config = CheckerConfig(name="test_config", config={})  # Empty config

        # Function with 2 assertions (within default range 1-3)
        body: list[ast.stmt] = [
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=i),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=i)],
                ),
                msg=None,
            )
            for i in range(2)
        ]

        test_function = TestFunction(
            name="test_defaults",
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
