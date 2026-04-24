"""
FastAPI server for QuotaRouter LLM API.

Exposes REST endpoints for LLM completions, streaming, status checking,
and configuration. Perfect for integration with Streamlit, web apps, etc.

Example:
    >>> from quotarouter.api.server import app
    >>> import uvicorn
    >>> uvicorn.run(app, host="0.0.0.0", port=8000)

Then in your Streamlit app:
    >>> import requests
    >>> response = requests.post(
    ...     "http://localhost:8000/complete",
    ...     json={"prompt": "Hello world"}
    ... )
    >>> print(response.json()["text"])
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from quotarouter import FreeRouter

from .models import (
    BookRequest,
    BookResponse,
    CompletionRequest,
    CompletionResponse,
    ConfigResponse,
    ErrorResponse,
    ResetResponse,
    StatusResponse,
    ProviderStatus,
    StreamChunk,
    StreamingCompletionRequest,
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="QuotaRouter API",
    description="Quota-aware LLM routing engine with multi-provider fallback",
    version="0.8.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware for Streamlit and web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global router instance
_router: FreeRouter | None = None


def get_router() -> FreeRouter:
    """Get or initialize the router."""
    global _router
    if _router is None:
        _router = FreeRouter(verbose=True)
    return _router


# ── Health & Info Endpoints ─────────────────────────────────────


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        {"status": "ok", "timestamp": ISO timestamp}
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/config", response_model=ConfigResponse, tags=["Configuration"])
async def get_config() -> ConfigResponse:
    """
    Get current configuration and available providers.

    Returns:
        ConfigResponse with provider list, storage backend, and versions.
    """
    router = get_router()

    return ConfigResponse(
        configured_providers=[p.name for p in router.providers],
        storage_backend="json",
        verbose_mode=router.verbose,
        api_version="0.8.0",
        quotarouter_version="0.8.0",
    )


@app.get("/status", response_model=StatusResponse, tags=["Status"])
async def get_status() -> StatusResponse:
    """
    Get current status of all providers and quota usage.

    Returns:
        StatusResponse with detailed provider information and statistics.
    """
    router = get_router()

    providers_status = []
    for provider in router.providers:
        # Calculate quota percentage
        token_percentage = 0.0
        if provider.daily_token_limit and provider.daily_token_limit > 0:
            token_percentage = (
                provider.tokens_used_today / provider.daily_token_limit
            ) * 100

        providers_status.append(
            ProviderStatus(
                name=provider.name,
                available=not provider.is_exhausted,
                tokens_used=provider.tokens_used_today,
                token_limit=provider.daily_token_limit,
                requests_used=provider.requests_this_minute,
                request_limit=provider.rpm_limit,
                quota_percentage=min(token_percentage, 100.0),
                priority=provider.priority,
            )
        )

    # Find first available provider
    active_provider = next(
        (p.name for p in router.providers if not p.is_exhausted),
        router.providers[0].name if router.providers else "unknown",
    )

    return StatusResponse(
        providers=providers_status,
        active_provider=active_provider,
        total_tokens_used=router._total_tokens,
        total_requests=router._total_requests,
        fallback_count=router._fallback_count,
    )


# ── Completion Endpoints ────────────────────────────────────────


@app.post("/complete", response_model=CompletionResponse, tags=["Completion"])
async def complete(request: CompletionRequest) -> CompletionResponse:
    """
    Generate a single completion.

    Args:
        request: CompletionRequest with prompt and sampling parameters.

    Returns:
        CompletionResponse with generated text and metadata.

    Raises:
        HTTPException: If all providers are quota-exhausted.
    """
    router = get_router()

    try:
        response = router.complete(
            prompt=request.prompt,
            system=request.system,
            max_tokens=request.max_tokens,
        )

        return CompletionResponse(
            text=response.get("text", ""),
            provider=response.get("provider", "unknown"),
            tokens_used=response.get("tokens_used", 0),
            stop_reason=response.get("stop_reason"),
        )

    except Exception as e:
        logger.error(f"Completion failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "completion_failed",
                "message": str(e),
            },
        ) from e


@app.post("/stream", tags=["Streaming"])
async def stream(request: StreamingCompletionRequest) -> StreamingResponse:
    """
    Stream a completion response.

    Args:
        request: StreamingCompletionRequest with prompt and parameters.

    Returns:
        StreamingResponse with Server-Sent Events (SSE) format.

    Usage in Streamlit:
        >>> import requests
        >>> response = requests.post(
        ...     "http://localhost:8000/stream",
        ...     json={"prompt": "Tell me a story"},
        ...     stream=True
        ... )
        >>> for line in response.iter_lines():
        ...     if line:
        ...         chunk = json.loads(line)
        ...         print(chunk["text"], end="", flush=True)
    """
    router = get_router()

    async def generate() -> AsyncGenerator[str, None]:
        """Generate streaming chunks."""
        try:
            total_tokens = 0
            provider_used = None
            stop_reason = None

            for chunk in router.complete_stream(
                prompt=request.prompt,
                system=request.system,
                max_tokens=request.max_tokens,
            ):
                # chunk is typically a dict with 'text', 'provider', 'tokens_used', etc.
                if isinstance(chunk, dict):
                    text = chunk.get("text", "")
                    provider_used = chunk.get("provider", provider_used)
                    tokens = chunk.get("tokens_used", 0)
                    total_tokens += tokens
                    stop_reason = chunk.get("stop_reason")
                else:
                    text = str(chunk)

                stream_chunk = StreamChunk(
                    text=text,
                    provider=provider_used or "unknown",
                    is_final=False,
                )
                yield stream_chunk.model_dump_json() + "\n"

            # Send final chunk with metadata
            final_chunk = StreamChunk(
                text="",
                provider=provider_used or "unknown",
                is_final=True,
                total_tokens=total_tokens,
                stop_reason=stop_reason,
            )
            yield final_chunk.model_dump_json() + "\n"

        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            error_chunk = {
                "error": "streaming_failed",
                "message": str(e),
            }
            yield (b"data: " + str(error_chunk).encode() + b"\n\n")

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
    )


# ── Book Generation Endpoint ────────────────────────────────────


@app.post("/book", response_model=BookResponse, tags=["Generation"])
async def generate_book(request: BookRequest) -> BookResponse:
    """
    Generate a complete book chapter by chapter.

    Args:
        request: BookRequest with title, chapter count, etc.

    Returns:
        BookResponse with generation statistics.

    Features:
        - Automatic chapter generation with retry logic
        - Progress tracking with token counting
        - Multi-provider fallback support
        - Checkpointing (each chapter saved immediately)
    """
    router = get_router()

    try:
        from pathlib import Path

        title = request.title
        num_chapters = request.chapters
        chapter_length = request.chapter_length

        # Create output file
        output_file = f"{title.lower().replace(' ', '_')}.md"
        output_path = Path(output_file)

        # Write header
        output_path.write_text(f"# {title}\n\n", encoding="utf-8")

        total_tokens = 0
        chapters_generated = 0
        providers_used = set()

        for chapter_num in range(1, num_chapters + 1):
            # Generate chapter prompt
            prompt = f"Write Chapter {chapter_num} of the book '{title}'. Each chapter should be approximately {chapter_length} words."
            if request.style:
                prompt += f" Style: {request.style}"

            # Try to generate chapter with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = router.complete(
                        prompt=prompt,
                        max_tokens=chapter_length * 2,  # Estimate tokens
                    )

                    chapter_text = response.get("text", "")
                    provider = response.get("provider", "unknown")
                    tokens = response.get("tokens_used", 0)

                    total_tokens += tokens
                    providers_used.add(provider)

                    # Append to file
                    with open(output_path, "a", encoding="utf-8") as f:
                        f.write(f"## Chapter {chapter_num}\n\n{chapter_text}\n\n")

                    chapters_generated += 1
                    break

                except Exception as e:
                    logger.warning(
                        f"Chapter {chapter_num} attempt {attempt + 1} failed: {e}"
                    )
                    if attempt == max_retries - 1:
                        logger.error(
                            f"Failed to generate chapter {chapter_num} after {max_retries} attempts"
                        )

        total_words = sum(
            len(line.split())
            for line in output_path.read_text(encoding="utf-8").split("\n")
        )

        return BookResponse(
            title=title,
            chapters_generated=chapters_generated,
            total_chapters=num_chapters,
            total_words=total_words,
            tokens_used=total_tokens,
            providers_used=list(providers_used),
            filename=str(output_path),
            status="completed" if chapters_generated == num_chapters else "partial",
        )

    except Exception as e:
        logger.error(f"Book generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "book_generation_failed",
                "message": str(e),
            },
        ) from e


# ── Utility Endpoints ───────────────────────────────────────────


@app.post("/reset", response_model=ResetResponse, tags=["Testing"])
async def reset_quotas(
    reset_all: bool = Query(
        False, description="Reset all providers or only exhausted ones"
    ),
) -> ResetResponse:
    """
    Reset quota counters (for testing).

    Args:
        reset_all: If True, reset all providers. If False, only reset exhausted ones.

    Returns:
        ResetResponse with confirmation and count of reset providers.

    Warning:
        This endpoint is for testing. Disable in production by removing this route.
    """
    router = get_router()

    reset_count = 0
    for provider in router.providers:
        quota = router.storage.get_quota(provider.name)
        if reset_all or quota.is_exhausted:
            router.storage.reset_quota(provider.name)
            reset_count += 1

    return ResetResponse(
        message=f"Reset {reset_count} provider quotas",
        providers_reset=reset_count,
        timestamp=datetime.utcnow().isoformat(),
    )


# ── Error Handlers ──────────────────────────────────────────────


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    error_detail = {
        "error": exc.detail.get("error", "http_error")
        if isinstance(exc.detail, dict)
        else "http_error",
        "message": exc.detail.get("message", str(exc.detail))
        if isinstance(exc.detail, dict)
        else str(exc.detail),
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=error_detail,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred",
            "details": str(exc),
        },
    )


# ── Root Endpoint ──────────────────────────────────────────────


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """
    API root endpoint.

    Returns information about the API and links to documentation.
    """
    return {
        "name": "QuotaRouter API",
        "version": "0.8.0",
        "description": "Quota-aware LLM routing engine with multi-provider fallback",
        "docs": "/docs",
        "health": "/health",
        "status": "/status",
    }


# Module exports
__all__ = ["app", "get_router"]
