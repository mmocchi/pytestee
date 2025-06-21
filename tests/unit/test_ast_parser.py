"""Unit tests for AST parser."""

import ast
from pathlib import Path

from pytestee.domain.models import TestFile
from pytestee.infrastructure.ast_parser import ASTParser


class TestASTParser:
    """Test cases for AST parser."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = ASTParser()
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures"

    def test_parse_file_with_valid_test_file(self) -> None:
        """Test parsing a valid test file."""
        test_file_path = self.fixtures_dir / "good_aaa_test.py"

        result = self.parser.parse_file(test_file_path)

        assert isinstance(result, TestFile)
        assert result.path == test_file_path
        assert len(result.test_functions) == 2
        assert result.content is not None
        assert isinstance(result.ast_tree, ast.AST)

    def test_extract_test_functions(self) -> None:
        """Test extracting test functions from AST."""
        test_file_path = self.fixtures_dir / "good_aaa_test.py"
        result = self.parser.parse_file(test_file_path)

        function_names = [func.name for func in result.test_functions]
        assert "test_user_creation_with_aaa_comments" in function_names
        assert "test_user_creation_with_structural_separation" in function_names
        assert "create_user" not in function_names  # Helper function should not be included

    def test_is_test_function_detection(self) -> None:
        """Test detection of test functions."""
        code = '''
def test_something():
    pass

def not_a_test():
    pass

@pytest.mark.parametrize("param", [1, 2])
def test_parametrized():
    pass
'''
        tree = ast.parse(code)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        assert self.parser._is_test_function(functions[0])  # test_something
        assert not self.parser._is_test_function(functions[1])  # not_a_test
        assert self.parser._is_test_function(functions[2])  # test_parametrized

    def test_count_assert_statements(self) -> None:
        """Test counting assert statements."""
        test_file_path = self.fixtures_dir / "bad_test.py"
        result = self.parser.parse_file(test_file_path)

        # Find test_too_many_assertions function
        target_function = None
        for func in result.test_functions:
            if func.name == "test_too_many_assertions":
                target_function = func
                break

        assert target_function is not None
        assert_count = self.parser.count_assert_statements(target_function)
        assert assert_count == 6  # Should count all assert statements

    def test_get_function_lines(self) -> None:
        """Test getting function line count."""
        test_file_path = self.fixtures_dir / "good_aaa_test.py"
        result = self.parser.parse_file(test_file_path)

        for func in result.test_functions:
            lines = self.parser.get_function_lines(func)
            assert lines > 0

    def test_find_comments(self) -> None:
        """Test finding comments in test functions."""
        test_file_path = self.fixtures_dir / "good_aaa_test.py"
        result = self.parser.parse_file(test_file_path)

        # Find function with AAA comments
        target_function = None
        for func in result.test_functions:
            if func.name == "test_user_creation_with_aaa_comments":
                target_function = func
                break

        assert target_function is not None
        comments = self.parser.find_comments(target_function, result.content)

        comment_texts = [comment[1] for comment in comments]
        assert any("# Arrange" in comment for comment in comment_texts)
        assert any("# Act" in comment for comment in comment_texts)
        assert any("# Assert" in comment for comment in comment_texts)
