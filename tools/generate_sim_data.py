#!/usr/bin/env python3
import json
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
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


def _annual_aggregation(monthly):
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
        })
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


def generate():
    records = _load_ssp()
    if not records:
        print("WARNING: SSP cache not found or empty -- writing empty sim_data.json")
        payload = {"monthly": [], "annual": [], "peak_records": [], "metadata": {"total_records": 0}}
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(payload, indent=2))
        return False

    monthly = _monthly_aggregation(records)
    annual = _annual_aggregation(monthly)
    peaks = _peak_records(records)

    dates = sorted(r["settlementDate"] for r in records if "settlementDate" in r)
    payload = {
        "monthly": monthly,
        "annual": annual,
        "peak_records": peaks,
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
    print("Generated", OUTPUT_PATH, "({} months, {} years, {} peak records)".format(
        len(monthly), len(annual), len(peaks)))
    return True


if __name__ == "__main__":
    generate()
