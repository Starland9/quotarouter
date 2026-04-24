"""
QuotaRouter CLI entry point.

Allow running quotarouter as:
    python -m quotarouter --help
    python -m quotarouter status
    quotarouter complete "Your prompt here"
"""

from .cli import app

if __name__ == "__main__":
    app()
