import json, statistics, datetime as dt
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SSP_CACHE = PROJECT / "sim" / "cache" / "elexon_ssp_full.json"
PRICE_FEED = PROJECT / "docs" / "market_data" / "price_feed.json"

def _load_ssp_records():
    try: return json.loads(SSP_CACHE.read_text())
    except: return []

def _load_price_feed_records():
    try:
        feed = json.loads(PRICE_FEED.read_text())
        return [{"settlementDate": p["period"][:10], "systemSellPrice": p["price_gbp_per_mwh"]}
                for p in feed.get("prices", []) if p.get("fuel") == "electricity"]
    except: return []

def _best_records(): return _load_ssp_records() or _load_price_feed_records()

def _effective_as_of(records, requested):
    all_dates = sorted(set(r["settlementDate"] for r in records))
    if requested and requested in all_dates: return requested
    if requested:
        before = [d for d in all_dates if d <= requested]
        return before[-1] if before else all_dates[-1]
    return all_dates[-1]

def fetch_spot_elec(as_of_date=None):
    from sim.forward_curve import _ewma
    records = _best_records()
    if not records: raise ValueError("No price records available")
    actual = _effective_as_of(records, as_of_date)
    end = dt.date.fromisoformat(actual)
    start = end - dt.timedelta(days=90)
    filtered = [r for r in records if start <= dt.date.fromisoformat(r["settlementDate"]) <= end] or records
    daily = {}
    for r in filtered: daily.setdefault(r["settlementDate"], []).append(r["systemSellPrice"])
    daily_means = [statistics.mean(v) for _, v in sorted(daily.items())]
    return round(_ewma(daily_means, min(30, len(daily_means))), 2)

def fetch_spot_gas(as_of_date=None):
    try:
        feed = json.loads(PRICE_FEED.read_text())
        gas = [p for p in feed.get("prices", []) if p.get("fuel") == "gas"]
        if gas:
            cutoff = as_of_date or "9999"
            rel = [p for p in gas if p["period"][:10] <= cutoff] or gas
            last30 = sorted(rel, key=lambda x: x["period"])[-30:]
            return round(statistics.mean(p["price_gbp_per_mwh"] for p in last30), 2)
    except: pass
    return round(fetch_spot_elec(as_of_date) * 0.30, 2)

def build_live_forward_price(as_of_date=None, fuel="electricity"):
    if fuel == "gas":
        return round(fetch_spot_gas(as_of_date) * 1.05, 2)
    from sim.forward_curve import generate_forward_price
    records = _best_records()
    if not records: raise ValueError("No SSP records available")
    actual = _effective_as_of(records, as_of_date)
    return round(generate_forward_price(
        acquisition_date=actual, system_price_records=records,
        contract_length_months=12, lookback_days=90, fuel=fuel), 2)

def get_market_summary(as_of_date=None):
    records = _best_records()
    actual = _effective_as_of(records, as_of_date) if records else None
    return {
        "as_of_date": actual,
        "elec_spot_gbp_per_mwh": fetch_spot_elec(as_of_date),
        "gas_spot_gbp_per_mwh": fetch_spot_gas(as_of_date),
        "elec_12m_forward_gbp_per_mwh": build_live_forward_price(as_of_date, "electricity"),
        "gas_12m_forward_gbp_per_mwh": build_live_forward_price(as_of_date, "gas"),
    }
