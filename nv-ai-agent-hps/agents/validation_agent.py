import json
from pathlib import Path
import re
import unicodedata
from agents.prompts import PROMPT_BUSINESS_VALIDATOR
# Validation Agent
#  Charge le template JSON (contrat)
#  Construit la liste des champs a remplir
#  Detecte les champs manquants
#  Genere des questions pour chaque champ


def load_template(template_path: Path) -> dict:
    if not template_path.exists():
        raise FileNotFoundError(
            f"Template introuvable: {template_path}\n"
            " Mets 'configmaster_required_fields.json' dans le meme dossier que agent.py"
        )
    with open(template_path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _is_missing(v) -> bool:
    if isinstance(v, dict) and "value" in v:
        return _is_missing(v.get("value"))
    if v is None:
        return True
    if isinstance(v, str) and v.strip().lower() in {"", "none", "null", "n/a", "na", "nil", "unknown"}:
        return True
    if isinstance(v, list):
        if len(v) == 0:
            return True
        return all(_is_missing(x) for x in v)
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
    skip_prefixes = (
        "options.",
        "cards.0.services.flags.",
    )
    skip_exact = {
        "cards.0.services.flags",
    }
    paths = [p for p in paths if p not in skip_exact and not any(p.startswith(pref) for pref in skip_prefixes)]
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
    "bank.currency": "Quelle est la devise ? (MAD/EUR/USD)",
    "bank.bank_code": "Quel est le code de la banque (bank code) ?",
    "bank.resources": "Quelles ressources veux-tu activer ?",
    # First agency (index 0)
    "bank.agencies.0.agency_name": "Quel est le nom de l'agence ?",
    "bank.agencies.0.agency_code": "Quel est le code de cette agence ?",
    "bank.agencies.0.city": "Dans quelle ville se trouve cette agence ?",
    "bank.agencies.0.city_code": "Quel est le code de la ville ?",
    "bank.agencies.0.region": "Quelle est la region ?",
    "bank.agencies.0.region_code": "Quel est le code de la region ?",
    # Cards (index 0)
    "cards.0.card_info.bin": "Quel est le BIN de la carte ? (6 a 11 chiffres)",
    "cards.0.card_info.network": "Quel est le reseau de la carte ?",
    "cards.0.services.enabled": "Quels services veux-tu activer pour la carte ?",
    "cards.0.card_range.tranche_min": "Peux-tu preciser la tranche Min et Max du (PAN) ?",
}


#  card_info 
CARD_INFO_QUESTIONS = {
    "cards.0.card_info.plastic_type": "Type de carte (plastique)",
    "cards.0.card_info.card_description": "Nom/description du produit carte",
    "cards.0.card_info.product_type": "Type de carte",
    "cards.0.card_info.product_code": "Code du produit carte",

    # Simplification des termes techniques
    "cards.0.card_info.pvk_index": "Index PVK",
    "cards.0.card_info.service_code": "Code service de la carte",

    "cards.0.card_info.expiration": "Duree de validite de la carte",
    "cards.0.card_info.renewal_option": "Renouvellement automatique ?",
    "cards.0.card_info.pre_expiration": "Delai avant expiration pour lancer le renouvellement",
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
    "region": "region",
    "region_code": "code de la region",
    "currency": "devise",
    "country": "pays",
    "name": "nom",
    "resources": "ressources",
    "card_info": "infos carte",
    "bin": "BIN",
    "network": "reseau",
    "product": "produit",
    "services": "services",
    "enabled": "services actives",
}


def _index_to_ordinal(idx: int) -> str:
    ords = ["premiere", "deuxieme", "troisieme", "quatrieme", "cinquieme"]
    return ords[idx] if 0 <= idx < len(ords) else f"numero {idx+1}"


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
        return "Quels types de limites veux-tu activer ?"

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
        "count": "nombre d'operations",
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
        "billing_event": "Quel est l'evenement de facturation ? (1, 2 ou 3)",
        "grace_period": "Quelle est la periode de grace ? (en jours, ex: 30)",
        "billing_period": "Quelle est la periode de facturation ? (M, A, T ou S)",
        "registration_fee": "Quels sont les frais d'inscription ? (ex: 50)",
        "periodic_fee": "Quels sont les frais periodiques ? (ex: 10)",
        "replacement_fee": "Quels sont les frais de remplacement ? (ex: 25)",
        "pin_recalculation_fee": "Quels sont les frais de recalcul du PIN ? (ex: 5)",
    }
    return mapping.get(field, "Peux-tu preciser les frais ?")


def _fees_form_question(paths: list[str]) -> str:
    return "=== Description des frais ===\nVeuillez remplir les champs suivants :"


def _fees_form_fields(paths: list[str]) -> list[dict]:
    ordered = [
        ("cards.0.fees.fee_description", "Description des frais :"),
        ("cards.0.fees.billing_event", "Evenement de facturation (1=Emission, 2=Renouvellement, 3=Remplacement) :"),
        ("cards.0.fees.grace_period", "Periode de grace (en jours, ex: 0) :"),
        ("cards.0.fees.billing_period", "Periode de facturation (M=Mensuel, A=Annuel, T=Trimestriel, S=Semestriel) :"),
        ("cards.0.fees.registration_fee", "Frais d'inscription :"),
        ("cards.0.fees.periodic_fee", "Frais periodiques :"),
        ("cards.0.fees.replacement_fee", "Frais de remplacement :"),
        ("cards.0.fees.pin_recalculation_fee", "Frais de recalcul du PIN :"),
    ]
    return [{"path": path, "label": label} for path, label in ordered if path in paths]


def _tranche_form_question(paths: list[str]) -> str:
    return "=== Configuration du PAN ===\nPeux-tu preciser la tranche Min et Max du PAN ?"


def _tranche_form_fields(paths: list[str]) -> list[dict]:
    ordered = [
        ("cards.0.card_range.tranche_min", "Tranche PAN minimum :"),
        ("cards.0.card_range.tranche_max", "Tranche PAN maximum :"),
    ]
    return [{"path": path, "label": label} for path, label in ordered if path in paths]


def _limits_form_question(title: str) -> str:
    return title


def _limits_form_validators(scope: str) -> list[dict]:
    if scope != "per_transaction":
        return []
    return [
        {
            "type": "gte_path",
            "left_path": "cards.0.limits.by_type.DEFAULT.per_transaction.max_amount",
            "right_path": "cards.0.limits.by_type.DEFAULT.per_transaction.min_amount",
            "message": "Le montant maximum par transaction doit etre superieur ou egal au montant minimum.",
        }
    ]


def _limits_form_fields(scope: str, paths: list[str]) -> list[dict]:
    ordered_map = {
        "domestic": [
            ("cards.0.limits.by_type.DEFAULT.domestic.daily_amount", "Montant limite national par jour :"),
            ("cards.0.limits.by_type.DEFAULT.domestic.daily_count", "Nombre d’opérations limite national par jour :"),
            ("cards.0.limits.by_type.DEFAULT.domestic.weekly_amount", "Montant limite national par semaine :"),
            ("cards.0.limits.by_type.DEFAULT.domestic.weekly_count", "Nombre d’opérations limite national par semaine :"),
            ("cards.0.limits.by_type.DEFAULT.domestic.monthly_amount", "Montant limite national par mois :"),
            ("cards.0.limits.by_type.DEFAULT.domestic.monthly_count", "Nombre d’opérations limite national par mois :"),
        ],
        "international": [
            ("cards.0.limits.by_type.DEFAULT.international.daily_amount", "Montant limite international par jour :"),
            ("cards.0.limits.by_type.DEFAULT.international.daily_count", "Nombre d’opérations limite international par jour :"),
            ("cards.0.limits.by_type.DEFAULT.international.weekly_amount", "Montant limite international par semaine :"),
            ("cards.0.limits.by_type.DEFAULT.international.weekly_count", "Nombre d’opérations limite international par semaine :"),
            ("cards.0.limits.by_type.DEFAULT.international.monthly_amount", "Montant limite international par mois :"),
            ("cards.0.limits.by_type.DEFAULT.international.monthly_count", "Nombre d’opérations limite international par mois :"),
        ],
        "total": [
            ("cards.0.limits.by_type.DEFAULT.total.daily_amount", "Montant limite global par jour :"),
            ("cards.0.limits.by_type.DEFAULT.total.daily_count", "Nombre d’opérations limite global par jour :"),
            ("cards.0.limits.by_type.DEFAULT.total.weekly_amount", "Montant limite global par semaine :"),
            ("cards.0.limits.by_type.DEFAULT.total.weekly_count", "Nombre d’opérations limite global par semaine :"),
            ("cards.0.limits.by_type.DEFAULT.total.monthly_amount", "Montant limite global par mois :"),
            ("cards.0.limits.by_type.DEFAULT.total.monthly_count", "Nombre d’opérations limite global par mois :"),
        ],
        "per_transaction": [
            ("cards.0.limits.by_type.DEFAULT.per_transaction.min_amount", "Montant minimum par transaction :"),
            ("cards.0.limits.by_type.DEFAULT.per_transaction.max_amount", "Montant maximum par transaction :"),
        ],
    }
    ordered = ordered_map.get(scope, [])
    return [{"path": path, "label": label} for path, label in ordered if path in paths]


def _humanize_question(path: str, q: str) -> str:
    base = (q or "").strip()
    if not base:
        base = "Peux-tu preciser cette information ?"

    if "?" not in base and "(ex:" not in base.lower():
        base = base.rstrip(".") + " ?"

    intros = [
        "",
        "Parfait.",
        "Top.",
        "D'accord.",
        "Super.",
    ]
    idx = sum(ord(c) for c in (path + "|" + base)) % len(intros)
    intro = intros[idx]

    explain = ""
    if path.endswith(".currency"):
        explain = "Format attendu: code ISO a 3 lettres (ex: MAD, EUR)."
    elif path.endswith(".bin"):
        explain = "Format attendu: 6 a 11 chiffres."
    elif path.endswith(".code") or path.endswith("_code"):
        explain = "Je prends le code exact."
    elif path.endswith(".resources") or path.endswith(".enabled"):
        explain = "Tu peux repondre sous forme de liste, separee par des virgules."

    msg = f"{intro} {base}".strip()
    if explain:
        msg = f"{msg} {explain}".strip()
    return msg


def _strip_examples(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return t
    # Remove explicit example lines and inline "(ex: ...)" snippets.
    t = re.sub(r"(?im)^\s*ex\s*:\s*.*$", "", t)
    t = re.sub(r"\s*\((?i:ex)\s*:\s*[^)]*\)", "", t)
    t = re.sub(r"\n{2,}", "\n", t).strip()
    return t


def next_question_for_missing(path: str) -> str:
    """
    Retourne une question simple pour ce champ manquant.
    """
    # 0) mapping ultra precis
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

    # 3) regles simples par suffixe
    if path.endswith(".country"):
        return "Quel est le pays ?"
    if path.endswith(".currency"):
        return "Quelle est la devise ?"
    if path.endswith(".name"):
        return "Quel est le nom ?"
    if path.endswith(".code"):
        return "Quel est le code ?"
    if path.endswith(".bin"):
        return "Quel est le BIN ? (6 a 11 chiffres)"
    if path.endswith(".network"):
        return "Quel est le reseau ?"
    if path.endswith(".resources") or path.endswith(".enabled"):
        return "Donne la liste (separee par virgules)."

    # 4) fallback SIMPLE (plus de chemin complet)
    leaf = path.split(".")[-1].replace("_", " ")
    return f"Peux-tu preciser {leaf} ?"


def humain_missing_list(missing: list, limit: int = 8) -> str:
    if not missing:
        return "rien ne manque"
    shown = missing[:limit]
    more = len(missing) - len(shown)
    s = ",".join(_pretty_path(p) for p in shown)
    if more > 0:
        s += f" ... (={more} autres)"
    return s
def format_business_errors(errors: list[dict]) -> str:
    if not errors:
        return ""
    lines = ["Probleme de coherence metier:"]
    for e in errors[:5]:
        lines.append(f"- {e.get('path')}: {e.get('reason')}")
    lines.append("Corrige ces champs puis reessaie.")
    return "\n".join(lines)

QUESTION_GROUPS = [
    {
        "id": "bank_identity",
        "paths": ["bank.name", "bank.country", "bank.currency", "bank.bank_code"],
        "normal": "Donne l'identite banque: nom, pays, devise, code banque.",
        "simple": "Donne 4 infos simples: nom banque, pays, devise, code.",
        "example": "Ex: Atlas Bank, Maroc, MAD, 90001X",
    },
    {
        "id": "main_agency",
        "paths": ["bank.agencies.0.agency_name", "bank.agencies.0.city", "bank.agencies.0.agency_code"],
        "normal": "Donne l'agence principale: nom, ville, code agence.",
        "simple": "Donne juste: nom agence, ville, code agence.",
        "example": "Ex: Agence Centre, Casablanca, 000025",
    },
    {
        "id": "card_profile",
        "paths": ["cards.0.card_info.network", "cards.0.card_info.product_type", "cards.0.card_info.plastic_type"],
        "normal": "Precise le profil carte: reseau, type, support.",
        "simple": "Choisis: reseau, type carte, support plastique.",
        "example": "Ex: VISA, DEBIT, PVC",
    },
    {
        "id": "limits_core",
        "paths": ["cards.0.limits.selected_limit_types", "cards.0.limits.by_type.DEFAULT.domestic.daily_amount"],
        "normal": "Pour les limites: type de limite puis montant journalier.",
        "simple": "Donne type limite + montant par jour.",
        "example": "Ex: Purchase, 30000",
    },
]


MENU_FIELDS = {
    "cards.0.card_info.network": {
        "title": "Choisis le reseau",
        "options": [
            {"id": "1", "label": "VISA", "value": "VISA", "aliases": ["1", "visa"]},
            {"id": "2", "label": "MASTERCARD", "value": "MCRD", "aliases": ["2", "mcrd", "mastercard", "master"]},
            {"id": "3", "label": "AMEX", "value": "AMEX", "aliases": ["3", "amex", "american express"]},
            {"id": "4", "label": "DINERS", "value": "DINERS", "aliases": ["4", "diners", "diners club"]},
            {"id": "5", "label": "EUROPAY", "value": "EUROPAY", "aliases": ["5", "europay"]},
            {"id": "6", "label": "TAG-YUP", "value": "TAG-YUP", "aliases": ["6", "tag-yup", "tag yup", "tagyup"]},
            {"id": "7", "label": "UPI", "value": "UPI", "aliases": ["7", "upi"]},
            {"id": "8", "label": "GIMN", "value": "GIMN", "aliases": ["8", "gimn"]},
            {"id": "9", "label": "JCB", "value": "JCB", "aliases": ["9", "jcb"]},
            {"id": "10", "label": "PRIVATIVE", "value": "PRIVATIVE", "aliases": ["10", "privative"]},
        ],
    },
    "cards.0.card_info.product_type": {
        "title": "Choisis le type carte",
        "options": [
            {"id": "1", "value": "DEBIT", "aliases": ["1", "debit", "debit card"]},
            {"id": "2", "value": "PREPAID", "aliases": ["2", "prepaid"]},
            {"id": "3", "value": "CREDIT", "aliases": ["3", "credit", "credit card"]},
        ],
    },
    "cards.0.card_info.plastic_type": {
        "title": "Choisis le type de carte (plastique)",
        "options": [
            {"id": "1", "label": "Printed", "value": "PVC", "aliases": ["1", "printed", "print", "pvc", "plastic"]},
            {"id": "2", "label": "EmBossed", "value": "PETG", "aliases": ["2", "embossed", "emboss", "embossed card", "embossed plastic", "embossed plastique", "embossed type", "embossed card type", "emBossed", "embossed", "petg"]},
            {"id": "3", "label": "VIRTUAL", "value": "VRT", "aliases": ["3", "virtual", "virtuelle", "virtuel", "vrt"]},
        ],
    },
    "cards.0.card_info.renewal_option": {
        "title": "Choisis l'option de renouvellement",
        "options": [
            {"id": "1", "label": "AUTO", "value": "AUTO", "aliases": ["1", "auto", "automatic", "automatique", "y", "yes", "oui"]},
            {"id": "2", "label": "MANUAL", "value": "MANUAL", "aliases": ["2", "manual", "manuel", "manuelle", "n", "no", "non"]},
        ],
    },
    "bank.resources": {
        "title": "Choisis les ressources (tu peux donner plusieurs choix: 1,3,5)",
        "options": [
            {"id": "1", "value": "MCD_MDS", "aliases": ["1", "mcd_mds", "mcd mds"]},
            {"id": "2", "value": "MCD_CIS", "aliases": ["2", "mcd_cis", "mcd cis"]},
            {"id": "3", "value": "UPI", "aliases": ["3", "upi"]},
            {"id": "4", "value": "HOST_BANK", "aliases": ["4", "host_bank", "host bank"]},
            {"id": "5", "value": "SID", "aliases": ["5", "sid"]},
            {"id": "6", "value": "VISA_BASE1", "aliases": ["6", "visa_base1", "visa base1"]},
            {"id": "7", "value": "VISA_SMS", "aliases": ["7", "visa_sms", "visa sms"]},
        ],
    },
    "cards.0.services.enabled": {
        "title": "Choisis les services (tu peux donner plusieurs choix: 1,4,9)",
        "options": [
            {"id": "1", "value": "achat", "aliases": ["1", "achat", "achats", "purchase"]},
            {"id": "2", "value": "retrait", "aliases": ["2", "retrait", "withdrawal"]},
            {"id": "3", "value": "cashback", "aliases": ["3", "cashback"]},
            {"id": "4", "value": "quasicash", "aliases": ["4", "quasicash", "quasi-cash", "quasi cash"]},
            {"id": "5", "value": "advance", "aliases": ["5", "advance", "cash advance"]},
            {"id": "6", "value": "refund", "aliases": ["6", "refund", "remboursement", "remboursements"]},
            {"id": "7", "value": "original", "aliases": ["7", "original"]},
            {"id": "8", "value": "moneysend", "aliases": ["8", "moneysend", "money send", "envoi d'argent"]},
            {"id": "9", "value": "authentication", "aliases": ["9", "authentication", "authentification"]},
            {"id": "10", "value": "solde", "aliases": ["10", "solde", "consultation solde", "balance"]},
            {"id": "11", "value": "releve", "aliases": ["11", "releve", "mini-releve", "statement"]},
            {"id": "12", "value": "transfert", "aliases": ["12", "transfert", "transfer", "transfers"]},
            {"id": "13", "value": "billpayment", "aliases": ["13", "billpayment", "paiement factures", "bill payment"]},
            {"id": "14", "value": "ecommerce", "aliases": ["14", "ecommerce", "e-commerce"]},
            {"id": "15", "value": "pinchange", "aliases": ["15", "pinchange", "changement pin", "pin change"]},
        ],
    },
    "cards.0.limits.selected_limit_types": {
        "title": "Choisis les types de limites (tu peux donner plusieurs choix: 1,2)",
        "options": [
            {"id": "1", "value": "Retrait", "aliases": ["1", "retrait"]},
            {"id": "2", "value": "Purchase", "aliases": ["2", "purchase"]},
            {"id": "3", "value": "CASH_advance", "aliases": ["3", "cash_advance", "cash advance"]},
            {"id": "4", "value": "Quasi-cash", "aliases": ["4", "quasi-cash", "quasi cash"]},
            {"id": "5", "value": "E-commerce", "aliases": ["5", "e-commerce", "ecommerce"]},
        ],
    },
}


def _norm(s: str) -> str:
    t = (s or "").strip().lower()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = re.sub(r"\s+", " ", t)
    return t


def _is_recent_repeat(dialog_state: dict, paths: list[str]) -> bool:
    if not isinstance(dialog_state, dict):
        return False
    # Do not trigger "Je reformule" when the previous user turn was empty.
    if not str(dialog_state.get("last_user_message") or "").strip():
        return False
    last = dialog_state.get("last_question_paths") or []
    asked = set(dialog_state.get("asked_fields") or [])
    return set(last) == set(paths) and any(p in asked for p in paths)


def _label_for_group_path(path: str) -> str:
    labels = {
        "bank.name": "nom",
        "bank.country": "pays",
        "bank.currency": "devise",
        "bank.bank_code": "code banque",
        "bank.agencies.0.agency_name": "nom agence",
        "bank.agencies.0.city": "ville",
        "bank.agencies.0.agency_code": "code agence",
        "cards.0.card_info.network": "reseau",
        "cards.0.card_info.product_type": "type carte",
        "cards.0.card_info.plastic_type": "support",
    }
    return labels.get(path, path.split(".")[-1].replace("_", " "))


def next_question_advanced(missing: list[str], dialog_state: dict, fallback_next_question) -> dict:
    if not missing:
        return {"question": "", "paths": [], "menu": None}

    mode = (dialog_state or {}).get("mode", "normal")

    if missing[0].startswith("cards.0.fees."):
        fee_form_paths = [
            "cards.0.fees.fee_description",
            "cards.0.fees.billing_event",
            "cards.0.fees.grace_period",
            "cards.0.fees.billing_period",
            "cards.0.fees.registration_fee",
            "cards.0.fees.periodic_fee",
            "cards.0.fees.replacement_fee",
            "cards.0.fees.pin_recalculation_fee",
        ]
        fee_form_missing = [p for p in fee_form_paths if p in missing]
        if fee_form_missing:
            repeated = _is_recent_repeat(dialog_state, fee_form_missing)
            q = _fees_form_question(fee_form_missing)
            if mode == "simplified":
                q = f"Version simple: {q}"
            if repeated:
                q = f"Je reformule: {q}"
            return {
                "question": q,
                "paths": fee_form_missing,
                "menu": None,
                "form": {
                    "id": "fees_details",
                    "title": "Description des frais",
                    "fields": _fees_form_fields(fee_form_missing),
                    "defaults": (
                        [{"path": "cards.0.fees.fee_description", "value": "Description des frais"}]
                        if "cards.0.fees.fee_description" in fee_form_missing
                        else []
                    ),
                },
            }

    limit_forms = [
        (
            "domestic",
            [
                "cards.0.limits.by_type.DEFAULT.domestic.daily_amount",
                "cards.0.limits.by_type.DEFAULT.domestic.daily_count",
                "cards.0.limits.by_type.DEFAULT.domestic.weekly_amount",
                "cards.0.limits.by_type.DEFAULT.domestic.weekly_count",
                "cards.0.limits.by_type.DEFAULT.domestic.monthly_amount",
                "cards.0.limits.by_type.DEFAULT.domestic.monthly_count",
            ],
            "--- Limites nationales ---",
        ),
        (
            "international",
            [
                "cards.0.limits.by_type.DEFAULT.international.daily_amount",
                "cards.0.limits.by_type.DEFAULT.international.daily_count",
                "cards.0.limits.by_type.DEFAULT.international.weekly_amount",
                "cards.0.limits.by_type.DEFAULT.international.weekly_count",
                "cards.0.limits.by_type.DEFAULT.international.monthly_amount",
                "cards.0.limits.by_type.DEFAULT.international.monthly_count",
            ],
            "--- Limites internationales ---",
        ),
        (
            "total",
            [
                "cards.0.limits.by_type.DEFAULT.total.daily_amount",
                "cards.0.limits.by_type.DEFAULT.total.daily_count",
                "cards.0.limits.by_type.DEFAULT.total.weekly_amount",
                "cards.0.limits.by_type.DEFAULT.total.weekly_count",
                "cards.0.limits.by_type.DEFAULT.total.monthly_amount",
                "cards.0.limits.by_type.DEFAULT.total.monthly_count",
            ],
            "--- Limites globales ---",
        ),
        (
            "per_transaction",
            [
                "cards.0.limits.by_type.DEFAULT.per_transaction.min_amount",
                "cards.0.limits.by_type.DEFAULT.per_transaction.max_amount",
            ],
            "--- Limites par transaction ---",
        ),
    ]
    for scope, scope_paths, title in limit_forms:
        if missing[0] in scope_paths:
            scope_missing = [p for p in scope_paths if p in missing]
            repeated = _is_recent_repeat(dialog_state, scope_missing)
            q = _limits_form_question(title)
            if mode == "simplified":
                q = f"Version simple: {q}"
            if repeated:
                q = f"Je reformule: {q}"
            return {
                "question": q,
                "paths": scope_missing,
                "menu": None,
                "form": {
                    "id": f"limits_{scope}",
                    "title": title,
                    "fields": _limits_form_fields(scope, scope_missing),
                    "validators": _limits_form_validators(scope),
                },
            }

    tranche_pair = [
        "cards.0.card_range.tranche_min",
        "cards.0.card_range.tranche_max",
    ]
    if missing[0] in tranche_pair and all(p in missing for p in tranche_pair):
        repeated = _is_recent_repeat(dialog_state, tranche_pair)
        q = _tranche_form_question(tranche_pair)
        if mode == "simplified":
            q = f"Version simple: {q}"
        if repeated:
            q = f"Je reformule: {q}"
        return {
            "question": q,
            "paths": tranche_pair,
            "menu": None,
            "form": {
                "id": "card_range_tranche",
                "title": "Tranche PAN",
                "fields": _tranche_form_fields(tranche_pair),
            },
        }

    path = missing[0]
    repeated = _is_recent_repeat(dialog_state, [path])
    q = fallback_next_question(path)
    if mode == "simplified":
        q = f"Version simple: {q}"
    if repeated:
        q = f"Je reformule: {q}"

    menu = MENU_FIELDS.get(path)
    if menu:
        lines = [f"{o['id']}) {o.get('label', o['value'])}" for o in menu["options"]]
        q = f"{q}\n{menu['title']}:\n" + "\n".join(lines)
    return {"question": q, "paths": [path], "menu": menu}


def resolve_menu_answer(menu: dict, user_text: str):
    if not isinstance(menu, dict):
        return False, user_text
    raw = (user_text or "").strip()
    if not raw:
        return False, user_text

    id_to_value = {}
    norm_to_value = {}
    for opt in menu.get("options", []):
        value = str(opt.get("value", "")).strip()
        if not value:
            continue
        oid = str(opt.get("id", "")).strip()
        if oid:
            id_to_value[oid] = value
        aliases = [_norm(a) for a in (opt.get("aliases") or [])]
        label = str(opt.get("label", "")).strip()
        if label:
            aliases.append(_norm(label))
        aliases.append(_norm(value))
        for a in aliases:
            norm_to_value[a] = value

    # multi-select support: "1,3,5" or "Retrait, E-commerce"
    tokens = [t.strip() for t in re.split(r"[,\;/]+", raw) if t.strip()]
    if len(tokens) > 1:
        out = []
        for tok in tokens:
            v = id_to_value.get(tok) or norm_to_value.get(_norm(tok))
            if not v:
                return False, user_text
            if v not in out:
                out.append(v)
        return True, ", ".join(out)

    single = id_to_value.get(raw) or norm_to_value.get(_norm(raw))
    if single:
        return True, single
    return False, user_text

