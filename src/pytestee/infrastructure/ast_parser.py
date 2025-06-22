"""AST parser for analyzing Python test files."""

import ast
from pathlib import Path
from typing import Optional

from pytestee.domain.models import TestFile, TestFunction


class ASTParser:
    """Parser for analyzing Python AST to extract test information."""

    def parse_file(self, file_path: Path) -> TestFile:
        """Parse a Python test file and extract test functions."""
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))

        test_functions = self._extract_test_functions(tree)

        return TestFile(
            path=file_path,
            content=content,
            ast_tree=tree,
            test_functions=test_functions,
        )

    def _extract_test_functions(self, tree: ast.AST) -> list[TestFunction]:
        """Extract test functions from AST."""
        test_functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and self._is_test_function(node):
                test_function = self._create_test_function(node)
                test_functions.append(test_function)

        return test_functions

    def _is_test_function(self, node: ast.FunctionDef) -> bool:
        """Check if a function is a test function."""
        # Check if function name starts with "test_"
        if node.name.startswith("test_"):
            return True

        # Check for pytest.mark decorators
        for decorator in node.decorator_list:
            if self._has_pytest_mark(decorator):
                return True

        return False

    def _has_pytest_mark(self, decorator: ast.expr) -> bool:
        """Check if decorator is a pytest mark."""
        if isinstance(decorator, ast.Attribute):
            if isinstance(decorator.value, ast.Attribute):
                # pytest.mark.something
                if (
                    isinstance(decorator.value.value, ast.Name)
                    and decorator.value.value.id == "pytest"
                    and decorator.value.attr == "mark"
                ):
                    return True
            elif isinstance(decorator.value, ast.Name) and decorator.value.id == "mark":
                # mark.something (if mark is imported)
                return True
        elif isinstance(decorator, ast.Call):
            return self._has_pytest_mark(decorator.func)

        return False

    def _create_test_function(self, node: ast.FunctionDef) -> TestFunction:
        """Create a TestFunction from an AST node."""
        docstring = ast.get_docstring(node)
        decorators = self._extract_decorators(node)

        return TestFunction(
            name=node.name,
            lineno=node.lineno,
            col_offset=node.col_offset,
            end_lineno=getattr(node, "end_lineno", None),
            end_col_offset=getattr(node, "end_col_offset", None),
            body=node.body,
            docstring=docstring,
            decorators=decorators,
        )

    def _extract_decorators(self, node: ast.FunctionDef) -> list[str]:
        """Extract decorator names from a function."""
        decorators = []

        for decorator in node.decorator_list:
            decorator_name = self._get_decorator_name(decorator)
            if decorator_name:
                decorators.append(decorator_name)

        return decorators

    def _get_decorator_name(self, decorator: ast.expr) -> Optional[str]:
        """Get the name of a decorator."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        if isinstance(decorator, ast.Attribute):
            return self._get_attribute_name(decorator)
        if isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)

        return None

    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get the full name of an attribute (e.g., pytest.mark.parametrize)."""
        parts = [node.attr]
        current = node.value

        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            parts.append(current.id)

        return ".".join(reversed(parts))

    def count_assert_statements(self, test_function: TestFunction) -> int:
        """Count assert statements in a test function."""
        count = 0

        for stmt in ast.walk(ast.Module(body=test_function.body, type_ignores=[])):
            if isinstance(stmt, ast.Assert):
                count += 1

        return count

    def get_function_lines(self, test_function: TestFunction) -> int:
        """Get the number of lines in a test function."""
        if test_function.end_lineno:
            return test_function.end_lineno - test_function.lineno + 1
        return len(test_function.body)

    def find_comments(
        self, test_function: TestFunction, file_content: str
    ) -> list[tuple[int, str]]:
        """Find comments in a test function."""
        comments = []
        lines = file_content.split("\n")

        start_line = test_function.lineno - 1  # Convert to 0-based index
        end_line = test_function.end_lineno or start_line + len(test_function.body)

        for i in range(start_line, min(end_line, len(lines))):
            line = lines[i].strip()
            if line.startswith("#"):
                comments.append((i + 1, line))  # Convert back to 1-based line numbers

        return comments
