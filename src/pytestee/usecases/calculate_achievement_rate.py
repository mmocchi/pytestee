"""Calculate achievement rate use case."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pytestee.domain.models import (
    AchievementRateResult,
    CheckSuccess,
    RuleAchievementRate,
)
from pytestee.usecases.analyze_tests import AnalyzeTestsUseCase

if TYPE_CHECKING:
    from pathlib import Path

    from pytestee.domain.interfaces import (
        ICheckerRegistry,
        IConfigManager,
        ITestRepository,
    )


class CalculateAchievementRateUseCase:
    """Calculate achievement rate for each rule."""

    def __init__(
        self,
        test_repository: ITestRepository,
        checker_registry: ICheckerRegistry,
        config_manager: IConfigManager,
    ) -> None:
        """Initialize the use case.

        Args:
            test_repository: Test repository for file access
            checker_registry: Registry for rule checkers
            config_manager: Configuration manager

        """
        self._test_repository = test_repository
        self._checker_registry = checker_registry
        self._config_manager = config_manager

    def execute(
        self,
        target: Path,
        config_overrides: dict[str, Any] | None = None,
    ) -> AchievementRateResult:
        """Execute achievement rate calculation.

        Args:
            target: Path to analyze
            config_overrides: Configuration overrides

        Returns:
            Achievement rate result

        """
        if config_overrides is None:
            config_overrides = {}

        # First, run the regular analysis to get all check results
        analyze_use_case = AnalyzeTestsUseCase(
            test_repository=self._test_repository,
            checker_registry=self._checker_registry,
            config_manager=self._config_manager,
        )

        analysis_result = analyze_use_case.execute(target, config_overrides)

        # Group results by rule ID
        rule_results: dict[str, dict[str, Any]] = {}

        for result in analysis_result.check_results:
            rule_id = result.rule_id
            if rule_id not in rule_results:
                rule_results[rule_id] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "checker_name": result.checker_name,
                }

            rule_results[rule_id]["total"] += 1

            # Check if this is a success or failure
            if isinstance(result, CheckSuccess):
                rule_results[rule_id]["passed"] += 1
            else:
                rule_results[rule_id]["failed"] += 1

        # Create RuleAchievementRate objects
        rule_rates = []
        for rule_id, stats in rule_results.items():
            rule_rate = RuleAchievementRate(
                rule_id=rule_id,
                checker_name=str(stats["checker_name"]),
                total_checks=int(stats["total"]),
                passed_checks=int(stats["passed"]),
                failed_checks=int(stats["failed"]),
            )
            rule_rates.append(rule_rate)

        # Sort by rule ID for consistent output
        rule_rates.sort(key=lambda x: x.rule_id)

        # Calculate overall achievement rate
        overall_rate = analysis_result.success_rate

        return AchievementRateResult(
            total_files=analysis_result.total_files,
            total_tests=analysis_result.total_tests,
            rule_rates=rule_rates,
            overall_rate=overall_rate,
        )
