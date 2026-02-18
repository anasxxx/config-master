def enrich_with_hps(data: dict) -> dict:
    # Stub: simule les données internes HPS (backend only)
    data["hps"] = {
        "segment": "SME",
        "offer": "STANDARD",
        "internal_code": "HPS-123"
    }
    return data
