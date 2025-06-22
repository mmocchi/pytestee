"""Assertion analysis helper for domain rules."""

import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytestee.domain.models import TestFunction


class AssertionAnalyzer:
    """Helper class for analyzing assertions in test functions."""

    @staticmethod
    def count_assertions(test_function: "TestFunction") -> int:
        """Count assert statements in a test function.

        Args:
            test_function: The test function to analyze

        Returns:
            Number of assert statements found

        """
        count = 0

        for node in test_function.body:
            count += AssertionAnalyzer._count_asserts_in_node(node)

        return count

    @staticmethod
    def _count_asserts_in_node(node: ast.AST) -> int:
        """Recursively count assert statements in an AST node."""
        count = 0

        if isinstance(node, ast.Assert):
            count += 1
        elif isinstance(node, ast.With) and AssertionAnalyzer._is_pytest_raises(node):
            # Check for pytest.raises pattern
            count += 1

        # Recursively check child nodes
        for child in ast.iter_child_nodes(node):
            count += AssertionAnalyzer._count_asserts_in_node(child)

        return count

    @staticmethod
    def _is_pytest_raises(node: ast.With) -> bool:
        """Check if a with statement is using pytest.raises."""
        for item in node.items:
            if hasattr(item.context_expr, "func"):
                func = item.context_expr.func

                # Check for pytest.raises or raises
                if isinstance(func, ast.Attribute):
                    if (
                        func.attr == "raises"
                        and isinstance(func.value, ast.Name)
                        and func.value.id == "pytest"
                    ):
                        return True
                elif isinstance(func, ast.Name) and func.id == "raises":
                    return True

        return False

    @staticmethod
    def calculate_assertion_density(test_function: "TestFunction") -> float:
        """Calculate assertion density (assertions per line of code).

        Args:
            test_function: The test function to analyze

        Returns:
            Assertion density as a float between 0.0 and 1.0

        """
        assert_count = AssertionAnalyzer.count_assertions(test_function)

        # Calculate total lines in function
        if test_function.end_lineno and test_function.lineno:
            total_lines = test_function.end_lineno - test_function.lineno + 1
        else:
            # Fallback: count body statements
            total_lines = len(test_function.body)

        if total_lines == 0:
            return 0.0

        return assert_count / total_lines
