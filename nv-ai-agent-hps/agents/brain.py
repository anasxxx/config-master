from typing import Dict, Any, List, Optional
import re


def brain_step(
    *,
    state: Dict[str, Any],
    template_obj: Dict[str, Any],
    req_paths: List[str],
    user_msg: Optional[str],
    apply_user_message_to_facts,
    apply_single_field_answer,
    apply_multi_field_answer,
    missing_paths,
    next_question_for_missing,
    auto_fill,
) -> Dict[str, Any]:

    
    IGNORE_PATTERNS = [
        r"^cards\.0\.limits\.selected_limit_types$",
        r"^cards\.0\.limits\.by_type\.DEFAULT\.(domestic|international|total)\.(daily|weekly|monthly)_count$",
        r"^cards\.0\.limits\.by_type\.DEFAULT\.total\.(daily|weekly|monthly)_amount$",
        r"^cards\.0\.limits\.by_type\.DEFAULT\.per_transaction\.(min|max)_amount$",
    ]

    def _is_ignored(path: str) -> bool:
        return any(re.match(pat, path) for pat in IGNORE_PATTERNS)

    
    GROUPS = {
        # Agence: nom + code
        "bank.agencies.0.agency_name": [
            "bank.agencies.0.agency_name",
            "bank.agencies.0.agency_code",
        ],
        # Agence: ville + code ville
        "bank.agencies.0.city": [
            "bank.agencies.0.city",
            "bank.agencies.0.city_code",
        ],
        # Agence: région + code région
        "bank.agencies.0.region": [
            "bank.agencies.0.region",
            "bank.agencies.0.region_code",
        ],
        # Carte: BIN + réseau
        "cards.0.card_info.bin": [
            "cards.0.card_info.bin",
            "cards.0.card_info.network",
        ],

        
        # National (domestic): jour/semaine/mois
        "cards.0.limits.by_type.DEFAULT.domestic.daily_amount": [
            "cards.0.limits.by_type.DEFAULT.domestic.daily_amount",
            "cards.0.limits.by_type.DEFAULT.domestic.weekly_amount",
            "cards.0.limits.by_type.DEFAULT.domestic.monthly_amount",
        ],
        # International: jour/semaine/mois
        "cards.0.limits.by_type.DEFAULT.international.daily_amount": [
            "cards.0.limits.by_type.DEFAULT.international.daily_amount",
            "cards.0.limits.by_type.DEFAULT.international.weekly_amount",
            "cards.0.limits.by_type.DEFAULT.international.monthly_amount",
        ],
    }

    GROUP_QUESTIONS = {
        "bank.agencies.0.agency_name": "Nom de l’agence + code (ex: Agence Centre, 555)",
        "bank.agencies.0.city": "Ville + code ville (ex: Casablanca, 001)",
        "bank.agencies.0.region": "Région + code région (ex: Grand Casablanca, 10)",
        "cards.0.card_info.bin": "BIN + réseau (ex: 445555, VISA)",

        
        "cards.0.limits.by_type.DEFAULT.domestic.daily_amount":
            "Plafonds NATIONAUX (montant par jour, semaine, mois) ex: 5000, 20000, 80000",
        "cards.0.limits.by_type.DEFAULT.international.daily_amount":
            "Plafonds INTERNATIONAUX (montant par jour, semaine, mois) ex: 2000, 10000, 40000",
    }

    
    if user_msg:
        apply_user_message_to_facts(state["facts"], template_obj, user_msg)
        auto_fill(state["facts"])

        last_paths = state.get("meta", {}).get("last_question_paths") or []
        if last_paths:
            miss_after = missing_paths(state["facts"], template_obj, req_paths)
            miss_after = [p for p in miss_after if not _is_ignored(p)]

            
            if len(last_paths) > 1 and any(p in miss_after for p in last_paths):
                ok = apply_multi_field_answer(state["facts"], template_obj, last_paths, user_msg)
                if ok:
                    auto_fill(state["facts"])
            else:
                last_path = last_paths[0]
                if last_path in miss_after:
                    ok = apply_single_field_answer(state["facts"], template_obj, last_path, user_msg)
                    if ok:
                        auto_fill(state["facts"])

    #  Vérifier les champs manquants
    miss = missing_paths(state["facts"], template_obj, req_paths)
    miss = [p for p in miss if not _is_ignored(p)]
    if not miss:
        return {"type": "DONE"}

    #  Choisir la prochaine question
    last_asked = state.get("meta", {}).get("last_question_path")
    if last_asked and last_asked in miss:
        next_path = last_asked
    else:
        def _priority(path: str) -> int:
            # Banque
            if path == "bank.name": return 0
            if path == "bank.country": return 1
            if path == "bank.currency": return 2
            if path == "bank.bank_code": return 3
            if path == "bank.resources": return 4

            # Agence
            if path.startswith("bank.agencies.0."): return 10

            # Carte base
            if path.startswith("cards.0.card_info."): return 20
            if path == "cards.0.services.enabled": return 25

            # ✅ Limits MVP : après infos carte
            if path.startswith("cards.0.limits.by_type.DEFAULT.domestic."): return 40
            if path.startswith("cards.0.limits.by_type.DEFAULT.international."): return 41

            # reste carte
            if path.startswith("cards.0."): return 50

            return 99

        next_path = sorted(miss, key=_priority)[0]

    # ✅ Multi-field si groupe
    group_paths = GROUPS.get(next_path)
    if group_paths:
        group_missing = [p for p in group_paths if p in miss]
        if group_missing:
            state.setdefault("meta", {})["last_question_path"] = next_path
            state.setdefault("meta", {})["last_question_paths"] = group_missing
            q = GROUP_QUESTIONS.get(next_path, "Donne les infos séparées par virgule.")
            return {"type": "ASK_MULTI", "paths": group_missing, "question": q}

    # fallback normal
    q = next_question_for_missing(next_path)
    state.setdefault("meta", {})["last_question_path"] = next_path
    state.setdefault("meta", {})["last_question_paths"] = [next_path]
    return {"type": "ASK", "path": next_path, "question": q}