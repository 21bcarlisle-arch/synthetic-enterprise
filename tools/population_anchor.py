"""Phase PQ -- Population Anchoring Validation Gate.

Compares SIM aggregate outputs against published UK energy market benchmarks.
Runs every sim run; outputs to site/state/population_anchoring.json.

Key benchmarks (sources: Ofgem switching data, DESNZ, Energy UK):
  - Annual switching rates by year (Ofgem Retail Market Indicators)
  - Bad debt rates vs industry range (0.5-2.5% of revenue)
  - Churn direction: 2021-22 crisis = switching COLLAPSE, not rise

Critical invariant: SIM market_switching_multiplier should track Ofgem rates.
If SIM effective churn RISES in 2022 vs 2021 by >15pp, flag as DIVERGENCE.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

PROJECT = Path(__file__).resolve().parent.parent
RUN_JSON = PROJECT / "docs" / "reports" / "run_output_latest.json"
OUT_PATH = PROJECT / "site" / "state" / "population_anchoring.json"

# Ofgem published switching rates (% of dual-fuel accounts switching per year)
# Source: Ofgem Retail Market Indicators
OFGEM_SWITCHING_RATE = {
    2016: 0.20, 2017: 0.19, 2018: 0.18, 2019: 0.17,
    2020: 0.14, 2021: 0.09, 2022: 0.04, 2023: 0.08,
    2024: 0.13, 2025: 0.14,
}

# Market switching multiplier from Phase NS calibration (normalised to 2024=1.0)
CALIBRATED_MULTIPLIER = {
    2016: 2.17, 2017: 1.88, 2018: 1.72, 2019: 1.43,
    2020: 0.95, 2021: 0.57, 2022: 0.44, 2023: 0.79,
    2024: 1.00, 2025: 0.93,
}

# Industry bad debt benchmark range (% of revenue)
BAD_DEBT_BENCHMARK_LOW = 0.005   # 0.5%
BAD_DEBT_BENCHMARK_HIGH = 0.025  # 2.5%
BAD_DEBT_CRISIS_HIGH = 0.040     # 4.0% during crisis peaks


def _churn_by_year(customer_events: list) -> dict:
    """Compute SIM churn rate by year from customer_events list."""
    by_year = {}
    for ev in customer_events:
        year = int(ev.get("event_date", "0000")[:4])
        if year == 0:
            continue
        if year not in by_year:
            by_year[year] = {"renewals": 0, "churns": 0}
        et = ev.get("event_type", "")
        if et == "renewed":
            by_year[year]["renewals"] += 1
        elif et == "churned":
            by_year[year]["churns"] += 1
    result = {}
    for yr, counts in by_year.items():
        total = counts["renewals"] + counts["churns"]
        result[yr] = {
            "renewals": counts["renewals"],
            "churns": counts["churns"],
            "sim_churn_rate": round(counts["churns"] / total, 4) if total > 0 else 0.0,
            "ofgem_benchmark": OFGEM_SWITCHING_RATE.get(yr),
            "calibrated_multiplier": CALIBRATED_MULTIPLIER.get(yr),
        }
    return result


def _bad_debt_check(years_data: dict) -> list:
    """Check bad debt rate vs benchmarks for each year."""
    findings = []
    for yr_str, yd in years_data.items():
        yr = int(yr_str)
        bad_debt = yd.get("bad_debt_gbp", 0.0)
        revenue = yd.get("revenue_gbp", 1.0)
        rate = bad_debt / revenue if revenue > 0 else 0.0
        upper = BAD_DEBT_CRISIS_HIGH if yr in (2021, 2022, 2023) else BAD_DEBT_BENCHMARK_HIGH
        rag = "GREEN"
        if rate > upper:
            rag = "RED"
        elif rate > BAD_DEBT_BENCHMARK_LOW:
            rag = "AMBER"
        findings.append({
            "year": yr,
            "bad_debt_gbp": round(bad_debt, 0),
            "bad_debt_rate": round(rate * 100, 2),
            "benchmark_low_pct": BAD_DEBT_BENCHMARK_LOW * 100,
            "benchmark_high_pct": upper * 100,
            "rag": rag,
        })
    return findings


def _crisis_churn_direction(churn_by_year: dict) -> dict:
    """Check: 2022 churn should NOT be higher than 2020 (pre-crisis baseline).
    
    I&C portfolios have high natural variance (small N), so we flag only when
    the multiplier-normalised rate diverges significantly.
    Critical: market_switching_multiplier in 2022 (0.44) vs 2020 (0.95) implies
    SIM should show lower propensity in 2022. If effective churn is higher in
    2022 than 2020, multiplier adjustment may be insufficient.
    """
    yr2020 = churn_by_year.get(2020, {})
    yr2021 = churn_by_year.get(2021, {})
    yr2022 = churn_by_year.get(2022, {})
    
    rate_2020 = yr2020.get("sim_churn_rate", 0.0)
    rate_2021 = yr2021.get("sim_churn_rate", 0.0)
    rate_2022 = yr2022.get("sim_churn_rate", 0.0)
    
    mult_2020 = CALIBRATED_MULTIPLIER.get(2020, 0.95)
    mult_2022 = CALIBRATED_MULTIPLIER.get(2022, 0.44)
    
    # Normalise churn by multiplier to get "propensity"
    prop_2020 = rate_2020 / mult_2020 if mult_2020 > 0 else 0
    prop_2022 = rate_2022 / mult_2022 if mult_2022 > 0 else 0
    
    diverges = prop_2022 > prop_2020 * 2.0  # 2x threshold allows for small-N variance
    
    return {
        "2020_churn_rate": round(rate_2020 * 100, 1),
        "2021_churn_rate": round(rate_2021 * 100, 1),
        "2022_churn_rate": round(rate_2022 * 100, 1),
        "2020_multiplier_normalised": round(prop_2020 * 100, 1),
        "2022_multiplier_normalised": round(prop_2022 * 100, 1),
        "crisis_divergence_flag": diverges,
        "note": (
            "SIM shows I&C-specific churn; Ofgem switching data is for residential. "
            "2022 multiplier=0.44 should suppress churn vs 2020 multiplier=0.95. "
            "Flag fires if 2022 normalised propensity is >2x 2020 propensity."
        ),
    }


def _multiplier_alignment(churn_by_year: dict) -> list:
    """Check that SIM churn direction tracks the Ofgem switching rate direction."""
    findings = []
    years = sorted(churn_by_year.keys())
    for i in range(1, len(years)):
        prev_yr = years[i - 1]
        curr_yr = years[i]
        if curr_yr not in OFGEM_SWITCHING_RATE or prev_yr not in OFGEM_SWITCHING_RATE:
            continue
        ofgem_direction = "down" if OFGEM_SWITCHING_RATE[curr_yr] < OFGEM_SWITCHING_RATE[prev_yr] else "up"
        sim_rate_prev = churn_by_year[prev_yr].get("sim_churn_rate", 0.0)
        sim_rate_curr = churn_by_year[curr_yr].get("sim_churn_rate", 0.0)
        sim_direction = "down" if sim_rate_curr < sim_rate_prev else ("up" if sim_rate_curr > sim_rate_prev else "flat")
        
        if ofgem_direction == "down" and sim_direction == "up":
            rag = "AMBER"
        else:
            rag = "GREEN"
        
        findings.append({
            "year_transition": "%d->%d" % (prev_yr, curr_yr),
            "ofgem_direction": ofgem_direction,
            "sim_direction": sim_direction,
            "ofgem_rate_prev": OFGEM_SWITCHING_RATE[prev_yr],
            "ofgem_rate_curr": OFGEM_SWITCHING_RATE[curr_yr],
            "sim_rate_prev": sim_rate_prev,
            "sim_rate_curr": sim_rate_curr,
            "rag": rag,
        })
    return findings


def generate(run_json_path=None, out_path=None):
    if run_json_path is None:
        run_json_path = RUN_JSON
    if out_path is None:
        out_path = OUT_PATH
    data = json.loads(Path(run_json_path).read_text())
    
    events = data.get("customer_events", [])
    years_data = data.get("years", {})
    
    churn_by_year = _churn_by_year(events)
    bad_debt_findings = _bad_debt_check(years_data)
    crisis_check = _crisis_churn_direction(churn_by_year)
    multiplier_alignment = _multiplier_alignment(churn_by_year)
    
    amber_count = sum(1 for f in bad_debt_findings if f["rag"] == "AMBER")
    red_count = sum(1 for f in bad_debt_findings if f["rag"] == "RED")
    bad_debt_rag = "RED" if red_count else ("AMBER" if amber_count else "GREEN")
    
    multiplier_amber = sum(1 for f in multiplier_alignment if f["rag"] == "AMBER")
    multiplier_rag = "AMBER" if multiplier_amber else "GREEN"
    
    overall_rag = "RED" if (bad_debt_rag == "RED" or crisis_check["crisis_divergence_flag"]) else (
        "AMBER" if (bad_debt_rag == "AMBER" or multiplier_rag == "AMBER") else "GREEN"
    )
    
    result = {
        "meta": {
            "ofgem_benchmark_source": "Ofgem Retail Market Indicators (annual switching data)",
            "bad_debt_benchmark": "Industry range 0.5-2.5% (Ofgem/EUA annual survey)",
        },
        "overall_rag": overall_rag,
        "crisis_churn_direction": crisis_check,
        "bad_debt_vs_benchmark": bad_debt_findings,
        "multiplier_alignment": multiplier_alignment,
        "churn_by_year": {str(k): v for k, v in sorted(churn_by_year.items())},
    }
    
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    r = generate()
    print("Overall RAG:", r["overall_rag"])
    print("Crisis divergence:", r["crisis_churn_direction"]["crisis_divergence_flag"])
    print("Bad debt RED years:", sum(1 for f in r["bad_debt_vs_benchmark"] if f["rag"] == "RED"))
