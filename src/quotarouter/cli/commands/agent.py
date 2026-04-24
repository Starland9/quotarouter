"""Autopilot agent command - Autonomous project development."""

import asyncio
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from quotarouter.core.router import FreeRouter
from quotarouter.agents.autonomous import AutopilotAgent

console = Console()


def agent_command(
    project_dir: str = typer.Argument(
        ".",
        help="Project directory to develop"
    ),
    autopilot: bool = typer.Option(
        False,
        "--autopilot",
        "-a",
        help="Run in fully autonomous mode without prompts"
    ),
    new_plan: bool = typer.Option(
        False,
        "--new",
        "-n",
        help="Create a new plan instead of loading existing one"
    ),
    max_iterations: int = typer.Option(
        100,
        "--max-iterations",
        "-m",
        help="Maximum iterations before stopping"
    ),
    system_prompt: str = typer.Option(
        None,
        "--system",
        "-s",
        help="Custom system prompt for the agent"
    ),
):
    """
    🤖 Autonomous development agent with autopilot mode.

    Automatically plans, implements, and completes development tasks.
    
    Features:
    • Project analysis and planning
    • Autonomous task execution
    • Progress tracking and checkpoints
    • Interactive approval workflow
    • Full autopilot mode with --autopilot flag

    Examples:
        quotarouter agent .
        quotarouter agent . --autopilot
        quotarouter agent /path/to/project --new --autopilot
        quotarouter agent . --max-iterations 200
        quotarouter agent . --system "You are a Python expert"

    The agent will:
    1. Analyze the project structure
    2. Create a development plan with tasks
    3. Execute tasks one by one
    4. Request approval (unless --autopilot is enabled)
    5. Track progress and save state
    6. Continue until all tasks are complete
    """
    
    try:
        project_path = Path(project_dir).expanduser().resolve()
        
        if not project_path.exists():
            console.print(f"[red]❌ Project directory not found: {project_path}[/red]")
            raise typer.Exit(code=1)

        # Welcome message
        console.print(Panel(
            "[bold cyan]🤖 QuotaRouter Autopilot Agent[/bold cyan]\n\n"
            f"[cyan]📁 Project:[/cyan] {project_path}\n"
            f"[cyan]🔄 Iterations:[/cyan] {max_iterations}\n"
            f"[cyan]⚙️  Mode:[/cyan] {'Fully Autonomous' if autopilot else 'Interactive'}",
            border_style="cyan",
            title="🚀 Starting Autopilot",
        ))

        # Initialize agent
        with console.status("[bold cyan]🔧 Initializing agent...[/bold cyan]"):
            router = FreeRouter(verbose=False)
            agent = AutopilotAgent(
                project_dir=str(project_path),
                router=router,
                max_iterations=max_iterations,
                auto_approve=autopilot,
            )

            # Override system prompt if provided
            if system_prompt:
                agent.system_prompt = system_prompt

        # Run autopilot
        asyncio.run(agent.run_autopilot(create_new_plan=new_plan))

        console.print(Panel(
            "[bold green]✅ Autopilot session complete![/bold green]\n\n"
            f"[cyan]📊 Results saved to:[/cyan] {project_path}/.autopilot",
            border_style="green",
            title="🎉 Complete",
        ))

    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️  Autopilot interrupted by user[/yellow]")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(f"[red]❌ Fatal error:[/red] {str(e)}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)
