"""Command line interface for the banking application."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from typing import Iterable, Optional

from .models import Institution
from .services import BankingManager, default_data_path
from .storage import BankingDataStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="banking-app",
        description=(
            "Manage banking institutions, cards and credit scores from a single "
            "command line tool."
        ),
    )
    parser.add_argument(
        "--storage",
        default=None,
        help=(
            "Path to the JSON file used for storing data. Defaults to "
            "~/.banking_app/data.json"
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Initialise or reset the data store")

    institution_parser = subparsers.add_parser(
        "add-institution", help="Add a new banking institution"
    )
    institution_parser.add_argument("name", help="Name of the institution")
    institution_parser.add_argument("--website", help="Website for the institution")
    institution_parser.add_argument(
        "--support-phone", help="Support phone number for the institution"
    )
    institution_parser.add_argument("--notes", help="Free form notes")

    subparsers.add_parser("list-institutions", help="List all institutions")

    card_parser = subparsers.add_parser("add-card", help="Add a payment card")
    card_parser.add_argument("name", help="Friendly name of the card")
    card_parser.add_argument(
        "--institution",
        required=True,
        help="Institution issuing the card (must exist)",
    )
    card_parser.add_argument(
        "--card-type",
        required=True,
        help="Card type (e.g. credit, debit, charge)",
    )
    card_parser.add_argument(
        "--credit-limit",
        type=float,
        default=0.0,
        help="Credit limit for the card",
    )
    card_parser.add_argument(
        "--balance",
        type=float,
        default=0.0,
        help="Current balance on the card",
    )
    card_parser.add_argument(
        "--interest-rate",
        type=float,
        help="Interest rate percentage (APR)",
    )
    card_parser.add_argument(
        "--annual-fee",
        type=float,
        help="Annual fee charged for the card",
    )
    card_parser.add_argument("--rewards", help="Rewards description")
    card_parser.add_argument("--notes", help="Free form notes")
    card_parser.add_argument(
        "--tag",
        dest="tags",
        action="append",
        default=None,
        help="Tag to associate with the card (can be passed multiple times)",
    )

    list_cards_parser = subparsers.add_parser("list-cards", help="List stored cards")
    list_cards_parser.add_argument(
        "--institution",
        help="Only show cards from the given institution",
    )

    credit_score_parser = subparsers.add_parser(
        "update-credit-score", help="Add or update a credit score"
    )
    credit_score_parser.add_argument("provider", help="Credit bureau or provider")
    credit_score_parser.add_argument("score", type=int, help="Score value")
    credit_score_parser.add_argument(
        "--notes", help="Optional notes about the credit score"
    )
    credit_score_parser.add_argument(
        "--date",
        help="ISO formatted date for when the score was last updated",
    )

    subparsers.add_parser("list-credit-scores", help="List stored credit scores")
    subparsers.add_parser(
        "summary",
        help="Display an overview of institutions, cards and credit scores",
    )

    return parser


def _resolve_storage(path: Optional[str]) -> str:
    return path or default_data_path()


def _format_date(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    return datetime.fromisoformat(raw)


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    storage_path = _resolve_storage(args.storage)
    store = BankingDataStore(storage_path)
    manager = BankingManager(store)

    if args.command == "init":
        manager.reset()
        print(f"Initialised data store at {storage_path}")
        return

    if args.command == "add-institution":
        institution = Institution(
            name=args.name,
            website=args.website,
            support_phone=args.support_phone,
            notes=args.notes,
        )
        manager.add_institution(institution)
        print(f"Added institution: {institution.name}")
        return

    if args.command == "list-institutions":
        institutions = manager.list_institutions()
        if not institutions:
            print("No institutions stored.")
            return
        for inst in institutions:
            description = inst.name
            extras = [value for value in [inst.website, inst.support_phone] if value]
            if extras:
                description += f" ({', '.join(extras)})"
            if inst.notes:
                description += f"\n  Notes: {inst.notes}"
            print(f"- {description}")
        return

    if args.command == "add-card":
        card = manager.add_card(
            institution_name=args.institution,
            name=args.name,
            card_type=args.card_type,
            credit_limit=args.credit_limit,
            balance=args.balance,
            interest_rate=args.interest_rate,
            annual_fee=args.annual_fee,
            rewards=args.rewards,
            notes=args.notes,
            tags=args.tags,
        )
        print(f"Added card '{card.name}' for {card.institution} with id {card.id}")
        return

    if args.command == "list-cards":
        cards = manager.list_cards(args.institution)
        if not cards:
            print("No cards stored.")
            return
        for card in cards:
            description = (
                f"- {card.name} [{card.card_type}] from {card.institution}\n"
                f"  Limit: {card.credit_limit:.2f} Balance: {card.balance:.2f}"
            )
            if card.interest_rate is not None:
                description += f" APR: {card.interest_rate:.2f}%"
            if card.annual_fee is not None:
                description += f" Annual fee: {card.annual_fee:.2f}"
            if card.rewards:
                description += f"\n  Rewards: {card.rewards}"
            if card.tags:
                description += f"\n  Tags: {', '.join(card.tags)}"
            if card.notes:
                description += f"\n  Notes: {card.notes}"
            print(description)
        return

    if args.command == "update-credit-score":
        score = manager.update_credit_score(
            provider=args.provider,
            score=args.score,
            last_updated=_format_date(args.date),
            notes=args.notes,
        )
        print(
            "Stored credit score for {provider}: {score}".format(
                provider=score.provider,
                score=score.score,
            )
        )
        return

    if args.command == "list-credit-scores":
        scores = manager.list_credit_scores()
        if not scores:
            print("No credit scores stored.")
            return
        for score in scores:
            description = (
                f"- {score.provider}: {score.score} (updated {score.last_updated.date()})"
            )
            if score.notes:
                description += f"\n  Notes: {score.notes}"
            print(description)
        return

    if args.command == "summary":
        summary = manager.summary()
        print(json.dumps(summary, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":  # pragma: no cover - entrypoint
    main()
