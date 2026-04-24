"""
QuotaRouter CLI - Command-line interface for FreeRouter.

Provides commands to interact with FreeRouter from the terminal.
"""

from __future__ import annotations

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .core.router import FreeRouter
from .core.types import ProviderConfig
from .config.registry import DEFAULT_PROVIDERS

app = typer.Typer(
    name="quotarouter",
    help="🔀 Quota-aware LLM routing engine with automatic provider fallback.",
    no_args_is_help=True,
)

console = Console()


@app.command()
def status():
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


@app.command()
def complete(
    prompt: str = typer.Argument(..., help="The prompt to send to the LLM"),
    system: str = typer.Option(
        "You are a helpful assistant.",
        "--system",
        "-s",
        help="System prompt",
    ),
    max_tokens: int = typer.Option(
        4096,
        "--max-tokens",
        "-m",
        help="Maximum response tokens",
    ),
):
    """
    Send a prompt and get a response.

    Automatically routes to the next available provider if quota is exhausted.

    Example:
        quotarouter complete "Explain quantum computing"
        quotarouter complete "Why is Python great?" --system "You are a Python expert"
    """
    try:
        console.print(f"[cyan]Prompt:[/cyan] {prompt}")
        console.print(f"[cyan]Max tokens:[/cyan] {max_tokens}")
        console.print()

        router = FreeRouter(verbose=False)

        with console.status("[bold green]Routing request...[/bold green]"):
            response = router.complete(
                prompt=prompt,
                system=system,
                max_tokens=max_tokens,
            )

        console.print("[bold cyan]Response:[/bold cyan]")
        console.print(response)

        # Show stats
        status_data = router.status()
        session = status_data["session"]
        console.print(
            f"\n[dim]Session: {session['requests']} requests, "
            f"{session['tokens']:,} tokens used, "
            f"{session['fallbacks']} fallbacks[/dim]"
        )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        raise typer.Exit(code=1)


@app.command()
def stream(
    prompt: str = typer.Argument(..., help="The prompt to send to the LLM"),
    system: str = typer.Option(
        "You are a helpful assistant.",
        "--system",
        "-s",
        help="System prompt",
    ),
    max_tokens: int = typer.Option(
        4096,
        "--max-tokens",
        "-m",
        help="Maximum response tokens",
    ),
):
    """
    Stream a response from the LLM.

    Useful for long responses, prints each chunk as it arrives.

    Example:
        quotarouter stream "Write a 500-word essay about AI"
        quotarouter stream "Explain machine learning" --max-tokens 2000
    """
    try:
        console.print(f"[cyan]Prompt:[/cyan] {prompt}")
        console.print(f"[cyan]Max tokens:[/cyan] {max_tokens}\n")

        router = FreeRouter(verbose=False)

        console.print("[bold cyan]Response:[/bold cyan]")
        total_tokens = 0

        for chunk in router.complete_stream(
            prompt=prompt,
            system=system,
            max_tokens=max_tokens,
        ):
            console.print(chunk, end="", highlight=False)
            total_tokens += len(chunk) // 4

        console.print()

        # Show stats
        status_data = router.status()
        session = status_data["session"]
        console.print(
            f"\n[dim]Session: {session['requests']} requests, "
            f"{session['tokens']:,} tokens used, "
            f"{session['fallbacks']} fallbacks[/dim]"
        )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        raise typer.Exit(code=1)


@app.command()
def reset():
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
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        raise typer.Exit(code=1)


@app.command()
def config(
    list_vars: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List required API key variables",
    ),
):
    """
    Show or manage configuration.

    Example:
        quotarouter config --list  # Show all required API keys
    """
    if list_vars:
        table = Table(
            title="Required API Key Environment Variables",
            show_header=True,
            header_style="bold cyan",
        )

        table.add_column("Provider", style="magenta")
        table.add_column("Environment Variable")
        table.add_column("Get Key")

        providers_map = {
            "Cerebras": ("CEREBRAS_API_KEY", "console.cerebras.ai"),
            "Groq": ("GROQ_API_KEY", "console.groq.com"),
            "Google AI Studio": ("GOOGLE_AI_API_KEY", "aistudio.google.com"),
            "Mistral AI": ("MISTRAL_API_KEY", "console.mistral.ai"),
            "OpenRouter": ("OPENROUTER_API_KEY", "openrouter.ai"),
            "Alibaba DashScope": ("ALIBABA_API_KEY", "dashscope.aliyun.com"),
        }

        for provider, (var, url) in providers_map.items():
            table.add_row(provider, var, url)

        console.print(table)
        console.print(
            "\n[yellow]Tip:[/yellow] Set these variables in a [cyan].env[/cyan] file "
            "in your project directory, or export them in your shell."
        )
    else:
        # Show default providers
        table = Table(
            title="Configured Providers",
            show_header=True,
            header_style="bold cyan",
        )

        table.add_column("Priority", justify="right")
        table.add_column("Provider", style="magenta")
        table.add_column("Model")
        table.add_column("Daily Limit")
        table.add_column("RPM Limit", justify="right")

        for p in DEFAULT_PROVIDERS:
            daily_limit_k = p.daily_token_limit // 1000
            table.add_row(
                str(p.priority),
                p.name,
                p.model,
                f"{daily_limit_k:,}K",
                str(p.rpm_limit),
            )

        console.print(table)


@app.callback()
def main():
    """🔀 QuotaRouter - Quota-aware LLM routing engine."""
    pass


if __name__ == "__main__":
    app()
