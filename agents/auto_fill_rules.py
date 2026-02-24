import csv
from pathlib import Path
import pycountry
from agents.prompts import PROMPT_AUTOFILL
# PROMPT_AUTOFILL = spec. L’autofill reste code-only.
BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "data" / "country_currency.csv"


ALIASES = {
    "maroc": "morocco",
    "royaume uni": "united kingdom",
    "uk": "united kingdom",
    "angleterre": "united kingdom",
    "etats unis": "united states",
    "états unis": "united states",
    "usa": "united states",
}


ALPHA2_TO_CURRENCY_FALLBACK = {
    "MA": "MAD",
    "FR": "EUR",
    "CH": "CHF",
    "GB": "GBP",
    "US": "USD",
}

def resolve_country_alpha2(text: str) -> str | None:
    if not text:
        return None
    q = text.strip().lower()
    q = ALIASES.get(q, q)

    
    if len(q) == 2 and q.isalpha():
        c = pycountry.countries.get(alpha_2=q.upper())
        return c.alpha_2 if c else None

    try:
        res = pycountry.countries.search_fuzzy(q)
        return res[0].alpha_2 if res else None
    except Exception:
        return None

def _load_currency_csv_by_alpha2() -> dict:
    """
    Lit country_currency.csv et construit un mapping:
    alpha2 -> currency
    En utilisant pycountry pour convertir 'country' (nom) -> alpha2
    """
    mapping = {}
    if not CSV_FILE.exists():
        return mapping

    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            country_txt = (row.get("country") or "").strip()
            currency = (row.get("currency") or "").strip().upper()
            if not country_txt or not currency:
                continue

            a2 = resolve_country_alpha2(country_txt)
            if a2:
                mapping[a2] = currency
    return mapping


ALPHA2_TO_CURRENCY_CSV = _load_currency_csv_by_alpha2()

def auto_fill(facts: dict) -> None:
    bank = facts.get("bank", {})
    if not isinstance(bank, dict):
        return

    country = bank.get("country")
    if not country:
        return

    
    if bank.get("currency"):
        return

    
    a2 = bank.get("country_alpha2")
    if not a2:
        a2 = resolve_country_alpha2(country)
        if a2:
            bank["country_alpha2"] = a2

    if not a2:
        return

    
    cur = ALPHA2_TO_CURRENCY_CSV.get(a2.upper())

    
    if not cur:
        cur = ALPHA2_TO_CURRENCY_FALLBACK.get(a2.upper())

    if cur:
        bank["currency"] = cur
        print("AUTO_FILL ok")