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
DOCS_STATUS_PATH = PROJECT / "docs" / "status" / "PROJECT_STATE.txt"


def _parse_phase_and_tests():
    """Return (phase, test_count) for the MOST RECENT phase, not the one with
    the highest test count -- the fast-suite total isn't monotonic (it
    fluctuates with which slow/simulation tests are ignored at write time),
    so picking the max silently regressed the reported phase label to an
    older one whenever a later phase happened to report a smaller count.
    New phases are always prepended at the top of "## Current state"
    (CLAUDE.md phase-close checklist step 5), so the first COMPLETE line is
    the current one."""
    try:
        text = CLAUDE_MD.read_text()
        idx = text.find("## Current state")
        if idx < 0:
            return "?", 0
        section = text[idx:]
        for line in section.split("\n"):
            if "COMPLETE" not in line:
                continue
            m_ph = re.search(r"\*\*Phase (\w+) COMPLETE", line)
            m_tc = re.search(r"(\d[\d,]+)\s+total", line)
            if m_ph and m_tc:
                return m_ph.group(1), int(m_tc.group(1).replace(",", ""))
        return "?", 0
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
        "# ADVISOR: use the github.io URLs below for verification fetches -- poesys.net (Cloudflare",
        "# Pages) has proven persistently stale on the advisor's egress path specifically, independent",
        "# of any CD incident (docs/staging/done/ADVISOR_GITHUBIO_MIRROR*.md). github.io is served",
        "# straight from this repo's docs/ folder on every push -- no separate CDN in the path.",
        "- https://21bcarlisle-arch.github.io/synthetic-enterprise/status/PROJECT_STATE.txt -- THIS FILE (canonical, GitHub Pages)",
        "- https://21bcarlisle-arch.github.io/synthetic-enterprise/shadow/ -- no-JS HTML: Supplier dashboard (GitHub Pages mirror)",
        "- https://21bcarlisle-arch.github.io/synthetic-enterprise/shadow/customers/ -- no-JS HTML: Customer portal (GitHub Pages mirror)",
        "- https://21bcarlisle-arch.github.io/synthetic-enterprise/shadow/supplier/ -- no-JS HTML: Supplier P&L (GitHub Pages mirror)",
        "- https://21bcarlisle-arch.github.io/synthetic-enterprise/shadow/project/ -- no-JS HTML: Project overview (GitHub Pages mirror)",
        "- https://21bcarlisle-arch.github.io/synthetic-enterprise/shadow/sim/ -- no-JS HTML: SIM market data (GitHub Pages mirror)",
        "- https://21bcarlisle-arch.github.io/synthetic-enterprise/state/customer_sample.json -- per-customer ground truth (GitHub Pages mirror)",
        "- https://21bcarlisle-arch.github.io/synthetic-enterprise/state/billing_ledger.json -- per-customer invoice/payment/arrears ledger (GitHub Pages mirror)",
        "- https://21bcarlisle-arch.github.io/synthetic-enterprise/state/population_anchoring.json -- SIM vs Ofgem/DESNZ benchmark validation (GitHub Pages mirror)",
        "- https://21bcarlisle-arch.github.io/synthetic-enterprise/state/sim_data.json -- Elexon SSP settlement data (GitHub Pages mirror)",
        "# Visitor surface (Cloudflare Pages, same generator pass -- not for advisor verification fetches):",
        "- https://poesys.net/state/PROJECT_STATE.txt -- mirror (Cloudflare Pages)",
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
    DOCS_STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_STATUS_PATH.write_text(content)
    print("Written: {} + {} (Phase={}, tests={:,})".format(OUT_PATH, DOCS_STATUS_PATH, phase, test_count))
    return True


if __name__ == "__main__":
    generate()
