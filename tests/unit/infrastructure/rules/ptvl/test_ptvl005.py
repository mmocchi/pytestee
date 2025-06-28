"""Tests for PTVL005: Class Variable Manipulation Detection rule."""

import ast
from pathlib import Path

import pytest

from pytestee.domain.models import CheckFailure, CheckSuccess, TestClass, TestFile, TestFunction
from pytestee.domain.rules.vulnerability.ptvl005 import PTVL005


@pytest.fixture
def rule() -> PTVL005:
    """Create PTVL005 rule instance."""
    return PTVL005()


def create_test_function_and_class(code: str, func_name: str = "test_example", class_name: str = "TestExample") -> tuple[TestFunction, TestFile]:
    """Create a TestFunction and TestFile from code string with class."""
    tree = ast.parse(code)
    class_def = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    func_def = next(node for node in class_def.body if isinstance(node, ast.FunctionDef) and node.name == func_name)
    
    test_function = TestFunction(
        name=func_name,
        lineno=func_def.lineno,
        col_offset=func_def.col_offset,
        end_lineno=getattr(func_def, "end_lineno", None),
        end_col_offset=getattr(func_def, "end_col_offset", None),
        body=func_def.body,
        docstring=None,
        decorators=[],
    )
    
    test_class = TestClass(
        name=class_name,
        lineno=class_def.lineno,
        col_offset=class_def.col_offset,
        end_lineno=getattr(class_def, "end_lineno", None),
        end_col_offset=getattr(class_def, "end_col_offset", None),
        body=class_def.body,
        test_methods=[func_name],
        decorators=[],
        docstring=None,
    )
    
    test_file = TestFile(
        path=Path("test_file.py"),
        content=code,
        ast_tree=tree,
        test_functions=[test_function],
        test_classes=[test_class],
    )
    
    return test_function, test_file


def create_standalone_test_function(code: str, name: str = "test_example") -> tuple[TestFunction, TestFile]:
    """Create a standalone TestFunction (not in a class) from code string."""
    tree = ast.parse(code)
    func_def = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
    
    test_function = TestFunction(
        name=name,
        lineno=func_def.lineno,
        col_offset=func_def.col_offset,
        end_lineno=getattr(func_def, "end_lineno", None),
        end_col_offset=getattr(func_def, "end_col_offset", None),
        body=func_def.body,
        docstring=None,
        decorators=[],
    )
    
    test_file = TestFile(
        path=Path("test_file.py"),
        content=code,
        ast_tree=tree,
        test_functions=[test_function],
        test_classes=[],
    )
    
    return test_function, test_file


class TestPTVL005:
    """Test cases for PTVL005 rule."""

    def test_standalone_function_not_applicable(self, rule: PTVL005) -> None:
        """Test that standalone functions are not affected by this rule."""
        code = '''
def test_example():
    user = User("Alice")
    assert user.name == "Alice"
'''
        test_function, test_file = create_standalone_test_function(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "Not in a test class - rule not applicable" in result.message

    def test_no_class_variable_modifications_success(self, rule: PTVL005) -> None:
        """Test function with no class variable modifications passes."""
        code = '''
class TestExample:
    shared_data = "initial"
    
    def test_example(self):
        user = User("Alice")
        result = user.get_name()
        assert result == "Alice"
'''
        test_function, test_file = create_test_function_and_class(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "No class variable modifications found" in result.message

    def test_class_variable_modification_via_self_failure(self, rule: PTVL005) -> None:
        """Test function modifying class variable via self fails."""
        code = '''
class TestExample:
    shared_counter = 0
    
    def test_example(self):
        self.shared_counter = 5
        result = process_data()
        assert result is not None
'''
        test_function, test_file = create_test_function_and_class(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Class variable modification detected" in result.message
        assert "self.shared_counter" in result.message
        assert "Consider using instance variables or test fixtures" in result.message

    def test_class_variable_modification_via_classname_failure(self, rule: PTVL005) -> None:
        """Test function modifying class variable via class name fails."""
        code = '''
class TestExample:
    shared_config = "default"
    
    def test_example(self):
        TestExample.shared_config = "test_config"
        result = get_config()
        assert result == "test_config"
'''
        test_function, test_file = create_test_function_and_class(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Class variable modification detected" in result.message
        assert "TestExample.shared_config" in result.message or "shared_config" in result.message

    def test_multiple_class_variable_modifications_failure(self, rule: PTVL005) -> None:
        """Test function with multiple class variable modifications fails."""
        code = '''
class TestExample:
    counter = 0
    flag = False
    
    def test_example(self):
        self.counter = 10
        self.flag = True
        result = process_with_settings()
        assert result is not None
'''
        test_function, test_file = create_test_function_and_class(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Class variable modification detected" in result.message
        assert "self.counter" in result.message
        assert "self.flag" in result.message

    def test_instance_variable_modifications_allowed(self, rule: PTVL005) -> None:
        """Test that instance variable modifications are allowed."""
        code = '''
class TestExample:
    shared_data = "initial"
    
    def test_example(self):
        self.instance_var = "value"
        self.another_instance_var = 123
        result = self.instance_var + str(self.another_instance_var)
        assert result == "value123"
'''
        test_function, test_file = create_test_function_and_class(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)

    def test_annotated_class_variable_modification_failure(self, rule: PTVL005) -> None:
        """Test function modifying annotated class variable fails."""
        code = '''
class TestExample:
    shared_counter: int = 0
    
    def test_example(self):
        self.shared_counter = 42
        result = get_counter_value()
        assert result == 42
'''
        test_function, test_file = create_test_function_and_class(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Class variable modification detected" in result.message
        assert "self.shared_counter" in result.message

    def test_no_class_variables_success(self, rule: PTVL005) -> None:
        """Test class with no class variables passes."""
        code = '''
class TestExample:
    def test_example(self):
        self.instance_var = "value"
        result = process_data(self.instance_var)
        assert result is not None
'''
        test_function, test_file = create_test_function_and_class(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)

    def test_class_method_calls_allowed(self, rule: PTVL005) -> None:
        """Test that calling class methods is allowed."""
        code = '''
class TestExample:
    shared_data = "initial"
    
    @classmethod
    def get_shared_data(cls):
        return cls.shared_data
    
    def test_example(self):
        result = self.get_shared_data()
        assert result == "initial"
'''
        test_function, test_file = create_test_function_and_class(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)

    def test_reading_class_variables_allowed(self, rule: PTVL005) -> None:
        """Test that reading class variables is allowed."""
        code = '''
class TestExample:
    expected_value = "test"
    
    def test_example(self):
        result = get_value()
        assert result == self.expected_value
'''
        test_function, test_file = create_test_function_and_class(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)

    def test_mixed_class_and_instance_variable_assignment(self, rule: PTVL005) -> None:
        """Test mixed class and instance variable assignments."""
        code = '''
class TestExample:
    shared_setting = "default"
    
    def test_example(self):
        self.shared_setting = "modified"  # This is class variable modification
        self.instance_setting = "instance"  # This is instance variable (allowed)
        result = process_settings()
        assert result is not None
'''
        test_function, test_file = create_test_function_and_class(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Class variable modification detected" in result.message
        assert "self.shared_setting" in result.message
        # Should not mention instance_setting as it's not a class variable
        assert "instance_setting" not in result.message

    def test_external_class_variable_access_allowed(self, rule: PTVL005) -> None:
        """Test that accessing external class variables is allowed."""
        code = '''
class TestExample:
    def test_example(self):
        OtherClass.some_variable = "value"  # Not our class variable
        result = OtherClass.get_value()
        assert result == "value"
'''
        test_function, test_file = create_test_function_and_class(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)

    def test_extract_class_variables_method(self, rule: PTVL005) -> None:
        """Test the _extract_class_variables method directly."""
        code = '''
class TestExample:
    regular_var = "value"
    annotated_var: int = 42
    
    def __init__(self):
        self.instance_var = "instance"
    
    def test_method(self):
        pass
'''
        tree = ast.parse(code)
        class_def = next(node for node in tree.body if isinstance(node, ast.ClassDef))
        
        class_variables = rule._extract_class_variables(class_def)
        
        assert "regular_var" in class_variables
        assert "annotated_var" in class_variables
        # Should not include instance variables or methods
        assert "instance_var" not in class_variables
        assert "test_method" not in class_variables

    def test_nested_attribute_access_allowed(self, rule: PTVL005) -> None:
        """Test that nested attribute access is allowed."""
        code = '''
class TestExample:
    config = {"key": "value"}
    
    def test_example(self):
        self.user = User()
        self.user.profile.name = "Alice"
        result = self.user.profile.name
        assert result == "Alice"
'''
        test_function, test_file = create_test_function_and_class(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)

    def test_rule_properties(self, rule: PTVL005) -> None:
        """Test rule properties."""
        assert rule.rule_id == "PTVL005"
        assert rule.name == "class_variable_manipulation_detection"
        assert "modifies class variables" in rule.description
        assert "affect other test methods" in rule.description