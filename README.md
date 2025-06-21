# pytestee

A pytest test quality checker CLI tool that analyzes your test code for structural and qualitative issues.

## Features

- **AAA/GWT Pattern Detection**: Checks if tests follow Arrange-Act-Assert or Given-When-Then patterns
- **Assert Density Analysis**: Validates appropriate assertion count and density per test function
- **Clean Architecture**: Extensible design for adding new quality checkers
- **Rich CLI Output**: Beautiful console output with detailed analysis results
- **Configurable**: Supports configuration via files and command-line options

## Installation

```bash
# Install from PyPI (when published)
pip install pytestee

# Or install in development mode
git clone <repository>
cd pytestee
uv sync
```

## Quick Start

```bash
# Check all test files in current directory
pytestee check tests/

# Check a specific test file
pytestee check test_example.py

# Check with custom limits
pytestee check tests/ --max-asserts=5 --min-asserts=1

# Show detailed information
pytestee check tests/ --verbose

# Get JSON output
pytestee check tests/ --format=json
```

## Usage Examples

### Basic Usage

```bash
# Analyze test quality
pytestee check tests/

# Output:
# ❌ test_user.py::test_create_user
#    - AAA pattern not detected (line 15)
#    - Too many assertions: 5 (recommended: ≤3)
#
# ✅ test_auth.py::test_login_success
#    - AAA pattern: OK
#    - Assert density: OK (2 assertions)
```

### Configuration Options

```bash
# Command line options
pytestee check tests/ --max-asserts=3 --min-asserts=1 --require-aaa-comments

# Quiet mode (errors only)
pytestee check tests/ --quiet

# Verbose mode (detailed info)
pytestee check tests/ --verbose
```

### File Information

```bash
# Show test file statistics
pytestee info tests/

# List available checkers
pytestee list-checkers
```

## Configuration

### Configuration File

Create `.pytestee.toml` or add to `pyproject.toml`:

```toml
[tool.pytestee]
max_asserts = 3
min_asserts = 1
require_aaa_comments = true

[tool.pytestee.aaa_pattern]
enabled = true
[tool.pytestee.aaa_pattern.config]
require_comments = false
allow_gwt = true

[tool.pytestee.assert_density]
enabled = true
[tool.pytestee.assert_density.config]
max_asserts = 3
min_asserts = 1
max_density = 0.5
```

### Environment Variables

```bash
export PYTESTEE_MAX_ASSERTS=5
export PYTESTEE_MIN_ASSERTS=1
export PYTESTEE_REQUIRE_AAA_COMMENTS=true
```

## Quality Checkers

### AAA Pattern Checker

Detects Arrange-Act-Assert or Given-When-Then patterns through:

- **Comment-based detection**: `# Arrange`, `# Act`, `# Assert`
- **Structural separation**: Empty lines separating test sections
- **Code flow analysis**: Logical grouping of setup, execution, and verification

### Assert Density Checker

Analyzes assertion usage:

- **Count validation**: Ensures appropriate number of assertions per test
- **Density analysis**: Checks assertion-to-code ratio
- **Complexity scoring**: Identifies overly complex test functions

## Architecture

Built with Clean Architecture principles:

```
src/pytestee/
├── domain/          # Business logic and models
├── usecases/        # Application logic
├── adapters/        # External interfaces (CLI, repositories, presenters)
├── infrastructure/  # Concrete implementations (AST parsing, checkers)
└── registry.py      # Dependency injection container
```

### Adding Custom Checkers

1. Implement the `IChecker` interface:

```python
from pytestee.domain.interfaces import IChecker
from pytestee.infrastructure.checkers.base_checker import BaseChecker

class MyCustomChecker(BaseChecker):
    def __init__(self):
        super().__init__("my_custom_checker")
    
    def check_function(self, test_function, test_file, config=None):
        # Your checking logic here
        return [CheckResult(...)]
```

2. Register the checker:

```python
from pytestee.registry import CheckerRegistry

registry = CheckerRegistry()
registry.register(MyCustomChecker())
```

## Development

### Setup

```bash
# Install mise for tool management
mise install

# Install dependencies
task install

# Run tests
task test

# Run linting
task lint

# Format code
task format

# Build package
task build
```

### Project Tasks

- `task install` - Install dependencies
- `task test` - Run test suite
- `task lint` - Run linting (ruff + mypy)
- `task format` - Format code
- `task build` - Build package
- `task clean` - Clean build artifacts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite and linting
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Roadmap

- [ ] Additional pattern checkers (Page Object, Builder, etc.)
- [ ] Integration with popular CI/CD systems
- [ ] VS Code extension
- [ ] Test coverage analysis
- [ ] Performance benchmarking
- [ ] Custom rule configuration DSL