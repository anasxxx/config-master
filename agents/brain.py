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
        "bank.agencies.0.agency_name": [
            "bank.agencies.0.agency_name",
            "bank.agencies.0.agency_code",
        ],
        "bank.agencies.0.city": [
            "bank.agencies.0.city",
            "bank.agencies.0.city_code",
        ],
        "bank.agencies.0.region": [
            "bank.agencies.0.region",
            "bank.agencies.0.region_code",
        ],
        "cards.0.card_info.bin": [
            "cards.0.card_info.bin",
            "cards.0.card_info.network",
        ],
        "cards.0.limits.by_type.DEFAULT.domestic.daily_amount": [
            "cards.0.limits.by_type.DEFAULT.domestic.daily_amount",
            "cards.0.limits.by_type.DEFAULT.domestic.weekly_amount",
            "cards.0.limits.by_type.DEFAULT.domestic.monthly_amount",
        ],
        "cards.0.limits.by_type.DEFAULT.international.daily_amount": [
            "cards.0.limits.by_type.DEFAULT.international.daily_amount",
            "cards.0.limits.by_type.DEFAULT.international.weekly_amount",
            "cards.0.limits.by_type.DEFAULT.international.monthly_amount",
        ],
    }

    GROUP_QUESTIONS = {
        "bank.agencies.0.agency_name": "Tu peux me donner le nom de l'agence et son code ? (ex: Agence Centre, 555)",
        "bank.agencies.0.city": "Tu peux me donner la ville et son code ? (ex: Casablanca, 001)",
        "bank.agencies.0.region": "Tu peux me donner la région et son code ? (ex: Grand Casablanca, 10)",
        "cards.0.card_info.bin": "Donne-moi le BIN et le réseau de la carte, s'il te plaît. (ex: 445555, VISA)",
        "cards.0.limits.by_type.DEFAULT.domestic.daily_amount":
            "Tu peux préciser les plafonds nationaux (jour, semaine, mois) ? (ex: 5000, 20000, 80000)",
        "cards.0.limits.by_type.DEFAULT.international.daily_amount":
            "Tu peux préciser les plafonds internationaux (jour, semaine, mois) ? (ex: 2000, 10000, 40000)",
    }

    if user_msg:
        # ✅ A2: on passe state (pas facts)
        apply_user_message_to_facts(state, template_obj, user_msg)
        auto_fill(state["facts"])

        last_paths = state.get("meta", {}).get("last_question_paths") or []
        if last_paths:
            miss_after = missing_paths(state["facts"], template_obj, req_paths)
            miss_after = [p for p in miss_after if not _is_ignored(p)]

            if len(last_paths) > 1 and any(p in miss_after for p in last_paths):
                ok = apply_multi_field_answer(state, template_obj, last_paths, user_msg)
                if ok:
                    auto_fill(state["facts"])
            else:
                last_path = last_paths[0]
                if last_path in miss_after:
                    ok = apply_single_field_answer(state, template_obj, last_path, user_msg)
                    if ok:
                        auto_fill(state["facts"])

    # Vérifier les champs manquants
    miss = missing_paths(state["facts"], template_obj, req_paths)
    miss = [p for p in miss if not _is_ignored(p)]
    if not miss:
        return {"type": "DONE"}

    # Question suivante
    next_path = miss[0]

    # Grouping
    if next_path in GROUPS:
        paths = GROUPS[next_path]
        state.setdefault("meta", {})["last_question_paths"] = paths
        return {"type": "ASK", "question": GROUP_QUESTIONS.get(next_path, "Donne les infos"), "paths": paths}

    # Single
    state.setdefault("meta", {})["last_question_paths"] = [next_path]
    q = next_question_for_missing(next_path)
    return {"type": "ASK", "question": q, "paths": [next_path]}

