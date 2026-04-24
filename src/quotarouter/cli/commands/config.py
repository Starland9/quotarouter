"""Config command - Show configuration."""

import typer
from rich.console import Console
from rich.table import Table

from ...config.registry import DEFAULT_PROVIDERS

console = Console()


def config_command(
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
