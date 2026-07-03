#!/usr/bin/env python3
"""Generate site/state/PROJECT_STATE.txt from current dashboard data and CLAUDE.md."""
import json
import re
import datetime as dt
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
CLAUDE_MD = PROJECT / "CLAUDE.md"
DASHBOARD_JSON = PROJECT / "site" / "data" / "dashboard.json"
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"
OUT_PATH = PROJECT / "site" / "state" / "PROJECT_STATE.txt"


def _parse_phase_and_tests():
    try:
        text = CLAUDE_MD.read_text()
        idx = text.find("## Current state")
        if idx < 0:
            return "?", 0
        section = text[idx:]
        best_tests, best_phase = 0, "?"
        for line in section.split("\n"):
            if "COMPLETE" not in line:
                continue
            m_ph = re.search(r"\*\*Phase (\w+) COMPLETE", line)
            m_tc = re.search(r"(\d[\d,]+)\s+total", line)
            if m_ph and m_tc:
                tc = int(m_tc.group(1).replace(",", ""))
                if tc > best_tests:
                    best_tests, best_phase = tc, m_ph.group(1)
        return best_phase, best_tests
    except Exception:
        return "?", 0


def _load_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return {}


def generate():
    now = dt.datetime.now(dt.timezone.utc)
    ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    phase, test_count = _parse_phase_and_tests()
    dash = _load_json(DASHBOARD_JSON)
    run = _load_json(RUN_OUTPUT)
    build = dash.get("build", {})
    fin = dash.get("financial", {})
    ann = fin.get("annual", [])
    net_margin = run.get("total_net_gbp", sum(r.get("net_gbp", 0) for r in ann))
    gross_margin = run.get("total_gross_gbp", 0)
    capital = run.get("total_capital_gbp", 0)
    treasury_start = run.get("starting_treasury_gbp", 0)
    treasury_end = run.get("final_treasury_gbp", 0)
    ev = run.get("enterprise_value_gbp", 0)
    net_cts = run.get("net_margin_after_cost_to_serve_gbp", 0)
    committees = run.get("committee_wake_ups_total", 0)
    bills = run.get("bills_total", 0)
    ret_log = run.get("retention_log", [])
    no_offer_log = run.get("no_offer_churn_log", [])
    churned = run.get("churned_billing_accounts", [])
    offers = len(ret_log)
    retained = sum(1 for e in ret_log if e.get("outcome") == "retained")
    no_offer_churns = len(no_offer_log)
    total_churned = len(churned)
    company_modules = build.get("company_modules", 405)
    sim_date = run.get("run_date", ts[:10])
    lines = [
        "# PROJECT STATE -- Synthetic Enterprise",
        "Generated: " + ts,
        "",
        "## Summary",
        "- Current Phase: " + phase,
        "- Test Suite: {:,} tests passing (unit / fast suite ~10s)".format(test_count),
        "- Company Modules: {}+ Python modules across company/".format(company_modules),
        "- Simulation Window: 2016-2025 (Elexon HH settlement data)",
        "- Architecture: sim/ | company/ | saas/ | site/ (dashboard at poesys.net)",
        "",
        "## Latest Simulation Results (auto-processed {})".format(sim_date[:10] if sim_date else ts[:10]),
        "- Net Margin: GBP{:,.0f} (10-year 2016-2025)".format(net_margin),
        "- Gross Margin: GBP{:,.0f}".format(gross_margin),
        "- Capital at Risk: GBP{:,.0f}".format(capital),
        "- Treasury: GBP{:,.0f} -> GBP{:,.0f}".format(treasury_start, treasury_end),
        "- Enterprise Value: GBP{:,.0f} | Net after CTS: GBP{:,.0f}".format(ev, net_cts),
        "- Risk Committee Interventions: {}".format(committees),
        "- Bills Issued: {:,}".format(int(bills)),
        "- Retention: {}/{} offers accepted | {} no-offer churns | {} total churned".format(
            retained, offers, no_offer_churns, total_churned),
        "",
        "## Key Files (fetchable without JavaScript)",
        "- https://poesys.net/state/PROJECT_STATE.txt -- THIS FILE (auto-generated on every push)",
        "- https://poesys.net/state/customer_sample.json -- per-customer ground truth",
        "- https://poesys.net/shadow/ -- no-JS HTML: Supplier dashboard",
        "- https://poesys.net/shadow/customers/ -- no-JS HTML: Customer portal",
        "- https://poesys.net/shadow/project/ -- no-JS HTML: Project overview",
        "- https://poesys.net/shadow/sim/ -- no-JS HTML: SIM market data",
        "- https://poesys.net/state/billing_ledger.json -- per-customer invoice/payment/arrears ledger",
        "- https://poesys.net/state/population_anchoring.json -- SIM vs Ofgem/DESNZ benchmark validation",
        "- docs/reports/run_output_latest.json -- full run output (JSON)",
        "",
        "## Architecture & Key Rules",
        "- Epistemic Honesty: company layer cannot see SIM internals (Point-in-Time Blindfold)",
        "- Board sections are NOT phases: reporting is a byproduct, not the capability",
        "- Churn model: bill shock YoY + payment behaviour + satisfaction + market year elasticity",
        "",
        "## Key Metrics",
        "- Tests at start (Phase 0): 0 | Tests now: {:,}".format(test_count),
        "- Net margin all-time: GBP{:,.0f} | Crisis survived: 2021-22".format(net_margin),
        "- Retention: {}/{} offers | {} no-offer churns".format(retained, offers, no_offer_churns),
    ]
    content = "\n".join(lines) + "\n"
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(content)
    print("Written: {} (Phase={}, tests={:,})".format(OUT_PATH, phase, test_count))
    return True


if __name__ == "__main__":
    generate()
