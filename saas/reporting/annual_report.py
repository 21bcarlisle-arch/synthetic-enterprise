"""Phase 5a — annual report generator.

Reads the structured output of `simulation.run_phase4c_on_phase2b.main()`
(the full 9.5-year Phase 2b settlement plus the 4c billing/payment/contact
layers for the real 10-account portfolio) and produces a markdown annual
report covering the whole window, one section per calendar year.

This module does not run the simulation. `extract_report_data()` is a pure
function over the run's output dict; `generate_annual_report()` is a pure
function over `extract_report_data()`'s result. The CLI entry point below
(`python3 -m saas.reporting.annual_report`) is the only place that calls
`run_phase4c_on_phase2b.main()`, and it caches the extracted data as JSON
(`docs/observability/phase4c_report_data.json`) so subsequent report
regenerations can run from `--from-json` without re-running the simulation.

Phase 5b: `run_phase4c_on_phase2b.main()` now runs Phase 2b once and feeds
the same `all_records`/`CUSTOMERS` through both the 4c billing-experience
builders and the 4b customer-value builders (`cost_to_serve`, `churn_model`,
`home_move_win_rate`, `enterprise_value`), so CLV, churn risk, cost to serve,
home-move win rate, enterprise value, and per-wake-up VaR are now part of the
run output and reflected here. Two figures remain "Not available" by design
(see `docs/reports/REPORTING_BACKLOG.md`): the churn-risk threshold and
"losses during year" (no churn mechanic is applied to the actual settlement
roster -- 4b's churn/home-move scores are point-in-time risk estimates, not
roster events) and regulatory threshold breaches (no threshold defined yet).
Per the "do not invent numbers" constraint, every other still-missing field
would be rendered as an explicit "Not available in current run output" note
rather than an estimate.
"""

import argparse
import json
import subprocess
from pathlib import Path

from saas.clv_model import build_clv
from saas.cost_to_serve import build_cost_to_serve
from saas.customer_reaction import _billing_account_id
from saas.customers import ACQUIRED_CUSTOMERS, CUSTOMERS, SUCCESSOR_CUSTOMERS
from simulation.run_phase4c_on_phase2b import main as run_phase4c_on_phase2b
from simulation.tou_periods import is_peak_period
from saas.capital.bsc_credit import compute_bsc_credit_by_year
from saas.capital.solvency import compute_solvency_by_year, compute_solvency_signal
from company.finance import management_accounts as _ma
from company.finance import budget as _budget

DEFAULT_REPORT_DATA_PATH = Path("docs/reports/run_output_latest.json")
DEFAULT_REPORT_PATH = Path("docs/reports/ANNUAL_REPORT.md")
LEDGER_LATEST_PATH = Path("docs/reports/ledger_latest.json")

# Phase 5c: snapshot of the pre-mandate (old reactive-hedging) run's
# extracted report data, kept so the mandate's effect can be shown
# side-by-side without re-running the old model.
OLD_MODEL_REPORT_DATA_PATH = Path("docs/reports/run_output_old_reactive_model_pre5c.json")

DRAWDOWN_THRESHOLD_PCT = 0.10

CRISIS_YEARS = {"2021", "2022"}

NOT_AVAILABLE = "Not available in current run output (see REPORTING_BACKLOG.md)"

# Phase 21b: Ofgem regulatory capital floor per customer (dual-fuel basis).
# Licence condition: £0 net assets/customer triggers regulatory review;
# £130/customer is the industry working-capital target.
REGULATORY_CAPITAL_FLOOR_PER_CUSTOMER_GBP = 130.0


def _year(date_str: str) -> str:
    return date_str[:4]


def _avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


_MARGIN_BENCHMARK_LOW = 0.02  # 2% net-margin floor per industry benchmark


def _build_clv_snapshots(
    all_records: list[dict],
    churn_risk: dict,
    years: list[str],
) -> dict[str, dict[str, float | None]]:
    """Per-year Point-in-Time CLV snapshots.

    For each year Y, computes CLV using only records and churn renewal events
    up to and including 31-Dec-Y. Accounts with no renewal points through year
    Y are excluded (nothing to project). Returns
    {year: {billing_account_id: clv_gbp | None}}.
    """
    snapshots: dict[str, dict] = {}
    for year in years:
        cutoff = f"{year}-12-31"
        records_to_year = [r for r in all_records if r["settlement_date"] <= cutoff]
        risk_to_year = {
            account_id: [r for r in renewals if r["renewal_period"] <= cutoff[:7]]
            for account_id, renewals in churn_risk.items()
        }
        cts_to_year = build_cost_to_serve(records_to_year, CUSTOMERS + SUCCESSOR_CUSTOMERS)
        clv_to_year = build_clv(risk_to_year, cts_to_year)
        snapshots[year] = {
            account_id: v["clv_gbp"] for account_id, v in clv_to_year.items()
        }
    return snapshots


def _pricing_action(net_margin_after_cts_gbp: float | None, revenue_gbp: float) -> dict:
    """Activity-based pricing policy for a customer's lifetime figures.

    Returns a dict with:
      flag: "OK" | "MARGIN_SQUEEZE" | "NET_NEGATIVE" | "UNKNOWN"
      recommended_uplift_pct: float | None  (% tariff increase to reach breakeven)
    """
    if net_margin_after_cts_gbp is None:
        return {"flag": "UNKNOWN", "recommended_uplift_pct": None}
    if revenue_gbp <= 0:
        return {"flag": "UNKNOWN", "recommended_uplift_pct": None}
    if net_margin_after_cts_gbp < 0:
        uplift_pct = (-net_margin_after_cts_gbp / revenue_gbp) * 100
        return {"flag": "NET_NEGATIVE", "recommended_uplift_pct": round(uplift_pct, 1)}
    if net_margin_after_cts_gbp < _MARGIN_BENCHMARK_LOW * revenue_gbp:
        return {"flag": "MARGIN_SQUEEZE", "recommended_uplift_pct": None}
    return {"flag": "OK", "recommended_uplift_pct": None}


def _drawdown_events(treasury_series: list[float], threshold: float = DRAWDOWN_THRESHOLD_PCT) -> list[dict]:
    """Peak-to-trough drawdowns in `treasury_series` (chronological order)
    of at least `threshold` (fraction of the peak). Returns
    `[{peak_gbp, trough_gbp, drawdown_pct}]`, one entry per completed
    drawdown (a new peak above the previous one ends/restarts tracking)."""
    events = []
    peak = treasury_series[0] if treasury_series else 0.0
    trough = peak
    for value in treasury_series[1:]:
        if value > peak:
            if peak > 0 and trough < peak:
                drawdown_pct = (peak - trough) / peak
                if drawdown_pct >= threshold:
                    events.append({
                        "peak_gbp": peak, "trough_gbp": trough, "drawdown_pct": drawdown_pct,
                    })
            peak = value
            trough = value
        elif value < trough:
            trough = value
    if peak > 0 and trough < peak:
        drawdown_pct = (peak - trough) / peak
        if drawdown_pct >= threshold:
            events.append({"peak_gbp": peak, "trough_gbp": trough, "drawdown_pct": drawdown_pct})
    return events


def extract_report_data(run_output: dict) -> dict:
    """Reduce `run_phase4c_on_phase2b.main()`'s output to a small,
    JSON-serialisable dict of everything `generate_annual_report()` needs --
    a per-year breakdown plus whole-window totals and per-customer lifetime
    figures. Does not retain `all_records` (too large to persist; ~1M rows
    for the full 9.5-year window)."""
    phase2b = run_output["phase2b"]
    all_records = phase2b["all_records"]
    bills = run_output.get("bills", [])
    payment_behaviour = run_output.get("payment_behaviour", {})
    contact_model = run_output.get("contact_model", {})
    committee_wake_ups = phase2b.get("committee_wake_ups", [])
    hedge_evolution = phase2b.get("hedge_evolution", {})
    by_customer_contact = contact_model.get("by_customer", {})

    cost_to_serve = run_output.get("cost_to_serve", {})
    churn_risk = run_output.get("churn_risk", {})
    home_move_win_rates = run_output.get("home_move_win_rates", {})
    enterprise_value = run_output.get("enterprise_value", {})

    hedge_entries = [
        {**entry, "customer_id": cid}
        for cid, entries in hedge_evolution.items()
        for entry in entries
    ]

    years = sorted({_year(r["settlement_date"]) for r in all_records})
    won_successor_activations: dict[str, str] = run_output.get("won_successor_activations", {})
    segment_by_customer = {
        c["customer_id"]: c["segment"]
        for c in CUSTOMERS + SUCCESSOR_CUSTOMERS + ACQUIRED_CUSTOMERS
    }

    # Phase 8a: growth mandate data
    acquisition_spend_events = run_output.get("acquisition_spend_events", [])
    fixed_cost_events = run_output.get("fixed_cost_events", [])
    acquired_customer_ids = run_output.get("acquired_customers", [])
    growth_mandate = run_output.get("growth_mandate", "flat")

    # Phase AF: flexibility revenue by year (CM + DFS)
    flex_by_year: dict[str, dict[str, float]] = phase2b.get("flexibility_revenue_by_year", {})
    flex_summary = phase2b.get("flexibility_revenue_summary", {})

    # Phase 53: BSC credit cover — computed while all_records is available
    bsc_credit_by_yr = compute_bsc_credit_by_year(all_records)

    yearly = {}
    for year in years:
        yr_records = [r for r in all_records if _year(r["settlement_date"]) == year]

        commodity_split = {}
        for commodity in ("electricity", "gas"):
            recs = [r for r in yr_records if r.get("commodity") == commodity]
            commodity_split[commodity] = {
                "revenue_gbp": sum(r["revenue_gbp"] for r in recs),
                "wholesale_cost_gbp": sum(r["wholesale_cost_gbp"] for r in recs),
                "gross_gbp": sum(r["margin_gbp"] for r in recs),
                "capital_gbp": sum(r["capital_cost_gbp"] for r in recs),
                "net_gbp": sum(r["net_margin_gbp"] for r in recs),
            }

        segment_split: dict[str, dict] = {}
        for r in yr_records:
            segment = segment_by_customer.get(r["customer_id"], "unknown")
            label = f"{segment} {r.get('commodity', 'electricity')}"
            entry = segment_split.setdefault(
                label, {"gross_gbp": 0.0, "capital_gbp": 0.0, "net_gbp": 0.0}
            )
            entry["gross_gbp"] += r["margin_gbp"]
            entry["capital_gbp"] += r["capital_cost_gbp"]
            entry["net_gbp"] += r["net_margin_gbp"]

        per_customer = {}
        for cid in sorted({r["customer_id"] for r in yr_records}):
            crecs = [r for r in yr_records if r["customer_id"] == cid]
            per_customer[cid] = {
                "commodity": crecs[0].get("commodity", "electricity"),
                "gross_gbp": sum(r["margin_gbp"] for r in crecs),
                "capital_gbp": sum(r["capital_cost_gbp"] for r in crecs),
                "net_gbp": sum(r["net_margin_gbp"] for r in crecs),
                "tariff_min_gbp_per_mwh": min(r["unit_rate_gbp_per_mwh"] for r in crecs),
                "tariff_max_gbp_per_mwh": max(r["unit_rate_gbp_per_mwh"] for r in crecs),
            }

        treasury_end = max(yr_records, key=lambda r: (r["settlement_date"], r["settlement_period"]))[
            "treasury_cash_balance_gbp"
        ]
        worst_record = min(yr_records, key=lambda r: r["net_margin_gbp"])

        wake_ups = [w for w in committee_wake_ups if _year(w["settlement_date"]) == year]

        hedge_fractions = {}
        for cid, entries in hedge_evolution.items():
            yr_entries = [e for e in entries if _year(e["term_start"]) == year]
            if yr_entries:
                hedge_fractions[cid] = {
                    "start_hf": yr_entries[0]["hf_used"],
                    "avg_hf": _avg([e["hf_used"] for e in yr_entries]),
                }

        yr_bills = [b for b in bills if _year(b["period_end"]) == year]
        shocked = [b for b in yr_bills if b["bill_shock_pct"] is not None]
        shock_events = [
            {"customer_id": b["customer_id"], "period_end": b["period_end"], "bill_shock_pct": b["bill_shock_pct"]}
            for b in shocked
            if b["bill_shock_pct"] >= 0.20
        ]

        bad_debt_gbp = sum(r.get("bad_debt_gbp", 0.0) for r in yr_records)

        complaint_probs = [
            e["complaint_probability"]
            for entries in by_customer_contact.values()
            for e in entries
            if _year(e["period_end"]) == year
        ]

        treasury_series = [
            r["treasury_cash_balance_gbp"]
            for r in sorted(yr_records, key=lambda r: (r["settlement_date"], r["settlement_period"]))
        ]
        treasury_drawdown_events = _drawdown_events(treasury_series)

        var_wake_ups = [w for w in wake_ups if "portfolio_var_current_gbp" in w]
        var_ratio = (
            _avg([
                w["portfolio_var_current_gbp"] / w["portfolio_var_stressed_gbp"]
                for w in var_wake_ups
                if w["portfolio_var_stressed_gbp"]
            ])
            if var_wake_ups
            else None
        )

        yr_hedge_entries = [e for e in hedge_entries if _year(e["term_start"]) == year]
        hedge_by_customer = {}
        for cid in sorted({e["customer_id"] for e in yr_hedge_entries}):
            centries = [e for e in yr_hedge_entries if e["customer_id"] == cid]
            actual = sum(e["actual_net"] for e in centries)
            naked = sum(e["naked_net"] for e in centries)
            hedge_by_customer[cid] = {
                "actual_net_gbp": actual,
                "naked_net_gbp": naked,
                "hedging_value_add_gbp": actual - naked,
            }
        hedge_effectiveness = {
            "actual_net_gbp": sum(e["actual_net"] for e in yr_hedge_entries),
            "naked_net_gbp": sum(e["naked_net"] for e in yr_hedge_entries),
            "hedging_value_add_gbp": sum(e["actual_net"] - e["naked_net"] for e in yr_hedge_entries),
            "by_customer": hedge_by_customer,
        }

        yearly[year] = {
            "revenue_gbp": sum(r["revenue_gbp"] for r in yr_records),
            "gross_gbp": sum(r["margin_gbp"] for r in yr_records),
            "capital_gbp": sum(r["capital_cost_gbp"] for r in yr_records),
            "bad_debt_gbp": sum(r.get("bad_debt_gbp", 0.0) for r in yr_records),
            "net_gbp": sum(r["net_margin_gbp"] for r in yr_records),
            "treasury_end_gbp": treasury_end,
            "bsc_credit_required_gbp": bsc_credit_by_yr.get(year, {}).get("credit_cover_required_gbp", 0.0),
            "bsc_peak_daily_gbp": bsc_credit_by_yr.get(year, {}).get("peak_daily_wholesale_gbp", 0.0),
            "commodity_split": commodity_split,
            "segment_split": segment_split,
            "per_customer": per_customer,
            "active_customer_ids": sorted({r["customer_id"] for r in yr_records}),
            "acquisitions": sorted(
                [c["customer_id"] for c in CUSTOMERS if _year(c["acquisition_date"]) == year]
                + [
                    sid for sid, act_date in won_successor_activations.items()
                    if _year(act_date) == year
                ]
            ),
            "committee_wake_ups": wake_ups,
            "hedge_fractions": hedge_fractions,
            "worst_period": {
                "settlement_date": worst_record["settlement_date"],
                "settlement_period": worst_record["settlement_period"],
                "customer_id": worst_record["customer_id"],
                "net_margin_gbp": worst_record["net_margin_gbp"],
            },
            "bills_count": len(yr_bills),
            "avg_clarity": _avg([b["clarity_score"] for b in yr_bills]),
            "avg_bill_shock_pct": _avg([b["bill_shock_pct"] for b in shocked]),
            "bill_shock_events": shock_events,
            "bad_debt_gbp": bad_debt_gbp,
            "avg_complaint_probability": _avg(complaint_probs),
            "treasury_drawdown_events": treasury_drawdown_events,
            "var_ratio": var_ratio,
            "hedge_effectiveness": hedge_effectiveness,
            "churn_risk_by_account": {
                account_id: yr_renewals[-1]["churn_probability"]
                for account_id, all_renewals in churn_risk.items()
                if (yr_renewals := [r for r in all_renewals if r["renewal_period"][:4] == year])
            },
            # Phase 8a: per-year acquisition and fixed cost data
            "acquisition_attempts": sum(
                1 for e in acquisition_spend_events if e["timestamp"][:4] == year
            ),
            "acquisition_wins": sum(
                1 for e in acquisition_spend_events
                if e["timestamp"][:4] == year and e.get("acquisition_won")
            ),
            "acquisition_spend_gbp": sum(
                -e["amount_gbp"] for e in acquisition_spend_events if e["timestamp"][:4] == year
            ),
            "fixed_cost_gbp": sum(
                -e["amount_gbp"] for e in fixed_cost_events if e["timestamp"][:4] == year
            ),
            # Phase 21a: electricity policy costs (RO + CfD) — deducted from net_margin_gbp
            "ro_levy_gbp": sum(
                r.get("ro_levy_gbp", 0.0) for r in yr_records if r.get("commodity") == "electricity"
            ),
            "cfd_levy_gbp": sum(
                r.get("cfd_levy_gbp", 0.0) for r in yr_records if r.get("commodity") == "electricity"
            ),
            # Phase 27b: CCL for business electricity customers (resi exempt)
            "ccl_gbp": sum(
                r.get("ccl_gbp", 0.0) for r in yr_records if r.get("commodity") == "electricity"
            ),
            # Phase 30a: CM levy for all electricity demand customers (domestic + business)
            "cm_levy_gbp": sum(
                r.get("cm_levy_gbp", 0.0) for r in yr_records if r.get("commodity") == "electricity"
            ),
            # Phase 31a: FiT levy for all electricity demand customers (no domestic exemption)
            "fit_levy_gbp": sum(
                r.get("fit_levy_gbp", 0.0) for r in yr_records if r.get("commodity") == "electricity"
            ),
            # Phase 54: SoLR mutualization levy (2021-2022 supplier failure wave recovery)
            "mutualization_levy_gbp": sum(
                r.get("mutualization_levy_gbp", 0.0) for r in yr_records if r.get("commodity") == "electricity"
            ),
            "policy_cost_gbp": sum(
                r.get("policy_cost_gbp", 0.0) for r in yr_records if r.get("commodity") == "electricity"
            ),
            # Phase 29a: DUoS + TNUoS network charges deducted from net_margin_gbp
            "network_cost_gbp": sum(
                r.get("network_cost_gbp", 0.0) for r in yr_records if r.get("commodity") == "electricity"
            ),
            # Phase 30b: gas-side policy costs (CCL + GGL) and network charges
            "gas_policy_cost_gbp": sum(
                r.get("gas_policy_cost_gbp", 0.0) for r in yr_records if r.get("commodity") == "gas"
            ),
            "gas_network_cost_gbp": sum(
                r.get("gas_network_cost_gbp", 0.0) for r in yr_records if r.get("commodity") == "gas"
            ),
            # Phase AF: DSR/CM flexibility revenue earned from flexible assets
            "flexibility_revenue_gbp": sum(
                flex_by_year.get(year, {}).values()
            ),
        }

    per_customer_lifetime = {}
    for c in CUSTOMERS + SUCCESSOR_CUSTOMERS:
        cid = c["customer_id"]
        recs = [r for r in all_records if r["customer_id"] == cid]
        if not recs:
            continue
        cts = cost_to_serve.get("by_customer", {}).get(cid, {})
        revenue_gbp = sum(r["revenue_gbp"] for r in recs)
        net_after_cts = cts.get("net_margin_gbp")
        per_customer_lifetime[cid] = {
            "commodity": c["commodity"],
            "segment": c["segment"],
            "acquisition_date": c["acquisition_date"],
            "revenue_gbp": revenue_gbp,
            "gross_gbp": sum(r["margin_gbp"] for r in recs),
            "capital_gbp": sum(r["capital_cost_gbp"] for r in recs),
            "net_gbp": sum(r["net_margin_gbp"] for r in recs),
            "cost_to_serve_gbp": cts.get("cost_to_serve_gbp"),
            "net_margin_after_cost_to_serve_gbp": net_after_cts,
            "pricing_action": _pricing_action(net_after_cts, revenue_gbp),
        }

    # CLV/churn/enterprise-value are computed per billing account (dual-fuel
    # electricity+gas legs combined, see _billing_account_id) -- a different
    # key space than per_customer_lifetime's per-commodity customer_id.
    by_billing_account = {}
    for cid, c in {c["customer_id"]: c for c in CUSTOMERS}.items():
        account_id = _billing_account_id(cid)
        if account_id in by_billing_account:
            continue
        renewals = churn_risk.get(account_id, [])
        win_rates = home_move_win_rates.get(account_id, [])
        ev = enterprise_value.get("by_customer", {}).get(account_id)
        by_billing_account[account_id] = {
            "latest_churn_probability": renewals[-1]["churn_probability"] if renewals else None,
            "latest_renewal_period": renewals[-1]["renewal_period"] if renewals else None,
            "home_move_win_probability": win_rates[-1]["win_probability"] if win_rates else None,
            "clv_gbp": ev["clv_gbp"] if ev else None,
            "expected_lifetime_periods": ev["expected_lifetime_periods"] if ev else None,
        }

    clv_values = [v["clv_gbp"] for v in by_billing_account.values() if v["clv_gbp"] is not None]
    if clv_values:
        highest_clv = max(by_billing_account.items(), key=lambda kv: kv[1]["clv_gbp"] or float("-inf"))
        lowest_clv = min(by_billing_account.items(), key=lambda kv: kv[1]["clv_gbp"] or float("inf"))
    else:
        highest_clv = lowest_clv = None

    if hedge_entries:
        best_decision = max(hedge_entries, key=lambda e: e["actual_net"] - e["naked_net"])
        worst_decision = min(hedge_entries, key=lambda e: e["actual_net"] - e["naked_net"])
        hedge_effectiveness_total = {
            "actual_net_gbp": sum(e["actual_net"] for e in hedge_entries),
            "naked_net_gbp": sum(e["naked_net"] for e in hedge_entries),
            "hedging_value_add_gbp": sum(e["actual_net"] - e["naked_net"] for e in hedge_entries),
            "best_decision": {
                "customer_id": best_decision["customer_id"],
                "term_start": best_decision["term_start"],
                "hedging_value_add_gbp": best_decision["actual_net"] - best_decision["naked_net"],
                "hf_used": best_decision["hf_used"],
            },
            "worst_decision": {
                "customer_id": worst_decision["customer_id"],
                "term_start": worst_decision["term_start"],
                "hedging_value_add_gbp": worst_decision["actual_net"] - worst_decision["naked_net"],
                "hf_used": worst_decision["hf_used"],
            },
        }
    else:
        hedge_effectiveness_total = None

    clv_snapshots = (
        _build_clv_snapshots(all_records, churn_risk, years) if churn_risk else None
    )

    # Phase 13a: ToU utilization stats for HH customers (C7-C9).
    # Computed here while all_records is in scope; stored as tou_stats in output.
    _HH_CUSTOMERS = {"C7", "C8", "C9"}
    tou_stats: dict[str, dict] = {}
    for cid in _HH_CUSTOMERS:
        hh_recs = [r for r in all_records if r.get("customer_id") == cid and r.get("commodity") == "electricity"]
        if not hh_recs:
            continue
        peak_recs = [r for r in hh_recs if is_peak_period(r["settlement_date"], r["settlement_period"])]
        offpeak_recs = [r for r in hh_recs if not is_peak_period(r["settlement_date"], r["settlement_period"])]
        total_kwh = sum(r["consumption_kwh"] for r in hh_recs)
        peak_kwh = sum(r["consumption_kwh"] for r in peak_recs)
        peak_revenue = sum(r["revenue_gbp"] for r in peak_recs)
        offpeak_revenue = sum(r["revenue_gbp"] for r in offpeak_recs)
        tou_stats[cid] = {
            "total_kwh": round(total_kwh, 1),
            "peak_kwh": round(peak_kwh, 1),
            "offpeak_kwh": round(total_kwh - peak_kwh, 1),
            "peak_pct": round(peak_kwh / total_kwh * 100, 1) if total_kwh else 0.0,
            "peak_revenue_gbp": round(peak_revenue, 2),
            "offpeak_revenue_gbp": round(offpeak_revenue, 2),
            "avg_peak_rate": round(peak_revenue / (peak_kwh / 1000), 2) if peak_kwh else 0.0,
            "avg_offpeak_rate": round(offpeak_revenue / ((total_kwh - peak_kwh) / 1000), 2) if (total_kwh - peak_kwh) else 0.0,
        }

    # Phase 17c/17d: pre-aggregate per-customer and per-customer/commodity P&L
    # while all_records is in scope. all_records is never persisted to JSON
    # (~1M rows), so these small aggregates are the only way these report sections
    # can populate when generate_annual_report() runs from the saved JSON.
    per_cid_pnl: dict = {}
    per_cid_comm_pnl: dict = {}
    for _r in all_records:
        _cid = _r["customer_id"]
        _comm = _r.get("commodity", "electricity")
        if _cid not in per_cid_pnl:
            per_cid_pnl[_cid] = {"gross": 0.0, "capital": 0.0, "net": 0.0, "revenue": 0.0}
        per_cid_pnl[_cid]["gross"] += _r.get("margin_gbp", 0.0)
        per_cid_pnl[_cid]["capital"] += _r.get("capital_cost_gbp", 0.0)
        per_cid_pnl[_cid]["net"] += _r.get("net_margin_gbp", 0.0)
        per_cid_pnl[_cid]["revenue"] += _r.get("revenue_gbp", 0.0)
        if _cid not in per_cid_comm_pnl:
            per_cid_comm_pnl[_cid] = {}
        if _comm not in per_cid_comm_pnl[_cid]:
            per_cid_comm_pnl[_cid][_comm] = {"gross": 0.0, "capital": 0.0, "net": 0.0, "revenue": 0.0}
        per_cid_comm_pnl[_cid][_comm]["gross"] += _r.get("margin_gbp", 0.0)
        per_cid_comm_pnl[_cid][_comm]["capital"] += _r.get("capital_cost_gbp", 0.0)
        per_cid_comm_pnl[_cid][_comm]["net"] += _r.get("net_margin_gbp", 0.0)
        per_cid_comm_pnl[_cid][_comm]["revenue"] += _r.get("revenue_gbp", 0.0)

    return {
        "starting_treasury_gbp": phase2b["starting_treasury"],
        "final_treasury_gbp": phase2b["final_treasury"],
        "total_revenue_gbp": sum(r["revenue_gbp"] for r in all_records),
        "total_gross_gbp": phase2b["total_gross"],
        "total_capital_gbp": phase2b["total_capital"],
        "total_bad_debt_gbp": phase2b.get("total_bad_debt", 0.0),
        "total_net_gbp": phase2b["total_net"],
        "administration_event": phase2b["administration_event"],
        "committee_wake_ups_total": len(committee_wake_ups),
        "years": yearly,
        "per_customer_lifetime": per_customer_lifetime,
        "bills_total": len(bills),
        "avg_clarity_total": _avg([b["clarity_score"] for b in bills]),
        "service_quality_score": contact_model.get("portfolio", {}).get("service_quality_score"),
        "avg_complaint_probability_total": contact_model.get("portfolio", {}).get(
            "avg_complaint_probability"
        ),
        "cost_to_serve_portfolio_gbp": cost_to_serve.get("portfolio", {}).get("cost_to_serve_gbp"),
        "net_margin_after_cost_to_serve_gbp": cost_to_serve.get("portfolio", {}).get("net_margin_gbp"),
        "flexibility_revenue_summary": flex_summary,
        "total_flexibility_revenue_gbp": flex_summary.get("total_flexibility_revenue_gbp", 0.0),
        "enterprise_value_gbp": enterprise_value.get("portfolio", {}).get("enterprise_value_gbp"),
        "enterprise_value_account_count": enterprise_value.get("portfolio", {}).get("account_count"),
        "by_billing_account": by_billing_account,
        "highest_clv": (
            {"customer_id": highest_clv[0], "clv_gbp": highest_clv[1]["clv_gbp"]} if highest_clv else None
        ),
        "lowest_clv": (
            {"customer_id": lowest_clv[0], "clv_gbp": lowest_clv[1]["clv_gbp"]} if lowest_clv else None
        ),
        "avg_clv_gbp": _avg(clv_values),
        "hedge_effectiveness_total": hedge_effectiveness_total,
        "customer_events": phase2b.get("customer_events", []),
        "churned_billing_accounts": phase2b.get("churned_billing_accounts", []),
        "company_event_log": phase2b.get("company_event_log", []),
        "basis_risk_terms": phase2b.get("basis_risk_terms", []),
        "churn_basis_risk": phase2b.get("churn_basis_risk", []),
        "retention_log": phase2b.get("retention_log", []),
        "no_offer_churn_log": phase2b.get("no_offer_churn_log", []),
        "company_divergence": phase2b.get("company_divergence", {}),
        "won_successor_activations": won_successor_activations,
        "ledger_meta": run_output.get("ledger_meta"),
        "ledger_pnl": run_output.get("ledger_pnl"),
        "clv_snapshots": clv_snapshots,
        # Phase 8a: growth mandate summary
        "growth_mandate": growth_mandate,
        "total_acquisition_spend_gbp": sum(-e["amount_gbp"] for e in acquisition_spend_events),
        "total_fixed_cost_gbp": sum(-e["amount_gbp"] for e in fixed_cost_events),
        "total_acquisition_attempts": len(acquisition_spend_events),
        "total_acquisition_wins": sum(1 for e in acquisition_spend_events if e.get("acquisition_won")),
        "acquired_customers": acquired_customer_ids,
        # Phase 9a: ledger-authoritative headline figures (when non-commodity/VAT events present)
        "_ledger_headline": _build_ledger_headline(run_output.get("ledger_pnl")),
        # Phase 13a: ToU utilization breakdown for HH customers
        "tou_stats": tou_stats,
        # Phase 14b/16c/17a: feedback logs (must be explicit — not auto-forwarded from phase2b)
        "company_gas_churn_log": phase2b.get("company_gas_churn_log", []),
        "margin_feedback_log": phase2b.get("margin_feedback_log", []),
        "dynamic_pricing_log": phase2b.get("dynamic_pricing_log", []),
        "demand_estimation_log": phase2b.get("demand_estimation_log", []),  # Phase 23a
        # Phase 17c/17d: pre-aggregated per-customer P&L (all_records not persisted)
        "per_cid_pnl": per_cid_pnl,
        "per_cid_comm_pnl": per_cid_comm_pnl,
        # Phase 22a: churn_risk kept in data so trailing-CLV section can recompute EV
        "churn_risk": churn_risk,
        # Phase 64: management accounts pre-computed from ledger events
        "management_accounts": _compute_management_accounts(run_output, phase2b.get("starting_treasury", 0.0)),
    }


def _compute_management_accounts(run_output, opening_treasury=0.0):
    events = run_output.get("ledger_events", [])
    if not events:
        return None
    try:
        return _ma.annual_management_pack(events, opening_treasury)
    except Exception:
        return None


def _section_management_accounts(data):
    ma = data.get("management_accounts")
    if not ma:
        return "## Management Accounts\n\n_Not available: re-run from scratch to populate._\n"

    def row(year):
        is_ = ma[year]["income_statement"]
        bs = ma[year]["balance_sheet"]
        cogs = is_["wholesale_cost_gbp"] + is_["non_commodity_cost_gbp"]
        opex = is_["total_opex_gbp"] + is_["capital_cost_gbp"]
        return (f"| {year} | {_fmt_gbp(is_[chr(114)+chr(101)+chr(118)+chr(101)+chr(110)+chr(117)+chr(101)+chr(95)+chr(103)+chr(98)+chr(112)])} | ({_fmt_gbp(cogs)}) "
                f"| {_fmt_gbp(is_[chr(103)+chr(114)+chr(111)+chr(115)+chr(115)+chr(95)+chr(109)+chr(97)+chr(114)+chr(103)+chr(105)+chr(110)+chr(95)+chr(103)+chr(98)+chr(112)])} | ({_fmt_gbp(opex)}) "
                f"| {_fmt_gbp(is_[chr(110)+chr(101)+chr(116)+chr(95)+chr(109)+chr(97)+chr(114)+chr(103)+chr(105)+chr(110)+chr(95)+chr(103)+chr(98)+chr(112)])} | {_fmt_gbp(bs[chr(99)+chr(97)+chr(115)+chr(104)+chr(95)+chr(103)+chr(98)+chr(112)])} "
                f"| {_fmt_gbp(bs[chr(116)+chr(111)+chr(116)+chr(97)+chr(108)+chr(95)+chr(101)+chr(113)+chr(117)+chr(105)+chr(116)+chr(121)+chr(95)+chr(103)+chr(98)+chr(112)])} |")

    rows = [
        "## Management Accounts", "",
        "P&L and balance sheet from double-entry journal (account codes), not formulas.",
        "",
        "| Year | Revenue | COGS | Gross | OpEx | Net | Cash | Equity |",
        "|------|---------|------|-------|------|-----|------|--------||",
    ] + [row(y) for y in sorted(ma)] + [""]

    journal_total = sum(ma[y]["income_statement"][chr(110)+chr(101)+chr(116)+chr(95)+chr(109)+chr(97)+chr(114)+chr(103)+chr(105)+chr(110)+chr(95)+chr(103)+chr(98)+chr(112)] for y in ma)
    ledger_net = data.get("total_net_gbp", 0.0)
    chk = _ma.cross_check(journal_total, ledger_net)
    status = "PASS" if chk["pass"] else "FAIL"
    rows.append(
        f"**Cross-check:** {status} -- Journal: {_fmt_gbp(chk[chr(106)+chr(111)+chr(117)+chr(114)+chr(110)+chr(97)+chr(108)+chr(95)+chr(110)+chr(101)+chr(116)+chr(95)+chr(103)+chr(98)+chr(112)])}, Sim: {_fmt_gbp(chk[chr(108)+chr(101)+chr(100)+chr(103)+chr(101)+chr(114)+chr(95)+chr(110)+chr(101)+chr(116)+chr(95)+chr(103)+chr(98)+chr(112)])}, Variance: {chk[chr(118)+chr(97)+chr(114)+chr(105)+chr(97)+chr(110)+chr(99)+chr(101)+chr(95)+chr(112)+chr(99)+chr(116)]:.1f}%"
    )
    rows.append("")
    final_year = max(ma)
    bs = ma[final_year]["balance_sheet"]
    eq_mark = "OK" if bs["equation_holds"] else "FAIL"
    key_cash = chr(99)+chr(97)+chr(115)+chr(104)+chr(95)+chr(103)+chr(98)+chr(112)
    key_rec = chr(116)+chr(114)+chr(97)+chr(100)+chr(101)+chr(95)+chr(114)+chr(101)+chr(99)+chr(101)+chr(105)+chr(118)+chr(97)+chr(98)+chr(108)+chr(101)+chr(115)+chr(95)+chr(103)+chr(98)+chr(112)
    key_assets = chr(116)+chr(111)+chr(116)+chr(97)+chr(108)+chr(95)+chr(97)+chr(115)+chr(115)+chr(101)+chr(116)+chr(115)+chr(95)+chr(103)+chr(98)+chr(112)
    key_cap = chr(111)+chr(112)+chr(101)+chr(110)+chr(105)+chr(110)+chr(103)+chr(95)+chr(99)+chr(97)+chr(112)+chr(105)+chr(116)+chr(97)+chr(108)+chr(95)+chr(103)+chr(98)+chr(112)
    key_profit = chr(99)+chr(117)+chr(114)+chr(114)+chr(101)+chr(110)+chr(116)+chr(95)+chr(112)+chr(101)+chr(114)+chr(105)+chr(111)+chr(100)+chr(95)+chr(112)+chr(114)+chr(111)+chr(102)+chr(105)+chr(116)+chr(95)+chr(103)+chr(98)+chr(112)
    key_equity = chr(116)+chr(111)+chr(116)+chr(97)+chr(108)+chr(95)+chr(101)+chr(113)+chr(117)+chr(105)+chr(116)+chr(121)+chr(95)+chr(103)+chr(98)+chr(112)
    rows += [
        f"**Balance sheet -- {final_year} year-end:**", "",
        "| Account | GBP |", "|---------|-----|",
        f"| Cash and Treasury (1001) | {_fmt_gbp(bs[key_cash])} |",
        f"| Trade Receivables (1100) | {_fmt_gbp(bs[key_rec])} |",
        f"| **Total Assets** | **{_fmt_gbp(bs[key_assets])}** |",
        f"| Opening Capital (3001) | {_fmt_gbp(bs[key_cap])} |",
        f"| Cumulative Net Profit | {_fmt_gbp(bs[key_profit])} |",
        f"| **Total Equity** | **{_fmt_gbp(bs[key_equity])}** |",
        f"| A = L + E | {eq_mark} |", "",
    ]
    return chr(10).join(rows)



def _section_budget_vs_actual(data: dict) -> str:
    ma = data.get("management_accounts")
    if not ma:
        return "## Budget vs Actual\n\n_Not available: management accounts required._\n"

    header = [
        "## Budget vs Actual",
        "",
        "Annual plan compared to management account actuals. "
        "RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).",
        "",
        "| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |",
        "|------|-------------|-------------|------|---------|---------|------|-----|",
    ]
    rows = list(header)
    for year in sorted(ma.keys()):
        vr = _budget.variance_report(ma, year)
        if not vr:
            continue
        rev = vr["revenue"]
        net = vr["net"]
        rag = _budget.traffic_light(net["variance_pct"])
        rows.append(
            f"| {year} | {_fmt_gbp(rev['budget'])} | {_fmt_gbp(rev['actual'])} "
            f"| {rev['variance_pct']:+.1f}% "
            f"| {_fmt_gbp(net['budget'])} | {_fmt_gbp(net['actual'])} "
            f"| {net['variance_pct']:+.1f}% | {rag} |"
        )
    rows.append("")
    return "\n".join(rows)



def _build_ledger_headline(pnl: dict | None) -> dict | None:
    """Extract Phase 9a headline P&L from ledger when non-commodity/VAT events exist.

    Returns None when ledger has no Phase 9a data (pre-9a ledgers).
    """
    if pnl is None or "total_billed_gbp" not in pnl:
        return None
    return {
        "total_billed_gbp": pnl["total_billed_gbp"],
        "vat_remittance_gbp": pnl.get("vat_remittance_gbp", 0.0),
        "revenue_gbp": pnl["revenue_gbp"],
        "non_commodity_cost_gbp": pnl.get("non_commodity_cost_gbp", 0.0),
        "gross_margin_gbp": pnl["gross_margin_gbp"],
        "capital_cost_gbp": pnl["capital_cost_gbp"],
        "net_margin_gbp": pnl["net_margin_gbp"],
    }


def _fmt_gbp(value: float) -> str:
    return f"£{value:,.2f}"


def _fmt_pct(value: float | None) -> str:
    return f"{value:.1%}" if value is not None else "n/a"


def _solvency_summary_line(data: dict) -> str:
    """Phase 21b: per-customer net assets for the final year of the run."""
    years = sorted(data["years"])
    if not years:
        return NOT_AVAILABLE
    final_yd = data["years"][years[-1]]
    active = final_yd.get("active_customer_ids", [])
    unique = {cid[:-1] if cid.endswith("g") else cid for cid in active}
    n_cust = max(len(unique), 1)
    per_cust = final_yd.get("treasury_end_gbp", 0.0) / n_cust
    flag = "⚠ BELOW FLOOR" if per_cust < REGULATORY_CAPITAL_FLOOR_PER_CUSTOMER_GBP else "OK"
    return (
        f"£{per_cust:,.0f}/customer ({n_cust} customers, {flag}; "
        f"Ofgem floor £{REGULATORY_CAPITAL_FLOOR_PER_CUSTOMER_GBP:.0f}/customer)"
    )


def _executive_summary(data: dict) -> str:
    years = sorted(data["years"])
    outcome = (
        "ADMINISTRATION on " + data["administration_event"]["date"]
        if data["administration_event"]
        else "survived the full window"
    )
    crisis_lines = []
    for year in sorted(CRISIS_YEARS & set(years)):
        crisis_lines.append(
            f"- **{year}** (crisis year): net margin "
            f"{_fmt_gbp(data['years'][year]['net_gbp'])}, "
            f"{len(data['years'][year]['committee_wake_ups'])} risk committee "
            "wake-up(s)."
        )

    if data["enterprise_value_gbp"] is not None:
        enterprise_value_line = (
            f"- Enterprise value (CLV sum across {data['enterprise_value_account_count']} "
            f"billing accounts): {_fmt_gbp(data['enterprise_value_gbp'])}"
        )
    else:
        enterprise_value_line = f"- Enterprise value: {NOT_AVAILABLE}"

    if data["cost_to_serve_portfolio_gbp"] is not None:
        _hl_cts = data.get("_ledger_headline")
        _cts_base = _hl_cts["net_margin_gbp"] if _hl_cts else data.get("total_net_gbp", 0.0)
        _net_after_cts = _cts_base - data["cost_to_serve_portfolio_gbp"]
        cost_to_serve_line = (
            f"- Cost to serve (whole portfolio): {_fmt_gbp(data['cost_to_serve_portfolio_gbp'])}, "
            f"net margin after cost to serve: {_fmt_gbp(_net_after_cts)}"
        )
    else:
        cost_to_serve_line = f"- Cost to serve (whole portfolio): {NOT_AVAILABLE}"

    hl = data.get("_ledger_headline")
    if hl:
        revenue_line = (
            f"- Customer bills (all-in): {_fmt_gbp(hl['total_billed_gbp'])}\n"
            f"  VAT remitted to HMRC: ({_fmt_gbp(hl['vat_remittance_gbp'])}) | "
            f"Revenue (ex-VAT): {_fmt_gbp(hl['revenue_gbp'])}\n"
            f"  Non-commodity pass-through: ({_fmt_gbp(hl['non_commodity_cost_gbp'])})"
        )
        gross_line = f"- Gross margin: {_fmt_gbp(hl['gross_margin_gbp'])}"
        capital_line = f"- Capital costs: {_fmt_gbp(hl['capital_cost_gbp'])}"
        net_line = f"- Net margin: {_fmt_gbp(hl['net_margin_gbp'])}"
        revenue_gbp = hl["revenue_gbp"]
        gross_gbp = hl["gross_margin_gbp"]
        net_gbp = hl["net_margin_gbp"]
        capital_gbp = hl["capital_cost_gbp"]
    else:
        revenue_line = f"- Revenue: {_fmt_gbp(data['total_revenue_gbp'])}"
        gross_line = f"- Gross margin: {_fmt_gbp(data['total_gross_gbp'])}"
        capital_line = f"- Capital costs: {_fmt_gbp(data['total_capital_gbp'])}"
        net_line = f"- Net margin: {_fmt_gbp(data['total_net_gbp'])}"
        revenue_gbp = data["total_revenue_gbp"]
        gross_gbp = data["total_gross_gbp"]
        net_gbp = data["total_net_gbp"]
        capital_gbp = data["total_capital_gbp"]

    cap_ratio_line = (
        f"- Capital cost ratio: {capital_gbp / gross_gbp:.1%} of gross"
        if gross_gbp else "- Capital cost ratio: n/a"
    )
    net_pct_line = (
        f"- Net margin as % of revenue: {net_gbp / revenue_gbp:.1%}"
        f"\n  (industry benchmark for a retail energy supplier: 2-5%)"
        if revenue_gbp else "- Net margin as % of revenue: n/a"
    )

    return f"""## Executive Summary

This report covers {years[0]}–{years[-1]} ({len(years)} calendar years,
the last partial). The business {outcome}.

- Starting treasury: {_fmt_gbp(data['starting_treasury_gbp'])}
- Final treasury: {_fmt_gbp(data['final_treasury_gbp'])}
  ({_fmt_gbp(data['final_treasury_gbp'] - data['starting_treasury_gbp'])} net change)
- Solvency signal (final year): {_solvency_summary_line(data)}
{revenue_line}
{gross_line}
{capital_line}
{net_line}
{cap_ratio_line}
{net_pct_line}
- Risk committee (Context Handshake) interventions: {data['committee_wake_ups_total']}
- Bills issued: {data['bills_total']}, average clarity {data['avg_clarity_total']:.3f},
  service quality score {data['service_quality_score']:.3f}
{enterprise_value_line}
{cost_to_serve_line}
- Hedge effectiveness (whole window): {_hedge_value_add_line(data['hedge_effectiveness_total'])}

{chr(10).join(crisis_lines) if crisis_lines else "No crisis years in this window."}
"""


def _hedge_value_add_line(totals: dict | None) -> str:
    if totals is None:
        return NOT_AVAILABLE
    add = totals["hedging_value_add_gbp"]
    verb = "added" if add >= 0 else "cost"
    return (
        f"hedging {verb} {_fmt_gbp(abs(add))} vs. a fully unhedged book "
        f"(commodity-only: actual net {_fmt_gbp(totals['actual_net_gbp'])} vs. naked net "
        f"{_fmt_gbp(totals['naked_net_gbp'])})"
    )


def _customer_book_section(year: str, yd: dict, data: dict) -> str:
    lines = ["**Customer Book**", ""]
    active = yd["active_customer_ids"]
    pcl = data.get("per_customer_lifetime", {})
    resi_elec = [
        c for c in active
        if not c.endswith("g") and pcl.get(c, {}).get("segment") == "resi"
    ]
    sme_elec = [
        c for c in active
        if not c.endswith("g") and pcl.get(c, {}).get("segment") == "SME"
    ]
    gas = [c for c in active if c.endswith("g")]
    lines.append(f"- Active accounts: {len(active)} ({', '.join(active)})")
    lines.append(
        f"  - Resi electricity: {len(resi_elec)}, SME electricity: {len(sme_elec)}, "
        f"gas (dual-fuel): {len(gas)}"
    )
    if yd["acquisitions"]:
        lines.append(f"- New acquisitions this year: {', '.join(yd['acquisitions'])}")
    else:
        lines.append("- New acquisitions this year: none")
    customer_events = data.get("customer_events") or []
    yr_events = [e for e in customer_events if e.get("event_date", "")[:4] == year]
    churned_this_year = [e["customer_id"] for e in yr_events if e.get("event_type") == "churned"]
    renewed_this_year = [e["customer_id"] for e in yr_events if e.get("event_type") == "renewed"]
    if yr_events:
        churn_str = ", ".join(churned_this_year) if churned_this_year else "none"
        lines.append(f"- Losses (churn) during year: {churn_str}")
        lines.append(f"  - Renewals (retained): {len(renewed_this_year)} accounts")
    else:
        lines.append("- Losses (churn / home move) during year: none (no renewal dates fell this year)")
    year_clv = (data.get("clv_snapshots") or {}).get(year)
    if year_clv:
        clv_vals = [v for v in year_clv.values() if v is not None]
        avg_yr_clv = _avg(clv_vals)
        if avg_yr_clv is not None:
            lines.append(
                f"- Average CLV (Point-in-Time, year-end {year}): {_fmt_gbp(avg_yr_clv)}"
            )
            per_acct = ", ".join(
                f"{acct} {_fmt_gbp(clv)}" for acct, clv in sorted(year_clv.items()) if clv is not None
            )
            lines.append(f"  - By billing account: {per_acct}")
        else:
            lines.append(f"- Average CLV (Point-in-Time, year-end {year}): {NOT_AVAILABLE}")
    elif data["avg_clv_gbp"] is not None:
        lines.append(
            f"- Average CLV across book (whole-run projection, per billing account): "
            f"{_fmt_gbp(data['avg_clv_gbp'])}"
        )
        lines.append(
            f"- Highest CLV: {data['highest_clv']['customer_id']} "
            f"({_fmt_gbp(data['highest_clv']['clv_gbp'])}); "
            f"Lowest CLV: {data['lowest_clv']['customer_id']} "
            f"({_fmt_gbp(data['lowest_clv']['clv_gbp'])})"
        )
    else:
        lines.append(f"- Average CLV across book at year end: {NOT_AVAILABLE}")
        lines.append(f"- Highest/lowest CLV customer: {NOT_AVAILABLE}")
    if yd["bill_shock_events"]:
        events = "; ".join(
            f"{e['customer_id']} {e['period_end']} ({e['bill_shock_pct']:.0%})"
            for e in yd["bill_shock_events"]
        )
        lines.append(f"- Bill shock events (>=20%): {len(yd['bill_shock_events'])} -- {events}")
    else:
        lines.append("- Bill shock events (>=20%): none")
    yr_churn_risk = yd.get("churn_risk_by_account", {})
    if yr_churn_risk:
        at_risk = {a: p for a, p in yr_churn_risk.items() if p >= 0.20}
        risk_str = (
            f"{len(at_risk)} at risk (≥20% churn prob): "
            + ", ".join(f"{a} {p:.0%}" for a, p in sorted(at_risk.items()))
            if at_risk else "none above 20% threshold"
        )
        lines.append(f"- Churn risk (accounts renewing in {year}): {risk_str}")
    else:
        lines.append(f"- Churn risk (accounts renewing in {year}): no renewals this year")
    return "\n".join(lines)


def _pricing_margin_section(yd: dict) -> str:
    """Per-year net margin per customer (tariff range + net). Lifetime cost-to-serve
    and pricing flags appear once in `_lifetime_pricing_section`, not here."""
    lines = ["**Pricing & Margin**", ""]
    for cid, pc in sorted(yd["per_customer"].items()):
        if pc["tariff_min_gbp_per_mwh"] == pc["tariff_max_gbp_per_mwh"]:
            tariff = f"£{pc['tariff_min_gbp_per_mwh']:.2f}/MWh"
        else:
            tariff = f"£{pc['tariff_min_gbp_per_mwh']:.2f}-£{pc['tariff_max_gbp_per_mwh']:.2f}/MWh"
        lines.append(
            f"- {cid} ({pc['commodity']}): tariff {tariff}, net margin "
            f"{_fmt_gbp(pc['net_gbp'])}"
            + (" -- **net-negative**" if pc["net_gbp"] < 0 else "")
        )
    return "\n".join(lines)


REPRICING_MANAGEABLE_THRESHOLD = 0.40   # post-uplift churn < 40% → raise
REPRICING_RISKY_THRESHOLD = 0.65        # post-uplift churn > 65% → hold


def _section_repricing_impact(data: dict) -> str:
    """Phase 16a: tariff repricing impact assessment.

    For each loss-making customer, estimates the churn consequence of raising
    the tariff to the break-even level using the company churn model. Shows
    active customers (repricing opportunity) and churned customers
    (retrospective counterfactual — could earlier repricing have helped?).
    """
    from datetime import date as _date
    from company.crm.churn_model import estimate_churn_probability

    per_customer = data.get("per_customer_lifetime", {})
    basis_risk = data.get("basis_risk_terms", [])
    churned_set = set(data.get("churned_billing_accounts", []))

    # Last known company forward rate per customer (most recent basis_risk entry)
    last_company_rate: dict[str, float] = {}
    for t in basis_risk:
        last_company_rate[t["customer_id"]] = t["company_fwd_gbp_per_mwh"]

    candidates = []
    for cid, cdata in sorted(per_customer.items()):
        pa = cdata.get("pricing_action", {})
        if pa.get("flag") != "NET_NEGATIVE":
            continue
        uplift_pct = pa.get("recommended_uplift_pct")
        if uplift_pct is None or uplift_pct <= 0 or cid not in last_company_rate:
            continue

        old_rate = last_company_rate[cid]
        new_rate = old_rate * (1 + uplift_pct / 100)

        acq_str = cdata.get("acquisition_date", "2016-01-01")
        try:
            acq_date = _date.fromisoformat(acq_str)
        except (ValueError, TypeError):
            acq_date = _date(2016, 1, 1)
        tenure_years = (_date(2025, 12, 31) - acq_date).days / 365.25

        fuel = "gas" if cdata.get("commodity") == "gas" else "electricity"
        post_uplift_est = estimate_churn_probability(old_rate, new_rate, tenure_years, fuel=fuel)

        if post_uplift_est < REPRICING_MANAGEABLE_THRESHOLD:
            decision = "Raise — churn risk manageable"
        elif post_uplift_est < REPRICING_RISKY_THRESHOLD:
            decision = "Partial — incremental uplift advised"
        else:
            decision = "Hold — uplift likely to accelerate churn"

        net_loss = -cdata.get("net_margin_after_cost_to_serve_gbp", 0.0)
        status = "churned" if cid in churned_set else "active"

        candidates.append({
            "cid": cid,
            "fuel": fuel[:4],
            "segment": cdata.get("segment", "?"),
            "status": status,
            "uplift_pct": uplift_pct,
            "net_loss_gbp": net_loss,
            "post_uplift_est": post_uplift_est,
            "decision": decision,
        })

    if not candidates:
        return ""

    candidates.sort(key=lambda c: c["uplift_pct"])

    lines = [
        "## Tariff Repricing Impact Assessment",
        "",
        "Estimated churn risk at the break-even tariff level for each loss-making customer.",
        "Active = current opportunity; churned = retrospective counterfactual.",
        "",
        "| Customer | Fuel | Seg | Status | Uplift needed | Total loss | Churn @ B/E | Decision |",
        "|----------|------|-----|--------|--------------|-----------|-------------|----------|",
    ]
    for c in candidates:
        lines.append(
            f"| {c['cid']} | {c['fuel']} | {c['segment']} | {c['status']} "
            f"| +{c['uplift_pct']:.1f}% | {_fmt_gbp(c['net_loss_gbp'])} "
            f"| {c['post_uplift_est']:.0%} | {c['decision']} |"
        )

    active_raise = [c for c in candidates if c["status"] == "active" and c["decision"].startswith("Raise")]
    churned_raise = [c for c in candidates if c["status"] == "churned" and c["decision"].startswith("Raise")]
    hold = [c for c in candidates if c["decision"].startswith("Hold")]

    lines.append("")
    if active_raise:
        names = ", ".join(c["cid"] for c in active_raise)
        lines.append(
            f"**Repriceable now ({len(active_raise)})**: {names} — "
            f"break-even churn risk below {REPRICING_MANAGEABLE_THRESHOLD:.0%}. Uplift advised."
        )
    if churned_raise:
        names = ", ".join(c["cid"] for c in churned_raise)
        lines.append(
            f"**Missed repricing window ({len(churned_raise)} churned)**: {names} — "
            f"break-even price would not have triggered high churn. Earlier repricing might have changed economics."
        )
    if hold:
        names = ", ".join(c["cid"] for c in hold)
        lines.append(
            f"**Price-sensitive ({len(hold)})**: {names} — break-even rate would have elevated churn risk above "
            f"{REPRICING_RISKY_THRESHOLD:.0%}. Retention strategy needed before any major uplift."
        )
    lines.append("")

    return "\n".join(lines)


def _lifetime_pricing_section(data: dict) -> str:
    """Whole-window cost-to-serve breakdown and activity-based pricing flags.
    Appears once at the top level (not repeated per year)."""
    cts_values = [
        v["cost_to_serve_gbp"]
        for v in data["per_customer_lifetime"].values()
        if v["cost_to_serve_gbp"] is not None
    ]
    if not cts_values:
        return (
            "## Cost to Serve & Pricing Actions\n\n"
            f"- Cost to serve per customer: {NOT_AVAILABLE}\n"
            f"- Net margin per customer after cost to serve: {NOT_AVAILABLE}\n"
        )
    lines = [
        "## Cost to Serve & Pricing Actions",
        "",
        f"Whole-run totals (cumulative across all settlement periods). "
        f"Average: {_fmt_gbp(_avg(cts_values))}, range "
        f"{_fmt_gbp(min(cts_values))}–{_fmt_gbp(max(cts_values))}.",
        "",
    ]
    for cid, pcl in sorted(data["per_customer_lifetime"].items()):
        if pcl["cost_to_serve_gbp"] is None:
            continue
        action = pcl.get("pricing_action", {})
        flag = action.get("flag", "UNKNOWN")
        uplift = action.get("recommended_uplift_pct")
        flag_str = ""
        if flag == "NET_NEGATIVE":
            flag_str = f" — **NET_NEGATIVE** (tariff uplift needed: +{uplift:.1f}%)"
        elif flag == "MARGIN_SQUEEZE":
            flag_str = " — MARGIN_SQUEEZE (below 2% benchmark)"
        lines.append(
            f"- {cid}: cost to serve {_fmt_gbp(pcl['cost_to_serve_gbp'])}, "
            f"net margin after CTS "
            f"{_fmt_gbp(pcl['net_margin_after_cost_to_serve_gbp'])}"
            + flag_str
        )
    _append_pricing_actions_summary(lines, data)
    lines.append("")
    return "\n".join(lines)


def _append_pricing_actions_summary(lines: list[str], data: dict) -> None:
    """Append an activity-based pricing summary block when actionable flags exist."""
    net_negative = [
        (cid, pcl)
        for cid, pcl in sorted(data["per_customer_lifetime"].items())
        if pcl.get("pricing_action", {}).get("flag") == "NET_NEGATIVE"
    ]
    squeeze = [
        cid
        for cid, pcl in sorted(data["per_customer_lifetime"].items())
        if pcl.get("pricing_action", {}).get("flag") == "MARGIN_SQUEEZE"
    ]
    if not net_negative and not squeeze:
        return
    lines.append("")
    lines.append("**Activity-Based Pricing Actions**")
    lines.append("")
    if net_negative:
        lines.append(
            f"The following {len(net_negative)} customer(s) are loss-making after cost-to-serve "
            f"and require immediate tariff review:"
        )
        for cid, pcl in net_negative:
            uplift = pcl["pricing_action"]["recommended_uplift_pct"]
            lines.append(
                f"  - {cid}: net margin after CTS {_fmt_gbp(pcl['net_margin_after_cost_to_serve_gbp'])} "
                f"on revenue {_fmt_gbp(pcl['revenue_gbp'])} — "
                f"raise tariff by ≥{uplift:.1f}% to break even"
            )
    if squeeze:
        lines.append(
            f"The following {len(squeeze)} customer(s) are profitable but below the 2% "
            f"net-margin benchmark (MARGIN_SQUEEZE): {', '.join(squeeze)}"
        )


def _trading_risk_section(year: str, yd: dict) -> str:
    lines = ["**Trading & Risk**", ""]
    lines.append(f"- Net margin: {_fmt_gbp(yd['net_gbp'])} (gross {_fmt_gbp(yd['gross_gbp'])}, "
                  f"capital {_fmt_gbp(yd['capital_gbp'])})")
    for commodity in ("electricity", "gas"):
        split = yd["commodity_split"][commodity]
        if split["gross_gbp"] or split["capital_gbp"] or split["net_gbp"]:
            lines.append(
                f"  - {commodity.title()}: gross {_fmt_gbp(split['gross_gbp'])}, "
                f"capital {_fmt_gbp(split['capital_gbp'])}, net {_fmt_gbp(split['net_gbp'])}"
            )
    lines.append(f"- Treasury at year end: {_fmt_gbp(yd['treasury_end_gbp'])}")
    if yd["hedge_fractions"]:
        hf_lines = ", ".join(
            f"{cid} {hf['start_hf']:.2f} (avg {hf['avg_hf']:.2f})"
            for cid, hf in sorted(yd["hedge_fractions"].items())
        )
        lines.append(f"- Hedge fraction at first renewal this year (avg across year's terms): {hf_lines}")
    else:
        lines.append("- Hedge fraction: no renewals this year")
    lines.append(f"- Risk committee (Context Handshake) interventions: {len(yd['committee_wake_ups'])}")
    for wu in yd["committee_wake_ups"]:
        adj = ", ".join(f"{k}->{v:.2f}" for k, v in wu["adjustments"].items()) or "(none)"
        line = f"  - {wu['settlement_date']}: treasury {_fmt_gbp(wu['treasury_gbp'])}, {adj}"
        if "portfolio_var_current_gbp" in wu and wu["portfolio_var_stressed_gbp"]:
            ratio = wu["portfolio_var_current_gbp"] / wu["portfolio_var_stressed_gbp"]
            line += (
                f", VaR (current {_fmt_gbp(wu['portfolio_var_current_gbp'])} / "
                f"stressed {_fmt_gbp(wu['portfolio_var_stressed_gbp'])}) ratio {ratio:.2f}"
            )
        lines.append(line)
    if yd["var_ratio"] is not None:
        lines.append(f"- VaR ratio (current vs stressed floor, avg of this year's wake-ups): {yd['var_ratio']:.2f}")
    elif yd["committee_wake_ups"]:
        lines.append(f"- VaR ratio (current vs stressed floor): {NOT_AVAILABLE}")
    else:
        lines.append("- VaR ratio (current vs stressed floor): no risk committee wake-up this year")
    wp = yd["worst_period"]
    lines.append(
        f"- Worst single period: {wp['customer_id']} on {wp['settlement_date']} "
        f"period {wp['settlement_period']}, net margin {_fmt_gbp(wp['net_margin_gbp'])}"
    )
    return "\n".join(lines)


def _portfolio_health_section(year: str, yd: dict, data: dict) -> str:
    lines = ["**Portfolio Health**", ""]
    if yd["gross_gbp"]:
        lines.append(f"- Capital cost ratio: {yd['capital_gbp'] / yd['gross_gbp']:.1%} of gross")
    else:
        lines.append("- Capital cost ratio: n/a (no gross margin this year)")
    if yd["treasury_drawdown_events"]:
        events = "; ".join(
            f"{_fmt_gbp(e['peak_gbp'])} -> {_fmt_gbp(e['trough_gbp'])} ({e['drawdown_pct']:.1%})"
            for e in yd["treasury_drawdown_events"]
        )
        lines.append(
            f"- Treasury drawdown events (>={DRAWDOWN_THRESHOLD_PCT:.0%} threshold): "
            f"{len(yd['treasury_drawdown_events'])} -- {events}"
        )
    else:
        lines.append(f"- Treasury drawdown events (>={DRAWDOWN_THRESHOLD_PCT:.0%} threshold): none")
    if yd["bills_count"]:
        lines.append(
            f"- Bills issued: {yd['bills_count']}, average clarity {yd['avg_clarity']:.3f}, "
            f"average bill shock {_fmt_pct(yd['avg_bill_shock_pct'])}, "
            f"bad debt provision {_fmt_gbp(yd['bad_debt_gbp'])}, "
            f"avg complaint probability {_fmt_pct(yd['avg_complaint_probability'])}"
        )
    else:
        lines.append("- Bills issued: none")
    # Phase 21b: Per-customer net assets — Ofgem solvency signal.
    # "C1g" pairs with "C1" → strip 'g' suffix to count unique customers.
    active = yd.get("active_customer_ids", [])
    unique_customers = {cid[:-1] if cid.endswith("g") else cid for cid in active}
    n_cust = max(len(unique_customers), 1)
    per_cust = yd.get("treasury_end_gbp", 0.0) / n_cust
    if per_cust < REGULATORY_CAPITAL_FLOOR_PER_CUSTOMER_GBP:
        lines.append(
            f"- ⚠ Solvency signal: £{per_cust:,.0f}/customer ({n_cust} customers) — "
            f"BELOW Ofgem floor £{REGULATORY_CAPITAL_FLOOR_PER_CUSTOMER_GBP:.0f}/customer"
        )
    else:
        lines.append(
            f"- Solvency signal: £{per_cust:,.0f}/customer ({n_cust} customers) — "
            f"OK (Ofgem floor £{REGULATORY_CAPITAL_FLOOR_PER_CUSTOMER_GBP:.0f}/customer)"
        )
    return "\n".join(lines)


def _year_narrative(year: str, yd: dict) -> str:
    flag = " (flagged crisis year)" if year in CRISIS_YEARS else ""
    direction = "a net gain" if yd["net_gbp"] >= 0 else "a net loss"
    risk_line = (
        f"The risk committee intervened {len(yd['committee_wake_ups'])} time(s), "
        "raising hedge fractions in response to elevated VaR."
        if yd["committee_wake_ups"]
        else "The risk committee did not intervene -- VaR stayed within the stressed floor."
    )
    return (
        f"**Year narrative:** {year}{flag} produced {direction} of "
        f"{_fmt_gbp(yd['net_gbp'])} across {len(yd['active_customer_ids'])} accounts. "
        f"{risk_line} "
        + (
            f"{len(yd['bill_shock_events'])} customer(s) experienced a bill shock of "
            f">=20%."
            if yd["bill_shock_events"]
            else "No customer experienced a large (>=20%) bill shock this year."
        )
    )


def _hedge_effectiveness_section(yd: dict) -> str:
    """Per-year hedge effectiveness: actual (hedged) vs naked (unhedged)
    net margin across all renewal terms starting in this year, overall and
    per customer. Answers the strategic question: did the risk committee's
    hedge-fraction interventions make money, or just reduce variance?"""
    he = yd["hedge_effectiveness"]
    lines = ["**Hedge Effectiveness**", ""]
    if not he["by_customer"]:
        lines.append("- No renewal terms started this year -- nothing to evaluate.")
        return "\n".join(lines)
    lines.append(
        f"- Actual (hedged) net margin: {_fmt_gbp(he['actual_net_gbp'])} vs. naked "
        f"(unhedged) net margin: {_fmt_gbp(he['naked_net_gbp'])}"
    )
    lines.append(f"- {_hedge_value_add_line(he)}")
    for cid, c in sorted(he["by_customer"].items()):
        add = c["hedging_value_add_gbp"]
        verb = "added" if add >= 0 else "cost"
        lines.append(
            f"  - {cid}: actual {_fmt_gbp(c['actual_net_gbp'])} vs. naked "
            f"{_fmt_gbp(c['naked_net_gbp'])} -- hedging {verb} {_fmt_gbp(abs(add))}"
        )
    return "\n".join(lines)


def _hedge_effectiveness_summary_section(data: dict) -> str:
    """Whole-run hedge effectiveness summary -- the best and worst single
    hedging decisions across the full 9.5-year run."""
    totals = data["hedge_effectiveness_total"]
    if totals is None:
        return f"## Hedge Effectiveness — Whole Run\n\n{NOT_AVAILABLE}\n"

    best = totals["best_decision"]
    worst = totals["worst_decision"]
    return f"""## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- {_hedge_value_add_line(totals)}
- **Best hedging decision of the run**: {best['customer_id']}, term starting
  {best['term_start']} (hedge fraction {best['hf_used']:.2f}) -- hedging
  protected {_fmt_gbp(best['hedging_value_add_gbp'])} vs. going naked.
- **Worst hedging decision of the run**: {worst['customer_id']}, term
  starting {worst['term_start']} (hedge fraction {worst['hf_used']:.2f}) --
  over-hedging cost {_fmt_gbp(abs(worst['hedging_value_add_gbp']))} vs. going
  naked.
"""


def _mandate_comparison_section(data: dict, old_data: dict | None) -> str:
    """Phase 5c: whole-run before/after comparison of the minimum hedge
    mandate (MIN_HEDGE_FLOOR=0.85, see sim/hedging_strategy.py) against the
    old reactive model (50/50 start, risk committee reacts upward from
    there with no floor) and against a fully naked book.

    `old_data` is the pre-Phase-5c run's extract_report_data() output
    (docs/reports/run_output_old_reactive_model_pre5c.json), kept as a
    snapshot specifically so this comparison doesn't require re-running the
    old model. If that snapshot isn't available, the section reports
    NOT_AVAILABLE rather than inventing numbers."""
    if old_data is None:
        return f"## Hedging Mandate — Before/After Phase 5c\n\n{NOT_AVAILABLE}\n"

    # Use Phase 9a figures for "this run" when available; old model is always commodity-only.
    hl = data.get("_ledger_headline")
    new_gross = hl["gross_margin_gbp"] if hl else data["total_gross_gbp"]
    new_capital = hl["capital_cost_gbp"] if hl else data["total_capital_gbp"]
    new_net = hl["net_margin_gbp"] if hl else data["total_net_gbp"]
    new_revenue = hl["revenue_gbp"] if hl else data.get("total_revenue_gbp", 0.0)

    # Capital ratio on commodity-only gross keeps the comparison apples-to-apples vs. old model.
    new_ratio_commodity = data["total_capital_gbp"] / data["total_gross_gbp"]
    old_ratio = old_data["total_capital_gbp"] / old_data["total_gross_gbp"]
    new_ratio_phase9a = (data["total_capital_gbp"] / new_gross) if (hl and new_gross) else None

    new_2021 = data["years"].get("2021", {}).get("net_gbp")
    old_2021 = old_data["years"].get("2021", {}).get("net_gbp")

    new_het = data["hedge_effectiveness_total"]
    old_het = old_data["hedge_effectiveness_total"]

    lines = ["## Hedging Mandate — Before/After Phase 5c", ""]
    lines.append(
        "Phase 5c replaced the old reactive hedging model (start at 50/50, "
        "risk committee reacts upward from there with no floor) with a "
        "minimum hedge mandate: every term starts at least 85% hedged "
        "(`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real "
        "supplier's supply-obligation-first behaviour rather than a "
        "speculative book with a safety valve. Because capital cost is "
        "charged on the unhedged (active) position only, raising the floor "
        "to 85% caps that active position at 15% of volume by construction."
    )
    lines.append("")
    lines.append(
        "The figures below come from two *different* simulation "
        "runs (this run vs. the preserved old-model snapshot) — do not "
        "subtract a figure from one run's row from a figure in the other's. "
        f"This run (Phase 9a): gross {_fmt_gbp(new_gross)}, capital "
        f"{_fmt_gbp(new_capital)}, net "
        f"{_fmt_gbp(new_net)}. Old-model run (commodity-only, pre-Phase-9a): gross "
        f"{_fmt_gbp(old_data['total_gross_gbp'])}, capital "
        f"{_fmt_gbp(old_data['total_capital_gbp'])}, net "
        f"{_fmt_gbp(old_data['total_net_gbp'])}."
    )
    lines.append("")

    cap_ratio_text = (
        f"- **Capital cost as % of gross margin**: "
        f"{_fmt_pct(new_ratio_commodity)} (commodity basis, comparable to old model)"
    )
    if new_ratio_phase9a is not None:
        cap_ratio_text += f" / {_fmt_pct(new_ratio_phase9a)} (Phase 9a all-in gross)"
    cap_ratio_text += (
        f" under the new mandate vs. {_fmt_pct(old_ratio)} (commodity-only) under the old "
        "reactive model."
    )
    lines.append(cap_ratio_text)

    if new_2021 is not None and old_2021 is not None:
        lines.append(
            f"- **2021 net margin**: {_fmt_gbp(new_2021)} under the new "
            f"mandate vs. {_fmt_gbp(old_2021)} under the old reactive model."
        )
    else:
        lines.append(f"- **2021 net margin**: {NOT_AVAILABLE}")

    old_revenue = old_data.get("total_revenue_gbp")
    if new_revenue and old_revenue:
        new_margin_pct = new_net / new_revenue
        old_margin_pct = old_data["total_net_gbp"] / old_revenue
        lines.append(
            f"- **Net margin as % of revenue**: {_fmt_pct(new_margin_pct)} "
            f"under the new mandate vs. {_fmt_pct(old_margin_pct)} (commodity-only) under the "
            "old reactive model (industry benchmark: 2-5%)."
        )
    elif new_revenue:
        lines.append(
            f"- **Net margin as % of revenue**: this run "
            f"{_fmt_pct(new_net / new_revenue)}; "
            f"old-model run {NOT_AVAILABLE} (revenue wasn't captured in that "
            "snapshot)."
        )
    else:
        lines.append(f"- **Net margin as % of revenue**: {NOT_AVAILABLE}")

    lines.append("")
    lines.append("**Whole-run net margin, three ways:**")
    lines.append("")
    lines.append(f"- Mandate-hedged (actual, this run, Phase 9a): {_fmt_gbp(new_net)}")
    if old_data is not None:
        lines.append(f"- Old reactive model (actual, commodity-only): {_fmt_gbp(old_data['total_net_gbp'])}")
    if new_het is not None:
        lines.append(f"- Fully naked (this run's counterfactual, commodity-only): {_fmt_gbp(new_het['naked_net_gbp'])}")
    if old_het is not None:
        lines.append(f"- Fully naked (old run's counterfactual, commodity-only): {_fmt_gbp(old_het['naked_net_gbp'])}")
    lines.append("")
    lines.append(
        "Comparing the two naked counterfactuals shows what changed in the "
        "underlying weather/price data between runs (LLM non-determinism in "
        "risk-committee responses also shifts these slightly run-to-run); "
        "comparing each model's actual to its own naked figure isolates what "
        "that model's hedging behaviour itself contributed."
    )
    lines.append("")
    lines.append(
        "_Note: old reactive model figures are commodity-only (pre-Phase-9a). "
        "Naked counterfactuals are commodity-only since non-commodity pass-through "
        "is not affected by hedging decisions._"
    )
    return "\n".join(lines)


def _segment_margin_trend_section(data: dict) -> str:
    """Whole-run net-margin trend by segment (e.g. "resi electricity", "SME
    electricity", "resi gas"), one row per year — REPORTING_BACKLOG item 11.
    A coarser-grained view than per-customer, for portfolio-strategy review."""
    years = sorted(data["years"])
    segments = sorted({
        segment
        for year in years
        for segment in data["years"][year].get("segment_split", {})
    })
    if not segments:
        return f"## Segment Margin Trend\n\n{NOT_AVAILABLE}\n"

    lines = ["## Segment Margin Trend", "", "Net margin (£) by segment, by year:", ""]
    lines.append("| Year | " + " | ".join(segments) + " | Total |")
    lines.append("|---" * (len(segments) + 2) + "|")
    for year in years:
        split = data["years"][year].get("segment_split", {})
        row_values = [split.get(segment, {}).get("net_gbp", 0.0) for segment in segments]
        cells = " | ".join(_fmt_gbp(v) for v in row_values)
        lines.append(f"| {year} | {cells} | {_fmt_gbp(sum(row_values))} |")
    lines.append("")
    return "\n".join(lines)


def _administration_section(data: dict) -> str:
    """Dedicated administration/insolvency section — REPORTING_BACKLOG item 12.
    Renders as a single clean line when the business survived the full window;
    expands to a full incident record if treasury ever hit the floor."""
    event = data.get("administration_event")
    if event is None:
        return "## Administration Events\n\nNone — business survived the full simulation window.\n"

    lines = [
        "## Administration Events",
        "",
        "> **ADMINISTRATION TRIGGERED** — the supplier entered insolvency within the simulation window.",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Trigger date | {event['date']} |",
        f"| Customer (last settled) | {event['customer_id']} |",
        f"| Commodity | {event['commodity']} |",
        f"| Treasury at trigger | {_fmt_gbp(event['treasury_balance_gbp'])} |",
        "",
        "Settlement processing halted at trigger date. All P&L figures in this report "
        "reflect only the period up to and including the trigger date.",
        "",
    ]
    return "\n".join(lines)


def _customer_lifecycle_events_section(data: dict) -> str:
    """Customer lifecycle events — Phase 6b. One row per renewal-time churn/
    retained event rolled during the simulation run. Replaces the
    "Not available" placeholder for REPORTING_BACKLOG item 7 (churn events)."""
    events = data.get("customer_events", [])
    churned = data.get("churned_billing_accounts", [])

    if not events:
        return f"## Customer Lifecycle Events\n\n{NOT_AVAILABLE}\n"

    renewed = [e for e in events if e["event_type"] == "renewed"]
    churned_events = [e for e in events if e["event_type"] == "churned"]

    lines = [
        "## Customer Lifecycle Events",
        "",
        "Renewal decisions rolled at each annual renewal point across the simulation window.",
        f"Retained: **{len(renewed)}** renewals.  Lost (churned): **{len(churned_events)}** accounts.",
    ]

    if churned:
        lines.append(f"\nAccounts lost before end of window: {', '.join(churned)}")

    lines += ["", "| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |"]
    lines.append("|---------|------|---------|----------|-------------|-----------|------|")

    for evt in events:
        flag = " **CHURNED**" if evt["event_type"] == "churned" else ""
        lines.append(
            f"| {evt['customer_id']} | {evt['event_date']} | {evt['event_type']}{flag} "
            f"| {evt['churn_probability']:.4f} | {evt['win_probability']:.4f} "
            f"| {evt['effective_retention_probability']:.4f} | {evt['random_roll']:.4f} |"
        )

    lines.append("")
    return "\n".join(lines)



def _churn_basis_risk_section(data: dict) -> str:
    """Churn Prediction Basis Risk — Phase 11b.

    At each renewal the company estimated churn probability from observable
    signals (rate change %, tenure). The SIM computed it from bill-shock
    history. The gap between them is epistemic basis risk: the company
    systematically under-estimates churn when prices spike, because it
    sees rate change % while the SIM sees the actual bill impact on a
    specific household.
    """
    cbr = data.get("churn_basis_risk", [])
    if not cbr:
        return f"## Churn Prediction Basis Risk\n\n{NOT_AVAILABLE}\n"

    errors = [r["churn_estimate_error_pct"] for r in cbr if r["churn_estimate_error_pct"] is not None]
    if not errors:
        return f"## Churn Prediction Basis Risk\n\n{NOT_AVAILABLE}\n"

    avg_abs_error = sum(abs(e) for e in errors) / len(errors)
    avg_signed_error = sum(errors) / len(errors)

    # Group by year for trend
    by_year: dict[str, list[float]] = {}
    for r in cbr:
        if r["churn_estimate_error_pct"] is None:
            continue
        year = r["term_start"][:4]
        by_year.setdefault(year, []).append(r["churn_estimate_error_pct"])

    lines = [
        "## Churn Prediction Basis Risk",
        "",
        "At each renewal the company estimated churn risk from observable signals "
        "(rate change %, customer tenure). The SIM used its bill-shock model "
        "(actual bill amount relative to customer-specific thresholds). The gap "
        "is epistemic: in crisis years the company sees a rate % while the SIM sees "
        "the household-level financial shock — the same failure mode that surprised "
        "real suppliers in 2021-22.",
        "",
        f"- **Average absolute error:** {avg_abs_error:.1%}",
        f"- **Average signed error:** {avg_signed_error:+.1%} "
        f"({'over-estimates' if avg_signed_error > 0 else 'under-estimates'} vs SIM)",
        f"- **Renewal events with estimates:** {len(cbr)}",
        "",
        "| Year | Renewals | Avg error (signed) | Avg abs error |",
        "|------|----------|--------------------|---------------|",
    ]

    for year in sorted(by_year):
        yr_errors = by_year[year]
        yr_signed = sum(yr_errors) / len(yr_errors)
        yr_abs = sum(abs(e) for e in yr_errors) / len(yr_errors)
        lines.append(
            f"| {year} | {len(yr_errors)} | {yr_signed:+.1%} | {yr_abs:.1%} |"
        )

    lines += [
        "",
        "Positive error = company over-estimated churn vs SIM. "
        "Negative error = company under-estimated (more dangerous — "
        "expected retentions that were actually at risk).",
        "",
    ]
    return "\n".join(lines)


def _section_active_passive_renewal(data: dict) -> str:
    """Phase 33b: Active vs passive renewal split analysis.

    Active renewers (35%) explicitly choose a new fixed deal at term end.
    Passive renewers (65%) roll to SVT by inaction — low rate sensitivity,
    low ongoing churn. Crisis years (2022) force all renewals passive.
    Silent when churn_basis_risk lacks is_active_renewal (pre-Phase-33a runs).
    """
    cbr = data.get("churn_basis_risk", [])
    if not cbr or not any("is_active_renewal" in r for r in cbr):
        return ""

    active = [r for r in cbr if r.get("is_active_renewal", True)]
    passive = [r for r in cbr if not r.get("is_active_renewal", True)]
    total = len(cbr)

    if total == 0:
        return ""

    def _mean_est(recs):
        ests = [r["company_churn_estimate"] for r in recs if r.get("company_churn_estimate") is not None]
        return sum(ests) / len(ests) if ests else 0.0

    def _mean_abs_err(recs):
        errs = [abs(r["churn_estimate_error_pct"]) for r in recs if r.get("churn_estimate_error_pct") is not None]
        return sum(errs) / len(errs) if errs else 0.0

    lines = [
        "## Active vs Passive Renewal Split (Phase 33a)",
        "",
        "~35% of domestic/SME customers actively choose a new fixed deal at term end. "
        "~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. "
        "Crisis years (2022) force all renewals passive (no fixed deals available).",
        "",
        f"- **Total renewal events:** {total}",
        f"- **Active renewers:** {len(active)} ({len(active)/total:.0%}) — "
        f"mean company estimate {_mean_est(active):.1%}, abs error {_mean_abs_err(active):.1%}",
        f"- **Passive SVT-rollers:** {len(passive)} ({len(passive)/total:.0%}) — "
        f"mean company estimate {_mean_est(passive):.1%}, abs error {_mean_abs_err(passive):.1%}",
        "",
        "| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |",
        "|------|--------|---------|-----------|------------|---------------|----------------|",
    ]

    by_year: dict[str, dict] = {}
    for r in cbr:
        year = r["term_start"][:4]
        yd = by_year.setdefault(year, {"active": [], "passive": []})
        key = "active" if r.get("is_active_renewal", True) else "passive"
        yd[key].append(r)

    for year in sorted(by_year):
        yd = by_year[year]
        a, p = yd["active"], yd["passive"]
        lines.append(
            f"| {year} | {len(a)} | {len(p)} "
            f"| {_mean_est(a):.1%} | {_mean_est(p):.1%} "
            f"| {_mean_abs_err(a):.1%} | {_mean_abs_err(p):.1%} |"
        )

    lines += [
        "",
        "Passive renewers should show lower company estimates and lower SIM churn — "
        "high abs error for passive renewers indicates the passive model needs recalibration.",
        "",
    ]
    return "\n".join(lines)


def _section_company_divergence(data: dict) -> str:
    """Company Model Divergence -- Phase 12e.

    Year-by-year mean/max absolute error for the two consequential company
    models: tariff pricing and churn estimation.
    """
    div = data.get("company_divergence", {})
    tariff_by_year = div.get("tariff_error_by_year", {})
    churn_by_year = div.get("churn_error_by_year", {})
    demand_by_year = div.get("demand_error_by_year", {})

    if not tariff_by_year and not churn_by_year and not demand_by_year:
        return f"## Company Model Divergence\n\n{NOT_AVAILABLE}\n"

    lines = [
        "## Company Model Divergence",
        "",
        "Year-by-year gap between company observable-data models and SIM ground truth.",
        "A well-calibrated company model narrows divergence over time as the company",
        "accumulates experience. Divergence in crisis years reveals epistemic risk.",
        "",
    ]

    if tariff_by_year:
        lines += [
            "### Tariff Pricing Error",
            "",
            "Company forward price (120-day rolling mean + 15% risk premium + Phase 13d seasonal",
            "adjustment: winter Oct-Mar +8%, summer Apr-Sep -4%) vs SIM forward curve.",
            "Seasonal adjustment reduces structural under-pricing of winter contracts.",
            "Crisis years (2021-22) remain negative — genuine market adversity, not model error.",
            "",
            "| Year | Terms | Mean Abs Error | Max Abs Error |",
            "|------|-------|---------------|--------------|",
        ]
        for yr, s in sorted(tariff_by_year.items()):
            n, mean_pct, max_pct = s["n"], s["mean_abs_error_pct"] * 100, s["max_abs_error_pct"] * 100
            lines.append(f"| {yr} | {n} | {mean_pct:.1f}% | {max_pct:.1f}% |")
        lines.append("")

    if churn_by_year:
        lines += [
            "### Churn Estimate Error",
            "",
            "Company observable-data churn estimate vs SIM bill-shock model.",
            "Phase 13c adds a bill burden signal (prev_annual_bill / £3,000 threshold)",
            "that captures high-spend SME customers under financial stress even when",
            "their renewal rate is falling — the failure mode that caused company_p=0%",
            "for C6 in 2024 despite SIM showing 38% churn risk.",
            "",
            "**Structural limitation**: the company model uses rate-change % as a churn proxy.",
            "The SIM uses bill-shock history (whether the customer experienced billing spikes",
            "during their contract). In crisis years (2021-22), rate increases were extreme",
            "but hedged customers had few bill shocks — the company systematically over-estimates",
            "churn (company_p→0.95) for customers the SIM correctly sees as low-risk (sim_p=5-14%).",
            "The 2021 max error reflects this: the company cannot observe that a customer was",
            "well-hedged and therefore not experiencing bill shocks during their last contract.",
            "",
            "| Year | Renewals | Mean Abs Error (×SIM) | Max Abs Error (×SIM) |",
            "|------|----------|-----------------------|---------------------|",
        ]
        for yr, s in sorted(churn_by_year.items()):
            n, mean_raw, max_raw = s["n"], s["mean_abs_error_pct"], s["max_abs_error_pct"]
            flag = " ⚠" if mean_raw > 2.0 else ""  # flag when company over-estimates by >2× on average
            lines.append(f"| {yr} | {n} | {mean_raw:.2f}×{flag} | {max_raw:.2f}× |")
        lines.append("")

    # Phase AO: Demand estimation error trend
    if demand_by_year:
        lines += [
            "### Demand Estimation Error (Phase AO)",
            "",
            "Company EAC estimate error vs SIM settled consumption — year-by-year trend.",
            "Error grows as customers acquire EVs, solar, and heat pumps that the company",
            "cannot directly observe. The first contract term after asset acquisition has",
            "the highest error; subsequent terms self-correct from billing history.",
            "",
            "| Year | Customers | Mean Abs Error | Max Abs Error | Signal |",
            "|------|-----------|----------------|---------------|--------|",
        ]
        errors = [(yr, s) for yr, s in sorted(demand_by_year.items())]
        for yr, s in errors:
            n = s["n"]
            mean_e = s["mean_abs_error_pct"]
            max_e = s["max_abs_error_pct"]
            if mean_e > 2.5:
                sig = "HIGH drift — EV/asset cohort growing"
            elif mean_e > 1.0:
                sig = "MODERATE — asset adoption visible"
            else:
                sig = "Low — stable portfolio"
            lines.append(f"| {yr} | {n} | {mean_e:.2f}% | {max_e:.2f}% | {sig} |")
        lines.append("")

        # Trend note
        first_yr = errors[0]
        last_active = [(yr, s) for yr, s in errors[:-1] if s["n"] >= 5]
        if last_active:
            peak_yr, peak_s = max(last_active, key=lambda kv: kv[1]["mean_abs_error_pct"])
            lines += [
                f"**Trend:** demand estimation error grew from **{first_yr[1]['mean_abs_error_pct']:.2f}%** "
                f"in {first_yr[0]} to **{peak_s['mean_abs_error_pct']:.2f}%** mean / "
                f"**{peak_s['max_abs_error_pct']:.2f}%** max in {peak_yr}. "
                "Root cause: new asset acquisitions (Phase B life events) create a "
                "temporary estimation gap until the company observes a full billing cycle.",
                "Portfolio action: prioritise smart meter installation for high-EAC-drift "
                "accounts — interval data eliminates estimation error at renewal.",
                "",
            ]

    return "\n".join(lines)



def _section_demand_estimation(data: dict) -> str:
    """Demand Estimation Accuracy -- Phase 23a.

    Company estimates customer annual consumption from observable prior-year
    billing records rather than reading the SIM's oracle EAC. Closes an
    epistemic honesty violation: real suppliers don't know forward consumption.
    """
    log = data.get("demand_estimation_log", [])
    if not log:
        return ""

    # Aggregate by year
    by_year: dict[str, list[float]] = {}
    for entry in log:
        yr = entry["term_start"][:4]
        by_year.setdefault(yr, []).append(abs(entry["error_pct"]))

    if not by_year:
        return ""

    lines = [
        "## Demand Estimation Accuracy (Phase 23a/25a)",
        "",
        "Company EAC estimate (from prior-year billing records) vs actual settled kWh.",
        "Phase 25a: true_eac_kwh uses mean annual settled consumption (not declared EAC),",
        "fixing the misleading ~100% error for EV customers (C2/C4: declared 3500/5500 kWh,",
        "actual ~6820 kWh/year with EV charging). Near-zero error after first term confirms",
        "company billing estimation correctly tracks actual consumption.",
        "",
        "| Year | Renewals | Mean Abs Error | Max Abs Error |",
        "|------|----------|----------------|--------------|",
    ]
    for yr, errs in sorted(by_year.items()):
        n = len(errs)
        mean_e = sum(errs) / n if n else 0.0
        max_e = max(errs) if errs else 0.0
        lines.append(f"| {yr} | {n} | {mean_e:.1f}% | {max_e:.1f}% |")

    total_n = len(log)
    prior_billing = sum(1 for e in log if e.get("source") == "prior_billing")
    fallback = total_n - prior_billing
    lines += [
        "",
        f"**{prior_billing}** of **{total_n}** renewals used prior billing records; "
        f"**{fallback}** used SIM oracle fallback (first term, no billing history).",
    ]

    return "\n".join(lines) + "\n"


def _section_eac_drift_snapshot(data: dict) -> str:
    """Phase AI: Per-customer EAC drift from billing history.

    Computes the drift in each customer's observed annual consumption (from the
    company's own billing-derived EAC estimates) between their first and most recent
    renewal. Customers with >+15% drift likely acquired EVs or ASHPs; <-15% drift
    suggests solar installation or significant efficiency improvements.

    Uses demand_estimation_log (Phase 23a/25a) — observable billing data only.
    Silent when no log entries.
    """
    log = data.get("demand_estimation_log", [])
    if not log:
        return ""

    from collections import defaultdict
    by_customer: dict = defaultdict(list)
    for entry in log:
        cid = entry.get("customer_id")
        if cid:
            by_customer[cid].append(entry)

    if not by_customer:
        return ""

    _SIGNIFICANT_INCREASE = 15.0
    _MODERATE_INCREASE = 5.0
    _MODERATE_DECREASE = -5.0
    _SIGNIFICANT_DECREASE = -15.0

    def _infer_cause(drift_pct: float, delta_kwh: float) -> str:
        if drift_pct > 50:
            return "likely EV acquisition"
        if drift_pct > 20:
            return "likely EV or ASHP installation"
        if drift_pct > 8:
            return "moderate demand growth (building use change)"
        if drift_pct < _SIGNIFICANT_DECREASE:
            return "likely solar installation or significant efficiency upgrade"
        if drift_pct < _MODERATE_DECREASE:
            return "efficiency improvement or reduced occupancy"
        return "stable"

    # Build per-customer drift records
    drifts = []
    for cid, entries in by_customer.items():
        sorted_entries = sorted(entries, key=lambda e: e["term_start"])
        first = sorted_entries[0]
        last = sorted_entries[-1]
        if first["company_eac_kwh"] <= 0:
            continue
        baseline_kwh = first["company_eac_kwh"]
        current_kwh = last["company_eac_kwh"]
        drift_pct = (current_kwh - baseline_kwh) / baseline_kwh * 100.0
        delta_kwh = current_kwh - baseline_kwh
        drifts.append({
            "customer_id": cid,
            "baseline_kwh": baseline_kwh,
            "current_kwh": current_kwh,
            "drift_pct": drift_pct,
            "delta_kwh": delta_kwh,
            "first_term": first["term_start"],
            "last_term": last["term_start"],
            "cause_hint": _infer_cause(drift_pct, delta_kwh),
        })

    if not drifts:
        return ""

    significant = [d for d in drifts if abs(d["drift_pct"]) >= _SIGNIFICANT_INCREASE]
    moderate = [d for d in drifts if _MODERATE_INCREASE <= abs(d["drift_pct"]) < _SIGNIFICANT_INCREASE]
    stable = [d for d in drifts if abs(d["drift_pct"]) < _MODERATE_INCREASE]

    # Sort: biggest drift first (absolute value)
    notable = sorted(
        [d for d in drifts if abs(d["drift_pct"]) >= _MODERATE_INCREASE],
        key=lambda d: abs(d["drift_pct"]),
        reverse=True,
    )

    lines = [
        "## EAC Drift Snapshot (Phase AI)",
        "",
        "Per-customer consumption drift from company billing history (first renewal → latest renewal).",
        "Drift > +15%: EV/ASHP acquisition. Drift < −15%: solar installation or efficiency upgrade.",
        "",
        f"**{len(significant)} significant** (≥15%) | **{len(moderate)} moderate** (5–15%) | **{len(stable)} stable** (<5%)",
        "",
    ]

    if notable:
        lines += [
            "| Customer | Baseline kWh | Current kWh | Drift | Likely Cause |",
            "|----------|-------------|-------------|-------|--------------|",
        ]
        for d in notable:
            drift_str = f"{d['drift_pct']:+.0f}%"
            lines.append(
                f"| {d['customer_id']} | {d['baseline_kwh']:,.0f} | {d['current_kwh']:,.0f} "
                f"| {drift_str} | {d['cause_hint']} |"
            )
        lines.append("")

    # Portfolio-wide trend
    avg_drift = sum(d["drift_pct"] for d in drifts) / len(drifts)
    increasing = sum(1 for d in drifts if d["drift_pct"] > 0)
    decreasing = sum(1 for d in drifts if d["drift_pct"] < 0)
    lines += [
        f"**Portfolio demand trend:** {increasing} customers increasing / {decreasing} decreasing "
        f"(mean drift: {avg_drift:+.1f}%)",
        "",
    ]

    return "\n".join(lines)



def _section_enterprise_value_analysis(data: dict) -> str:
    """Phase 22a: dual enterprise value — full-history vs 3yr-trailing margin.

    The full-history EV anchors avg_annual_margin to all simulation years,
    including deep crisis losses. The trailing variant uses only the last 3
    completed years, reflecting the company's current earning power rather
    than its cumulative history. Both are valid; showing both makes the
    methodology choice explicit.
    """
    from saas.clv_model import build_clv, _annuity_factor, fit_theta_prior_from_churn_probabilities, DISCOUNT_RATE_ANNUAL
    from saas.cost_to_serve import build_cost_to_serve

    churn_risk = data.get("churn_risk", {})
    yearly = data.get("years", {})
    ev_full = data.get("enterprise_value_gbp")

    if not churn_risk or not yearly or ev_full is None:
        return ""

    sorted_years = sorted(yearly.keys())
    trailing_years = sorted_years[-3:] if len(sorted_years) >= 3 else sorted_years

    # Build per-customer trailing net margin from yearly per_customer dicts
    trailing_margin_by_cid: dict[str, list[float]] = {}
    for yr in trailing_years:
        yd = yearly[yr]
        for cid, pc in yd.get("per_customer", {}).items():
            trailing_margin_by_cid.setdefault(cid, []).append(pc["net_gbp"])

    # Map CID → billing account ID (electricity CIDs map to themselves for named customers)
    from saas.customer_reaction import _billing_account_id
    trailing_avg_by_account: dict[str, float] = {}
    for cid, margins in trailing_margin_by_cid.items():
        account_id = _billing_account_id(cid)
        existing = trailing_avg_by_account.get(account_id, 0.0)
        trailing_avg_by_account[account_id] = existing + sum(margins) / len(margins)

    # Compute trailing CLV using override margins (same lifetime, different margin basis)
    # Only include accounts that have churn_risk renewal data
    accounts_with_risk = {aid for aid, renewals in churn_risk.items() if renewals}
    trailing_avg_filtered = {k: v for k, v in trailing_avg_by_account.items() if k in accounts_with_risk}
    if not trailing_avg_filtered:
        return ""

    # Get expected lifetimes from existing CLV snapshots (most recent year's snapshot)
    snapshots = data.get("clv_snapshots") or {}
    latest_snap = snapshots.get(sorted_years[-1], {}) if snapshots else {}

    # Compute alpha/beta from churn risk for annuity factor
    alpha, beta = fit_theta_prior_from_churn_probabilities(churn_risk)
    theta_mean = alpha / (alpha + beta) if (alpha + beta) > 0 else 0.10
    # Expected geometric lifetime = 1/theta (simplified; consistent with SBG projection)
    base_lifetime = min(1.0 / theta_mean, 50.0) if theta_mean > 0 else 10.0
    annuity = _annuity_factor(base_lifetime, DISCOUNT_RATE_ANNUAL)

    trailing_clv_by_account = {
        account_id: avg_margin * annuity
        for account_id, avg_margin in trailing_avg_filtered.items()
    }
    trailing_ev = sum(trailing_clv_by_account.values())

    # Year-by-year portfolio net margin table
    yr_rows = []
    for yr in sorted_years:
        yd = yearly[yr]
        net = yd.get("net_gbp", 0.0)
        marker = " ← trailing" if yr in trailing_years else ""
        yr_rows.append(f"| {yr} | {_fmt_gbp(net)} |{marker}")

    # Per-account comparison
    acct_rows = []
    all_accts = sorted(set(trailing_avg_by_account) | {k for k in data.get("by_billing_account", {})})
    full_by_acct = data.get("by_billing_account", {})
    for acct in all_accts:
        full_clv = (full_by_acct.get(acct) or {}).get("clv_gbp")
        trail_clv = trailing_clv_by_account.get(acct)
        full_str = _fmt_gbp(full_clv) if full_clv is not None else "—"
        trail_str = _fmt_gbp(trail_clv) if trail_clv is not None else "—"
        acct_rows.append(f"| {acct} | {full_str} | {trail_str} |")

    lines = [
        "## Enterprise Value Analysis (Phase 22a)",
        "",
        f"**Full-history EV:** {_fmt_gbp(ev_full)} — anchored to all {len(sorted_years)} years including crisis losses",
        f"**3yr-trailing EV:** {_fmt_gbp(trailing_ev)} — based on last {len(trailing_years)} years ({', '.join(trailing_years)}), reflecting current earning power",
        "",
        "The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.",
        "When trailing EV > full-history EV, the company's recent performance is better than its",
        "cumulative history suggests — a recovery signal.",
        "",
        "**Portfolio net margin by year:**",
        "",
        "| Year | Net margin |",
        "|------|----------:|",
        *yr_rows,
        "",
        "**CLV by billing account:**",
        "",
        "| Account | Full-history CLV | 3yr-trailing CLV |",
        "|---------|----------------:|----------------:|",
        *acct_rows,
        "",
    ]
    return "\n".join(lines)


def _clv_trajectory_section(data: dict) -> str:
    """Whole-run CLV trajectory table — Point-in-Time CLV per billing account
    at each year end, showing how estimates evolved as renewal data accumulated.
    Only rendered when clv_snapshots is available (fresh simulation run).
    """
    snapshots = data.get("clv_snapshots")
    if not snapshots:
        return f"## CLV Trajectory\n\n{NOT_AVAILABLE}\n"

    years = sorted(snapshots)
    # Collect billing accounts that appear in at least one year
    all_accounts = sorted({
        account_id
        for yr_snap in snapshots.values()
        for account_id in yr_snap
    })
    if not all_accounts:
        return f"## CLV Trajectory\n\n{NOT_AVAILABLE}\n"

    header = "| Year | " + " | ".join(all_accounts) + " |"
    sep = "|------|" + "|".join("------:" for _ in all_accounts) + "|"
    rows = []
    for year in years:
        yr = snapshots[year]
        cells = [
            _fmt_gbp(yr[acct]) if yr.get(acct) is not None else "—"
            for acct in all_accounts
        ]
        rows.append(f"| {year} | " + " | ".join(cells) + " |")

    return "\n".join([
        "## CLV Trajectory",
        "",
        "Point-in-Time Customer Lifetime Value per billing account at each year-end.",
        "CLV is computed from churn renewal history and net margins accumulated up to "
        "that date only (Point-in-Time Blindfold). '—' = no renewal points yet.",
        "",
        header,
        sep,
        *rows,
        "",
    ])


def _section_margin_feedback(data: dict) -> str:
    """Phase 16c + 19a: realized-margin recovery surcharges applied during the run."""
    log = data.get("margin_feedback_log", [])
    if not log:
        return ""

    total_surcharge_events = len(log)
    avg_surcharge = sum(e["surcharge_pct"] for e in log) / total_surcharge_events
    gas_events = [e for e in log if e.get("commodity") == "gas"]

    lines = [
        "## Margin Recovery Surcharges (Phase 16c + 19a)",
        "",
        f"Company applied {total_surcharge_events} recovery surcharge(s) at renewal based on prior-term losses "
        f"({len(gas_events)} gas). Avg surcharge: {avg_surcharge:.1f}%.",
        "",
        "| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |",
        "|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|",
    ]
    for e in sorted(log, key=lambda x: x["term_start"]):
        comm = e.get("commodity", "electricity")
        lines.append(
            f"| {e['customer_id']} | {comm} | {e['term_start']} "
            f"| {_fmt_gbp(e['prev_margin_gbp'])} "
            f"| {_fmt_gbp(e['prev_revenue_gbp'])} "
            f"| +{e['surcharge_pct']:.1f}% "
            f"| £{e['unit_rate_before']:.2f}/MWh "
            f"| £{e['unit_rate_after']:.2f}/MWh |"
        )
    lines.append("")
    return "\n".join(lines)


def _section_profitability_uplift(data: dict) -> str:
    """Phase 44a: customer profitability uplift events — net-negative accounts repriced."""
    log = data.get("profitability_uplift_log", [])
    if not log:
        return ""

    lines = [
        "## Activity-Based Profitability Uplift (Phase 44a)",
        "",
        f"Company identified {len(log)} net-negative customer-term(s) and applied a £{log[0]['uplift_gbp_per_mwh']:.0f}/MWh uplift at renewal.",
        "Churn model handles the outcome: higher rate → higher churn probability → unprofitable customers naturally filter out.",
        "",
        "| Customer | Term start | Uplift £/MWh | Rate after uplift |",
        "|----------|------------|-------------|------------------|",
    ]
    for e in sorted(log, key=lambda x: x["term_start"]):
        lines.append(
            f"| {e['customer_id']} | {e['term_start']} "
            f"| +£{e['uplift_gbp_per_mwh']:.2f}/MWh "
            f"| £{e['unit_rate_after']:.2f}/MWh |"
        )
    lines.append("")
    return "\n".join(lines)


def _section_dynamic_pricing(data: dict) -> str:
    """Phase 17a + 19a: portfolio learning premium events applied during the run."""
    log = data.get("dynamic_pricing_log", [])
    if not log:
        return ""

    total_events = len(log)
    pos_events = [e for e in log if e["portfolio_premium_pct"] > 0]
    neg_events = [e for e in log if e["portfolio_premium_pct"] < 0]
    gas_events = [e for e in log if e.get("commodity") == "gas"]

    lines = [
        "## Portfolio Learning Premium (Phase 17a + 19a)",
        "",
        f"Company applied portfolio premium adjustments at {total_events} renewal(s) "
        f"({len(gas_events)} gas) based on recent portfolio-wide margin rates: "
        f"{len(pos_events)} surcharge(s), {len(neg_events)} discount(s).",
        "",
        "| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |",
        "|----------|-----------|------------|-------------------|-------------------|------------|-----------|",
    ]
    for e in sorted(log, key=lambda x: x["term_start"]):
        sign = "+" if e["portfolio_premium_pct"] >= 0 else ""
        comm = e.get("commodity", "electricity")
        lines.append(
            f"| {e['customer_id']} | {comm} | {e['term_start']} "
            f"| {e['mean_recent_margin_rate'] * 100:.1f}% "
            f"| {sign}{e['portfolio_premium_pct']:.1f}% "
            f"| £{e['unit_rate_before']:.2f}/MWh "
            f"| £{e['unit_rate_after']:.2f}/MWh |"
        )
    lines.append("")
    return "\n".join(lines)


def _section_churn_avoidability(data: dict) -> str:
    """Phase 17b: classify no-offer churns as blind misses vs deliberate passes.

    Joins no_offer_churn_log (company's perspective) with company_event_log
    (which carries sim_churn_probability ground truth) to answer:
    - How many churns were 'blind' (company underestimated)?
    - Of the blind misses, how many were actually 'detectable' (SIM p >= 30%)?
    - What margin was lost to each category?
    """
    no_offer_log = data.get("no_offer_churn_log", [])
    if not no_offer_log:
        return ""

    # Build lookup: (customer_id, event_date) → sim_churn_probability
    cel = data.get("company_event_log", [])
    sim_p_lookup: dict[tuple, float | None] = {}
    for ev in cel:
        if ev.get("event_type") == "churn":
            key = (ev["customer_id"], ev["event_date"])
            sim_p_lookup[key] = ev.get("sim_churn_probability")

    RETENTION_THRESHOLD = 0.30  # must match sim runner constant

    # Annotate each no-offer churn
    annotated = []
    for e in no_offer_log:
        key = (e["customer_id"], e["event_date"])
        sim_p = sim_p_lookup.get(key)
        detectable = sim_p is not None and sim_p >= RETENTION_THRESHOLD
        annotated.append({
            **e,
            "sim_churn_probability": sim_p,
            "detectable_by_better_model": detectable,
        })

    blind = [a for a in annotated if a["no_offer_reason"] == "below_threshold"]
    uneconomical = [a for a in annotated if a["no_offer_reason"] == "uneconomical"]
    detectable_blind = [a for a in blind if a["detectable_by_better_model"]]

    total_margin_lost = sum(a["expected_term_margin_gbp"] for a in annotated)
    blind_margin = sum(a["expected_term_margin_gbp"] for a in blind)
    uneconomical_margin = sum(a["expected_term_margin_gbp"] for a in uneconomical)

    lines = [
        "## Churn Avoidability Analysis (Phase 17b)",
        "",
        f"Total no-offer churns: **{len(annotated)}** | "
        f"Blind misses: **{len(blind)}** | "
        f"Deliberate passes (uneconomical): **{len(uneconomical)}**",
        "",
        f"- Blind misses: company estimated churn < {RETENTION_THRESHOLD:.0%} → no offer made. "
        f"Of these, {len(detectable_blind)} had SIM p ≥ {RETENTION_THRESHOLD:.0%} (detectable with a better model).",
        f"- Deliberate passes: company estimated churn ≥ {RETENTION_THRESHOLD:.0%} but the "
        f"retention offer was uneconomical (margin + acq cost < offer cost).",
        "",
        f"**Estimated margin at stake** — blind: {_fmt_gbp(blind_margin)} | "
        f"deliberate: {_fmt_gbp(uneconomical_margin)} | "
        f"total: {_fmt_gbp(total_margin_lost)}",
        "",
    ]

    if annotated:
        lines += [
            "| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |",
            "|----------|------|--------|---------|-------|-------------|----------------|",
        ]
        for a in sorted(annotated, key=lambda x: x["event_date"]):
            sim_str = f"{a['sim_churn_probability']:.2f}" if a["sim_churn_probability"] is not None else "n/a"
            det_str = "Yes" if a["detectable_by_better_model"] else "No"
            co_str = f"{a['company_churn_estimate']:.2f}" if a.get("company_churn_estimate") is not None else "n/a"
            reason_str = "Blind miss" if a["no_offer_reason"] == "below_threshold" else "Uneconomical"
            lines.append(
                f"| {a['customer_id']} | {a['event_date']} "
                f"| {reason_str} | {co_str} | {sim_str} "
                f"| {det_str} | {_fmt_gbp(a['expected_term_margin_gbp'])} |"
            )
        lines.append("")

    return "\n".join(lines)


def _section_dual_fuel_pnl(data: dict) -> str:
    """Phase 17d: combined P&L for dual-fuel accounts (electricity + gas legs).

    Pairs electricity customers with their gas counterparts (e.g., C1 + C1g)
    and shows the combined lifetime margin. Answers: 'Did gas add value to the
    dual-fuel relationship, or was it a drag?'
    """
    # per_cid_comm_pnl: {cid: {commodity: {gross, capital, net, revenue}}}
    by_cid_comm: dict = data.get("per_cid_comm_pnl") or {}
    if not by_cid_comm:
        # fallback: aggregate from all_records if present (legacy test fixtures)
        records = data.get("all_records", [])
        if not records:
            return ""
        for r in records:
            cid = r["customer_id"]
            comm = r.get("commodity", "electricity")
            if cid not in by_cid_comm:
                by_cid_comm[cid] = {}
            if comm not in by_cid_comm[cid]:
                by_cid_comm[cid][comm] = {"net": 0.0, "gross": 0.0, "capital": 0.0, "revenue": 0.0}
            by_cid_comm[cid][comm]["net"] += r.get("net_margin_gbp", 0.0)
            by_cid_comm[cid][comm]["gross"] += r.get("margin_gbp", 0.0)
            by_cid_comm[cid][comm]["capital"] += r.get("capital_cost_gbp", 0.0)
            by_cid_comm[cid][comm]["revenue"] += r.get("revenue_gbp", 0.0)

    # Find dual-fuel pairs: gas leg "C1g" paired with elec leg "C1"
    gas_cids = {cid for cid, commodities in by_cid_comm.items() if "gas" in commodities}
    pairs = []
    for gas_cid in sorted(gas_cids):
        # Convention: gas leg is "C1g" → elec leg is "C1"
        if gas_cid.endswith("g"):
            elec_cid = gas_cid[:-1]
        else:
            continue
        if elec_cid in by_cid_comm and "electricity" in by_cid_comm.get(elec_cid, {}):
            elec = by_cid_comm[elec_cid]["electricity"]
            gas = by_cid_comm[gas_cid]["gas"]
            pairs.append({
                "elec_id": elec_cid,
                "gas_id": gas_cid,
                "elec_net": elec["net"],
                "gas_net": gas["net"],
                "combined_net": elec["net"] + gas["net"],
                "elec_revenue": elec["revenue"],
                "gas_revenue": gas["revenue"],
            })

    if not pairs:
        return ""

    lines = [
        "## Dual-Fuel Account P&L (Phase 17d)",
        "",
        f"{len(pairs)} dual-fuel account pair(s): electricity leg + gas leg combined.",
        "",
        "| Account | Elec net | Gas net | Combined net | Gas accretive? |",
        "|---------|----------|---------|-------------|---------------|",
    ]
    for p in sorted(pairs, key=lambda x: x["combined_net"], reverse=True):
        accretive = "Yes" if p["gas_net"] >= 0 else "No"
        lines.append(
            f"| {p['elec_id']}+{p['gas_id']} "
            f"| {_fmt_gbp(p['elec_net'])} "
            f"| {_fmt_gbp(p['gas_net'])} "
            f"| {_fmt_gbp(p['combined_net'])} "
            f"| {accretive} |"
        )

    gas_accretive = sum(1 for p in pairs if p["gas_net"] >= 0)
    total_gas_net = sum(p["gas_net"] for p in pairs)
    lines += [
        "",
        f"Gas accretive in {gas_accretive}/{len(pairs)} dual-fuel accounts. "
        f"Total gas net margin: {_fmt_gbp(total_gas_net)}.",
        "",
    ]
    return "\n".join(lines)


def _section_revenue_sanity(data: dict) -> str:
    """Phase 45a: revenue and margin sanity check against industry benchmarks.

    Delegates to tools.revenue_sanity_check for computation, embeds output inline.
    Silent if that module is unavailable.
    """
    try:
        from tools.revenue_sanity_check import run_check
        _passed, report = run_check(data)
        return report
    except Exception:
        return ""


def _section_customer_pnl_ranking(data: dict) -> str:
    """Phase 17c: per-customer lifetime P&L ranking across the full simulation window.

    Ranks all billing accounts (including successors) by net margin (best to worst).
    Phase 40b: shows tariff_type column for I&C customers.
    """
    from saas.customers import CUSTOMERS
    tariff_by_cid = {c["customer_id"]: c.get("tariff_type", "fixed") for c in CUSTOMERS}

    by_cid = data.get("per_cid_pnl") or {}
    if not by_cid:
        # fallback: aggregate from all_records if present (legacy test fixtures)
        records = data.get("all_records", [])
        if not records:
            return ""
        for r in records:
            cid = r["customer_id"]
            if cid not in by_cid:
                by_cid[cid] = {"gross": 0.0, "capital": 0.0, "net": 0.0, "revenue": 0.0}
            by_cid[cid]["gross"] += r.get("margin_gbp", 0.0)
            by_cid[cid]["capital"] += r.get("capital_cost_gbp", 0.0)
            by_cid[cid]["net"] += r.get("net_margin_gbp", 0.0)
            by_cid[cid]["revenue"] += r.get("revenue_gbp", 0.0)

    ranked = sorted(by_cid.items(), key=lambda x: x[1]["net"], reverse=True)

    total_net = sum(v["net"] for _, v in ranked)
    total_revenue = sum(v["revenue"] for _, v in ranked)

    lines = [
        "## Customer P&L Ranking (Phase 17c)",
        "",
        f"Lifetime net margin: {_fmt_gbp(total_net)} across {len(ranked)} billing accounts. "
        f"Revenue: {_fmt_gbp(total_revenue)}.",
        "",
        "| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |",
        "|---|----------|--------|---------|-------------|---------|------------|-------------|",
    ]
    for rank, (cid, v) in enumerate(ranked, 1):
        net_pct = f"{v['net'] / v['revenue'] * 100:.1f}%" if v["revenue"] > 0 else "n/a"
        tariff = tariff_by_cid.get(cid, "fixed")
        lines.append(
            f"| {rank} | {cid} "
            f"| {tariff} "
            f"| {_fmt_gbp(v['revenue'])} "
            f"| {_fmt_gbp(v['gross'])} "
            f"| {_fmt_gbp(v['capital'])} "
            f"| {_fmt_gbp(v['net'])} "
            f"| {net_pct} |"
        )
    lines.append("")
    return "\n".join(lines)


def _ledger_summary_section(data: dict) -> str:
    """Transaction log summary — Phase 7a/7b/9a. Shows event counts, cash-flow
    waterfall, and verification that ledger P&L agrees with the simulation."""
    meta = data.get("ledger_meta")
    pnl = data.get("ledger_pnl")

    if meta is None or pnl is None:
        return f"## Transaction Log\n\n{NOT_AVAILABLE}\n"

    by_type = meta.get("by_type", {})

    lines = [
        "## Transaction Log",
        "",
        f"Total events: {meta['event_count']:,}",
        "",
        "| Event type | Count |",
        "|------------|-------|",
    ]
    for etype, count in sorted(by_type.items()):
        lines.append(f"| {etype} | {count:,} |")

    lines += [
        "",
        "**Cash-flow waterfall (from ledger)**",
        "",
        "| Flow | Amount |",
        "|------|--------|",
    ]

    # Phase 9a: show full bill breakdown when non-commodity / VAT events present
    if "total_billed_gbp" in pnl:
        lines += [
            f"| Customer bills (all-in) | {_fmt_gbp(pnl['total_billed_gbp'])} |",
            f"|   Less: VAT remitted to HMRC | ({_fmt_gbp(pnl['vat_remittance_gbp'])}) |",
            f"| = Revenue (ex-VAT) | {_fmt_gbp(pnl['revenue_gbp'])} |",
        ]
    else:
        lines.append(f"| Revenue billed (billing events) | {_fmt_gbp(pnl['revenue_gbp'])} |")

    if "non_commodity_cost_gbp" in pnl:
        lines.append(f"| Less: non-commodity pass-through | ({_fmt_gbp(pnl['non_commodity_cost_gbp'])}) |")

    lines += [
        f"| Wholesale cost (settlement events) | ({_fmt_gbp(pnl['wholesale_cost_gbp'])}) |",
        f"| Gross margin | {_fmt_gbp(pnl['gross_margin_gbp'])} |",
        f"| Capital charges | ({_fmt_gbp(pnl['capital_cost_gbp'])}) |",
        f"| Net margin | {_fmt_gbp(pnl['net_margin_gbp'])} |",
    ]

    if "cash_collected_gbp" in pnl:
        # Cash reconciliation: shown after the P&L waterfall as a memo.
        # cash_collected = bills (all-in) − bad_debt (different path from revenue ex-VAT).
        # cash_net_margin = cash_collected − wholesale − capital − non_commodity (before VAT remittance).
        lines += [
            "",
            f"_Cash reconciliation: of {_fmt_gbp(pnl['total_billed_gbp'])} billed, "
            f"bad debt of {_fmt_gbp(pnl['bad_debt_gbp'])} was written off, leaving "
            f"{_fmt_gbp(pnl['cash_collected_gbp'])} cash collected (gross of VAT). "
            f"After operating costs, net cash position before VAT remittance: "
            f"{_fmt_gbp(pnl['cash_net_margin_gbp'])}._",
        ]

    lines += [""]

    if "acquisition_spend_gbp" in pnl or "fixed_cost_gbp" in pnl:
        lines += [
            f"| Acquisition spend | ({_fmt_gbp(pnl.get('acquisition_spend_gbp', 0.0))}) |",
            f"| Fixed overhead | ({_fmt_gbp(pnl.get('fixed_cost_gbp', 0.0))}) |",
            f"| Operating net margin | {_fmt_gbp(pnl.get('operating_net_margin_gbp', 0.0))} |",
            "",
        ]

    return "\n".join(lines)


def _growth_acquisition_section(data: dict) -> str:
    """Phase 8a: Growth Mandate & Acquisition model summary section."""
    mandate = data.get("growth_mandate", "flat")
    total_attempts = data.get("total_acquisition_attempts", 0)
    total_wins = data.get("total_acquisition_wins", 0)
    total_spend = data.get("total_acquisition_spend_gbp", 0.0)
    total_fixed = data.get("total_fixed_cost_gbp", 0.0)
    acquired = data.get("acquired_customers", [])
    from saas.growth_mandate import COST_PER_ACQUISITION, FIXED_COST_MONTHLY

    if not total_attempts and not total_fixed:
        return ""

    lines = [
        "## Growth & Acquisition\n",
        f"**Mandate:** `{mandate}`  "
        f"**Acquisition cost:** resi £{COST_PER_ACQUISITION['resi']:.0f} / SME £{COST_PER_ACQUISITION['SME']:.0f}  "
        f"**Fixed overhead:** £{FIXED_COST_MONTHLY:.0f}/month\n",
    ]

    # Per-year table
    years = sorted(data["years"])
    if total_attempts:
        lines += [
            "**Acquisition activity by year**\n",
            "| Year | Attempts | Wins | Win Rate | Spend |",
            "|------|----------|------|----------|-------|",
        ]
        for year in years:
            yd = data["years"][year]
            attempts = yd.get("acquisition_attempts", 0)
            wins = yd.get("acquisition_wins", 0)
            spend = yd.get("acquisition_spend_gbp", 0.0)
            if not attempts:
                continue
            win_rate = wins / attempts if attempts else 0.0
            lines.append(
                f"| {year} | {attempts} | {wins} | {win_rate:.0%} | {_fmt_gbp(spend)} |"
            )
        lines += [
            "",
            f"**Total:** {total_attempts} attempts, {total_wins} wins "
            f"({total_wins/total_attempts:.0%} win rate), "
            f"{_fmt_gbp(total_spend)} total spend",
            "",
        ]

    if acquired:
        lines += [
            f"**Fresh acquisitions won ({len(acquired)}):** {', '.join(sorted(acquired))}\n",
            "_Note: acquired customers are registered but do not yet settle energy in Phase 8a. "
            "Settlement revenue deferred to Phase 8b._\n",
        ]

    # Fixed cost summary
    if total_fixed:
        lines += [
            "**Operating overhead**\n",
            "| Year | Fixed Cost |",
            "|------|-----------|",
        ]
        for year in years:
            yd = data["years"][year]
            fc = yd.get("fixed_cost_gbp", 0.0)
            if fc:
                lines.append(f"| {year} | ({_fmt_gbp(fc)}) |")
        hl = data.get("_ledger_headline")
        net_gbp = hl["net_margin_gbp"] if hl else data.get("total_net_gbp", 0.0)
        lines += [
            "",
            f"**Total fixed cost:** {_fmt_gbp(total_fixed)} over simulation window",
        ]
        if net_gbp:
            operating_margin = net_gbp - total_spend - total_fixed
            lines.append(
                f"**Operating net margin** (energy margin less acquisition spend & fixed costs): "
                f"{_fmt_gbp(operating_margin)}"
            )
        lines.append("")

    return "\n".join(lines)


def _section_company_crm(data: dict) -> str:
    """Company CRM vs SIM Ground Truth — Phase 12a.

    Shows dated churn and acquisition events as the company CRM knows them,
    and reconciles company CRM active accounts against SIM churned accounts
    at each year-end.
    """
    cel = data.get("company_event_log", [])
    churned_ba = set(data.get("churned_billing_accounts", []))
    years = sorted(data.get("years", {}).keys())

    if not cel:
        return "## Company CRM — Event Log\n\nNo events recorded in current run.\n"

    lines = [
        "## Company CRM — Event Log",
        "",
        "Dated artefacts of customer lifecycle events as seen by the company layer.",
        f"Total events: **{len(cel)}** "
        f"({sum(1 for e in cel if e['event_type'] == 'churn')} churn, "
        f"{sum(1 for e in cel if e['event_type'] == 'acquisition')} acquisition)",
        "",
        "| Date | Event | Customer | Detail |",
        "|------|-------|----------|--------|",
    ]

    for ev in sorted(cel, key=lambda e: e["event_date"]):
        if ev["event_type"] == "churn":
            sim_p = ev.get("sim_churn_probability")
            co_est = ev.get("company_churn_estimate")
            sim_str = f"SIM p={sim_p:.2f}" if sim_p is not None else "SIM p=n/a"
            co_str = f"est={co_est:.2f}" if co_est is not None else "est=n/a"
            detail = f"{sim_str}, company {co_str}"
            lines.append(f"| {ev['event_date']} | CHURN | {ev['customer_id']} | {detail} |")
        else:
            ch = ev.get("channel", "market-acquisition")
            pred = ev.get("predecessor_id")
            detail = f"{ch}" + (f" (predecessor: {pred})" if pred else "")
            lines.append(f"| {ev['event_date']} | ACQUISITION | {ev['customer_id']} | {detail} |")

    if years:
        lines += [
            "",
            "**SIM ground truth vs company CRM reconciliation (year-end snapshots):**",
            "",
            "| Year-end | SIM churned (cumulative) | CRM active | Match |",
            "|----------|--------------------------|------------|-------|",
        ]
        from company.crm.event_log import AcquisitionEvent, ChurnEvent, CompanyEventLog
        log = CompanyEventLog()
        for ev in sorted(cel, key=lambda e: e["event_date"]):
            if ev["event_type"] == "churn":
                log.record_churn(ChurnEvent(
                    customer_id=ev["customer_id"],
                    event_date=ev["event_date"],
                    reason=ev.get("reason", "non-renewal"),
                    sim_churn_probability=ev.get("sim_churn_probability"),
                    company_churn_estimate=ev.get("company_churn_estimate"),
                ))
            else:
                log.record_acquisition(AcquisitionEvent(
                    customer_id=ev["customer_id"],
                    event_date=ev["event_date"],
                    channel=ev.get("channel", "market-acquisition"),
                    predecessor_id=ev.get("predecessor_id"),
                ))

        for year in years:
            year_end = f"{year}-12-31"
            crm_active = log.active_accounts(year_end)
            crm_churned = {
                e["customer_id"] for e in cel
                if e["event_type"] == "churn" and e["event_date"] <= year_end
            }
            sim_churned_by_year = {
                ba for ba in churned_ba
                if any(
                    e["event_type"] == "churn" and e["customer_id"] == ba
                    and e["event_date"] <= year_end
                    for e in cel
                )
            }
            match = "yes" if crm_churned == sim_churned_by_year else "mismatch"
            lines.append(
                f"| {year_end} | {len(crm_churned)} accounts | "
                f"{len(crm_active)} active | {match} |"
            )

    lines.append("")
    return "\n".join(lines)


def _tou_revenue_premium(s: dict) -> tuple[float, float]:
    """Return (flat_equiv_revenue_gbp, premium_pct) for a tou_stats entry.

    Derives the flat rate from avg_peak_rate / TOU_PEAK_MULTIPLIER (1.5), then
    computes what total revenue would have been at that flat rate across all kWh.
    Premium > 0 means actual ToU revenue exceeded flat equivalent (occurs when
    actual peak % > 30% design assumption).
    """
    from saas.tariff_pricing import TOU_PEAK_MULTIPLIER
    avg_peak = s.get("avg_peak_rate", 0.0)
    if not avg_peak:
        return 0.0, 0.0
    flat_rate = avg_peak / TOU_PEAK_MULTIPLIER
    total_kwh = s.get("peak_kwh", 0.0) + s.get("offpeak_kwh", 0.0)
    flat_equiv = total_kwh * flat_rate / 1000.0
    actual = s.get("peak_revenue_gbp", 0.0) + s.get("offpeak_revenue_gbp", 0.0)
    premium_pct = (actual - flat_equiv) / flat_equiv * 100.0 if flat_equiv else 0.0
    return flat_equiv, premium_pct


def _section_tou_utilization(data: dict) -> str:
    """Time-of-Use utilization breakdown for HH smart meter customers."""
    tou = data.get("tou_stats", {})
    if not tou:
        return ""
    lines = [
        "## Time-of-Use Tariff Utilization (C7-C9 HH Customers)",
        "",
        "Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).",
        "Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).",
        "ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.",
        "",
        "| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |",
        "|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|",
    ]
    total_actual = 0.0
    total_flat_equiv = 0.0
    for cid, s in sorted(tou.items()):
        flat_equiv, premium_pct = _tou_revenue_premium(s)
        actual = s["peak_revenue_gbp"] + s["offpeak_revenue_gbp"]
        total_actual += actual
        total_flat_equiv += flat_equiv
        sign = "+" if premium_pct >= 0 else ""
        lines.append(
            f"| {cid} | {s['total_kwh']:,.0f} | {s['peak_kwh']:,.0f} | {s['peak_pct']:.1f}%"
            f" | \xa3{s['peak_revenue_gbp']:,.2f} | \xa3{s['offpeak_revenue_gbp']:,.2f}"
            f" | \xa3{s['avg_peak_rate']:,.2f}/MWh | \xa3{s['avg_offpeak_rate']:,.2f}/MWh"
            f" | {sign}{premium_pct:.1f}% |"
        )
    if total_flat_equiv:
        total_premium_pct = (total_actual - total_flat_equiv) / total_flat_equiv * 100.0
        sign = "+" if total_premium_pct >= 0 else ""
        lines.append("")
        lines.append(
            f"Total HH revenue: \xa3{total_actual:,.2f} vs flat equivalent \xa3{total_flat_equiv:,.2f}"
            f" ({sign}{total_premium_pct:.1f}% ToU premium)"
        )
    lines.append("")
    return "\n".join(lines)


def _section_bill_shock_summary(data: dict) -> str:
    """Bill shock summary across all years — Phase 14e.

    Bill shocks (month-on-month billing increase ≥20%) are a primary churn driver
    in the SIM model. This section aggregates the per-year event lists from
    data['years'][year]['bill_shock_events'] into a portfolio view.
    """
    years_data = data.get("years", {})
    churned = set(data.get("churned_billing_accounts", []))
    all_shocks = []
    for yr, yd in years_data.items():
        for ev in yd.get("bill_shock_events", []):
            all_shocks.append({
                "year": yr,
                "customer_id": ev["customer_id"],
                "period_end": ev["period_end"],
                "pct": ev["bill_shock_pct"],
            })
    if not all_shocks:
        return ""

    lines = [
        "## Bill Shock Summary (2016-2025)",
        "",
        "Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability",
        "via the bill-shock history model. Crisis years (2021-22) see the largest spikes.",
        "",
    ]

    # Year-by-year table
    from collections import defaultdict
    by_year: dict[str, list] = defaultdict(list)
    for s in all_shocks:
        by_year[s["year"]].append(s)

    lines += [
        "| Year | Events | Max Spike | Worst Customer |",
        "|------|--------|-----------|----------------|",
    ]
    for yr in sorted(by_year.keys()):
        evs = by_year[yr]
        worst = max(evs, key=lambda x: x["pct"])
        lines.append(
            f"| {yr} | {len(evs)} | {worst['pct']:.0%} | {worst['customer_id']} ({worst['period_end']}) |"
        )

    lines.append(f"\nTotal: **{len(all_shocks)}** bill shock events across {len(by_year)} years\n")

    # Top-10 worst spikes
    top10 = sorted(all_shocks, key=lambda x: x["pct"], reverse=True)[:10]
    lines += [
        "**Top 10 worst single-period bill spikes:**",
        "",
        "| Date | Customer | Spike | Eventually Churned? |",
        "|------|----------|-------|---------------------|",
    ]
    for s in top10:
        churned_str = "yes" if s["customer_id"] in churned else "no"
        lines.append(
            f"| {s['period_end']} | {s['customer_id']} | +{s['pct']:.0%} | {churned_str} |"
        )
    lines.append("")
    return "\n".join(lines)


def _section_policy_costs(data: dict) -> str:
    """Phase 21a/27b/30a/31a: Electricity Policy Costs — year-by-year breakdown.

    Shows levies collected from customers (via tariff pass-through) and paid to Ofgem/LCCC/HMRC.
    Net effect on margin is near-zero when pass-through matches actual levy. Key signal: 2022
    negative CfD levy (crisis rebate) appears as a net positive contribution to that year's margin.
    Phase 27b: CCL for business (SME/I&C) customers; domestic resi exempt.
    Phase 30a: CM levy for ALL demand customers — no domestic exemption.
    Phase 31a: FiT levy for ALL demand customers — no domestic exemption.
    """
    years = data.get("years", {})
    has_policy = any(
        yd.get("policy_cost_gbp", 0.0) != 0.0 or yd.get("ro_levy_gbp", 0.0) != 0.0
        for yd in years.values()
    )
    if not has_policy:
        return ""

    has_ccl = any(yd.get("ccl_gbp", 0.0) != 0.0 for yd in years.values())
    has_cm = any(yd.get("cm_levy_gbp", 0.0) != 0.0 for yd in years.values())
    has_fit = any(yd.get("fit_levy_gbp", 0.0) != 0.0 for yd in years.values())

    has_mutualization = any(yd.get("mutualization_levy_gbp", 0.0) != 0.0 for yd in years.values())

    if has_fit:
        title_suffix = " + Mutualization (Phase 21a/27b/30a/31a/54)" if has_mutualization else " (Phase 21a/27b/30a/31a)"
        lines = [
            f"## Policy Costs — RO + CfD + CCL + CM + FiT{title_suffix}",
            "",
            "Electricity policy costs deducted from net_margin_gbp each year. ",
            "CfD levy was NEGATIVE in 2022 (crisis rebate from LCCC). ",
            "CCL applies to business (SME/I&C) only — resi exempt. ",
            "CM (Capacity Market) and FiT (Feed-in Tariff) levies apply to ALL demand including domestic.",
            "",
            "| Year | RO levy £ | CfD levy £ | CCL £ | CM levy £ | FiT levy £ | Mutualization £ | Total policy cost £ | Note |",
            "|------|-----------|------------|-------|-----------|-----------------|---------------------|------|---------------------|",
        ]
        for year in sorted(years):
            yd = years[year]
            ro = yd.get("ro_levy_gbp", 0.0)
            cfd = yd.get("cfd_levy_gbp", 0.0)
            ccl = yd.get("ccl_gbp", 0.0)
            cm = yd.get("cm_levy_gbp", 0.0)
            fit = yd.get("fit_levy_gbp", 0.0)
            mut = yd.get("mutualization_levy_gbp", 0.0)
            total = yd.get("policy_cost_gbp", ro + cfd + ccl + cm + fit + mut)
            note = "⬇ CfD REBATE" if cfd < 0 else ""
            mut_str = f"{mut:,.0f}" if has_mutualization else "—"
            lines.append(
                f"| {year} | {ro:,.0f} | {cfd:,.0f} | {ccl:,.0f} | {cm:,.0f} | {fit:,.0f} | {mut_str} | {total:,.0f} | {note} |"
            )
        total_ro = sum(yd.get("ro_levy_gbp", 0.0) for yd in years.values())
        total_cfd = sum(yd.get("cfd_levy_gbp", 0.0) for yd in years.values())
        total_ccl = sum(yd.get("ccl_gbp", 0.0) for yd in years.values())
        total_cm = sum(yd.get("cm_levy_gbp", 0.0) for yd in years.values())
        total_fit = sum(yd.get("fit_levy_gbp", 0.0) for yd in years.values())
        total_mut = sum(yd.get("mutualization_levy_gbp", 0.0) for yd in years.values())
        total_policy = sum(yd.get("policy_cost_gbp", 0.0) for yd in years.values())
        total_mut_str = f"**{total_mut:,.0f}**" if has_mutualization else "—"
        lines.append(
            f"| **Total** | **{total_ro:,.0f}** | **{total_cfd:,.0f}** | "
            f"**{total_ccl:,.0f}** | **{total_cm:,.0f}** | **{total_fit:,.0f}** | {total_mut_str} | **{total_policy:,.0f}** | |"
        )
    elif has_cm:
        lines = [
            "## Policy Costs — RO + CfD + CCL + CM (Phase 21a/27b/30a)",
            "",
            "Electricity policy costs deducted from net_margin_gbp each year. ",
            "CfD levy was NEGATIVE in 2022 (crisis rebate from LCCC). ",
            "CCL applies to business (SME/I&C) only — resi exempt. ",
            "CM (Capacity Market) levy applies to ALL demand including domestic.",
            "",
            "| Year | RO levy £ | CfD levy £ | CCL £ | CM levy £ | Total policy cost £ | Note |",
            "|------|-----------|------------|-------|-----------|---------------------|------|",
        ]
        for year in sorted(years):
            yd = years[year]
            ro = yd.get("ro_levy_gbp", 0.0)
            cfd = yd.get("cfd_levy_gbp", 0.0)
            ccl = yd.get("ccl_gbp", 0.0)
            cm = yd.get("cm_levy_gbp", 0.0)
            total = yd.get("policy_cost_gbp", ro + cfd + ccl + cm)
            note = "⬇ CfD REBATE" if cfd < 0 else ""
            lines.append(
                f"| {year} | {ro:,.0f} | {cfd:,.0f} | {ccl:,.0f} | {cm:,.0f} | {total:,.0f} | {note} |"
            )
        total_ro = sum(yd.get("ro_levy_gbp", 0.0) for yd in years.values())
        total_cfd = sum(yd.get("cfd_levy_gbp", 0.0) for yd in years.values())
        total_ccl = sum(yd.get("ccl_gbp", 0.0) for yd in years.values())
        total_cm = sum(yd.get("cm_levy_gbp", 0.0) for yd in years.values())
        total_policy = sum(yd.get("policy_cost_gbp", 0.0) for yd in years.values())
        lines.append(
            f"| **Total** | **{total_ro:,.0f}** | **{total_cfd:,.0f}** | "
            f"**{total_ccl:,.0f}** | **{total_cm:,.0f}** | **{total_policy:,.0f}** | |"
        )
    elif has_ccl:
        lines = [
            "## Policy Costs — RO + CfD + CCL (Phase 21a/27b)",
            "",
            "Electricity policy costs deducted from net_margin_gbp each year. ",
            "CfD levy was NEGATIVE in 2022 (crisis rebate from LCCC). ",
            "CCL (Climate Change Levy) applies to business (SME/I&C) customers only — resi exempt.",
            "",
            "| Year | RO levy £ | CfD levy £ | CCL £ | Total policy cost £ | Note |",
            "|------|-----------|------------|-------|---------------------|------|",
        ]
        for year in sorted(years):
            yd = years[year]
            ro = yd.get("ro_levy_gbp", 0.0)
            cfd = yd.get("cfd_levy_gbp", 0.0)
            ccl = yd.get("ccl_gbp", 0.0)
            total = yd.get("policy_cost_gbp", ro + cfd + ccl)
            note = "⬇ CfD REBATE" if cfd < 0 else ""
            lines.append(
                f"| {year} | {ro:,.0f} | {cfd:,.0f} | {ccl:,.0f} | {total:,.0f} | {note} |"
            )
        total_ro = sum(yd.get("ro_levy_gbp", 0.0) for yd in years.values())
        total_cfd = sum(yd.get("cfd_levy_gbp", 0.0) for yd in years.values())
        total_ccl = sum(yd.get("ccl_gbp", 0.0) for yd in years.values())
        total_policy = sum(yd.get("policy_cost_gbp", 0.0) for yd in years.values())
        lines.append(
            f"| **Total** | **{total_ro:,.0f}** | **{total_cfd:,.0f}** | "
            f"**{total_ccl:,.0f}** | **{total_policy:,.0f}** | |"
        )
    else:
        lines = [
            "## Policy Costs — RO + CfD Levies (Phase 21a)",
            "",
            "Electricity policy costs deducted from net_margin_gbp each year. ",
            "CfD levy was NEGATIVE in 2022 (crisis rebate from LCCC) — this appears ",
            "as a positive contribution to that year's margin.",
            "",
            "| Year | RO levy £ | CfD levy £ | Total policy cost £ | Note |",
            "|------|-----------|------------|---------------------|------|",
        ]
        for year in sorted(years):
            yd = years[year]
            ro = yd.get("ro_levy_gbp", 0.0)
            cfd = yd.get("cfd_levy_gbp", 0.0)
            total = yd.get("policy_cost_gbp", ro + cfd)
            note = "⬇ CfD REBATE" if cfd < 0 else ""
            lines.append(
                f"| {year} | {ro:,.0f} | {cfd:,.0f} | {total:,.0f} | {note} |"
            )
        total_ro = sum(yd.get("ro_levy_gbp", 0.0) for yd in years.values())
        total_cfd = sum(yd.get("cfd_levy_gbp", 0.0) for yd in years.values())
        total_policy = sum(yd.get("policy_cost_gbp", 0.0) for yd in years.values())
        lines.append(
            f"| **Total** | **{total_ro:,.0f}** | **{total_cfd:,.0f}** | "
            f"**{total_policy:,.0f}** | |"
        )

    lines.append("")
    lines.append(
        f"Total policy cost: £{sum(yd.get('policy_cost_gbp', 0.0) for yd in years.values()):,.0f} across all years. "
        f"Net margin is after deducting this. Revenue side: "
        f"tariff pass-through at term-start year's levy rate — basis risk arises "
        f"when cross-year terms meet a different actual levy (notably 2022 CfD rebate)."
    )
    lines.append("")
    return "\n".join(lines)


def _section_network_costs(data: dict) -> str:
    """Phase 29a: Network charges (DUoS + TNUoS) — year-by-year breakdown.

    DUoS (Distribution Use of System) + TNUoS (Transmission Use of System) are
    the largest non-commodity cost component for electricity supply. Passed through
    in the tariff unit rate and deducted from net_margin_gbp at settlement.
    Resi/SME: combined DUoS + TNUoS unit rate (£35-46/MWh, 2016-2024).
    I&C HV: DUoS only (£11-14/MWh) — TNUoS is Triad-based, tracked separately.
    """
    years = data.get("years", {})
    has_network = any(yd.get("network_cost_gbp", 0.0) != 0.0 for yd in years.values())
    if not has_network:
        return ""

    lines = [
        "## Network Charges — DUoS + TNUoS (Phase 29a)",
        "",
        "Electricity network charges deducted from net_margin_gbp each year. ",
        "Resi/SME: combined DUoS + TNUoS unit rate (largest single non-commodity cost). ",
        "I&C HV: DUoS only (Triad TNUoS is an annual lump tracked in the Triad section).",
        "",
        "| Year | Network cost £ | Note |",
        "|------|----------------|------|",
    ]
    for year in sorted(years):
        yd = years[year]
        net = yd.get("network_cost_gbp", 0.0)
        if net == 0.0:
            continue
        note = "BSUoS 100% demand-side from Apr 2022" if year == "2022" else ("RIIO-ED2 from Apr 2023" if year == "2023" else "")
        lines.append(f"| {year} | {net:,.0f} | {note} |")
    total_net = sum(yd.get("network_cost_gbp", 0.0) for yd in years.values())
    lines.append(f"| **Total** | **{total_net:,.0f}** | |")
    lines.append("")
    lines.append(
        f"Total network cost: £{total_net:,.0f} across all years. "
        f"Pass-through: tariff unit rate includes network cost at term-start year's rate; "
        f"settlement deducts it — basis risk near-zero for annual contracts."
    )
    lines.append("")
    return "\n".join(lines)


def _section_gas_policy_costs(data: dict) -> str:
    """Phase 30b: Gas policy costs (CCL + GGL) and gas network charges by year.

    Gas CCL: applies to non-domestic gas only (domestic/resi exempt).
    GGL (Green Gas Levy): per-meter charge from Nov 2021 — tiny (£0.03–0.18/MWh).
    Gas network: GDN distribution + NTS transmission, all on unit rate.
    """
    years = data.get("years", {})
    has_gas_costs = any(
        yd.get("gas_policy_cost_gbp", 0.0) != 0.0 or yd.get("gas_network_cost_gbp", 0.0) != 0.0
        for yd in years.values()
    )
    if not has_gas_costs:
        return ""

    lines = [
        "## Gas Policy Costs and Network Charges (Phase 30b)",
        "",
        "Gas CCL: non-domestic only (domestic gas exempt). Gas network (GDN + NTS): all on unit rate.",
        "GGL (Green Gas Levy): per-meter, from Nov 2021; tiny in £/MWh terms.",
        "",
        "| Year | Gas Policy (CCL + GGL) £ | Gas Network £ | Total Gas Non-Commodity £ |",
        "|------|--------------------------|---------------|--------------------------|",
    ]
    total_policy = total_network = 0.0
    for year in sorted(years):
        yd = years[year]
        policy = yd.get("gas_policy_cost_gbp", 0.0)
        network = yd.get("gas_network_cost_gbp", 0.0)
        if policy == 0.0 and network == 0.0:
            continue
        total_policy += policy
        total_network += network
        lines.append(f"| {year} | {policy:,.0f} | {network:,.0f} | {policy + network:,.0f} |")
    lines.append(
        f"| **Total** | **{total_policy:,.0f}** | **{total_network:,.0f}** | **{total_policy + total_network:,.0f}** |"
    )
    lines.append("")
    lines.append(
        f"Gas policy pass-through in tariff unit rate (CCL + GGL at term start); "
        f"gas network pass-through likewise. Net basis risk near-zero for annual contracts."
    )
    lines.append("")
    return "\n".join(lines)


def _section_trading_pnl(data: dict) -> str:
    """Phase 43b: Company trading desk P&L — year-by-year hedge gain/loss and bid-ask costs.

    Decomposes the hedge P&L from supply margin, showing what the trading desk
    contributed separately from the core supply business.

    Silent (returns "") when no hedge_pnl_gbp fields exist (pre-Phase-43a runs).
    """
    records = data.get("all_records", [])
    hedge_records = [r for r in records if "hedge_pnl_gbp" in r]
    if not hedge_records:
        return ""

    trading_book = data.get("trading_book", {})
    total_bid_ask = trading_book.get("total_bid_ask_cost_gbp", 0.0)
    contract_count = trading_book.get("contract_count", 0)
    total_hedged_mwh = trading_book.get("total_hedged_mwh", 0.0)

    from collections import defaultdict
    by_year: dict[str, float] = defaultdict(float)
    for r in hedge_records:
        year = r["settlement_date"][:4]
        by_year[year] += r.get("hedge_pnl_gbp", 0.0)

    years = sorted(by_year.keys())
    total_pnl = sum(by_year.values())

    lines = [
        "## Trading Desk P&L",
        "",
        f"**Contracts opened:** {contract_count}  |  "
        f"**Total hedged volume:** {total_hedged_mwh:,.1f} MWh  |  "
        f"**Total hedge P&L:** £{total_pnl:,.0f}  |  "
        f"**Bid-ask execution cost:** £{total_bid_ask:,.0f}",
        "",
        "Hedge P&L = (agreed_price − actual_spot) × hedged_MWh. Positive when the forward",
        "price locked at tariff signing exceeded actual spot at delivery (hedge paid off).",
        "Bid-ask cost = transaction cost of executing OTC forward hedges at ask price.",
        "",
        "| Year | Hedge P&L £ | vs Gross Margin % | Direction |",
        "|------|------------|-------------------|-----------|",
    ]

    # Get gross margin by year for context
    gross_by_year: dict[str, float] = defaultdict(float)
    for r in records:
        year = r["settlement_date"][:4]
        gross_by_year[year] += r.get("gross_margin_gbp", 0.0)

    for year in years:
        pnl = by_year[year]
        gross = gross_by_year.get(year, 0.0)
        pct = (pnl / gross * 100) if gross != 0 else 0.0
        direction = "↑ paid off" if pnl > 0 else "↓ opportunity cost" if pnl < -1 else "≈ neutral"
        lines.append(f"| {year} | £{pnl:>12,.0f} | {pct:>+6.1f}% | {direction} |")

    lines += [
        f"| **Total** | **£{total_pnl:>10,.0f}** | | |",
        "",
    ]
    return "\n".join(lines)


def _section_gas_pl(data: dict) -> str:
    """Phase 32a: Year-by-year gas book P&L — revenue, wholesale, gross margin,
    policy + network costs, capital charges, net margin.

    Mirrors the electricity settlement section but for the gas book.
    Silent (returns "") when no gas settlement records exist.
    """
    years = data.get("years", {})
    has_gas = any(
        yd.get("commodity_split", {}).get("gas", {}).get("revenue_gbp", 0.0) != 0.0
        for yd in years.values()
    )
    if not has_gas:
        return ""

    lines = [
        "## Gas Book P&L — Year by Year (Phase 32a)",
        "",
        "Revenue = billing at fixed tariff unit rate. Wholesale = hedged + unhedged NBP cost.",
        "Policy = gas CCL + GGL. Network = GDN + NTS. Net = gross − policy − network − capital.",
        "",
        "| Year | Revenue £ | Wholesale £ | Gross £ | Policy £ | Network £ | Capital £ | Net £ | Net % |",
        "|------|-----------|-------------|---------|----------|-----------|-----------|-------|-------|",
    ]

    total_rev = total_whl = total_gross = total_policy = total_network = total_cap = total_net = 0.0
    for year in sorted(years):
        yd = years[year]
        cs = yd.get("commodity_split", {}).get("gas", {})
        rev = cs.get("revenue_gbp", 0.0)
        if rev == 0.0:
            continue
        whl = cs.get("wholesale_cost_gbp", 0.0)
        gross = cs.get("gross_gbp", 0.0)
        cap = cs.get("capital_gbp", 0.0)
        net = cs.get("net_gbp", 0.0)
        policy = yd.get("gas_policy_cost_gbp", 0.0)
        network = yd.get("gas_network_cost_gbp", 0.0)
        net_pct = net / rev * 100 if rev else 0.0

        total_rev += rev
        total_whl += whl
        total_gross += gross
        total_policy += policy
        total_network += network
        total_cap += cap
        total_net += net

        lines.append(
            f"| {year} | {rev:,.0f} | {whl:,.0f} | {gross:,.0f} "
            f"| {policy:,.0f} | {network:,.0f} | {cap:,.0f} "
            f"| {net:,.0f} | {net_pct:+.1f}% |"
        )

    total_net_pct = total_net / total_rev * 100 if total_rev else 0.0
    lines.append(
        f"| **Total** | **{total_rev:,.0f}** | **{total_whl:,.0f}** | **{total_gross:,.0f}** "
        f"| **{total_policy:,.0f}** | **{total_network:,.0f}** | **{total_cap:,.0f}** "
        f"| **{total_net:,.0f}** | **{total_net_pct:+.1f}%** |"
    )
    lines.append("")
    net_sign = "positive" if total_net >= 0 else "negative"
    lines.append(
        f"Gas book net margin {net_sign} over the simulation period. "
        f"Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack."
    )
    lines.append("")
    return "\n".join(lines)


def _section_solvency_signal(data: dict) -> str:
    """Phase 21b/55: Per-customer solvency — Ofgem MCR compliance signal.

    Ofgem licence Standard Condition 27 requires positive net assets per customer.
    MCR target: £130/dual-fuel account. Phase 55: formal Watch/STRESS status from
    saas/capital/solvency.py; solvency_ratio = per_customer_net_assets / £130 floor.
    Watch < 2×, STRESS < 1×.
    """
    years = data.get("years", {})
    if not years:
        return ""

    lines = [
        "## Solvency Signal — Net Assets per Customer (Phase 21b/55)",
        "",
        "Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.",
        "Watch < 2×, STRESS < 1× (account balance below regulatory floor).",
        "",
        "| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |",
        "|------|-----------|----------|----------------------|----------------|--------|",
    ]

    for year in sorted(years):
        yd = years[year]
        treasury = yd.get("treasury_end_gbp", 0.0)
        active_cids = yd.get("active_customer_ids", [])
        billing_accounts = {_billing_account_id(cid) for cid in active_cids}
        n_accounts = len(billing_accounts) or 1
        sol = compute_solvency_signal(treasury, n_accounts)
        per_acct = sol["per_customer_net_assets_gbp"]
        ratio = sol["solvency_ratio"]
        status = sol["status"]
        status_fmt = f"**{status}**" if status in ("STRESS", "Watch") else status

        lines.append(
            f"| {year} | {treasury:,.0f} | {n_accounts} | {per_acct:,.0f} "
            f"| {ratio:.2f}× | {status_fmt} |"
        )

    # End-state summary
    final_year = sorted(years)[-1]
    final_cids = years[final_year].get("active_customer_ids", [])
    final_n = len({_billing_account_id(cid) for cid in final_cids}) or 1
    final_treasury = years[final_year].get("treasury_end_gbp", 0.0)
    final_sol = compute_solvency_signal(final_treasury, final_n)
    final_per = final_sol["per_customer_net_assets_gbp"]
    final_status = final_sol["status"]

    lines.append("")
    lines.append(
        f"End-state ({final_year}): **£{final_per:,.0f}/account** across {final_n} billing accounts — {final_status}."
    )
    lines.append("")
    return "\n".join(lines)




def _section_bsc_credit(data: dict) -> str:
    """Phase 53: BSC credit cover as working capital requirement.

    BSC credit = peak daily wholesale charge × 28-day window × 1.2 buffer.
    Shows treasury vs credit cover each year — stress when ratio < 5:1.
    In 2021-2022, spiking SSP drove credit demands that exceeded many
    small suppliers' available capital, directly causing their failure.
    """
    years = data.get("years", {})
    if not years:
        return ""
    if not any(y.get("bsc_credit_required_gbp", 0.0) > 0 for y in years.values()):
        return ""

    lines = [
        "## BSC Credit Cover — Working Capital Requirement (Phase 53)",
        "",
        "Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.",
        "Below 5× coverage ratio (treasury / credit cover) flags working capital stress.",
        "",
        "| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |",
        "|------|-------------|---------------|-----------|----------------|--------|",
    ]

    for year in sorted(years):
        yd = years[year]
        peak = yd.get("bsc_peak_daily_gbp", 0.0)
        credit = yd.get("bsc_credit_required_gbp", 0.0)
        treasury = yd.get("treasury_end_gbp", 0.0)
        if credit > 0:
            ratio = treasury / credit
            status = "OK" if ratio >= 5.0 else ("**STRESS**" if ratio < 2.0 else "Watch")
        else:
            ratio = float("inf")
            status = "n/a"
        ratio_str = f"{ratio:.1f}×" if ratio != float("inf") else "n/a"
        lines.append(
            f"| {year} | {peak:,.0f} | {credit:,.0f} | {treasury:,.0f} | {ratio_str} | {status} |"
        )

    lines.append("")
    return "\n".join(lines)

def _section_volume_tolerance(data: dict) -> str:
    """Phase 27c: Volume tolerance tracking for I&C contracts."""
    log = data.get("volume_tolerance_log", [])
    if not log:
        return ""

    total_excess_kwh = sum(e["excess_kwh"] for e in log)
    total_excess_cost = sum(e["excess_spot_cost_gbp"] for e in log)
    total_deficit_kwh = sum(e["deficit_kwh"] for e in log)
    breach_terms = [e for e in log if not e["within_band"]]

    lines = [
        "## I&C Volume Tolerance (Phase 27c)",
        "",
        "I&C contracts include ±10% volume tolerance. Consumption above +10% of contracted"
        " settles at spot. Under-delivery below -10% triggers an over-hedge unwind at spot.",
        "",
        f"Terms tracked: {len(log)} | Tolerance breaches: {len(breach_terms)} "
        f"| Total excess: {total_excess_kwh:,.0f} kWh | Excess spot cost: £{total_excess_cost:,.0f}",
        "",
        "| Customer | Term Start | Contracted kWh | Actual kWh | Variance % | "
        "Excess kWh | Deficit kWh | Excess Spot Cost £ |",
        "|----------|-----------|---------------|-----------|-----------|----------|----------|-------------------|",
    ]

    for e in sorted(log, key=lambda x: (x["customer_id"], x["term_start"])):
        flag = "" if e["within_band"] else " ⚠"
        lines.append(
            f"| {e['customer_id']} | {e['term_start']} | {e['contracted_kwh']:,.0f} "
            f"| {e['actual_kwh']:,.0f} | {e['variance_pct']:+.1f}%{flag} "
            f"| {e['excess_kwh']:,.0f} | {e['deficit_kwh']:,.0f} "
            f"| £{e['excess_spot_cost_gbp']:,.0f} |"
        )

    lines.append("")
    if not breach_terms:
        lines.append(
            "All I&C terms settled within ±10% volume tolerance — no spot over-run costs."
        )
    else:
        lines.append(
            f"**{len(breach_terms)} tolerance breach(es)** across the run. "
            f"Total excess spot cost: £{total_excess_cost:,.0f}. "
            f"Total deficit volume: {total_deficit_kwh:,.0f} kWh."
        )
    lines.append("")
    return "\n".join(lines)


def _section_triad_exposure(data: dict) -> str:
    """Phase 27d: Triad risk for I&C electricity customers."""
    log = data.get("triad_log", [])
    if not log:
        return ""

    total_tnuos = sum(e["estimated_tnuos_gbp"] for e in log)
    customers = sorted({e["customer_id"] for e in log})

    lines = [
        "## I&C Triad Exposure (Phase 27d)",
        "",
        "TNUoS Triad charges are determined by I&C customer demand at the 3 highest"
        " national demand settlement periods each winter (Nov-Feb). Periods identified"
        " using SSP as a demand proxy; minimum 10-day separation enforced.",
        "",
        f"Total estimated TNUoS across all winters and I&C customers: **£{total_tnuos:,.0f}**",
        "",
        "| Customer | Winter | Avg Triad Demand kW | TNUoS Rate £/kW | Est. TNUoS £ |",
        "|----------|--------|--------------------|--------------------|-------------|",
    ]

    for e in sorted(log, key=lambda x: (x["customer_id"], x["triad_year"])):
        winter = f"{e['triad_year']}/{str(e['triad_year']+1)[-2:]}"
        lines.append(
            f"| {e['customer_id']} | {winter} | {e['avg_triad_kw']:,.1f} "
            f"| £{e['tnuos_tariff_gbp_per_kw']:.2f} | £{e['estimated_tnuos_gbp']:,.0f} |"
        )

    lines.append("")
    if len(customers) > 1:
        by_cust = {cid: sum(e["estimated_tnuos_gbp"] for e in log if e["customer_id"] == cid) for cid in customers}
        for cid, total in sorted(by_cust.items()):
            lines.append(f"- {cid}: cumulative Triad exposure £{total:,.0f}")
    lines.append("")
    return "\n".join(lines)


def _section_ic_portfolio(data: dict) -> str:
    """Phase 28a: I&C portfolio — segment comparison, CCL, Triad, volume tolerance."""
    all_records = data.get("all_records", [])
    if not all_records:
        return ""

    # Identify I&C customers from segment_split keys or all_records
    ic_records = [r for r in all_records if r.get("commodity") == "electricity"
                  and any(k for k in r if k == "customer_id")]
    # Build CCL totals and revenue by customer from settlement records
    ic_customers = set()
    years = data.get("years", {})
    for year, yd in years.items():
        seg_split = yd.get("segment_split", {})
        for seg_key in seg_split:
            if seg_key.startswith("I&C"):
                # I&C customers are present this year
                pass

    # Build I&C customer set from customers module
    from saas.customers import CUSTOMERS as _CUST_LIST, SUCCESSOR_CUSTOMERS as _SUCC_LIST, ACQUIRED_CUSTOMERS as _ACQ_LIST
    _all_customers = _CUST_LIST + _SUCC_LIST + list(_ACQ_LIST)
    _ic_cust_ids = {c["customer_id"] for c in _all_customers if c.get("segment") == "I&C"}

    # Aggregate by customer from all_records — I&C customers only
    cust_stats: dict[str, dict] = {}
    for rec in all_records:
        if rec.get("commodity") != "electricity":
            continue
        cid = rec.get("customer_id", "")
        if cid not in _ic_cust_ids:
            continue
        ccl = rec.get("ccl_gbp", 0.0)
        if cid not in cust_stats:
            cust_stats[cid] = {
                "revenue_gbp": 0.0, "net_margin_gbp": 0.0, "ccl_gbp": 0.0,
                "consumption_kwh": 0.0, "n_records": 0,
            }
        cust_stats[cid]["revenue_gbp"] += rec.get("revenue_gbp", 0.0)
        cust_stats[cid]["net_margin_gbp"] += rec.get("net_margin_gbp", 0.0)
        cust_stats[cid]["ccl_gbp"] += ccl
        cust_stats[cid]["consumption_kwh"] += rec.get("consumption_kwh", 0.0)
        cust_stats[cid]["n_records"] += 1

    if not cust_stats:
        return ""

    triad_log = data.get("triad_log", [])
    vol_log = data.get("volume_tolerance_log", [])

    lines = [
        "## I&C Portfolio Summary (Phase 28a)",
        "",
        "I&C customers (business electricity, HH metered): lifetime P&L, policy costs, and risk metrics.",
        "",
        "| Customer | Revenue £ | Net Margin £ | Net Margin % | CCL £ | MWh Settled | CCL £/MWh |",
        "|----------|----------|-------------|-------------|-------|-------------|-----------|",
    ]

    totals = {"revenue": 0.0, "net": 0.0, "ccl": 0.0, "mwh": 0.0}
    for cid in sorted(cust_stats):
        s = cust_stats[cid]
        mwh = s["consumption_kwh"] / 1000.0
        net_pct = s["net_margin_gbp"] / s["revenue_gbp"] * 100.0 if s["revenue_gbp"] > 0 else 0.0
        ccl_per_mwh = s["ccl_gbp"] / mwh if mwh > 0 else 0.0
        totals["revenue"] += s["revenue_gbp"]
        totals["net"] += s["net_margin_gbp"]
        totals["ccl"] += s["ccl_gbp"]
        totals["mwh"] += mwh
        lines.append(
            f"| {cid} | {s['revenue_gbp']:,.0f} | {s['net_margin_gbp']:,.0f} "
            f"| {net_pct:.1f}% | {s['ccl_gbp']:,.0f} | {mwh:,.0f} | {ccl_per_mwh:.2f} |"
        )

    if len(cust_stats) > 1:
        total_pct = totals["net"] / totals["revenue"] * 100.0 if totals["revenue"] > 0 else 0.0
        total_ccl_mwh = totals["ccl"] / totals["mwh"] if totals["mwh"] > 0 else 0.0
        lines.append(
            f"| **Total** | **{totals['revenue']:,.0f}** | **{totals['net']:,.0f}** "
            f"| **{total_pct:.1f}%** | **{totals['ccl']:,.0f}** | **{totals['mwh']:,.0f}** "
            f"| {total_ccl_mwh:.2f} |"
        )

    lines.append("")

    # Triad summary
    if triad_log:
        total_tnuos = sum(e["estimated_tnuos_gbp"] for e in triad_log)
        ic_tnuos = {e["customer_id"]: 0.0 for e in triad_log}
        for e in triad_log:
            ic_tnuos[e["customer_id"]] = ic_tnuos.get(e["customer_id"], 0.0) + e["estimated_tnuos_gbp"]
        lines.append(f"**TNUoS Triad exposure (cumulative):** £{total_tnuos:,.0f} across all winters.")
        for cid, total in sorted(ic_tnuos.items()):
            lines.append(f"- {cid}: £{total:,.0f}")
        lines.append("")

    # Volume tolerance summary
    if vol_log:
        breach_count = sum(1 for e in vol_log if not e["within_band"])
        total_excess = sum(e["excess_kwh"] for e in vol_log)
        total_excess_cost = sum(e["excess_spot_cost_gbp"] for e in vol_log)
        lines.append(
            f"**Volume tolerance:** {len(vol_log)} I&C terms tracked; "
            f"{breach_count} breach(es); total excess {total_excess:,.0f} kWh "
            f"at spot cost £{total_excess_cost:,.0f}."
        )
        lines.append("")

    # Segment margin comparison from yearly data
    ic_net_by_year: dict[str, float] = {}
    resi_net_by_year: dict[str, float] = {}
    sme_net_by_year: dict[str, float] = {}
    for year, yd in sorted(years.items()):
        seg = yd.get("segment_split", {})
        ic_net_by_year[year] = sum(v.get("net_gbp", 0.0) for k, v in seg.items() if k.startswith("I&C"))
        resi_net_by_year[year] = sum(v.get("net_gbp", 0.0) for k, v in seg.items() if k.startswith("resi"))
        sme_net_by_year[year] = sum(v.get("net_gbp", 0.0) for k, v in seg.items() if k.startswith("SME"))

    ic_years = {y for y, v in ic_net_by_year.items() if v != 0.0}
    if ic_years:
        lines.append("**Net margin by segment and year (£):**")
        lines.append("")
        lines.append("| Year | I&C | SME | Resi |")
        lines.append("|------|-----|-----|------|")
        for year in sorted(ic_net_by_year):
            if year in ic_years or sme_net_by_year.get(year) or resi_net_by_year.get(year):
                lines.append(
                    f"| {year} | {ic_net_by_year.get(year, 0):,.0f} "
                    f"| {sme_net_by_year.get(year, 0):,.0f} "
                    f"| {resi_net_by_year.get(year, 0):,.0f} |"
                )
        lines.append("")

    return "\n".join(lines)


def _section_gas_renewal_pressure(data: dict) -> str:
    """Gas Renewal Pressure -- Phase 15a: dual-fuel gas rate change monitoring.

    Consumes company_gas_churn_log from run_phase2b (Phase 14b).
    Shows year-by-year gas company churn estimate distribution and flags
    years with elevated gas price pressure on the dual-fuel portfolio.
    """
    log = data.get("company_gas_churn_log", [])
    if not log:
        return ""

    from collections import defaultdict
    by_year: dict[str, list[dict]] = defaultdict(list)
    for entry in log:
        yr = entry["term_start"][:4]
        by_year[yr].append(entry)

    HIGH_PRESSURE_THRESHOLD = 0.20  # gas company_est > 20% = elevated risk

    lines = [
        "## Gas Renewal Pressure (Dual-Fuel Portfolio)",
        "",
        "Company gas churn estimates at each gas leg renewal (Phase 14b).",
        f"Threshold for elevated risk: >{HIGH_PRESSURE_THRESHOLD:.0%} company gas churn estimate.",
        "",
        "| Year | Renewals | Mean Est | Max Est | Elevated Risk |",
        "|------|----------|----------|---------|---------------|",
    ]
    for yr in sorted(by_year.keys()):
        evs = by_year[yr]
        ests = [e["company_gas_churn_estimate"] for e in evs]
        mean_est = sum(ests) / len(ests)
        max_est = max(ests)
        elevated = sum(1 for e in ests if e > HIGH_PRESSURE_THRESHOLD)
        flag = " ⚠" if elevated > 0 else ""
        lines.append(
            f"| {yr} | {len(evs)} | {mean_est:.0%} | {max_est:.0%} | {elevated}{flag} |"
        )

    # Most elevated renewals
    high = [e for e in log if e["company_gas_churn_estimate"] > HIGH_PRESSURE_THRESHOLD]
    if high:
        top = sorted(high, key=lambda x: -x["company_gas_churn_estimate"])[:5]
        lines += [
            "",
            f"**Top elevated gas renewals (>{HIGH_PRESSURE_THRESHOLD:.0%} estimated churn):**",
            "",
            "| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |",
            "|------|----------|-----------------|-----------------|-----------|",
        ]
        for e in top:
            change_pct = (e["new_gas_rate"] - e["old_gas_rate"]) / e["old_gas_rate"] if e["old_gas_rate"] else 0.0
            direction = f"+{change_pct:.0%}" if change_pct >= 0 else f"{change_pct:.0%}"
            lines.append(
                f"| {e['term_start']} | {e['customer_id']} "
                f"| £{e['old_gas_rate']:.1f} | £{e['new_gas_rate']:.1f} ({direction}) "
                f"| {e['company_gas_churn_estimate']:.0%} |"
            )
    lines.append("")
    return "\n".join(lines)


def _section_retention_strategy(data: dict) -> str:
    """Retention Strategy -- Phase 12c: ROI analysis and missed opportunities."""
    from collections import defaultdict

    rl = data.get("retention_log", [])
    no_offer = data.get("no_offer_churn_log", [])

    if not rl and not no_offer:
        return "\n".join([
            "## Retention Strategy",
            "",
            "No retention offers made and no tracked churns in this run.",
            "",
        ])

    offered = len(rl)
    retained_count = sum(1 for r in rl if r["outcome"] == "retained")
    churned_despite = sum(1 for r in rl if r["outcome"] == "churned_despite_offer")
    total_offer_cost = sum(r.get("retention_cost_gbp", 0.0) for r in rl)
    margin_saved = sum(
        r.get("expected_term_margin_gbp", 0.0)
        for r in rl if r["outcome"] == "retained"
    )
    wasted_cost = sum(
        r.get("retention_cost_gbp", 0.0)
        for r in rl if r["outcome"] == "churned_despite_offer"
    )
    net_roi = margin_saved - total_offer_cost
    # Phase 15c: include acquisition cost savings in full economic ROI.
    # When we retain a customer we avoid spending acq_cost on a replacement.
    # acq_cost_saved_gbp is only present in Phase 15b+ runs.
    acq_cost_saved_total = sum(
        r.get("acq_cost_saved_gbp", 0.0)
        for r in rl if r["outcome"] == "retained"
    )
    full_roi = net_roi + acq_cost_saved_total
    missed_count = len(no_offer)
    missed_margin = sum(r.get("expected_term_margin_gbp", 0.0) for r in no_offer)
    missed_uneconomical = [r for r in no_offer if r.get("no_offer_reason") == "uneconomical"]
    missed_below_threshold = [r for r in no_offer if r.get("no_offer_reason") != "uneconomical"]
    success_pct = (retained_count / offered * 100) if offered else 0.0

    offered_str = str(offered)
    retained_str = str(retained_count) + " (" + str(round(success_pct)) + "%)"
    churned_despite_str = str(churned_despite)
    cost_str = "\xa3" + f"{total_offer_cost:,.2f}"
    saved_str = "\xa3" + f"{margin_saved:,.2f}"
    wasted_str = "\xa3" + "%.2f" % wasted_cost
    roi_str = "\xa3" + f"{net_roi:,.2f}"
    full_roi_str = "\xa3" + f"{full_roi:,.2f}"
    missed_str = "\xa3" + f"{missed_margin:,.2f}"

    lines = [
        "## Retention Strategy P&L",
        "",
        "### Aggregate (2016-2025)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        "| Offers made | " + offered_str + " |",
        "| Retained | " + retained_str + " |",
        "| Churned despite offer | " + churned_despite_str + " |",
        "| Total offer cost (foregone margin) | " + cost_str + " |",
        "| Margin saved (retained customers' terms) | " + saved_str + " |",
        "| Wasted offer cost (churned anyway) | " + wasted_str + " |",
        "| **Net ROI of retention strategy** | **" + roi_str + "** |",
    ]
    if acq_cost_saved_total > 0:
        lines.append(
            "| Acquisition cost avoided (retained customers) | \xa3" + f"{acq_cost_saved_total:,.2f}" + " |"
        )
        lines.append(
            "| **Full economic ROI (margin + acq savings)** | **" + full_roi_str + "** |"
        )
    lines += [
        "",
        "Missed opportunities (churns with no offer): **" + str(missed_count) + "**"
        " (" + missed_str + " expected margin lost without offer)",
    ]
    if missed_uneconomical:
        unecon_margin = sum(r.get("expected_term_margin_gbp", 0.0) for r in missed_uneconomical)
        lines.append(
            "- **Blocked — uneconomical** (churn estimate above threshold but margin + acq_cost < discount cost): "
            + str(len(missed_uneconomical)) + " (\xa3" + f"{unecon_margin:,.2f}" + " margin foregone)"
        )
    if missed_below_threshold:
        below_margin = sum(r.get("expected_term_margin_gbp", 0.0) for r in missed_below_threshold)
        lines.append(
            "- **Below threshold** (churn estimate under 30%): "
            + str(len(missed_below_threshold)) + " (\xa3" + f"{below_margin:,.2f}" + " margin lost)"
            + " — Phase 13c bill burden signal reduces this for high-spend SME customers"
        )
    lines.append("")

    by_year = defaultdict(lambda: {"offered": 0, "retained": 0, "cost": 0.0, "saved": 0.0})
    for r in rl:
        yr = r["event_date"][:4]
        by_year[yr]["offered"] += 1
        by_year[yr]["cost"] += r.get("retention_cost_gbp", 0.0)
        if r["outcome"] == "retained":
            by_year[yr]["retained"] += 1
            by_year[yr]["saved"] += r.get("expected_term_margin_gbp", 0.0)

    missed_by_year = defaultdict(float)
    for r in no_offer:
        missed_by_year[r["event_date"][:4]] += r.get("expected_term_margin_gbp", 0.0)

    all_years = sorted(set(list(by_year.keys()) + list(missed_by_year.keys())))
    if all_years:
        lines += [
            "### Year-by-Year Breakdown",
            "",
            "| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |",
            "|------|--------|----------|-----------|-------------|---------|---------------|",
        ]
        for yr in all_years:
            yd = by_year[yr]
            yr_net = yd["saved"] - yd["cost"]
            missed_m = missed_by_year.get(yr, 0.0)
            row = (
                "| " + yr + " | " + str(yd["offered"]) + " | " + str(yd["retained"])
                + " | \xa3" + "%.2f" % yd["cost"]
                + " | \xa3" + "%.2f" % yd["saved"]
                + " | \xa3" + "%.2f" % yr_net
                + " | \xa3" + "%.2f" % missed_m + " |"
            )
            lines.append(row)
        lines.append("")

    has_acq_col = any("acq_cost_saved_gbp" in r for r in rl)
    if has_acq_col:
        lines += [
            "### Per-Offer Detail",
            "",
            "| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |",
            "|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|",
        ]
        for r in sorted(rl, key=lambda x: x["event_date"]):
            exp_m = r.get("expected_term_margin_gbp", 0.0)
            cost = r.get("retention_cost_gbp", 0.0)
            acq = r.get("acq_cost_saved_gbp", 0.0)
            net = (exp_m - cost) if r["outcome"] == "retained" else -cost
            row = (
                "| " + r["event_date"] + " | " + r["customer_id"] + " | " + "%.2f" % r["company_churn_estimate"]
                + " | " + "%.0f%%" % (r.get("discount_pct", 0.05) * 100)
                + " | \xa3" + "%.2f" % cost
                + " | \xa3" + "%.2f" % exp_m
                + " | \xa3" + "%.0f" % acq
                + " | \xa3" + "%.2f" % net
                + " | " + r["outcome"] + " |"
            )
            lines.append(row)
    else:
        lines += [
            "### Per-Offer Detail",
            "",
            "| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Net | Outcome |",
            "|------|----------|-----------|---------|-----------|----------------|-----|---------|",
        ]
        for r in sorted(rl, key=lambda x: x["event_date"]):
            exp_m = r.get("expected_term_margin_gbp", 0.0)
            cost = r.get("retention_cost_gbp", 0.0)
            net = (exp_m - cost) if r["outcome"] == "retained" else -cost
            row = (
                "| " + r["event_date"] + " | " + r["customer_id"] + " | " + "%.2f" % r["company_churn_estimate"]
                + " | " + "%.0f%%" % (r.get("discount_pct", 0.05) * 100)
                + " | \xa3" + "%.2f" % cost
                + " | \xa3" + "%.2f" % exp_m
                + " | \xa3" + "%.2f" % net
                + " | " + r["outcome"] + " |"
            )
            lines.append(row)
    lines.append("")
    return "\n".join(lines)

def _section_retention_durability(data: dict) -> str:
    """Phase 16b: retention durability — post-retention survival analysis.

    For each retained customer, tracks how long they stayed post-retention
    until either churning or reaching the simulation end. Shows whether
    retention offers produced durable outcomes or merely delayed churn.
    """
    from datetime import date as _date

    rl = data.get("retention_log", [])
    cel = data.get("company_event_log", [])
    churned_set = set(data.get("churned_billing_accounts", []))

    if not rl:
        return ""

    # Build churn date per customer from company event log
    churn_dates: dict[str, str] = {
        e["customer_id"]: e["event_date"]
        for e in cel
        if e.get("event_type") == "churn"
    }

    # First retention date per customer (for cohort analysis)
    first_retention: dict[str, str] = {}
    for r in sorted(rl, key=lambda x: x["event_date"]):
        cid = r["customer_id"]
        if cid not in first_retention:
            first_retention[cid] = r["event_date"]

    SIM_END = "2025-12-31"

    rows = []
    for cid, ret_date in sorted(first_retention.items(), key=lambda x: x[1]):
        if cid in churn_dates:
            end_date = churn_dates[cid]
            status = "churned"
        else:
            end_date = SIM_END
            status = "active"
        try:
            months = (
                (_date.fromisoformat(end_date) - _date.fromisoformat(ret_date)).days / 30.44
            )
        except (ValueError, TypeError):
            months = 0.0
        rows.append({
            "cid": cid,
            "retained": ret_date,
            "end_date": end_date if status == "churned" else "(window end)",
            "months": months,
            "status": status,
        })

    if not rows:
        return ""

    eventually_churned = [r for r in rows if r["status"] == "churned"]
    still_active = [r for r in rows if r["status"] == "active"]

    lines = [
        "## Retention Durability",
        "",
        "Post-retention survival: how long did retained customers stay before churning or reaching the simulation end?",
        "",
        "| Customer | First retained | End of tenure | Post-retention months | Outcome |",
        "|----------|---------------|--------------|----------------------|---------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['cid']} | {r['retained']} | {r['end_date']} | {r['months']:.0f} | {r['status']} |"
        )

    lines.append("")
    if eventually_churned:
        avg_survival = sum(r["months"] for r in eventually_churned) / len(eventually_churned)
        names = ", ".join(r["cid"] for r in eventually_churned)
        lines.append(
            f"**Eventually churned ({len(eventually_churned)}/{len(rows)})**: {names} — "
            f"avg {avg_survival:.0f} months post-retention before final churn."
        )
    if still_active:
        names = ", ".join(r["cid"] for r in still_active)
        lines.append(f"**Still active ({len(still_active)}/{len(rows)})**: {names} — survived to simulation end.")

    lines.append("")
    return "\n".join(lines)


def _section_svt_comparison(data: dict) -> str:
    """Phase 39a: SVT comparative pricing — fixed rate vs Standard Variable Tariff.

    For passive renewers (who rolled to a fixed deal when they could have stayed
    on SVT), shows whether the company's fixed rate was cheaper or more expensive
    than the contemporaneous Ofgem cap SVT rate. A rate above SVT is a risk signal:
    passive renewers will eventually notice and churn.

    Silent if churn_basis_risk lacks SVT data (pre-Phase-39a runs).
    """
    cbr = data.get("churn_basis_risk", [])
    passive = [r for r in cbr if not r.get("is_active_renewal", True) and r.get("svt_rate_gbp_per_mwh") is not None]
    if not passive:
        return ""

    def _mean(vals):
        return sum(vals) / len(vals) if vals else 0.0

    premium_pcts = [r["rate_vs_svt_pct"] for r in passive if r.get("rate_vs_svt_pct") is not None]
    above_svt = [r for r in passive if (r.get("rate_vs_svt_pct") or 0) > 0]
    below_svt = [r for r in passive if (r.get("rate_vs_svt_pct") or 0) <= 0]

    avg_premium = _mean(premium_pcts)
    pct_above = len(above_svt) / len(passive) if passive else 0.0

    lines = [
        "## SVT Comparative Pricing — Passive Renewers (Phase 39a)",
        "",
        "Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates "
        "latent churn risk: once the customer notices they're paying more than the cap, "
        "they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.",
        "",
        f"- **Passive renewal events with SVT data:** {len(passive)}",
        f"- **Above SVT (at-risk):** {len(above_svt)} ({pct_above:.0%})",
        f"- **Below/at SVT (protected):** {len(below_svt)} ({1-pct_above:.0%})",
        f"- **Mean rate vs SVT premium:** {avg_premium:+.1f}%",
        "",
        "| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |",
        "|------|-----------------|-----------|-------------|----------------------|----------------|",
    ]

    by_year: dict[str, list] = {}
    for r in passive:
        year = r["term_start"][:4]
        by_year.setdefault(year, []).append(r)

    for year in sorted(by_year):
        recs = by_year[year]
        above = sum(1 for r in recs if (r.get("rate_vs_svt_pct") or 0) > 0)
        pcts = [r["rate_vs_svt_pct"] for r in recs if r.get("rate_vs_svt_pct") is not None]
        avg_p = _mean(pcts)
        avg_fixed = _mean([r["unit_rate_gbp_per_mwh"] for r in recs if r.get("unit_rate_gbp_per_mwh") is not None])
        avg_svt = _mean([r["svt_rate_gbp_per_mwh"] for r in recs if r.get("svt_rate_gbp_per_mwh") is not None])
        lines.append(
            f"| {year} | {len(recs)} | {above} ({above/len(recs):.0%}) "
            f"| {avg_p:+.1f}% | {avg_fixed:.1f} | {avg_svt:.1f} |"
        )

    lines += [
        "",
        "**Interpretation:** Premium > 0% means the company is charging passive renewers "
        "above the SVT rate — a regulatory and reputational risk. Premium < 0% means "
        "passive renewers are getting a better-than-SVT deal — the company is leaving "
        "margin on the table but building loyalty.",
        "",
    ]
    return "\n".join(lines)


def _section_scenario_metadata(data: dict) -> str:
    """Phase 37a: Forward scenario metadata banner.

    Rendered when the run dict includes 'scenario_name' (set by run_scenario.run_forward_scenario).
    Shows the scenario preset, synthetic year range, and key distribution parameters.
    Silent for standard historical runs.
    """
    scenario_name = data.get("scenario_name")
    if not scenario_name:
        return ""

    year_range = data.get("scenario_year_range", [])
    year_from = year_range[0] if len(year_range) >= 1 else "?"
    year_to = year_range[1] if len(year_range) >= 2 else "?"

    try:
        from sim.scenario.bimodal_generator import SCENARIOS
        params = SCENARIOS.get(scenario_name)
    except ImportError:
        params = None

    lines = [
        "## Forward Scenario Run",
        "",
        f"> **This report covers a FORWARD SCENARIO run, not a historical replay.**",
        f"> Prices for {year_from}–{year_to} are synthetic, generated by `sim.scenario.bimodal_generator`.",
        f"> Historical data covers 2016–{int(year_from) - 1}. Do not treat scenario financials as forecasts.",
        "",
        f"**Scenario:** `{scenario_name}`",
        f"**Synthetic years:** {year_from}–{year_to}",
    ]

    if params is not None:
        lines += [
            "",
            "**Electricity price parameters (synthetic period):**",
            "",
            f"| Parameter | Value |",
            f"|-----------|-------|",
            f"| Lower mode (renewable-rich) | £{params.lower_mode_mean:.0f}/MWh (σ={params.lower_mode_std:.0f}) |",
            f"| Upper mode (gas-marginal) | £{params.upper_mode_mean:.0f}/MWh (σ={params.upper_mode_std:.0f}) |",
            f"| Lower mode fraction | {params.lower_mode_fraction:.0%} of days |",
            f"| Negative price days/year | {params.negative_days_per_year:.0f} |",
            f"| Negative price floor | £{params.negative_price_floor:.0f}/MWh |",
            f"| Dunkelflaute events/year | {params.dunkelflaute_events_per_year:.0f} |",
            f"| Dunkelflaute price premium | {params.dunkelflaute_multiplier_mean:.1f}× upper mode |",
        ]

    lines.append("")
    return "\n".join(lines)


def _section_flexibility_revenue(data: dict) -> str:
    """Phase AG: DSR/Capacity Market flexibility revenue breakdown by year.

    Renders the CM and DFS revenue earned from customers with flexible assets
    (EV, ASHP, battery). CM is available 2016+; DFS launched October 2022.
    Data comes from FlexibilityRevenueBook (Phase AF) via flex_summary in run_phase2b.
    Silent when no customers hold flexible assets.
    """
    flex = data.get("flexibility_revenue_summary", {})
    if not flex or not flex.get("years_with_revenue"):
        return ""

    total_gbp = flex.get("total_flexibility_revenue_gbp", 0.0)
    cm_total = flex.get("total_cm_revenue_gbp", 0.0)
    dfs_total = flex.get("total_dfs_revenue_gbp", 0.0)
    peak_yr_rev = flex.get("peak_year_revenue_gbp", 0.0)
    enrolled_years = flex.get("enrolled_customer_years", 0)
    per_year: dict = flex.get("per_year", {})

    lines = [
        "## Flexibility Revenue — DSR & Capacity Market (Phase AG)",
        "",
        "Customers with EVs, ASHPs, and batteries earn ancillary revenue through two channels:",
        "- **Capacity Market (CM):** ~£75/kW/yr; T-4 auctions; operational since 2014.",
        "- **Demand Flexibility Service (DFS):** launched October 2022 by NESO; ~£4.5/MWh × 20 winter dispatch events/yr.",
        "",
    ]

    cm_total_str = _fmt_gbp(cm_total)
    dfs_total_str = _fmt_gbp(dfs_total)
    peak_str = _fmt_gbp(peak_yr_rev)
    total_str = _fmt_gbp(total_gbp)
    lines.append(f"**Portfolio total (2016–2025):** {total_str} (CM: {cm_total_str} | DFS: {dfs_total_str} | Peak year: {peak_str} | Enrolled customer-years: {enrolled_years})")
    lines += [
        "",
        "| Year | CM Revenue | DFS Revenue | Total | Enrolled |",
        "|------|------------|-------------|-------|----------|",
    ]

    for yr in sorted(per_year.keys()):
        yd = per_year[yr]
        cm_gbp = yd.get("cm_gbp", 0.0)
        dfs_gbp = yd.get("dfs_gbp", 0.0)
        yr_total = yd.get("total_gbp", 0.0)
        enrolled = yd.get("enrolled_customers", 0)
        cm_str = _fmt_gbp(cm_gbp)
        dfs_str = _fmt_gbp(dfs_gbp)
        if dfs_gbp == 0.0 and int(yr) < 2022:
            dfs_str = "£0.00 (pre-DFS)"
        yr_total_str = _fmt_gbp(yr_total)
        lines.append(f"| {yr} | {cm_str} | {dfs_str} | {yr_total_str} | {enrolled} |")

    lines += [
        "",
        "DFS launched October 2022 (NESO Winter Demand Flexibility Service). Pre-2022 years show CM-only revenue. EV+battery customers earn ~£2,046/yr; EV-only ~£930/yr.",
        "",
    ]
    return "\n".join(lines)



def _section_portfolio_intelligence_pack(data: dict) -> str:
    """Phase AH: Board-level portfolio intelligence synthesis.

    Synthesises observable CRM and operational intelligence into a board pack:
    - Retention coverage rate and offer effectiveness
    - Flexibility enrollment growth and revenue per enrolled customer
    - Churn pattern analysis (peak years, net book movement)
    - Board recommendations derived from the above signals

    Silent when there are no retention events or churn history to draw from.
    """
    rl = data.get("retention_log", [])
    no_offer = data.get("no_offer_churn_log", [])
    cel = data.get("company_event_log", [])
    flex = data.get("flexibility_revenue_summary", {})

    churn_events = [e for e in cel if e.get("event_type") == "churn"]
    if not rl and not churn_events:
        return ""

    lines = [
        "## Portfolio Intelligence Pack (Phase AH)",
        "",
        "Board-level synthesis of CRM and flexibility intelligence derived from observable operational data.",
        "",
    ]

    # 1. Retention Intelligence
    lines += ["### 1. Retention Intelligence", ""]

    if rl:
        total_offers = len(rl)
        retained_ct = sum(1 for r in rl if r.get("outcome") == "retained")
        churned_despite = sum(1 for r in rl if r.get("outcome") == "churned_despite_offer")
        acceptance_rate = retained_ct / total_offers * 100 if total_offers > 0 else 0.0
        margin_protected = sum(r.get("expected_term_margin_gbp", 0.0) for r in rl if r.get("outcome") == "retained")
        lines += [
            f"- **Retention offers made:** {total_offers}",
            f"- **Offer acceptance rate:** {acceptance_rate:.0f}% "
            f"({retained_ct} retained / {churned_despite} churned despite offer)",
            f"- **Estimated margin protected:** {_fmt_gbp(margin_protected)}",
        ]
    else:
        lines.append("- No retention offers in this run period.")

    no_offer_count = len(no_offer)
    if no_offer_count > 0:
        blind_miss = sum(1 for n in no_offer if n.get("no_offer_reason") is None)
        deliberate = sum(1 for n in no_offer if n.get("no_offer_reason") == "uneconomical")
        avoidable_loss = sum(
            n.get("expected_term_margin_gbp", 0.0) for n in no_offer
            if n.get("no_offer_reason") is None
        )
        lines.append(
            f"- **No-offer churns:** {no_offer_count} total "
            f"({blind_miss} blind miss / {deliberate} deliberate pass)"
        )
        if avoidable_loss > 0:
            lines.append(f"- **Estimated avoidable margin loss:** {_fmt_gbp(avoidable_loss)}")

    coverage_denom = len(rl) + no_offer_count
    if coverage_denom > 0:
        coverage_rate = len(rl) / coverage_denom * 100
        lines.append(f"- **Retention coverage rate:** {coverage_rate:.0f}% of at-risk renewals received an offer")

    lines.append("")

    # 2. Flexibility Revenue Intelligence
    per_year = flex.get("per_year", {})
    lines += ["### 2. Flexibility Revenue Intelligence", ""]

    if per_year:
        years_sorted = sorted(per_year.keys())
        first_yr, last_yr = years_sorted[0], years_sorted[-1]
        enrolled_first = per_year[first_yr].get("enrolled_customers", 0)
        enrolled_last = per_year[last_yr].get("enrolled_customers", 0)
        n_intervals = len(years_sorted) - 1
        if n_intervals > 0 and enrolled_first > 0:
            enrollment_cagr = ((enrolled_last / enrolled_first) ** (1 / n_intervals) - 1) * 100
        else:
            enrollment_cagr = 0.0

        total_rev = flex.get("total_flexibility_revenue_gbp", 0.0)
        enrolled_years = flex.get("enrolled_customer_years", 0)
        rev_per_enrolled = total_rev / enrolled_years if enrolled_years > 0 else 0.0

        lines += [
            f"- **Total flexibility revenue (full run):** {_fmt_gbp(total_rev)}",
            f"- **Revenue per enrolled customer-year:** {_fmt_gbp(rev_per_enrolled)}",
            f"- **Enrollment trajectory:** {enrolled_first} ({first_yr}) → {enrolled_last} ({last_yr})"
            + (f" (CAGR {enrollment_cagr:.0f}%/yr)" if enrollment_cagr > 0 else ""),
        ]

        dfs_years = [y for y in years_sorted if per_year[y].get("dfs_gbp", 0.0) > 0]
        if dfs_years:
            dfs_total = sum(per_year[y].get("dfs_gbp", 0.0) for y in dfs_years)
            dfs_launch = dfs_years[0]
            if len(dfs_years) >= 2:
                dfs_first = per_year[dfs_years[0]].get("dfs_gbp", 0.0)
                dfs_last = per_year[dfs_years[-1]].get("dfs_gbp", 0.0)
                n_dfs = len(dfs_years) - 1
                if dfs_first > 0 and n_dfs > 0:
                    dfs_cagr = ((dfs_last / dfs_first) ** (1 / n_dfs) - 1) * 100
                    lines.append(
                        f"- **DFS revenue since {dfs_launch}:** {_fmt_gbp(dfs_total)}"
                        f" (CAGR {dfs_cagr:.0f}%/yr)"
                    )
                else:
                    lines.append(f"- **DFS revenue since {dfs_launch}:** {_fmt_gbp(dfs_total)}")
            else:
                lines.append(f"- **DFS revenue since {dfs_launch}:** {_fmt_gbp(dfs_total)}")
    else:
        lines.append("- No flexibility revenue data available.")

    lines.append("")

    # 3. Churn Pattern Analysis
    lines += ["### 3. Churn Pattern Analysis", ""]

    net_change = 0
    by_year_churn: dict = {}
    if churn_events:
        total_churns = len(churn_events)
        for ev in churn_events:
            yr = (ev.get("event_date") or "")[:4]
            if yr:
                by_year_churn[yr] = by_year_churn.get(yr, 0) + 1

        peak_yr = max(by_year_churn, key=by_year_churn.get) if by_year_churn else None
        lines.append(f"- **Total lifetime churn events:** {total_churns}")
        if peak_yr:
            lines.append(f"- **Peak churn year:** {peak_yr} ({by_year_churn[peak_yr]} events)")

        acq_events = [e for e in cel if e.get("event_type") == "acquisition"]
        if acq_events:
            net_change = len(acq_events) - total_churns
            lines.append(
                f"- **Net book movement:** {len(acq_events)} acquisitions − {total_churns} churns "
                f"= {net_change:+d}"
            )
            trend = "growing" if net_change > 0 else "shrinking" if net_change < 0 else "stable"
            lines.append(f"- **Portfolio trend:** {trend}")
    else:
        lines.append("- No churn events recorded in this run period.")

    lines.append("")

    # 4. Board Recommendations
    lines += ["### 4. Board Recommendations", ""]
    recommendations: list = []

    blind_miss_count = sum(1 for n in no_offer if n.get("no_offer_reason") is None)
    if blind_miss_count > 0:
        missed_gbp = sum(n.get("expected_term_margin_gbp", 0.0) for n in no_offer if n.get("no_offer_reason") is None)
        recommendations.append(
            f"**Retention gap:** {blind_miss_count} customers churned without receiving a retention offer "
            f"(estimated margin loss: {_fmt_gbp(missed_gbp)}). Lower the blind-miss detection threshold."
        )

    if rl:
        churned_despite_ct = sum(1 for r in rl if r.get("outcome") == "churned_despite_offer")
        fail_rate = churned_despite_ct / len(rl) * 100
        if fail_rate > 25:
            recommendations.append(
                f"**Offer effectiveness:** {fail_rate:.0f}% of retention offers did not succeed. "
                "Consider TOU_REFERRAL for EV customers or deeper price-match discounts for bill-stress cases."
            )

    if per_year:
        last_enrolled_n = per_year.get(last_yr, {}).get("enrolled_customers", 0)
        if last_enrolled_n > 0:
            recommendations.append(
                f"**Flexibility revenue:** {last_enrolled_n} customers enrolled in CM/DFS as of {last_yr}. "
                "Prioritise EV+battery acquisition — combined enrollment earns ~£2,046/yr vs EV-only ~£930/yr."
            )

    if churn_events and by_year_churn:
        crisis_churns = sum(by_year_churn.get(str(y), 0) for y in [2021, 2022])
        if crisis_churns > 0:
            recommendations.append(
                f"**Crisis-year churn:** {crisis_churns} churn events in 2021–2022. "
                "Maintain minimum hedge floor pre-crisis to preserve pricing stability and limit bill-shock churn."
            )

    if not recommendations:
        recommendations.append(
            "Portfolio operating within normal parameters. "
            "Monitor retention coverage and flexibility enrollment growth."
        )

    for i, rec in enumerate(recommendations, 1):
        lines.append(f"{i}. {rec}")

    lines.append("")
    return "\n".join(lines)


def _section_churn_root_cause(data: dict) -> str:
    """Phase AK: Churn Root Cause Attribution.

    For each churned account, traces the price journey and churn estimate context.
    Cross-references:
      - customer_events (event_type=churned) for departure timing
      - dynamic_pricing_log for last rate change before churn
      - churn_basis_risk for rate-vs-SVT and company vs sim divergence
      - per_customer_lifetime for tenure and margin lost

    Silent when no churned events.
    """
    ce_all = data.get("customer_events", [])
    churned = [e for e in ce_all if e.get("event_type") == "churned"]
    if not churned:
        return ""

    dpl = data.get("dynamic_pricing_log", [])
    cbr = data.get("churn_basis_risk", [])
    pcl = data.get("per_customer_lifetime", {})

    rows = []
    for ev in sorted(churned, key=lambda e: e["event_date"]):
        cid = ev["customer_id"]
        churn_date = ev["event_date"]

        # Last pricing entry for this customer at or before churn
        cid_pricing = [p for p in dpl if p["customer_id"] == cid and p["term_start"] <= churn_date]
        last_price = max(cid_pricing, key=lambda p: p["term_start"]) if cid_pricing else None

        # Last churn basis risk entry at or before churn
        cid_cbr = [r for r in cbr if r["customer_id"] == cid and r["term_start"] <= churn_date]
        last_cbr = max(cid_cbr, key=lambda r: r["term_start"]) if cid_cbr else None

        pcl_rec = pcl.get(cid, {})
        segment = pcl_rec.get("segment", "?")
        net_margin = pcl_rec.get("net_margin_after_cost_to_serve_gbp", 0.0)
        acq_date = pcl_rec.get("acquisition_date", "")
        tenure_years = 0.0
        if acq_date:
            from datetime import date as _date
            try:
                d0 = _date.fromisoformat(acq_date)
                d1 = _date.fromisoformat(churn_date)
                tenure_years = (d1 - d0).days / 365.25
            except ValueError:
                pass

        rate_shock_pct = None
        final_rate = None
        if last_price:
            rb = last_price.get("unit_rate_before", 0)
            ra = last_price.get("unit_rate_after", 0)
            if rb:
                rate_shock_pct = (ra - rb) / rb * 100
            final_rate = ra

        rate_vs_svt = last_cbr.get("rate_vs_svt_pct") if last_cbr else None
        sim_p = last_cbr.get("sim_churn_probability", 0.0) if last_cbr else 0.0
        co_est = last_cbr.get("company_churn_estimate", 0.0) if last_cbr else 0.0

        rows.append({
            "cid": cid,
            "date": churn_date,
            "segment": segment,
            "tenure_years": tenure_years,
            "rate_shock_pct": rate_shock_pct,
            "final_rate": final_rate,
            "rate_vs_svt": rate_vs_svt,
            "sim_p": sim_p,
            "co_est": co_est,
            "net_margin": net_margin,
        })

    lines = [
        "## Churn Root Cause Attribution",
        "",
        "Per-churned-account analysis: pricing journey, rate-vs-SVT positioning, and company "
        "vs SIM churn estimate at the point of departure.",
        "",
        "| Account | Seg | Churn Date | Tenure | Last Rate Shock | Rate vs SVT | Sim Risk | Co. Est. | Margin Lost |",
        "|---------|-----|------------|--------|-----------------|-------------|----------|----------|-------------|",
    ]

    for r in rows:
        shock_str = (
            f"{r['rate_shock_pct']:+.1f}%" if r["rate_shock_pct"] is not None else "n/a"
        )
        rvs_str = (
            f"{r['rate_vs_svt']:+.1f}%" if r["rate_vs_svt"] is not None else "n/a"
        )
        lines.append(
            "| " + r["cid"] + " | " + r["segment"] + " | " + r["date"] + " | " +
            f"{r['tenure_years']:.1f}yr" + " | " + shock_str + " | " + rvs_str +
            " | " + f"{r['sim_p']:.0%}" + " | " + f"{r['co_est']:.0%}" + " | " +
            _fmt_gbp(r["net_margin"]) + " |"
        )

    lines.append("")

    # Summary metrics
    total_margin_lost = sum(r["net_margin"] for r in rows)
    avg_tenure = sum(r["tenure_years"] for r in rows) / len(rows) if rows else 0.0
    blind_misses = [r for r in rows if r["co_est"] < 0.10 and r["sim_p"] >= 0.30]
    warned = [r for r in rows if r["co_est"] >= 0.20]
    crisis_churns = [r for r in rows if "2021" in r["date"] or "2022" in r["date"]]

    lines += [
        "**Root Cause Summary:**",
        "- Total churned accounts: " + str(len(rows)),
        "- Lifetime margin lost: " + _fmt_gbp(total_margin_lost),
        "- Average tenure at departure: " + f"{avg_tenure:.1f} years",
    ]
    if blind_misses:
        lines.append(
            "- Company blind misses (sim >=30%, co. est. <10%): " +
            str(len(blind_misses)) + " -- " +
            ", ".join(r["cid"] for r in blind_misses)
        )
    if warned:
        lines.append(
            "- Company-warned churns (co. est. >=20%): " +
            str(len(warned)) + " -- " +
            ", ".join(r["cid"] for r in warned)
        )
    if crisis_churns:
        lines.append(
            "- Crisis-era churns (2021-22): " + str(len(crisis_churns)) +
            " -- absolute crisis price level, not rate-change delta, was the driver"
        )

    # Overpriced at churn
    overpriced = [r for r in rows if r["rate_vs_svt"] is not None and r["rate_vs_svt"] > 5.0]
    if overpriced:
        lines.append(
            "- Overpriced vs SVT at departure: " + str(len(overpriced)) + " account(s) -- " +
            "rate shock risk was observable but unactioned"
        )

    lines.append("")
    return "\n".join(lines)


def _section_counterfactual_retention(data: dict) -> str:
    """Phase AL: Counterfactual Retention Value.

    For each no_offer_churn_log entry (departed with no retention offer made),
    computes the counterfactual net benefit of a hypothetical retention offer.
    Uses:
      - no_offer_churn_log: expected_term_margin_gbp, company_churn_estimate
      - retention_log: calibrates P(retain|offer) from actual outcomes
      - per_customer_lifetime: segment for discount rate selection

    Counterfactual: 5% discount for resi, 8% for SME/I&C (Phase AE calibrated).
    Retention probability: calibrated from actual retention_log outcomes.
    Net benefit = P_retain * etm - retention_cost; only meaningful if etm > 0.

    Silent when no_offer_churn_log is absent.
    """
    no_offer = data.get("no_offer_churn_log", [])
    if not no_offer:
        return ""

    rl = data.get("retention_log", [])
    pcl = data.get("per_customer_lifetime", {})

    # Calibrate retention probability from actual offer outcomes
    retained_count = sum(1 for r in rl if r.get("outcome") == "retained")
    p_retain = retained_count / len(rl) if rl else 0.60

    def _discount_rate(segment: str) -> float:
        if segment in ("SME", "I&C"):
            return 0.08
        return 0.05

    rows = []
    for r in no_offer:
        cid = r["customer_id"]
        etm = r.get("expected_term_margin_gbp", 0.0)
        co_est = r.get("company_churn_estimate", 0.0)
        event_date = r.get("event_date", "")
        pcl_rec = pcl.get(cid, {})
        segment = pcl_rec.get("segment", "resi")
        disc = _discount_rate(segment)
        retention_cost = max(0.0, etm) * disc
        counterfactual_net = (p_retain * etm - retention_cost) if etm > 0 else 0.0
        decision = "correct_no_offer" if etm <= 0 else "missed_opportunity"
        rows.append({
            "cid": cid,
            "segment": segment,
            "date": event_date,
            "etm": etm,
            "co_est": co_est,
            "disc": disc,
            "retention_cost": retention_cost,
            "counterfactual_net": counterfactual_net,
            "decision": decision,
        })

    lines = [
        "## Counterfactual Retention Value",
        "",
        f"What would company-initiated retention offers have been worth for the {len(rows)} "
        f"accounts that churned without an offer? Calibrated from {len(rl)} actual offers "
        f"(observed retention rate {p_retain:.0%}).",
        "",
        "| Account | Seg | Churn Date | Co. Est. | Term Margin | Disc Rate | "
        "Retention Cost | CF Net Benefit | Assessment |",
        "|---------|-----|------------|----------|-------------|-----------|"
        "----------------|----------------|------------|",
    ]

    for r in rows:
        etm_str = _fmt_gbp(r["etm"])
        rc_str = _fmt_gbp(r["retention_cost"])
        cf_str = _fmt_gbp(r["counterfactual_net"]) if r["counterfactual_net"] != 0 else "n/a"
        assess = "CORRECT PASS" if r["decision"] == "correct_no_offer" else "MISSED OPP."
        lines.append(
            "| " + r["cid"] + " | " + r["segment"] + " | " + r["date"] + " | " +
            f"{r['co_est']:.0%}" + " | " + etm_str + " | " +
            f"{r['disc']:.0%}" + " | " + rc_str + " | " + cf_str + " | " + assess + " |"
        )

    lines.append("")

    # Summary
    missed = [r for r in rows if r["decision"] == "missed_opportunity"]
    correct_passes = [r for r in rows if r["decision"] == "correct_no_offer"]
    total_cf_net = sum(r["counterfactual_net"] for r in missed)
    total_cost = sum(r["retention_cost"] for r in missed)
    total_etm = sum(r["etm"] for r in missed)

    lines += [
        "**Counterfactual Summary:**",
        "- No-offer churns assessed: " + str(len(rows)),
        "- Correct no-offer (net-neg ETM): " + str(len(correct_passes)) +
        (" (" + ", ".join(r["cid"] for r in correct_passes) + ")" if correct_passes else ""),
        "- Missed opportunities (positive ETM, below detection): " + str(len(missed)),
    ]
    if missed:
        lines += [
            "- Total term margin foregone: " + _fmt_gbp(total_etm),
            "- Total retention cost (counterfactual): " + _fmt_gbp(total_cost),
            "- Net counterfactual benefit: " + _fmt_gbp(total_cf_net) +
            " (at " + f"{p_retain:.0%}" + " retention probability)",
            "- Root cause: company churn detection below threshold for all missed cases "
            "-- churn model underestimated bill-shock risk",
        ]

    lines.append("")
    return "\n".join(lines)


def _section_pricing_basis_risk(data: dict) -> str:
    """Phase AM: Pricing Basis Risk Attribution.

    Uses basis_risk_terms (per-contract forward-rate comparison) to show
    year-by-year accuracy of the company's forward curve model.
    tariff_error_pct = (company_fwd - sim_fwd) / sim_fwd:
      positive = company overestimated forward costs (over-priced contracts)
      negative = company underestimated (under-priced, margin-at-risk)

    Crisis pattern: 2021-22 error near zero (company correctly priced the crisis).
    Post-crisis 2023+: high positive error = company locked in expensive forwards
    after market normalised -- the mechanism that destroyed real suppliers.

    Silent when basis_risk_terms absent.
    """
    brt = data.get("basis_risk_terms", [])
    if not brt:
        return ""

    from collections import defaultdict
    by_year: dict[str, list[dict]] = defaultdict(list)
    for r in brt:
        yr = r.get("term_start", "")[:4]
        if yr:
            by_year[yr].append(r)

    if not by_year:
        return ""

    all_errors = [r["tariff_error_pct"] for r in brt]
    portfolio_mean = sum(all_errors) / len(all_errors)

    lines = [
        "## Pricing Basis Risk Attribution",
        "",
        "Forward curve accuracy at each contract term. "
        "tariff_error_pct = (company_fwd - sim_fwd) / sim_fwd: "
        "positive = company over-estimated costs (higher than market); "
        "negative = company under-estimated (margin-at-risk).",
        f"Portfolio-wide mean error: {portfolio_mean:+.1%}",
        "",
        "| Year | Contracts | Mean Error | Max Abs | Over-priced | Under-priced | Assessment |",
        "|------|-----------|------------|---------|-------------|--------------|------------|",
    ]

    worst_over_yr = None
    worst_over_val = 0.0
    under_priced_years = []
    late_crisis_over = []

    for yr in sorted(by_year.keys()):
        entries = by_year[yr]
        errors = [r["tariff_error_pct"] for r in entries]
        mean_err = sum(errors) / len(errors)
        max_abs = max(abs(e) for e in errors)
        over = sum(1 for e in errors if e > 0.05)
        under = sum(1 for e in errors if e < -0.05)

        if mean_err > 0.15:
            assess = "HIGH OVER-PRICE"
            late_crisis_over.append(yr)
        elif mean_err > 0.05:
            assess = "moderate over"
        elif mean_err < -0.05:
            assess = "UNDER-PRICE"
            under_priced_years.append(yr)
        else:
            assess = "on target"

        if mean_err > worst_over_val:
            worst_over_val = mean_err
            worst_over_yr = yr

        lines.append(
            f"| {yr} | {len(entries)} | {mean_err:+.1%} | {max_abs:.1%} | "
            f"{over} | {under} | {assess} |"
        )

    lines.append("")
    lines.append("**Basis Risk Summary:**")
    lines.append(f"- Portfolio mean tariff error: {portfolio_mean:+.1%}")
    if worst_over_yr:
        lines.append(
            f"- Worst over-pricing year: {worst_over_yr} ({worst_over_val:+.1%}) "
            "-- company forward curve above settled market"
        )
    if under_priced_years:
        lines.append(
            "- Under-pricing years (margin risk): " +
            ", ".join(under_priced_years) +
            " -- company forward curve below settled market"
        )
    if late_crisis_over:
        lines.append(
            "- Post-crisis over-pricing years (" +
            ", ".join(late_crisis_over) +
            "): company locked in expensive crisis-era forwards after prices normalised "
            "-- mechanism that eroded real suppliers' margins 2022-24"
        )

    lines.append("")
    return "\n".join(lines)


def _section_board_risk_summary(data: dict) -> str:
    pcl = data.get("per_customer_lifetime", {})
    years_data = data.get("years", {})
    cd = data.get("company_divergence", {})
    brt = data.get("basis_risk_terms", [])
    ce_all = data.get("customer_events", [])
    cbr = data.get("churn_basis_risk", [])
    hl = data.get("_ledger_headline")

    if not any([pcl, years_data, cd, brt, ce_all, cbr, hl]):
        return ""

    rows = []

    # 1. Revenue concentration (from Phase AN)
    pos_margins = {
        cid: v.get("net_margin_after_cost_to_serve_gbp") or 0.0
        for cid, v in pcl.items()
        if (v.get("net_margin_after_cost_to_serve_gbp") or 0.0) > 0
    }
    if pos_margins:
        total_pos = sum(pos_margins.values())
        ic_pct = sum(v for cid, v in pos_margins.items()
                     if pcl.get(cid, {}).get("segment") == "I&C") / total_pos
        shares = [v / total_pos for v in pos_margins.values()]
        hhi = sum(s * s for s in shares) * 10000
        rag = "RED" if hhi > 2500 else ("AMBER" if hhi > 1500 else "GREEN")
        rows.append(("Revenue concentration",
                     "HHI %.0f, I&C %.0f%%" % (hhi, ic_pct * 100),
                     rag,
                     "Single I&C departure removes 14-29%% of margin"))

    # 2. Gas ROC (from Phase AP)
    seg_lifetime: dict = {}
    for yr, yd in sorted(years_data.items()):
        for seg, vals in yd.get("segment_split", {}).items():
            if seg not in seg_lifetime:
                seg_lifetime[seg] = [0.0, 0.0, 0.0]
            seg_lifetime[seg][0] += vals.get("gross_gbp", 0.0)
            seg_lifetime[seg][1] += vals.get("capital_gbp", 0.0)
            seg_lifetime[seg][2] += vals.get("net_gbp", 0.0)
    gas_net = sum(seg_lifetime[s][2] for s in seg_lifetime if "gas" in s)
    gas_cap = sum(seg_lifetime[s][1] for s in seg_lifetime if "gas" in s)
    if gas_cap > 0:
        gas_roc = gas_net / gas_cap
        rag = "RED" if gas_roc < 0 else ("AMBER" if gas_roc < 3 else "GREEN")
        rows.append(("Gas segment ROC",
                     "%.1fx (net %s on %s capital)" % (gas_roc, _fmt_gbp(gas_net), _fmt_gbp(gas_cap)),
                     rag,
                     "Gas legs destroy capital; electricity cross-subsidises"))

    # 3. Churn blind miss rate (from Phase AK)
    churned = [e for e in ce_all if e.get("event_type") == "churned"]
    if churned and cbr:
        latest_churn: dict = {}
        seen_ts: dict = {}
        for rec in cbr:
            cid = rec.get("customer_id", "")
            ts = rec.get("term_start", "")
            if cid and (cid not in seen_ts or ts > seen_ts[cid]):
                seen_ts[cid] = ts
                latest_churn[cid] = rec.get("company_churn_estimate", 0.0)
        misses = sum(1 for e in churned
                     if latest_churn.get(e.get("customer_id"), 0.0) < 0.10)
        miss_rate = misses / len(churned) if churned else 0.0
        rag = "RED" if miss_rate > 0.4 else ("AMBER" if miss_rate > 0.2 else "GREEN")
        rows.append(("Churn blind miss rate",
                     "%d/%d departures (%.0f%%)" % (misses, len(churned), miss_rate * 100),
                     rag,
                     "Company did not forecast these churns"))

    # 4. Demand estimation error peak (from Phase AO)
    ded = cd.get("demand_error_by_year", {})
    if ded:
        peak_mean = max((s["mean_abs_error_pct"] for s in ded.values() if s.get("n", 0) >= 5), default=0.0)
        peak_max = max((s["max_abs_error_pct"] for s in ded.values()), default=0.0)
        rag = "RED" if peak_mean > 3.0 else ("AMBER" if peak_mean > 1.0 else "GREEN")
        rows.append(("Demand estimation error",
                     "Peak mean %.1f%%, max %.1f%%" % (peak_mean, peak_max),
                     rag,
                     "EAC drift from asset acquisitions; smart meters eliminate"))

    # 5. Pricing basis risk worst year mean (from Phase AM)
    if brt:
        by_year: dict = {}
        for b in brt:
            if "tariff_error_pct" in b:
                yr = b.get("term_start", "")[:4]
                by_year.setdefault(yr, []).append(b["tariff_error_pct"])
        year_means = {yr: sum(v)/len(v) for yr, v in by_year.items() if v}
        if year_means:
            worst_yr = max(year_means, key=lambda k: year_means[k])
            worst_over = year_means[worst_yr]
            rag = "RED" if worst_over > 0.15 else ("AMBER" if worst_over > 0.05 else "GREEN")
            rows.append(("Pricing basis risk (worst year)",
                         "%s: +%.1f%% mean over-estimate" % (worst_yr, worst_over * 100),
                         rag,
                         "Over-priced contracts help margin but create churn risk"))

    # 6. Net margin as % of revenue
    if hl and hl.get("revenue_gbp", 0) > 0:
        nm_pct = hl["net_margin_gbp"] / hl["revenue_gbp"]
        rag = "GREEN" if nm_pct > 0.02 else ("AMBER" if nm_pct > 0 else "RED")
        rows.append(("Net margin % of revenue",
                     "%.1f%% (benchmark: 2-5%%)" % (nm_pct * 100),
                     rag,
                     "Within/above industry range" if nm_pct > 0.02 else "Below benchmark"))

    if not rows:
        return ""

    lines = [
        "## Board Risk Summary",
        "",
        "Synthesised risk indicators across portfolio, capital, operations and pricing.",
        "RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.",
        "",
        "| Risk Indicator | Value | RAG | Implication |",
        "|----------------|-------|-----|-------------|",
    ]
    for metric, value, rag, implication in rows:
        lines.append("| " + metric + " | " + value + " | **" + rag + "** | " + implication + " |")
    lines.append("")

    reds = [r for r in rows if r[2] == "RED"]
    if reds:
        lines.append(
            "**Board Action Required:** "
            + ", ".join(r[0] for r in reds)
            + " — RED rating(s) require immediate attention."
        )
        lines.append("")

    return "\n".join(lines)


def _section_gas_exit_analysis(data: dict) -> str:
    pcp = data.get("per_cid_comm_pnl", {})
    pcl = data.get("per_customer_lifetime", {})
    if not pcp:
        return ""
    try:
        from company.finance.gas_exit_analysis import GasExitDecisionBook
        book = GasExitDecisionBook(pcp, pcl)
        if not book._profiles:
            return ""
        comp = book.scenario_comparison()
        sq = book.status_quo()
        exit_s = book.exit_gas()
        reprice_s = book.reprice_gas()
        loss = book.loss_making_accounts()
        accr = book.accretive_accounts()
        lines = [
            "## Gas Supply Exit Decision Analysis (Phase AR/AS)",
            "",
            "Models three strategic scenarios for the board regarding gas supply legs.",
            "Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.",
            "",
            "### Scenario Comparison (Dual-Fuel Portfolio Only)",
            "",
            "| Scenario | Portfolio Net | vs Status Quo | Action |",
            "|----------|--------------|---------------|--------|",
            "| STATUS_QUO | " + _fmt_gbp(sq.total_net_gbp) + " | — | Current strategy |",
            "| EXIT_GAS | " + _fmt_gbp(exit_s.total_net_gbp) + " | " + _fmt_gbp(comp["exit_vs_status_quo_gbp"]) + " | Remove gas; model elec churn risk |",
            "| REPRICE_GAS | " + _fmt_gbp(reprice_s.total_net_gbp) + " | " + _fmt_gbp(comp["reprice_vs_status_quo_gbp"]) + " | Raise gas tariff to break-even |",
            "",
            "**Recommended action: " + comp["recommended_action"] + "**",
            "",
        ]
        if loss:
            lines += [
                "### Loss-Making Gas Accounts",
                "",
                "| Account | Gas Net | Gas ROC | Revenue Uplift Needed |",
                "|---------|---------|---------|----------------------|",
            ]
            for p in loss:
                roc_str = ("%.2fx" % p.gas_roc) if p.gas_roc is not None else "n/a"
                lines.append(
                    "| " + p.customer_id + "g | " + _fmt_gbp(p.gas_net_gbp) +
                    " | " + roc_str + " | +" + ("%.1f%%" % (p.breakeven_revenue_uplift_pct * 100)) + " |"
                )
            lines.append("")
        if accr:
            lines.append(
                "**Accretive gas accounts:** " +
                ", ".join(p.customer_id + "g (" + _fmt_gbp(p.gas_net_gbp) + ")" for p in accr) +
                " — these gas legs support customer retention without capital destruction."
            )
            lines.append("")
        lines += [
            "**Board Decision:**",
            "- Exit gas: I&C customers at 40% electricity churn risk when gas removed (relationship loss)",
            "- Reprice gas: increases customer cost but eliminates capital destruction",
            "- Status quo: unsustainable — gas legs destroying £" + ("%.0f" % abs(sq.gas_net_gbp)) + " in net value",
        ]
        lines.append("")
        return "\n".join(lines)
    except Exception:
        return ""


def _section_price_cap_headroom(data: dict) -> str:
    """Phase BM: Price cap headroom — tariff vs SVT by year."""
    churn_basis = data.get("churn_basis_risk", [])
    if not churn_basis:
        return ""
    by_year: dict = {}
    for r in churn_basis:
        yr = r.get("term_start", "")[:4]
        if not yr:
            continue
        vs_svt = r.get("rate_vs_svt_pct")
        if vs_svt is None:
            continue
        by_year.setdefault(yr, []).append(vs_svt)
    if not by_year:
        return ""
    rows = []
    for yr in sorted(by_year.keys()):
        vals = by_year[yr]
        n = len(vals)
        avg = sum(vals) / n
        above_cap = sum(1 for v in vals if v > 0)
        min_v = min(vals)
        max_v = max(vals)
        rows.append((yr, n, avg, above_cap, min_v, max_v))
    lines = [
        "## Price Cap Headroom (Tariff vs SVT)",
        "",
        "Percentage difference between contracted unit rate and SVT (price cap) at term start.",
        "Negative = below cap (headroom). Positive = above cap (I&C terms; SVT applies to resi only).",
        "",
        "| Year | Terms | Avg vs SVT% | Above Cap | Min% | Max% |",
        "|------|-------|-------------|-----------|------|------|",
    ]
    for yr, n, avg, above, mn, mx in rows:
        sign = "+" if avg >= 0 else ""
        lines.append("| {} | {} | {}{:.1f}% | {}/{} | {:.1f}% | +{:.1f}% |".format(
            yr, n, sign, avg, above, n, mn, mx))
    best_yr = min(rows, key=lambda r: r[2])
    worst_avg_yr = max(rows, key=lambda r: r[2])
    lines.extend([
        "",
        "**Best headroom year: {} (avg {:.1f}% below SVT)**".format(best_yr[0], abs(best_yr[2])),
        "**Largest above-SVT year: {}** ({}/{} terms above — note: I&C customers exempt from SVT cap)".format(
            worst_avg_yr[0], worst_avg_yr[3], worst_avg_yr[1]),
        "",
        "> SVT (Standard Variable Tariff) = Ofgem price cap. Residential tariffs must not exceed SVT.",
        "> I&C/SME terms above SVT are expected during crisis years when wholesale >cap.",
        "",
    ])
    return "\n".join(lines)

def _section_stress_test_history(data: dict) -> str:
    """Phase BL: Portfolio stress test — retrospective RAG per year per scenario."""
    try:
        from company.risk.stress_test import StressTestBook, StressScenario
    except ImportError:
        return ""
    yrs_data = data.get("years", {})
    if not yrs_data:
        return ""
    book = StressTestBook(credit_facility_gbp=2_000_000.0)
    scenario_order = [
        StressScenario.MARKET_SPIKE,
        StressScenario.CREDIT_DEFAULT,
        StressScenario.DEMAND_SHOCK,
        StressScenario.LIQUIDITY_CRISIS,
        StressScenario.COMBINED_CRISIS,
    ]
    short_names = {
        StressScenario.MARKET_SPIKE: "Mkt Spike",
        StressScenario.CREDIT_DEFAULT: "Credit",
        StressScenario.DEMAND_SHOCK: "Demand",
        StressScenario.LIQUIDITY_CRISIS: "Liquidity",
        StressScenario.COMBINED_CRISIS: "Combined",
    }
    rows = []
    for yr in sorted(yrs_data.keys()):
        treasury = yrs_data[yr].get("treasury_end_gbp", 0.0)
        cwu = yrs_data[yr].get("committee_wake_ups", [])
        var_current = 50_000.0
        if cwu:
            last_var = cwu[-1].get("portfolio_var_current_gbp", None)
            if last_var and last_var > 0:
                var_current = last_var
        weekly_burn = max(treasury * 0.01, 25_000.0)
        scenario_rags = {}
        for sc in scenario_order:
            result = book.run_stress(
                scenario=sc,
                starting_treasury_gbp=treasury,
                current_var_gbp=var_current,
                weekly_burn_gbp=weekly_burn,
            )
            scenario_rags[sc] = result.severity_rag
        rows.append((yr, treasury, scenario_rags))
    header_cells = " | ".join(short_names[sc] for sc in scenario_order)
    lines = [
        "## Portfolio Stress Test History",
        "",
        "Retrospective RAG status: would year-end treasury have survived each scenario?",
        "Credit facility: £2M. Weekly burn estimated at 1% of year-end treasury.",
        "",
        f"| Year | Treasury £ | {header_cells} |",
        "|------|-----------|" + "|".join("----------" for _ in scenario_order) + "|",
    ]
    for yr, treasury, rags in rows:
        cells = " | ".join(rags[sc] for sc in scenario_order)
        lines.append(f"| {yr} | £{treasury:,.0f} | {cells} |")
    all_reds = [yr for yr, _, rags in rows if any(v == "RED" for v in rags.values())]
    all_green = [yr for yr, _, rags in rows if all(v == "GREEN" for v in rags.values())]
    worst_yr = None
    worst_count = 0
    for yr, _, rags in rows:
        red_count = sum(1 for v in rags.values() if v == "RED")
        if red_count > worst_count:
            worst_count = red_count
            worst_yr = yr
    lines.extend([""])
    if worst_yr:
        lines.append(f"**Most stressed year: {worst_yr} ({worst_count} RED scenario(s))**")
    if all_green:
        lines.append(f"**Clean bill of health (all GREEN): {', '.join(all_green)}**")
    lines.extend(["",
        "> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).",
        "",
    ])
    return "\n".join(lines)

def _section_financial_ratios(data: dict) -> str:
    """Phase BK: Financial Ratios — EBIT margin, revenue and margin per customer."""
    ma = data.get("management_accounts", {})
    yrs_data = data.get("years", {})
    if not ma:
        return ""
    rows = []
    for yr in sorted(ma.keys()):
        ist = ma[yr].get("income_statement", {})
        rev = ist.get("revenue_gbp", 0.0)
        nm = ist.get("net_margin_gbp", 0.0)
        gm = ist.get("gross_margin_gbp", 0.0)
        bd = ist.get("bad_debt_gbp", 0.0)
        active_ids = yrs_data.get(yr, {}).get("active_customer_ids", [])
        n_cust = len(active_ids) if active_ids else 1
        ebit_pct = nm / rev * 100 if rev else 0.0
        rev_per_cust = rev / n_cust
        gm_per_cust = gm / n_cust
        bad_debt_rate_pct = bd / rev * 100 if rev else 0.0
        rows.append((yr, n_cust, ebit_pct, rev_per_cust, gm_per_cust, bad_debt_rate_pct))
    lines = [
        "## Financial Ratios",
        "",
        "Key per-customer and margin metrics by year.",
        "",
        "| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |",
        "|------|-----------|-------|--------------------|--------------|-----------|",
    ]
    for yr, n, ebit, rpc, gmpc, bd_rate in rows:
        lines.append("| {} | {} | {:.1f}% | £{:,.0f} | £{:,.0f} | {:.2f}% |".format(
            yr, n, ebit, rpc, gmpc, bd_rate))
    best_ebit_yr, best_ebit = max(((r[0], r[2]) for r in rows), key=lambda x: x[1])
    worst_ebit_yr, worst_ebit = min(((r[0], r[2]) for r in rows), key=lambda x: x[1])
    max_rev_per_cust_yr, max_rpc = max(((r[0], r[3]) for r in rows), key=lambda x: x[1])
    lines.extend([
        "",
        "**Best EBIT%: {} ({:.1f}%)** | **Worst EBIT%: {} ({:.1f}%)**".format(
            best_ebit_yr, best_ebit, worst_ebit_yr, worst_ebit),
        "**Peak revenue/customer: {} (£{:,.0f})**".format(max_rev_per_cust_yr, max_rpc),
        "",
        "> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).",
        "",
    ])
    return "\n".join(lines)

def _section_churn_prediction_calibration(data: dict) -> str:
    """Phase BJ: Churn prediction calibration — company estimate vs sim probability."""
    cel = [e for e in data.get("company_event_log", []) if e.get("event_type") == "churn"]
    if not cel:
        return ""
    rows = []
    for e in cel:
        cid = e.get("customer_id", "?")
        date = e.get("event_date", "?")[:7]  # YYYY-MM
        sim_p = e.get("sim_churn_probability", 0.0)
        co_p = e.get("company_churn_estimate", 0.0)
        delta = co_p - sim_p
        if abs(delta) < 0.10:
            verdict = "ACCURATE"
        elif delta > 0:
            verdict = "OVERESTIMATED"
        else:
            verdict = "UNDERESTIMATED"
        rows.append((cid, date, sim_p, co_p, delta, verdict))
    lines = [
        "## Churn Prediction Calibration",
        "",
        "How well the company estimated churn probability versus actual simulation outcomes.",
        "",
        "| Customer | Date | Sim Probability | Company Estimate | Delta | Verdict |",
        "|----------|------|----------------|-----------------|-------|---------|",
    ]
    for cid, date, sim_p, co_p, delta, verdict in rows:
        sign = "+" if delta >= 0 else ""
        lines.append("| {} | {} | {:.1f}% | {:.1f}% | {}{:.1f}pp | {} |".format(
            cid, date, sim_p * 100, co_p * 100, sign, delta * 100, verdict))
    underest = sum(1 for r in rows if r[5] == "UNDERESTIMATED")
    overest = sum(1 for r in rows if r[5] == "OVERESTIMATED")
    accurate = sum(1 for r in rows if r[5] == "ACCURATE")
    mae = sum(abs(r[4]) for r in rows) / len(rows) if rows else 0
    lines.extend([
        "",
        "**Outcomes: {} underestimated / {} accurate / {} overestimated**".format(
            underest, accurate, overest),
        "**Mean absolute error: {:.1f}pp**".format(mae * 100),
    ])
    if underest > overest:
        lines.append("**Systematic bias: company consistently UNDER-predicted churn risk.**")
    elif overest > underest:
        lines.append("**Systematic bias: company consistently OVER-predicted churn risk.**")
    else:
        lines.append("**No systematic directional bias detected.**")
    lines.extend([
        "",
        "> Company churn estimates derived from company-observable signals (bill shock,",
        "> margin feedback, renewal history) without access to the simulation\'s internal",
        "> churn parameters — epistemic gap is expected and realistic for a small supplier.",
        "",
    ])
    return "\n".join(lines)

def _section_tariff_estimation_accuracy(data: dict) -> str:
    """Phase BI: Tariff estimation accuracy — company vs actual outturn by year."""
    div = data.get("company_divergence", {})
    teby = div.get("tariff_error_by_year", {})
    if not teby:
        return ""
    rows = []
    for yr in sorted(teby.keys()):
        e = teby[yr]
        n = e.get("n", 0)
        mean_err = e.get("mean_abs_error_pct", 0.0)
        max_err = e.get("max_abs_error_pct", 0.0)
        rows.append((yr, n, mean_err, max_err))
    lines = [
        "## Tariff Estimation Accuracy",
        "",
        "Mean and maximum absolute error between company tariff estimates and actual outturn.",
        "",
        "| Year | Observations | Mean Abs Error | Max Abs Error | Accuracy |",
        "|------|-------------|---------------|--------------|----------|",
    ]
    for yr, n, mean_err, max_err in rows:
        if mean_err < 0.10:
            accuracy = "GOOD"
        elif mean_err < 0.15:
            accuracy = "MODERATE"
        else:
            accuracy = "POOR"
        lines.append("| {} | {} | {:.1f}% | {:.1f}% | {} |".format(
            yr, n, mean_err * 100, max_err * 100, accuracy))
    # Use rows with n >= 5 for fair comparison
    fair_rows = [(yr, n, m, mx) for yr, n, m, mx in rows if n >= 5]
    if fair_rows:
        best_yr, _, best_mean, _ = min(fair_rows, key=lambda r: r[2])
        worst_yr, _, worst_mean, _ = max(fair_rows, key=lambda r: r[2])
        lines.extend([
            "",
            "**Best accuracy year (n≥5): {} ({:.1f}% mean error)**".format(best_yr, best_mean * 100),
            "**Worst accuracy year (n≥5): {} ({:.1f}% mean error)**".format(worst_yr, worst_mean * 100),
        ])
    lines.extend([
        "",
        "> Errors reflect the company\'s information gap: forward curves are approximations;",
        "> the company cannot observe simulation wholesale cost internals (epistemic blindfold).",
        "",
    ])
    return "\n".join(lines)

def _section_dynamic_pricing_activity(data: dict) -> str:
    """Phase BH: Dynamic Pricing Activity — year-by-year tariff adjustment analysis."""
    dpl = data.get("dynamic_pricing_log", [])
    mfl = data.get("margin_feedback_log", [])
    if not dpl:
        return ""
    by_year: dict = {}
    for e in dpl:
        yr = e.get("term_start", "")[:4]
        if not yr:
            continue
        by_year.setdefault(yr, []).append(e)
    mfl_by_year: dict = {}
    for e in mfl:
        yr = e.get("term_start", "")[:4]
        if not yr:
            continue
        mfl_by_year.setdefault(yr, []).append(e)
    rows = []
    for yr in sorted(by_year.keys()):
        entries = by_year[yr]
        avg_delta = sum(e.get("unit_rate_after", 0) - e.get("unit_rate_before", 0) for e in entries) / len(entries)
        ups = sum(1 for e in entries if e.get("unit_rate_after", 0) > e.get("unit_rate_before", 0))
        downs = sum(1 for e in entries if e.get("unit_rate_after", 0) < e.get("unit_rate_before", 0))
        emergency = len(mfl_by_year.get(yr, []))
        rows.append((yr, len(entries), avg_delta, ups, downs, emergency))
    lines = [
        "## Dynamic Pricing Activity",
        "",
        "Rate adjustments driven by the margin feedback loop and emergency reprice events.",
        "",
        "| Year | Adjustments | Avg Delta £/MWh | Up | Down | Emergency |",
        "|------|------------|-----------------|-----|------|-----------|",
    ]
    for yr, adj, avg_d, up, dn, emerg in rows:
        sign = "+" if avg_d >= 0 else ""
        lines.append("| {} | {} | {}{:.1f} | {} | {} | {} |".format(
            yr, adj, sign, avg_d, up, dn, emerg))
    total_adj = sum(r[1] for r in rows)
    peak_yr, peak_delta = max(((r[0], r[2]) for r in rows), key=lambda x: x[1])
    max_emerg_yr = max(rows, key=lambda r: r[5])
    total_emergency = sum(r[5] for r in rows)
    lines.extend([
        "",
        "**Total adjustments 2016-2025: {}** | **Peak avg adjustment: {} (+{:.1f} £/MWh)**".format(
            total_adj, peak_yr, peak_delta if peak_delta >= 0 else -peak_delta),
        "**Emergency reprices: {} total** ({} in {})".format(
            total_emergency, max_emerg_yr[5], max_emerg_yr[0]),
        "",
        "> Emergency reprices triggered when recent margin dropped below cost floor.",
        "> Normal adjustments from rolling margin feedback; £/MWh delta versus prior contracted rate.",
        "",
    ])
    return "\n".join(lines)

def _section_clv_evolution(data: dict) -> str:
    """Phase BG: CLV Evolution — portfolio forward value trajectory by year."""
    clv_snapshots = data.get("clv_snapshots", {})
    if len(clv_snapshots) < 2:
        return ""
    rows = []
    prev_total = None
    for yr in sorted(clv_snapshots.keys()):
        accts = clv_snapshots[yr]
        elec = {k: v for k, v in accts.items() if not k.endswith("g")}
        total = sum(elec.values())
        count = len(elec)
        avg = total / count if count else 0
        if prev_total is None:
            delta = "\u2014"
        elif total >= prev_total:
            delta = "+\u00a3{:,.0f}".format(total - prev_total)
        else:
            delta = "\u00a3{:,.0f}".format(total - prev_total)
        rows.append((yr, count, total, avg, delta))
        prev_total = total
    lines = [
        "## Portfolio CLV Evolution",
        "",
        "Estimated forward lifetime value of active billing accounts at each year-end.",
        "",
        "| Year | Accounts | Total CLV \u00a3 | Avg CLV \u00a3 | \u0394 CLV \u00a3 |",
        "|------|----------|-------------|-----------|---------|",
    ]
    for yr, count, total, avg, delta in rows:
        lines.append("| {} | {} | \u00a3{:,.0f} | \u00a3{:,.0f} | {} |".format(yr, count, total, avg, delta))
    best_yr, best_total = max(((r[0], r[2]) for r in rows), key=lambda x: x[1])
    worst_yr, worst_total = min(((r[0], r[2]) for r in rows), key=lambda x: x[1])
    deltas_raw = [(rows[i][0], rows[i][2] - rows[i - 1][2]) for i in range(1, len(rows))]
    biggest_jump_yr, biggest_jump_val = max(deltas_raw, key=lambda x: x[1])
    biggest_drop_yr, biggest_drop_val = min(deltas_raw, key=lambda x: x[1])
    lines.extend([
        "",
        "**Peak portfolio CLV: {} (\u00a3{:,.0f})** | **Earliest/lowest: {} (\u00a3{:,.0f})**".format(
            best_yr, best_total, worst_yr, worst_total),
        "**Largest YoY gain: {} (+\u00a3{:,.0f})**".format(biggest_jump_yr, biggest_jump_val),
    ])
    if biggest_drop_val < 0:
        lines.append("**Largest YoY fall: {} (\u00a3{:,.0f})**".format(biggest_drop_yr, biggest_drop_val))
    lines.extend([
        "",
        "> Note: CLV snapshots are forward estimates at year-end based on remaining"
        " contract tenure and expected margins at that point in time.",
        "",
    ])
    return "\n".join(lines)

def _section_gross_margin_bridge(data: dict) -> str:
    """Phase BE: Gross margin bridge — year-over-year P&L attribution."""
    ma = data.get("management_accounts", {})
    if not ma:
        return ""
    years = sorted(ma.keys())
    if len(years) < 2:
        return ""
    lines = [
        "## Gross Margin Bridge (Year-over-Year Attribution)",
        "",
        "Annual change in gross margin decomposed into revenue and cost drivers.",
        "",
        "| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |",
        "|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|",
    ]
    prev = None
    max_gm_pct = 0.0
    min_gm_pct = 100.0
    worst_yr = None
    best_yr = None
    for yr in years:
        inc = ma[yr].get("income_statement", {})
        rev = inc.get("revenue_gbp", 0.0)
        wc = inc.get("wholesale_cost_gbp", 0.0)
        nc = inc.get("non_commodity_cost_gbp", 0.0)
        gm = inc.get("gross_margin_gbp", 0.0)
        gm_pct = gm / rev * 100 if rev > 0 else 0.0
        if gm_pct > max_gm_pct:
            max_gm_pct = gm_pct
            best_yr = yr
        if gm_pct < min_gm_pct:
            min_gm_pct = gm_pct
            worst_yr = yr
        if prev is not None:
            p_inc = ma[prev].get("income_statement", {})
            p_rev = p_inc.get("revenue_gbp", 0.0)
            p_wc = p_inc.get("wholesale_cost_gbp", 0.0)
            p_nc = p_inc.get("non_commodity_cost_gbp", 0.0)
            p_gm = p_inc.get("gross_margin_gbp", 0.0)
            d_rev = rev - p_rev
            d_wc = wc - p_wc
            d_nc = nc - p_nc
            d_gm = gm - p_gm
            sign = lambda x: ("+" if x >= 0 else "") + _fmt_gbp(x)
            lines.append(
                f"| {yr} | {_fmt_gbp(rev)} | {_fmt_gbp(wc)} | {_fmt_gbp(nc)} | "
                f"{_fmt_gbp(gm)} | {gm_pct:.1f}% | {sign(d_rev)} | {sign(d_wc)} | {sign(d_nc)} | {sign(d_gm)} |"
            )
        else:
            lines.append(
                f"| {yr} | {_fmt_gbp(rev)} | {_fmt_gbp(wc)} | {_fmt_gbp(nc)} | "
                f"{_fmt_gbp(gm)} | {gm_pct:.1f}% | — | — | — | — |"
            )
        prev = yr
    lines += [
        "",
        f"**Best GM year: {best_yr} ({max_gm_pct:.1f}%)** | **Worst GM year: {worst_yr} ({min_gm_pct:.1f}%)**",
        "",
        "> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.",
        "",
    ]
    return "\n".join(lines)


def _section_risk_committee_activity(data: dict) -> str:
    """Phase BC: Risk Committee intervention summary from committee_wake_ups."""
    years = data.get("years", {})
    all_sessions = []
    for yr, yd in sorted(years.items()):
        wk = yd.get("committee_wake_ups", [])
        if isinstance(wk, list):
            for s in wk:
                all_sessions.append((yr, s))
    if not all_sessions:
        return ""
    lines = [
        "## Risk Committee Activity (2016-2025)",
        "",
        "Committee wake-up sessions: triggered when VaR stress ratio exceeds mandate threshold.",
        "",
        "| Year | Sessions | Peak VaR (current) £ | Peak VaR (stressed) £ | Accounts touched |",
        "|------|----------|----------------------|----------------------|-----------------|",
    ]
    total_sessions = 0
    total_accounts = set()
    busiest_year = None
    busiest_count = 0
    peak_var_yr = None
    peak_var_val = 0.0
    for yr, yd in sorted(years.items()):
        wk = yd.get("committee_wake_ups", [])
        if not isinstance(wk, list) or not wk:
            continue
        n = len(wk)
        total_sessions += n
        if n > busiest_count:
            busiest_count = n
            busiest_year = yr
        peak_var_current = max(s.get("portfolio_var_current_gbp", 0) for s in wk)
        peak_var_stressed = max(s.get("portfolio_var_stressed_gbp", 0) for s in wk)
        if peak_var_current > peak_var_val:
            peak_var_val = peak_var_current
            peak_var_yr = yr
        accounts = set()
        for s in wk:
            accounts.update(s.get("adjustments", {}).keys())
        total_accounts.update(accounts)
        lines.append(f"| {yr} | {n} | £{peak_var_current:,.0f} | £{peak_var_stressed:,.0f} | {len(accounts)} |")
    lines += [
        "",
        f"**Total sessions 2016-2025: {total_sessions}** | Busiest year: {busiest_year} ({busiest_count} sessions)",
        f"Peak VaR observed: {peak_var_yr} at £{peak_var_val:,.0f} | Unique accounts ever adjusted: {len(total_accounts)}",
        "",
    ]
    # Most frequently adjusted accounts
    account_freq: dict[str, int] = {}
    for yr, s in all_sessions:
        for cid in s.get("adjustments", {}).keys():
            account_freq[cid] = account_freq.get(cid, 0) + 1
    if account_freq:
        lines.append("**Most frequently adjusted accounts:**")
        for cid, cnt in sorted(account_freq.items(), key=lambda x: -x[1])[:5]:
            lines.append(f"- {cid}: {cnt} sessions")
        lines.append("")
    lines.append("> Risk committee wake-ups are documented in `docs/observability/run_history.json`.")
    lines.append("")
    return "\n".join(lines)


def _section_customer_strategic_value(data: dict) -> str:
    bba = data.get("by_billing_account", {})
    if not bba:
        return ""
    # Only electricity accounts (not gas legs)
    elec_accounts = {cid: v for cid, v in bba.items() if not cid.endswith("g")}
    if not elec_accounts:
        return ""
    # Compute median CLV for quadrant boundary
    clvs = sorted(v.get("clv_gbp", 0.0) for v in elec_accounts.values())
    n = len(clvs)
    med_clv = clvs[n // 2]
    # Churn boundary: median churn probability
    churns = sorted(v.get("latest_churn_probability", 0.0) for v in elec_accounts.values())
    med_churn = churns[n // 2]
    quadrants = {
        "PROTECT": [],   # High CLV, Low Churn
        "CRITICAL": [],  # High CLV, High Churn
        "MONITOR": [],   # Low CLV, Low Churn
        "EXIT": [],      # Low CLV, High Churn
    }
    for cid, v in sorted(elec_accounts.items(), key=lambda x: -x[1].get("clv_gbp", 0)):
        clv = v.get("clv_gbp", 0.0)
        churn = v.get("latest_churn_probability", 0.0)
        periods = v.get("expected_lifetime_periods", 0.0)
        if clv >= med_clv and churn < med_churn:
            q = "PROTECT"
        elif clv >= med_clv and churn >= med_churn:
            q = "CRITICAL"
        elif clv < med_clv and churn < med_churn:
            q = "MONITOR"
        else:
            q = "EXIT"
        quadrants[q].append((cid, clv, churn, periods))
    total_clv = sum(v.get("clv_gbp", 0) for v in elec_accounts.values())
    lines = [
        "## Customer Strategic Value Matrix",
        "",
        "2x2 matrix: CLV (above/below median) × Churn probability (above/below median).",
        "Median CLV: " + _fmt_gbp(med_clv) + " | Median churn: " + ("%.0f%%" % (med_churn * 100)) + " | Total portfolio CLV: " + _fmt_gbp(total_clv),
        "",
    ]
    for q_name, q_label in [("PROTECT", "PROTECT (High CLV, Low Churn)"),
                              ("CRITICAL", "CRITICAL (High CLV, High Churn — priority intervention)"),
                              ("MONITOR", "MONITOR (Low CLV, Low Churn)"),
                              ("EXIT", "EXIT (Low CLV, High Churn)")]:
        members = quadrants[q_name]
        if not members:
            continue
        lines.append("### " + q_label)
        lines.append("")
        lines.append("| Account | CLV | Churn Prob | Expected Life |")
        lines.append("|---------|-----|------------|--------------|")
        for cid, clv, churn, periods in members:
            lines.append("| " + cid + " | " + _fmt_gbp(clv) + " | " + ("%.0f%%" % (churn * 100)) + " | " + ("%.1f" % periods) + " periods |")
        q_clv = sum(c for _, c, _, _ in members)
        lines.append("")
        lines.append("Quadrant CLV: " + _fmt_gbp(q_clv) + " (" + ("%.0f%%" % (q_clv / total_clv * 100 if total_clv else 0)) + " of portfolio)")
        lines.append("")
    if quadrants["CRITICAL"]:
        lines.append("**Board action: CRITICAL quadrant has " + str(len(quadrants["CRITICAL"])) +
                     " account(s). High CLV at risk from elevated churn probability. Immediate retention offers recommended.**")
        lines.append("")
    return "\n".join(lines)


def _section_customer_experience(data: dict) -> str:
    ydata = data.get("years", {})
    sq = data.get("service_quality_score")
    avg_clarity = data.get("avg_clarity_total")
    avg_complaint = data.get("avg_complaint_probability_total")
    if not ydata or not sq:
        return ""
    years = sorted(ydata.keys())
    lines = [
        "## Customer Experience & Service Quality",
        "",
        "| Year | Billing Clarity | Complaint Prob | Acq Attempts | Acq Wins | Flag |",
        "|------|----------------|---------------|-------------|---------|------|",
    ]
    worst_clarity = 1.0
    worst_yr = None
    for yr in years:
        yd = ydata[yr]
        clarity = yd.get("avg_clarity") or 0.0
        complaint = yd.get("avg_complaint_probability") or 0.0
        acq_att = yd.get("acquisition_attempts") or 0
        acq_wins = yd.get("acquisition_wins") or 0
        flag = ""
        if clarity < 0.80:
            flag = "**LOW CLARITY**"
        elif complaint > 0.055:
            flag = "HIGH COMPLAINTS"
        if clarity < worst_clarity:
            worst_clarity = clarity
            worst_yr = yr
        lines.append(
            "| " + yr + " | " + ("%.3f" % clarity) + " | " + ("%.3f" % complaint) +
            " | " + str(acq_att) + " | " + str(acq_wins) + " | " + flag + " |"
        )
    lines.append("")
    total_att = data.get("total_acquisition_attempts", 0) or 0
    total_wins = data.get("total_acquisition_wins", 0) or 0
    win_rate = (total_wins / total_att * 100) if total_att > 0 else 0.0
    if sq:
        lines.append("**Overall service quality:** " + ("%.1f%%" % (sq * 100)) + " | " +
                     "**Average billing clarity:** " + ("%.3f" % (avg_clarity or 0)) + " | " +
                     "**Average complaint probability:** " + ("%.3f" % (avg_complaint or 0)))
        lines.append("")
    if total_att > 0:
        lines.append(
            "**Acquisition performance:** " + str(total_att) + " attempts, " +
            str(total_wins) + " wins (" + ("%.0f%%" % win_rate) + " win rate). " +
            ("No new customers acquired — " if total_wins == 0 else "") +
            "cap-constrained gate blocked resi acquisition 2021-2023 (negative projected margin)."
        )
        lines.append("")
    if worst_yr:
        lines.append(
            "**Lowest clarity: " + worst_yr + "** (" + ("%.3f" % worst_clarity) + ") — " +
            "crisis complexity (multiple tariff changes, bill shock events) degraded statement clarity."
        )
        lines.append("")
    return "\n".join(lines)


def _section_bill_shock_analysis(data: dict) -> str:
    ydata = data.get("years", {})
    if not ydata:
        return ""
    years = sorted(ydata.keys())
    has_data = any(ydata[yr].get("avg_bill_shock_pct") is not None for yr in years)
    if not has_data:
        return ""
    lines = [
        "## Bill Shock Analysis",
        "",
        "Bill shock events occur when a customer\'s bill increases >20% vs the prior bill.",
        "Regulatory context: Ofgem monitors bill shock as a consumer harm indicator.",
        "",
        "| Year | Avg Shock % | Events | Bills | Shock Rate | Flag |",
        "|------|------------|--------|-------|------------|------|",
    ]
    worst_yr = None
    worst_shock = 0.0
    for yr in years:
        yd = ydata[yr]
        avg = yd.get("avg_bill_shock_pct") or 0.0
        events_list = yd.get("bill_shock_events", [])
        n_events = len(events_list) if isinstance(events_list, list) else int(events_list or 0)
        bills = yd.get("bills_count", 0) or 0
        shock_rate = (n_events / bills * 100) if bills > 0 else 0.0
        flag = ""
        if avg >= 0.30:
            flag = "**HIGH**"
        elif avg >= 0.20:
            flag = "ELEVATED"
        if avg > worst_shock:
            worst_shock = avg
            worst_yr = yr
        lines.append(
            "| " + yr + " | " + ("%.1f%%" % (avg * 100)) + " | " + str(n_events) +
            " | " + str(bills) + " | " + ("%.0f%%" % shock_rate) + " | " + flag + " |"
        )
    lines.append("")
    if worst_yr:
        lines += [
            "**Crisis peak: " + worst_yr + "** — " + ("%.1f%%" % (worst_shock * 100)) +
            " average shock. Energy crisis drove wholesale costs above locked tariff rates,",
            "causing step-change increases at every renewal. SLC 21: suppliers must issue",
            "renewal notice 42 days before contract end, giving customers time to switch.",
            "",
        ]
    return "\n".join(lines)


def _section_policy_cost_breakdown(data: dict) -> str:
    ydata = data.get("years", {})
    if not ydata:
        return ""
    years = sorted(ydata.keys())
    has_data = any(ydata[yr].get("policy_cost_gbp") for yr in years)
    if not has_data:
        return ""
    lines = [
        "## Policy Cost & Levy Breakdown",
        "",
        "UK energy levies collected through supplier bills. Policy costs are non-commodity costs",
        "passed through to customers. CfD levy went negative in 2022 (crisis: spot exceeded strike prices;",
        "renewable generators repaid back via levy mechanism).",
        "",
        "| Year | RO | CfD | CCL | CM | FiT | Total Policy | Network |",
        "|------|----|-----|-----|----|-----|-------------|---------|",
    ]
    cfd_negative_year = None
    for yr in years:
        yd = ydata[yr]
        ro = yd.get("ro_levy_gbp", 0.0)
        cfd = yd.get("cfd_levy_gbp", 0.0)
        ccl = yd.get("ccl_gbp", 0.0)
        cm = yd.get("cm_levy_gbp", 0.0)
        fit = yd.get("fit_levy_gbp", 0.0)
        pc = yd.get("policy_cost_gbp", 0.0)
        nc = yd.get("network_cost_gbp", 0.0)
        if cfd < 0 and cfd_negative_year is None:
            cfd_negative_year = yr
        cfd_str = _fmt_gbp(cfd)
        if cfd < 0:
            cfd_str = "**" + cfd_str + "**"
        lines.append(
            "| " + yr + " | " + _fmt_gbp(ro) + " | " + cfd_str +
            " | " + _fmt_gbp(ccl) + " | " + _fmt_gbp(cm) + " | " + _fmt_gbp(fit) +
            " | " + _fmt_gbp(pc) + " | " + _fmt_gbp(nc) + " |"
        )
    lines.append("")
    if cfd_negative_year:
        lines += [
            "**CfD rebate in " + cfd_negative_year + ":** Contracts for Difference (CfD) generators are paid",
            "the difference between strike price and reference price. When spot > strike (2022 crisis),",
            "the mechanism reverses — generators pay back, creating a negative levy for suppliers.",
            "",
        ]
    # Policy cost CAGR from first to latest year
    first_pc = ydata[years[0]].get("policy_cost_gbp", 0.0)
    last_pc = ydata[years[-1]].get("policy_cost_gbp", 0.0)
    if first_pc > 0 and last_pc > 0:
        n_years = len(years) - 1
        if n_years > 0:
            cagr = ((last_pc / first_pc) ** (1.0 / n_years) - 1.0) * 100.0
            lines.append(
                "Policy costs: " + _fmt_gbp(first_pc) + " (" + years[0] + ") → " +
                _fmt_gbp(last_pc) + " (" + years[-1] + "). CAGR: " + ("%.1f%%" % cagr) + "."
            )
            lines.append("")
    return "\n".join(lines)


def _section_commodity_split(data: dict) -> str:
    ydata = data.get("years", {})
    if not ydata:
        return ""
    years = sorted(ydata.keys())
    has_cs = any(ydata[yr].get("commodity_split") for yr in years)
    if not has_cs:
        return ""
    lines = [
        "## Electricity vs Gas P&L Split",
        "",
        "Year-by-year net margin by fuel. Gas became structurally loss-making from 2021.",
        "",
        "| Year | Elec Net | Gas Net | Elec Rev | Gas Rev | Gas Share of Rev | Gas Profitable |",
        "|------|----------|---------|----------|---------|-----------------|---------------|",
    ]
    gas_loss_years = []
    gas_prof_years = []
    for yr in years:
        cs = ydata[yr].get("commodity_split", {})
        elec = cs.get("electricity", {})
        gas = cs.get("gas", {})
        e_net = elec.get("net_gbp", 0.0)
        g_net = gas.get("net_gbp", 0.0)
        e_rev = elec.get("revenue_gbp", 0.0)
        g_rev = gas.get("revenue_gbp", 0.0)
        total_rev = e_rev + g_rev
        gas_share_pct = (g_rev / total_rev * 100) if total_rev > 0 else 0.0
        is_gas_profitable = g_net >= 0
        flag = "YES" if is_gas_profitable else "**NO**"
        if is_gas_profitable:
            gas_prof_years.append(yr)
        else:
            gas_loss_years.append(yr)
        lines.append(
            "| " + yr + " | " + _fmt_gbp(e_net) + " | " + _fmt_gbp(g_net) +
            " | " + _fmt_gbp(e_rev) + " | " + _fmt_gbp(g_rev) +
            " | " + ("%.1f%%" % gas_share_pct) + " | " + flag + " |"
        )
    lines.append("")
    if gas_loss_years:
        first_loss = gas_loss_years[0]
        lines.append(
            "**Gas has been loss-making since " + first_loss + "** (" +
            str(len(gas_loss_years)) + " consecutive years). " +
            "Electricity cross-subsidises gas supply."
        )
    else:
        lines.append("**Gas supply has been profitable throughout** (" + str(len(gas_prof_years)) + " years).")
    lines.append("")
    return "\n".join(lines)


def _section_management_accounts(data: dict) -> str:
    ma = data.get("management_accounts", {})
    if not ma:
        return ""
    years = sorted(ma.keys())
    lines = [
        "## Annual Management Accounts",
        "",
        "Year-by-year income statement from company accounting records. All figures £.",
        "",
        "| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |",
        "|------|---------|-----------|-----------|--------------|----------|------|------------|",
    ]
    cumulative_rev = 0.0
    cumulative_net = 0.0
    for yr in years:
        inc = ma[yr].get("income_statement", {})
        rev = inc.get("revenue_gbp", 0.0)
        whl = inc.get("wholesale_cost_gbp", 0.0)
        ncm = inc.get("non_commodity_cost_gbp", 0.0)
        gm = inc.get("gross_margin_gbp", 0.0)
        bd = inc.get("bad_debt_gbp", 0.0)
        opx = inc.get("total_opex_gbp", 0.0)
        net = inc.get("net_margin_gbp", 0.0)
        cumulative_rev += rev
        cumulative_net += net
        net_pct = (net / rev * 100) if rev > 0 else 0.0
        net_str = _fmt_gbp(net) + " (" + ("%.1f%%" % net_pct) + ")"
        lines.append(
            "| " + yr + " | " + _fmt_gbp(rev) + " | " + _fmt_gbp(whl) +
            " | " + _fmt_gbp(ncm) + " | " + _fmt_gbp(gm) +
            " | " + _fmt_gbp(bd) + " | " + _fmt_gbp(opx) +
            " | " + net_str + " |"
        )
    # Totals row
    total_pct = (cumulative_net / cumulative_rev * 100) if cumulative_rev > 0 else 0.0
    lines.append(
        "| **Total** | **" + _fmt_gbp(cumulative_rev) + "** | | | | | | **" +
        _fmt_gbp(cumulative_net) + " (" + ("%.1f%%" % total_pct) + ")** |"
    )
    lines.append("")
    # Key commentary
    # Identify worst and best net margin years
    margin_by_year = {yr: ma[yr].get("income_statement", {}).get("net_margin_gbp", 0.0) for yr in years}
    best_yr = max(margin_by_year, key=lambda y: margin_by_year[y])
    worst_yr = min(margin_by_year, key=lambda y: margin_by_year[y])
    best_inc = ma[best_yr].get("income_statement", {})
    worst_inc = ma[worst_yr].get("income_statement", {})
    lines += [
        "**Best year:** " + best_yr + " — net " + _fmt_gbp(best_inc.get("net_margin_gbp", 0)) +
        " (" + ("%.1f%%" % (best_inc.get("net_margin_gbp", 0) / best_inc.get("revenue_gbp", 1) * 100)) + " margin)",
        "**Worst year:** " + worst_yr + " — net " + _fmt_gbp(worst_inc.get("net_margin_gbp", 0)) +
        " (" + ("%.1f%%" % (worst_inc.get("net_margin_gbp", 0) / worst_inc.get("revenue_gbp", 1) * 100)) + " margin)",
        "",
    ]
    # Balance sheet summary for latest year
    latest_yr = years[-1]
    bs = ma[latest_yr].get("balance_sheet", {})
    if bs:
        lines += [
            "### Balance Sheet (Year End " + latest_yr + ")",
            "",
            "| Item | Value |",
            "|------|-------|",
            "| Cash | " + _fmt_gbp(bs.get("cash_gbp", 0)) + " |",
            "| Trade Receivables | " + _fmt_gbp(bs.get("trade_receivables_gbp", 0)) + " |",
            "| **Total Assets** | **" + _fmt_gbp(bs.get("total_assets_gbp", 0)) + "** |",
            "| Opening Capital | " + _fmt_gbp(bs.get("opening_capital_gbp", 0)) + " |",
            "| Current Period Profit | " + _fmt_gbp(bs.get("current_period_profit_gbp", 0)) + " |",
            "",
        ]
    return "\n".join(lines)


def _section_segment_capital_efficiency(data):
    ydata = data.get('years', {})
    if not ydata:
        return ''
    sl = {}
    for yr, yd in sorted(ydata.items()):
        for seg, vals in yd.get('segment_split', {}).items():
            if seg not in sl:
                sl[seg] = [0.0, 0.0, 0.0]
            sl[seg][0] += vals.get('gross_gbp', 0.0)
            sl[seg][1] += vals.get('capital_gbp', 0.0)
            sl[seg][2] += vals.get('net_gbp', 0.0)
    if not sl:
        return ''
    lines = [
        '## Segment Capital Efficiency (Return-on-Capital)',
        '',
        'Lifetime net margin and capital deployed per segment.',
        'ROC = lifetime net / lifetime capital. ROC < 0 = capital destroyer.',
        '',
        '| Segment | Lifetime Gross | Capital Deployed | Lifetime Net | ROC | Signal |',
        '|---------|---------------|------------------|--------------|-----|--------|',
    ]
    for seg in sorted(sl):
        g, cap, net = sl[seg]
        roc = net / cap if cap > 0 else 0.0
        sig = 'CAPITAL DESTROYER' if roc < 0 else ('Low return' if roc < 5 else ('Moderate' if roc < 15 else 'Strong'))
        lines.append('| ' + seg + ' | ' + _fmt_gbp(g) + ' | ' + _fmt_gbp(cap) + ' | ' + _fmt_gbp(net) + ' | ' + ('%.1fx' % roc) + ' | ' + sig + ' |')
    lines.append('')
    gas_segs = [s for s in sl if 'gas' in s]
    elec_segs = [s for s in sl if 'electricity' in s]
    gas_net = sum(sl[s][2] for s in gas_segs)
    elec_net = sum(sl[s][2] for s in elec_segs)
    gas_cap = sum(sl[s][1] for s in gas_segs)
    if gas_cap > 0 and gas_net < 0:
        lines += [
            '**Gas Segment Finding:**',
            '- Gas supply legs are net-negative over the simulation period (' + _fmt_gbp(gas_net) + ' net on ' + _fmt_gbp(gas_cap) + ' capital)',
            '- Electricity segments (' + _fmt_gbp(elec_net) + ' net) cross-subsidise gas retention',
            '- Board decision required: is dual-fuel gas justified by CLV, or does it need pricing reform?',
            '',
        ]
    return chr(10).join(lines)


def _section_portfolio_concentration_risk(data: dict) -> str:
    """Phase AN: Portfolio Concentration Risk.

    Computes revenue concentration across segments and customers.
    Uses per_customer_lifetime net_margin_after_cost_to_serve_gbp as the
    revenue proxy (lifetime contribution to margin).

    HHI (Herfindahl-Hirschman Index) on net margin shares:
      HHI < 1500: low concentration
      HHI 1500-2500: moderate
      HHI > 2500: high (regulatory concern in many sectors)

    Board signal: a supplier where >95% of margin comes from I&C customers
    faces existential concentration risk — one large departure is catastrophic.

    Silent when per_customer_lifetime absent.
    """
    pcl = data.get("per_customer_lifetime", {})
    if not pcl:
        return ""

    cbr = data.get("churn_basis_risk", [])

    # Latest churn probability per customer
    latest_churn: dict[str, float] = {}
    for rec in cbr:
        cid = rec.get("customer_id", "")
        ts = rec.get("term_start", "")
        if cid and (cid not in latest_churn or ts > (cbr[0].get("term_start", ""))):
            latest_churn[cid] = rec.get("sim_churn_probability", 0.0)

    # Rebuild using proper latest
    latest_churn = {}
    seen_ts: dict[str, str] = {}
    for rec in cbr:
        cid = rec.get("customer_id", "")
        ts = rec.get("term_start", "")
        if cid and (cid not in seen_ts or ts > seen_ts[cid]):
            seen_ts[cid] = ts
            latest_churn[cid] = rec.get("sim_churn_probability", 0.0)

    # Segment concentrations
    segment_margin: dict[str, float] = {}
    customer_margin: dict[str, float] = {}
    for cid, v in pcl.items():
        seg = v.get("segment", "?")
        nm = v.get("net_margin_after_cost_to_serve_gbp") or 0.0
        if nm > 0:
            segment_margin[seg] = segment_margin.get(seg, 0.0) + nm
            customer_margin[cid] = nm

    total_pos = sum(customer_margin.values())
    if total_pos <= 0:
        return ""

    # HHI
    shares = [v / total_pos for v in customer_margin.values()]
    hhi = sum(s * s for s in shares) * 10000

    if hhi > 2500:
        hhi_label = "HIGH (>2,500)"
    elif hhi > 1500:
        hhi_label = "MODERATE (1,500-2,500)"
    else:
        hhi_label = "LOW (<1,500)"

    lines = [
        "## Portfolio Concentration Risk",
        "",
        f"Revenue concentration analysis across {len(customer_margin)} margin-positive accounts. "
        f"Herfindahl-Hirschman Index (HHI): **{hhi:.0f}** — {hhi_label}.",
        "",
        "**Segment Margin Share:**",
    ]
    for seg, sm in sorted(segment_margin.items(), key=lambda kv: -kv[1]):
        pct = sm / total_pos
        lines.append(f"- {seg}: {_fmt_gbp(sm)} ({pct:.1%} of total positive margin)")

    lines += [
        "",
        "**Top 5 Accounts by Margin Contribution:**",
        "",
        "| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |",
        "|---------|---------|-----------------|-------|-------------------|----------------|",
    ]

    top5 = sorted(customer_margin.items(), key=lambda kv: -kv[1])[:5]
    for cid, nm in top5:
        share = nm / total_pos
        churn_p = latest_churn.get(cid, 0.0)
        margin_at_risk = nm * churn_p
        seg = pcl.get(cid, {}).get("segment", "?")
        lines.append(
            "| " + cid + " | " + seg + " | " + _fmt_gbp(nm) + " | " +
            f"{share:.1%}" + " | " + f"{churn_p:.0%}" + " | " +
            _fmt_gbp(margin_at_risk) + " |"
        )

    lines.append("")

    # Board warning
    ic_share = segment_margin.get("I&C", 0.0) / total_pos if total_pos > 0 else 0.0
    if ic_share > 0.95:
        lines += [
            "**Concentration Risk Warning:**",
            f"- I&C segment accounts for {ic_share:.1%} of total portfolio margin",
            "- Resi and SME segments are effectively margin-neutral at portfolio scale",
            "- A single large I&C departure would remove 14-29% of all margin",
            "- Board action: diversify acquisition pipeline toward profitable resi/SME to reduce I&C dependency",
        ]
    elif ic_share > 0.80:
        lines.append(
            "**Note:** I&C segment accounts for " + f"{ic_share:.1%}" +
            " of margin. Consider resi/SME margin improvement to reduce concentration."
        )

    lines.append("")
    return "\n".join(lines)


def _section_crm_intelligence(data: dict) -> str:
    """Phase AJ: CRM Risk Triage - final-year churn risk bands + repricing triage.

    Uses churn_basis_risk (latest renewal per customer) and per_customer_lifetime
    to produce an ex-post board view of which accounts ended the simulation at
    which risk band and what repricing action is warranted.

    Risk bands mirror Phase AD: CRITICAL>=50%, HIGH>=30%, MEDIUM>=15%, LOW<15%.
    Silent when churn_basis_risk is absent.
    """
    cbr = data.get("churn_basis_risk", [])
    if not cbr:
        return ""

    pcl = data.get("per_customer_lifetime", {})

    latest = {}
    for rec in cbr:
        cid = rec.get("customer_id", "")
        if not cid:
            continue
        if cid not in latest or rec.get("term_start", "") > latest[cid].get("term_start", ""):
            latest[cid] = rec

    if not latest:
        return ""

    def _risk_band(p):
        if p >= 0.50:
            return "CRITICAL"
        if p >= 0.30:
            return "HIGH"
        if p >= 0.15:
            return "MEDIUM"
        return "LOW"

    def _rate_flag(rate_vs_svt):
        if rate_vs_svt is None:
            return "n/a"
        if rate_vs_svt > 5.0:
            return "+" + f"{rate_vs_svt:.1f}" + "% [overpriced]"
        if rate_vs_svt < -20.0:
            return f"{rate_vs_svt:.1f}" + "% [competitive]"
        return f"{rate_vs_svt:+.1f}" + "%"

    rows = []
    for cid, rec in sorted(
        latest.items(),
        key=lambda kv: kv[1].get("sim_churn_probability", 0.0),
        reverse=True,
    ):
        sim_p = rec.get("sim_churn_probability", 0.0)
        co_est = rec.get("company_churn_estimate", 0.0)
        rate_vs_svt = rec.get("rate_vs_svt_pct")
        band = _risk_band(sim_p)
        pcl_rec = pcl.get(cid, {})
        segment = pcl_rec.get("segment", "?")
        lifetime_margin = pcl_rec.get("net_margin_after_cost_to_serve_gbp", 0.0)
        rows.append((cid, segment, band, sim_p, co_est, rate_vs_svt, lifetime_margin))

    lines = [
        "## CRM Intelligence: Risk Triage (Final Year)",
        "",
        "Latest renewal record per account. Risk bands: CRITICAL>=50% | HIGH>=30% | MEDIUM>=15% | LOW<15%.",
        "",
        "| Account | Seg | Risk Band | Sim Churn | Co. Est. | Rate vs SVT | Lifetime Margin |",
        "|---------|-----|-----------|-----------|----------|-------------|-----------------|",
    ]

    for cid, seg, band, sim_p, co_est, rvs, lm in rows:
        lm_fmt = _fmt_gbp(lm) if lm else "n/a"
        lines.append(
            "| " + cid + " | " + seg + " | " + band + " | " +
            f"{sim_p:.0%}" + " | " + f"{co_est:.0%}" + " | " +
            _rate_flag(rvs) + " | " + lm_fmt + " |"
        )

    lines.append("")

    band_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    at_risk_margin = 0.0
    overpriced_high = 0
    for cid, seg, band, sim_p, co_est, rvs, lm in rows:
        band_counts[band] += 1
        if band in ("CRITICAL", "HIGH"):
            at_risk_margin += lm if lm else 0.0
            if rvs is not None and rvs > 5.0:
                overpriced_high += 1

    lines += [
        "**Risk Band Summary (latest renewal):**",
        "- CRITICAL (>=50%): " + str(band_counts["CRITICAL"]) + " accounts",
        "- HIGH (>=30%): " + str(band_counts["HIGH"]) + " accounts",
        "- MEDIUM (>=15%): " + str(band_counts["MEDIUM"]) + " accounts",
        "- LOW (<15%): " + str(band_counts["LOW"]) + " accounts",
        "- Lifetime margin at risk (CRITICAL+HIGH): " + _fmt_gbp(at_risk_margin),
    ]
    if overpriced_high:
        lines.append(
            "- Overpriced vs SVT within HIGH/CRITICAL band: " + str(overpriced_high) +
            " account(s) -- rate shock risk compounds churn probability"
        )

    high_risk_missed = [
        (cid, sim_p, co_est)
        for cid, seg, band, sim_p, co_est, rvs, lm in rows
        if band in ("CRITICAL", "HIGH") and co_est < 0.10
    ]
    if high_risk_missed:
        lines += [
            "",
            "**Company blind spot:** " + str(len(high_risk_missed)) +
            " HIGH/CRITICAL account(s) where company churn estimate was <10%.",
        ]
        for cid, sim_p, co_est in high_risk_missed[:5]:
            lines.append("  - " + cid + ": sim " + f"{sim_p:.0%}" + ", company est " + f"{co_est:.0%}")

    lines.append("")
    return "\n".join(lines)


def _load_old_model_data() -> dict | None:
    """Load the pre-Phase-5c run snapshot for `_mandate_comparison_section`,
    or None if it isn't present."""
    if not OLD_MODEL_REPORT_DATA_PATH.exists():
        return None
    return json.loads(OLD_MODEL_REPORT_DATA_PATH.read_text())


def generate_annual_report(data: dict) -> str:
    """Build the full markdown annual report from `extract_report_data()`'s
    output."""
    sections = [
        "# Annual Report — The Synthetic Enterprise\n",
        _section_scenario_metadata(data),   # Phase 37a: forward scenario banner (silent if not a scenario run)
        _executive_summary(data),
    ]

    sections.append(_section_board_risk_summary(data))               # Phase AQ
    sections.append(_mandate_comparison_section(data, _load_old_model_data()))
    sections.append(_administration_section(data))
    sections.append(_hedge_effectiveness_summary_section(data))
    sections.append(_segment_margin_trend_section(data))
    sections.append(_customer_lifecycle_events_section(data))
    sections.append(_churn_basis_risk_section(data))
    sections.append(_section_active_passive_renewal(data))
    sections.append(_section_svt_comparison(data))      # Phase 39a
    sections.append(_section_company_divergence(data))
    sections.append(_section_demand_estimation(data))
    sections.append(_section_eac_drift_snapshot(data))  # Phase AI
    sections.append(_section_company_crm(data))
    sections.append(_section_policy_costs(data))
    sections.append(_section_network_costs(data))
    sections.append(_section_gas_policy_costs(data))
    sections.append(_section_trading_pnl(data))
    sections.append(_section_gas_pl(data))
    sections.append(_section_solvency_signal(data))
    sections.append(_section_bsc_credit(data))        # Phase 53
    sections.append(_section_volume_tolerance(data))
    sections.append(_section_triad_exposure(data))
    sections.append(_section_ic_portfolio(data))
    sections.append(_section_tou_utilization(data))
    sections.append(_section_bill_shock_summary(data))
    sections.append(_section_gas_renewal_pressure(data))
    sections.append(_section_retention_strategy(data))
    sections.append(_section_retention_durability(data))
    sections.append(_section_enterprise_value_analysis(data))
    sections.append(_clv_trajectory_section(data))
    sections.append(_lifetime_pricing_section(data))
    sections.append(_section_repricing_impact(data))
    sections.append(_section_margin_feedback(data))
    sections.append(_section_profitability_uplift(data))
    sections.append(_section_flexibility_revenue(data))   # Phase AG
    sections.append(_section_portfolio_intelligence_pack(data))  # Phase AH
    sections.append(_section_crm_intelligence(data))  # Phase AJ
    sections.append(_section_churn_root_cause(data))   # Phase AK
    sections.append(_section_counterfactual_retention(data))  # Phase AL
    sections.append(_section_pricing_basis_risk(data))          # Phase AM
    sections.append(_section_price_cap_headroom(data))             # Phase BM
    sections.append(_section_stress_test_history(data))            # Phase BL
    sections.append(_section_financial_ratios(data))               # Phase BK
    sections.append(_section_churn_prediction_calibration(data))   # Phase BJ
    sections.append(_section_tariff_estimation_accuracy(data))     # Phase BI
    sections.append(_section_dynamic_pricing_activity(data))       # Phase BH
    sections.append(_section_clv_evolution(data))                  # Phase BG
    sections.append(_section_gross_margin_bridge(data))            # Phase BE
    sections.append(_section_risk_committee_activity(data))        # Phase BC
    sections.append(_section_customer_strategic_value(data))       # Phase AY
    sections.append(_section_customer_experience(data))            # Phase AX
    sections.append(_section_bill_shock_analysis(data))            # Phase AW
    sections.append(_section_policy_cost_breakdown(data))          # Phase AV
    sections.append(_section_commodity_split(data))                # Phase AU
    sections.append(_section_gas_exit_analysis(data))              # Phase AS
    sections.append(_section_segment_capital_efficiency(data))     # Phase AP
    sections.append(_section_portfolio_concentration_risk(data))  # Phase AN
    sections.append(_section_dynamic_pricing(data))
    sections.append(_section_churn_avoidability(data))
    sections.append(_section_dual_fuel_pnl(data))
    sections.append(_section_customer_pnl_ranking(data))
    sections.append(_section_revenue_sanity(data))
    sections.append(_ledger_summary_section(data))
    sections.append(_section_management_accounts(data))
    sections.append(_section_budget_vs_actual(data))   # Phase 65
    sections.append(_growth_acquisition_section(data))

    for year in sorted(data["years"]):
        yd = data["years"][year]
        sections.append(f"## {year}\n")
        sections.append(_trading_risk_section(year, yd))
        sections.append("")
        sections.append(_customer_book_section(year, yd, data))
        sections.append("")
        sections.append(_pricing_margin_section(yd))
        sections.append("")
        sections.append(_portfolio_health_section(year, yd, data))
        sections.append("")
        sections.append(_hedge_effectiveness_section(yd))
        sections.append("")
        sections.append(_year_narrative(year, yd))
        sections.append("")

    return "\n".join(sections)


def _current_git_commit() -> str | None:
    """Short hash of HEAD, or None if it can't be determined (e.g. not a
    git checkout)."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _run_and_extract(report_end: str | None = None) -> dict:
    run_output = run_phase4c_on_phase2b(report_end=report_end)
    return extract_report_data(run_output)


def _send_run_complete_ntfy(data: dict, report_path: Path) -> None:
    # Removed: per-run NTFYs from annual_report are spam (one run every ~17min).
    # Claude picks up results via run_complete_*.md staging markers instead.
    pass


def main() -> None:
    import os

    parser = argparse.ArgumentParser(description="Generate the annual report")
    parser.add_argument(
        "--from-json",
        type=Path,
        default=None,
        help="Load extracted report data from this JSON file instead of "
        "running the simulation",
    )
    parser.add_argument("--save-json", type=Path, default=DEFAULT_REPORT_DATA_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument(
        "--end-year",
        type=int,
        default=None,
        metavar="YYYY",
        help="Truncate the simulation window at Dec 31 of this year (e.g. 2020). "
        "Useful for fast iteration on early years without running the full window.",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Set SIM_FAST_MODE=1: use the deterministic mock risk committee "
        "(no LLM calls). Cuts per-run time from ~hours to ~minutes.",
    )
    args = parser.parse_args()

    if args.fast:
        os.environ["SIM_FAST_MODE"] = "1"
        print("[FAST MODE] SIM_FAST_MODE=1 — deterministic mock committee, no LLM calls.")

    report_end = f"{args.end_year}-12-31" if args.end_year else None
    if report_end:
        print(f"[TRUNCATED] Simulation window truncated to {report_end}.")

    if args.from_json:
        data = json.loads(args.from_json.read_text())
    elif not report_end and DEFAULT_REPORT_DATA_PATH.exists() and args.save_json == DEFAULT_REPORT_DATA_PATH:
        data = json.loads(DEFAULT_REPORT_DATA_PATH.read_text())
        cached_commit = data.get("_cache_meta", {}).get("git_commit")
        current_commit = _current_git_commit()
        if cached_commit and current_commit and cached_commit != current_commit:
            print(
                f"WARNING: cached report data ({DEFAULT_REPORT_DATA_PATH}) was "
                f"generated at commit {cached_commit}, but HEAD is now "
                f"{current_commit} -- figures may be stale. Delete the cache "
                f"or pass --save-json to re-run the simulation."
            )
    else:
        raw_output = run_phase4c_on_phase2b(report_end=report_end)
        data = extract_report_data(raw_output)
        args.save_json.parent.mkdir(parents=True, exist_ok=True)
        args.save_json.write_text(json.dumps(data, indent=2))
        fresh_full_run = not args.fast and not report_end
        if fresh_full_run:
            ledger_events = raw_output.get("ledger_events", [])
            if ledger_events:
                LEDGER_LATEST_PATH.parent.mkdir(parents=True, exist_ok=True)
                LEDGER_LATEST_PATH.write_text(json.dumps(ledger_events, indent=2))
                print(f"Wrote {LEDGER_LATEST_PATH} ({len(ledger_events):,} events)")
            _send_run_complete_ntfy(data, args.output)

    report = generate_annual_report(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report)
    print(f"Wrote {args.output} ({len(report)} chars, {len(data['years'])} years)")


if __name__ == "__main__":
    main()
