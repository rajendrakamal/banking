"""Core services for managing banking data."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Optional
from uuid import uuid4

from .models import Card, CreditScore, Institution
from .storage import BankingDataStore


class BankingManager:
    """High level API for working with the banking data store."""

    def __init__(self, store: BankingDataStore) -> None:
        self.store = store

    # ------------------------------------------------------------------
    # Institution management
    # ------------------------------------------------------------------
    def list_institutions(self) -> List[Institution]:
        data = self.store.load()
        return [Institution.from_dict(raw) for raw in data.get("institutions", [])]

    def add_institution(self, institution: Institution) -> Institution:
        data = self.store.load()
        existing = [inst for inst in data.get("institutions", []) if inst["name"].lower() == institution.name.lower()]
        if existing:
            raise ValueError(f"Institution '{institution.name}' already exists")
        data.setdefault("institutions", []).append(institution.to_dict())
        self.store.save(data)
        return institution

    # ------------------------------------------------------------------
    # Card management
    # ------------------------------------------------------------------
    def list_cards(self, institution_name: Optional[str] = None) -> List[Card]:
        data = self.store.load()
        cards = [Card.from_dict(raw) for raw in data.get("cards", [])]
        if institution_name:
            cards = [card for card in cards if card.institution.lower() == institution_name.lower()]
        return cards

    def add_card(
        self,
        *,
        institution_name: str,
        name: str,
        card_type: str,
        credit_limit: float,
        balance: float = 0.0,
        interest_rate: Optional[float] = None,
        annual_fee: Optional[float] = None,
        rewards: Optional[str] = None,
        notes: Optional[str] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> Card:
        data = self.store.load()
        institutions = data.get("institutions", [])
        if not any(inst["name"].lower() == institution_name.lower() for inst in institutions):
            raise ValueError(
                f"Institution '{institution_name}' does not exist. "
                "Create it before adding cards."
            )

        card = Card(
            id=str(uuid4()),
            institution=institution_name,
            name=name,
            card_type=card_type,
            credit_limit=float(credit_limit),
            balance=float(balance),
            interest_rate=float(interest_rate) if interest_rate is not None else None,
            annual_fee=float(annual_fee) if annual_fee is not None else None,
            rewards=rewards,
            notes=notes,
            tags=list(tags or []),
        )
        data.setdefault("cards", []).append(card.to_dict())
        self.store.save(data)
        return card

    # ------------------------------------------------------------------
    # Credit score management
    # ------------------------------------------------------------------
    def list_credit_scores(self) -> List[CreditScore]:
        data = self.store.load()
        return [CreditScore.from_dict(raw) for raw in data.get("credit_scores", [])]

    def update_credit_score(
        self,
        *,
        provider: str,
        score: int,
        last_updated: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> CreditScore:
        data = self.store.load()
        credit_scores = data.setdefault("credit_scores", [])
        existing_idx = next((i for i, raw in enumerate(credit_scores) if raw["provider"].lower() == provider.lower()), None)
        score_obj = CreditScore(
            provider=provider,
            score=int(score),
            last_updated=last_updated or datetime.now(UTC),
            notes=notes,
        )
        if existing_idx is not None:
            credit_scores[existing_idx] = score_obj.to_dict()
        else:
            credit_scores.append(score_obj.to_dict())
        self.store.save(data)
        return score_obj

    # ------------------------------------------------------------------
    # High level summaries
    # ------------------------------------------------------------------
    def credit_utilisation(self) -> float:
        cards = self.list_cards()
        limits = [card.credit_limit for card in cards if card.credit_limit > 0]
        balances = [card.balance for card in cards]
        if not limits:
            return 0.0
        total_limit = sum(limits)
        total_balance = sum(balances)
        return min(1.0, max(0.0, total_balance / total_limit))

    def summary(self) -> Dict[str, object]:
        data = self.store.load()
        institutions = [Institution.from_dict(raw) for raw in data.get("institutions", [])]
        cards = [Card.from_dict(raw) for raw in data.get("cards", [])]
        credit_scores = [CreditScore.from_dict(raw) for raw in data.get("credit_scores", [])]

        score_values = [score.score for score in credit_scores]
        summary_data: Dict[str, object] = {
            "total_institutions": len(institutions),
            "total_cards": len(cards),
            "credit_utilisation": self.credit_utilisation(),
            "credit_scores": [score.to_dict() for score in credit_scores],
            "highest_credit_score": max(score_values) if score_values else None,
            "lowest_credit_score": min(score_values) if score_values else None,
            "average_credit_score": mean(score_values) if score_values else None,
        }
        return summary_data

    def reset(self) -> None:
        """Reset the underlying data store to its default state."""

        self.store.reset()


def default_data_path() -> str:
    """Return the default path used for storing the application data."""

    base_dir = Path.home() / ".banking_app"
    base_dir.mkdir(parents=True, exist_ok=True)
    return str(base_dir / "data.json")
