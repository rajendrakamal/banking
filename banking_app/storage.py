"""Persistent storage helper for the banking application."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_DATA = {
    "institutions": [],
    "cards": [],
    "credit_scores": [],
}


class BankingDataStore:
    """Simple JSON file backed storage for the banking data."""

    def __init__(self, path: os.PathLike[str] | str) -> None:
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.save(DEFAULT_DATA)

    def load(self) -> Dict[str, Any]:
        """Load the banking data from disk."""

        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save(self, data: Dict[str, Any]) -> None:
        """Persist the given banking data to disk."""

        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")

    def reset(self) -> None:
        """Reset the datastore to its default state."""

        self.save(DEFAULT_DATA)
