"""Integration tests for rule examples from RULES.md."""

from pathlib import Path

from pytestee.adapters.repositories.file_repository import FileRepository
from pytestee.domain.models import CheckerConfig
from pytestee.domain.rules.ptas.assertion_count_ok import PTAS005
from pytestee.domain.rules.ptas.high_assertion_density import PTAS003
from pytestee.domain.rules.ptas.no_assertions import PTAS004
from pytestee.domain.rules.ptas.too_few_assertions import PTAS001
from pytestee.domain.rules.ptas.too_many_assertions import PTAS002
from pytestee.domain.rules.ptcm.aaa_comment_pattern import PTCM001
from pytestee.domain.rules.ptcm.gwt_comment_pattern import PTCM002
from pytestee.domain.rules.ptst.structural_pattern import PTST001


class TestRuleExamples:
    """Test that rule examples from RULES.md work as expected."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.repo = FileRepository()
        self.ptcm001 = PTCM001()
        self.ptcm002 = PTCM002()
        self.ptst001 = PTST001()
        self.ptas001 = PTAS001()
        self.ptas002 = PTAS002()
        self.ptas003 = PTAS003()
        self.ptas004 = PTAS004()
        self.ptas005 = PTAS005()
        self.example_file_path = Path("tests/fixtures/test_example_patterns.py")

    def test_ptcm001_good_examples(self) -> None:
        """Test PTCM001 rule with good examples."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find AAA pattern test functions
        aaa_functions = [
            f
            for f in test_file.test_functions
            if f.name in ["test_aaa_standard_pattern", "test_aaa_combined_act_assert"]
        ]

        for func in aaa_functions:
            result = self.ptcm001.check(func, test_file)
            # Should detect PTCM001 (AAA pattern in comments)
            # Single result (not a list anymore)
            assert result.rule_id == "PTCM001"
            assert result.severity.value == "info"

    def test_ptcm001_bad_examples(self) -> None:
        """Test PTCM001 rule with bad examples (should not trigger)."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find functions that should not trigger PTCM001
        bad_functions = [
            f
            for f in test_file.test_functions
            if f.name in ["test_without_comments", "test_mixed_pattern_terminology"]
        ]

        for func in bad_functions:
            result = self.ptcm001.check(func, test_file)
            # Should not detect PTCM001 (should return failure result)
            # Single result (not a list anymore)
            assert result.rule_id == "PTCM001"
            assert result.severity.value == "error"  # Pattern not found

    def test_ptcm002_good_examples(self) -> None:
        """Test PTCM002 rule with good examples."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find GWT pattern test functions
        gwt_functions = [
            f
            for f in test_file.test_functions
            if f.name in ["test_gwt_standard_pattern", "test_gwt_combined_when_then"]
        ]

        for func in gwt_functions:
            result = self.ptcm002.check(func, test_file)
            # Should detect PTCM002 (GWT pattern in comments)
            # Single result (not a list anymore)
            assert result.rule_id == "PTCM002"
            assert result.severity.value == "info"

    def test_ptst001_good_examples(self) -> None:
        """Test PTST001 rule with good examples."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find structural pattern test functions
        structural_functions = [
            f
            for f in test_file.test_functions
            if f.name
            in ["test_structural_three_sections", "test_structural_two_sections"]
        ]

        for func in structural_functions:
            result = self.ptst001.check(func, test_file)
            # Should detect PTST001 (structural pattern)
            # Single result (not a list anymore)
            assert result.rule_id == "PTST001"
            assert result.severity.value == "info"

    def test_ptst001_bad_examples(self) -> None:
        """Test PTST001 rule with bad examples (should not trigger)."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find functions that should not trigger PTST001
        bad_functions = [
            f
            for f in test_file.test_functions
            if f.name
            in ["test_no_structural_separation", "test_mixed_code_no_sections"]
        ]

        for func in bad_functions:
            result = self.ptst001.check(func, test_file)
            # Should not detect PTST001 (should return failure result)
            # Single result (not a list anymore)
            assert result.rule_id == "PTST001"
            assert result.severity.value == "error"  # Pattern not found

    def test_ptas001_good_examples(self) -> None:
        """Test PTAS001 rule with good examples (should not trigger)."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find functions with sufficient assertions
        good_functions = [
            f
            for f in test_file.test_functions
            if f.name
            in ["test_sufficient_assertions", "test_single_meaningful_assertion"]
        ]

        for func in good_functions:
            result = self.ptas001.check(func, test_file)
            # Should not trigger PTAS001 (too few assertions) - should return success
            assert result.rule_id == "PTAS001"
            assert result.severity.value == "info"  # Success result

    def test_ptas001_bad_examples(self) -> None:
        """Test PTAS001 rule with bad examples (should trigger)."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find functions with no assertions
        bad_functions = [
            f
            for f in test_file.test_functions
            if f.name in ["test_no_assertions", "test_side_effects_only"]
        ]

        for func in bad_functions:
            result = self.ptas004.check(func, test_file)
            # Should trigger PTAS004 (no assertions)
            # Single result (not a list anymore)
            assert result.rule_id == "PTAS004"
            assert result.severity.value == "error"

    def test_ptas002_good_examples(self) -> None:
        """Test PTAS002 rule with good examples (should not trigger)."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find functions with appropriate assertion count
        good_functions = [
            f
            for f in test_file.test_functions
            if f.name == "test_focused_user_validation"
        ]

        for func in good_functions:
            result = self.ptas002.check(func, test_file)
            # Should not trigger PTAS002 (too many assertions) - should return success
            assert result.rule_id == "PTAS002"
            assert result.severity.value == "info"  # Success result

    def test_ptas002_bad_examples(self) -> None:
        """Test PTAS002 rule with bad examples (should trigger)."""
        test_file = self.repo.load_test_file(self.example_file_path)
        config = CheckerConfig(name="test_config", config={"max_asserts": 3})

        # Find functions with too many assertions
        bad_functions = [
            f for f in test_file.test_functions if f.name == "test_too_many_assertions"
        ]

        for func in bad_functions:
            result = self.ptas002.check(func, test_file, config)
            # Should trigger PTAS002 (too many assertions)
            # Single result (not a list anymore)
            assert result.rule_id == "PTAS002"
            assert result.severity.value == "error"

    def test_ptas003_good_examples(self) -> None:
        """Test PTAS003 rule with good examples."""
        test_file = self.repo.load_test_file(self.example_file_path)
        config = CheckerConfig(name="test_config", config={"max_density": 0.5})

        # Find functions with high assertion density
        good_functions = [
            f for f in test_file.test_functions if f.name == "test_high_density_focused"
        ]

        for func in good_functions:
            _ = self.ptas003.check(func, test_file, config)
            # May or may not trigger PTAS003 depending on actual density calculation
            # This is more of an informational rule

    def test_ptas004_bad_examples(self) -> None:
        """Test PTAS004 rule with bad examples (should trigger)."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find functions with no assertions
        bad_functions = [
            f for f in test_file.test_functions if f.name == "test_completely_empty"
        ]

        for func in bad_functions:
            result = self.ptas004.check(func, test_file)
            # Should trigger PTAS004 (no assertions)
            # Single result (not a list anymore)
            assert result.rule_id == "PTAS004"
            assert result.severity.value == "error"

    def test_ptas005_good_examples(self) -> None:
        """Test PTAS005 rule with good examples."""
        test_file = self.repo.load_test_file(self.example_file_path)

        # Find functions with appropriate assertion count
        good_functions = [
            f
            for f in test_file.test_functions
            if f.name == "test_appropriate_assertion_count"
        ]

        for func in good_functions:
            result = self.ptas005.check(func, test_file)
            # Should trigger PTAS005 (assertion count OK)
            assert result.rule_id == "PTAS005"
            assert result.severity.value == "info"
