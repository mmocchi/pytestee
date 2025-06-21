"""PTLG001: AAA Pattern Detected Through Code Flow Analysis."""

import ast
from typing import Dict, List, Optional

from ....domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from ..base_rule import BaseRule


class PTLG001(BaseRule):
    """Rule for detecting AAA pattern through code flow analysis."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="PTLG001",
            name="aaa_pattern_logical",
            description="AAA pattern detected through AST analysis of code structure"
        )

    def check(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """Check for logical AAA pattern in code flow."""
        # Analyze the AST to detect typical patterns
        body_statements = test_function.body

        sections = self._categorize_statements(body_statements)

        if self._has_logical_aaa_flow(sections):
            return [self._create_result(
                "info",
                "AAA pattern detected through code flow analysis",
                test_file,
                test_function
            )]

        return []

    def _categorize_statements(self, statements: List[ast.stmt]) -> Dict[str, List[ast.stmt]]:
        """Categorize statements into arrange, act, assert groups."""
        sections: Dict[str, List[ast.stmt]] = {
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

        # Should have all three sections for clear AAA pattern
        return has_arrange and has_act and has_assert
