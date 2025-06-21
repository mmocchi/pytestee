"""Main entry point for pytestee CLI."""

from .adapters.cli.commands import cli


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
