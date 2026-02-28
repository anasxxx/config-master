# -*- coding: utf-8 -*-
import json
import copy
from pathlib import Path

import agents.conversation_agent as ca
from agents.conversation_agent import extract_then_merge_user_text

BASE_DIR = Path(__file__).parent
TEMPLATE_FILE = BASE_DIR / "configmaster_required_fields.json"


def load_template(path: Path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def get_by_path(obj, path: str):
    cur = obj
    for part in path.split("."):
        if part.isdigit():
            idx = int(part)
            if not isinstance(cur, list) or idx >= len(cur):
                return None
            cur = cur[idx]
        else:
            if not isinstance(cur, dict) or part not in cur:
                return None
            cur = cur[part]
    return cur


def run_case(name: str, text: str, expects: dict):
    template = load_template(TEMPLATE_FILE)
    state = {"facts": copy.deepcopy(template), "provenance": {}, "meta": {}, "history": [], "done": False}

    # Force regex-first for deterministic tests.
    ca.USE_LLM = False

    extract_then_merge_user_text(state, template, text)

    for path, exp in expects.items():
        got = get_by_path(state["facts"], path)
        if isinstance(exp, list):
            if not isinstance(got, list) or any(x not in got for x in exp):
                raise AssertionError(f"{name} failed: {path} -> {got} expected contains {exp}")
        else:
            if got != exp:
                raise AssertionError(f"{name} failed: {path} -> {got} expected {exp}")

    print(f"OK: {name}")


def main():
    cases = [
        (
            "Orion correction + multi",
            "Créer une banque appelée Orion Pay Bank (non… mets plutôt Orion Payments Bank) au Maroc, bank code 55660. agence principale: Casablanca Anfa, code agence 0011 (ville Casablanca). Active Visa + Mastercard : cartes debit et prepaid en PVC. Services: 3DS, SMS, tokenization. Limites: national et international retrait 5000, paiement 20000, e-commerce 12000. Fees: registration 50, periodic 10/mois, replacement 30.",
            {
                "bank.name": "ORION PAYMENTS BANK",
                "bank.agencies.0.agency_name": "CASABLANCA ANFA",
                "bank.agencies.0.agency_code": "0011",
                "cards.0.card_info.plastic_type": "PVC",
                "cards.0.services.enabled": ["3DS", "SMS", "TOKENIZATION"],
            },
        ),
        (
            "International only",
            "Transactions international uniquement, limite paiement 25000 EUR/jour et retrait 7000 EUR/jour.",
            {
                "cards.0.limits.by_type.DEFAULT.international.daily_amount": 25000.0,
            },
        ),
        (
            "National only",
            "Transactions national uniquement, limite paiement 12000 MAD/jour.",
            {
                "cards.0.limits.by_type.DEFAULT.domestic.daily_amount": 12000.0,
            },
        ),
        (
            "Single network",
            "Active Visa credit en PVC avec 3DS.",
            {
                "cards.0.card_info.network": "VISA",
                "cards.0.card_info.product_type": "CREDIT",
            },
        ),
        (
            "Single product",
            "cartes prepaid en PVC",
            {
                "cards.0.card_info.product_type": "PREPAID",
            },
        ),
        (
            "Agency code",
            "Agence Casablanca Anfa, code agence 0105.",
            {
                "bank.agencies.0.agency_code": "0105",
            },
        ),
    ]

    for name, text, expects in cases:
        run_case(name, text, expects)


if __name__ == "__main__":
    main()
