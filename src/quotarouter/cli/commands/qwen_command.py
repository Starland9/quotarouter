"""Qwen Code CLI command for QuotaRouter."""

import asyncio
from typing import Optional

import typer
from rich.console import Console

from quotarouter.cli.qwen_integration import QwenCLI
from quotarouter.core.router import FreeRouter

console = Console()

app = typer.Typer(help="🦞 Qwen Code Agent with quota routing")


@app.command()
def interactive(
    with_routing: bool = typer.Option(
        False, "--routing", help="Enable QuotaRouter for quota management"
    ),
):
    """Launch interactive Qwen Code agent."""
    console.print("[bold cyan]🦞 Qwen Code Interactive Agent[/bold cyan]")

    router = FreeRouter() if with_routing else None

    async def main():
        cli = QwenCLI(router)
        await cli.run()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        raise typer.Exit()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def chat(
    message: str = typer.Argument(..., help="Message to send to Qwen"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use"),
    stream: bool = typer.Option(True, "--stream/--no-stream", help="Stream response"),
):
    """Send a message to Qwen Code."""
    console.print(f"[cyan]📨 Sending message...[/cyan]")

    async def main():
        cli = QwenCLI()
        if not cli.config.list_providers():
            console.print(
                "[red]❌ No providers configured. Run 'quotarouter qwen interactive' to setup.[/red]"
            )
            raise typer.Exit(1)

        cli.session_manager.create_session("default")
        agent = cli.session_manager.get_current_session()

        if model:
            agent.set_model(model)

        if stream:
            console.print("[cyan]🔄 Streaming response...[/cyan]\n")
            async for chunk in agent.chat_stream(message):
                console.print(chunk, end="")
        else:
            response = await agent.chat(message)
            console.print(f"\n[green]{response}[/green]")

    try:
        asyncio.run(main())
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def analyze(
    language: str = typer.Option("python", "--lang", "-l", help="Programming language"),
    analysis_type: str = typer.Option(
        "general",
        "--type",
        "-t",
        help="Type of analysis (general, bugs, performance, security)",
    ),
):
    """Analyze code with Qwen."""
    console.print(
        "[cyan]📝 Enter code to analyze (end with blank line or Ctrl+D):[/cyan]"
    )

    # Read code from stdin
    lines = []
    try:
        while True:
            line = input()
            if not line and lines:
                break
            lines.append(line)
    except EOFError:
        pass

    code = "\n".join(lines)
    if not code.strip():
        console.print("[yellow]No code provided[/yellow]")
        raise typer.Exit(0)

    console.print(f"\n[cyan]🔍 Analyzing {language} code...[/cyan]\n")

    async def main():
        cli = QwenCLI()
        cli.session_manager.create_session("default")
        agent = cli.session_manager.get_current_session()

        result = await agent.analyze_code(
            code, language=language, analysis_type=analysis_type
        )
        console.print(result)

    try:
        asyncio.run(main())
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def test(
    language: str = typer.Option("python", "--lang", "-l", help="Programming language"),
    framework: Optional[str] = typer.Option(
        None, "--framework", "-f", help="Testing framework"
    ),
):
    """Generate tests for code."""
    console.print(
        "[cyan]📝 Enter code for test generation (end with blank line or Ctrl+D):[/cyan]"
    )

    # Read code from stdin
    lines = []
    try:
        while True:
            line = input()
            if not line and lines:
                break
            lines.append(line)
    except EOFError:
        pass

    code = "\n".join(lines)
    if not code.strip():
        console.print("[yellow]No code provided[/yellow]")
        raise typer.Exit(0)

    console.print(f"\n[cyan]✅ Generating tests...[/cyan]\n")

    async def main():
        cli = QwenCLI()
        cli.session_manager.create_session("default")
        agent = cli.session_manager.get_current_session()

        result = await agent.generate_tests(
            code, language=language, framework=framework
        )
        console.print(result)

    try:
        asyncio.run(main())
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def refactor(
    language: str = typer.Option("python", "--lang", "-l", help="Programming language"),
):
    """Refactor code."""
    console.print(
        "[cyan]📝 Enter code to refactor (end with blank line or Ctrl+D):[/cyan]"
    )

    # Read code from stdin
    lines = []
    try:
        while True:
            line = input()
            if not line and lines:
                break
            lines.append(line)
    except EOFError:
        pass

    code = "\n".join(lines)
    if not code.strip():
        console.print("[yellow]No code provided[/yellow]")
        raise typer.Exit(0)

    console.print(f"\n[cyan]♻️  Refactoring code...[/cyan]\n")

    async def main():
        cli = QwenCLI()
        cli.session_manager.create_session("default")
        agent = cli.session_manager.get_current_session()

        result = await agent.refactor_code(code, language=language)
        console.print(result)

    try:
        asyncio.run(main())
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def explain(
    language: str = typer.Option("python", "--lang", "-l", help="Programming language"),
    detail: str = typer.Option(
        "medium", "--detail", "-d", help="Detail level (simple, medium, detailed)"
    ),
):
    """Explain code."""
    console.print(
        "[cyan]📝 Enter code to explain (end with blank line or Ctrl+D):[/cyan]"
    )

    # Read code from stdin
    lines = []
    try:
        while True:
            line = input()
            if not line and lines:
                break
            lines.append(line)
    except EOFError:
        pass

    code = "\n".join(lines)
    if not code.strip():
        console.print("[yellow]No code provided[/yellow]")
        raise typer.Exit(0)

    console.print(f"\n[cyan]📖 Explaining code...[/cyan]\n")

    async def main():
        cli = QwenCLI()
        cli.session_manager.create_session("default")
        agent = cli.session_manager.get_current_session()

        result = await agent.explain_code(code, language=language, detail_level=detail)
        console.print(result)

    try:
        asyncio.run(main())
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def models():
    """List available Qwen Code models."""

    async def main():
        cli = QwenCLI()
        models = (
            cli.current_agent.mcp.get_available_providers() if cli.current_agent else []
        )

        if not models:
            console.print("[yellow]No models configured[/yellow]")
            raise typer.Exit(1)

        console.print("[bold cyan]📦 Available Models:[/bold cyan]")
        for model in models:
            console.print(
                f"  • [bold]{model['id']:<25}[/bold] ({model['protocol']}) - {model['description']}"
            )

    try:
        asyncio.run(main())
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def auth():
    """Configure Qwen Code authentication."""

    async def main():
        cli = QwenCLI()
        await cli.setup_provider()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        raise typer.Exit()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
