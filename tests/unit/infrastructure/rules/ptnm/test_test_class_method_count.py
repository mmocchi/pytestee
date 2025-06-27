"""Unit tests for PTNM003 test class method count rule."""

import ast
from pathlib import Path

from pytestee.domain.models import (
    CheckerConfig,
    CheckFailure,
    CheckSeverity,
    CheckSuccess,
    TestClass,
    TestFile,
    TestFunction,
)
from pytestee.domain.rules.naming.test_class_method_count import PTNM003


class TestPTNM003:
    """Test cases for PTNM003 test class method count rule."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.rule = PTNM003()
        self.test_file = TestFile(
            path=Path("/test/dummy.py"),
            content="",
            ast_tree=ast.parse(""),
            test_functions=[],
            test_classes=[],
        )

    def test_rule_properties(self) -> None:
        """Test rule ID, name, and description."""
        assert self.rule.rule_id == "PTNM003"
        assert self.rule.name == "test_class_method_count"
        assert "test methods" in self.rule.description

    def test_appropriate_method_count_returns_success(self) -> None:
        """Test that test class with appropriate method count returns success."""
        test_class = TestClass(
            name="TestUserManagement",
            lineno=1,
            col_offset=0,
            end_lineno=20,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
            test_methods=["test_create", "test_read", "test_update", "test_delete"],
        )

        result = self.rule.check_class(test_class, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert result.rule_id == "PTNM003"
        assert "TestUserManagement" in result.message
        assert "appropriate number of test methods: 4" in result.message
        assert result.line_number == 1
        assert result.column == 0

    def test_too_many_methods_returns_warning(self) -> None:
        """Test that test class with too many methods returns warning."""
        test_methods = [f"test_method_{i}" for i in range(15)]  # 15 methods > default 10
        test_class = TestClass(
            name="TestLargeClass",
            lineno=5,
            col_offset=4,
            end_lineno=100,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
            test_methods=test_methods,
        )

        result = self.rule.check_class(test_class, self.test_file)

        assert isinstance(result, CheckFailure)
        assert result.severity == CheckSeverity.WARNING
        assert result.rule_id == "PTNM003"
        assert "TestLargeClass" in result.message
        assert "too many test methods: 15" in result.message
        assert "maximum recommended: 10" in result.message
        assert "Consider splitting into multiple classes" in result.message
        assert result.line_number == 5
        assert result.column == 4

    def test_empty_test_class_returns_success(self) -> None:
        """Test that empty test class returns success."""
        test_class = TestClass(
            name="TestEmptyClass",
            lineno=10,
            col_offset=0,
            end_lineno=15,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
            test_methods=[],
        )

        result = self.rule.check_class(test_class, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert result.rule_id == "PTNM003"
        assert "TestEmptyClass" in result.message
        assert "appropriate number of test methods: 0" in result.message

    def test_none_test_methods_returns_success(self) -> None:
        """Test that test class with None test_methods returns success."""
        test_class = TestClass(
            name="TestNoneMethodsClass",
            lineno=20,
            col_offset=0,
            end_lineno=25,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
            test_methods=None,
        )

        result = self.rule.check_class(test_class, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert result.rule_id == "PTNM003"
        assert "TestNoneMethodsClass" in result.message
        assert "appropriate number of test methods: 0" in result.message

    def test_custom_max_methods_config(self) -> None:
        """Test that custom max_methods configuration is respected."""
        config = CheckerConfig(name="test_checker", config={"max_methods": 5})
        test_methods = [f"test_method_{i}" for i in range(7)]  # 7 methods > custom 5
        test_class = TestClass(
            name="TestConfigClass",
            lineno=15,
            col_offset=0,
            end_lineno=50,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
            test_methods=test_methods,
        )

        result = self.rule.check_class(test_class, self.test_file, config)

        assert isinstance(result, CheckFailure)
        assert result.severity == CheckSeverity.WARNING
        assert "too many test methods: 7" in result.message
        assert "maximum recommended: 5" in result.message

    def test_custom_max_methods_success(self) -> None:
        """Test that custom max_methods allows higher counts."""
        config = CheckerConfig(name="test_checker", config={"max_methods": 20})
        test_methods = [f"test_method_{i}" for i in range(15)]  # 15 methods < custom 20
        test_class = TestClass(
            name="TestCustomConfigClass",
            lineno=25,
            col_offset=0,
            end_lineno=100,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
            test_methods=test_methods,
        )

        result = self.rule.check_class(test_class, self.test_file, config)

        assert isinstance(result, CheckSuccess)
        assert result.rule_id == "PTNM003"
        assert "appropriate number of test methods: 15" in result.message

    def test_boundary_case_exactly_max_methods(self) -> None:
        """Test boundary case where method count exactly equals max."""
        test_methods = [f"test_method_{i}" for i in range(10)]  # Exactly 10 methods
        test_class = TestClass(
            name="TestBoundaryClass",
            lineno=30,
            col_offset=0,
            end_lineno=80,
            end_col_offset=0,
            body=[],
            decorators=[],
            docstring=None,
            test_methods=test_methods,
        )

        result = self.rule.check_class(test_class, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert result.rule_id == "PTNM003"
        assert "appropriate number of test methods: 10" in result.message

    def test_dummy_check_method_returns_success(self) -> None:
        """Test that the dummy check method returns success."""
        test_function = TestFunction(
            name="test_example",
            lineno=1,
            col_offset=0,
            end_lineno=None,
            end_col_offset=None,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert isinstance(result, CheckSuccess)
        assert result.rule_id == "PTNM003"
        assert "class-level rule" in result.message

    def test_get_config_value_with_none_config(self) -> None:
        """Test _get_config_value with None config returns default."""
        value = self.rule._get_config_value(None, "max_methods", 15)
        assert value == 15

    def test_get_config_value_with_empty_config(self) -> None:
        """Test _get_config_value with empty config returns default."""
        config = CheckerConfig(name="test_checker", config={})
        value = self.rule._get_config_value(config, "max_methods", 15)
        assert value == 15

    def test_get_config_value_with_missing_key(self) -> None:
        """Test _get_config_value with missing key returns default."""
        config = CheckerConfig(name="test_checker", config={"other_key": 25})
        value = self.rule._get_config_value(config, "max_methods", 15)
        assert value == 15

    def test_get_config_value_with_present_key(self) -> None:
        """Test _get_config_value with present key returns config value."""
        config = CheckerConfig(name="test_checker", config={"max_methods": 25})
        value = self.rule._get_config_value(config, "max_methods", 15)
        assert value == 25

