"""
Quick payload inspection — no network, no DB.
Builds a complete mock state, maps it to the BankReq payload,
and prints what would be sent to the Spring Boot backend.

Run:
    cd nv-ai-agent-hps
    python test_payload.py
"""
import json
from agents.bank_pipeline import map_facts_to_bank_req

MOCK_STATE = {
    "facts": {
        "bank": {
            "name": "Banque Test",
            "country": "Maroc",
            "currency": "MAD",
            "bank_code": "BTK",
            "resources": ["MCD_MDS", "HOST_BANK"],
            "agencies": [
                {
                    "agency_name": "Agence Centre",
                    "agency_code": "001",
                    "city": "Casablanca",
                    "city_code": "01",
                    "region": "Grand Casablanca",
                    "region_code": "10",
                }
            ],
        },
        "cards": [
            {
                "card_info": {
                    "bin": "445555",
                    "plastic_type": "PVC",
                    "card_description": "Carte Classic",
                    "product_type": "DEBIT",
                    "product_code": "CLS",   # 3 chars
                    "pvk_index": "1",
                    "service_code": "101",
                    "network": "VISA",        # must be PL/SQL-compatible
                    "expiration": "36",
                    "renewal_option": "A",    # 1 char
                    "pre_expiration": "3",    # 1 char
                },
                "card_range": {
                    "start_range": "4455550000000000",
                    "end_range":   "4455559999999999",
                },
                "fees": {
                    "fee_description": "Frais Classic",
                    "billing_event": "A",     # 1 char: A=Anniversaire
                    "grace_period": 30,
                    "billing_period": "Y",    # 1 char: Y=Annuel
                    "registration_fee": "50",
                    "periodic_fee": "10",
                    "replacement_fee": "25",
                    "pin_recalculation_fee": "5",
                },
                "services": {
                    "enabled": ["Retrait", "Achats", "E-commerce", "Consultation Solde"]
                },
                "limits": {
                    "selected_limit_types": ["DEFAULT"],
                    "by_type": {
                        "DEFAULT": {
                            "domestic": {
                                "daily_amount": "5000",
                                "weekly_amount": "20000",
                                "monthly_amount": "80000",
                            },
                            "international": {
                                "daily_amount": "2000",
                                "weekly_amount": "10000",
                                "monthly_amount": "40000",
                            },
                        }
                    },
                },
            }
        ],
    }
}


def main():
    payload = map_facts_to_bank_req(MOCK_STATE)
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    # Quick field checks
    print("\n--- VALIDATION CHECKS ---")
    card = payload["cardProducts"][0]

    pc_info = card["info"]["productCode"]
    pc_svc  = card["services"]["productCode"]
    pc_lim  = card["limits"][0]["productCode"]
    print(f"info.productCode    = '{pc_info}' (len={len(pc_info)}, expected 3)")
    print(f"service.productCode = '{pc_svc}'  (len={len(pc_svc)}, expected 3)")
    print(f"limit.productCode   = '{pc_lim}'  (len={len(pc_lim)}, expected 4 = 'L'+3)")

    sub = card["fees"]["subscriptionAmount"]
    print(f"subscriptionAmount  = {repr(sub)} (type={type(sub).__name__}, expected str)")

    fees_evt = card["fees"]["cardFeesBillingEvt"]
    fees_per = card["fees"]["cardFeesBillingPeriod"]
    print(f"billingEvt          = '{fees_evt}' (len={len(fees_evt)}, expected 1)")
    print(f"billingPeriod       = '{fees_per}' (len={len(fees_per)}, expected 1)")

    tranche_min = card["info"]["trancheMin"]
    tranche_max = card["info"]["trancheMax"]
    print(f"trancheMin          = '{tranche_min}'")
    print(f"trancheMax          = '{tranche_max}'")

    assert len(pc_info) == 3, f"FAIL: info.productCode should be 3 chars, got {len(pc_info)}"
    assert len(pc_svc)  == 3, f"FAIL: service.productCode should be 3 chars, got {len(pc_svc)}"
    assert len(pc_lim)  == 4, f"FAIL: limit.productCode should be 4 chars, got {len(pc_lim)}"
    assert isinstance(sub, str), f"FAIL: subscriptionAmount should be str, got {type(sub).__name__}"
    assert len(fees_evt) == 1, f"FAIL: billingEvt should be 1 char, got {len(fees_evt)}"
    assert len(fees_per) == 1, f"FAIL: billingPeriod should be 1 char, got {len(fees_per)}"
    print("\nAll checks PASSED [OK]")


if __name__ == "__main__":
    main()
