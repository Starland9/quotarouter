"""Reset command - Reset quotas."""

import typer
from rich.console import Console

from ...core.router import FreeRouter

console = Console()


def reset_command():
    """
    Reset all quota counters to zero.

    Useful for testing. In production, quotas reset automatically at midnight.

    WARNING: This resets all tracked token usage.
    """
    try:
        if typer.confirm("Are you sure you want to reset all quotas?"):
            router = FreeRouter(verbose=False)
            router.reset_quotas()
            console.print("[green]✅ All quotas reset[/green]")
        else:
            console.print("[yellow]Cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
