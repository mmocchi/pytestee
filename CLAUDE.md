# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Development Setup
```bash
# Install dependencies
uv sync

# Run all checks (lint, format, typecheck, test)
task check
```

### Testing
```bash
# Run all tests
task test

# Run specific test file
uv run pytest tests/unit/test_ast_parser.py

# Run specific test with verbose output
uv run pytest tests/integration/test_cli.py::TestCLI::test_check_command_basic -v

# Run tests with coverage
uv run pytest --cov=src/pytestee
```

### Code Quality
```bash
# Run linting
task lint

# Fix auto-fixable lint issues
uv run ruff check --fix

# Run type checking
task typecheck

# Format code
task format
```

### Development
```bash
# Run CLI in development mode
task dev

# Build package
task build

# Clean build artifacts
task clean
```

## Architecture Overview

Pytestee is a pytest test quality checker CLI tool built using Clean Architecture principles. The codebase follows a rule-based architecture where each quality check is implemented as an individual rule module.

### Core Architecture Layers

```
src/pytestee/
├── domain/          # Business logic and models (TestFunction, CheckResult, etc.)
├── usecases/        # Application logic (AnalyzeTestsUseCase, CheckQualityUseCase)
├── adapters/        # External interfaces
│   ├── cli/         # Click-based CLI commands
│   ├── presenters/  # Rich-based console output
│   └── repositories/ # File system access
├── infrastructure/ # Concrete implementations
│   ├── checkers/   # Test quality checkers
│   ├── rules/      # Individual rule implementations
│   ├── config/     # Configuration management
│   └── ast_parser.py # Python AST parsing
└── registry.py     # Dependency injection container
```

### Rule-Based System

The core of pytestee is its rule system organized by categories:

- **PTCM (Pattern Comment)**: Comment-based pattern detection (`# Arrange`, `# Act`, `# Assert`)
- **PTST (Pattern Structural)**: Structural pattern detection (empty line separation)
- **PTLG (Pattern Logic)**: Logical flow pattern detection (AST analysis)
- **PTAS (Pattern Test Assertion)**: Assertion count and density analysis

### Pattern Detection Priority

Pattern checkers follow a priority hierarchy:
1. **Comment-based** (PTCM) - Highest priority
2. **Structural** (PTST) - Medium priority  
3. **Logical** (PTLG) - Low priority
4. **Pattern not detected** (PTST002) - Fallback warning

Only the highest priority pattern found is reported to avoid noise.

### Key Components

**PatternChecker**: Orchestrates pattern detection with priority logic. Contains PTCM001, PTCM002, PTST001, PTST002, and PTLG001 rules.

**AssertionChecker**: Manages assertion-related rules (PTAS001-PTAS005) for count and density analysis.

**BaseRule**: Abstract base class that all rule implementations inherit from. Provides `check()` method and `_create_result()` helper.

**RuleValidator**: Validates rule configurations to prevent conflicts (e.g., PTAS004 conflicts with other assertion count rules).

## Development Guidelines

### Python Version Support
- Minimum Python 3.8
- Use `Union[X, None]` instead of `X | None` for type hints (3.8 compatibility)

### Code Quality Standards
- All functions must have type annotations (ANN201 rule enforced)
- Classes must have docstrings with blank line after (D203/D211 rules)
- Use ruff for linting and formatting
- mypy for type checking with strict mode

### Testing Structure
- Unit tests in `tests/unit/` for individual components
- Integration tests in `tests/integration/` for full workflows  
- Fixture tests in `tests/fixtures/` with example patterns
- Test coverage target: 83%+

### Adding New Rules

1. Create rule module in appropriate `infrastructure/rules/` subdirectory
2. Inherit from `BaseRule` and implement `check()` method
3. Add rule to appropriate checker (PatternChecker or AssertionChecker)
4. Update `RuleValidator` if rule has conflicts
5. Add comprehensive tests including good/bad examples
6. Update fixture files if needed for integration tests

### Configuration
- Uses Click for CLI with rich console output
- Configuration via `pyproject.toml` or `.pytestee.toml`
- Environment variable support with `PYTESTEE_` prefix
- JSON and console output formats supported