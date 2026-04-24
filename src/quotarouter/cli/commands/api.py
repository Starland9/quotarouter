"""
API server command for CLI.

Starts the FastAPI server for REST API access.
"""

from __future__ import annotations

import typer


def api_command(
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        help="Host to bind server to",
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Port to listen on",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        help="Enable auto-reload on file changes (development)",
    ),
    workers: int = typer.Option(
        1,
        "--workers",
        "-w",
        help="Number of worker processes",
    ),
) -> None:
    """
    Launch the QuotaRouter REST API server.

    The API provides endpoints for:
    - Single & streaming completions
    - Provider status & quota information
    - Book generation
    - Configuration details

    Examples:
        # Start on default 0.0.0.0:8000
        quotarouter api

        # Custom host and port
        quotarouter api --host localhost --port 9000

        # Development with auto-reload
        quotarouter api --reload

        # Production with 4 workers
        quotarouter api --workers 4

    After starting, access:
        - API docs (Swagger): http://localhost:8000/docs
        - Alternative docs (ReDoc): http://localhost:8000/redoc
        - Health check: http://localhost:8000/health

    Integration with Streamlit:
        >>> import requests
        >>> response = requests.post(
        ...     "http://localhost:8000/complete",
        ...     json={"prompt": "Hello world"}
        ... )
        >>> print(response.json()["text"])
    """
    try:
        import uvicorn
    except ImportError:
        from ..utils.errors import print_error

        print_error(
            "uvicorn not installed. Install with: pip install uvicorn[standard]"
        )

    from quotarouter.api import app as fastapi_app
    from rich.console import Console

    console = Console()

    console.print("[green]🚀 Starting QuotaRouter API server[/green]")
    console.print(f"[cyan]  Host:[/cyan] {host}")
    console.print(f"[cyan]  Port:[/cyan] {port}")
    console.print(f"[cyan]  Reload:[/cyan] {'enabled' if reload else 'disabled'}")
    console.print(f"[cyan]  Workers:[/cyan] {workers}")
    console.print()
    console.print("[yellow]📚 API Documentation:[/yellow]")
    console.print(f"[cyan]  http://{host}:{port}/docs[/cyan]")
    console.print(f"[cyan]  http://{host}:{port}/redoc[/cyan]")
    console.print()

    uvicorn.run(
        fastapi_app,
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,  # Force 1 worker with reload
        log_level="info",
    )


__all__ = ["api_command"]
