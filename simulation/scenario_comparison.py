"""Phase 38a: Scenario comparison runner.

Runs all (or selected) forward scenarios and produces a side-by-side comparison
of key financial KPIs. Useful for understanding which scenario is worst-case
for the company's net margin, treasury position, and customer retention.

Usage:
    from simulation.scenario_comparison import run_scenario_comparison, format_comparison_table
    comparison = run_scenario_comparison(year_from=2026, year_to=2028)
    print(format_comparison_table(comparison))
"""

from __future__ import annotations

from sim.scenario.bimodal_generator import SCENARIOS as ELEC_SCENARIOS


def extract_scenario_kpis(result: dict, scenario_name: str) -> dict:
    """Extract key financial KPIs from a single scenario run result.

    Returns a dict with:
        scenario_name: str
        years_summary: dict[str, dict] — year → {net_margin_gbp, treasury_gbp, active_customers}
        total_churn: int
        total_net_margin_gbp: float
        final_treasury_gbp: float | None
        retention_events: int
    """
    years_data = result.get("years", {})
    customer_events = result.get("customer_events", [])
    retention_log = result.get("retention_log", [])

    years_summary: dict[str, dict] = {}
    total_net_margin = 0.0

    for year, yd in sorted(years_data.items()):
        net_margin = yd.get("net_margin_gbp", 0.0)
        treasury = yd.get("treasury_end_gbp", yd.get("treasury_gbp"))
        active = len(yd.get("active_customer_ids", []))
        years_summary[year] = {
            "net_margin_gbp": round(net_margin, 2),
            "treasury_gbp": round(treasury, 2) if treasury is not None else None,
            "active_customers": active,
        }
        total_net_margin += net_margin

    # Count churns from customer_events
    churn_count = sum(1 for e in customer_events if e.get("event_type") == "churned")

    # Final treasury
    final_treasury = None
    if years_summary:
        last_year = max(years_summary.keys())
        final_treasury = years_summary[last_year].get("treasury_gbp")

    return {
        "scenario_name": scenario_name,
        "years_summary": years_summary,
        "total_churn": churn_count,
        "total_net_margin_gbp": round(total_net_margin, 2),
        "final_treasury_gbp": final_treasury,
        "retention_events": len(retention_log),
    }


def format_comparison_table(comparison: list[dict]) -> str:
    """Format a list of scenario KPI dicts as a markdown table.

    comparison: list of dicts from extract_scenario_kpis() (one per scenario).

    Returns a markdown string with:
    - Summary table: Scenario | Net Margin | Final Treasury | Total Churn | Retention Events
    - Year-by-year net margin comparison (scenarios as columns)
    """
    if not comparison:
        return ""

    lines = [
        "## Scenario Comparison",
        "",
        "### Summary by Scenario",
        "",
        "| Scenario | Total Net Margin | Final Treasury | Churns | Retention Events |",
        "|----------|-----------------|----------------|--------|-----------------|",
    ]

    for sc in comparison:
        margin = sc["total_net_margin_gbp"]
        treasury = sc["final_treasury_gbp"]
        margin_str = f"£{margin:+,.0f}"
        treasury_str = f"£{treasury:,.0f}" if treasury is not None else "—"
        lines.append(
            f"| {sc['scenario_name']} | {margin_str} | {treasury_str}"
            f" | {sc['total_churn']} | {sc['retention_events']} |"
        )

    # Year-by-year net margin comparison
    all_years = sorted({yr for sc in comparison for yr in sc["years_summary"]})
    if all_years:
        lines += [
            "",
            "### Net Margin by Year (£)",
            "",
        ]
        header = "| Year | " + " | ".join(sc["scenario_name"] for sc in comparison) + " |"
        separator = "|------|" + "------|" * len(comparison)
        lines += [header, separator]

        for yr in all_years:
            row_parts = [yr]
            for sc in comparison:
                margin = sc["years_summary"].get(yr, {}).get("net_margin_gbp")
                row_parts.append(f"£{margin:+,.0f}" if margin is not None else "—")
            lines.append("| " + " | ".join(row_parts) + " |")

    lines.append("")
    return "\n".join(lines)


def run_scenario_comparison(
    scenarios: list[str] | None = None,
    year_from: int = 2026,
    year_to: int = 2028,
    seed: str | None = None,
) -> list[dict]:
    """Run all (or selected) forward scenarios and return a comparison list.

    scenarios: list of scenario names to run. Defaults to all 5 ELEC_SCENARIOS.
    year_from, year_to: synthetic price range for each run.
    seed: deterministic seed. Defaults to "comparison_{year_from}_{year_to}".

    Returns a list of KPI dicts, one per scenario, sorted by total_net_margin_gbp
    descending (best-case first).

    WARNING: this runs `main()` once per scenario — each call takes ~30-60 seconds.
    A 5-scenario comparison at year_from=2026, year_to=2028 takes ~3-5 minutes.
    Run interactively or as a background task, not as a unit test.
    """
    from simulation.run_scenario import run_forward_scenario

    if scenarios is None:
        scenarios = sorted(ELEC_SCENARIOS.keys())

    _seed = seed or f"comparison_{year_from}_{year_to}"
    results = []

    for sc_name in scenarios:
        print(f"\n[Scenario comparison] Running: {sc_name!r} ({year_from}-{year_to})")
        result = run_forward_scenario(
            scenario=sc_name,
            year_from=year_from,
            year_to=year_to,
            seed=_seed,
        )
        kpis = extract_scenario_kpis(result, sc_name)
        results.append(kpis)
        print(f"  Net margin: £{kpis['total_net_margin_gbp']:+,.0f} | "
              f"Treasury: £{kpis['final_treasury_gbp']:,.0f} | "
              f"Churns: {kpis['total_churn']}")

    return sorted(results, key=lambda x: -(x["total_net_margin_gbp"] or 0))
