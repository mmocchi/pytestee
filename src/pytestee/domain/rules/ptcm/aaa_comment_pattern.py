"""PTCM001: AAA Pattern Detected in Comments."""

import re
from typing import List, Optional, Set, Tuple

from ....domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from ....infrastructure.ast_parser import ASTParser
from ..base_rule import BaseRule


class PTCM001(BaseRule):
    """Rule for detecting AAA pattern in comments."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="PTCM001",
            name="aaa_pattern_comments",
            description="AAA (Arrange, Act, Assert) pattern detected through comment analysis",
        )
        self._parser = ASTParser()

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """Check for AAA pattern in comments."""
        comments = self._parser.find_comments(test_function, test_file.content)

        aaa_patterns = [r"#\s*arrange", r"#\s*act", r"#\s*assert"]

        # Combined patterns (count as multiple matches)
        aaa_combined_patterns = [
            r"#\s*act\s*[&/,]\s*assert",  # Act & Assert, Act/Assert, Act, Assert
            r"#\s*act\s+and\s+assert",  # Act and Assert
            r"#\s*arrange\s*[&/,]\s*act\s*[&/,]\s*assert",  # Arrange & Act & Assert
            r"#\s*arrange\s+and\s+act\s+and\s+assert",  # Arrange and Act and Assert
        ]

        aaa_found = self._check_patterns_in_comments(comments, aaa_patterns)
        aaa_combined_found = self._check_combined_patterns_in_comments(
            comments, aaa_combined_patterns
        )

        # Calculate total score (combined patterns count as 2)
        total_aaa_score = aaa_found + (aaa_combined_found * 2)

        if total_aaa_score >= 2:
            # Pattern found - return success (INFO)
            return self._create_success_result(
                "AAA pattern detected in comments", test_file, test_function
            )
        # Pattern not found - return failure (ERROR/WARNING based on config)
        return self._create_failure_result(
            "AAA pattern not detected in comments. Consider adding # Arrange, # Act, # Assert comments.",
            test_file,
            test_function,
        )

    def _check_patterns_in_comments(
        self, comments: List[Tuple[int, str]], patterns: List[str]
    ) -> int:
        """Check how many patterns are found in comments."""
        found = 0

        for _, comment in comments:
            for pattern in patterns:
                if re.search(pattern, comment.lower()):
                    found += 1
                    break

        return found

    def _check_combined_patterns_in_comments(
        self, comments: List[Tuple[int, str]], patterns: List[str]
    ) -> int:
        """Check how many combined patterns are found in comments."""
        found = 0

        for _, comment in comments:
            for pattern in patterns:
                if re.search(pattern, comment.lower()):
                    found += 1
                    # Don't break here - one comment could match multiple combined patterns

        return found

    def get_conflicting_rules(self) -> Set[str]:
        """PTCM001はPTCM003と競合する。"""
        return {"PTCM003"}
