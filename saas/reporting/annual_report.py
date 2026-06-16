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

from saas.customer_reaction import _billing_account_id
from saas.customers import CUSTOMERS
from simulation.run_phase4c_on_phase2b import main as run_phase4c_on_phase2b

DEFAULT_REPORT_DATA_PATH = Path("docs/reports/run_output_latest.json")
DEFAULT_REPORT_PATH = Path("docs/reports/ANNUAL_REPORT.md")

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

    segment_by_customer = {c["customer_id"]: c["segment"] for c in CUSTOMERS}

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
                c["customer_id"] for c in CUSTOMERS if _year(c["acquisition_date"]) == year
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
        }

    per_customer_lifetime = {}
    for c in CUSTOMERS:
        cid = c["customer_id"]
        recs = [r for r in all_records if r["customer_id"] == cid]
        if not recs:
            continue
        cts = cost_to_serve.get("by_customer", {}).get(cid, {})
        per_customer_lifetime[cid] = {
            "commodity": c["commodity"],
            "segment": c["segment"],
            "acquisition_date": c["acquisition_date"],
            "gross_gbp": sum(r["margin_gbp"] for r in recs),
            "capital_gbp": sum(r["capital_cost_gbp"] for r in recs),
            "net_gbp": sum(r["net_margin_gbp"] for r in recs),
            "cost_to_serve_gbp": cts.get("cost_to_serve_gbp"),
            "net_margin_after_cost_to_serve_gbp": cts.get("net_margin_gbp"),
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
        cost_to_serve_line = (
            f"- Cost to serve (whole portfolio): {_fmt_gbp(data['cost_to_serve_portfolio_gbp'])}, "
            f"net margin after cost to serve: {_fmt_gbp(data['net_margin_after_cost_to_serve_gbp'])}"
        )
    else:
        cost_to_serve_line = f"- Cost to serve (whole portfolio): {NOT_AVAILABLE}"

    return f"""## Executive Summary

This report covers {years[0]}–{years[-1]} ({len(years)} calendar years,
the last partial). The business {outcome}.

- Starting treasury: {_fmt_gbp(data['starting_treasury_gbp'])}
- Final treasury: {_fmt_gbp(data['final_treasury_gbp'])}
  ({_fmt_gbp(data['final_treasury_gbp'] - data['starting_treasury_gbp'])} net change)
- Revenue: {_fmt_gbp(data['total_revenue_gbp'])}
- Gross margin: {_fmt_gbp(data['total_gross_gbp'])}
- Capital costs: {_fmt_gbp(data['total_capital_gbp'])}
- Net margin: {_fmt_gbp(data['total_net_gbp'])}
- Capital cost ratio: {data['total_capital_gbp'] / data['total_gross_gbp']:.1%} of gross
- Net margin as % of revenue: {data['total_net_gbp'] / data['total_revenue_gbp']:.1%}
  (industry benchmark for a retail energy supplier: 2-5%)
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
        f"(actual net {_fmt_gbp(totals['actual_net_gbp'])} vs. naked net "
        f"{_fmt_gbp(totals['naked_net_gbp'])})"
    )


def _customer_book_section(year: str, yd: dict, data: dict) -> str:
    lines = ["**Customer Book**", ""]
    active = yd["active_customer_ids"]
    resi_elec = [c for c in active if c in {"C1", "C2", "C3", "C4"}]
    sme_elec = [c for c in active if c in {"C5", "C6"}]
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
    lines.append(
        "- Losses (churn / home move) during year: " + NOT_AVAILABLE
        + " -- no churn mechanic is applied to the actual customer roster in "
        "the settlement run; 4b's churn/home-move models are point-in-time "
        "risk scores, not roster events."
    )
    if data["avg_clv_gbp"] is not None:
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
    lines.append(f"- Churn risk: how many customers above threshold at year end: {NOT_AVAILABLE}")
    return "\n".join(lines)


def _pricing_margin_section(yd: dict, data: dict) -> str:
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
    cts_values = [
        v["cost_to_serve_gbp"]
        for v in data["per_customer_lifetime"].values()
        if v["cost_to_serve_gbp"] is not None
    ]
    if cts_values:
        lines.append(
            f"- Cost to serve per customer (whole-run total, average "
            f"{_fmt_gbp(_avg(cts_values))}, range "
            f"{_fmt_gbp(min(cts_values))}-{_fmt_gbp(max(cts_values))}):"
        )
        for cid, pcl in sorted(data["per_customer_lifetime"].items()):
            if pcl["cost_to_serve_gbp"] is None:
                continue
            lines.append(
                f"  - {cid}: cost to serve {_fmt_gbp(pcl['cost_to_serve_gbp'])}, "
                f"net margin after cost to serve "
                f"{_fmt_gbp(pcl['net_margin_after_cost_to_serve_gbp'])}"
                + (" -- **net-negative**" if pcl["net_margin_after_cost_to_serve_gbp"] < 0 else "")
            )
    else:
        lines.append(f"- Cost to serve per customer (average and range): {NOT_AVAILABLE}")
        lines.append(f"- Net margin per customer after cost to serve: {NOT_AVAILABLE}")
    return "\n".join(lines)


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

    new_ratio = data["total_capital_gbp"] / data["total_gross_gbp"]
    old_ratio = old_data["total_capital_gbp"] / old_data["total_gross_gbp"]

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
        "**Note:** the figures below come from two *different* simulation "
        "runs (this run vs. the preserved old-model snapshot) — do not "
        "subtract a figure from one run's row from a figure in the other's. "
        f"This run: gross {_fmt_gbp(data['total_gross_gbp'])}, capital "
        f"{_fmt_gbp(data['total_capital_gbp'])}, net "
        f"{_fmt_gbp(data['total_net_gbp'])}. Old-model run: gross "
        f"{_fmt_gbp(old_data['total_gross_gbp'])}, capital "
        f"{_fmt_gbp(old_data['total_capital_gbp'])}, net "
        f"{_fmt_gbp(old_data['total_net_gbp'])}."
    )
    lines.append("")
    lines.append(
        f"- **Capital cost as % of gross margin**: {_fmt_pct(new_ratio)} "
        f"under the new mandate vs. {_fmt_pct(old_ratio)} under the old "
        "reactive model."
    )
    if new_2021 is not None and old_2021 is not None:
        lines.append(
            f"- **2021 net margin**: {_fmt_gbp(new_2021)} under the new "
            f"mandate vs. {_fmt_gbp(old_2021)} under the old reactive model."
        )
    else:
        lines.append(f"- **2021 net margin**: {NOT_AVAILABLE}")

    old_revenue = old_data.get("total_revenue_gbp")
    if old_revenue:
        new_margin_pct = data["total_net_gbp"] / data["total_revenue_gbp"]
        old_margin_pct = old_data["total_net_gbp"] / old_revenue
        lines.append(
            f"- **Net margin as % of revenue**: {_fmt_pct(new_margin_pct)} "
            f"under the new mandate vs. {_fmt_pct(old_margin_pct)} under the "
            "old reactive model (industry benchmark: 2-5%)."
        )
    else:
        lines.append(
            f"- **Net margin as % of revenue**: this run "
            f"{_fmt_pct(data['total_net_gbp'] / data['total_revenue_gbp'])}; "
            f"old-model run {NOT_AVAILABLE} (revenue wasn't captured in that "
            "snapshot)."
        )
    lines.append("")
    lines.append("**Whole-run net margin, three ways:**")
    lines.append("")
    lines.append(f"- Mandate-hedged (actual, this run): {_fmt_gbp(data['total_net_gbp'])}")
    if old_data is not None:
        lines.append(f"- Old reactive model (actual): {_fmt_gbp(old_data['total_net_gbp'])}")
    if new_het is not None:
        lines.append(f"- Fully naked (this run's counterfactual): {_fmt_gbp(new_het['naked_net_gbp'])}")
    if old_het is not None:
        lines.append(f"- Fully naked (old run's counterfactual): {_fmt_gbp(old_het['naked_net_gbp'])}")
    lines.append("")
    lines.append(
        "Comparing the two naked counterfactuals shows what changed in the "
        "underlying weather/price data between runs (LLM non-determinism in "
        "risk-committee responses also shifts these slightly run-to-run); "
        "comparing each model's actual to its own naked figure isolates what "
        "that model's hedging behaviour itself contributed."
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
        f"| Field | Value |",
        f"|-------|-------|",
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
        f"Renewal decisions rolled at each annual renewal point across the simulation window.",
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

    for year in sorted(data["years"]):
        yd = data["years"][year]
        sections.append(f"## {year}\n")
        sections.append(_trading_risk_section(year, yd))
        sections.append("")
        sections.append(_customer_book_section(year, yd, data))
        sections.append("")
        sections.append(_pricing_margin_section(yd, data))
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
        data = _run_and_extract(report_end=report_end)
        args.save_json.parent.mkdir(parents=True, exist_ok=True)
        args.save_json.write_text(json.dumps(data, indent=2))

    report = generate_annual_report(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report)
    print(f"Wrote {args.output} ({len(report)} chars, {len(data['years'])} years)")


if __name__ == "__main__":
    main()
