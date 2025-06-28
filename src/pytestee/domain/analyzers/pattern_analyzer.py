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

        # Extract only actual comments (lines with # outside of strings)
        comments = PatternAnalyzer._extract_comments(function_lines)

        has_arrange = any("arrange" in comment.lower() for comment in comments)
        has_act = any("act" in comment.lower() for comment in comments)
        has_assert = any("assert" in comment.lower() for comment in comments)

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

        # Extract only actual comments (lines with # outside of strings)
        comments = PatternAnalyzer._extract_comments(function_lines)

        has_given = any("given" in comment.lower() for comment in comments)
        has_when = any("when" in comment.lower() for comment in comments)
        has_then = any("then" in comment.lower() for comment in comments)

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

    @staticmethod
    def _extract_comments(lines: list[str]) -> list[str]:
        """Extract actual comments from lines, ignoring comments inside strings.

        Args:
            lines: List of lines to extract comments from

        Returns:
            List of comment texts (without the # prefix)

        """
        comments = []
        for line in lines:
            # Find comment position, but ignore # inside strings
            comment_pos = PatternAnalyzer._find_comment_position(line)
            if comment_pos != -1:
                comment_text = line[comment_pos + 1:].strip()
                if comment_text:  # Only add non-empty comments
                    comments.append(comment_text)
        return comments

    @staticmethod
    def _find_comment_position(line: str) -> int:
        """Find the position of comment start (#), ignoring # inside strings.

        Args:
            line: Line to search for comment

        Returns:
            Position of comment start, or -1 if no comment found

        """
        in_single_quote = False
        in_double_quote = False
        i = 0

        while i < len(line):
            char = line[i]

            # Handle escape sequences
            if char == '\\' and i + 1 < len(line):
                i += 2  # Skip escaped character
                continue

            # Track string boundaries
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
            elif char == '#' and not in_single_quote and not in_double_quote:
                return i

            i += 1

        return -1
