"""Status command - Show provider status."""

import sys
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ...core.router import FreeRouter

console = Console()


def status_command():
    """
    Show the status of all configured providers.

    Displays:
    - Which providers are configured (have API keys)
    - Daily token quota usage
    - Remaining tokens
    - Overall quota availability
    """
    try:
        router = FreeRouter(verbose=False)
        status_data = router.status()

        # Build providers table
        table = Table(
            title="🔀 FreeRouter — Provider Status",
            show_header=True,
            header_style="bold cyan",
        )

        table.add_column("Provider", style="magenta")
        table.add_column("Status", justify="center")
        table.add_column("Used", justify="right")
        table.add_column("Limit", justify="right")
        table.add_column("Remaining", justify="right")
        table.add_column("Usage %", justify="right")

        for p in status_data["providers"]:
            icon = "✅" if p["configured"] else "⚪"
            status_icon = (
                "🟢 Available"
                if (p["configured"] and not p["exhausted"])
                else "🔴 Exhausted"
                if p["exhausted"]
                else "⚫ Not configured"
            )

            used_k = p["tokens_used"] // 1000
            limit_k = p["tokens_limit"] // 1000
            remaining_k = p["tokens_remaining"] // 1000
            pct = f"{p['pct_used']:.1f}%"

            table.add_row(
                f"{icon} {p['name']}",
                status_icon,
                f"{used_k:,}K",
                f"{limit_k:,}K",
                f"{remaining_k:,}K",
                pct,
            )

        console.print(table)

        # Summary
        configured_count = sum(1 for p in status_data["providers"] if p["configured"])
        total_remaining = sum(
            p["tokens_remaining"] for p in status_data["providers"] if p["configured"]
        )

        summary = (
            f"\n🟢 {configured_count}/{len(status_data['providers'])} providers configured  |  "
            f"~{total_remaining:,} tokens available today"
        )
        console.print(Panel(summary, expand=False))

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        raise typer.Exit(code=1)
