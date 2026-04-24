"""MCP Server for Qwen Code integration."""

import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Optional

from quotarouter.config.qwen_config import QwenConfig, QwenProvider
from quotarouter.core.router import FreeRouter

logger = logging.getLogger(__name__)


class QwenCodeMCPServer:
    """MCP server for Qwen Code with QuotaRouter integration."""

    def __init__(self, router: Optional[FreeRouter] = None):
        """Initialize Qwen Code MCP server.

        Args:
            router: FreeRouter instance for quota management
        """
        self.router = router
        self.config = QwenConfig()
        self.config.load_from_file()
        self.current_provider: Optional[QwenProvider] = None

    def _get_headers(self, provider: QwenProvider) -> dict[str, str]:
        """Build headers for API request."""
        headers = {"Content-Type": "application/json"}
        api_key = self.config.get_api_key(provider)

        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        return headers

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: str = "You are a helpful assistant.",
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Get completion from Qwen Code.

        Args:
            prompt: User prompt
            model: Model name (uses default if not specified)
            system: System prompt
            max_tokens: Maximum tokens in response

        Returns:
            Completion response
        """
        provider = self._get_provider(model)
        if not provider:
            return {"error": "No provider configured"}

        # If we have a router, use it for quota checking
        if self.router:
            return await self._complete_with_router(
                prompt, provider, system, max_tokens
            )

        # Otherwise, direct call
        return await self._direct_complete(prompt, provider, system, max_tokens)

    async def _complete_with_router(
        self,
        prompt: str,
        provider: QwenProvider,
        system: str,
        max_tokens: int,
    ) -> dict[str, Any]:
        """Complete using QuotaRouter for quota management."""
        try:
            # Use router's complete method (synchronous, wrapped in thread)
            result = await asyncio.to_thread(
                self.router.complete,
                prompt=prompt,
                system=system,
                max_tokens=max_tokens,
            )

            return {
                "text": result.get("text", ""),
                "provider": result.get("provider", provider.name),
                "model": provider.id,
                "tokens_used": result.get("tokens_used", 0),
                "stop_reason": result.get("stop_reason"),
            }
        except Exception as e:
            logger.error(f"Router completion error: {e}")
            return {"error": str(e)}

    async def _direct_complete(
        self,
        prompt: str,
        provider: QwenProvider,
        system: str,
        max_tokens: int,
    ) -> dict[str, Any]:
        """Direct completion without router."""
        if not provider.base_url:
            return {"error": f"No base_url configured for {provider.id}"}

        api_key = self.config.get_api_key(provider)
        if not api_key:
            return {"error": f"No API key for {provider.id}"}

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{provider.base_url}/chat/completions",
                    headers=self._get_headers(provider),
                    json={
                        "model": provider.id,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                        "max_tokens": max_tokens,
                    },
                    timeout=60.0,
                )

                response.raise_for_status()
                data = response.json()

                return {
                    "text": data["choices"][0]["message"]["content"],
                    "provider": provider.name,
                    "model": provider.id,
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                    "stop_reason": data["choices"][0].get("finish_reason"),
                }
        except Exception as e:
            logger.error(f"Direct completion error: {e}")
            return {"error": str(e)}

    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: str = "You are a helpful assistant.",
        max_tokens: int = 4096,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream completion from Qwen Code.

        Args:
            prompt: User prompt
            model: Model name
            system: System prompt
            max_tokens: Maximum tokens

        Yields:
            Streaming chunks
        """
        provider = self._get_provider(model)
        if not provider:
            yield {"error": "No provider configured"}
            return

        # If we have a router, use it
        if self.router:
            async for chunk in self._stream_with_router(
                prompt, provider, system, max_tokens
            ):
                yield chunk
        else:
            async for chunk in self._direct_stream(
                prompt, provider, system, max_tokens
            ):
                yield chunk

    async def _stream_with_router(
        self,
        prompt: str,
        provider: QwenProvider,
        system: str,
        max_tokens: int,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream using QuotaRouter."""
        try:
            # Run router's stream in thread (it's synchronous, yields strings)
            def _stream():
                for chunk in self.router.complete_stream(
                    prompt=prompt,
                    system=system,
                    max_tokens=max_tokens,
                ):
                    if isinstance(chunk, dict):
                        yield chunk
                    else:
                        yield {"text": str(chunk)}

            for item in _stream():
                yield {
                    "text": item.get("text", ""),
                    "provider": provider.name,
                    "model": provider.id,
                    "is_final": False,
                }

            # Send final chunk
            yield {"text": "", "is_final": True}

        except Exception as e:
            logger.error(f"Router stream error: {e}")
            yield {"error": str(e)}

    async def _direct_stream(
        self,
        prompt: str,
        provider: QwenProvider,
        system: str,
        max_tokens: int,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Direct streaming without router."""
        if not provider.base_url:
            yield {"error": f"No base_url configured for {provider.id}"}
            return

        api_key = self.config.get_api_key(provider)
        if not api_key:
            yield {"error": f"No API key for {provider.id}"}
            return

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{provider.base_url}/chat/completions",
                    headers=self._get_headers(provider),
                    json={
                        "model": provider.id,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                        "max_tokens": max_tokens,
                        "stream": True,
                    },
                    timeout=60.0,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break

                            try:
                                data = json.loads(data_str)
                                chunk = data["choices"][0].get("delta", {})
                                if "content" in chunk:
                                    yield {
                                        "text": chunk["content"],
                                        "provider": provider.name,
                                        "model": provider.id,
                                        "is_final": False,
                                    }
                            except json.JSONDecodeError:
                                pass

            yield {"text": "", "is_final": True}

        except Exception as e:
            logger.error(f"Direct stream error: {e}")
            yield {"error": str(e)}

    def _get_provider(self, model: Optional[str] = None) -> Optional[QwenProvider]:
        """Get provider by model name or use default."""
        if model:
            return self.config.get_provider(model)

        if self.current_provider:
            return self.current_provider

        if self.config.default_provider:
            return self.config.get_provider(self.config.default_provider)

        providers = self.config.list_providers()
        if providers:
            return self.config.get_provider(providers[0])

        return None

    def set_provider(self, provider_id: str) -> bool:
        """Set current provider."""
        provider = self.config.get_provider(provider_id)
        if provider:
            self.current_provider = provider
            return True
        return False

    def get_available_providers(self) -> list[dict[str, str]]:
        """Get list of available providers."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "protocol": p.protocol,
                "description": p.description,
            }
            for p in self.config.providers.values()
        ]

    def get_provider_info(self, provider_id: str) -> Optional[dict[str, Any]]:
        """Get detailed provider info."""
        provider = self.config.get_provider(provider_id)
        if not provider:
            return None

        return {
            "id": provider.id,
            "name": provider.name,
            "protocol": provider.protocol,
            "base_url": provider.base_url,
            "description": provider.description,
            "has_api_key": bool(self.config.get_api_key(provider)),
        }
