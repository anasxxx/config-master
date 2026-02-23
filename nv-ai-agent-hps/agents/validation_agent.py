import json
from pathlib import Path
import re

# Validation Agent
#  Charge le template JSON (contrat)
#  Construit la liste des champs "à remplir"
#  Détecte les champs manquants
#  Génère des questions pour chaque champ


def load_template(template_path: Path) -> dict:
    if not template_path.exists():
        raise FileNotFoundError(
            f"Template introuvable: {template_path}\n"
            " Mets 'configmaster_required_fields.json' dans le même dossier que agent.py"
        )
    with open(template_path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _is_missing(v) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and v.strip() == "":
        return True
    if isinstance(v, list) and len(v) == 0:
        return True
    if isinstance(v, dict) and len(v) == 0:
        return True
    return False


def _iter_leaf_paths(template_obj, prefix=""):
    """
    Leaf paths:
    - dict: recurse
    - list:
        - if empty: list itself is required (user must provide items)
        - if has an element: use index 0 schema and recurse
    - primitive/None/str: leaf => required
    """
    if isinstance(template_obj, dict):
        for k, v in template_obj.items():
            p = f"{prefix}.{k}" if prefix else k
            yield from _iter_leaf_paths(v, p)
    elif isinstance(template_obj, list):
        if len(template_obj) == 0:
            # list itself required
            yield prefix
        else:
            p = f"{prefix}.0" if prefix else "0"
            yield from _iter_leaf_paths(template_obj[0], p)
    else:
        yield prefix


def build_required_paths(template_obj: dict) -> list:
    paths = [p.strip(".") for p in _iter_leaf_paths(template_obj) if p and p.strip(".")]
    return paths


def _get_by_path(obj, path: str):
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


def missing_paths(facts: dict, template_obj: dict, required_paths: list) -> list:
    missing = []
    for p in required_paths:
        v = _get_by_path(facts, p)
        if _is_missing(v):
            missing.append(p)
    return missing


CUSTOM_QUESTIONS = {
    # Bank
    "bank.name": "Quel est le nom de la banque ?",
    "bank.country": "Quel est le pays de la banque ? ",
    "bank.currency": "Quelle est la devise ? ",
    "bank.bank_code": "Quel est le code de la banque (bank code) ?",
    "bank.resources": "Quelles ressources veux-tu activer ? (ex: accounts, cards, transactions) Donne une liste séparée par virgules.",
    # First agency (index 0)
    "bank.agencies.0.agency_name": "Quel est le nom de l'agence ?",
    "bank.agencies.0.agency_code": "Quel est le code de cette agence ?",
    "bank.agencies.0.city": "Dans quelle ville se trouve cette agence ?",
    "bank.agencies.0.city_code": "Quel est le code de la ville ?",
    "bank.agencies.0.region": "Quelle est la région ?",
    "bank.agencies.0.region_code": "Quel est le code de la région ?",
    # Cards (index 0)
    "cards.0.card_info.bin": "Quel est le BIN de la carte ? (6 à 8 chiffres)",
    "cards.0.card_info.network": "Quel est le réseau de la carte ? (ex: VISA, MASTERCARD)",
    "cards.0.card_info.product": "Quel est le produit carte ? (ex: Classic, Gold...)",
    "cards.0.services.enabled": "Quels services veux-tu activer pour la carte ? (liste séparée par virgules) (ex: 3DS, TOKENIZATION)",
}


#  card_info 
CARD_INFO_QUESTIONS = {
    "cards.0.card_info.plastic_type": "Type de carte (plastique) (ex: PVC)",
    "cards.0.card_info.card_description": "Nom/description de la carte (ex: Carte Classic)",
    "cards.0.card_info.product_type": "Type de carte (ex: DEBIT ou CREDIT)",
    "cards.0.card_info.product_code": "Code du produit carte (ex: PRD001)",

    # ✅ Simplification des termes techniques
    "cards.0.card_info.pvk_index": "Paramètre sécurité PIN (PVK index). Si tu ne sais pas, mets 1",
    "cards.0.card_info.service_code": "Code service de la carte. Si tu ne sais pas, mets 101",

    "cards.0.card_info.expiration": "Durée de validité de la carte (ex: 36 mois)",
    "cards.0.card_info.renewal_option": "Renouvellement automatique ? (ex: AUTO ou MANUAL)",
    "cards.0.card_info.pre_expiration": "Délai avant expiration pour lancer le renouvellement (ex: 30 jours)",
}

HUMAN_LABELS = {
    "bank": "banque",
    "cards": "cartes",
    "agencies": "agences",
    "agency_name": "nom de l'agence",
    "agency_code": "code de l'agence",
    "bank_code": "code banque",
    "city": "ville",
    "city_code": "code de la ville",
    "region": "région",
    "region_code": "code de la région",
    "currency": "devise",
    "country": "pays",
    "name": "nom",
    "resources": "ressources",
    "card_info": "infos carte",
    "bin": "BIN",
    "network": "réseau",
    "product": "produit",
    "services": "services",
    "enabled": "services activés",
}


def _index_to_ordinal(idx: int) -> str:
    ords = ["première", "deuxième", "troisième", "quatrième", "cinquième"]
    return ords[idx] if 0 <= idx < len(ords) else f"numéro {idx+1}"


def _pretty_segment(seg: str) -> str:
    return HUMAN_LABELS.get(seg, seg.replace("_", " "))


def _pretty_path(path: str) -> str:
    parts = path.split(".")
    out = []
    i = 0
    while i < len(parts):
        p = parts[i]
        if p.isdigit():
            idx = int(p)
            out.append(f"({_index_to_ordinal(idx)})")
            i += 1
            continue
        out.append(_pretty_segment(p))
        i += 1
    s = " > ".join(out)
    s = re.sub(r">\s+\(", " (", s)
    return s


def _friendly_limits_question(path: str) -> str:
    """
    Convertit un path limits profond en question courte.
    Ex:
    cards.0.limits.by_type.DEFAULT.domestic.daily_amount
    -> "Quel est le montant limite national par jour ? (ex: 20000)"
    """
    if path.endswith("limits.selected_limit_types"):
        return "Quels types de limites veux-tu activer ? (ex: DEFAULT) Donne une liste séparée par virgules."

    m = re.search(
        r"cards\.0\.limits\.by_type\.([A-Za-z0-9_]+)\.(domestic|international|total|per_transaction)\.(daily|weekly|monthly)_(amount|count|min|max)$",
        path,
    )
    if not m:
        return ""

    _limit_type, scope, period, metric = m.groups()

    scope_fr = {
        "domestic": "national",
        "international": "international",
        "total": "global",
        "per_transaction": "par transaction",
    }.get(scope, scope)

    period_fr = {"daily": "par jour", "weekly": "par semaine", "monthly": "par mois"}.get(
        period, period
    )

    metric_fr = {
        "amount": "montant",
        "count": "nombre d’opérations",
        "min": "montant minimum",
        "max": "montant maximum",
    }.get(metric, metric)

    if scope == "per_transaction":
        return f"Quel est le {metric_fr} {scope_fr} ? (ex: 100)"
    return f"Quel est le {metric_fr} limite {scope_fr} {period_fr} ? (ex: 20000)"


def _friendly_fees_question(path: str) -> str:
    """
    Simplifie cards.0.fees.* en questions lisibles.
    """
    if not path.startswith("cards.0.fees."):
        return ""

    field = path.split(".")[-1]
    mapping = {
        "fee_description": "Quelle est la description des frais ?",
        "billing_event": "Quel est l’événement de facturation ? (ex: ISSUANCE, RENEWAL)",
        "grace_period": "Quelle est la période de grâce ? (en jours, ex: 30)",
        "billing_period": "Quelle est la période de facturation ? (ex: MONTHLY, YEARLY)",
        "registration_fee": "Quels sont les frais d’inscription ? (ex: 50)",
        "periodic_fee": "Quels sont les frais périodiques ? (ex: 10)",
        "replacement_fee": "Quels sont les frais de remplacement ? (ex: 25)",
        "pin_recalculation_fee": "Quels sont les frais de recalcul du PIN ? (ex: 5)",
    }
    return mapping.get(field, "Peux-tu préciser les frais ?")


def next_question_for_missing(path: str) -> str:
    """
    Retourne une question simple pour ce champ manquant.
    """
    # 0) mapping ultra précis
    if path in CUSTOM_QUESTIONS:
        return CUSTOM_QUESTIONS[path]

    if path in CARD_INFO_QUESTIONS:
        return CARD_INFO_QUESTIONS[path]

    # 1) limits
    ql = _friendly_limits_question(path)
    if ql:
        return ql

    # 2) fees
    qf = _friendly_fees_question(path)
    if qf:
        return qf

    # 3) règles simples par suffixe
    if path.endswith(".country"):
        return "Quel est le pays ? "
    if path.endswith(".currency"):
        return "Quelle est la devise ? "
    if path.endswith(".name"):
        return "Quel est le nom ?"
    if path.endswith(".code"):
        return "Quel est le code ?"
    if path.endswith(".bin"):
        return "Quel est le BIN ? (6 à 8 chiffres)"
    if path.endswith(".network"):
        return "Quel est le réseau ? (VISA, MASTERCARD)"
    if path.endswith(".resources") or path.endswith(".enabled"):
        return "Donne la liste (séparée par virgules)."

    # 4) fallback SIMPLE (plus de chemin complet)
    leaf = path.split(".")[-1].replace("_", " ")
    return f"Peux-tu préciser {leaf} ?"


def humain_missing_list(missing: list, limit: int = 8) -> str:
    if not missing:
        return "rien ne manque"
    shown = missing[:limit]
    more = len(missing) - len(shown)
    s = ",".join(_pretty_path(p) for p in shown)
    if more > 0:
        s += f" ... (={more} autres)"
    return s