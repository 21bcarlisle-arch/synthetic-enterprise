#!/usr/bin/env python3
"""Generate site/state/PROJECT_STATE.txt from current dashboard data and CLAUDE.md."""
import datetime as dt
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DASHBOARD_JSON = PROJECT / "site" / "data" / "dashboard.json"
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"
OUT_PATH = PROJECT / "site" / "state" / "PROJECT_STATE.txt"
DOCS_STATUS_PATH = PROJECT / "docs" / "status" / "PROJECT_STATE.txt"


def _parse_phase_and_tests():
    """(phase, test_count) from CLAUDE.md -- DELEGATED, because there must be exactly one parser.

    THIS FUNCTION USED TO BE A SECOND IMPLEMENTATION and it is why a startup anchor published
    `Current Phase: ?` and `Test Suite: 0 tests passing` for eight days (2026-08-28 to 2026-09-05,
    found from the director's console after another session's startup read the published mirror and
    took the figures as current).

    The mechanism, exactly: it located CLAUDE.md's build stamp by `text.find("## Current state")`
    and returned `("?", 0)` when that section was absent. The 2026-08-28 CLAUDE.md rewrite removed
    the section. Nothing noticed, because the fallback is a well-formed pair that formats cleanly.

    Its twin `generate_dashboard_data._derive_build_from_claude_md` ALREADY HELD THE REPAIR -- it
    degrades to scanning the whole document (`section = text if idx < 0 else text[idx:]`) with a
    comment saying it exists "so that a future rewrite cannot break the stamp merely by renaming a
    section". One rule, two implementations, repaired in one and still live in the other: CLAUDE.md
    names this shape as the seat's own recurring defect and the VAT rule as its evidence. Guarding
    the divergence would have left two parsers to drift; this removes the second one.

    Returns `(None, None)` rather than `("?", 0)` when CLAUDE.md cannot be parsed. A `0` test count
    is indistinguishable from a measurement of nothing once it is rendered, and it rendered for
    eight days. Callers MUST handle None -- `generate()` prints "unavailable" and names the reason,
    which is a result a reader can act on in a way that `0` is not.
    """
    try:
        # Lazy: the twin lives in a module that imports `company.*` at load time, and this module
        # is itself imported by `generate_phases_json`. Deferring keeps that edge off import.
        from tools.generate_dashboard_data import _derive_build_from_claude_md
        return _derive_build_from_claude_md()
    except Exception:
        return None, None


def _load_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return {}


def generate():
    now = dt.datetime.now(dt.timezone.utc)
    ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    phase, test_count = _parse_phase_and_tests()
    # NEVER render an unavailable measurement as a number. The eight-day `0 tests passing` on the
    # published mirror was not a wrong figure a reader could argue with -- it was a missing figure
    # wearing a measurement's formatting, and it read as a catastrophic regression.
    #
    # The wording says "not stated in CLAUDE.md" rather than naming a parse failure, because that
    # is the one claim true in every branch -- an unreadable file, a missing figure and a dropped
    # convention all leave CLAUDE.md not stating it, and only the last is what actually happened
    # here (the 2026-08-28 rewrite dropped phase lettering entirely, so `phase` is legitimately
    # absent and will stay absent). A refusal that names a reason it cannot support is how the
    # refusal itself goes unexamined.
    _ABSENT = "not stated in CLAUDE.md"
    phase_str = phase if phase else _ABSENT
    tests_str = ("{:,} tests passing (unit / fast suite ~10s)".format(test_count)
                 if test_count else _ABSENT)
    tests_now_str = "{:,}".format(test_count) if test_count else _ABSENT
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
        "- Current Phase: " + phase_str,
        "- Test Suite: " + tests_str,
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
        "- Tests at start (Phase 0): 0 | Tests now: " + tests_now_str,
        "- Net margin all-time: GBP{:,.0f} | Crisis survived: 2021-22".format(net_margin),
        "- Retention: {}/{} offers | {} no-offer churns".format(retained, offers, no_offer_churns),
    ]
    content = "\n".join(lines) + "\n"
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(content)
    DOCS_STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_STATUS_PATH.write_text(content)
    print("Written: {} + {} (Phase={}, tests={})".format(
        OUT_PATH, DOCS_STATUS_PATH, phase_str, tests_now_str))
    return True


if __name__ == "__main__":
    generate()
