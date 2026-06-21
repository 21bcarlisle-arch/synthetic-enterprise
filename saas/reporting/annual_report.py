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

    yearly = {}
    for year in years:
        yr_records = [r for r in all_records if _year(r["settlement_date"]) == year]

        commodity_split = {}
        for commodity in ("electricity", "gas"):
            recs = [r for r in yr_records if r.get("commodity") == commodity]
            commodity_split[commodity] = {
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

        bad_debt_gbp = sum(
            r["bad_debt_provision_gbp"]
            for records in payment_behaviour.values()
            for r in records
            if _year(r["period_end"]) == year
        )

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
            "net_gbp": sum(r["net_margin_gbp"] for r in yr_records),
            "treasury_end_gbp": treasury_end,
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

    return {
        "starting_treasury_gbp": phase2b["starting_treasury"],
        "final_treasury_gbp": phase2b["final_treasury"],
        "total_revenue_gbp": sum(r["revenue_gbp"] for r in all_records),
        "total_gross_gbp": phase2b["total_gross"],
        "total_capital_gbp": phase2b["total_capital"],
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
    }


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
    lines.append(f"- Regulatory threshold breaches: {NOT_AVAILABLE}")
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


def _section_company_divergence(data: dict) -> str:
    """Company Model Divergence -- Phase 12e.

    Year-by-year mean/max absolute error for the two consequential company
    models: tariff pricing and churn estimation.
    """
    div = data.get("company_divergence", {})
    tariff_by_year = div.get("tariff_error_by_year", {})
    churn_by_year = div.get("churn_error_by_year", {})

    if not tariff_by_year and not churn_by_year:
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
            "| Year | Renewals | Mean Abs Error | Max Abs Error |",
            "|------|----------|---------------|--------------|",
        ]
        for yr, s in sorted(churn_by_year.items()):
            n, mean_pct, max_pct = s["n"], s["mean_abs_error_pct"] * 100, s["max_abs_error_pct"] * 100
            lines.append(f"| {yr} | {n} | {mean_pct:.1f}% | {max_pct:.1f}% |")
        lines.append("")

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
        "",
        "| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate |",
        "|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|",
    ]
    for cid, s in sorted(tou.items()):
        lines.append(
            f"| {cid} | {s['total_kwh']:,.0f} | {s['peak_kwh']:,.0f} | {s['peak_pct']:.1f}%"
            f" | \xa3{s['peak_revenue_gbp']:,.2f} | \xa3{s['offpeak_revenue_gbp']:,.2f}"
            f" | \xa3{s['avg_peak_rate']:,.2f}/MWh | \xa3{s['avg_offpeak_rate']:,.2f}/MWh |"
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
        "",
        "Missed opportunities (churns with no offer): **" + str(missed_count) + "**"
        " (" + missed_str + " expected margin lost without offer)",
    ]
    if missed_uneconomical:
        unecon_margin = sum(r.get("expected_term_margin_gbp", 0.0) for r in missed_uneconomical)
        lines.append(
            "- **Blocked — uneconomical** (churn estimate above threshold but margin < discount cost): "
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

    lines += [
        "### Per-Offer Detail",
        "",
        "| Date | Customer | Est. churn | Offer Cost | Expected Margin | Net | Outcome |",
        "|------|----------|-----------|-----------|----------------|-----|---------|",
    ]
    for r in sorted(rl, key=lambda x: x["event_date"]):
        exp_m = r.get("expected_term_margin_gbp", 0.0)
        cost = r.get("retention_cost_gbp", 0.0)
        net = (exp_m - cost) if r["outcome"] == "retained" else -cost
        ed = r["event_date"]
        cid = r["customer_id"]
        ce = r["company_churn_estimate"]
        oc = r["outcome"]
        row = (
            "| " + ed + " | " + cid + " | " + "%.2f" % ce
            + " | \xa3" + "%.2f" % cost
            + " | \xa3" + "%.2f" % exp_m
            + " | \xa3" + "%.2f" % net
            + " | " + oc + " |"
        )
        lines.append(row)
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
        _executive_summary(data),
    ]

    sections.append(_mandate_comparison_section(data, _load_old_model_data()))
    sections.append(_administration_section(data))
    sections.append(_hedge_effectiveness_summary_section(data))
    sections.append(_segment_margin_trend_section(data))
    sections.append(_customer_lifecycle_events_section(data))
    sections.append(_churn_basis_risk_section(data))
    sections.append(_section_company_divergence(data))
    sections.append(_section_company_crm(data))
    sections.append(_section_tou_utilization(data))
    sections.append(_section_retention_strategy(data))
    sections.append(_clv_trajectory_section(data))
    sections.append(_lifetime_pricing_section(data))
    sections.append(_ledger_summary_section(data))
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
