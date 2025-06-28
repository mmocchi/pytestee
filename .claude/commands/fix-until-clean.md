# Fix Until Clean

Runs `task check` repeatedly, fixing any errors that are found until the codebase passes all checks.

## Steps

1. Run `task check` to identify all linting, formatting, type checking, and test issues
2. Analyze the output to understand what needs to be fixed
3. Fix the identified issues systematically:
   - Auto-fix linting issues with `uv run ruff check --fix`
   - Format code with `task format`
   - Fix type checking errors manually
   - Fix any failing tests
4. Re-run `task check` to verify fixes
5. Repeat steps 1-4 until `task check` passes completely with no errors

## Usage

This command is useful for:
- Ensuring code quality before committing
- Cleaning up a codebase after major changes
- Preparing code for review or deployment
- Maintaining consistent code standards

## Notes

- Uses the project's configured tools (ruff, mypy, pytest)
- Follows the project's quality standards as defined in pyproject.toml
- May require manual intervention for complex type errors or test failures
- Will stop if unable to make progress on fixing errors