"""
Quota storage and persistence layer.

Handles loading and saving quota data from/to disk.
Implements Single Responsibility Principle - only handles storage.
"""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path
from typing import Dict

from ..core.types import QuotaStorage

logger = logging.getLogger(__name__)


class JSONQuotaStorage(QuotaStorage):
    """
    File-based quota storage using JSON.

    Stores quota state in a JSON file at ~/.freerouter_quotas.json
    with daily reset logic.
    """

    def __init__(self, storage_path: Path = None):
        """
        Initialize storage.

        Args:
            storage_path: Path to quota file. Defaults to ~/.freerouter_quotas.json
        """
        self.path = storage_path or Path.home() / ".freerouter_quotas.json"

    def load_quotas(self) -> Dict[str, int]:
        """
        Load quotas from disk.

        Returns dict {provider_id: tokens_used_today}.
        Automatically resets quotas if date has changed.
        """
        if not self.path.exists():
            return {}

        try:
            data = json.loads(self.path.read_text())
            today = str(date.today())

            # Reset quotas from previous days
            if data.get("date") != today:
                logger.info("New day - resetting quotas")
                return {}

            return data.get("providers", {})

        except Exception as e:
            logger.error(f"Error loading quotas: {e}")
            return {}

    def save_quotas(self, quotas: Dict[str, int]) -> None:
        """
        Save quotas to disk.

        Args:
            quotas: Dict of {provider_id: tokens_used_today}
        """
        try:
            data = {
                "date": str(date.today()),
                "providers": quotas,
            }
            self.path.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Error saving quotas: {e}")


class InMemoryQuotaStorage(QuotaStorage):
    """
    In-memory quota storage for testing.

    Useful for unit tests and demos where persistence isn't needed.
    """

    def __init__(self):
        self._quotas: Dict[str, int] = {}

    def load_quotas(self) -> Dict[str, int]:
        """Return current in-memory quotas."""
        return self._quotas.copy()

    def save_quotas(self, quotas: Dict[str, int]) -> None:
        """Update in-memory quotas."""
        self._quotas = quotas.copy()
