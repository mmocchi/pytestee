"""AST parser for analyzing Python test files."""

import ast
from pathlib import Path
from typing import Any, Optional

from pytestee.domain.models import TestClass, TestFile, TestFunction


class ASTParser:
    """Parser for analyzing Python AST to extract test information."""

    def parse_file(self, file_path: Path) -> TestFile:
        """Parse a Python test file and extract test functions and test classes."""
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))

        test_functions = self._extract_test_functions(tree)
        test_classes = self._extract_test_classes(tree)

        return TestFile(
            path=file_path,
            content=content,
            ast_tree=tree,
            test_functions=test_functions,
            test_classes=test_classes,
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

    def _extract_test_classes(self, tree: ast.AST) -> list[TestClass]:
        """Extract test classes from AST."""
        test_classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and self._is_test_class(node):
                test_class = self._create_test_class(node)
                test_classes.append(test_class)

        return test_classes

    def _is_test_class(self, node: ast.ClassDef) -> bool:
        """Check if a class is a test class."""
        # Check if class name starts with "Test"
        if node.name.startswith("Test"):
            return True

        # Check if class contains test methods
        for child_node in node.body:
            if isinstance(child_node, ast.FunctionDef) and self._is_test_function(child_node):
                return True

        return False

    def _create_test_class(self, node: ast.ClassDef) -> TestClass:
        """Create a TestClass from an AST node."""
        docstring = ast.get_docstring(node)
        decorators = self._extract_class_decorators(node)
        test_methods = self._extract_test_method_names(node)

        return TestClass(
            name=node.name,
            lineno=node.lineno,
            col_offset=node.col_offset,
            end_lineno=getattr(node, "end_lineno", None),
            end_col_offset=getattr(node, "end_col_offset", None),
            body=node.body,
            docstring=docstring,
            decorators=decorators,
            test_methods=test_methods,
        )

    def _extract_class_decorators(self, node: ast.ClassDef) -> list[str]:
        """Extract decorator names from a class."""
        decorators = []

        for decorator in node.decorator_list:
            decorator_name = self._get_decorator_name(decorator)
            if decorator_name:
                decorators.append(decorator_name)

        return decorators

    def _extract_test_method_names(self, node: ast.ClassDef) -> list[str]:
        """Extract test method names from a test class."""
        return [
            child_node.name
            for child_node in node.body
            if isinstance(child_node, ast.FunctionDef) and self._is_test_function(child_node)
        ]

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

    def extract_function_parameters(self, test_function: TestFunction) -> list[tuple[str, Optional[type]]]:
        """Extract parameter names and inferred types from test function calls."""
        parameters = []

        for node in ast.walk(ast.Module(body=test_function.body, type_ignores=[])):
            if isinstance(node, ast.Call):
                # Extract function call arguments
                for arg in node.args:
                    param_info = self._analyze_argument(arg)
                    if param_info:
                        parameters.append(param_info)

        return parameters

    def _analyze_argument(self, arg: ast.expr) -> Optional[tuple[str, Optional[type]]]:
        """Analyze a function argument to extract name and type."""
        if isinstance(arg, ast.Constant):
            # Direct constant value
            value_type = type(arg.value) if arg.value is not None else type(None)
            return (str(arg.value), value_type)
        if isinstance(arg, ast.Name):
            # Variable reference
            return (arg.id, None)  # Type unknown without additional analysis
        if isinstance(arg, ast.List):
            # List literal
            return ("list_literal", list)
        if isinstance(arg, ast.Dict):
            # Dict literal
            return ("dict_literal", dict)
        if isinstance(arg, ast.Set):
            # Set literal
            return ("set_literal", set)

        return None

    def extract_pytest_parametrize_data(self, test_function: TestFunction) -> list[tuple]:
        """Extract test data from pytest.mark.parametrize decorators."""
        parametrize_data = []

        for decorator_name in test_function.decorators or []:
            if "parametrize" in decorator_name:
                # Find the actual decorator AST node
                for node in ast.walk(ast.Module(body=test_function.body, type_ignores=[])):
                    if isinstance(node, ast.Call) and self._is_parametrize_decorator(node):
                        data = self._extract_parametrize_values(node)
                        parametrize_data.extend(data)

        return parametrize_data

    def _is_parametrize_decorator(self, node: ast.Call) -> bool:
        """Check if a call node is a pytest.mark.parametrize decorator."""
        if isinstance(node.func, ast.Attribute):
            if (isinstance(node.func.value, ast.Attribute) and
                isinstance(node.func.value.value, ast.Name) and
                node.func.value.value.id == "pytest" and
                node.func.value.attr == "mark" and
                node.func.attr == "parametrize"):
                return True
        return False

    def _extract_parametrize_values(self, node: ast.Call) -> list[tuple]:
        """Extract values from a parametrize decorator."""
        values = []

        # Parametrize typically has at least 2 arguments: parameter names and values
        if len(node.args) >= 2:
            values_arg = node.args[1]

            if isinstance(values_arg, ast.List):
                for item in values_arg.elts:
                    if isinstance(item, ast.Tuple):
                        # Multiple parameters
                        tuple_values = []
                        for elt in item.elts:
                            if isinstance(elt, ast.Constant):
                                tuple_values.append(elt.value)
                        if tuple_values:
                            values.append(tuple(tuple_values))
                    elif isinstance(item, ast.Constant):
                        # Single parameter
                        values.append((item.value,))

        return values

    def find_variable_assignments(self, test_function: TestFunction) -> dict[str, list[Any]]:
        """Find all variable assignments and their values in a test function."""
        assignments: dict[str, list[Any]] = {}

        for node in ast.walk(ast.Module(body=test_function.body, type_ignores=[])):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        value = self._extract_assignment_value(node.value)

                        if var_name not in assignments:
                            assignments[var_name] = []
                        assignments[var_name].append(value)

        return assignments

    def _extract_assignment_value(self, value_node: ast.expr) -> Any:
        """Extract the value from an assignment node."""
        if isinstance(value_node, ast.Constant):
            return value_node.value
        if isinstance(value_node, ast.List):
            return [self._extract_assignment_value(elt) for elt in value_node.elts]
        if isinstance(value_node, ast.Dict):
            result = {}
            for k, v in zip(value_node.keys, value_node.values):
                if isinstance(k, ast.Constant):
                    result[k.value] = self._extract_assignment_value(v)
            return result
        if isinstance(value_node, ast.Set):
            return {self._extract_assignment_value(elt) for elt in value_node.elts}
        if isinstance(value_node, ast.Name):
            return f"var:{value_node.id}"  # Variable reference
        if isinstance(value_node, ast.Call):
            return f"call:{self._get_call_name(value_node)}"
        return f"complex:{type(value_node).__name__}"

    def _get_call_name(self, call_node: ast.Call) -> str:
        """Get the name of a function call."""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        if isinstance(call_node.func, ast.Attribute):
            return self._get_attribute_name(call_node.func)
        return "unknown_call"
