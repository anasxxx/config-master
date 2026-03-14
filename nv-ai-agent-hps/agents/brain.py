from typing import Dict, Any, List, Optional
import re


# ── Supervisor-defined question ordering (52 questions) ─────────────────────
# This list defines the EXACT order in which the agent asks questions,
# matching the supervisor's "Questions d'agent" document.
QUESTION_ORDER = [
    # Q1-4: Informations Bancaires
    "bank.name",                                      # Q1
    "bank.country",                                    # Q2
    "bank.currency",                                   # Q3 [auto fill]
    "bank.bank_code",                                  # Q4
    # Q5: Ressources
    "bank.resources",                                  # Q5
    # Q6-11: Agences
    "bank.agencies.0.agency_name",                     # Q6
    "bank.agencies.0.agency_code",                     # Q7
    "bank.agencies.0.city",                            # Q8
    "bank.agencies.0.city_code",                       # Q9 [auto fill]
    "bank.agencies.0.region",                          # Q10 [auto fill]
    "bank.agencies.0.region_code",                     # Q11 [auto fill]
    # Q12-22: Informations Carte
    "cards.0.card_info.bin",                            # Q12
    "cards.0.card_info.plastic_type",                   # Q13
    "cards.0.card_info.card_description",               # Q14
    "cards.0.card_info.product_type",                   # Q15
    "cards.0.card_info.product_code",                   # Q16
    "cards.0.card_info.pvk_index",                      # Q17
    "cards.0.card_info.service_code",                   # Q18
    "cards.0.card_info.network",                        # Q19
    "cards.0.card_info.expiration",                     # Q20
    "cards.0.card_info.renewal_option",                 # Q21
    "cards.0.card_info.pre_expiration",                 # Q22
    # Q23: Tranche PAN (grouped: start + end)
    "cards.0.card_range.start_range",                   # Q23a
    "cards.0.card_range.end_range",                     # Q23b
    # Q24-30: Frais (grouped as form)
    "cards.0.fees.fee_description",                     # Q24
    "cards.0.fees.billing_event",                       # Q25
    "cards.0.fees.billing_period",                      # Q26
    "cards.0.fees.grace_period",                        # grace period (DB field)
    "cards.0.fees.registration_fee",                    # Q27
    "cards.0.fees.periodic_fee",                        # Q28
    "cards.0.fees.replacement_fee",                     # Q29
    "cards.0.fees.pin_recalculation_fee",               # Q30
    # Q31: Services (checkboxes)
    "cards.0.services.enabled",                         # Q31
    # Q32: Types de limites
    "cards.0.limits.selected_limit_types",              # Q32
    # Q33-38: Limites nationales
    "cards.0.limits.by_type.DEFAULT.domestic.daily_amount",      # Q33
    "cards.0.limits.by_type.DEFAULT.domestic.daily_count",       # Q34
    "cards.0.limits.by_type.DEFAULT.domestic.weekly_amount",     # Q35
    "cards.0.limits.by_type.DEFAULT.domestic.weekly_count",      # Q36
    "cards.0.limits.by_type.DEFAULT.domestic.monthly_amount",    # Q37
    "cards.0.limits.by_type.DEFAULT.domestic.monthly_count",     # Q38
    # Q39-44: Limites internationales
    "cards.0.limits.by_type.DEFAULT.international.daily_amount",   # Q39
    "cards.0.limits.by_type.DEFAULT.international.daily_count",    # Q40
    "cards.0.limits.by_type.DEFAULT.international.weekly_amount",  # Q41
    "cards.0.limits.by_type.DEFAULT.international.weekly_count",   # Q42
    "cards.0.limits.by_type.DEFAULT.international.monthly_amount", # Q43
    "cards.0.limits.by_type.DEFAULT.international.monthly_count",  # Q44
    # Q45-50: Limites globales
    "cards.0.limits.by_type.DEFAULT.total.daily_amount",     # Q45
    "cards.0.limits.by_type.DEFAULT.total.daily_count",      # Q46
    "cards.0.limits.by_type.DEFAULT.total.weekly_amount",    # Q47
    "cards.0.limits.by_type.DEFAULT.total.weekly_count",     # Q48
    "cards.0.limits.by_type.DEFAULT.total.monthly_amount",   # Q49
    "cards.0.limits.by_type.DEFAULT.total.monthly_count",    # Q50
    # Q51-52: Min/Max par transaction
    "cards.0.limits.by_type.DEFAULT.per_transaction.min_amount",  # Q51
    "cards.0.limits.by_type.DEFAULT.per_transaction.max_amount",  # Q52
]

# ── Grouping: supervisor says these should be shown as forms ────────────────
GROUPS = {
    # Q23: PAN range — ask min+max together
    "cards.0.card_range.start_range": [
        "cards.0.card_range.start_range",
        "cards.0.card_range.end_range",
    ],
    # Q24-30: Fees — show as form to fill at once (yellow highlight)
    "cards.0.fees.fee_description": [
        "cards.0.fees.fee_description",
        "cards.0.fees.billing_event",
        "cards.0.fees.billing_period",
        "cards.0.fees.grace_period",
        "cards.0.fees.registration_fee",
        "cards.0.fees.periodic_fee",
        "cards.0.fees.replacement_fee",
        "cards.0.fees.pin_recalculation_fee",
    ],
    # Q33-38: Domestic limits — group as form
    "cards.0.limits.by_type.DEFAULT.domestic.daily_amount": [
        "cards.0.limits.by_type.DEFAULT.domestic.daily_amount",
        "cards.0.limits.by_type.DEFAULT.domestic.daily_count",
        "cards.0.limits.by_type.DEFAULT.domestic.weekly_amount",
        "cards.0.limits.by_type.DEFAULT.domestic.weekly_count",
        "cards.0.limits.by_type.DEFAULT.domestic.monthly_amount",
        "cards.0.limits.by_type.DEFAULT.domestic.monthly_count",
    ],
    # Q39-44: International limits — group as form
    "cards.0.limits.by_type.DEFAULT.international.daily_amount": [
        "cards.0.limits.by_type.DEFAULT.international.daily_amount",
        "cards.0.limits.by_type.DEFAULT.international.daily_count",
        "cards.0.limits.by_type.DEFAULT.international.weekly_amount",
        "cards.0.limits.by_type.DEFAULT.international.weekly_count",
        "cards.0.limits.by_type.DEFAULT.international.monthly_amount",
        "cards.0.limits.by_type.DEFAULT.international.monthly_count",
    ],
    # Q45-50: Global/total limits — group as form
    "cards.0.limits.by_type.DEFAULT.total.daily_amount": [
        "cards.0.limits.by_type.DEFAULT.total.daily_amount",
        "cards.0.limits.by_type.DEFAULT.total.daily_count",
        "cards.0.limits.by_type.DEFAULT.total.weekly_amount",
        "cards.0.limits.by_type.DEFAULT.total.weekly_count",
        "cards.0.limits.by_type.DEFAULT.total.monthly_amount",
        "cards.0.limits.by_type.DEFAULT.total.monthly_count",
    ],
    # Q51-52: Per-transaction limits — group
    "cards.0.limits.by_type.DEFAULT.per_transaction.min_amount": [
        "cards.0.limits.by_type.DEFAULT.per_transaction.min_amount",
        "cards.0.limits.by_type.DEFAULT.per_transaction.max_amount",
    ],
}

GROUP_QUESTIONS = {
    "cards.0.card_range.start_range":
        "Peux-tu préciser la tranche Min et Max du PAN ?",
    "cards.0.fees.fee_description":
        "Remplis les informations de frais:\n"
        "- Description des frais\n"
        "- Événement de facturation (1, 2 ou 3)\n"
        "- Période de facturation (M=Mensuel, A=Annuel, T=Trimestriel, S=Semestriel)\n"
        "- Période de grâce (en jours)\n"
        "- Frais d'inscription\n"
        "- Frais périodiques\n"
        "- Frais de remplacement\n"
        "- Frais de recalcul du PIN",
    "cards.0.limits.by_type.DEFAULT.domestic.daily_amount":
        "Précise les limites nationales (montant et nombre d'opérations):\n"
        "- Par jour (montant, nombre)\n"
        "- Par semaine (montant, nombre)\n"
        "- Par mois (montant, nombre)",
    "cards.0.limits.by_type.DEFAULT.international.daily_amount":
        "Précise les limites internationales (montant et nombre d'opérations):\n"
        "- Par jour (montant, nombre)\n"
        "- Par semaine (montant, nombre)\n"
        "- Par mois (montant, nombre)",
    "cards.0.limits.by_type.DEFAULT.total.daily_amount":
        "Précise les limites globales (montant et nombre d'opérations):\n"
        "- Par jour (montant, nombre)\n"
        "- Par semaine (montant, nombre)\n"
        "- Par mois (montant, nombre)",
    "cards.0.limits.by_type.DEFAULT.per_transaction.min_amount":
        "Précise le montant minimum et maximum par transaction.",
}


def _sort_missing_by_order(miss: List[str]) -> List[str]:
    """Sort missing paths according to the supervisor's question order."""
    order_map = {p: i for i, p in enumerate(QUESTION_ORDER)}
    known = [p for p in miss if p in order_map]
    unknown = [p for p in miss if p not in order_map]
    known.sort(key=lambda p: order_map[p])
    return known + unknown


def brain_step(
    *,
    state: Dict[str, Any],
    template_obj: Dict[str, Any],
    req_paths: List[str],
    user_msg: Optional[str],
    dialog_state: Optional[Dict[str, Any]] = None,
    apply_user_message_to_facts,
    apply_single_field_answer,
    apply_multi_field_answer,
    missing_paths,
    next_question_for_missing,
    next_question_advanced=None,
    auto_fill,
) -> Dict[str, Any]:

    if user_msg:
        last_paths = state.get("meta", {}).get("last_question_paths") or []
        ds = dialog_state or {}
        in_collecting_targeted = bool(last_paths) and ds.get("step") == "collecting"

        if not in_collecting_targeted:
            apply_user_message_to_facts(state, template_obj, user_msg)
            auto_fill(state["facts"])

        if last_paths:
            miss_after = missing_paths(state["facts"], template_obj, req_paths)
            pending_last_paths = [p for p in last_paths if p in miss_after]

            if len(pending_last_paths) > 1:
                ok = apply_multi_field_answer(state, template_obj, pending_last_paths, user_msg)
                if ok:
                    auto_fill(state["facts"])
            elif len(pending_last_paths) == 1:
                last_path = pending_last_paths[0]
                if last_path in miss_after:
                    ok = apply_single_field_answer(state, template_obj, last_path, user_msg)
                    if ok:
                        auto_fill(state["facts"])

    # Check missing fields
    miss = missing_paths(state["facts"], template_obj, req_paths)
    if not miss:
        return {"type": "DONE"}

    # Sort missing by supervisor's question order
    miss = _sort_missing_by_order(miss)

    # Try advanced question generator first (for QUESTION_GROUPS in validation_agent)
    if callable(next_question_advanced):
        adv = next_question_advanced(miss, dialog_state or {}, next_question_for_missing)
        if isinstance(adv, dict):
            adv_paths = adv.get("paths") or []
            adv_q = adv.get("question") or ""
            if adv_paths and adv_q:
                state.setdefault("meta", {})["last_question_paths"] = adv_paths
                out = {"type": "ASK", "question": adv_q, "paths": adv_paths}
                if adv.get("menu") is not None:
                    out["menu"] = adv.get("menu")
                return out

    # Next path by supervisor ordering
    next_path = miss[0]

    # Grouping: check if this path triggers a group
    if next_path in GROUPS:
        group_paths = GROUPS[next_path]
        paths = [p for p in group_paths if p in miss]
        if len(paths) > 1:
            state.setdefault("meta", {})["last_question_paths"] = paths
            return {
                "type": "ASK",
                "question": GROUP_QUESTIONS.get(next_path, "Donne les infos"),
                "paths": paths,
            }
        if len(paths) == 1:
            single = paths[0]
            state.setdefault("meta", {})["last_question_paths"] = [single]
            q = next_question_for_missing(single)
            return {"type": "ASK", "question": q, "paths": [single]}

    # Single question
    state.setdefault("meta", {})["last_question_paths"] = [next_path]
    q = next_question_for_missing(next_path)
    return {"type": "ASK", "question": q, "paths": [next_path]}
