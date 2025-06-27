"""Pattern analysis helper for domain rules."""

import re
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pytestee.domain.models import TestClass, TestFunction


class PatternAnalyzer:
    """Helper class for analyzing patterns in test functions."""

    @staticmethod
    def find_aaa_comments(test_function: "TestFunction", file_content: str) -> bool:
        """Check if test function has AAA (Arrange, Act, Assert) comment pattern.

        Args:
            test_function: The test function to analyze
            file_content: The full file content

        Returns:
            True if AAA pattern is found in comments

        """
        function_lines = PatternAnalyzer._extract_function_lines(
            test_function, file_content
        )

        has_arrange = any("# arrange" in line.lower() for line in function_lines)
        has_act = any("# act" in line.lower() for line in function_lines)
        has_assert = any("# assert" in line.lower() or ("assert" in line.lower() and "#" in line) for line in function_lines)

        return has_arrange and has_act and has_assert

    @staticmethod
    def find_gwt_comments(test_function: "TestFunction", file_content: str) -> bool:
        """Check if test function has GWT (Given, When, Then) comment pattern.

        Args:
            test_function: The test function to analyze
            file_content: The full file content

        Returns:
            True if GWT pattern is found in comments

        """
        function_lines = PatternAnalyzer._extract_function_lines(
            test_function, file_content
        )

        has_given = any("# given" in line.lower() for line in function_lines)
        has_when = any("# when" in line.lower() or ("when" in line.lower() and "#" in line) for line in function_lines)
        has_then = any("# then" in line.lower() or ("then" in line.lower() and "#" in line) for line in function_lines)

        return has_given and has_when and has_then

    @staticmethod
    def find_aaa_or_gwt_comments(test_function: "TestFunction", file_content: str) -> tuple[bool, Optional[str]]:
        """Check if test function has either AAA or GWT comment pattern.

        Args:
            test_function: The test function to analyze
            file_content: The full file content

        Returns:
            Tuple of (has_pattern, pattern_type) where pattern_type is "AAA", "GWT", or None

        """
        if PatternAnalyzer.find_aaa_comments(test_function, file_content):
            return True, "AAA"
        if PatternAnalyzer.find_gwt_comments(test_function, file_content):
            return True, "GWT"
        return False, None

    @staticmethod
    def has_japanese_characters(test_function: "TestFunction") -> bool:
        """Check if test function name contains Japanese characters.

        Args:
            test_function: The test function to analyze

        Returns:
            True if Japanese characters are found in function name

        """
        # Japanese character ranges
        japanese_pattern = re.compile(
            r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3400-\u4DBF]'
        )
        return bool(japanese_pattern.search(test_function.name))

    @staticmethod
    def has_japanese_characters_in_class(test_class: "TestClass") -> bool:
        """Check if test class name contains Japanese characters.

        Args:
            test_class: The test class to analyze

        Returns:
            True if Japanese characters are found in class name

        """
        # Japanese character ranges
        japanese_pattern = re.compile(
            r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3400-\u4DBF]'
        )
        return bool(japanese_pattern.search(test_class.name))

    @staticmethod
    def _extract_function_lines(test_function: "TestFunction", file_content: str) -> list[str]:
        """Extract lines belonging to a specific function from file content.

        Args:
            test_function: The test function to analyze
            file_content: The full file content

        Returns:
            List of lines belonging to the function

        """
        lines = file_content.splitlines()

        # Get function boundaries
        start_line = test_function.lineno - 1  # Convert to 0-based
        end_line = test_function.end_lineno if test_function.end_lineno else len(lines)

        # Extract function lines
        if 0 <= start_line < len(lines) and start_line < end_line:
            return lines[start_line:end_line]
        return []
