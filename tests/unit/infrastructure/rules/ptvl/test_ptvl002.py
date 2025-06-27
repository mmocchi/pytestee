"""Tests for PTVL002: Time Dependency Detection rule."""

import ast
from pathlib import Path

import pytest

from pytestee.domain.models import CheckFailure, CheckSuccess, TestFile, TestFunction
from pytestee.domain.rules.vulnerability.ptvl002 import PTVL002


@pytest.fixture
def rule() -> PTVL002:
    """Create PTVL002 rule instance."""
    return PTVL002()


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


class TestPTVL002:
    """Test cases for PTVL002 rule."""

    def test_no_time_dependency_success(self, rule: PTVL002) -> None:
        """Test function with no time dependencies passes."""
        code = '''
def test_example():
    fixed_time = datetime(2023, 1, 1, 12, 0, 0)
    result = process_time(fixed_time)
    assert result is not None
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)
        assert "No time dependencies found" in result.message

    def test_datetime_now_failure(self, rule: PTVL002) -> None:
        """Test function with datetime.now() fails."""
        code = '''
def test_example():
    current_time = datetime.now()
    result = process_time(current_time)
    assert result is not None
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "Time dependency detected" in result.message
        assert "datetime.now" in result.message
        assert "Consider using mocks or fixed time values" in result.message

    def test_time_time_failure(self, rule: PTVL002) -> None:
        """Test function with time.time() fails."""
        code = '''
def test_example():
    timestamp = time.time()
    result = process_timestamp(timestamp)
    assert result is not None
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "time.time" in result.message

    def test_time_sleep_failure(self, rule: PTVL002) -> None:
        """Test function with time.sleep() fails."""
        code = '''
def test_example():
    start = time.time()
    time.sleep(0.1)
    end = time.time()
    assert end > start
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "time.time" in result.message
        assert "time.sleep" in result.message

    def test_direct_function_calls_failure(self, rule: PTVL002) -> None:
        """Test function with direct time function calls fails."""
        code = '''
def test_example():
    current = now()
    today_date = today()
    assert current is not None
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "now" in result.message
        assert "today" in result.message

    def test_multiple_time_dependencies_failure(self, rule: PTVL002) -> None:
        """Test function with multiple time dependencies fails."""
        code = '''
def test_example():
    current = datetime.now()
    timestamp = time.time()
    assert current is not None
    assert timestamp > 0
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckFailure)
        assert "datetime.now" in result.message
        assert "time.time" in result.message

    def test_mocked_time_success(self, rule: PTVL002) -> None:
        """Test function with mocked time passes."""
        code = '''
def test_example():
    with patch('module.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 1, 1)
        result = get_current_time()
        assert result == datetime(2023, 1, 1)
'''
        test_function = create_test_function(code)
        test_file = create_test_file(code)

        result = rule.check(test_function, test_file)

        assert isinstance(result, CheckSuccess)

    def test_rule_properties(self, rule: PTVL002) -> None:
        """Test rule properties."""
        assert rule.rule_id == "PTVL002"
        assert rule.name == "time_dependency_detection"
        assert "time-dependent code" in rule.description
