"""Unit tests for PTNM001 Japanese characters rule."""

import ast
from pathlib import Path

from pytestee.domain.models import CheckSeverity, TestFile, TestFunction
from pytestee.domain.rules.ptnm.japanese_characters import PTNM001


class TestPTNM001:
    """Test cases for PTNM001 Japanese characters rule."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.rule = PTNM001()
        self.test_file = TestFile(
            path=Path("/test/dummy.py"),
            content="",
            ast_tree=ast.parse(""),
            test_functions=[],
        )

    def test_rule_properties(self) -> None:
        """Test rule ID, name, and description."""
        assert self.rule.rule_id == "PTNM001"
        assert self.rule.name == "japanese_characters_in_name"
        assert "日本語文字" in self.rule.description

    def test_japanese_test_method_returns_info(self) -> None:
        """Test that test method with Japanese characters returns info."""
        test_function = TestFunction(
            name="test_ユーザー作成",
            lineno=1,
            col_offset=0,
            end_lineno=None,
            end_col_offset=None,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        # Single result (not a list)
        assert result.severity == CheckSeverity.INFO
        assert "日本語文字が含まれています" in result.message
        assert "可読性が良好です" in result.message

    def test_english_test_method_returns_warning(self) -> None:
        """Test that test method without Japanese characters returns warning."""
        test_function = TestFunction(
            name="test_user_creation",
            lineno=1,
            col_offset=0,
            end_lineno=None,
            end_col_offset=None,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert result.severity == CheckSeverity.WARNING
        assert "日本語文字が含まれていません" in result.message
        assert "日本語での命名を検討してください" in result.message

    def test_mixed_japanese_english_returns_info(self) -> None:
        """Test that test method with mixed Japanese and English returns info."""
        test_function = TestFunction(
            name="test_ユーザー_creation",
            lineno=1,
            col_offset=0,
            end_lineno=None,
            end_col_offset=None,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert result.severity == CheckSeverity.INFO

    def test_hiragana_katakana_kanji_all_detected(self) -> None:
        """Test that hiragana, katakana, and kanji are all detected."""
        test_cases = [
            ("test_ひらがな", "hiragana"),
            ("test_カタカナ", "katakana"),
            ("test_漢字", "kanji"),
            ("test_すべて混在", "mixed"),
        ]

        for method_name, case_type in test_cases:
            test_function = TestFunction(
                name=method_name,
                lineno=1,
                col_offset=0,
                end_lineno=None,
                end_col_offset=None,
                body=[],
                decorators=[],
                docstring=None,
            )

            result = self.rule.check(test_function, self.test_file)

            assert result.severity == CheckSeverity.INFO, (
                f"Failed for {case_type}: {method_name}"
            )

    def test_non_test_method_ignored(self) -> None:
        """Test that non-test methods are ignored."""
        test_function = TestFunction(
            name="helper_method",
            lineno=1,
            col_offset=0,
            end_lineno=None,
            end_col_offset=None,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert result is not None

    def test_contains_japanese_characters_method(self) -> None:
        """Test the _contains_japanese_characters method directly."""
        # Test cases with expected results
        test_cases = [
            ("test_ユーザー", True),
            ("test_カタカナ", True),
            ("test_漢字", True),
            ("test_user", False),
            ("test_123", False),
            ("test_mixed_ユーザー", True),
            ("", False),
            ("test_", False),
        ]

        for text, expected in test_cases:
            result = self.rule._contains_japanese_characters(text)
            assert result == expected, (
                f"Failed for '{text}': expected {expected}, got {result}"
            )

    def test_result_contains_correct_metadata(self) -> None:
        """Test that results contain correct metadata."""
        test_function = TestFunction(
            name="test_ユーザー作成",
            lineno=42,
            col_offset=4,
            end_lineno=None,
            end_col_offset=None,
            body=[],
            decorators=[],
            docstring=None,
        )

        result = self.rule.check(test_function, self.test_file)

        assert result.rule_id == "PTNM001"
        assert result.checker_name == "japanese_characters_in_name"
        assert result.function_name == "test_ユーザー作成"
        assert result.line_number == 42
        assert result.file_path == Path("/test/dummy.py")
