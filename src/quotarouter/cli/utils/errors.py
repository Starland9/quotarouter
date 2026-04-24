"""
Error handling utilities for CLI commands.
"""

import sys
from typing import NoReturn

from rich.console import Console

console = Console()


def print_error(message: str, exit_code: int = 1) -> NoReturn:
    """
    Print error message and exit.

    Args:
        message: Error message to display
        exit_code: Exit code (default 1)
    """
    console.print(f"[red]Error:[/red] {message}", file=sys.stderr)
    raise SystemExit(exit_code)


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow]Warning:[/yellow] {message}")


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]✅[/green] {message}")
