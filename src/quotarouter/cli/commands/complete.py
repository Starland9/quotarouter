"""Complete command - Send simple completion requests."""

import sys
import typer
from rich.console import Console

from ...core.router import FreeRouter

console = Console()


def complete_command(
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
