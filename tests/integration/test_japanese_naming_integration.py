"""Integration tests for Japanese naming rule."""

from pathlib import Path

from pytestee.domain.analyzers.pattern_analyzer import PatternAnalyzer
from pytestee.domain.models import CheckFailure, CheckSeverity, CheckSuccess
from pytestee.domain.rules.naming.japanese_characters import PTNM001
from pytestee.infrastructure.ast_parser import ASTParser


class TestJapaneseNamingIntegration:
    """Integration tests for Japanese naming rule functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = ASTParser()
        self.checker = PTNM001(PatternAnalyzer())
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures"

    def test_japanese_naming_rule_with_real_file(self) -> None:
        """Test Japanese naming rule with real test file."""
        test_file_path = self.fixtures_dir / "japanese_naming_test.py"
        test_file = self.parser.parse_file(test_file_path)

        # Collect results for all test functions
        results = []
        for test_function in test_file.test_functions:
            function_result = self.checker.check(test_function, test_file)
            results.append(function_result)

        # Should have results for all test methods (6 test methods total)
        assert len(results) == 6

        # Count results by type
        success_results = [r for r in results if isinstance(r, CheckSuccess)]
        failure_results = [r for r in results if isinstance(r, CheckFailure) and r.severity == CheckSeverity.WARNING]

        # Japanese methods should return INFO (4 methods: 日本語, ひらがな, カタカナ, 漢字)
        # Mixed method should return INFO (1 method: mixed_japanese)
        # English only should return WARNING (1 method: english_only)
        assert len(success_results) == 5  # 4 pure Japanese + 1 mixed
        assert len(failure_results) == 1  # 1 English only

        # Verify specific methods
        japanese_methods = [
            "test_日本語メソッド名",
            "test_ひらがなでのテスト",
            "test_カタカナでのテスト",
            "test_漢字を含むテスト",
            "test_mixed_japanese_englishテスト",
        ]
        english_methods = ["test_english_only_method"]

        success_function_names = {r.function_name for r in success_results}
        failure_function_names = {r.function_name for r in failure_results}

        assert success_function_names == set(japanese_methods)
        assert failure_function_names == set(english_methods)

    def test_rule_id_consistency(self) -> None:
        """Test that all results have consistent rule ID."""
        test_file_path = self.fixtures_dir / "japanese_naming_test.py"
        test_file = self.parser.parse_file(test_file_path)

        # Collect results for all test functions
        results = []
        for test_function in test_file.test_functions:
            function_result = self.checker.check(test_function, test_file)
            results.append(function_result)

        # All results should have PTNM001 rule ID
        for result in results:
            assert result.rule_id == "PTNM001"
            assert result.checker_name == "japanese_characters_in_name"

    def test_line_number_accuracy(self) -> None:
        """Test that line numbers are accurately reported."""
        test_file_path = self.fixtures_dir / "japanese_naming_test.py"
        test_file = self.parser.parse_file(test_file_path)

        # Collect results for all test functions
        results = []
        for test_function in test_file.test_functions:
            function_result = self.checker.check(test_function, test_file)
            results.append(function_result)

        # All results should have valid line numbers
        for result in results:
            assert result.line_number is not None
            assert result.line_number > 0
            assert result.file_path == test_file_path

    def test_message_content(self) -> None:
        """Test that messages contain appropriate content."""
        test_file_path = self.fixtures_dir / "japanese_naming_test.py"
        test_file = self.parser.parse_file(test_file_path)

        # Collect results for all test functions
        results = []
        for test_function in test_file.test_functions:
            function_result = self.checker.check(test_function, test_file)
            results.append(function_result)

        success_results_check = [r for r in results if isinstance(r, CheckSuccess)]
        failure_results_check = [r for r in results if isinstance(r, CheckFailure) and r.severity == CheckSeverity.WARNING]

        # INFO messages should mention Japanese characters are included
        for result in success_results_check:
            assert "日本語文字が含まれています" in result.message
            assert "可読性が良好です" in result.message

        # WARNING messages should mention Japanese characters are not included
        for i in range(len(failure_results_check)):
            failure_result = failure_results_check[i]
            assert "日本語文字が含まれていません" in failure_result.message
            assert "日本語での命名を検討してください" in failure_result.message
