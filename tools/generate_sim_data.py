#!/usr/bin/env python3
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))
SSP_CACHE = PROJECT / "sim" / "cache" / "elexon_ssp_full.json"
OUTPUT_PATH = PROJECT / "site" / "data" / "sim_data.json"

CRISIS_YEARS = {"2021", "2022"}
SIM_START = "2016-01-01"
SIM_END = "2025-12-31"


def _load_ssp():
    if not SSP_CACHE.exists():
        return []
    with open(SSP_CACHE) as f:
        return json.load(f)


def _monthly_aggregation(records):
    monthly = defaultdict(list)
    for rec in records:
        date = rec.get("settlementDate", "")
        if not (SIM_START <= date <= SIM_END):
            continue
        price = rec.get("systemSellPrice")
        if price is not None:
            monthly[date[:7]].append(float(price))

    result = []
    for month in sorted(monthly):
        prices = sorted(monthly[month])
        n = len(prices)
        p95 = prices[min(int(n * 0.95), n - 1)]
        p5 = prices[max(int(n * 0.05), 0)]
        result.append({
            "month": month,
            "mean": round(statistics.mean(prices), 2),
            "p95": round(p95, 2),
            "p5": round(p5, 2),
            "max": round(max(prices), 2),
            "min": round(min(prices), 2),
            "period_count": n,
            "is_crisis": month[:4] in CRISIS_YEARS,
        })
    return result


def _annual_aggregation(monthly, negative_hours_by_year=None):
    negative_hours_by_year = negative_hours_by_year or {}
    annual_map = defaultdict(list)
    for m in monthly:
        annual_map[m["month"][:4]].append(m)
    result = []
    for year in sorted(annual_map):
        months = annual_map[year]
        all_means = [m["mean"] for m in months]
        all_maxes = [m["max"] for m in months]
        all_mins = [m["min"] for m in months]
        all_p95s = [m["p95"] for m in months]
        result.append({
            "year": year,
            "mean": round(statistics.mean(all_means), 2),
            "p95": round(max(all_p95s), 2),
            "max": round(max(all_maxes), 2),
            "min": round(min(all_mins), 2),
            "month_count": len(months),
            "is_crisis": year in CRISIS_YEARS,
            "negative_price_hours": negative_hours_by_year.get(year, 0),
        })
    return result


def _negative_price_hours_by_year(records):
    """Half-hourly settlement periods with SSP < 0, converted to hours (0.5h/period)."""
    counts = defaultdict(int)
    for rec in records:
        date = rec.get("settlementDate", "")
        if not (SIM_START <= date <= SIM_END):
            continue
        price = rec.get("systemSellPrice")
        if price is not None and float(price) < 0:
            counts[date[:4]] += 1
    return {year: round(n * 0.5, 1) for year, n in counts.items()}


def _daily_aggregation(records):
    """Per-day mean/max/min SSP -- feeds monthly-to-daily progressive disclosure
    on the price chart (annual -> monthly -> daily is the drill-down chain).
    Also carries daily short_pct (NIV-derived market tightness) so the Weather
    tab's physics-chain panel can pair a chosen cold-snap episode's daily HDD
    against daily price and short% without a second aggregation pass."""
    daily = defaultdict(list)
    daily_niv = defaultdict(list)
    for rec in records:
        date = rec.get("settlementDate", "")
        if not (SIM_START <= date <= SIM_END):
            continue
        price = rec.get("systemSellPrice")
        if price is not None:
            daily[date].append(float(price))
        niv = rec.get("netImbalanceVolume")
        if niv is not None:
            daily_niv[date].append(float(niv))

    result = {}
    for date in sorted(daily):
        prices = daily[date]
        niv_vals = daily_niv.get(date, [])
        short_pct = (
            round(100.0 * sum(1 for v in niv_vals if v < 0) / len(niv_vals), 1)
            if niv_vals else None
        )
        result[date] = {
            "mean": round(statistics.mean(prices), 2),
            "max": round(max(prices), 2),
            "min": round(min(prices), 2),
            "short_pct": short_pct,
        }
    return result


def _peak_records(records, n=10):
    filtered = [
        r for r in records
        if SIM_START <= r.get("settlementDate", "") <= SIM_END
        and r.get("systemSellPrice") is not None
    ]
    top = sorted(filtered, key=lambda r: r["systemSellPrice"], reverse=True)[:n]
    return [
        {
            "date": r["settlementDate"],
            "period": r["settlementPeriod"],
            "start_time": r.get("startTime", ""),
            "ssp": round(r["systemSellPrice"], 2),
        }
        for r in top
    ]



def _bm_monthly_aggregation(records):
    monthly_ssp = defaultdict(list)
    monthly_sbp = defaultdict(list)
    monthly_niv = defaultdict(list)
    for rec in records:
        date = rec.get("settlementDate", "")
        if not (SIM_START <= date <= SIM_END):
            continue
        ssp = rec.get("systemSellPrice")
        sbp = rec.get("systemBuyPrice")
        niv = rec.get("netImbalanceVolume")
        month = date[:7]
        if ssp is not None:
            monthly_ssp[month].append(float(ssp))
        if sbp is not None:
            monthly_sbp[month].append(float(sbp))
        if niv is not None:
            monthly_niv[month].append(float(niv))

    result = []
    for month in sorted(monthly_ssp):
        ssp_vals = monthly_ssp[month]
        sbp_vals = monthly_sbp.get(month, [])
        niv_vals = monthly_niv.get(month, [])
        mean_ssp = statistics.mean(ssp_vals)
        mean_sbp = statistics.mean(sbp_vals) if sbp_vals else mean_ssp
        spread = round(mean_sbp - mean_ssp, 2)
        mean_niv = round(statistics.mean(niv_vals), 1) if niv_vals else 0.0
        short_pct = round(100.0 * sum(1 for v in niv_vals if v < 0) / len(niv_vals), 1) if niv_vals else 0.0
        result.append({
            "month": month,
            "mean_ssp": round(mean_ssp, 2),
            "mean_sbp": round(mean_sbp, 2),
            "spread_sbp_ssp": spread,
            "max_ssp": round(max(ssp_vals), 2),
            "max_sbp": round(max(sbp_vals), 2) if sbp_vals else None,
            "mean_niv_mwh": mean_niv,
            "short_pct": short_pct,
            "is_crisis": month[:4] in CRISIS_YEARS,
        })
    return result


def _gas_monthly_aggregation():
    """Monthly mean NBP gas price GBP/MWh -- overlay series for the power price
    chart (PRICES -> MARKET rebuild: any pair of signals can be compared)."""
    try:
        from sim.gas_prices_history import load_nbp_history
    except ImportError:
        return {}
    records = load_nbp_history()
    monthly = defaultdict(list)
    for rec in records:
        date = rec.get("settlementDate", "")
        if not (SIM_START <= date <= SIM_END):
            continue
        price = rec.get("systemSellPrice")
        if price is not None:
            monthly[date[:7]].append(float(price))
    return {month: round(statistics.mean(vals), 2) for month, vals in monthly.items()}


def generate():
    records = _load_ssp()
    if not records:
        print("WARNING: SSP cache not found or empty -- writing empty sim_data.json")
        payload = {"monthly": [], "annual": [], "peak_records": [], "metadata": {"total_records": 0}}
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(payload, indent=2))
        return False

    monthly = _monthly_aggregation(records)
    negative_hours_by_year = _negative_price_hours_by_year(records)
    annual = _annual_aggregation(monthly, negative_hours_by_year)
    peaks = _peak_records(records)
    bm = _bm_monthly_aggregation(records)
    daily = _daily_aggregation(records)
    gas_monthly = _gas_monthly_aggregation()

    short_pct_by_month = {b["month"]: b["short_pct"] for b in bm}
    for m in monthly:
        m["gas_mean"] = gas_monthly.get(m["month"])
        m["short_pct"] = short_pct_by_month.get(m["month"])

    dates = sorted(r["settlementDate"] for r in records if "settlementDate" in r)
    payload = {
        "monthly": monthly,
        "annual": annual,
        "peak_records": peaks,
        "bm": bm,
        "daily": daily,
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_records": len(records),
            "period_from": dates[0] if dates else "",
            "period_to": dates[-1] if dates else "",
            "crisis_years": sorted(CRISIS_YEARS),
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2))
    print("Generated", OUTPUT_PATH, "({} months, {} years, {} peak records, {} days)".format(
        len(monthly), len(annual), len(peaks), len(daily)))
    return True


if __name__ == "__main__":
    generate()
