"""PTAS003: High Assertion Density."""

from typing import Optional, Union

from ....domain.models import CheckerConfig, CheckResult, TestFile, TestFunction
from ....infrastructure.ast_parser import ASTParser
from ..base_rule import BaseRule


class PTAS003(BaseRule):
    """Rule for detecting high assertion density."""

    def __init__(self) -> None:
        super().__init__(
            rule_id="PTAS003",
            name="high_assertion_density",
            description="High ratio of assertions to lines of code",
        )
        self._parser = ASTParser()

    def check(
        self,
        test_function: TestFunction,
        test_file: TestFile,
        config: Optional[CheckerConfig] = None,
    ) -> CheckResult:
        """Check for high assertion density."""
        max_density = self._get_config_value(config, "max_density", 0.5)  # 50% of lines
        assert_count = self._parser.count_assert_statements(test_function)
        function_lines = self._count_effective_lines(test_function, test_file)

        if function_lines > 0:
            density = assert_count / function_lines
            if density > max_density:
                return self._create_result(
                    f"High assertion density: {density:.2f} ({assert_count} assertions in {function_lines} lines)",
                    test_file,
                    test_function,
                )
            return self._create_success_result(
                f"Assertion density OK: {density:.2f} ({assert_count} assertions in {function_lines} lines)",
                test_file,
                test_function,
            )
        return self._create_success_result(
            "No effective lines found to calculate density", test_file, test_function
        )

    def _get_config_value(
        self, config: Optional[CheckerConfig], key: str, default: Union[int, float]
    ) -> Union[int, float]:
        """Get configuration value with fallback to default."""
        if config and config.config:
            return config.config.get(key, default)
        return default

    def _count_effective_lines(
        self, test_function: TestFunction, test_file: TestFile
    ) -> int:
        """Count effective lines of code (excluding blank lines and comments)."""
        lines = test_file.content.split("\n")
        start_line = test_function.lineno - 1  # Convert to 0-based index
        end_line = test_function.end_lineno or start_line + len(test_function.body)

        effective_lines = 0

        for i in range(
            start_line + 1, min(end_line, len(lines))
        ):  # Skip function definition line
            line = lines[i].strip()

            # Skip blank lines and comment-only lines
            if line and not line.startswith("#"):
                effective_lines += 1

        return effective_lines
