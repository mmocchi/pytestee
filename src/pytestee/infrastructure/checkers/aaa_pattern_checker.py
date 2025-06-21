"""AAA (Arrange, Act, Assert) pattern checker."""

import ast
import re
from typing import Dict, List, Optional

from ...domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from .base_checker import BaseChecker


class AAAPatternChecker(BaseChecker):
    """Checker for AAA (Arrange, Act, Assert) and GWT (Given, When, Then) patterns."""

    def __init__(self) -> None:
        super().__init__("aaa_pattern")

    def check_function(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """Check if a test function follows AAA/GWT pattern."""
        results = []

        # Check for comment-based patterns
        comment_result = self._check_comment_pattern(test_function, test_file)
        if comment_result:
            results.append(comment_result)

        # Check for structural patterns (empty lines)
        structural_result = self._check_structural_pattern(test_function, test_file)
        if structural_result:
            results.append(structural_result)

        # Check for logical flow pattern
        logical_result = self._check_logical_pattern(test_function, test_file)
        if logical_result:
            results.append(logical_result)

        # If no pattern is detected, create a warning
        if not results:
            results.append(self._create_result(
                "warning",
                "AAA/GWT pattern not clearly detected. Consider using comments or structural separation.",
                test_file,
                test_function
            ))

        return results

    def _check_comment_pattern(self, test_function: TestFunction, test_file: TestFile) -> Optional[CheckResult]:
        """Check for AAA/GWT pattern in comments."""
        from ...infrastructure.ast_parser import ASTParser

        parser = ASTParser()
        comments = parser.find_comments(test_function, test_file.content)

        aaa_patterns = [
            r'#\s*arrange',
            r'#\s*act',
            r'#\s*assert'
        ]

        gwt_patterns = [
            r'#\s*given',
            r'#\s*when',
            r'#\s*then'
        ]

        aaa_found = self._check_patterns_in_comments(comments, aaa_patterns)
        gwt_found = self._check_patterns_in_comments(comments, gwt_patterns)

        if aaa_found >= 2 or gwt_found >= 2:
            pattern_type = "AAA" if aaa_found >= gwt_found else "GWT"
            return self._create_result(
                "info",
                f"{pattern_type} pattern detected in comments",
                test_file,
                test_function
            )

        return None

    def _check_patterns_in_comments(self, comments: List[tuple[int, str]], patterns: List[str]) -> int:
        """Check how many patterns are found in comments."""
        found = 0

        for _, comment in comments:
            for pattern in patterns:
                if re.search(pattern, comment.lower()):
                    found += 1
                    break

        return found

    def _check_structural_pattern(self, test_function: TestFunction, test_file: TestFile) -> Optional[CheckResult]:
        """Check for structural AAA pattern using empty lines."""
        lines = test_file.content.split('\n')
        start_line = test_function.lineno - 1
        end_line = test_function.end_lineno or start_line + len(test_function.body)

        function_lines = lines[start_line:end_line]

        # Find empty lines within the function
        empty_line_indices = []
        for i, line in enumerate(function_lines[1:], 1):  # Skip function definition line
            if line.strip() == "":
                empty_line_indices.append(i)

        # AAA pattern typically has 2 empty lines separating 3 sections
        if len(empty_line_indices) >= 2:
            sections = self._analyze_sections(function_lines, empty_line_indices)
            if self._looks_like_aaa_structure(sections):
                return self._create_result(
                    "info",
                    "AAA pattern detected through structural separation",
                    test_file,
                    test_function
                )

        return None

    def _analyze_sections(self, function_lines: List[str], empty_line_indices: List[int]) -> List[List[str]]:
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

    def _looks_like_aaa_structure(self, sections: List[List[str]]) -> bool:
        """Check if sections look like AAA structure."""
        if len(sections) < 2:
            return False

        # Simple heuristic: last section should contain assert statements
        last_section = sections[-1]
        has_assert = any("assert" in line.lower() for line in last_section)

        return has_assert and len(sections) >= 2

    def _check_logical_pattern(self, test_function: TestFunction, test_file: TestFile) -> Optional[CheckResult]:
        """Check for logical AAA pattern in code flow."""
        # Analyze the AST to detect typical patterns
        body_statements = test_function.body

        sections = self._categorize_statements(body_statements)

        if self._has_logical_aaa_flow(sections):
            return self._create_result(
                "info",
                "AAA pattern detected through code flow analysis",
                test_file,
                test_function
            )

        return None

    def _categorize_statements(self, statements: List[ast.stmt]) -> Dict[str, List[ast.stmt]]:
        """Categorize statements into arrange, act, assert groups."""
        sections = {
            "arrange": [],
            "act": [],
            "assert": []
        }

        current_section = "arrange"

        for stmt in statements:
            if isinstance(stmt, ast.Assert):
                current_section = "assert"
                sections["assert"].append(stmt)
            elif isinstance(stmt, ast.Assign):
                if current_section == "arrange":
                    sections["arrange"].append(stmt)
                else:
                    sections["act"].append(stmt)
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                # Function calls are typically "act"
                if current_section in ["arrange", "act"]:
                    current_section = "act"
                sections["act"].append(stmt)
            else:
                sections[current_section].append(stmt)

        return sections

    def _has_logical_aaa_flow(self, sections: Dict[str, List[ast.stmt]]) -> bool:
        """Check if sections represent a good AAA flow."""
        has_arrange = len(sections["arrange"]) > 0
        has_act = len(sections["act"]) > 0
        has_assert = len(sections["assert"]) > 0

        # At minimum, should have act and assert
        return has_act and has_assert
