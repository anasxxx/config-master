import csv
import json
import os
import re
import unicodedata
from pathlib import Path
try:
    import pycountry
except Exception:
    pycountry = None
try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None
from agents.prompts import PROMPT_AUTOFILL
from agents.value_store import get_value, set_value
from agents.powercard_constraints import should_block_autofill
# PROMPT_AUTOFILL = spec. L’autofill reste code-only.
BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "data" / "country_currency.csv"
CITY_JSON_FILE = BASE_DIR / "data" / "code_postal_ville.json"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017").strip()
MONGO_DB = os.getenv("MONGO_DB", "geo_ref").strip()
MONGO_CITY_COLLECTION = os.getenv("MONGO_CITY_COLLECTION", "cities").strip()
MONGO_REGION_COLLECTION = os.getenv("MONGO_REGION_COLLECTION", "regions").strip()
MONGO_COUNTRY_COLLECTION = os.getenv("MONGO_COUNTRY_COLLECTION", "countries").strip()


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
        if pycountry is None:
            return q.upper()
        c = pycountry.countries.get(alpha_2=q.upper())
        return c.alpha_2 if c else None

    try:
        if pycountry is None:
            return None
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


def _norm_loc(s: str) -> str:
    t = (s or "").strip().lower()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = t.replace("_", " ")
    t = t.replace("-", " ")
    t = " ".join(t.split())
    return t


def _display_region_name(region_key: str) -> str:
    txt = (region_key or "").strip().replace("_", " ").replace("-", " ")
    return " ".join(w.capitalize() for w in txt.split())


def _load_city_lookup() -> dict:
    out = {}
    if not CITY_JSON_FILE.exists():
        return out
    try:
        with open(CITY_JSON_FILE, "r", encoding="utf-8-sig") as f:
            payload = json.load(f)
    except Exception:
        return out

    if not isinstance(payload, dict):
        return out

    for region_key, region_obj in payload.items():
        if not isinstance(region_obj, dict):
            continue
        region_code = str(region_obj.get("region_code") or "").strip()
        cities = region_obj.get("cities") or {}
        if not isinstance(cities, dict):
            continue
        for city_name, city_code in cities.items():
            city_norm = _norm_loc(str(city_name))
            if not city_norm:
                continue
            out[city_norm] = {
                "city_code": str(city_code).strip(),
                "region": _display_region_name(str(region_key)),
                "region_code": region_code,
            }
    return out


CITY_LOOKUP = _load_city_lookup()
_MONGO_CLIENT = None
_AUTO_MONGO_DB = None
_AUTO_MONGO_COLLECTION = None
_AUTO_GEO_DB = None


def _mongo_enabled() -> bool:
    return bool(MONGO_URI and MongoClient is not None)


def _mongo_get_collection_for_scan():
    global _MONGO_CLIENT
    if not _mongo_enabled():
        return None
    try:
        if _MONGO_CLIENT is None:
            _MONGO_CLIENT = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
        return _MONGO_CLIENT
    except Exception:
        return None


def _candidate_db_names(client) -> list[str]:
    try:
        names = client.list_database_names()
    except Exception:
        return []
    return [d for d in names if d not in {"admin", "local", "config"}]


def _pick_existing_collection(col_names: list[str], preferred: list[str], keywords: list[str]) -> str | None:
    by_lower = {c.lower(): c for c in col_names}
    for wanted in preferred:
        key = (wanted or "").strip().lower()
        if key and key in by_lower:
            return by_lower[key]
    for col in col_names:
        cl = col.lower()
        if any(k in cl for k in keywords):
            return col
    return None


def _resolve_geo_db_name():
    global _AUTO_GEO_DB

    client = _mongo_get_collection_for_scan()
    if client is None:
        return None

    if MONGO_DB:
        try:
            if MONGO_DB in client.list_database_names():
                _AUTO_GEO_DB = MONGO_DB
                return _AUTO_GEO_DB
        except Exception:
            return None

    if _AUTO_GEO_DB:
        return _AUTO_GEO_DB

    best_db = None
    best_score = -1
    for dbn in _candidate_db_names(client):
        try:
            col_names = client[dbn].list_collection_names()
        except Exception:
            continue
        low = {c.lower() for c in col_names}
        score = 0
        if "cities" in low or (MONGO_CITY_COLLECTION and MONGO_CITY_COLLECTION.lower() in low):
            score += 5
        if "regions" in low or (MONGO_REGION_COLLECTION and MONGO_REGION_COLLECTION.lower() in low):
            score += 3
        if "countries" in low or (MONGO_COUNTRY_COLLECTION and MONGO_COUNTRY_COLLECTION.lower() in low):
            score += 2
        if score > best_score:
            best_db, best_score = dbn, score

    if best_db and best_score > 0:
        _AUTO_GEO_DB = best_db
        return _AUTO_GEO_DB
    return None


def _mongo_get_db():
    client = _mongo_get_collection_for_scan()
    if client is None:
        return None
    db_name = _resolve_geo_db_name()
    if not db_name:
        return None
    try:
        return client[db_name]
    except Exception:
        return None


def _resolve_mongo_target():
    global _AUTO_MONGO_DB, _AUTO_MONGO_COLLECTION

    db = _mongo_get_db()
    if db is None:
        return None, None

    if MONGO_DB and MONGO_CITY_COLLECTION:
        try:
            if MONGO_CITY_COLLECTION in db.list_collection_names():
                return MONGO_DB, MONGO_CITY_COLLECTION
        except Exception:
            pass

    if _AUTO_MONGO_DB and _AUTO_MONGO_COLLECTION:
        return _AUTO_MONGO_DB, _AUTO_MONGO_COLLECTION

    try:
        col_names = db.list_collection_names()
    except Exception:
        return None, None

    chosen = _pick_existing_collection(
        col_names,
        [MONGO_CITY_COLLECTION, "cities", "city", MONGO_REGION_COLLECTION, "regions"],
        ["city", "ville", "region"],
    )
    if chosen:
        _AUTO_MONGO_DB, _AUTO_MONGO_COLLECTION = db.name, chosen
        return _AUTO_MONGO_DB, _AUTO_MONGO_COLLECTION
    return None, None


def _mongo_get_collection():
    client = _mongo_get_collection_for_scan()
    if client is None:
        return None
    db_name, col_name = _resolve_mongo_target()
    if not db_name or not col_name:
        return None
    try:
        db = client[db_name]
        return db[col_name]
    except Exception:
        return None


def _doc_get_first(doc: dict, keys: list[str]) -> str:
    for k in keys:
        v = doc.get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return ""


def _clean_geo_value(value: str) -> str:
    s = str(value or "").strip()
    if not s:
        return ""
    if s.lower() in {"null", "none", "nan", "n/a"}:
        return ""
    return s


def _normalize_city_code(value: str) -> str:
    s = _clean_geo_value(value).upper()
    if not s:
        return ""
    if re.fullmatch(r"[A-Z0-9]{1,5}", s):
        return s
    return ""


def _normalize_region_code(value: str) -> str:
    s = _clean_geo_value(value).upper()
    if not s:
        return ""
    if re.fullmatch(r"[A-Z0-9]{1,3}", s):
        return s
    return ""


def _doc_country_tokens(doc: dict) -> set[str]:
    out = set()
    if not isinstance(doc, dict):
        return out
    keys = [
        "country_code",
        "code_country",
        "country_alpha2",
        "alpha2",
        "iso2",
        "iso_alpha",
        "country",
        "country_name",
        "country_name_short",
        "name",
    ]
    for k in keys:
        v = doc.get(k)
        if isinstance(v, dict):
            for inner in ("code", "country_code", "alpha2", "iso2", "name", "country_name", "label"):
                val = _clean_geo_value(v.get(inner))
                if val:
                    out.add(_norm_loc(val))
        else:
            val = _clean_geo_value(v)
            if val:
                out.add(_norm_loc(val))

    alt_names = doc.get("alternate_names")
    if isinstance(alt_names, list):
        for item in alt_names:
            if isinstance(item, dict):
                nm = _clean_geo_value(item.get("name"))
                if nm:
                    out.add(_norm_loc(nm))
            else:
                nm = _clean_geo_value(item)
                if nm:
                    out.add(_norm_loc(nm))
    return out


def _collect_country_tokens(country_value: str, countries_coll=None) -> set[str]:
    out = set()
    raw = _clean_geo_value(country_value)
    if not raw:
        return out
    out.add(_norm_loc(raw))
    if raw.isdigit():
        out.add(_norm_loc(raw.zfill(3)))

    alpha2 = resolve_country_alpha2(raw)
    if alpha2:
        out.add(_norm_loc(alpha2))
        if pycountry is not None:
            try:
                c = pycountry.countries.get(alpha_2=alpha2.upper())
                if c:
                    for name_key in ("name", "official_name", "common_name"):
                        nm = _clean_geo_value(getattr(c, name_key, "") or "")
                        if nm:
                            out.add(_norm_loc(nm))
            except Exception:
                pass

    if countries_coll is None:
        return out

    c_re = {"$regex": f"^{re.escape(raw)}$", "$options": "i"}
    query = {
        "$or": [
            {"country": c_re},
            {"country_name": c_re},
            {"country_name_fr": c_re},
            {"country_name_short": c_re},
            {"country_short_name": c_re},
            {"country_short_name_fr": c_re},
            {"name": c_re},
            {"label": c_re},
            {"alpha2": c_re},
            {"iso2": c_re},
            {"iso_alpha": c_re},
            {"country_iso_alpha3": c_re},
            {"country_code": c_re},
            {"code_country": c_re},
            {"alternate_names.name": c_re},
        ]
    }
    projection = {
        "_id": 0,
        "country": 1,
        "country_name": 1,
        "country_name_fr": 1,
        "country_name_short": 1,
        "country_short_name": 1,
        "country_short_name_fr": 1,
        "name": 1,
        "label": 1,
        "country_code": 1,
        "code_country": 1,
        "alpha2": 1,
        "iso2": 1,
        "iso_alpha": 1,
        "country_iso_alpha3": 1,
        "country_alpha2": 1,
        "alternate_names": 1,
    }
    try:
        docs = list(countries_coll.find(query, projection).limit(20))
    except Exception:
        docs = []

    for doc in docs:
        for key in projection:
            if key == "_id":
                continue
            raw_val = doc.get(key)
            if isinstance(raw_val, list):
                for item in raw_val:
                    if isinstance(item, dict):
                        nm = _clean_geo_value(item.get("name"))
                        if nm:
                            out.add(_norm_loc(nm))
                    else:
                        vv = _clean_geo_value(item)
                        if vv:
                            out.add(_norm_loc(vv))
                continue
            val = _clean_geo_value(raw_val)
            if val:
                out.add(_norm_loc(val))
    return out


def _doc_matches_country(doc: dict, country_tokens: set[str]) -> bool:
    if not country_tokens:
        return True
    doc_tokens = _doc_country_tokens(doc)
    if not doc_tokens:
        # Some datasets keep only city/region data in cities collection.
        return True
    return bool(country_tokens & doc_tokens)


def _country_match_score(doc: dict, country_tokens: set[str]) -> int:
    if not country_tokens:
        return 0
    return len(_doc_country_tokens(doc) & country_tokens)


def _extract_city_match_from_doc(doc: dict) -> dict:
    out = {}
    region_obj = doc.get("region") if isinstance(doc.get("region"), dict) else {}

    city_code = _normalize_city_code(
        _doc_get_first(doc, ["city_code", "code_ville", "postal_code", "code_postal", "zip", "code"])
    )
    region = _clean_geo_value(_doc_get_first(doc, ["region_name", "nom_region"]))
    if not region:
        region = _clean_geo_value(_doc_get_first(doc, ["region", "name"]))
    if not region:
        region = _clean_geo_value(_doc_get_first(region_obj, ["name", "label", "region_name"]))

    region_code = _normalize_region_code(_doc_get_first(doc, ["region_code", "code_region"]))
    if not region_code:
        region_code = _normalize_region_code(_doc_get_first(region_obj, ["code", "region_code", "code_region"]))

    if city_code:
        out["city_code"] = city_code
    if region:
        out["region"] = region
    if region_code:
        out["region_code"] = region_code
    return out


def _city_doc_quality_score(doc: dict) -> int:
    score = 0
    region_name = _clean_geo_value(_doc_get_first(doc, ["region_name", "nom_region", "region"]))
    if region_name:
        score += 30

    city_code = _clean_geo_value(_doc_get_first(doc, ["city_code", "code_ville", "postal_code", "code_postal", "zip"]))
    if city_code:
        score += 8
        if city_code.isdigit() and len(city_code) <= 2:
            # Often legacy/ambiguous entries in imported datasets.
            score -= 6

    src = _clean_geo_value(doc.get("source") or "").lower()
    if src:
        if "manual" in src or "official" in src or "officiel" in src:
            score += 20
        if "xlsx" in src:
            score -= 2
    return score


def _resolve_region_label(regions_coll, region_code: str, country_tokens: set[str]) -> str:
    region_code = _normalize_region_code(region_code)
    if regions_coll is None or not region_code:
        return ""
    code_query = {
        "$or": [
            {"region_code": region_code},
            {"code_region": region_code},
            {"code": region_code},
        ]
    }
    projection = {
        "_id": 0,
        "region": 1,
        "region_name": 1,
        "nom_region": 1,
        "name": 1,
        "label": 1,
        "region_code": 1,
        "code_region": 1,
        "country": 1,
        "country_name": 1,
        "country_code": 1,
        "code_country": 1,
        "alpha2": 1,
        "iso2": 1,
    }
    try:
        docs = list(regions_coll.find(code_query, projection).limit(20))
    except Exception:
        docs = []

    ranked = sorted(docs, key=lambda d: _country_match_score(d, country_tokens), reverse=True)
    for doc in ranked:
        if not _doc_matches_country(doc, country_tokens):
            continue
        label = _clean_geo_value(_doc_get_first(doc, ["region_name", "nom_region", "region", "name", "label"]))
        if label:
            return label
    return ""


def _lookup_city_from_geo_collections(city_value: str, country_value: str | None = None) -> dict | None:
    db = _mongo_get_db()
    if db is None:
        return None

    try:
        col_names = db.list_collection_names()
    except Exception:
        return None

    city_col_name = _pick_existing_collection(
        col_names,
        [MONGO_CITY_COLLECTION, "cities", "city"],
        ["city", "ville"],
    )
    if not city_col_name:
        return None

    region_col_name = _pick_existing_collection(
        col_names,
        [MONGO_REGION_COLLECTION, "regions", "region"],
        ["region"],
    )
    country_col_name = _pick_existing_collection(
        col_names,
        [MONGO_COUNTRY_COLLECTION, "countries", "country"],
        ["country"],
    )

    city_coll = db[city_col_name]
    regions_coll = db[region_col_name] if region_col_name else None
    countries_coll = db[country_col_name] if country_col_name else None

    country_tokens = _collect_country_tokens(country_value or "", countries_coll)

    city_raw = _clean_geo_value(city_value)
    if not city_raw:
        return None
    city_norm = _norm_loc(city_raw)
    city_re = {"$regex": f"^{re.escape(city_raw)}$", "$options": "i"}
    city_query = {
        "$or": [
            {"city": city_re},
            {"city_name": city_re},
            {"city_name_normalized": city_norm},
            {"ville": city_re},
            {"name": city_re},
            {"alternate_names.name": city_re},
        ]
    }
    projection = {
        "_id": 0,
        "city": 1,
        "city_name": 1,
        "city_name_normalized": 1,
        "ville": 1,
        "name": 1,
        "alternate_names": 1,
        "city_code": 1,
        "code_ville": 1,
        "postal_code": 1,
        "code_postal": 1,
        "zip": 1,
        "region": 1,
        "region_name": 1,
        "nom_region": 1,
        "region_code": 1,
        "code_region": 1,
        "country": 1,
        "country_name": 1,
        "country_name_short": 1,
        "country_code": 1,
        "code_country": 1,
        "country_alpha2": 1,
        "alpha2": 1,
        "iso2": 1,
        "iso_alpha": 1,
    }
    try:
        docs = list(city_coll.find(city_query, projection).limit(60))
    except Exception:
        docs = []
    if not docs:
        return None

    candidates = [d for d in docs if _doc_matches_country(d, country_tokens)]
    if not candidates:
        candidates = docs

    candidates = sorted(
        candidates,
        key=lambda d: (_country_match_score(d, country_tokens), _city_doc_quality_score(d)),
        reverse=True,
    )
    best = candidates[0]
    match = _extract_city_match_from_doc(best)

    # If the best row has no valid city_code for strict PowerCard format,
    # keep region from best row but reuse a valid city_code from another row.
    if not match.get("city_code"):
        for alt in candidates:
            alt_code = _normalize_city_code(
                _doc_get_first(alt, ["city_code", "code_ville", "postal_code", "code_postal", "zip", "code"])
            )
            if alt_code:
                match["city_code"] = alt_code
                break

    if not match.get("region") and match.get("region_code"):
        reg_name = _resolve_region_label(regions_coll, match.get("region_code") or "", country_tokens)
        if reg_name:
            match["region"] = reg_name

    return match or None


def _lookup_city_from_legacy_collection(city_value: str, country_tokens: set[str]) -> dict | None:
    coll = _mongo_get_collection()
    if coll is None:
        return None

    city_raw = _clean_geo_value(city_value)
    if not city_raw:
        return None
    city_norm = _norm_loc(city_raw)
    city_re = {"$regex": f"^{re.escape(city_raw)}$", "$options": "i"}

    flat_query = {
        "$or": [
            {"city": city_re},
            {"city_name": city_re},
            {"city_name_normalized": city_norm},
            {"ville": city_re},
            {"name": city_re},
            {"alternate_names.name": city_re},
        ]
    }
    projection = {
        "_id": 0,
        "city": 1,
        "city_name": 1,
        "city_name_normalized": 1,
        "ville": 1,
        "name": 1,
        "alternate_names": 1,
        "city_code": 1,
        "code_ville": 1,
        "postal_code": 1,
        "code_postal": 1,
        "zip": 1,
        "region": 1,
        "region_name": 1,
        "nom_region": 1,
        "region_code": 1,
        "code_region": 1,
        "country": 1,
        "country_name": 1,
        "country_name_short": 1,
        "country_code": 1,
        "code_country": 1,
        "country_alpha2": 1,
        "alpha2": 1,
        "iso2": 1,
        "iso_alpha": 1,
        "cities": 1,
    }
    try:
        docs = list(coll.find(flat_query, projection).limit(60))
    except Exception:
        docs = []

    flat_matches = [d for d in docs if _doc_matches_country(d, country_tokens)]
    if flat_matches:
        flat_matches = sorted(flat_matches, key=lambda d: _country_match_score(d, country_tokens), reverse=True)
        out = _extract_city_match_from_doc(flat_matches[0])
        if out:
            return out

    nested_query = {
        "$or": [
            {"cities.name": city_re},
            {"cities.city": city_re},
            {"cities.ville": city_re},
        ]
    }
    try:
        rdocs = list(
            coll.find(
                nested_query,
                {
                    "_id": 0,
                    "region": 1,
                    "region_name": 1,
                    "nom_region": 1,
                    "region_code": 1,
                    "code_region": 1,
                    "country": 1,
                    "country_name": 1,
                    "country_code": 1,
                    "code_country": 1,
                    "alpha2": 1,
                    "iso2": 1,
                    "cities": 1,
                },
            ).limit(60)
        )
    except Exception:
        rdocs = []

    city_norm = _norm_loc(city_raw)
    ranked_rdocs = sorted(rdocs, key=lambda d: _country_match_score(d, country_tokens), reverse=True)
    for rdoc in ranked_rdocs:
        if not _doc_matches_country(rdoc, country_tokens):
            continue
        cities = rdoc.get("cities") or []
        target = None
        if isinstance(cities, list):
            for c in cities:
                if not isinstance(c, dict):
                    continue
                cname = _clean_geo_value(c.get("name") or c.get("city") or c.get("ville"))
                if cname and _norm_loc(cname) == city_norm:
                    target = c
                    break
        out = {}
        if isinstance(target, dict):
            city_code = _normalize_city_code(
                _doc_get_first(target, ["postal_code", "code_postal", "city_code", "code_ville", "zip", "code"])
            )
            if city_code:
                out["city_code"] = city_code
        region = _clean_geo_value(_doc_get_first(rdoc, ["region", "region_name", "nom_region"]))
        region_code = _normalize_region_code(_doc_get_first(rdoc, ["region_code", "code_region"]))
        if region:
            out["region"] = region
        if region_code:
            out["region_code"] = region_code
        if out:
            return out
    return None


def _lookup_city_from_mongo(city_value: str, country_value: str | None = None) -> dict | None:
    match = _lookup_city_from_geo_collections(city_value, country_value)
    if match:
        return match
    country_tokens = _collect_country_tokens(country_value or "", countries_coll=None)
    return _lookup_city_from_legacy_collection(city_value, country_tokens)

def auto_fill(facts: dict, meta: dict | None = None) -> None:
    bank = facts.get("bank", {})
    if not isinstance(bank, dict):
        return

    # 1) Autofill currency from country/country_alpha2.
    country = get_value(facts, "bank.country")
    if country and not get_value(facts, "bank.currency"):
        a2 = get_value(facts, "bank.country_alpha2")
        if not a2:
            a2 = resolve_country_alpha2(country)
            if a2:
                if not should_block_autofill("bank.country_alpha2", meta or {}):
                    set_value(facts, "bank.country_alpha2", a2, source="autofill", confidence=1.0)

        if a2:
            cur = ALPHA2_TO_CURRENCY_CSV.get(a2.upper())
            if not cur:
                cur = ALPHA2_TO_CURRENCY_FALLBACK.get(a2.upper())
            if cur:
                if not should_block_autofill("bank.currency", meta or {}):
                    set_value(facts, "bank.currency", cur, source="autofill", confidence=1.0)

    # 2) Autofill city_code + region + region_code from city dictionary.
    city_val = get_value(facts, "bank.agencies.0.city")
    if not city_val:
        return

    city_str = str(city_val).strip()
    city_norm = _norm_loc(city_str)
    match = _lookup_city_from_mongo(city_str, str(country or ""))
    if not match:
        match = CITY_LOOKUP.get(city_norm)
    if not match:
        return

    if not get_value(facts, "bank.agencies.0.city_code") and match.get("city_code"):
        if not should_block_autofill("bank.agencies.0.city_code", meta or {}):
            set_value(
                facts,
                "bank.agencies.0.city_code",
                match["city_code"],
                source="autofill",
                confidence=1.0,
            )

    if not get_value(facts, "bank.agencies.0.region") and match.get("region"):
        if not should_block_autofill("bank.agencies.0.region", meta or {}):
            set_value(
                facts,
                "bank.agencies.0.region",
                match["region"],
                source="autofill",
                confidence=1.0,
            )

    if not get_value(facts, "bank.agencies.0.region_code") and match.get("region_code"):
        if not should_block_autofill("bank.agencies.0.region_code", meta or {}):
            set_value(
                facts,
                "bank.agencies.0.region_code",
                match["region_code"],
                source="autofill",
                confidence=1.0,
            )
