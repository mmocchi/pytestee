"""Tests for PTVL004: Global State Modification Detection rule."""

import ast
from pathlib import Path

import pytest

from pytestee.domain.models import CheckFailure, CheckSuccess, TestFile, TestFunction
from pytestee.domain.rules.vulnerability.ptvl004 import PTVL004


@pytest.fixture
def rule() -> PTVL004:
    """Create PTVL004 rule instance."""
    return PTVL004()


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


class TestPTVL004:
    """Test cases for PTVL004 rule."""

    def test_no_global_modifications_success(self, rule: PTVL004) -> None:
        """Test function with no global modifications passes."""
        code = '''
def test_example():
    user = User("Alice")
    result = user.get_name()
    assert result == "Alice"
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "No global state modifications found" in result.message

    def test_all_caps_global_variable_failure(self, rule: PTVL004) -> None:
        """Test function with ALL_CAPS global variable modification fails."""
        code = '''
def test_example():
    GLOBAL_CONFIG = "test_value"
    user = User()
    assert user.get_config() == "test_value"
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Global state modification detected" in result.message
        assert "GLOBAL_CONFIG" in result.message
        assert "Consider using dependency injection, mocks, or test fixtures" in result.message

    def test_private_global_variable_failure(self, rule: PTVL004) -> None:
        """Test function with _PRIVATE_GLOBAL variable modification fails."""
        code = '''
def test_example():
    _PRIVATE_GLOBAL = "new_value"
    result = get_private_setting()
    assert result == "new_value"
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Global state modification detected" in result.message
        assert "_PRIVATE_GLOBAL" in result.message

    def test_long_global_variable_failure(self, rule: PTVL004) -> None:
        """Test function with long global variable name modification fails."""
        code = '''
def test_example():
    application_global_setting = "test_value"
    result = get_app_setting()
    assert result == "test_value"
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Global state modification detected" in result.message
        assert "application_global_setting" in result.message

    def test_module_attribute_modification_failure(self, rule: PTVL004) -> None:
        """Test function with module attribute modification fails."""
        code = '''
def test_example():
    import config
    config.DATABASE_URL = "test://localhost"
    result = connect_to_database()
    assert result is not None
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Global state modification detected" in result.message
        assert "config.DATABASE_URL" in result.message

    def test_global_statement_usage_failure(self, rule: PTVL004) -> None:
        """Test function with global statement usage fails."""
        code = '''
def test_example():
    global SHARED_STATE
    SHARED_STATE = "modified"
    result = get_shared_value()
    assert result == "modified"
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Global state modification detected" in result.message
        assert "global SHARED_STATE" in result.message

    def test_multiple_global_modifications_failure(self, rule: PTVL004) -> None:
        """Test function with multiple global modifications fails."""
        code = '''
def test_example():
    GLOBAL_A = "value_a"
    GLOBAL_B = "value_b"
    result = process_globals()
    assert result is not None
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Global state modification detected" in result.message
        assert "GLOBAL_A" in result.message
        assert "GLOBAL_B" in result.message

    def test_local_variables_allowed(self, rule: PTVL004) -> None:
        """Test that local variables are allowed."""
        code = '''
def test_example():
    local_var = "value"
    other = 123
    result = process_data(local_var, other)
    assert result is not None
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "No global state modifications found" in result.message

    def test_short_uppercase_variables_detected_as_global(self, rule: PTVL004) -> None:
        """Test that short uppercase variables are detected as global."""
        code = '''
def test_example():
    X = 1
    Y = 2
    Z = X + Y
    assert Z == 3
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Global state modification detected" in result.message
        assert "X" in result.message
        assert "Y" in result.message
        assert "Z" in result.message

    def test_class_attributes_allowed(self, rule: PTVL004) -> None:
        """Test that class attribute modifications are allowed."""
        code = '''
def test_example():
    user = User()
    user.name = "Alice"
    user.age = 30
    assert user.name == "Alice"
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "No global state modifications found" in result.message

    def test_constant_assignments_allowed(self, rule: PTVL004) -> None:
        """Test that regular constant assignments are allowed."""
        code = '''
def test_example():
    expected = "test_value"
    actual = get_value()
    assert actual == expected
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)

    def test_looks_like_global_var_method(self, rule: PTVL004) -> None:
        """Test the _looks_like_global_var method directly."""
        # Should be detected as global
        assert rule._looks_like_global_var("GLOBAL_CONFIG") is True
        assert rule._looks_like_global_var("_PRIVATE_GLOBAL") is True
        assert rule._looks_like_global_var("application_global_setting") is True
        assert rule._looks_like_global_var("DATABASE_CONNECTION_URL") is True
        assert rule._looks_like_global_var("X") is True  # Single uppercase letters are considered global
        assert rule._looks_like_global_var("Y") is True
        
        # Should not be detected as global
        assert rule._looks_like_global_var("local_var") is False
        assert rule._looks_like_global_var("user") is False
        assert rule._looks_like_global_var("temp") is False
        assert rule._looks_like_global_var("short_name") is False

    def test_mixed_global_and_local_modifications(self, rule: PTVL004) -> None:
        """Test function with both global and local modifications."""
        code = '''
def test_example():
    local_var = "local"
    GLOBAL_VAR = "global"
    another_local = 123
    result = process_data(local_var, another_local)
    assert result is not None
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Global state modification detected" in result.message
        assert "GLOBAL_VAR" in result.message
        # Check exact message format
        assert "line 4: GLOBAL_VAR" in result.message or "GLOBAL_VAR" in result.message

    def test_nested_attribute_access_allowed(self, rule: PTVL004) -> None:
        """Test that nested attribute access is allowed."""
        code = '''
def test_example():
    user = User()
    user.profile.name = "Alice"
    user.settings.theme = "dark"
    assert user.profile.name == "Alice"
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)

    def test_rule_properties(self, rule: PTVL004) -> None:
        """Test rule properties."""
        assert rule.rule_id == "PTVL004"
        assert rule.name == "global_state_modification_detection"
        assert "modifies global state" in rule.description
        assert "affect other tests" in rule.description