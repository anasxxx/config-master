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
    "bank.currency": "Quelle est la devise ? (ex: MAD, EUR, USD)",
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
    "cards.0.services.enabled": "Quels services veux-tu activer pour la carte ? (liste séparée par virgules)",
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


def next_question_for_missing(path: str) -> str:
    """
    Retourne une question simple pour ce champ manquant.
    """
    if path in CUSTOM_QUESTIONS:
        return CUSTOM_QUESTIONS[path]

    
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
        return "Quel est le réseau ? (VISA, MASTERCARD..)"
    if path.endswith(".resources") or path.endswith(".enabled"):
        return "Donne la liste (séparée par virgules)."

    
    return f"Peux-tu me donner : {_pretty_path(path)} ?"
def humain_missing_list(missing:list,limit:int=8) -> str:
    if not missing:
        return "rien ne manque"
    shown=missing[:limit]
    more=len(missing)-len(shown)
    s=",".join(_pretty_path(p) for p in shown)
    if more > 0:
        s+=f" ... (={more} autres)"
        return s
