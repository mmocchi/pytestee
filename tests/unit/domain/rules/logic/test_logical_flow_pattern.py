"""Unit tests for PTLG001 Logical Flow Pattern rule."""

import ast
from pathlib import Path

from pytestee.domain.models import (
    CheckFailure,
    CheckSeverity,
    CheckSuccess,
    TestFile,
    TestFunction,
)
from pytestee.domain.rules.logic.logical_flow_pattern import PTLG001


class TestPTLG001:
    """Test cases for PTLG001 Logical Flow Pattern rule."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.rule = PTLG001()
        self.test_file = TestFile(
            path=Path("/test/dummy.py"),
            content="",
            ast_tree=ast.parse(""),
            test_functions=[],
            test_classes=[],
        )

    def test_rule_properties(self) -> None:
        """Test rule ID, name, and description."""
        assert self.rule.rule_id == "PTLG001"
        assert self.rule.name == "aaa_pattern_logical"
        assert "AAA pattern detected through AST analysis" in self.rule.description

    def test_clear_aaa_flow_returns_success(self) -> None:
        """Test that function with clear AAA flow returns success."""
        # Arrange: assignments, Act: function call, Assert: assertion
        body = [
            # Arrange section
            ast.Assign(targets=[ast.Name(id="x", ctx=ast.Store())], value=ast.Constant(value=1)),
            ast.Assign(targets=[ast.Name(id="y", ctx=ast.Store())], value=ast.Constant(value=2)),
            # Act section
            ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="calculate", ctx=ast.Load()),
                    args=[ast.Name(id="x", ctx=ast.Load()), ast.Name(id="y", ctx=ast.Load())],
                    keywords=[],
                )
            ),
            ast.Assign(
                targets=[ast.Name(id="result", ctx=ast.Store())],
                value=ast.BinOp(
                    left=ast.Name(id="x", ctx=ast.Load()),
                    op=ast.Add(),
                    right=ast.Name(id="y", ctx=ast.Load()),
                ),
            ),
            # Assert section
            ast.Assert(
                test=ast.Compare(
                    left=ast.Name(id="result", ctx=ast.Load()),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=3)],
                ),
                msg=None,
            ),
        ]
        
        test_function = TestFunction(
            name="test_clear_aaa",
            lineno=1,
            col_offset=0,
            end_lineno=6,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert "AAA pattern detected through code flow analysis" in result.message

    def test_arrange_only_returns_failure(self) -> None:
        """Test that function with only arrange section returns failure."""
        body = [
            ast.Assign(targets=[ast.Name(id="x", ctx=ast.Store())], value=ast.Constant(value=1)),
            ast.Assign(targets=[ast.Name(id="y", ctx=ast.Store())], value=ast.Constant(value=2)),
        ]
        
        test_function = TestFunction(
            name="test_arrange_only",
            lineno=1,
            col_offset=0,
            end_lineno=3,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckFailure)
        assert result.severity == CheckSeverity.ERROR
        assert "AAA pattern not detected through code flow analysis" in result.message
        assert "Consider organizing code with clear Arrange, Act, Assert sections" in result.message

    def test_assert_only_returns_failure(self) -> None:
        """Test that function with only assert section returns failure."""
        body = [
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=1),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=1)],
                ),
                msg=None,
            ),
        ]
        
        test_function = TestFunction(
            name="test_assert_only",
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
        assert "AAA pattern not detected through code flow analysis" in result.message

    def test_arrange_act_only_returns_failure(self) -> None:
        """Test that function with only arrange and act returns failure."""
        body = [
            # Arrange
            ast.Assign(targets=[ast.Name(id="x", ctx=ast.Store())], value=ast.Constant(value=1)),
            # Act
            ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="process", ctx=ast.Load()),
                    args=[ast.Name(id="x", ctx=ast.Load())],
                    keywords=[],
                )
            ),
        ]
        
        test_function = TestFunction(
            name="test_arrange_act_only",
            lineno=1,
            col_offset=0,
            end_lineno=3,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckFailure)
        assert "AAA pattern not detected through code flow analysis" in result.message

    def test_arrange_assert_only_returns_failure(self) -> None:
        """Test that function with only arrange and assert returns failure."""
        body = [
            # Arrange
            ast.Assign(targets=[ast.Name(id="x", ctx=ast.Store())], value=ast.Constant(value=1)),
            # Assert
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
            name="test_arrange_assert_only",
            lineno=1,
            col_offset=0,
            end_lineno=3,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckFailure)
        assert "AAA pattern not detected through code flow analysis" in result.message

    def test_act_assert_only_returns_failure(self) -> None:
        """Test that function with only act and assert returns failure."""
        body = [
            # Act
            ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="perform_action", ctx=ast.Load()),
                    args=[],
                    keywords=[],
                )
            ),
            # Assert
            ast.Assert(
                test=ast.Compare(
                    left=ast.Constant(value=1),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=1)],
                ),
                msg=None,
            ),
        ]
        
        test_function = TestFunction(
            name="test_act_assert_only",
            lineno=1,
            col_offset=0,
            end_lineno=3,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckFailure)
        assert "AAA pattern not detected through code flow analysis" in result.message

    def test_empty_function_returns_failure(self) -> None:
        """Test that empty function returns failure."""
        body = []
        
        test_function = TestFunction(
            name="test_empty",
            lineno=1,
            col_offset=0,
            end_lineno=1,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckFailure)
        assert "AAA pattern not detected through code flow analysis" in result.message

    def test_complex_aaa_pattern_returns_success(self) -> None:
        """Test more complex AAA pattern with multiple statements."""
        body = [
            # Arrange section - multiple setup statements
            ast.Assign(targets=[ast.Name(id="data", ctx=ast.Store())], value=ast.List(elts=[ast.Constant(value=1), ast.Constant(value=2)], ctx=ast.Load())),
            ast.Assign(targets=[ast.Name(id="processor", ctx=ast.Store())], value=ast.Call(func=ast.Name(id="DataProcessor", ctx=ast.Load()), args=[], keywords=[])),
            # Act section - function calls and result assignments
            ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(value=ast.Name(id="processor", ctx=ast.Load()), attr="initialize", ctx=ast.Load()),
                    args=[],
                    keywords=[],
                )
            ),
            ast.Assign(
                targets=[ast.Name(id="result", ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(value=ast.Name(id="processor", ctx=ast.Load()), attr="process", ctx=ast.Load()),
                    args=[ast.Name(id="data", ctx=ast.Load())],
                    keywords=[],
                )
            ),
            # Assert section - multiple assertions
            ast.Assert(
                test=ast.Compare(
                    left=ast.Name(id="result", ctx=ast.Load()),
                    ops=[ast.IsNot()],
                    comparators=[ast.Constant(value=None)],
                ),
                msg=None,
            ),
            ast.Assert(
                test=ast.Call(
                    func=ast.Name(id="len", ctx=ast.Load()),
                    args=[ast.Name(id="result", ctx=ast.Load())],
                    keywords=[],
                ),
                msg=None,
            ),
        ]
        
        test_function = TestFunction(
            name="test_complex_aaa",
            lineno=1,
            col_offset=0,
            end_lineno=8,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert "AAA pattern detected through code flow analysis" in result.message

    def test_assignment_after_assertion_goes_to_act(self) -> None:
        """Test that assignments after assertions are categorized as act."""
        body = [
            # Arrange
            ast.Assign(targets=[ast.Name(id="x", ctx=ast.Store())], value=ast.Constant(value=1)),
            # Act
            ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="do_something", ctx=ast.Load()),
                    args=[],
                    keywords=[],
                )
            ),
            # Assert
            ast.Assert(
                test=ast.Compare(
                    left=ast.Name(id="x", ctx=ast.Load()),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=1)],
                ),
                msg=None,
            ),
            # Another assignment after assert (should go to act, not arrange)
            ast.Assign(targets=[ast.Name(id="y", ctx=ast.Store())], value=ast.Constant(value=2)),
            # Another assert
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
            name="test_assignment_after_assert",
            lineno=1,
            col_offset=0,
            end_lineno=7,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert "AAA pattern detected through code flow analysis" in result.message

    def test_categorize_statements_correctly(self) -> None:
        """Test that statements are categorized correctly."""
        body = [
            ast.Assign(targets=[ast.Name(id="x", ctx=ast.Store())], value=ast.Constant(value=1)),  # arrange
            ast.Expr(value=ast.Call(func=ast.Name(id="func", ctx=ast.Load()), args=[], keywords=[])),  # act
            ast.Assert(test=ast.Constant(value=True), msg=None),  # assert
        ]
        
        test_function = TestFunction(
            name="test_categorization",
            lineno=1,
            col_offset=0,
            end_lineno=4,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        sections = self.rule._categorize_statements(body)
        
        assert len(sections["arrange"]) == 1
        assert len(sections["act"]) == 1
        assert len(sections["assert"]) == 1

    def test_result_contains_correct_metadata(self) -> None:
        """Test that results contain correct metadata."""
        body = [
            ast.Assign(targets=[ast.Name(id="x", ctx=ast.Store())], value=ast.Constant(value=1)),
            ast.Expr(value=ast.Call(func=ast.Name(id="func", ctx=ast.Load()), args=[], keywords=[])),
            ast.Assert(test=ast.Constant(value=True), msg=None),
        ]
        
        test_function = TestFunction(
            name="test_metadata",
            lineno=42,
            col_offset=4,
            end_lineno=45,
            end_col_offset=0,
            body=body,
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert result.rule_id == "PTLG001"
        assert result.checker_name == "aaa_pattern_logical"
        assert result.function_name == "test_metadata"
        assert result.line_number == 42
        assert result.file_path == Path("/test/dummy.py")