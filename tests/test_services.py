"""Unit tests for the banking services layer."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from banking_app.models import Institution
from banking_app.services import BankingManager
from banking_app.storage import BankingDataStore


def test_institution_and_card_management(tmp_path: Path) -> None:
    store = BankingDataStore(tmp_path / "data.json")
    manager = BankingManager(store)

    institution = Institution(name="Chase", website="https://www.chase.com")
    manager.add_institution(institution)

    institutions = manager.list_institutions()
    assert len(institutions) == 1
    assert institutions[0].name == "Chase"

    card = manager.add_card(
        institution_name="Chase",
        name="Freedom Unlimited",
        card_type="credit",
        credit_limit=5000,
        balance=1250,
        interest_rate=19.99,
        annual_fee=0,
        rewards="1.5% cashback",
        tags=["personal", "cashback"],
    )

    cards = manager.list_cards()
    assert len(cards) == 1
    assert cards[0].id == card.id
    assert cards[0].institution == "Chase"

    # Utilisation should be balance / limit
    assert manager.credit_utilisation() == card.balance / card.credit_limit


def test_credit_score_management(tmp_path: Path) -> None:
    store = BankingDataStore(tmp_path / "data.json")
    manager = BankingManager(store)

    timestamp = datetime(2023, 5, 1, 12, 0, 0, tzinfo=UTC)
    manager.update_credit_score(
        provider="Experian", score=720, last_updated=timestamp, notes="Solid score"
    )

    scores = manager.list_credit_scores()
    assert len(scores) == 1
    assert scores[0].provider == "Experian"
    assert scores[0].score == 720
    assert scores[0].last_updated == timestamp

    # Updating the same provider should replace the existing entry
    new_timestamp = datetime(2023, 6, 1, 8, 30, 0, tzinfo=UTC)
    manager.update_credit_score(
        provider="Experian", score=735, last_updated=new_timestamp
    )

    scores = manager.list_credit_scores()
    assert len(scores) == 1
    assert scores[0].score == 735
    assert scores[0].last_updated == new_timestamp


def test_summary_report(tmp_path: Path) -> None:
    store = BankingDataStore(tmp_path / "data.json")
    manager = BankingManager(store)

    manager.add_institution(Institution(name="Bank A"))
    manager.add_institution(Institution(name="Bank B"))

    manager.add_card(
        institution_name="Bank A",
        name="Bank A Credit",
        card_type="credit",
        credit_limit=4000,
        balance=1000,
    )
    manager.add_card(
        institution_name="Bank B",
        name="Bank B Credit",
        card_type="credit",
        credit_limit=6000,
        balance=500,
    )

    manager.update_credit_score(provider="Experian", score=700)
    manager.update_credit_score(provider="Equifax", score=710)

    summary = manager.summary()

    assert summary["total_institutions"] == 2
    assert summary["total_cards"] == 2
    assert summary["highest_credit_score"] == 710
    assert summary["lowest_credit_score"] == 700
    assert summary["average_credit_score"] == 705

    # Total utilisation should be (1000 + 500) / (4000 + 6000)
    assert summary["credit_utilisation"] == (1500 / 10000)

    credit_score_providers = {item["provider"] for item in summary["credit_scores"]}
    assert credit_score_providers == {"Experian", "Equifax"}
