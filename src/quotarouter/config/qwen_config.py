"""Qwen Code integration configuration."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class QwenProvider(BaseModel):
    """Qwen provider configuration."""

    id: str = Field(..., description="Model ID")
    name: str = Field(..., description="Provider name")
    protocol: str = Field(
        default="openai", description="API protocol (openai, anthropic, gemini)"
    )
    base_url: Optional[str] = Field(None, description="API base URL")
    api_key: Optional[str] = Field(None, description="API key")
    env_key: Optional[str] = Field(
        None, description="Environment variable name for API key"
    )
    description: str = Field(default="", description="Provider description")


class QwenConfig(BaseModel):
    """Qwen Code configuration manager."""

    providers: Dict[str, QwenProvider] = Field(default_factory=dict)
    default_provider: Optional[str] = Field(None, description="Default provider ID")
    default_model: Optional[str] = Field(None, description="Default model name")
    settings_path: Path = Field(
        default_factory=lambda: Path.home() / ".qwen" / "settings.json"
    )

    class Config:
        arbitrary_types_allowed = True

    def load_from_file(self) -> bool:
        """Load configuration from ~/.qwen/settings.json."""
        if not self.settings_path.exists():
            return False

        try:
            with open(self.settings_path) as f:
                data = json.load(f)

            # Parse model providers
            if "modelProviders" in data:
                for protocol, providers_list in data["modelProviders"].items():
                    for provider_data in providers_list:
                        provider_data["protocol"] = protocol
                        provider = QwenProvider(**provider_data)
                        self.providers[provider.id] = provider

            # Set default provider
            if "security" in data and "auth" in data["security"]:
                self.default_provider = data["security"]["auth"].get("selectedType")

            # Set default model
            if "model" in data:
                self.default_model = data["model"].get("name")

            return True
        except Exception as e:
            print(f"Error loading Qwen config: {e}")
            return False

    def save_to_file(self) -> bool:
        """Save configuration to ~/.qwen/settings.json."""
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)

            # Build structure matching Qwen Code format
            data: Dict[str, Any] = {
                "modelProviders": {},
                "security": {
                    "auth": {"selectedType": self.default_provider or "openai"}
                },
                "model": {"name": self.default_model},
            }

            # Group providers by protocol
            for provider in self.providers.values():
                protocol = provider.protocol
                if protocol not in data["modelProviders"]:
                    data["modelProviders"][protocol] = []

                provider_dict = provider.model_dump(exclude={"protocol"})
                data["modelProviders"][protocol].append(provider_dict)

            with open(self.settings_path, "w") as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving Qwen config: {e}")
            return False

    def add_provider(self, provider: QwenProvider) -> None:
        """Add a provider to the configuration."""
        self.providers[provider.id] = provider

    def get_provider(self, provider_id: str) -> Optional[QwenProvider]:
        """Get a provider by ID."""
        return self.providers.get(provider_id)

    def get_api_key(self, provider: QwenProvider) -> Optional[str]:
        """Get API key from provider config or environment."""
        # First try explicit API key in config
        if provider.api_key:
            return provider.api_key

        # Then try environment variable
        if provider.env_key:
            return os.getenv(provider.env_key)

        return None

    def list_providers(self) -> list[str]:
        """List all available provider IDs."""
        return list(self.providers.keys())

    def list_by_protocol(self, protocol: str) -> list[QwenProvider]:
        """List providers by protocol."""
        return [p for p in self.providers.values() if p.protocol == protocol]
