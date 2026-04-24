"""Interactive chat command - Multi-turn conversation with memory."""

import json
import typer
import time
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.live import Live
from rich.table import Table
from rich.align import Align
from rich.text import Text

from ...core.router import FreeRouter

console = Console()


def _load_history(history_file: Path) -> list[dict]:
    """Load conversation history from file."""
    if history_file.exists():
        try:
            with console.status("[bold cyan]📂 Loading history...[/bold cyan]"):
                time.sleep(0.3)  # Brief visual feedback
                with open(history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_history(history: list[dict], history_file: Path) -> None:
    """Save conversation history to file."""
    try:
        with console.status("[bold cyan]💾 Saving history...[/bold cyan]"):
            time.sleep(0.2)
            history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
    except IOError as e:
        console.print(f"[yellow]⚠️  Warning: Could not save history: {e}[/yellow]")


def _show_help() -> None:
    """Show available commands with animated display."""
    commands = [
        ("🆘 /help", "Show this help message", "cyan"),
        ("🗑️  /clear", "Clear conversation history", "yellow"),
        ("💾 /save", "Save conversation to file", "green"),
        ("📂 /load", "Load previous conversation", "green"),
        ("📝 /history", "Show current conversation history", "blue"),
        ("📊 /status", "Show provider quota status", "magenta"),
        ("🚀 /stream", "Enable streaming: /stream Your message", "bright_cyan"),
        ("⚙️  /system", "Set or show system prompt", "bright_magenta"),
        ("🚪 /exit", "Exit chat", "bright_red"),
    ]

    # Create formatted command list
    help_content = ""
    for cmd, desc, color in commands:
        help_content += f"\n[{color}]{cmd:<20}[/{color}] {desc}"

    tips = """

[bold cyan]💡 Pro Tips:[/bold cyan]
• [green]Multi-turn context[/green] - Full conversation history is maintained
• [green]Streaming responses[/green] - See answers generate in real-time
• [green]Auto-save[/green] - Conversations saved to ~/.quotarouter/chat_history.json
• [green]Provider switching[/green] - Seamlessly switches if quota exhausted
    """

    console.print(
        Panel(
            help_content.strip() + tips,
            border_style="cyan",
            title="💬 Chat Commands",
            expand=False,
        )
    )


def _show_status(router: FreeRouter) -> None:
    """Show current provider status with animated display."""
    with console.status("[bold cyan]🔍 Fetching provider status...[/bold cyan]"):
        time.sleep(0.3)
        status = router.get_status()

    # Create a table for providers
    table = Table(
        title="📊 Provider Status", show_header=True, header_style="bold cyan"
    )
    table.add_column("Provider", style="cyan", width=20)
    table.add_column("Status", justify="center", width=10)
    table.add_column("Quota", justify="center", width=25)
    table.add_column("Usage", style="green", width=20)

    for provider in status.get("providers", []):
        name = provider["name"]
        available = "✅ Online" if provider.get("available", False) else "❌ Offline"
        quota_pct = provider.get("quota_percentage", 0)
        tokens_used = provider.get("tokens_used", 0)
        token_limit = provider.get("token_limit", 0)

        # Color based on quota usage
        if quota_pct > 80:
            quota_color = "red"
        elif quota_pct > 50:
            quota_color = "yellow"
        else:
            quota_color = "green"

        quota_bar = "█" * int(quota_pct / 5) + "░" * (20 - int(quota_pct / 5))
        quota_text = f"[{quota_color}][{quota_bar}] {quota_pct:.1f}%[/{quota_color}]"
        usage_text = f"{tokens_used:,} / {token_limit:,}"

        table.add_row(name, available, quota_text, usage_text)

    console.print(table)

    # Show active provider info
    active = status.get("active_provider", "Unknown")
    total_used = status.get("total_tokens_used", 0)

    info_panel = f"[cyan]🎯 Active:[/cyan] [bold]{active}[/bold]  [cyan]📈 Today:[/cyan] [bold green]{total_used:,}[/bold green] tokens"
    console.print(Panel(info_panel, border_style="green", padding=(1, 2)))


def _show_history(history: list[dict]) -> None:
    """Display conversation history with formatted output."""
    if not history:
        console.print("[yellow]📭 No conversation history yet.[/yellow]")
        return

    # Create conversation display
    panel_content = ""
    for i, msg in enumerate(history, 1):
        role = msg["role"].upper()
        content = (
            msg["content"][:100] + "..."
            if len(msg["content"]) > 100
            else msg["content"]
        )
        icon = "👤" if role == "USER" else "🤖"
        color = "cyan" if role == "USER" else "green"

        line_num = Text(f"{i:2}.", style="dim white")
        panel_content += f"\n{line_num} [{color}]{icon} {role}[/{color}]: {content}"

    console.print(
        Panel(
            panel_content.strip(),
            border_style="blue",
            title=f"📝 Conversation History ({len(history)} messages)",
            padding=(1, 2),
        )
    )


def _print_response_header() -> None:
    """Print a formatted response header."""
    console.print()


def _print_typing_animation(text: str, use_markdown: bool = False) -> None:
    """Print text with typing animation effect."""
    # For streaming, we'll use Live display for better animation
    if use_markdown:
        console.print(Markdown(text))
    else:
        # Print with slight delay for visual effect
        for char in text:
            console.print(char, end="", soft_wrap=True)
            time.sleep(0.001)  # Minimal delay for smooth output
        console.print()  # New line after typing


def chat_command(
    system: str = typer.Option(
        "You are a helpful assistant.",
        "--system",
        "-s",
        help="System prompt for the conversation",
    ),
    max_tokens: int = typer.Option(
        4096,
        "--max-tokens",
        "-m",
        help="Maximum response tokens",
    ),
    history_file: str = typer.Option(
        "~/.quotarouter/chat_history.json",
        "--history",
        "-h",
        help="Path to save conversation history",
    ),
):
    """
    Start an interactive chat with memory and streaming support.

    Features:
    • Multi-turn conversation with automatic history management
    • Streaming responses for real-time feedback
    • Auto-save conversation to JSON
    • Provider status monitoring
    • System prompt customization

    Example:
        quotarouter chat
        quotarouter chat --system "You are a Python expert"
        quotarouter chat --max-tokens 8000
    """

    # Expand home directory
    history_path = Path(history_file).expanduser()

    try:
        with console.status("[bold cyan]🤖 Initializing QuotaRouter...[/bold cyan]"):
            time.sleep(0.5)
            router = FreeRouter(verbose=False)

        # Load previous history if it exists
        history = _load_history(history_path)
        current_system = system

        # Animated welcome screen
        welcome_lines = [
            "[bold cyan]🤖 QuotaRouter Interactive Chat[/bold cyan]",
            "",
            f"[cyan]✨ System:[/cyan] {current_system[:60]}{'...' if len(current_system) > 60 else ''}",
            f"[cyan]⚙️  Max Tokens:[/cyan] {max_tokens}",
            f"[cyan]💬 Messages:[/cyan] {len(history)} previous",
            "",
            "[bold green]Type [/bold green][green]/help[/green][bold green] for commands or start typing[/bold green]",
        ]

        welcome_text = "\n".join(welcome_lines)
        console.print(
            Panel(
                welcome_text,
                border_style="cyan",
                title="💬 Welcome",
                expand=False,
            )
        )

        while True:
            try:
                # Get user input
                user_input = Prompt.ask("[bold cyan]You[/bold cyan]").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    if user_input in ["/exit", "/quit"]:
                        console.print(
                            Panel(
                                "[bold green]👋 Goodbye![/bold green]\n[dim]Chat history saved[/dim]",
                                border_style="green",
                                padding=(1, 2),
                            )
                        )
                        if history:
                            _save_history(history, history_path)
                        break

                    elif user_input == "/help":
                        _show_help()

                    elif user_input == "/clear":
                        history = []
                        console.print("[green]✓ Conversation history cleared[/green]")

                    elif user_input == "/history":
                        _show_history(history)

                    elif user_input == "/status":
                        _show_status(router)

                    elif user_input == "/save":
                        _save_history(history, history_path)
                        console.print(
                            Panel(
                                f"✓ Saved to [cyan]{history_path}[/cyan]",
                                border_style="green",
                                padding=(0, 1),
                            )
                        )

                    elif user_input.startswith("/system"):
                        parts = user_input.split(maxsplit=1)
                        if len(parts) > 1:
                            current_system = parts[1]
                            console.print(
                                Panel(
                                    f"⚙️  System prompt updated\n[dim]{current_system}[/dim]",
                                    border_style="yellow",
                                    padding=(0, 1),
                                )
                            )
                        else:
                            console.print(
                                Panel(
                                    f"[cyan]{current_system}[/cyan]",
                                    border_style="blue",
                                    title="⚙️  Current System Prompt",
                                    padding=(1, 1),
                                )
                            )

                    elif user_input.startswith("/load"):
                        with console.status("[bold cyan]📂 Loading...[/bold cyan]"):
                            time.sleep(0.3)
                            parts = user_input.split(maxsplit=1)
                            if len(parts) > 1:
                                custom_path = Path(parts[1]).expanduser()
                                loaded = _load_history(custom_path)
                            else:
                                loaded = _load_history(history_path)

                            if loaded:
                                history = loaded
                                console.print(
                                    Panel(
                                        f"[green]✓ Loaded {len(loaded)} messages[/green]",
                                        border_style="green",
                                        padding=(0, 1),
                                    )
                                )
                            else:
                                console.print(
                                    Panel(
                                        "[red]✗ No history found[/red]",
                                        border_style="red",
                                        padding=(0, 1),
                                    )
                                )

                    else:
                        console.print(
                            Panel(
                                "[yellow]⚠️  Unknown command. Type [/yellow][green]/help[/green][yellow] for help[/yellow]",
                                border_style="yellow",
                                padding=(0, 1),
                            )
                        )

                    continue

                # Check for streaming prefix
                use_streaming = False
                message = user_input

                if user_input.startswith("/stream "):
                    use_streaming = True
                    message = user_input[8:]  # Remove "/stream " prefix

                # Add user message to history
                history.append({"role": "user", "content": message})

                # Display user message with emoji
                user_panel = f"👤 [cyan]{message}[/cyan]"
                console.print(Panel(user_panel, border_style="cyan", padding=(0, 1)))

                # Show spinner while processing
                spinner_text = "[bold cyan]🤖 Thinking" + (
                    "..." if use_streaming else " (streaming)..."
                )

                if use_streaming:
                    # Stream the response with spinner
                    console.print(
                        f"[bold green]🤖 Assistant[/bold green] [dim](streaming)[/dim]"
                    )
                    full_response = ""

                    for chunk in router.complete_stream(
                        prompt=message,
                        system=current_system,
                        history=history[:-1],
                        max_tokens=max_tokens,
                    ):
                        console.print(chunk, end="", soft_wrap=True)
                        full_response += chunk

                    console.print()  # New line after streaming
                    response = full_response
                else:
                    # Non-streaming response with loading animation
                    with console.status(f"[bold cyan]🤖 Thinking...[/bold cyan]"):
                        response = router.complete(
                            prompt=message,
                            system=current_system,
                            history=history[:-1],
                            max_tokens=max_tokens,
                        )

                    # Display response in a panel
                    console.print(f"[bold green]🤖 Assistant[/bold green]")
                    console.print(response)

                # Add assistant response to history
                history.append({"role": "assistant", "content": response})

                # Auto-save history with subtle feedback
                with console.status("[dim]💾 Saving...[/dim]", spinner="dots"):
                    time.sleep(0.15)
                    _save_history(history, history_path)

            except KeyboardInterrupt:
                console.print("\n")
                console.print(
                    Panel(
                        "[yellow]⏹️  Chat interrupted[/yellow]\n[dim]Saving history...[/dim]",
                        border_style="yellow",
                        padding=(1, 2),
                    )
                )
                if history:
                    _save_history(history, history_path)
                console.print("[green]✓ Goodbye![/green]")
                break
            except Exception as e:
                console.print(
                    Panel(
                        f"[red]❌ Error:[/red] {str(e)}\n[dim]Continuing chat...[/dim]",
                        border_style="red",
                        padding=(1, 1),
                    )
                )

    except Exception as e:
        console.print(
            Panel(
                f"[bold red]💥 Fatal Error[/bold red]\n\n{str(e)}",
                border_style="red",
                padding=(1, 2),
                title="Error",
            )
        )
        raise typer.Exit(code=1)
