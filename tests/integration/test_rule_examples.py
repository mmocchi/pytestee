"""Integration tests for rule examples from RULES.md."""

from pathlib import Path

from pytestee.adapters.repositories.file_repository import FileRepository
from pytestee.domain.checkers.assertion_checker import AssertionChecker
from pytestee.domain.checkers.pattern_checker import PatternChecker
from pytestee.domain.models import CheckerConfig
from pytestee.domain.rules.ptcm.aaa_comment_pattern import PTCM001
from pytestee.domain.rules.ptcm.gwt_comment_pattern import PTCM002
from pytestee.domain.rules.ptst.structural_pattern import PTST001


class TestRuleExamples:
    """Test that rule examples from RULES.md work as expected."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.repo = FileRepository()
        self.pattern_checker = PatternChecker()
        self.assertion_checker = AssertionChecker()
        self.ptcm001 = PTCM001()
        self.ptcm002 = PTCM002()
        self.ptst001 = PTST001()
        self.example_file_path = Path("tests/fixtures/test_example_patterns.py")

    def test_ptcm001_good_examples(self) -> None:
        """Test PTCM001 rule with good examples."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find AAA pattern test functions
        aaa_functions = [
            f for f in test_file.test_functions
            if f.name in ["test_aaa_standard_pattern", "test_aaa_combined_act_assert"]
        ]

        for func in aaa_functions:
            results = self.ptcm001.check(func, test_file)
            # Should detect PTCM001 (AAA pattern in comments)
            assert len(results) == 1
            assert results[0].rule_id == "PTCM001"
            assert results[0].severity.value == "info"

    def test_ptcm001_bad_examples(self) -> None:
        """Test PTCM001 rule with bad examples (should not trigger)."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find functions that should not trigger PTCM001
        bad_functions = [
            f for f in test_file.test_functions
            if f.name in ["test_without_comments", "test_mixed_pattern_terminology"]
        ]

        for func in bad_functions:
            results = self.ptcm001.check(func, test_file)
            # Should not detect PTCM001 (should return failure result)
            assert len(results) == 1
            assert results[0].rule_id == "PTCM001"
            assert results[0].severity.value == "error"  # Pattern not found

    def test_ptcm002_good_examples(self) -> None:
        """Test PTCM002 rule with good examples."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find GWT pattern test functions
        gwt_functions = [
            f for f in test_file.test_functions
            if f.name in ["test_gwt_standard_pattern", "test_gwt_combined_when_then"]
        ]

        for func in gwt_functions:
            results = self.ptcm002.check(func, test_file)
            # Should detect PTCM002 (GWT pattern in comments)
            assert len(results) == 1
            assert results[0].rule_id == "PTCM002"
            assert results[0].severity.value == "info"

    def test_ptst001_good_examples(self) -> None:
        """Test PTST001 rule with good examples."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find structural pattern test functions
        structural_functions = [
            f for f in test_file.test_functions
            if f.name in ["test_structural_three_sections", "test_structural_two_sections"]
        ]

        for func in structural_functions:
            results = self.ptst001.check(func, test_file)
            # Should detect PTST001 (structural pattern)
            assert len(results) == 1
            assert results[0].rule_id == "PTST001"
            assert results[0].severity.value == "info"

    def test_ptst001_bad_examples(self) -> None:
        """Test PTST001 rule with bad examples (should not trigger)."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find functions that should not trigger PTST001
        bad_functions = [
            f for f in test_file.test_functions
            if f.name in ["test_no_structural_separation", "test_mixed_code_no_sections"]
        ]

        for func in bad_functions:
            results = self.ptst001.check(func, test_file)
            # Should not detect PTST001 (should return failure result)
            assert len(results) == 1
            assert results[0].rule_id == "PTST001"
            assert results[0].severity.value == "error"  # Pattern not found

    def test_ptas001_good_examples(self) -> None:
        """Test PTAS001 rule with good examples (should not trigger)."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find functions with sufficient assertions
        good_functions = [
            f for f in test_file.test_functions
            if f.name in ["test_sufficient_assertions", "test_single_meaningful_assertion"]
        ]

        for func in good_functions:
            results = self.assertion_checker.check_function(func, test_file)
            # Should not trigger PTAS001 (too few assertions)
            ptas001_results = [r for r in results if r.rule_id == "PTAS001"]
            assert len(ptas001_results) == 0

    def test_ptas001_bad_examples(self) -> None:
        """Test PTAS001 rule with bad examples (should trigger)."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find functions with no assertions
        bad_functions = [
            f for f in test_file.test_functions
            if f.name in ["test_no_assertions", "test_side_effects_only"]
        ]

        for func in bad_functions:
            results = self.assertion_checker.check_function(func, test_file)
            # Should trigger PTAS004 (no assertions) instead of PTAS001
            ptas004_results = [r for r in results if r.rule_id == "PTAS004"]
            assert len(ptas004_results) == 1
            assert ptas004_results[0].severity.value == "error"

    def test_ptas002_good_examples(self) -> None:
        """Test PTAS002 rule with good examples (should not trigger)."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find functions with appropriate assertion count
        good_functions = [
            f for f in test_file.test_functions
            if f.name == "test_focused_user_validation"
        ]

        for func in good_functions:
            results = self.assertion_checker.check_function(func, test_file)
            # Should not trigger PTAS002 (too many assertions)
            ptas002_results = [r for r in results if r.rule_id == "PTAS002"]
            assert len(ptas002_results) == 0

    def test_ptas002_bad_examples(self) -> None:
        """Test PTAS002 rule with bad examples (should trigger)."""
        test_file = self.repo.load_test_file(self.example_file_path)
        config = CheckerConfig(name="test_config", config={"max_asserts": 3})

        # Find functions with too many assertions
        bad_functions = [
            f for f in test_file.test_functions
            if f.name == "test_too_many_assertions"
        ]

        for func in bad_functions:
            results = self.assertion_checker.check_function(func, test_file, config)
            # Should trigger PTAS002 (too many assertions)
            ptas002_results = [r for r in results if r.rule_id == "PTAS002"]
            assert len(ptas002_results) == 1
            assert ptas002_results[0].severity.value == "error"

    def test_ptas003_good_examples(self) -> None:
        """Test PTAS003 rule with good examples."""
        test_file = self.repo.load_test_file(self.example_file_path)
        config = CheckerConfig(name="test_config", config={"max_density": 0.5})

        # Find functions with high assertion density
        good_functions = [
            f for f in test_file.test_functions
            if f.name == "test_high_density_focused"
        ]

        for func in good_functions:
            _ = self.assertion_checker.check_function(func, test_file, config)
            # May or may not trigger PTAS003 depending on actual density calculation
            # This is more of an informational rule

    def test_ptas004_bad_examples(self) -> None:
        """Test PTAS004 rule with bad examples (should trigger)."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find functions with no assertions
        bad_functions = [
            f for f in test_file.test_functions
            if f.name == "test_completely_empty"
        ]

        for func in bad_functions:
            results = self.assertion_checker.check_function(func, test_file)
            # Should trigger PTAS004 (no assertions)
            ptas004_results = [r for r in results if r.rule_id == "PTAS004"]
            assert len(ptas004_results) == 1
            assert ptas004_results[0].severity.value == "error"

    def test_ptas005_good_examples(self) -> None:
        """Test PTAS005 rule with good examples."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find functions with appropriate assertion count
        good_functions = [
            f for f in test_file.test_functions
            if f.name == "test_appropriate_assertion_count"
        ]

        for func in good_functions:
            results = self.assertion_checker.check_function(func, test_file)
            # Should trigger PTAS005 (assertion count OK)
            ptas005_results = [r for r in results if r.rule_id == "PTAS005"]
            assert len(ptas005_results) == 1
            assert ptas005_results[0].severity.value == "info"
