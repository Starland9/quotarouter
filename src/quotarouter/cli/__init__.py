"""
QuotaRouter CLI - Command-line interface for FreeRouter.

Modular CLI with commands organized by feature.
Each command is defined in its own module under .commands/
"""

from __future__ import annotations

import typer
from rich.console import Console

from .commands import (
    status_command,
    complete_command,
    stream_command,
    config_command,
    reset_command,
    book_command,
)

console = Console()

app = typer.Typer(
    name="quotarouter",
    help="🔀 Quota-aware LLM routing engine with automatic provider fallback.",
    no_args_is_help=True,
)

# Register all commands with proper names
app.command(name="status")(status_command)
app.command(name="complete")(complete_command)
app.command(name="stream")(stream_command)
app.command(name="config")(config_command)
app.command(name="reset")(reset_command)
app.command(name="book")(book_command)


@app.callback()
def main():
    """🔀 QuotaRouter - Quota-aware LLM routing engine."""
    pass


if __name__ == "__main__":
    app()


__all__ = ["app", "console"]
