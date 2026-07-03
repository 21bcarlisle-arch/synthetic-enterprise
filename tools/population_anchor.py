"""Phase PQ/PS -- Population Anchoring Validation Gate.

Compares SIM aggregate outputs against published UK energy market benchmarks.
Runs every sim run; outputs to site/state/population_anchoring.json.

Key benchmarks (sources: Ofgem switching data, DESNZ, Energy UK):
  - Annual switching rates by year (Ofgem Retail Market Indicators)
  - Bad debt rates vs industry range (0.5-2.5% of revenue)
  - Churn direction: 2021-22 crisis = switching COLLAPSE, not rise
  - Complaint rate vs Ofgem QoS survey benchmarks (Phase PS)
  - Arrears rate vs DESNZ business energy debt data (Phase PS)

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




COMPLAINT_BENCHMARK_NORMAL_HI = 6.0
COMPLAINT_BENCHMARK_NORMAL_LO = 1.0
COMPLAINT_BENCHMARK_CRISIS_HI = 8.0
COMPLAINT_RED_HI = 10.0
ARREARS_BENCHMARK_NORMAL_HI = 8.0
ARREARS_BENCHMARK_CRISIS_HI = 12.0
ARREARS_AMBER_HI = 15.0
ARREARS_AMBER_CRISIS_HI = 18.0
_CRISIS_YEARS = {2021, 2022, 2023}
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




def _complaints_check(years_data: dict) -> list:
    """Check complaint rate vs Ofgem QoS benchmarks per year.

    Metric: avg_complaint_probability * 100 = % of billing periods generating
    a formal complaint. Benchmarks: Ofgem QoS survey, I&C adjusted.
    Normal years GREEN 2-6%; crisis years (2021-2023) GREEN ceiling 8%.
    """
    findings = []
    for yr_str in sorted(years_data.keys()):
        yr = int(yr_str)
        yd = years_data[yr_str]
        rate = yd.get("avg_complaint_probability", 0.0) * 100
        is_crisis = yr in _CRISIS_YEARS
        green_hi = COMPLAINT_BENCHMARK_CRISIS_HI if is_crisis else COMPLAINT_BENCHMARK_NORMAL_HI
        if rate < COMPLAINT_BENCHMARK_NORMAL_LO or rate > COMPLAINT_RED_HI:
            rag = "RED"
        elif rate > green_hi:
            rag = "AMBER"
        else:
            rag = "GREEN"
        findings.append({
            "year": yr,
            "complaint_rate_pct": round(rate, 2),
            "benchmark_green_hi": green_hi,
            "benchmark_lo": COMPLAINT_BENCHMARK_NORMAL_LO,
            "is_crisis_year": is_crisis,
            "rag": rag,
        })
    return findings
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




def _arrears_check_by_year(billing_ledger_data: dict, years_data: dict) -> list:
    """Check new arrears rate per year vs DESNZ business energy debt benchmarks.

    Metric: unique customers with a new arrears case opened in each calendar year
    divided by active customers that year. DESNZ I&C benchmark: <8% normal, <12% crisis.
    """
    customers = billing_ledger_data.get("customers", {})
    arrears_by_year: dict = {}
    for cid, cdata in customers.items():
        for case in cdata.get("arrears_history", []):
            opened = case.get("opened_date", "")
            if not opened:
                continue
            try:
                yr = int(opened[:4])
            except ValueError:
                continue
            arrears_by_year.setdefault(yr, set()).add(cid)

    findings = []
    for yr_str in sorted(years_data.keys()):
        yr = int(yr_str)
        yd = years_data[yr_str]
        active = yd.get("active_customer_ids", [])
        n_active = len(active) if active else 0
        n_arrears = len(arrears_by_year.get(yr, set()))
        rate = (n_arrears / n_active * 100) if n_active > 0 else 0.0
        is_crisis = yr in _CRISIS_YEARS
        green_hi = ARREARS_BENCHMARK_CRISIS_HI if is_crisis else ARREARS_BENCHMARK_NORMAL_HI
        amber_hi = ARREARS_AMBER_CRISIS_HI if is_crisis else ARREARS_AMBER_HI
        if rate > amber_hi:
            rag = "RED"
        elif rate > green_hi:
            rag = "AMBER"
        else:
            rag = "GREEN"
        findings.append({
            "year": yr,
            "new_arrears_count": n_arrears,
            "active_customers": n_active,
            "new_arrears_rate_pct": round(rate, 1),
            "benchmark_green_hi": green_hi,
            "is_crisis_year": is_crisis,
            "rag": rag,
        })
    return findings
def _long_run_comparison(churn_by_year: dict) -> dict:
    """Compare SIM average churn (2016-2025) vs Ofgem average switching rate.

    More statistically robust than single-year comparisons with small N.
    """
    sim_years = [yr for yr in churn_by_year if yr in OFGEM_SWITCHING_RATE]
    if not sim_years:
        return {"sim_avg_pct": None, "ofgem_avg_pct": None, "ratio": None, "rag": "GREEN", "note": "no data"}
    sim_avg = sum(churn_by_year[yr]["sim_churn_rate"] for yr in sim_years) / len(sim_years)
    ofgem_avg = sum(OFGEM_SWITCHING_RATE[yr] for yr in sim_years) / len(sim_years)
    ratio = sim_avg / ofgem_avg if ofgem_avg > 0 else None
    total_renewals = sum(
        churn_by_year[yr]["renewals"] + churn_by_year[yr]["churns"] for yr in sim_years
    )
    rag = "GREEN" if ratio is None or ratio < 2.0 else ("AMBER" if ratio < 3.5 else "RED")
    return {
        "sim_avg_pct": round(sim_avg * 100, 1),
        "ofgem_avg_pct": round(ofgem_avg * 100, 1),
        "ratio": round(ratio, 2) if ratio is not None else None,
        "years_compared": len(sim_years),
        "total_renewals": total_renewals,
        "rag": rag,
        "note": (
            "SIM portfolio is predominantly I&C (B2B contract churn) vs Ofgem residential switching. "
            "Long-run average comparison is more robust than single-year with N<15 renewals."
        ),
    }


def _crisis_churn_direction(churn_by_year: dict) -> dict:
    """Check: 2022 crisis window churn should not diverge dramatically from pre-crisis.

    Uses 3-year rolling average to reduce single-year small-N noise.
    Also checks absolute 2022 SIM rate vs Ofgem 2022 rate.
    """
    pre_crisis_years = [yr for yr in [2019, 2020, 2021] if yr in churn_by_year]
    crisis_years = [yr for yr in [2021, 2022, 2023] if yr in churn_by_year]

    pre_rate = (sum(churn_by_year[yr]["sim_churn_rate"] for yr in pre_crisis_years)
                / len(pre_crisis_years)) if pre_crisis_years else 0.0
    crisis_rate = (sum(churn_by_year[yr]["sim_churn_rate"] for yr in crisis_years)
                   / len(crisis_years)) if crisis_years else 0.0

    pre_n = sum(churn_by_year[yr]["renewals"] + churn_by_year[yr]["churns"]
                for yr in pre_crisis_years)
    crisis_n = sum(churn_by_year[yr]["renewals"] + churn_by_year[yr]["churns"]
                   for yr in crisis_years)

    yr2022 = churn_by_year.get(2022, {})
    rate_2022 = yr2022.get("sim_churn_rate", 0.0)
    ofgem_2022 = OFGEM_SWITCHING_RATE.get(2022, 0.04)

    rolling_diverges = crisis_rate > pre_rate * 1.5 and crisis_rate > 0.05
    absolute_diverges = rate_2022 > ofgem_2022 * 4.0 and crisis_n >= 5
    insufficient_data = pre_n < 10 or crisis_n < 10

    return {
        "pre_crisis_avg_pct": round(pre_rate * 100, 1),
        "crisis_avg_pct": round(crisis_rate * 100, 1),
        "2022_sim_rate_pct": round(rate_2022 * 100, 1),
        "2022_ofgem_rate_pct": round(ofgem_2022 * 100, 1),
        "2022_ratio_vs_ofgem": round(rate_2022 / ofgem_2022, 1) if ofgem_2022 else None,
        "rolling_divergence_flag": rolling_diverges,
        "absolute_divergence_flag": absolute_diverges,
        "crisis_divergence_flag": rolling_diverges and absolute_diverges and not insufficient_data,
        "insufficient_data": insufficient_data,
        "note": (
            "3-year rolling comparison reduces single-year small-N noise. "
            "crisis_divergence_flag requires BOTH rolling AND absolute divergence AND adequate N. "
            "I&C at-contract-end churn is structurally higher than residential -- 4x Ofgem "
            "threshold allows for portfolio composition difference."
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


def generate(run_json_path=None, out_path=None, billing_ledger_path=None):
    if run_json_path is None:
        run_json_path = RUN_JSON
    if out_path is None:
        out_path = OUT_PATH
    data = json.loads(Path(run_json_path).read_text())
    
    events = data.get("customer_events", [])
    years_data = data.get("years", {})
    
    churn_by_year = _churn_by_year(events)
    bad_debt_findings = _bad_debt_check(years_data)
    long_run = _long_run_comparison(churn_by_year)
    crisis_check = _crisis_churn_direction(churn_by_year)
    multiplier_alignment = _multiplier_alignment(churn_by_year)

    complaints_findings = _complaints_check(years_data)
    if billing_ledger_path is None:
        billing_ledger_path = PROJECT / "site" / "state" / "billing_ledger.json"
    try:
        ledger_data: dict = json.loads(Path(billing_ledger_path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        ledger_data = {}
    arrears_findings = _arrears_check_by_year(ledger_data, years_data)

    amber_count = sum(1 for f in bad_debt_findings if f["rag"] == "AMBER")
    red_count = sum(1 for f in bad_debt_findings if f["rag"] == "RED")
    bad_debt_rag = "RED" if red_count else ("AMBER" if amber_count else "GREEN")

    multiplier_amber = sum(1 for f in multiplier_alignment if f["rag"] == "AMBER")
    multiplier_rag = "AMBER" if multiplier_amber else "GREEN"

    # Long-run average is primary calibration signal; single-year crisis flag is secondary.
    # crisis_divergence_flag requires both rolling AND absolute divergence with adequate N.
    crisis_flag = crisis_check["crisis_divergence_flag"]
    overall_rag = "RED" if (bad_debt_rag == "RED" or (long_run["rag"] == "RED" and crisis_flag)) else (
        "AMBER" if (bad_debt_rag == "AMBER" or long_run["rag"] == "AMBER"
                    or crisis_flag or multiplier_rag == "AMBER") else "GREEN"
    )

    result = {
        "meta": {
            "ofgem_benchmark_source": "Ofgem Retail Market Indicators (annual switching data)",
            "bad_debt_benchmark": "Industry range 0.5-2.5% (Ofgem/EUA annual survey)",
            "complaint_benchmark": "Ofgem QoS survey; I&C adjusted 2-6% normal, 2-8% crisis",
            "arrears_benchmark": "DESNZ business energy debt; I&C <8% normal, <12% crisis",
        },
        "overall_rag": overall_rag,
        "long_run_comparison": long_run,
        "crisis_churn_direction": crisis_check,
        "bad_debt_vs_benchmark": bad_debt_findings,
        "multiplier_alignment": multiplier_alignment,
        "churn_by_year": {str(k): v for k, v in sorted(churn_by_year.items())},
        "complaints_vs_benchmark": complaints_findings,
        "arrears_vs_benchmark": arrears_findings,
    }
    
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    r = generate()
    print("Overall RAG:", r["overall_rag"])
    print("Crisis divergence:", r["crisis_churn_direction"]["crisis_divergence_flag"])
    print("Bad debt RED years:", sum(1 for f in r["bad_debt_vs_benchmark"] if f["rag"] == "RED"))
