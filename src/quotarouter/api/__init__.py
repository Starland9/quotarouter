"""
QuotaRouter API module.

REST API server for LLM routing with Streamlit and web app integration.

Example:
    >>> from quotarouter.api import app
    >>> import uvicorn
    >>> uvicorn.run(app, host="0.0.0.0", port=8000)
"""

from .server import app, get_router

__all__ = ["app", "get_router"]
