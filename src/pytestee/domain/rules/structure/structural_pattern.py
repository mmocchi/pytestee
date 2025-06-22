"""PTST001: AAA Pattern Detected Through Structural Separation."""

from typing import Optional

from pytestee.domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from pytestee.domain.rules.base_rule import BaseRule


class PTST001(BaseRule):
    """Rule for detecting AAA pattern through structural separation."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="PTST001",
            name="aaa_pattern_structural",
            description="AAA pattern detected through empty lines separating code sections",
        )

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """Check for structural AAA pattern using empty lines."""
        lines = test_file.content.split("\n")
        start_line = test_function.lineno - 1
        end_line = test_function.end_lineno or start_line + len(test_function.body)

        function_lines = lines[start_line:end_line]

        # Find empty lines within the function
        empty_line_indices = []
        for i, line in enumerate(
            function_lines[1:], 1
        ):  # Skip function definition line
            if line.strip() == "":
                empty_line_indices.append(i)

        # AAA pattern typically has 2 empty lines separating 3 sections
        if len(empty_line_indices) >= 2:
            sections = self._analyze_sections(function_lines, empty_line_indices)
            if self._looks_like_aaa_structure(sections):
                # Pattern found - return success (INFO)
                return self._create_success_result(
                    "AAA pattern detected through structural separation",
                    test_file,
                    test_function,
                )

        # Pattern not found - return failure (ERROR/WARNING based on config)
        return self._create_failure_result(
            "AAA pattern not detected through structural separation. Consider using empty lines to separate Arrange, Act, Assert sections.",
            test_file,
            test_function,
        )

    def _analyze_sections(
        self, function_lines: list[str], empty_line_indices: list[int]
    ) -> list[list[str]]:
        """Analyze sections separated by empty lines."""
        sections = []
        start = 1  # Skip function definition

        for empty_idx in empty_line_indices:
            if empty_idx > start:
                section = function_lines[start:empty_idx]
                non_empty_section = [line for line in section if line.strip()]
                if non_empty_section:
                    sections.append(non_empty_section)
            start = empty_idx + 1

        # Add the last section
        if start < len(function_lines):
            section = function_lines[start:]
            non_empty_section = [line for line in section if line.strip()]
            if non_empty_section:
                sections.append(non_empty_section)

        return sections

    def _looks_like_aaa_structure(self, sections: list[list[str]]) -> bool:
        """Check if sections look like AAA structure."""
        if len(sections) < 2:
            return False

        # Simple heuristic: last section should contain assert statements
        last_section = sections[-1]
        has_assert = any("assert" in line.lower() for line in last_section)

        return has_assert and len(sections) >= 2
