"""Phase 10b — Segment portfolio annual report generator.

Reads the structured output of `simulation.run_segments.main()` and produces a
markdown annual report covering the full simulation window, one section per
calendar year, with segment-level headcount trajectory and unit economics.

Unlike annual_report.py (which serves the 9-named-customer model), this module
has no CLV, billing experience, or home-move mechanics — headcount handles all
portfolio dynamics. The added value is unit economics at realistic scale:
margin per customer, smart-meter migration tracking, and per-segment P&L.

CLI: python3 -m saas.reporting.segment_report
     --from-json <path>   load pre-computed run output (skip re-running sim)
     --save-json <path>   save run output for later re-use
     --output <path>      report destination (default: docs/reports/SEGMENT_REPORT.md)
     --end-year <YYYY>    truncate report at year end (for partial windows)
"""

import argparse
import json
from pathlib import Path

from simulation.segments import SEGMENT_BY_ID, SEGMENTS

DEFAULT_REPORT_PATH = Path("docs/reports/SEGMENT_REPORT.md")
DEFAULT_JSON_PATH = Path("docs/reports/run_output_segments_latest.json")

CRISIS_YEARS = {"2021", "2022"}

_SEGMENT_LABELS = {
    "resi_standard": "Resi Standard (elec)",
    "resi_smart": "Resi Smart (elec)",
    "sme_standard": "SME Standard (elec)",
    "sme_smart": "SME Smart (elec)",
    "gas_resi": "Resi Gas",
}


def _year(date_str: str) -> str:
    return date_str[:4]


def _avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _fmt_gbp(v: float) -> str:
    return f"£{v:,.2f}"


def _fmt_pct(v: float | None) -> str:
    return f"{v:.1%}" if v is not None else "n/a"


def extract_segment_data(run_output: dict) -> dict:
    """Reduce run_segments.main() output to a compact, JSON-serialisable dict.

    run_segments output is flat (not nested under 'phase2b' like run_phase4c_on_phase2b).
    """
    all_records = run_output["all_records"]
    committee_wake_ups = run_output.get("committee_wake_ups", [])
    hedge_evolution = run_output.get("hedge_evolution", {})  # {sid: [entries]}
    headcount_history = run_output.get("headcount_history", [])
    final_headcounts = run_output.get("final_headcounts", {})
    fixed_cost_events = run_output.get("fixed_cost_events", [])
    administration_event = run_output.get("administration_event")

    hedge_entries_flat = [
        {**entry, "segment_id": sid}
        for sid, entries in hedge_evolution.items()
        for entry in entries
    ]

    years = sorted({_year(r["settlement_date"]) for r in all_records})

    # Build headcount lookup: {year_str: {sid: headcount}}
    hc_by_year: dict[str, dict[str, int]] = {
        str(snap["year"]): snap["headcounts"]
        for snap in headcount_history
    }

    # Initial headcounts from SEGMENTS definition
    initial_hc = {s.segment_id: s.headcount for s in SEGMENTS}

    yearly: dict[str, dict] = {}
    for year in years:
        yr_records = [r for r in all_records if _year(r["settlement_date"]) == year]
        yr_hc = hc_by_year.get(year, {})

        # Per-segment P&L for this year
        per_segment: dict[str, dict] = {}
        for sid in sorted({r["customer_id"] for r in yr_records}):
            srecs = [r for r in yr_records if r["customer_id"] == sid]
            hc = yr_hc.get(sid)
            seg = SEGMENT_BY_ID.get(sid)
            gross = sum(r["margin_gbp"] for r in srecs)
            capital = sum(r["capital_cost_gbp"] for r in srecs)
            net = sum(r["net_margin_gbp"] for r in srecs)
            revenue = sum(r.get("revenue_gbp", 0.0) for r in srecs)
            per_segment[sid] = {
                "headcount": hc,
                "commodity": seg.commodity if seg else None,
                "gross_gbp": gross,
                "capital_gbp": capital,
                "net_gbp": net,
                "revenue_gbp": revenue,
                "net_per_customer_gbp": net / hc if hc else None,
                "gross_per_customer_gbp": gross / hc if hc else None,
            }

        # Smart meter migration this year
        smart_upgrades: dict[str, int] = {}
        for snap in headcount_history:
            if str(snap["year"]) == year:
                for sid in ("resi_smart", "sme_smart"):
                    prev_snap = next(
                        (s for s in headcount_history if str(s["year"]) == str(int(year) - 1)),
                        None,
                    )
                    if prev_snap:
                        prev_hc = prev_snap["headcounts"].get(sid, 0)
                        curr_hc = snap["headcounts"].get(sid, 0)
                        smart_upgrades[sid] = max(0, curr_hc - prev_hc)

        treasury_series = [
            r["treasury_cash_balance_gbp"]
            for r in sorted(yr_records, key=lambda r: (r["settlement_date"], r.get("settlement_period", 0)))
        ]
        treasury_end = treasury_series[-1] if treasury_series else None

        wake_ups = [w for w in committee_wake_ups if _year(w["settlement_date"]) == year]

        yr_hedge_entries = [e for e in hedge_entries_flat if _year(e["term_start"]) == year]
        hedge_effectiveness = {
            "actual_net_gbp": sum(e["actual_net"] for e in yr_hedge_entries),
            "naked_net_gbp": sum(e["naked_net"] for e in yr_hedge_entries),
            "hedging_value_add_gbp": sum(e["actual_net"] - e["naked_net"] for e in yr_hedge_entries),
        }

        yr_fixed_cost = sum(
            -e["amount_gbp"] for e in fixed_cost_events if e["timestamp"][:4] == year
        )

        total_hc = sum(v for v in yr_hc.values()) if yr_hc else None
        gross_yr = sum(r["margin_gbp"] for r in yr_records)
        net_yr = sum(r["net_margin_gbp"] for r in yr_records)

        yearly[year] = {
            "gross_gbp": gross_yr,
            "capital_gbp": sum(r["capital_cost_gbp"] for r in yr_records),
            "net_gbp": net_yr,
            "revenue_gbp": sum(r.get("revenue_gbp", 0.0) for r in yr_records),
            "treasury_end_gbp": treasury_end,
            "per_segment": per_segment,
            "committee_wake_ups": wake_ups,
            "hedge_effectiveness": hedge_effectiveness,
            "fixed_cost_gbp": yr_fixed_cost,
            "smart_upgrades": smart_upgrades,
            "headcounts": yr_hc,
            "total_headcount": total_hc,
            "net_per_customer_gbp": net_yr / total_hc if total_hc else None,
        }

    # Whole-window totals
    total_gross = sum(r["margin_gbp"] for r in all_records)
    total_capital = sum(r["capital_cost_gbp"] for r in all_records)
    total_net = sum(r["net_margin_gbp"] for r in all_records)
    total_revenue = sum(r.get("revenue_gbp", 0.0) for r in all_records)
    total_fixed_cost = sum(-e["amount_gbp"] for e in fixed_cost_events)

    hedge_total = (
        {
            "actual_net_gbp": sum(e["actual_net"] for e in hedge_entries_flat),
            "naked_net_gbp": sum(e["naked_net"] for e in hedge_entries_flat),
            "hedging_value_add_gbp": sum(e["actual_net"] - e["naked_net"] for e in hedge_entries_flat),
        }
        if hedge_entries_flat else None
    )

    # Per-segment lifetime P&L
    per_segment_lifetime: dict[str, dict] = {}
    for seg in SEGMENTS:
        sid = seg.segment_id
        recs = [r for r in all_records if r["customer_id"] == sid]
        if not recs:
            continue
        gross = sum(r["margin_gbp"] for r in recs)
        capital = sum(r["capital_cost_gbp"] for r in recs)
        net = sum(r["net_margin_gbp"] for r in recs)
        final_hc = final_headcounts.get(sid, seg.headcount)
        avg_hc = _avg([
            yearly[yr]["per_segment"].get(sid, {}).get("headcount") or 0
            for yr in years
        ])
        per_segment_lifetime[sid] = {
            "commodity": seg.commodity,
            "initial_headcount": seg.headcount,
            "final_headcount": final_hc,
            "avg_headcount": avg_hc,
            "gross_gbp": gross,
            "capital_gbp": capital,
            "net_gbp": net,
        }

    return {
        "starting_treasury_gbp": run_output["starting_treasury"],
        "final_treasury_gbp": run_output["final_treasury"],
        "total_gross_gbp": total_gross,
        "total_capital_gbp": total_capital,
        "total_net_gbp": total_net,
        "total_revenue_gbp": total_revenue,
        "total_fixed_cost_gbp": total_fixed_cost,
        "administration_event": administration_event,
        "committee_wake_ups_total": len(committee_wake_ups),
        "hedge_effectiveness_total": hedge_total,
        "initial_headcounts": initial_hc,
        "final_headcounts": final_headcounts,
        "headcount_history": headcount_history,
        "per_segment_lifetime": per_segment_lifetime,
        "years": yearly,
    }


def _headcount_table(data: dict) -> str:
    years = sorted(data["years"])
    segs = [s.segment_id for s in SEGMENTS]
    header = "| Segment | " + " | ".join(years) + " |"
    sep = "|---------|" + "--------|" * len(years)
    rows = []
    for sid in segs:
        label = _SEGMENT_LABELS.get(sid, sid)
        initial = data["initial_headcounts"].get(sid, 0)
        cells = []
        for yr in years:
            hc = data["years"][yr]["per_segment"].get(sid, {}).get("headcount")
            cells.append(str(hc) if hc is not None else str(initial))
        rows.append(f"| {label} | " + " | ".join(cells) + " |")

    # Portfolio total row
    totals = []
    for yr in years:
        t = data["years"][yr].get("total_headcount")
        totals.append(str(t) if t is not None else "?")
    rows.append("| **Portfolio** | " + " | ".join(f"**{t}**" for t in totals) + " |")

    return "\n".join([header, sep] + rows)


def _per_segment_pnl_table(data: dict) -> str:
    lines = [
        "| Segment | Gross £ | Capital £ | Net £ | Init HC | Final HC | Net/cust £ |",
        "|---------|--------:|----------:|------:|--------:|---------:|-----------:|",
    ]
    for seg in SEGMENTS:
        sid = seg.segment_id
        psl = data["per_segment_lifetime"].get(sid)
        if not psl:
            continue
        label = _SEGMENT_LABELS.get(sid, sid)
        net_per = (
            f"{psl['net_gbp'] / psl['avg_headcount']:.2f}" if psl.get("avg_headcount") else "n/a"
        )
        lines.append(
            f"| {label} | {psl['gross_gbp']:,.2f} | {psl['capital_gbp']:,.2f} | "
            f"{psl['net_gbp']:,.2f} | {psl['initial_headcount']} | "
            f"{psl['final_headcount']} | {net_per} |"
        )
    return "\n".join(lines)


def _year_section(year: str, yd: dict, data: dict) -> str:
    flag = " *(crisis year)*" if year in CRISIS_YEARS else ""
    gross_pct = yd["net_gbp"] / yd["gross_gbp"] if yd["gross_gbp"] else None
    fixed = yd.get("fixed_cost_gbp", 0.0)
    net_after_fixed = yd["net_gbp"] - fixed

    heff = yd.get("hedge_effectiveness", {})
    add = heff.get("hedging_value_add_gbp", 0.0)
    hedge_line = (
        f"hedging added {_fmt_gbp(add)}" if add >= 0
        else f"hedging cost {_fmt_gbp(-add)}"
    ) if heff.get("actual_net_gbp") is not None else "n/a"

    # Per-segment P&L table for this year
    seg_rows = ["| Segment | HC | Gross £ | Capital £ | Net £ | Net/cust £ |",
                "|---------|---:|--------:|----------:|------:|-----------:|"]
    for seg in SEGMENTS:
        sid = seg.segment_id
        ps = yd["per_segment"].get(sid)
        if not ps:
            continue
        label = _SEGMENT_LABELS.get(sid, sid)
        hc = ps.get("headcount", "?")
        npc = f"{ps['net_per_customer_gbp']:.2f}" if ps.get("net_per_customer_gbp") is not None else "n/a"
        seg_rows.append(
            f"| {label} | {hc} | {ps['gross_gbp']:,.2f} | {ps['capital_gbp']:,.2f} | "
            f"{ps['net_gbp']:,.2f} | {npc} |"
        )
    seg_table = "\n".join(seg_rows)

    # Smart meter upgrade note
    upgrades = yd.get("smart_upgrades", {})
    upgrade_parts = []
    for sid in ("resi_smart", "sme_smart"):
        n = upgrades.get(sid, 0)
        if n:
            label = "Resi" if "resi" in sid else "SME"
            upgrade_parts.append(f"{n} {label} upgrade(s)")
    upgrade_note = (
        "Smart upgrades this year: " + ", ".join(upgrade_parts)
        if upgrade_parts else "No net smart-meter migration this year."
    )

    return f"""### {year}{flag}

**Portfolio P&L**
- Revenue: {_fmt_gbp(yd['revenue_gbp'])}
- Gross margin: {_fmt_gbp(yd['gross_gbp'])}
- Capital costs: ({_fmt_gbp(yd['capital_gbp'])})
- Net margin: {_fmt_gbp(yd['net_gbp'])} ({_fmt_pct(gross_pct)} of gross)
- Fixed overhead: ({_fmt_gbp(fixed)})
- Net after overhead: {_fmt_gbp(net_after_fixed)}
- Treasury at year end: {_fmt_gbp(yd['treasury_end_gbp']) if yd.get('treasury_end_gbp') is not None else 'n/a'}
- Risk committee wake-ups: {len(yd['committee_wake_ups'])}
- Hedge effectiveness: {hedge_line}
- Net per customer: {_fmt_gbp(yd['net_per_customer_gbp']) if yd.get('net_per_customer_gbp') is not None else 'n/a'}

{upgrade_note}

**Per-segment P&L**

{seg_table}

"""


def generate_segment_report(data: dict, end_year: str | None = None) -> str:
    years = sorted(data["years"])
    if end_year:
        years = [y for y in years if y <= end_year]

    outcome = (
        "ADMINISTRATION on " + data["administration_event"]["date"]
        if data["administration_event"]
        else "survived the full window"
    )

    heff = data.get("hedge_effectiveness_total")
    if heff:
        add = heff["hedging_value_add_gbp"]
        verb = "added" if add >= 0 else "cost"
        hedge_total_line = (
            f"hedging {verb} {_fmt_gbp(abs(add))} vs. a fully unhedged book "
            f"(actual net {_fmt_gbp(heff['actual_net_gbp'])} vs. naked net "
            f"{_fmt_gbp(heff['naked_net_gbp'])})"
        )
    else:
        hedge_total_line = "n/a"

    total_net = data["total_net_gbp"]
    total_gross = data["total_gross_gbp"]
    total_capital = data["total_capital_gbp"]
    total_revenue = data["total_revenue_gbp"]
    total_fixed = data.get("total_fixed_cost_gbp", 0.0)
    net_after_fixed = total_net - total_fixed

    cap_ratio = f"{total_capital / total_gross:.1%}" if total_gross else "n/a"
    net_pct = f"{total_net / total_revenue:.1%}" if total_revenue else "n/a"

    # Final portfolio headcount
    final_total_hc = sum(data["final_headcounts"].values()) if data["final_headcounts"] else None
    initial_total_hc = sum(data["initial_headcounts"].values())

    year_sections = "\n".join(_year_section(yr, data["years"][yr], data) for yr in years)

    return f"""# Segment Portfolio Annual Report
## {years[0]}–{years[-1]}

*Generated by Phase 10a segment customer model — {initial_total_hc} initial customers across 5 segments.*

---

## Executive Summary

This report covers {years[0]}–{years[-1]} ({len(years)} calendar years, the last partial).
The business {outcome}.

**Portfolio economics**
- Starting treasury: {_fmt_gbp(data['starting_treasury_gbp'])}
- Final treasury: {_fmt_gbp(data['final_treasury_gbp'])}
  ({_fmt_gbp(data['final_treasury_gbp'] - data['starting_treasury_gbp'])} net change)
- Gross margin (whole window): {_fmt_gbp(total_gross)}
- Capital costs: ({_fmt_gbp(total_capital)}) — {cap_ratio} of gross
- Net margin: {_fmt_gbp(total_net)} — {net_pct} of revenue
- Fixed overhead (whole window): ({_fmt_gbp(total_fixed)})
- Net after overhead: {_fmt_gbp(net_after_fixed)}
- Risk committee (Context Handshake) interventions: {data['committee_wake_ups_total']}
- Hedge effectiveness (whole window): {hedge_total_line}

**Customer book**
- Initial portfolio: {initial_total_hc} customers
- Final portfolio: {final_total_hc if final_total_hc is not None else 'n/a'} customers

---

## Headcount Trajectory

{_headcount_table(data)}

---

## Lifetime Segment Economics

{_per_segment_pnl_table(data)}

*Net/cust £ = whole-window net margin ÷ average annual headcount.*

---

## Year-by-Year Detail

{year_sections}
"""


def _save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Run output saved → {path}")


def _load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate segment portfolio annual report")
    parser.add_argument("--from-json", metavar="PATH", help="load pre-computed run output")
    parser.add_argument("--save-json", metavar="PATH", help="save run output for re-use")
    parser.add_argument("--output", metavar="PATH", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--end-year", metavar="YYYY", help="truncate report at this year")
    args = parser.parse_args()

    if args.from_json:
        run_output = _load_json(Path(args.from_json))
        print(f"Loaded run output from {args.from_json}")
    else:
        from simulation.run_segments import main as run_segments
        print("Running segment simulation…")
        run_output = run_segments()

    if args.save_json:
        _save_json(run_output, Path(args.save_json))

    data = extract_segment_data(run_output)
    report = generate_segment_report(data, end_year=args.end_year)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report)
    print(f"Segment report written → {out_path}")


if __name__ == "__main__":
    main()
