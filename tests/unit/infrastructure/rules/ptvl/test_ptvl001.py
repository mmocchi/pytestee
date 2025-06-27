"""Tests for PTVL001: Private Access Detection rule."""

import ast
from pathlib import Path

import pytest

from pytestee.domain.models import CheckFailure, CheckSuccess, TestFile, TestFunction
from pytestee.domain.rules.vulnerability.ptvl001 import PTVL001


@pytest.fixture
def rule() -> PTVL001:
    """Create PTVL001 rule instance."""
    return PTVL001()


def create_test_function(code: str, name: str = "test_example") -> TestFunction:
    """Create a TestFunction from code string."""
    tree = ast.parse(code)
    func_def = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
    return TestFunction(
        name=name,
        lineno=func_def.lineno,
        col_offset=func_def.col_offset,
        end_lineno=getattr(func_def, "end_lineno", None),
        end_col_offset=getattr(func_def, "end_col_offset", None),
        body=func_def.body,
        docstring=None,
        decorators=[],
    )


def create_test_file(content: str = "") -> TestFile:
    """Create a TestFile for testing."""
    return TestFile(
        path=Path("test_file.py"),
        content=content,
        ast_tree=ast.parse(content) if content else ast.Module(body=[], type_ignores=[]),
        test_functions=[],
        test_classes=[],
    )


class TestPTVL001:
    """Test cases for PTVL001 rule."""

    def test_no_private_access_success(self, rule: PTVL001) -> None:
        """Test function with no private access passes."""
        code = '''
def test_example():
    user = User("Alice")
    assert user.get_name() == "Alice"
    assert user.is_valid()
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "No private attribute/method access found" in result.message

    def test_private_attribute_access_failure(self, rule: PTVL001) -> None:
        """Test function with private attribute access fails."""
        code = '''
def test_example():
    user = User("Alice")
    assert user._internal_id is not None
    assert user.name == "Alice"
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Private attribute/method access detected" in result.message
        assert "_internal_id" in result.message
        assert "Consider using public interfaces" in result.message

    def test_private_method_access_failure(self, rule: PTVL001) -> None:
        """Test function with private method access fails."""
        code = '''
def test_example():
    user = User("Alice")
    hash_value = user._calculate_hash()
    assert hash_value == "abc"
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Private attribute/method access detected" in result.message
        assert "_calculate_hash()" in result.message

    def test_multiple_private_accesses_failure(self, rule: PTVL001) -> None:
        """Test function with multiple private accesses fails."""
        code = '''
def test_example():
    user = User("Alice")
    assert user._internal_id is not None
    hash_value = user._calculate_hash()
    assert hash_value is not None
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "_internal_id" in result.message
        assert "_calculate_hash()" in result.message

    def test_dunder_methods_allowed(self, rule: PTVL001) -> None:
        """Test that dunder methods are allowed."""
        code = '''
def test_example():
    user = User("Alice")
    assert user.__str__() == "Alice"
    assert user.__len__() == 5
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)

    def test_public_methods_allowed(self, rule: PTVL001) -> None:
        """Test that public methods are allowed."""
        code = '''
def test_example():
    user = User("Alice")
    assert user.public_method() == "result"
    assert user.another_method() is not None
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)

    def test_rule_properties(self, rule: PTVL001) -> None:
        """Test rule properties."""
        assert rule.rule_id == "PTVL001"
        assert rule.name == "private_access_detection"
        assert "private attributes or methods" in rule.description
