"""Integration tests for Japanese naming rule."""

from pathlib import Path

from pytestee.domain.models import CheckSeverity
from pytestee.infrastructure.ast_parser import ASTParser
from pytestee.infrastructure.checkers.naming_checker import NamingChecker


class TestJapaneseNamingIntegration:
    """Integration tests for Japanese naming rule functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = ASTParser()
        self.checker = NamingChecker()
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures"

    def test_japanese_naming_rule_with_real_file(self) -> None:
        """Test Japanese naming rule with real test file."""
        test_file_path = self.fixtures_dir / "japanese_naming_test.py"
        test_file = self.parser.parse_file(test_file_path)

        results = self.checker.check(test_file)

        # Should have results for all test methods (6 test methods total)
        assert len(results) == 6

        # Count results by severity
        info_results = [r for r in results if r.severity == CheckSeverity.INFO]
        warning_results = [r for r in results if r.severity == CheckSeverity.WARNING]

        # Japanese methods should return INFO (4 methods: 日本語, ひらがな, カタカナ, 漢字)
        # Mixed method should return INFO (1 method: mixed_japanese)
        # English only should return WARNING (1 method: english_only)
        assert len(info_results) == 5  # 4 pure Japanese + 1 mixed
        assert len(warning_results) == 1  # 1 English only

        # Verify specific methods
        japanese_methods = ["test_日本語メソッド名", "test_ひらがなでのテスト", "test_カタカナでのテスト", "test_漢字を含むテスト", "test_mixed_japanese_englishテスト"]
        english_methods = ["test_english_only_method"]

        info_function_names = {r.function_name for r in info_results}
        warning_function_names = {r.function_name for r in warning_results}

        assert info_function_names == set(japanese_methods)
        assert warning_function_names == set(english_methods)

    def test_rule_id_consistency(self) -> None:
        """Test that all results have consistent rule ID."""
        test_file_path = self.fixtures_dir / "japanese_naming_test.py"
        test_file = self.parser.parse_file(test_file_path)

        results = self.checker.check(test_file)

        # All results should have PTNM001 rule ID
        for result in results:
            assert result.rule_id == "PTNM001"
            assert result.checker_name == "japanese_characters_in_name"

    def test_line_number_accuracy(self) -> None:
        """Test that line numbers are accurately reported."""
        test_file_path = self.fixtures_dir / "japanese_naming_test.py"
        test_file = self.parser.parse_file(test_file_path)

        results = self.checker.check(test_file)

        # All results should have valid line numbers
        for result in results:
            assert result.line_number is not None
            assert result.line_number > 0
            assert result.file_path == test_file_path

    def test_message_content(self) -> None:
        """Test that messages contain appropriate content."""
        test_file_path = self.fixtures_dir / "japanese_naming_test.py"
        test_file = self.parser.parse_file(test_file_path)

        results = self.checker.check(test_file)

        info_results = [r for r in results if r.severity == CheckSeverity.INFO]
        warning_results = [r for r in results if r.severity == CheckSeverity.WARNING]

        # INFO messages should mention Japanese characters are included
        for result in info_results:
            assert "日本語文字が含まれています" in result.message
            assert "可読性が良好です" in result.message

        # WARNING messages should mention Japanese characters are not included
        for result in warning_results:
            assert "日本語文字が含まれていません" in result.message
            assert "日本語での命名を検討してください" in result.message
