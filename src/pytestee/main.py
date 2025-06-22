"""Main entry point for pytestee CLI."""

from pytestee.adapters.cli.commands import cli


def main() -> None:
    """メインCLIを実行します。"""
    cli()


if __name__ == "__main__":
    main()
