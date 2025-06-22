"""Assert density checker for test functions."""

import ast
from typing import List, Optional, Union

from ...domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from ...infrastructure.ast_parser import ASTParser
from .base_checker import BaseChecker


class AssertDensityChecker(BaseChecker):
    """Checker for assert statement density and count in test functions."""

    def __init__(self) -> None:
        super().__init__("assert_density")
        self._parser = ASTParser()

    def check_function(self, test_function: TestFunction, test_file: TestFile, config: Optional[CheckerConfig] = None) -> List[CheckResult]:
        """Check assert density and count for a test function."""
        results = []

        # Get configuration values
        max_asserts = self._get_config_value(config, "max_asserts", 3)
        min_asserts = self._get_config_value(config, "min_asserts", 1)
        max_density = self._get_config_value(config, "max_density", 0.5)  # 50% of lines

        # Count assertions
        assert_count = self._parser.count_assert_statements(test_function)

        # Count function lines (excluding blank lines and comments)
        function_lines = self._count_effective_lines(test_function, test_file)

        # Check minimum assertions
        if assert_count < min_asserts:
            results.append(self._create_result(
                "PTAS001",
                "warning",
                f"Too few assertions: {assert_count} (minimum recommended: {min_asserts})",
                test_file,
                test_function
            ))

        # Check maximum assertions
        if assert_count > max_asserts:
            results.append(self._create_result(
                "PTAS002",
                "warning",
                f"Too many assertions: {assert_count} (maximum recommended: {max_asserts})",
                test_file,
                test_function
            ))

        # Check assertion density
        if function_lines > 0:
            density = assert_count / function_lines
            if density > max_density:
                results.append(self._create_result(
                    "PTAS003",
                    "info",
                    f"High assertion density: {density:.2f} ({assert_count} assertions in {function_lines} lines)",
                    test_file,
                    test_function
                ))

        # Check for no assertions (potential issue)
        if assert_count == 0:
            results.append(self._create_result(
                "PTAS004",
                "error",
                "No assertions found - test function should verify expected behavior",
                test_file,
                test_function
            ))

        # If all checks pass, add positive result
        if not results and assert_count >= min_asserts and assert_count <= max_asserts:
            results.append(self._create_result(
                "PTAS005",
                "info",
                f"Assertion count OK: {assert_count} assertions",
                test_file,
                test_function
            ))

        return results

    def _get_config_value(self, config: Optional[CheckerConfig], key: str, default: Union[int, float]) -> Union[int, float]:
        """Get configuration value with fallback to default."""
        if config and config.config:
            return config.config.get(key, default)
        return default

    def _count_effective_lines(self, test_function: TestFunction, test_file: TestFile) -> int:
        """Count effective lines of code (excluding blank lines and comments)."""
        lines = test_file.content.split('\n')
        start_line = test_function.lineno - 1  # Convert to 0-based index
        end_line = test_function.end_lineno or start_line + len(test_function.body)

        effective_lines = 0

        for i in range(start_line + 1, min(end_line, len(lines))):  # Skip function definition line
            line = lines[i].strip()

            # Skip blank lines and comment-only lines
            if line and not line.startswith('#'):
                effective_lines += 1

        return effective_lines

    def analyze_test_complexity(self, test_function: TestFunction, test_file: TestFile) -> dict:
        """Analyze test complexity metrics."""
        assert_count = self._parser.count_assert_statements(test_function)
        function_lines = self._count_effective_lines(test_function, test_file)
        total_lines = self._parser.get_function_lines(test_function)

        # Calculate metrics
        density = assert_count / function_lines if function_lines > 0 else 0
        complexity_score = self._calculate_complexity_score(test_function)

        return {
            "assert_count": assert_count,
            "effective_lines": function_lines,
            "total_lines": total_lines,
            "assert_density": density,
            "complexity_score": complexity_score,
            "recommendations": self._generate_recommendations(assert_count, function_lines, complexity_score)
        }

    def _calculate_complexity_score(self, test_function: TestFunction) -> int:
        """Calculate a simple complexity score based on control flow."""
        complexity = 1  # Base complexity

        for node in ast.walk(ast.Module(body=test_function.body, type_ignores=[])):
            # Add complexity for control flow structures
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With, ast.ExceptHandler)):
                complexity += 1

        return complexity

    def _generate_recommendations(self, assert_count: int, function_lines: int, complexity_score: int) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []

        if assert_count == 0:
            recommendations.append("Add assertions to verify expected behavior")
        elif assert_count > 5:
            recommendations.append("Consider splitting into multiple test functions")

        if function_lines > 20:
            recommendations.append("Consider breaking down into smaller test functions")

        if complexity_score > 3:
            recommendations.append("High complexity - consider simplifying test logic")

        density = assert_count / function_lines if function_lines > 0 else 0
        if density < 0.1:
            recommendations.append("Low assertion density - ensure adequate verification")
        elif density > 0.7:
            recommendations.append("Very high assertion density - consider test focus")

        return recommendations
