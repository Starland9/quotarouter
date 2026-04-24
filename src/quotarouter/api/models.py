"""
Pydantic models for API requests and responses.

Defines request/response schemas for FastAPI endpoints,
ensuring type safety and automatic OpenAPI documentation.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ── Request Models ──────────────────────────────────────────────


class CompletionRequest(BaseModel):
    """Request model for single completion."""

    prompt: str = Field(..., min_length=1, description="The prompt to complete")
    system: Optional[str] = Field(
        "You are a helpful assistant.",
        description="System prompt",
    )
    temperature: float = Field(
        0.7, ge=0.0, le=2.0, description="Sampling temperature (0-2)"
    )
    max_tokens: Optional[int] = Field(
        None, ge=1, le=8000, description="Maximum tokens to generate"
    )
    top_p: float = Field(0.9, ge=0.0, le=1.0, description="Nucleus sampling parameter")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Explain quantum computing in simple terms",
                "system": "You are a helpful assistant.",
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 0.9,
            }
        }


class StreamingCompletionRequest(BaseModel):
    """Request model for streaming completion."""

    prompt: str = Field(..., min_length=1, description="The prompt to complete")
    system: Optional[str] = Field(
        "You are a helpful assistant.",
        description="System prompt",
    )
    temperature: float = Field(
        0.7, ge=0.0, le=2.0, description="Sampling temperature (0-2)"
    )
    max_tokens: Optional[int] = Field(
        None, ge=1, le=8000, description="Maximum tokens to generate"
    )
    top_p: float = Field(0.9, ge=0.0, le=1.0, description="Nucleus sampling parameter")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a short story about a robot",
                "system": "You are a helpful assistant.",
                "temperature": 0.8,
                "max_tokens": 1000,
            }
        }


class BookRequest(BaseModel):
    """Request model for book generation."""

    title: str = Field(..., min_length=1, description="Book title")
    chapters: int = Field(3, ge=1, le=50, description="Number of chapters to generate")
    chapter_length: int = Field(
        2000, ge=500, le=10000, description="Words per chapter (approximate)"
    )
    style: Optional[str] = Field(
        None,
        description="Writing style (e.g., 'technical', 'narrative', 'educational')",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "The Art of Python",
                "chapters": 5,
                "chapter_length": 2000,
                "style": "educational",
            }
        }


# ── Response Models ────────────────────────────────────────────


class CompletionResponse(BaseModel):
    """Response model for single completion."""

    text: str = Field(..., description="Generated completion text")
    provider: str = Field(..., description="Provider used for completion")
    tokens_used: int = Field(..., ge=0, description="Tokens consumed")
    stop_reason: Optional[str] = Field(
        None, description="Reason generation stopped (e.g., 'length', 'stop_sequence')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Quantum computing uses quantum bits (qubits)...",
                "provider": "openrouter",
                "tokens_used": 142,
                "stop_reason": "length",
            }
        }


class StreamChunk(BaseModel):
    """Single chunk in streaming response."""

    text: str = Field(..., description="Text chunk")
    provider: str = Field(..., description="Provider used")
    is_final: bool = Field(
        False, description="Whether this is the final chunk with metadata"
    )
    total_tokens: Optional[int] = Field(
        None, description="Total tokens if is_final=True"
    )
    stop_reason: Optional[str] = Field(None, description="Stop reason if is_final=True")


class ProviderStatus(BaseModel):
    """Status information for a single provider."""

    name: str = Field(..., description="Provider name (e.g., 'openrouter')")
    available: bool = Field(..., description="Whether provider is available")
    tokens_used: int = Field(..., description="Tokens used in current quota period")
    token_limit: Optional[int] = Field(
        None, description="Token limit (None if unlimited)"
    )
    requests_used: int = Field(..., description="Requests made in current period")
    request_limit: Optional[int] = Field(
        None, description="Request limit per minute (None if unlimited)"
    )
    quota_percentage: float = Field(
        0.0, ge=0.0, le=100.0, description="Percentage of quota used"
    )
    priority: int = Field(
        ..., description="Provider priority (lower = higher priority)"
    )


class StatusResponse(BaseModel):
    """Response model for /status endpoint."""

    providers: list[ProviderStatus] = Field(
        ..., description="List of provider statuses"
    )
    active_provider: str = Field(
        ..., description="Currently active provider (first available)"
    )
    total_tokens_used: int = Field(
        ..., description="Total tokens used across all providers"
    )
    total_requests: int = Field(..., description="Total requests routed")
    fallback_count: int = Field(
        ..., description="Number of times fallback to next provider occurred"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "providers": [
                    {
                        "name": "openrouter",
                        "available": True,
                        "tokens_used": 5000,
                        "token_limit": 100000,
                        "requests_used": 10,
                        "request_limit": 60,
                        "quota_percentage": 5.0,
                        "priority": 1,
                    }
                ],
                "active_provider": "openrouter",
                "total_tokens_used": 5000,
                "total_requests": 10,
                "fallback_count": 0,
            }
        }


class BookResponse(BaseModel):
    """Response model for book generation."""

    title: str = Field(..., description="Book title")
    chapters_generated: int = Field(
        ..., description="Number of chapters successfully generated"
    )
    total_chapters: int = Field(..., description="Total chapters requested")
    total_words: int = Field(..., description="Total words in generated book")
    tokens_used: int = Field(..., description="Total tokens consumed")
    providers_used: list[str] = Field(..., description="List of providers used")
    filename: Optional[str] = Field(
        None, description="Filename if saved (relative path)"
    )
    status: str = Field(
        ..., description="'completed' or 'partial' if some chapters failed"
    )


class ConfigResponse(BaseModel):
    """Response model for /config endpoint."""

    configured_providers: list[str] = Field(
        ..., description="List of configured provider names"
    )
    storage_backend: str = Field(
        ..., description="Quota storage backend (e.g., 'json')"
    )
    verbose_mode: bool = Field(..., description="Whether verbose logging is enabled")
    api_version: str = Field(..., description="API version")
    quotarouter_version: str = Field(..., description="QuotaRouter library version")


class ErrorResponse(BaseModel):
    """Response model for error responses."""

    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "quota_exhausted",
                "message": "All providers have exhausted their quota",
                "details": "Try again later",
            }
        }


class ResetResponse(BaseModel):
    """Response model for /reset endpoint."""

    message: str = Field(..., description="Confirmation message")
    providers_reset: int = Field(..., description="Number of providers reset")
    timestamp: str = Field(..., description="When reset occurred")
