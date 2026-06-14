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

Not-yet-available metrics (CLV, churn risk, home-move win rate, enterprise
value, cost to serve, VaR ratios, treasury drawdown events) are not part of
`run_phase4c_on_phase2b`'s output -- they come from
`simulation/run_phase4b_on_phase2b.py` (4b) or aren't persisted at all yet.
Per the "do not invent numbers" constraint, every such field is rendered as
an explicit "Not available in current run output" note rather than an
estimate. See `docs/reports/REPORTING_BACKLOG.md` for the integration work
that would close each gap.
"""

import argparse
import json
from pathlib import Path

from saas.customers import CUSTOMERS
from simulation.run_phase4c_on_phase2b import main as run_phase4c_on_phase2b

DEFAULT_REPORT_DATA_PATH = Path("docs/observability/phase4c_report_data.json")
DEFAULT_REPORT_PATH = Path("docs/reports/ANNUAL_REPORT.md")

CRISIS_YEARS = {"2021", "2022"}

NOT_AVAILABLE = "Not available in current run output (see REPORTING_BACKLOG.md)"


def _year(date_str: str) -> str:
    return date_str[:4]


def _avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


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

    years = sorted({_year(r["settlement_date"]) for r in all_records})

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

        yearly[year] = {
            "gross_gbp": sum(r["margin_gbp"] for r in yr_records),
            "capital_gbp": sum(r["capital_cost_gbp"] for r in yr_records),
            "net_gbp": sum(r["net_margin_gbp"] for r in yr_records),
            "treasury_end_gbp": treasury_end,
            "commodity_split": commodity_split,
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
        }

    per_customer_lifetime = {}
    for c in CUSTOMERS:
        cid = c["customer_id"]
        recs = [r for r in all_records if r["customer_id"] == cid]
        if not recs:
            continue
        per_customer_lifetime[cid] = {
            "commodity": c["commodity"],
            "segment": c["segment"],
            "acquisition_date": c["acquisition_date"],
            "gross_gbp": sum(r["margin_gbp"] for r in recs),
            "capital_gbp": sum(r["capital_cost_gbp"] for r in recs),
            "net_gbp": sum(r["net_margin_gbp"] for r in recs),
        }

    return {
        "starting_treasury_gbp": phase2b["starting_treasury"],
        "final_treasury_gbp": phase2b["final_treasury"],
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

    return f"""## Executive Summary

This report covers {years[0]}–{years[-1]} ({len(years)} calendar years,
the last partial). The business {outcome}.

- Starting treasury: {_fmt_gbp(data['starting_treasury_gbp'])}
- Final treasury: {_fmt_gbp(data['final_treasury_gbp'])}
  ({_fmt_gbp(data['final_treasury_gbp'] - data['starting_treasury_gbp'])} net change)
- Gross margin: {_fmt_gbp(data['total_gross_gbp'])}
- Capital costs: {_fmt_gbp(data['total_capital_gbp'])}
- Net margin: {_fmt_gbp(data['total_net_gbp'])}
- Capital cost ratio: {data['total_capital_gbp'] / data['total_gross_gbp']:.1%} of gross
- Risk committee (Context Handshake) interventions: {data['committee_wake_ups_total']}
- Bills issued: {data['bills_total']}, average clarity {data['avg_clarity_total']:.3f},
  service quality score {data['service_quality_score']:.3f}

{chr(10).join(crisis_lines) if crisis_lines else "No crisis years in this window."}

**Enterprise value, CLV, churn risk, and cost-to-serve figures are not
included** -- they are produced by a separate run
(`simulation/run_phase4b_on_phase2b.py`) not yet integrated into this
report's data source. See REPORTING_BACKLOG.md.
"""


def _customer_book_section(year: str, yd: dict) -> str:
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


def _pricing_margin_section(yd: dict) -> str:
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
        lines.append(f"  - {wu['settlement_date']}: treasury {_fmt_gbp(wu['treasury_gbp'])}, {adj}")
    lines.append(f"- VaR ratio (current vs stressed floor): {NOT_AVAILABLE}")
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
    lines.append(f"- Treasury drawdown events (>10% threshold): {NOT_AVAILABLE}")
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


def generate_annual_report(data: dict) -> str:
    """Build the full markdown annual report from `extract_report_data()`'s
    output."""
    sections = [
        "# Annual Report — The Synthetic Enterprise\n",
        _executive_summary(data),
    ]

    for year in sorted(data["years"]):
        yd = data["years"][year]
        sections.append(f"## {year}\n")
        sections.append(_trading_risk_section(year, yd))
        sections.append("")
        sections.append(_customer_book_section(year, yd))
        sections.append("")
        sections.append(_pricing_margin_section(yd))
        sections.append("")
        sections.append(_portfolio_health_section(year, yd, data))
        sections.append("")
        sections.append(_year_narrative(year, yd))
        sections.append("")

    return "\n".join(sections)


def _run_and_extract() -> dict:
    run_output = run_phase4c_on_phase2b()
    return extract_report_data(run_output)


def main() -> None:
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
    args = parser.parse_args()

    if args.from_json:
        data = json.loads(args.from_json.read_text())
    elif DEFAULT_REPORT_DATA_PATH.exists() and args.save_json == DEFAULT_REPORT_DATA_PATH:
        data = json.loads(DEFAULT_REPORT_DATA_PATH.read_text())
    else:
        data = _run_and_extract()
        args.save_json.parent.mkdir(parents=True, exist_ok=True)
        args.save_json.write_text(json.dumps(data, indent=2))

    report = generate_annual_report(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report)
    print(f"Wrote {args.output} ({len(report)} chars, {len(data['years'])} years)")


if __name__ == "__main__":
    main()
