"""Main entry point for pytestee CLI."""

from .adapters.cli.commands import cli


def main() -> None:
    """Run the main CLI."""
    cli()


if __name__ == "__main__":
    main()
