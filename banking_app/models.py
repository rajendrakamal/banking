"""Data models for the banking application."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import UTC, datetime
from typing import Dict, List, Optional


@dataclass
class Institution:
    """Represents a banking institution that issues payment cards."""

    name: str
    website: Optional[str] = None
    support_phone: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Return a serialisable representation of the institution."""

        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Optional[str]]) -> "Institution":
        """Create an :class:`Institution` instance from raw data."""

        return cls(
            name=data.get("name", ""),
            website=data.get("website"),
            support_phone=data.get("support_phone"),
            notes=data.get("notes"),
        )


@dataclass
class Card:
    """Represents a payment card that belongs to a user."""

    id: str
    institution: str
    name: str
    card_type: str
    credit_limit: float
    balance: float = 0.0
    interest_rate: Optional[float] = None
    annual_fee: Optional[float] = None
    rewards: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        """Return a serialisable representation of the card."""

        data = asdict(self)
        data["tags"] = list(self.tags)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Card":
        """Create a :class:`Card` instance from raw data."""

        return cls(
            id=str(data.get("id")),
            institution=str(data.get("institution", "")),
            name=str(data.get("name", "")),
            card_type=str(data.get("card_type", "")),
            credit_limit=float(data.get("credit_limit", 0.0)),
            balance=float(data.get("balance", 0.0)),
            interest_rate=data.get("interest_rate"),
            annual_fee=data.get("annual_fee"),
            rewards=data.get("rewards"),
            notes=data.get("notes"),
            tags=list(data.get("tags", [])),
        )

    @property
    def utilisation(self) -> float:
        """Return the card's utilisation ratio as a float between 0 and 1."""

        if self.credit_limit == 0:
            return 0.0
        return max(0.0, min(1.0, self.balance / self.credit_limit))


@dataclass
class CreditScore:
    """Represents a credit score provided by a scoring bureau."""

    provider: str
    score: int
    last_updated: datetime
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        """Return a serialisable representation of the credit score."""

        data = {
            "provider": self.provider,
            "score": self.score,
            "last_updated": self.last_updated.isoformat(),
            "notes": self.notes,
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "CreditScore":
        """Create a :class:`CreditScore` instance from raw data."""

        last_updated_raw = data.get("last_updated")
        if isinstance(last_updated_raw, datetime):
            last_updated = last_updated_raw
        elif last_updated_raw:
            last_updated = datetime.fromisoformat(str(last_updated_raw))
        else:
            last_updated = datetime.now(UTC)
        return cls(
            provider=str(data.get("provider", "")),
            score=int(data.get("score", 0)),
            last_updated=last_updated,
            notes=data.get("notes"),
        )
