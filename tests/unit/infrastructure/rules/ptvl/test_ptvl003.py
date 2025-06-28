"""Tests for PTVL003: Random Dependency Detection rule."""

import ast
from pathlib import Path

import pytest

from pytestee.domain.models import CheckFailure, CheckSuccess, TestFile, TestFunction
from pytestee.domain.rules.vulnerability.ptvl003 import PTVL003


@pytest.fixture
def rule() -> PTVL003:
    """Create PTVL003 rule instance."""
    return PTVL003()


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


class TestPTVL003:
    """Test cases for PTVL003 rule."""

    def test_no_random_dependencies_success(self, rule: PTVL003) -> None:
        """Test function with no random dependencies passes."""
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
        assert "No random dependencies found" in result.message

    def test_random_module_function_failure(self, rule: PTVL003) -> None:
        """Test function with random module function fails."""
        code = '''
def test_example():
    import random
    value = random.randint(1, 10)
    assert value > 0
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Random dependency detected" in result.message
        assert "random.randint" in result.message
        assert "Consider using fixed seeds, mocks, or deterministic values" in result.message

    def test_uuid_module_function_failure(self, rule: PTVL003) -> None:
        """Test function with uuid module function fails."""
        code = '''
def test_example():
    import uuid
    identifier = uuid.uuid4()
    assert str(identifier) is not None
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Random dependency detected" in result.message
        assert "uuid.uuid4" in result.message

    def test_secrets_module_function_failure(self, rule: PTVL003) -> None:
        """Test function with secrets module function fails."""
        code = '''
def test_example():
    import secrets
    token = secrets.token_hex(16)
    assert len(token) == 32
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Random dependency detected" in result.message
        assert "secrets.token_hex" in result.message

    def test_direct_random_function_failure(self, rule: PTVL003) -> None:
        """Test function with direct random function import fails."""
        code = '''
def test_example():
    from random import randint
    value = randint(1, 100)
    assert value > 0
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Random dependency detected" in result.message
        assert "randint" in result.message

    def test_multiple_random_dependencies_failure(self, rule: PTVL003) -> None:
        """Test function with multiple random dependencies fails."""
        code = '''
def test_example():
    import random
    import uuid
    value = random.choice([1, 2, 3])
    identifier = uuid.uuid1()
    assert value in [1, 2, 3]
    assert identifier is not None
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Random dependency detected" in result.message
        assert "random.choice" in result.message
        assert "uuid.uuid1" in result.message

    def test_random_uniform_function_failure(self, rule: PTVL003) -> None:
        """Test function with random.uniform fails."""
        code = '''
def test_example():
    import random
    value = random.uniform(0.0, 1.0)
    assert 0.0 <= value <= 1.0
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "random.uniform" in result.message

    def test_random_shuffle_function_failure(self, rule: PTVL003) -> None:
        """Test function with random.shuffle fails."""
        code = '''
def test_example():
    import random
    data = [1, 2, 3, 4]
    random.shuffle(data)
    assert len(data) == 4
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "random.shuffle" in result.message

    def test_random_sample_function_failure(self, rule: PTVL003) -> None:
        """Test function with random.sample fails."""
        code = '''
def test_example():
    import random
    data = [1, 2, 3, 4, 5]
    sample = random.sample(data, 3)
    assert len(sample) == 3
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "random.sample" in result.message

    def test_random_gauss_function_failure(self, rule: PTVL003) -> None:
        """Test function with random.gauss fails."""
        code = '''
def test_example():
    import random
    value = random.gauss(0, 1)
    assert isinstance(value, float)
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "random.gauss" in result.message

    def test_random_normalvariate_function_failure(self, rule: PTVL003) -> None:
        """Test function with random.normalvariate fails."""
        code = '''
def test_example():
    import random
    value = random.normalvariate(0, 1)
    assert isinstance(value, float)
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "random.normalvariate" in result.message

    def test_secrets_token_urlsafe_failure(self, rule: PTVL003) -> None:
        """Test function with secrets.token_urlsafe fails."""
        code = '''
def test_example():
    import secrets
    token = secrets.token_urlsafe(32)
    assert len(token) > 0
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "secrets.token_urlsafe" in result.message

    def test_secrets_choice_failure(self, rule: PTVL003) -> None:
        """Test function with secrets.choice fails."""
        code = '''
def test_example():
    import secrets
    value = secrets.choice([1, 2, 3])
    assert value in [1, 2, 3]
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "secrets.choice" in result.message

    def test_deterministic_functions_allowed(self, rule: PTVL003) -> None:
        """Test that deterministic functions are allowed."""
        code = '''
def test_example():
    import math
    result = math.sqrt(16)
    assert result == 4.0
    assert math.pi > 3.14
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)

    def test_string_functions_allowed(self, rule: PTVL003) -> None:
        """Test that string functions are allowed."""
        code = '''
def test_example():
    text = "hello world"
    assert text.upper() == "HELLO WORLD"
    assert "world" in text
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)

    def test_rule_properties(self, rule: PTVL003) -> None:
        """Test rule properties."""
        assert rule.rule_id == "PTVL003"
        assert rule.name == "random_dependency_detection"
        assert "random-dependent code" in rule.description
        assert "flaky tests" in rule.description
