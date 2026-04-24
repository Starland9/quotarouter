"""Stream command - Stream long responses."""

import sys
import typer
from rich.console import Console

from ...core.router import FreeRouter

console = Console()


def stream_command(
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
