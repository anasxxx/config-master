import json
from pathlib import Path
import re
import unicodedata
from agents.prompts import PROMPT_BUSINESS_VALIDATOR
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
    if isinstance(v, dict) and "value" in v:
        return _is_missing(v.get("value"))
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


def _humanize_question(path: str, q: str) -> str:
    base = (q or "").strip()
    if not base:
        base = "Peux-tu préciser cette information ?"

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
        explain = "Format attendu: code ISO à 3 lettres (ex: MAD, EUR)."
    elif path.endswith(".bin"):
        explain = "Format attendu: 6 à 8 chiffres."
    elif path.endswith(".network"):
        explain = "Valeurs courantes: VISA ou MASTERCARD."
    elif path.endswith(".code") or path.endswith("_code"):
        explain = "Je prends le code exact."
    elif path.endswith(".resources") or path.endswith(".enabled"):
        explain = "Tu peux répondre sous forme de liste, séparée par des virgules."

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
    # 0) mapping ultra précis
    if path in CUSTOM_QUESTIONS:
        q = CUSTOM_QUESTIONS[path]
        return _strip_examples(_humanize_question(path, q))

    if path in CARD_INFO_QUESTIONS:
        q = CARD_INFO_QUESTIONS[path]
        return _strip_examples(_humanize_question(path, q))

    # 1) limits
    ql = _friendly_limits_question(path)
    if ql:
        return _strip_examples(_humanize_question(path, ql))

    # 2) fees
    qf = _friendly_fees_question(path)
    if qf:
        return _strip_examples(_humanize_question(path, qf))

    # 3) règles simples par suffixe
    if path.endswith(".country"):
        q = "Quel est le pays ?"
        return _strip_examples(_humanize_question(path, q))
    if path.endswith(".currency"):
        q = "Quelle est la devise ?"
        return _strip_examples(_humanize_question(path, q))
    if path.endswith(".name"):
        q = "Quel est le nom ?"
        return _strip_examples(_humanize_question(path, q))
    if path.endswith(".code"):
        q = "Quel est le code ?"
        return _strip_examples(_humanize_question(path, q))
    if path.endswith(".bin"):
        q = "Quel est le BIN ? (6 à 8 chiffres)"
        return _strip_examples(_humanize_question(path, q))
    if path.endswith(".network"):
        q = "Quel est le réseau ? (VISA, MASTERCARD)"
        return _strip_examples(_humanize_question(path, q))
    if path.endswith(".resources") or path.endswith(".enabled"):
        q = "Donne la liste (séparée par virgules)."
        return _strip_examples(_humanize_question(path, q))

    # 4) fallback SIMPLE (plus de chemin complet)
    leaf = path.split(".")[-1].replace("_", " ")
    q = f"Peux-tu préciser {leaf} ?"
    return _strip_examples(_humanize_question(path, q))


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
    lines = ["⚠ Problème de cohérence métier:"]
    for e in errors[:5]:
        lines.append(f"- {e.get('path')}: {e.get('reason')}")
    lines.append("Corrige ces champs puis réessaie.")
    return "\n".join(lines)

QUESTION_GROUPS = [
    {
        "id": "bank_identity",
        "paths": ["bank.name", "bank.country", "bank.currency", "bank.bank_code"],
        "normal": "Donne l'identite banque: nom, pays, devise, code banque.",
        "simple": "Donne 4 infos simples: nom banque, pays, devise, code.",
        "example": "Ex: Atlas Bank, Maroc, MAD, 90001",
    },
    {
        "id": "main_agency",
        "paths": ["bank.agencies.0.agency_name", "bank.agencies.0.city", "bank.agencies.0.agency_code"],
        "normal": "Donne l'agence principale: nom, ville, code agence.",
        "simple": "Donne juste: nom agence, ville, code agence.",
        "example": "Ex: Agence Centre, Casablanca, 0025",
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
            {"id": "1", "value": "VISA", "aliases": ["1", "visa"]},
            {"id": "2", "value": "MASTERCARD", "aliases": ["2", "mastercard", "master"]},
            {"id": "3", "value": "VISA", "aliases": ["3", "both", "les deux", "les 2"]},
        ],
    },
    "cards.0.card_info.product_type": {
        "title": "Choisis le type carte",
        "options": [
            {"id": "1", "value": "DEBIT", "aliases": ["1", "debit"]},
            {"id": "2", "value": "PREPAID", "aliases": ["2", "prepaid", "prepayee"]},
            {"id": "3", "value": "CREDIT", "aliases": ["3", "credit"]},
        ],
    },
    "cards.0.card_info.plastic_type": {
        "title": "Choisis le support",
        "options": [
            {"id": "1", "value": "PVC", "aliases": ["1", "pvc"]},
            {"id": "2", "value": "METAL", "aliases": ["2", "metal"]},
            {"id": "3", "value": "OTHER", "aliases": ["3", "other", "autre", "petg"]},
        ],
    },
    "bank.currency": {
        "title": "Choisis la devise",
        "options": [
            {"id": "1", "value": "MAD", "aliases": ["1", "mad"]},
            {"id": "2", "value": "EUR", "aliases": ["2", "eur"]},
            {"id": "3", "value": "USD", "aliases": ["3", "usd"]},
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
            {"id": "1", "value": "Retrait", "aliases": ["1", "retrait"]},
            {"id": "2", "value": "Cash Advance", "aliases": ["2", "cash advance"]},
            {"id": "3", "value": "Transferts", "aliases": ["3", "transferts", "transferts"]},
            {"id": "4", "value": "Consultation Solde", "aliases": ["4", "consultation solde"]},
            {"id": "5", "value": "Changement PIN", "aliases": ["5", "changement pin"]},
            {"id": "6", "value": "Envoi d'argent", "aliases": ["6", "envoi d'argent", "envoi dargent"]},
            {"id": "7", "value": "Original", "aliases": ["7", "original"]},
            {"id": "8", "value": "Achats", "aliases": ["8", "achats"]},
            {"id": "9", "value": "E-commerce", "aliases": ["9", "e-commerce", "ecommerce"]},
            {"id": "10", "value": "Quasi-Cash", "aliases": ["10", "quasi-cash", "quasi cash"]},
            {"id": "11", "value": "Mini-Relevé", "aliases": ["11", "mini-releve", "mini relevé"]},
            {"id": "12", "value": "Remboursements", "aliases": ["12", "remboursements"]},
            {"id": "13", "value": "Paiement Factures", "aliases": ["13", "paiement factures"]},
            {"id": "14", "value": "Authentification", "aliases": ["14", "authentification"]},
            {"id": "15", "value": "Cashback", "aliases": ["15", "cashback"]},
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

    for grp in QUESTION_GROUPS:
        grp_missing = [p for p in grp["paths"] if p in missing]
        if len(grp_missing) >= 2:
            repeated = _is_recent_repeat(dialog_state, grp_missing)
            labels = ", ".join(_label_for_group_path(p) for p in grp_missing)
            if mode == "simplified":
                prompt = f"Donne juste: {labels}."
            else:
                prompt = f"Donne: {labels}."
            if repeated:
                prompt = "Je reformule: " + prompt
            q = prompt

            menu_blocks = []
            for p in grp_missing:
                menu = MENU_FIELDS.get(p)
                if not menu:
                    continue
                lines = [f"{o['id']}) {o['value']}" for o in menu["options"]]
                menu_blocks.append(f"{menu['title']}:\n" + "\n".join(lines))
            if menu_blocks:
                q = q + "\n" + "\n\n".join(menu_blocks)
            return {"question": q, "paths": grp_missing, "menu": None}

    path = missing[0]
    repeated = _is_recent_repeat(dialog_state, [path])
    q = fallback_next_question(path)
    if mode == "simplified":
        q = f"Version simple: {q}"
    if repeated:
        q = f"Je reformule: {q}"

    menu = MENU_FIELDS.get(path)
    if menu:
        lines = [f"{o['id']}) {o['value']}" for o in menu["options"]]
        q = f"{q}\n{menu['title']}:\n" + "\n".join(lines)
    return {"question": q, "paths": [path], "menu": menu}


def resolve_menu_answer(menu: dict, user_text: str):
    if not isinstance(menu, dict):
        return False, user_text
    raw = (user_text or "").strip()
    if not raw:
        return False, user_text

    norm_to_value = {}
    for opt in menu.get("options", []):
        value = str(opt.get("value", "")).strip()
        if not value:
            continue
        aliases = [_norm(a) for a in (opt.get("aliases") or [])]
        aliases.append(_norm(value))
        for a in aliases:
            norm_to_value[a] = value

    # multi-select support: "1,3,5" or "Retrait, E-commerce"
    tokens = [t.strip() for t in re.split(r"[,\;/]+", raw) if t.strip()]
    if len(tokens) > 1:
        out = []
        for tok in tokens:
            v = norm_to_value.get(_norm(tok))
            if not v:
                return False, user_text
            if v not in out:
                out.append(v)
        return True, ", ".join(out)

    single = norm_to_value.get(_norm(raw))
    if single:
        return True, single
    return False, user_text
