#!/usr/bin/env python3
"""
Generate site/data/dashboard.json from the latest sim run output + Elexon SSP cache.
Called by process_run_complete.py after every full sim run, or manually:
  python3 tools/generate_dashboard_data.py [path/to/run_output.json]
"""
import json
import math
import operator
import random
import re
import statistics
import subprocess
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

from company.analytics.retention_deferral_economics import (
    compute_realized_deferrals, serial_saver_summary,
)
from company.trading.hedge_decision import VAR_REVENUE_LIMIT

PROJECT = Path(__file__).resolve().parent.parent
SSP_CACHE = PROJECT / "sim" / "cache" / "elexon_ssp_full.json"
OUTPUT_PATH = PROJECT / "site" / "data" / "dashboard.json"
# SITE_EH3_figure_reconciliation_and_periods (MAJOR-6): the sim's real
# settlement window, read so a year's period COVERAGE is computed from the
# data, never hardcoded ("2025 is partial"). Same file site/world/
# generate_world_data.py already reads for the same purpose.
SIM_DATA_PATH = PROJECT / "site" / "data" / "sim_data.json"

# THE TWO-ARM DIRECT-DEBIT COMPARISON. The measurement is expensive (it rebuilds
# both DD books over a whole run's issued bills), so the publisher READS the
# committed artefact rather than re-running it -- `python3 -m tools.dd_opening_arms
# --json <this path> --publish <the feed>` is what refreshes it. The feed is written
# here, on the publish path, so the block a reader meets and the block this generator
# computed cannot be two different things.
DD_ARMS_ARTEFACT = PROJECT / "docs" / "reports" / "dd_opening_arms.json"
DD_ARMS_FEED = PROJECT / "site" / "data" / "dd_opening_arms.json"

RUN_INSIGHTS_PATH = PROJECT / "docs" / "observability" / "run_insights.json"
RUN_HISTORY_PATH = PROJECT / "docs" / "observability" / "run_history.json"
BUILD_INFO_PATH = PROJECT / "docs" / "observability" / "build_info.json"

# Fallback only -- canonical phase/test-count values live in build_info.json,
# updated at phase close (CLAUDE.md phase-close checklist step 1) so this page
# never bakes in a stale phase/test-count label.
_BUILD_PHASE = "OL"
_BUILD_TEST_COUNT = 15148


def _git_head():
    """Real HEAD SHA, or None if git cannot answer. Returning None (never a
    guess) is what lets the caller publish the honest string "unknown" instead of
    a plausible-looking fake -- an unavailable provenance lookup is a FAILED
    lookup, not a licence to invent one (R15 fail-silent)."""
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def _resolve_book():
    """Resolve the customer book through the single ``live_population()`` seam.

    Generator draw-wiring (PRODUCT-FIRST item 2, report-lookup generator #2):
    BYTE-IDENTICAL to the static ``CUSTOMERS`` literal while the
    director-reserved ``SE_DRAW_POPULATION`` flag is off (the seam returns
    ``list(CUSTOMERS)``); additively carries the SYN acquisition cohort when
    the flag is on. Extracted so the wiring is R15-testable both ways
    (tests/tools/test_generate_dashboard_data_population_seam.py). The seam
    omits the hidden ground-truth ``cohort`` by construction (epistemic wall).

    HONEST SCOPE (asserted, not hidden): this replaces ONLY the two sites in
    this module that read the ``CUSTOMERS`` acquisition literal directly as a
    list (``extract_customers`` tariff map, ``extract_nudge_discovery`` lift
    table). The ``get_customer(cid)`` lookups in ``extract_opex_ledger`` /
    ``_resi_household_ids_from_active`` are deliberately NOT routed here: that
    helper unions ``CUSTOMERS + SUCCESSOR_CUSTOMERS + ACQUIRED_CUSTOMERS``, so
    routing it through ``live_population()`` (a CUSTOMERS-only + SYN book)
    would DROP the successor/acquired records — the opposite of byte-identical.
    Composing the SYN cohort into that wider union is a separate follow-on.
    """
    from simulation.live_population import live_population
    return live_population()


def count_company_modules():
    """Live count of company/*.py modules -- never manually maintained.

    build_info.json's company_modules field drifted stale for 5+ consecutive
    phases (RF-RN) because the phase-close checklist step that updates it kept
    getting skipped. Since this number is mechanically derivable (unlike
    phase/test_count, which track git/pytest history), computing it fresh here
    removes the manual-update step -- and the drift -- entirely.
    """
    company_dir = PROJECT / "company"
    if not company_dir.exists():
        return 0
    return sum(
        1 for p in company_dir.rglob("*.py")
        if "__pycache__" not in p.parts and not p.name.startswith("test_")
    )


def _derive_build_from_claude_md():
    """Mechanically derive (phase, test_count) from CLAUDE.md's Current-state
    section -- the doc updated at every phase close.

    WEBSITE_FRESHNESS_AND_DEDUP.md item 1 (2026-07-08): build_info.json was a
    manually-maintained stamp that drifted stale (dashboard showed "Phase RE /
    15740 tests" while the project was at RX / 15,996). Rather than one more
    hand-edited number, derive it from the one doc that is always current --
    the same live-computation treatment count_company_modules() already gets.

    2026-07-10, THIRD recurrence of the same documentation-convention-drift
    class this session (R10: close the class, not the instance): this
    function previously required a literal "Phase XY (COMPLETE|CLOSED...)"
    tag to appear in CLAUDE.md at all, but the newest Current-state entries
    (this session's own) are bare descriptive titles with no phase-letter
    code -- `_load_build_info()`'s `if phase and test_count` gate then
    silently fell through to the (stale, manually-maintained) build_info.json
    fallback the moment the newest entries lost that tag, exactly the
    staleness class this mechanism exists to prevent. Test count -- the part
    that actually matters functionally (`phase` is never displayed anywhere
    on the live site, only `test_count` is consumed) -- is now extracted
    independently of whether a phase code is present at all. `phase` is
    still returned as a best-effort label when a code IS found nearby (kept
    for backward-compat / cosmetic use), but is no longer required for
    test_count to be trusted.

    Returns (phase, test_count), either of which may be None if CLAUDE.md
    can't be parsed at all or no test-count figure is found in the
    Current-state section, so callers fall back to build_info.json then the
    module constants for whichever half is missing."""
    claude_md = PROJECT / "CLAUDE.md"
    if not claude_md.exists():
        return None, None
    try:
        text = claude_md.read_text()
    except OSError:
        return None, None
    # KEYED TO THE FIGURE, NOT TO A HEADING (2026-08-28). This used to anchor on the literal
    # "## Current state" and return (None, None) if that heading was absent -- so the director's
    # CLAUDE.md rewrite, which keeps the build figure but drops that section name, silently
    # unstamped the live site. The heading is a structure that can move; "N tests collected" is
    # the property actually being read, and it is unique in this file by the phase-close
    # convention. `test_derive_build_from_claude_md_parses_current_state` runs against the REAL
    # CLAUDE.md and does fire on the regression -- the repair here is so that a future rewrite
    # cannot break the stamp merely by renaming a section.
    idx = text.find("## Current state")
    section = text if idx < 0 else text[idx:]
    # Phase code is a best-effort label only -- not required (see docstring).
    m = re.search(r"Phase ([A-Z]{1,3})\b", section)
    phase = m.group(1) if m else None
    # Test count: NOT simply "the first match" -- some entries (this
    # session's own "221 tests passing across the two touched test files")
    # state a partial, scoped count with no full-suite figure anywhere in
    # that entry's own body, and a first-match scan can land on exactly that
    # partial number (observed live, 2026-07-10 -- the same bug this fix
    # already closed once for the Home page chart, recurring here in a
    # second parser). "collected" is, by this project's own phase-close
    # convention, always the true pytest full-suite collection count, while
    # "tests passing" is used ambiguously for both full-suite and
    # partial/scoped claims -- so "collected" figures are strongly preferred,
    # and the MAXIMUM across all matches of whichever kind is used (never
    # just the first in scan order), since the real suite only grows.
    collected = [int(g.replace(",", "")) for g in re.findall(r"([\d,]+)\s*tests?\s*collected", section)]
    if not collected:
        collected = [int(g.replace(",", "")) for g in re.findall(r"([\d,]+)\s*collected", section)]
    if collected:
        test_count = max(collected)
    else:
        passing = [int(g.replace(",", "")) for g in re.findall(r"([\d,]+)\s*tests?\s*passing", section)]
        test_count = max(passing) if passing else None
    return phase, test_count


def _load_build_info():
    company_modules = count_company_modules()
    # Preferred source: derive fresh from CLAUDE.md so the stamp can never drift.
    phase, test_count = _derive_build_from_claude_md()
    # test_count is the part that actually matters functionally (phase is
    # never displayed on the live site, only test_count is consumed) -- a
    # missing phase code alone must not discard a fresh, correct test_count
    # (2026-07-10: this exact gate previously required BOTH, so the newest
    # phase-close entries losing their literal "Phase XY" tag silently fell
    # through to the stale build_info.json fallback).
    if test_count:
        if not phase and BUILD_INFO_PATH.exists():
            try:
                phase = json.loads(BUILD_INFO_PATH.read_text()).get("phase")
            except (json.JSONDecodeError, ValueError):
                pass
        return phase or _BUILD_PHASE, test_count, company_modules
    # Fallbacks: build_info.json, then the module constants.
    if BUILD_INFO_PATH.exists():
        try:
            info = json.loads(BUILD_INFO_PATH.read_text())
            return (
                phase or info.get("phase", _BUILD_PHASE),
                test_count or info.get("test_count", _BUILD_TEST_COUNT),
                company_modules,
            )
        except (json.JSONDecodeError, ValueError):
            pass
    return phase or _BUILD_PHASE, test_count or _BUILD_TEST_COUNT, company_modules


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt(v):
    return round(float(v), 2) if v is not None else 0.0


def _find_latest_run_json():
    reports = PROJECT / "docs" / "reports"
    candidates = sorted(reports.glob("run_output_*[0-9Z].json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


# ---------------------------------------------------------------------------
# Elexon SSP monthly aggregation
# ---------------------------------------------------------------------------

def load_spot_monthly():
    if not SSP_CACHE.exists():
        return []
    with open(SSP_CACHE) as f:
        ssp = json.load(f)

    monthly = defaultdict(list)
    for rec in ssp:
        date = rec.get("settlementDate", "")
        if not (date >= "2016-01-01" and date <= "2025-12-31"):
            continue
        price = rec.get("systemSellPrice")
        if price is not None:
            monthly[date[:7]].append(float(price))

    result = []
    for month in sorted(monthly):
        prices = monthly[month]
        ps = sorted(prices)
        p95 = ps[min(int(len(ps) * 0.95), len(ps) - 1)]
        result.append({
            "month": month,
            "mean": round(statistics.mean(prices), 2),
            "max": round(max(prices), 2),
            "p95": round(p95, 2),
            "above_500": sum(1 for p in prices if p > 500),
        })
    return result


# ---------------------------------------------------------------------------
# COST BASIS OF A DERIVED VALUATION
# (2026-08-17, WORKER_FINDING_THE_BOOK_IS_VALUED_ON_A_MARGIN_THAT_EXCLUDES_
#  THREE_QUARTERS_OF_THE_COST_STACK, recommendation 3 -- the CLASS, not the row)
#
# A published figure carries its clock (R14). A published figure DERIVED from
# another must also carry the COST BASIS it was built on, because a valuation
# and its stated parent can share a clock and still be different quantities:
# £6,304,202.92 of enterprise value was labelled "derived from the settled-clock
# net margin" while its real parent was a contribution margin totalling 4.15x
# that line. Same clock, same run, same page -- and the label was false.
#
# Which margin line a run's valuation used is the run's own answer
# (`enterprise_value_margin_basis`, carried out of `saas.clv_model`'s
# CLV_MARGIN_BASIS), so the label below cannot be restated independently of the
# code that produced the number. This maps the field NAME to the basis VOCABULARY
# the parent figures declare, and refuses anything it does not recognise.
_MARGIN_FIELD_TO_COST_BASIS = {
    # revenue - wholesale - levies - network - capital - bad debt - cost-to-serve
    "net_of_all_costs_margin_gbp": "net_of_all_costs",
    # revenue - wholesale - cost-to-serve ONLY (the pre-2026-08-17 basis)
    "contribution_margin_gbp": "contribution",
}

#: Basis reported when the run does not say. NOT "assume it is fine": this
#: value matches no parent's declared `cost_basis`, so the parentage gate below
#: FAILS on it. An unavailable check is a failed check (R15 fail-silent), and a
#: valuation that cannot name its own basis is precisely the state the finding
#: measured.
UNKNOWN_COST_BASIS = "unknown"


def _cost_basis_of_valuation(data):
    """The cost basis THIS run's enterprise value was actually computed on.

    Fails closed at every step: a missing key, a null, or a margin field this
    module has no vocabulary entry for all return `UNKNOWN_COST_BASIS`, which
    no parent declares and the parentage gate therefore rejects.
    """
    field = (data or {}).get("enterprise_value_margin_basis")
    if not isinstance(field, str):
        return UNKNOWN_COST_BASIS
    return _MARGIN_FIELD_TO_COST_BASIS.get(field, UNKNOWN_COST_BASIS)


def _check_derived_basis_parentage(portfolio):
    """R10 CLASS GATE: every basis entry that CLAIMS a parent must name a
    parent that is published, labelled, and on the SAME cost basis.

    Runs over every `derived_from` in `portfolio["basis"]` -- not over
    enterprise value specifically -- so a future derived figure inherits the
    check by declaring a parent, which is the class the finding named.

    INDEPENDENCE (R15 anti-tautology): the child's `cost_basis` comes from the
    RUN (`enterprise_value_margin_basis`, i.e. the field the valuation code
    actually indexed); the parent's is declared here against the P&L line. Two
    sources that can genuinely disagree -- and did, for the whole life of the
    defect.

    FAIL-CLOSED: an absent parent entry, an unpublished parent figure, a
    missing `cost_basis` on either side, and the `unknown` sentinel all FAIL.
    "Nothing to compare" must never read as "parentage fine".
    """
    basis = portfolio.get("basis", {}) or {}
    problems = []
    for key, entry in sorted(basis.items()):
        if not isinstance(entry, dict):
            continue
        parent_key = entry.get("derived_from")
        if not parent_key:
            continue  # not a derived figure; nothing is claimed, nothing to check
        if portfolio.get(key) is None:
            continue  # the figure itself is not published this run
        parent_entry = basis.get(parent_key)
        if portfolio.get(parent_key) is None or not isinstance(parent_entry, dict):
            problems.append(
                "{} claims derived_from '{}', which is not a published, "
                "basis-labelled figure".format(key, parent_key)
            )
            continue
        child_basis = entry.get("cost_basis")
        parent_basis = parent_entry.get("cost_basis")
        if not child_basis or child_basis == UNKNOWN_COST_BASIS:
            problems.append(
                "{} does not state the cost basis it was computed on "
                "(got {!r})".format(key, child_basis)
            )
        elif not parent_basis:
            problems.append(
                "{}'s declared parent '{}' states no cost basis".format(key, parent_key)
            )
        elif child_basis != parent_basis:
            problems.append(
                "{} is computed on the '{}' basis but claims to derive from "
                "'{}', which is on the '{}' basis".format(
                    key, child_basis, parent_key, parent_basis
                )
            )
    if problems:
        print(
            "BASIS-PARENTAGE GATE FAILED: {}".format("; ".join(problems)),
            file=sys.stderr,
        )
        return False
    return True


# ---------------------------------------------------------------------------
# Extraction functions
# ---------------------------------------------------------------------------

def extract_portfolio(data):
    ledger = data.get("_ledger_headline", {}) or data.get("ledger_pnl", {})
    # Prefer total_net_gbp (final P&L after all costs including capital) over
    # _ledger_headline.net_margin_gbp (which is a ledger subtotal, not final net).
    net = _fmt(data.get("total_net_gbp") or ledger.get("net_margin_gbp", 0))
    gross = _fmt(data.get("total_gross_gbp") or ledger.get("gross_margin_gbp", 0))
    ret_log = data.get("retention_log", [])
    churned = data.get("churned_billing_accounts", [])
    return {
        "net_margin_gbp": net,
        "gross_margin_gbp": gross,
        "enterprise_value_gbp": _fmt(data.get("enterprise_value_gbp", 0)),
        "treasury_start_gbp": _fmt(data.get("starting_treasury_gbp", 0)),
        "treasury_end_gbp": _fmt(data.get("final_treasury_gbp", 0)),
        "bills_total": int(data.get("bills_total", 0)),
        "committee_interventions_total": int(data.get("committee_wake_ups_total", 0)),
        "retention_offers": len(ret_log),
        "retention_retained": sum(1 for r in ret_log if r.get("outcome") == "retained"),
        "churn_count": len(churned),
        "cost_to_serve_gbp": _fmt(data.get("cost_to_serve_portfolio_gbp", 0)),
        "net_after_cts_gbp": _fmt(data.get("net_margin_after_cost_to_serve_gbp", 0)),
        # CLOCK_TRUTH_AND_THE_BRIDGE.md (2026-07-12, P0): the site's own
        # NUMBER-PASSPORT rule requires basis + freshness + provisional on
        # every published figure. net_margin_gbp is settlement-derived
        # (total_net_gbp) and diverges materially (~4x) from the bill-derived
        # ledger view -- see tools/generate_margin_bridge.py /
        # site/data/margin_bridge.json for the quantified reconciliation.
        # enterprise_value_gbp is computed FROM net_margin_gbp and inherits
        # the same dependency.
        "basis": {
            "net_margin_gbp": {
                "clock": "settled",
                "provisional": True,
                "bridge_available": True,
                # Door pages live one level down (/company/, /proof/), so the
                # bridge resolves as ../data/. "./data/..." resolved to
                # /company/data/margin_bridge.json -> 404 (cold-eyes Expert Hour
                # 2026-07-29). Latent when caught -- no site/ consumer reads this
                # field yet -- but a broken evidence path shipped in published
                # data is the constitution's rule-1 defect whether or not
                # anything currently follows it.
                "bridge_url": "../data/margin_bridge.json",
                # The COST BASIS, beside the clock. `total_net_gbp` is net of
                # every cost attributable to consumption -- wholesale, policy
                # levies (RO/CfD/CM/FiT/CCL/mutualisation), network charges
                # both fuels, capital and bad debt.
                "cost_basis": "net_of_all_costs",
                "note": (
                    "Settlement-derived (total_net_gbp), net of wholesale, "
                    "policy levies, network charges, capital and bad debt. "
                    "Diverges from the bill-derived ledger view "
                    "(financial.ledger.net_margin_gbp) -- see the "
                    "reconciliation bridge."
                ),
            },
            "enterprise_value_gbp": {
                "clock": "settled",
                "provisional": True,
                "derived_from": "net_margin_gbp",
                # DERIVED FROM THE RUN, NOT ASSERTED HERE (2026-08-17
                # margin-basis finding). Until that repair this entry said
                # "Derived from the settled-clock net margin above" while the
                # figure's actual parent was a contribution margin 4.15x that
                # line, and nothing could tell: the sentence was hand-written
                # next to a number computed somewhere else. It now reports
                # what `saas.clv_model.CLV_MARGIN_BASIS` actually was for THIS
                # run, and `_check_derived_basis_parentage` below fails the
                # publish when it stops matching the parent named above.
                "cost_basis": _cost_basis_of_valuation(data),
                "note": (
                    "Discounted future margin of the supplied book, valued on "
                    "the same net-of-all-costs basis as the settled net margin "
                    "above. Inherits that line's divergence from the "
                    "bill-derived view until the bridge is applied to "
                    "recompute it."
                ),
            },
        },
    }


# ---------------------------------------------------------------------------
# SITE_EH3_figure_reconciliation_and_periods (2026-07-29, cold-eyes Expert
# Hour MAJOR-4/5/6): three defects of ONE class -- a published figure whose
# own basis is not defensible. These helpers compute (a) a bad-debt bridge
# (mirroring the existing settled<->billed margin_bridge.json pattern) and
# (c) real, data-derived period coverage per annual row -- never a hardcoded
# "this year is partial" flag.
# ---------------------------------------------------------------------------

def _load_sim_window():
    """Read the sim's real settlement window (site/data/sim_data.json's own
    metadata) as (date, date), or (None, None) if unavailable/malformed --
    callers must treat that as COVERAGE UNKNOWN, never silently assume a
    year is complete (that would be the exact fail-open this atom exists to
    close)."""
    try:
        raw = json.loads(SIM_DATA_PATH.read_text())
    except (OSError, json.JSONDecodeError, ValueError):
        return None, None
    meta = raw.get("metadata", {}) or {}
    pf, pt = meta.get("period_from"), meta.get("period_to")
    try:
        d_from = datetime.strptime(pf, "%Y-%m-%d").date() if pf else None
        d_to = datetime.strptime(pt, "%Y-%m-%d").date() if pt else None
    except (ValueError, TypeError):
        return None, None
    return d_from, d_to


def _year_coverage_fraction(year, period_from, period_to):
    """Fraction (0..1) of calendar YEAR actually covered by the real sim
    window [period_from, period_to] (inclusive) -- COMPUTED from the two
    real dates, never a hardcoded per-year flag. None means coverage is
    unknown (window unavailable), never silently 1.0 (full)."""
    if period_from is None or period_to is None:
        return None
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    win_start = max(year_start, period_from)
    win_end = min(year_end, period_to)
    if win_start > win_end:
        return 0.0
    covered_days = (win_end - win_start).days + 1
    total_days = (year_end - year_start).days + 1
    return round(covered_days / total_days, 4)


_PERIOD_PARTIAL_THRESHOLD = 0.999  # below this, a year is PARTIAL, not "near enough to full"


def _period_note(year, coverage, period_from, period_to):
    """Human-legible period-coverage caveat for a partial annual row, or
    None for a full year / unknown coverage (the fraction itself already
    carries the unknown case)."""
    if coverage is None:
        return "period coverage unknown -- sim window (site/data/sim_data.json) unavailable"
    if coverage >= _PERIOD_PARTIAL_THRESHOLD:
        return None
    year_start, year_end = date(year, 1, 1), date(year, 12, 31)
    win_start = max(year_start, period_from) if period_from else year_start
    win_end = min(year_end, period_to) if period_to else year_end
    months = round(coverage * 12, 1)
    return (
        f"PART YEAR -- covers {win_start.isoformat()} to {win_end.isoformat()} "
        f"({months} of 12 months, {coverage * 100:.0f}% of the calendar year); "
        "excluded from year-over-year trend comparisons."
    )


def extract_financial(data):
    # MARGIN_REALISM.md Step 1 (2026-07-10, director-decided programme, gauge
    # fix): `years[yr].revenue_gbp` is commodity/energy revenue ONLY
    # (settlement-record based) -- it excludes standing charges, non-
    # commodity pass-through, and VAT entirely. `management_accounts[yr].
    # income_statement.revenue_gbp` is the real double-entry TOTAL revenue
    # booked (net of VAT, includes non-commodity pass-through recovery),
    # confirmed by tracing saas/ledger.py's billing_event ("total customer
    # bill, all-in") through company/finance/double_entry.py. These two
    # figures disagree by 26-52% every year with no shrinking trend -- not a
    # bug in either, but a genuine "which revenue" ambiguity, and the site's
    # net_margin_pct was computed against the smaller (commodity-only)
    # denominator, inflating every year's reported margin percentage
    # (director: "levels ~5x too high vs real UK domestic retail ~1-3%").
    # Using the real total revenue as the denominator brings the 10-year
    # average from ~12.5% to ~8.9% -- a real, mechanically-explained
    # correction, not a tuned output (R12: diagnose the mechanism, never
    # tune toward a benchmark). Full diagnosis: docs/design/
    # MARGIN_REALISM_STEP1_DIAGNOSIS.md -- NOT yet reconciled across every
    # surface or added to the consistency gate; this is the first surface.
    mgmt_accounts = data.get("management_accounts", {})
    period_from, period_to = _load_sim_window()
    annual = []
    shock_pops = _annual_shock_by_population(data, sorted(data.get("years", {}).keys()))
    for yr in sorted(data.get("years", {}).keys()):
        ydata = data["years"][yr]
        csplit = ydata.get("commodity_split", {})
        elec = csplit.get("electricity", {})
        gas = csplit.get("gas", {})
        net = ydata.get("net_gbp", 0)
        total_revenue = mgmt_accounts.get(yr, {}).get("income_statement", {}).get("revenue_gbp")
        year_int = int(yr)
        coverage = _year_coverage_fraction(year_int, period_from, period_to)
        is_partial = bool(coverage is not None and coverage < _PERIOD_PARTIAL_THRESHOLD)
        annual.append({
            "year": year_int,
            "revenue_gbp": _fmt(ydata.get("revenue_gbp", 0)),
            "total_revenue_gbp": _fmt(total_revenue) if total_revenue is not None else None,
            "net_margin_pct": (
                round(net / total_revenue * 100, 2) if total_revenue else 0.0
            ),
            "gross_gbp": _fmt(ydata.get("gross_gbp", 0)),
            "capital_gbp": _fmt(ydata.get("capital_gbp", 0)),
            "net_gbp": _fmt(net),
            "treasury_end_gbp": _fmt(ydata.get("treasury_end_gbp", 0)),
            "policy_cost_gbp": _fmt(ydata.get("policy_cost_gbp", 0)),
            "bad_debt_gbp": _fmt(ydata.get("bad_debt_gbp", 0)),
            "elec_gross_gbp": _fmt(elec.get("gross_gbp", 0)),
            "elec_net_gbp": _fmt(elec.get("net_gbp", 0)),
            "gas_gross_gbp": _fmt(gas.get("gross_gbp", 0)),
            "gas_net_gbp": _fmt(gas.get("net_gbp", 0)),
            "bills_count": int(ydata.get("bills_count", 0)),
            "avg_bill_shock_pct": _fmt(ydata.get("avg_bill_shock_pct", 0)),
            # WHICH BILLS -- and, since 2026-09-01, WHICH HOUSEHOLDS. The second
            # half was missing and its absence was worse than silence: a note that
            # answers the population question in the wrong dimension reads as a
            # field whose population question is settled. This one is a mean over
            # BOTH definitions of bill shock at once and says so, and points at the
            # field that separates them.
            "avg_bill_shock_pct_population": (
                "every bill with a computable shock (has a prior bill, and a "
                "baseline at or above BILL_SHOCK_BASELINE_FLOOR_GBP) -- NOT only "
                "the bills flagged as shocks. The flagged-only mean is "
                "monthly_ops.monthly[].avg_shock_pct and is several times larger. "
                "THIS FIGURE IS A MEAN OVER BOTH POPULATIONS AT ONCE and is kept "
                "only as the reconciling total: bill shock is two experiences in "
                "two populations decided by how the household pays, and the two "
                "means are bill_shock_by_population below. It is also a FRACTION "
                "despite the _pct name -- bill_shock_by_population publishes "
                "percentages, as monthly_ops.shock_by_population does."
            ),
            # THE SPLIT, on the surface rather than in a note. Each population's
            # own mean, median, max and bootstrap interval, plus `n`, which this
            # field has never carried at all. A cell with no bills publishes nulls
            # and its n=0 -- not 0.0, which would be an unobservable published as a
            # measured zero -- and a cell too thin to bound itself publishes a null
            # interval beside a real n, which is this series saying "we cannot
            # tell" in the reader's own units.
            "bill_shock_by_population": shock_pops.get(yr, {}),
            # SITE_EH3 MAJOR-6 (R10 class-closing invariant): every published
            # annual row states its own period coverage, COMPUTED from the
            # real sim window -- never a hardcoded "this year is partial".
            "period_coverage_fraction": coverage,
            "period_partial": is_partial,
            "period_note": _period_note(year_int, coverage, period_from, period_to),
        })

    # Segment annual
    segments_seen = set()
    for yr in data.get("years", {}).keys():
        segments_seen.update(data["years"][yr].get("segment_split", {}).keys())

    segment_annual = []
    for yr in sorted(data.get("years", {}).keys()):
        ydata = data["years"][yr]
        ssplit = ydata.get("segment_split", {})
        year_int = int(yr)
        seg_coverage = _year_coverage_fraction(year_int, period_from, period_to)
        row = {
            "year": year_int,
            "period_coverage_fraction": seg_coverage,
            "period_partial": bool(seg_coverage is not None and seg_coverage < _PERIOD_PARTIAL_THRESHOLD),
        }
        for seg, sdata in ssplit.items():
            key = seg.lower().replace(" ", "_")
            rev = sdata.get("revenue_gbp", 0)
            net = sdata.get("net_gbp", 0)
            row[key] = {
                "revenue_gbp": _fmt(rev),
                "gross_gbp": _fmt(sdata.get("gross_gbp", 0)),
                "net_gbp": _fmt(net),
                "net_margin_pct": round(net / rev * 100, 2) if rev > 0 else 0.0,
            }
        segment_annual.append(row)

    ledger = data.get("ledger_pnl", {})
    ledger_bad_debt_gbp = _fmt(ledger.get("bad_debt_gbp", 0))
    annual_bad_debt_total_gbp = round(sum(r["bad_debt_gbp"] for r in annual), 2)
    ratio_x = None
    if (
        isinstance(annual_bad_debt_total_gbp, (int, float))
        and math.isfinite(annual_bad_debt_total_gbp)
        and annual_bad_debt_total_gbp not in (0, 0.0)
    ):
        ratio_x = round(ledger_bad_debt_gbp / annual_bad_debt_total_gbp, 2)
    # SITE_EH3 MAJOR-4 (R10 class-closing invariant): bad debt was published
    # TWICE with no bridge (129.6x apart at one run), and the annual series
    # can go negative -- this reconciliation block names BOTH bases (grounded
    # in company/compliance/crisis_bad_debt_validator.py's own documented
    # distinction, not fabricated) and states which is authoritative, mirroring
    # the existing settled<->billed net-margin bridge pattern above.
    bad_debt_reconciliation = {
        "annual_series_total_gbp": annual_bad_debt_total_gbp,
        "annual_series_basis": (
            "Per-settlement-record behavioural arrears-engine write-off "
            "(simulation/arrears_engine.py) -- can be NEGATIVE in a year where "
            "a recovery/reversal event outweighs that year's new write-offs. "
            "company/compliance/crisis_bad_debt_validator.py documents this as "
            "the 'HEADLINE arrears figure': implausibly low, with no crisis "
            "step-up. Kept for its own per-year SHAPE only -- never read as a "
            "reconciled total."
        ),
        "ledger_total_gbp": ledger_bad_debt_gbp,
        "ledger_basis": (
            "Double-entry P&L accrual (management_accounts[*].income_statement."
            "bad_debt_gbp, summed) -- company/compliance/crisis_bad_debt_"
            "validator.py's 'PnL ACCRUAL figure': tracks ~2-3% of revenue most "
            "years, in the Ofgem/EUA 1-3% benchmark band "
            "(docs/market_research/ASSUMPTIONS.md)."
        ),
        "ratio_x": ratio_x,
        "authoritative": "ledger",
        "note": (
            "These are two different measurements of bad debt, previously "
            "published with no bridge between them -- the ledger figure is the "
            "plausible one (in-band vs Ofgem/EUA, always non-negative) and is "
            "what the board's bad-debt-rate reporting should be read from; the "
            "annual series is a diagnostic shape only."
        ),
        "evidence": "company/compliance/crisis_bad_debt_validator.py",
    }
    return {
        "annual": annual,
        "segment_annual": segment_annual,
        "segments": sorted(segments_seen),
        "ledger": {
            "revenue_gbp": _fmt(ledger.get("revenue_gbp", 0)),
            "wholesale_cost_gbp": _fmt(ledger.get("wholesale_cost_gbp", 0)),
            "gross_margin_gbp": _fmt(ledger.get("gross_margin_gbp", 0)),
            "capital_cost_gbp": _fmt(ledger.get("capital_cost_gbp", 0)),
            "net_margin_gbp": _fmt(ledger.get("net_margin_gbp", 0)),
            "bad_debt_gbp": ledger_bad_debt_gbp,
            "vat_remittance_gbp": _fmt(ledger.get("vat_remittance_gbp", 0)),
            "non_commodity_cost_gbp": _fmt(ledger.get("non_commodity_cost_gbp", 0)),
            "acquisition_spend_gbp": _fmt(ledger.get("acquisition_spend_gbp", 0)),
            "fixed_cost_gbp": _fmt(ledger.get("fixed_cost_gbp", 0)),
            "operating_net_margin_gbp": _fmt(ledger.get("operating_net_margin_gbp", 0)),
        },
        "bad_debt_reconciliation": bad_debt_reconciliation,
        "sim_window": (
            f"{period_from.isoformat()} to {period_to.isoformat()}"
            if period_from and period_to else None
        ),
        "period_coverage_source": (
            "site/data/sim_data.json metadata.period_from/period_to"
            if period_from and period_to else "unavailable"
        ),
    }


def extract_flexibility(data):
    """Phase NY: Flexibility revenue summary for site/ dashboard tab."""
    flex = data.get("flexibility_revenue_summary", {})
    ic_flex = data.get("ic_flexibility_summary", {})

    resi_per_year = {}
    for yr, yd in flex.get("per_year", {}).items():
        resi_per_year[str(yr)] = {
            "cm_gbp": _fmt(yd.get("cm_gbp", 0)),
            "dfs_gbp": _fmt(yd.get("dfs_gbp", 0)),
            "total_gbp": _fmt(yd.get("total_gbp", 0)),
            "enrolled_customers": int(yd.get("enrolled_customers", 0)),
        }

    ic_per_year = {}
    for yr, yd in ic_flex.get("per_year", {}).items():
        ic_per_year[str(yr)] = {
            "net_gbp": _fmt(yd.get("total_net_gbp", 0)),
            "enrolled_customers": int(yd.get("enrolled_customers", 0)),
            "total_flex_kw": _fmt(yd.get("total_flex_kw", 0)),
        }

    resi_total_gbp = flex.get("total_flexibility_revenue_gbp", 0)
    ic_total_gbp = ic_flex.get("total_ic_flex_revenue_gbp", 0)
    return {
        # Computed locally as resi+ic rather than trusting data["total_
        # flexibility_revenue_gbp"] -- that upstream field was itself buggy
        # (resi-only, silently missing I&C) until saas/reporting/
        # annual_report.py's 2026-07-10 fix, and a run_output.json generated
        # by an older sim run still carries the stale value regardless of
        # that fix. This keeps the dashboard correct even against old data.
        "total_gbp": _fmt(resi_total_gbp + ic_total_gbp),
        "resi_total_gbp": _fmt(resi_total_gbp),
        "ic_total_gbp": _fmt(ic_total_gbp),
        "resi_enrolled_customer_years": int(flex.get("enrolled_customer_years", 0)),
        "ic_enrolled_customer_years": int(ic_flex.get("enrolled_customer_years", 0)),
        "resi_per_year": resi_per_year,
        "ic_per_year": ic_per_year,
    }


def extract_trading(data, spot_monthly):
    # Committee interventions per month
    committee_monthly = defaultdict(int)
    for yr, ydata in data.get("years", {}).items():
        for wu in ydata.get("committee_wake_ups", []):
            date = wu.get("settlement_date", "")
            if date:
                committee_monthly[date[:7]] += 1

    # Hedge fraction per year (portfolio average)
    hedge_annual = []
    for yr in sorted(data.get("years", {}).keys()):
        hf_data = data["years"][yr].get("hedge_fractions", {})
        if isinstance(hf_data, dict) and hf_data:
            avgs = [v.get("avg_hf", 0.85) for v in hf_data.values() if isinstance(v, dict)]
            if avgs:
                hedge_annual.append({
                    "year": int(yr),
                    "avg_hf": round(statistics.mean(avgs), 4),
                    "min_hf": round(min(avgs), 4),
                    "max_hf": round(max(avgs), 4),
                })

    # Forward terms (basis risk)
    forward_terms = []
    for t in data.get("basis_risk_terms", []):
        forward_terms.append({
            "date": t.get("term_start", ""),
            "customer_id": t.get("customer_id", ""),
            "commodity": t.get("commodity", "electricity"),
            "company_fwd": _fmt(t.get("company_fwd_gbp_per_mwh", 0)),
            "sim_fwd": _fmt(t.get("sim_fwd_gbp_per_mwh", 0)),
            "error_pct": round(float(t.get("tariff_error_pct", 0)), 4),
        })

    # Enrich spot_monthly with committee counts
    committee_enriched = []
    for row in spot_monthly:
        row = dict(row)
        row["committee_count"] = committee_monthly.get(row["month"], 0)
        committee_enriched.append(row)

    # Add committee months with no spot data
    for month, count in sorted(committee_monthly.items()):
        if not any(r["month"] == month for r in committee_enriched):
            committee_enriched.append({"month": month, "mean": 0, "max": 0, "p95": 0, "above_500": 0, "committee_count": count})

    committee_enriched.sort(key=lambda r: r["month"])

    # VaR per year (realized value-at-risk carried on the naked/unhedged position)
    var_by_year = defaultdict(list)
    for e in data.get("hedge_var_log", []):
        term_start = e.get("term_start", "")
        if len(term_start) >= 4:
            var_by_year[term_start[:4]].append(e)
    var_annual = []
    for yr in sorted(var_by_year.keys()):
        entries = var_by_year[yr]
        pcts = [e.get("var_pct_of_term_revenue", 0.0) for e in entries]
        var_annual.append({
            "year": int(yr),
            "avg_var_pct_of_term_revenue": round(statistics.mean(pcts), 6) if pcts else 0.0,
            "max_var_pct_of_term_revenue": round(max(pcts), 6) if pcts else 0.0,
            "total_var_gbp": _fmt(sum(e.get("var_gbp", 0.0) for e in entries)),
            "term_count": len(entries),
        })

    # Wholesale value-chain organs (VALUE_CHAIN mint): counterparty attribution,
    # per-counterparty credit exposure, and the margin-call book. All three are
    # company-observable (own netted MtM, own margin calls, public rating bands)
    # -- never a sim internal. Fail-open to available:False on older run shapes
    # (C-S1 partial-arrival tolerance): the keys were only added to run output
    # on 2026-07-24 (git 15b6e8c4a).
    tb = data.get("trading_book") or {}
    ce = data.get("wholesale_credit_exposure") or {}
    mc = data.get("margin_call_book") or {}
    cpd = tb.get("counterparty_distribution") or {}
    if tb or ce or mc:
        wholesale = {
            "available": True,
            # counterparty attribution (who the hedges sit with)
            "contract_count": tb.get("contract_count"),
            "distinct_counterparties": cpd.get("distinct_counterparties"),
            "cleared_count": cpd.get("cleared_count"),
            "bilateral_count": cpd.get("bilateral_count"),
            "broker_arranged_count": cpd.get("broker_arranged_count"),
            "by_counterparty_type": cpd.get("by_counterparty_type"),
            # credit exposure (owed TO the company, ISDA-netted, MtM-driven)
            "eor_mark_date": ce.get("mark_date"),
            "eor_net_exposure_gbp": ce.get("total_net_exposure_gbp"),
            "largest_counterparty": ce.get("largest_counterparty"),
            "largest_net_exposure_gbp": ce.get("largest_net_exposure_gbp"),
            "largest_utilisation_pct": ce.get("largest_utilisation_pct"),
            "collateral_held_gbp": ce.get("total_collateral_held_gbp"),
            "n_breach": ce.get("n_breach"),
            # mid-run peak (the board-meaningful figure -- exposure peaks at a
            # price shock, not at run-end when most terms have delivered)
            "peak_net_exposure_gbp": ce.get("peak_total_net_exposure_gbp"),
            "peak_sample_date": ce.get("peak_sample_date"),
            "sampling": ce.get("sampling"),
            "n_samples": ce.get("n_samples"),
            # margin-call book (the liquidity leg the collateral death-loop drains)
            "margin_outstanding_gbp": mc.get("total_outstanding_gbp"),
            "margin_calls": mc.get("total_calls"),
            "credit_facility_gbp": mc.get("credit_facility_gbp"),
            "facility_headroom_gbp": mc.get("headroom_gbp"),
            "is_liquidity_stressed": mc.get("is_liquidity_stressed"),
        }
    else:
        wholesale = {"available": False}

    return {
        "spot_monthly": committee_enriched,
        "hedge_annual": hedge_annual,
        "forward_terms": forward_terms[:500],  # cap for payload size
        "var_annual": var_annual,
        "var_limit_pct_of_term_revenue": VAR_REVENUE_LIMIT,
        "wholesale": wholesale,
    }


def extract_customers(data):
    # Book size per year
    book_annual = []
    for yr in sorted(data.get("years", {}).keys()):
        ydata = data["years"][yr]
        active = ydata.get("active_customer_ids", [])
        elec_ids = [c for c in active if not c.endswith("g")]
        gas_ids = [c for c in active if c.endswith("g")]
        acqs = len(ydata.get("acquisitions", []))
        bill_shocks = ydata.get("bill_shock_events", [])
        worst_shock = max((e.get("bill_shock_pct", 0) for e in bill_shocks), default=0)
        # D3 Expert-Hour finding (2026-07-12): organic_bill_shock_count
        # excludes catchup-driven shocks (an individual account's own read/
        # closure timing, not a market/consumption signal) -- for callers
        # that specifically want the market-driven signal (e.g. a crisis-
        # year comparison), not the raw customer-experience total.
        organic_shocks = [e for e in bill_shocks if not e.get("catchup_driven")]
        book_annual.append({
            "year": int(yr),
            "active_elec": len(elec_ids),
            "active_gas": len(gas_ids),
            "acquisitions": acqs,
            "bill_shock_count": len(bill_shocks),
            "organic_bill_shock_count": len(organic_shocks),
            "worst_shock_pct": round(float(worst_shock) * 100, 1) if worst_shock else 0,
        })

    # Per-customer per-year net margin for heatmap
    per_year_net = defaultdict(dict)
    for yr, ydata in data.get("years", {}).items():
        for cid, cdata in ydata.get("per_customer", {}).items():
            per_year_net[cid][yr] = _fmt(cdata.get("net_gbp", 0))

    # Customer lifecycle events (churn, renewal, acquisition)
    events = []
    for ev in data.get("customer_events", []):
        events.append({
            "customer_id": ev.get("customer_id", ""),
            "date": ev.get("event_date", ""),
            "type": ev.get("event_type", ""),
            "commodity": ev.get("commodity", "electricity"),
            "sim_churn_p": round(float(ev.get("churn_probability", 0)), 3),
            "company_est": round(float(ev.get("company_churn_estimate", 0)), 3),
            "retention_offered": bool(ev.get("retention_offered", False)),
            "market_signal": round(float(ev.get("market_switching_multiplier", 0)), 4),
            "realized_churn_p": round(float(ev.get("realized_churn_probability", 0)), 3),
            "is_active_renewal": ev.get("is_active_renewal"),
            "engagement_level": ev.get("engagement_level"),
        })

    _events_by_key = {(e["customer_id"], e["date"]): e for e in events}

    # Retention log
    retention = []
    for r in data.get("retention_log", []):
        _key = (r.get("customer_id", ""), r.get("event_date", ""))
        _sim_side = _events_by_key.get(_key)
        retention.append({
            "customer_id": r.get("customer_id", ""),
            "date": r.get("event_date", ""),
            "company_est": round(float(r.get("company_churn_estimate", 0)), 3),
            "discount_pct": round(float(r.get("discount_pct", 0)), 3),
            "cost_gbp": _fmt(r.get("retention_cost_gbp", 0)),
            "expected_term_margin_gbp": _fmt(r.get("expected_term_margin_gbp", 0)),
            "assumed_deferral_months": r.get("assumed_deferral_months", 12),
            "outcome": r.get("outcome", ""),
            "framing_type": r.get("framing_type"),
            "sim_churn_p": _sim_side["sim_churn_p"] if _sim_side else None,
            "market_signal": _sim_side["market_signal"] if _sim_side else None,
            "realized_churn_p": _sim_side["realized_churn_p"] if _sim_side else None,
        })

    # Phase QM (QL_WIRE_AND_DEFERRAL.md): retention offers priced as deferral windows
    # (H1 assumed vs H2 realized), plus serial-saver EV-negative detection.
    retention_deferral = compute_realized_deferrals(
        data.get("retention_log", []), data.get("company_event_log", [])
    )
    serial_savers = serial_saver_summary(data.get("retention_log", []))

    # Lifetime per customer — pull tariff_type from the customer book, resolved
    # through the single `live_population()` seam (generator draw-wiring,
    # PRODUCT-FIRST item 2, report-lookup generator #2): BYTE-IDENTICAL while
    # `SE_DRAW_POPULATION` is off, additively carrying the SYN acquisition
    # cohort's tariff_type when the director-reserved flag is on.
    _CUSTS = _resolve_book()
    _tariff_by_cid = {c["customer_id"]: c.get("tariff_type", "fixed") for c in _CUSTS}

    lifetime = {}
    for cid, cdata in data.get("per_customer_lifetime", {}).items():
        lifetime[cid] = {
            "segment": cdata.get("segment", ""),
            "commodity": cdata.get("commodity", "electricity"),
            "tariff_type": _tariff_by_cid.get(cid, "fixed"),
            "acquisition_date": cdata.get("acquisition_date", ""),
            "revenue_gbp": _fmt(cdata.get("revenue_gbp", 0)),
            "gross_gbp": _fmt(cdata.get("gross_gbp", 0)),
            "capital_gbp": _fmt(cdata.get("capital_gbp", 0)),
            "net_gbp": _fmt(cdata.get("net_gbp", 0)),
            "cost_to_serve_gbp": _fmt(cdata.get("cost_to_serve_gbp", 0)),
            "net_after_cts_gbp": _fmt(cdata.get("net_margin_after_cost_to_serve_gbp", 0)),
        }

    journey_log = []  # Phase QL Part 2: churn journey trajectory (SIM-side hidden state)
    for j in data.get("churn_journey_log", []):
        journey_log.append({
            "customer_id": j.get("customer_id", ""),
            "date": j.get("term_start", ""),
            "state": j.get("journey_state", ""),
            "resentment_score": j.get("resentment_score", 0),
            "is_burned": bool(j.get("is_burned", False)),
            "perceived_bill_saving_gbp": j.get("perceived_bill_saving_gbp", 0),
        })

    acquisition_funnel_log = []  # PROCESS_NOT_EVENTS.md: acquisition funnel, not a coin flip
    for a in data.get("acquisition_funnel_log", []):
        acquisition_funnel_log.append({
            "billing_account": a.get("billing_account", ""),
            "segment": a.get("segment", ""),
            "term_start": a.get("term_start", ""),
            "won": bool(a.get("won", False)),
            "stage_reached": a.get("stage_reached", ""),
            "total_cost_gbp": a.get("total_cost_gbp", 0),
            "credit_bureau_score_band": a.get("credit_bureau_score_band"),
            "credit_bureau_passed": a.get("credit_bureau_passed"),
            "credit_bureau_true_creditworthy": a.get("credit_bureau_true_creditworthy"),
            "stages": a.get("stages", []),
        })

    # Phase 3 (CORE_FIDELITY_PHASES.md item 1): meter-read arrival/
    # estimation/failure events -- raw passthrough, binned client-side to
    # match the journey_log/acquisition_funnel_log convention above.
    meter_read_log = []
    for m in data.get("meter_read_log", []):
        meter_read_log.append({
            "customer_id": m.get("customer_id", ""),
            "period_end": m.get("period_end", ""),
            "meter_type": m.get("meter_type", ""),
            "delay_days": m.get("delay_days", 0),
            "status": m.get("status", ""),
        })

    return {
        "book_annual": book_annual,
        "per_year_net": dict(per_year_net),
        "events": events,
        "retention": retention,
        "retention_deferral": retention_deferral,
        "serial_savers": serial_savers,
        "lifetime": lifetime,
        "journey_log": journey_log,
        "acquisition_funnel_log": acquisition_funnel_log,
        "meter_read_log": meter_read_log,
    }




def extract_insights(insights_path=None):
    """Return run insights dict from run_insights.json, or None if absent/invalid."""
    path = insights_path or RUN_INSIGHTS_PATH
    if not Path(path).exists():
        return None
    try:
        return json.loads(Path(path).read_text())
    except (json.JSONDecodeError, ValueError):
        return None

def extract_market(data, spot_monthly=None):
    # Segment margins per year from segment_split
    segment_annual = []
    segments_seen = set()
    for yr in sorted(data.get("years", {}).keys()):
        ydata = data["years"][yr]
        ssplit = ydata.get("segment_split", {})
        for seg in ssplit:
            segments_seen.add(seg)

    for yr in sorted(data.get("years", {}).keys()):
        ydata = data["years"][yr]
        ssplit = ydata.get("segment_split", {})
        row = {"year": int(yr)}
        for seg in sorted(segments_seen):
            sdata = ssplit.get(seg, {})
            key = seg.lower().replace(" ", "_")
            row[key + "_gross"] = _fmt(sdata.get("gross_gbp", 0))
            row[key + "_net"] = _fmt(sdata.get("net_gbp", 0))
        segment_annual.append(row)

    # Company vs SIM forward price error: company pricing error relative to SIM ground truth
    company_error_by_year = defaultdict(list)
    for t in data.get("basis_risk_terms", []):
        yr = (t.get("term_start", "0000") or "0000")[:4]
        if yr.isdigit():
            company = float(t.get("company_fwd_gbp_per_mwh", 0) or 0)
            sim = float(t.get("sim_fwd_gbp_per_mwh", 0) or 0)
            if sim > 0:
                company_error_by_year[yr].append(company - sim)

    forward_premium_annual = []
    for yr in sorted(company_error_by_year):
        vals = company_error_by_year[yr]
        forward_premium_annual.append({
            "year": int(yr),
            "mean_error_gbp_per_mwh": round(statistics.mean(vals), 2),
            "count": len(vals),
        })

    # Contango/backwardation: sim_fwd vs actual spot price in that month
    # Positive = contango (forward > spot), negative = backwardation (crisis: spot > forward)
    spot_by_month = {r["month"]: r["mean"] for r in spot_monthly} if spot_monthly else {}
    contango_by_month = defaultdict(list)
    for t in data.get("basis_risk_terms", []):
        term_start = t.get("term_start", "")
        month = term_start[:7]
        sim_fwd = float(t.get("sim_fwd_gbp_per_mwh", 0) or 0)
        spot = spot_by_month.get(month)
        if sim_fwd > 0 and spot and spot > 0:
            contango_by_month[month].append(sim_fwd - spot)

    contango_monthly = []
    for month in sorted(contango_by_month):
        vals = contango_by_month[month]
        spot = spot_by_month.get(month, 0)
        mean_fwd = spot + statistics.mean(vals)
        contango_monthly.append({
            "month": month,
            "spot": round(spot, 2),
            "forward": round(mean_fwd, 2),
            "premium_gbp": round(statistics.mean(vals), 2),
            "premium_pct": round(statistics.mean(vals) / spot * 100, 1) if spot > 0 else 0,
        })

    return {
        "segment_annual": segment_annual,
        "segments": sorted(segments_seen),
        "forward_premium_annual": forward_premium_annual,
        "contango_monthly": contango_monthly,
    }


def extract_management_accounts(data):
    ma = data.get("management_accounts", {})
    rows = []
    for yr in sorted(ma.keys()):
        stmt = ma[yr].get("income_statement", {})
        rev = _fmt(stmt.get("revenue_gbp", 0))
        net = _fmt(stmt.get("net_margin_gbp", 0))
        # E1 Corporation Tax triplet (docs/design/E1_CORPORATION_TAX_FINDING.md) -- computed in
        # company/finance/double_entry.py::income_statement() since 2026-07-10, but never
        # extracted here until a 2026-07-11 HARDEN-sweep Expert Hour found it missing from every
        # business surface (real UK statutory accounts always headline post-tax "Profit for the
        # Financial Year" with Corporation Tax as its own line -- a real legibility gap, not a
        # substance one). None for years before the triplet existed / if genuinely absent --
        # never defaulted to 0, which would misrepresent a real "not computed" as "no tax due".
        profit_before_tax = stmt.get("profit_before_tax_gbp")
        corporation_tax = stmt.get("corporation_tax_gbp")
        profit_for_year = stmt.get("profit_for_year_gbp")
        rows.append({
            "year": int(yr),
            "revenue_gbp": rev,
            "wholesale_cost_gbp": _fmt(stmt.get("wholesale_cost_gbp", 0)),
            "non_commodity_cost_gbp": _fmt(stmt.get("non_commodity_cost_gbp", 0)),
            "gross_margin_gbp": _fmt(stmt.get("gross_margin_gbp", 0)),
            "capital_cost_gbp": _fmt(stmt.get("capital_cost_gbp", 0)),
            "bad_debt_gbp": _fmt(stmt.get("bad_debt_gbp", 0)),
            "cost_to_serve_gbp": _fmt(stmt.get("cost_to_serve_gbp", 0)),
            "fixed_cost_gbp": _fmt(stmt.get("fixed_cost_gbp", 0)),
            "acquisition_spend_gbp": _fmt(stmt.get("acquisition_spend_gbp", 0)),
            "total_opex_gbp": _fmt(stmt.get("total_opex_gbp", 0)),
            "net_margin_gbp": net,
            "net_margin_pct": round(net / rev * 100, 2) if rev > 0 else 0.0,
            "profit_before_tax_gbp": _fmt(profit_before_tax) if profit_before_tax is not None else None,
            "corporation_tax_gbp": _fmt(corporation_tax) if corporation_tax is not None else None,
            "profit_for_year_gbp": _fmt(profit_for_year) if profit_for_year is not None else None,
        })
    return {"annual": rows}


def _final_year_active_ids(data):
    """The final simulation year's active_customer_ids -- the SAME source
    population the pulse-strip Book Size (extract_customers()'s book_annual
    last entry) is counted from. One canonical population, so every
    count-of-accounts figure on the page reconciles by construction rather
    than by coincidence (defect 3, ADVISOR_STEER_THESIS_CHART.md)."""
    years = data.get("years", {})
    if not years:
        return []
    last_yr = sorted(years.keys())[-1]
    return list(years[last_yr].get("active_customer_ids", []))


def _resi_household_ids_from_active(active_ids):
    """Resi-only, deduplicated household base-IDs from a set of active account
    legs. Resi filter fixes defect 2 (SME/I&C accounts have no valid DOMESTIC
    Ofgem allowance and must never load the benchmark); dedup collapses a
    dual-fuel household's two legs (e.g. C2 + C2g) into one household, since the
    Ofgem allowance is per dual-fuel household, not per fuel account."""
    from saas.customers import get_customer
    from saas.opex_ledger import _household_base_id
    resi = [
        cid for cid in active_ids
        if (get_customer(cid) or {}).get("segment") == "resi"
    ]
    return sorted({_household_base_id(cid) for cid in resi})


def extract_opex_ledger(data):
    """MARGIN_REALISM Step 3 (B2, Maturity Map): the dual opex ledger --
    TRUE (a+b) cost vs a BENCHMARK-loaded proxy, per saas/opex_ledger.py.

    Population (ADVISOR_STEER_THESIS_CHART.md, defects 2+3, 2026-07-11): RESI
    households that are ACTIVE IN THE FINAL SIMULATION YEAR, deduplicated to
    households. This is the resi-only, deduplicated subset of the exact same
    final-year active_customer_ids population the pulse-strip Book Size is
    counted from -- so the two page figures reconcile by construction, not by
    coincidence. It replaces the previous static, all-time, all-segment
    saas.customers.CUSTOMERS master list, which (a) loaded the DOMESTIC Ofgem
    benchmark with SME/I&C accounts that have no valid domestic allowance
    (inflating the benchmark) and (b) counted a different population from the
    Book Size (the reader-visible 11-vs-13 mismatch)."""
    from saas.customers import get_customer
    from saas.opex_ledger import build_opex_ledger
    from simulation.household_segments import payment_channel_for_customer

    active_ids = _final_year_active_ids(data)
    resi_active_ids = [
        cid for cid in active_ids
        if (get_customer(cid) or {}).get("segment") == "resi"
    ]
    resi_records = [get_customer(cid) for cid in resi_active_ids if get_customer(cid)]

    households = _resi_household_ids_from_active(active_ids)
    channels = {}
    for household in households:
        try:
            channels[household] = payment_channel_for_customer(household).value
        except Exception:
            continue  # left unresolved -- build_opex_ledger excludes it from the benchmark side only

    ledger = build_opex_ledger(resi_records, channels)
    return {
        "true_third_party_cost_gbp": ledger["true_third_party_cost_gbp"],
        "true_ai_compute_cost_gbp": ledger["true_ai_compute_cost_gbp"],
        "true_opex_total_gbp": ledger["true_opex_total_gbp"],
        "benchmark_labour_cost_gbp": ledger["benchmark_labour_cost_gbp"],
        "benchmark_opex_total_gbp": ledger["benchmark_opex_total_gbp"],
        "investor_thesis_gap_gbp": ledger["investor_thesis_gap_gbp"],
        "household_count": ledger["household_count"],
        "unresolved_household_count": ledger["unresolved_household_count"],
        "benchmark_opex_per_household_gbp": ledger["benchmark_opex_per_household_gbp"],
        "true_opex_per_household_gbp": ledger["true_opex_per_household_gbp"],
        "population_basis": "resi households active in the final simulation year",
        "note": (
            "TRUE ledger = real third-party costs (DCC comms charge only -- "
            "payment processing/postage/credit-check/debt-collection/Elexon/"
            "Xoserve are genuine, documented gaps, not estimated) + AI-compute "
            "(not yet populated -- open costing-basis + director-rate questions, "
            "see PRIORITIES.md). BENCHMARK ledger = Ofgem price-cap 'operating, "
            "debt and industry' allowance per household, netted of the TRUE "
            "third-party cost to avoid double-counting DCC. Population = RESI "
            "households active in the final simulation year (the same population "
            "the Book Size is counted from); SME/I&C are excluded because the "
            "Ofgem allowance is a DOMESTIC figure. *_total_gbp fields are book "
            "sums across households; *_per_household_gbp are the honest "
            "per-household figures. The gap is the investor thesis, not a claim "
            "the TRUE ledger is complete."
        ),
    }


def extract_b2_taxonomy(data):
    """B2_OPEX_TAXONOMY_EXPANSION.md (2026-07-10, director-direct NTFY): the
    fixed-cost floor (categories 4+5), the emergent break-even analysis, segment
    capital-employed + ROCE, and single-customer gross-margin concentration.
    ROCE hurdle + concentration limit are the director's own real numbers
    (2026-07-10 NTFY reply, docs/staging/done/from_rich_20260710_190908.md):
    "ROCE hurdle: 12% pre-tax on segment capital employed. Concentration
    limit: 15% of gross margin per customer, amber at 10% -- current breaches
    render as standing risk exceptions curable only by book growth, exactly as
    intended." Break-even is explicitly flagged provisional per the same
    reply: "5.1 is machinery-proof only, pre-normalisation and
    whale-distorted -- label it provisional on all surfaces, and re-derive
    with segment-level break-evens after MARGIN_REALISM steps 4-5 land"."""
    from saas.opex_ledger import (
        break_even_analysis, fixed_cost_floor_gbp_per_year,
    )
    from company.finance.segment_capital import (
        segment_capital_employed_gbp, segment_roce_pct, segments_under_hurdle,
    )
    from company.risk.concentration_risk import (
        build_gross_margin_concentration_snapshot, gross_margin_concentration_check,
    )
    import datetime as _dt

    ROCE_HURDLE_PCT = 12.0
    CONCENTRATION_LIMIT_PCT = 15.0
    CONCENTRATION_AMBER_PCT = 10.0

    floor = fixed_cost_floor_gbp_per_year(golive=False)

    years = data.get("years", {})
    latest_year = max(years.keys(), key=int) if years else None
    ssplit = years.get(latest_year, {}).get("segment_split", {}) if latest_year else {}

    segment_avg_margin = {}
    segment_revenue_share = {}
    segment_net_profit = {}
    total_revenue = sum(s.get("revenue_gbp", 0.0) for s in ssplit.values())
    total_capital_cost = sum(s.get("capital_gbp", 0.0) for s in ssplit.values())

    pcl = data.get("per_customer_lifetime", {})
    count_by_label = {}
    for cid, cdata in pcl.items():
        seg = cdata.get("segment", "unknown")
        comm = cdata.get("commodity", "electricity")
        label = f"{seg} {comm}"
        count_by_label[label] = count_by_label.get(label, 0) + 1

    for label, sdata in ssplit.items():
        rev = sdata.get("revenue_gbp", 0.0)
        gross = sdata.get("gross_gbp", 0.0)
        net = sdata.get("net_gbp", 0.0)
        n = count_by_label.get(label, 0)
        segment_avg_margin[label] = round(gross / n, 2) if n > 0 else 0.0
        segment_revenue_share[label] = round(rev / total_revenue, 4) if total_revenue > 0 else 0.0
        segment_net_profit[label] = net

    current_mix_counts = {label: count_by_label.get(label, 0) for label in ssplit}

    break_even = break_even_analysis(
        segment_avg_gross_margin_gbp=segment_avg_margin,
        current_mix_counts=current_mix_counts,
        fixed_floor_gbp=floor["total_floor_gbp"],
    )
    # Director-flagged 2026-07-10: this figure is "machinery-proof only,
    # pre-normalisation and whale-distorted" at this book's current scale (one
    # dominant I&C customer skews the weighted-average gross margin) -- must
    # be labelled provisional on every surface until re-derived with
    # segment-level break-evens after MARGIN_REALISM steps 4-5 land.
    break_even["provisional"] = True
    break_even["provisional_note"] = (
        "Machinery-proof only, pre-normalisation and whale-distorted at this "
        "book's current scale (one dominant I&C customer skews the weighted-"
        "average gross margin) -- to be re-derived with segment-level "
        "break-evens once MARGIN_REALISM steps 4-5 land."
    )

    # Segment capital/ROCE works at the BARE segment grain (resi/SME/I&C), not
    # segment_split's finer "segment commodity" grain used for break-even above
    # -- working capital (AR) is a per-household concept (a dual-fuel household
    # owes money as a household, not per fuel leg), so mixing the two grains in
    # one dict would silently double-count/misattribute. Aggregate ssplit's
    # per-label figures up to bare segment (strip the trailing commodity word)
    # to match.
    bare_revenue = {}
    bare_net_profit = {}
    for label, sdata in ssplit.items():
        bare_seg = label.rsplit(" ", 1)[0]
        bare_revenue[bare_seg] = bare_revenue.get(bare_seg, 0.0) + sdata.get("revenue_gbp", 0.0)
        bare_net_profit[bare_seg] = bare_net_profit.get(bare_seg, 0.0) + sdata.get("net_gbp", 0.0)
    bare_revenue_share = {
        seg: round(rev / total_revenue, 4) if total_revenue > 0 else 0.0
        for seg, rev in bare_revenue.items()
    }

    # Working capital (accounts receivable) per segment, from the real billing
    # ledger -- balance_gbp is total_paid - total_billed, so a NEGATIVE balance
    # is money owed BY the customer TO the company (a real receivable); a
    # positive balance (credit/overpaid) contributes nothing to working capital
    # tied up. Bare segment grain (resi/SME/I&C), matching bare_revenue_share
    # above -- working capital is a per-household concept, not per-fuel-account.
    ledger_path = PROJECT / "site" / "state" / "billing_ledger.json"
    segment_working_capital = {}
    if ledger_path.is_file():
        try:
            ledger = json.loads(ledger_path.read_text())
            for cid, cdata in ledger.get("customers", {}).items():
                seg = cdata.get("segment", "unknown")
                owed = max(0.0, -cdata.get("balance_gbp", 0.0))
                segment_working_capital[seg] = segment_working_capital.get(seg, 0.0) + owed
        except (json.JSONDecodeError, OSError):
            segment_working_capital = {}

    # No real per-segment attribution exists in this codebase for wholesale
    # collateral/credit exposure (company/trading/wholesale_credit_exposure.py,
    # initial_margin_register.py are portfolio-level, never wired to a specific
    # segment) -- allocated pro-rata by revenue share instead, using the year's
    # real total capital_gbp (hedging capital cost) as the closest already-
    # computed real portfolio figure, documented as a proxy, not collateral
    # itself.
    capital_employed = segment_capital_employed_gbp(
        segment_working_capital_gbp=segment_working_capital,
        segment_revenue_share=bare_revenue_share,
        total_collateral_and_exposure_gbp=total_capital_cost,
    )
    roce = segment_roce_pct(bare_net_profit, capital_employed)
    under_hurdle = segments_under_hurdle(roce, ROCE_HURDLE_PCT)

    concentration = None
    if pcl:
        per_cid_margin = {cid: cdata.get("gross_gbp", 0.0) for cid, cdata in pcl.items()}
        snap = build_gross_margin_concentration_snapshot(per_cid_margin, _dt.date.today())
        concentration = gross_margin_concentration_check(
            snap, CONCENTRATION_LIMIT_PCT, CONCENTRATION_AMBER_PCT
        )

    return {
        "fixed_cost_floor": floor,
        "break_even_analysis": break_even,
        "segment_capital_employed_gbp": capital_employed,
        "segment_roce_pct": roce,
        "segment_roce_hurdle": under_hurdle,
        "single_customer_concentration": concentration,
        "note": (
            "Fixed floor = categories (4) infrastructure + (5) governance/"
            "professional, own P&L line, never blended per-customer -- see "
            "saas/opex_ledger.py and docs/market_research/B2_CATEGORY{4,5,6}_"
            "*.md for anchors, most estimate-flagged not invented. Break-even "
            "= book size at current segment mix needed for gross margin to "
            "cover the floor -- emergent, recomputed each run, never tuned "
            "(R12). PROVISIONAL at this book's scale (director-flagged "
            "2026-07-10): whale-distorted by one dominant I&C customer, to be "
            "re-derived with segment-level break-evens once MARGIN_REALISM "
            "steps 4-5 land. Segment capital employed = real per-segment AR "
            "(working capital) + a revenue-share-allocated portion of total "
            "hedging capital cost (a documented proxy for collateral/credit "
            "exposure, which has no real per-segment attribution in this "
            "codebase). ROCE hurdle (12% pre-tax) and the concentration limit "
            "(15%, amber at 10%) are the director's own real risk-appetite "
            "numbers (set 2026-07-10) -- current breaches are standing risk "
            "exceptions curable only by book growth, by design, not a defect "
            "to silence."
        ),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

#: Resamples behind the published shock interval. A COMPUTATIONAL parameter (how
#: finely the bootstrap distribution is sampled), not a domain quantity: it changes
#: the interval's last decimal, never what the interval means. 2,000 is the
#: conventional floor for a percentile bootstrap and the whole 113-month series
#: costs well under a second.
_SHOCK_BOOTSTRAP_RESAMPLES = 2000
#: The published interval is the conventional 95%. Named here rather than inlined
#: so the field name and the number cannot drift apart.
_SHOCK_BOOTSTRAP_TAILS_PCT = (2.5, 97.5)


def _bootstrap_mean_interval(sample, seed_key):
    """The bound a sample of this size earns for its own mean, as a percentile
    bootstrap over ``_SHOCK_BOOTSTRAP_RESAMPLES`` resamples.

    Why a bootstrap and not a standard error. The distribution under complaint is
    the reason this exists: post-floor, the shock series' p99 is 19.8x its median.
    A symmetric +/-1.96*SE band around the mean of five draws from that would state
    a precision the sample does not have, and would do it in the exact months --
    the thin ones -- where the bound is the whole point. The bootstrap assumes no
    shape.

    Why no minimum-n cutoff anywhere in this function. Suppressing months below
    some n would be a threshold picked because a threshold was needed, and no
    published source establishes a minimum sample for this quantity -- nobody
    published measures it. The interval IS the honest statement: for a thin month
    it comes out wide, and a wide interval says "we cannot tell" in the reader's
    own units instead of hiding the month.

    Returns (low, high) as fractions, or (None, None) when the sample cannot bound
    itself. n < 2 returns Nones rather than a degenerate zero-width interval around
    the single point: a one-observation "interval" of [x, x] would publish perfect
    confidence off one bill, which is the fail-open reading of this whole field.

    ``seed_key`` makes the draw deterministic per subject, so the published
    interval is reproducible from the same run artefact and a re-render is not a
    new measurement. R15 both ways: what MUST hold is independence from the
    `random` module's global state -- a bootstrap drawing from it reproduces only
    until something else in the publish run draws first, and that mutation is
    killed by a control. Keying the seed on ``seed_key`` rather than on a constant
    is ESTABLISHED AS AN EQUIVALENCE for every published figure, not assumed to be
    one: under a constant seed each month's interval is still a valid bootstrap of
    its own sample, and only the resample draws of two same-n months become
    correlated, which no published field reads. It is kept because decorrelating
    them is free, and it is deliberately not asserted, because a control that
    cannot name the defect it catches is one this project has paid for before.
    """
    n = len(sample)
    if n < 2:
        return (None, None)
    rng = random.Random(f"bill-shock-bound::{seed_key}")
    means = []
    for _ in range(_SHOCK_BOOTSTRAP_RESAMPLES):
        resample = [sample[rng.randrange(n)] for _ in range(n)]
        means.append(sum(resample) / n)
    means.sort()
    lo_pct, hi_pct = _SHOCK_BOOTSTRAP_TAILS_PCT
    lo = means[min(len(means) - 1, int(lo_pct / 100.0 * len(means)))]
    hi = means[min(len(means) - 1, int(hi_pct / 100.0 * len(means)))]
    return (lo, hi)


#: WHICH DEFINITION OF BILL SHOCK A PUBLISHED EVENT IS UNDER
#: (`docs/market_research/what_bill_shock_is.md`; `saas.bill_generator.
#: BILL_SHOCK_POPULATION_BY_PAYMENT_CHANNEL`). `"bill"` -- standard credit -- is the ONLY
#: population for whom the difference between two bills is the quantity the definition names.
#: For `"payment"` (a level direct debit, ~74% of GB households and 70.8% of our own events) the
#: bill is a statement that arrives and is filed, and the shock is a change in the amount
#: COLLECTED, which this codebase cannot yet measure because the DD amount is not a modelled
#: quantity. So its bill-to-bill difference is published UNDER ITS OWN NAME and explicitly not as
#: a shock: deleting it would hide 70.8% of the record, and leaving it inside `avg_shock_pct` is
#: the defect this split exists to end.
SHOCK_DEFINITION_POPULATION = "bill"
UNMEASURABLE_SHOCK_POPULATION = "payment"


def _shock_stats(sample, seed_key):
    """Mean/median/max/bound for one population's events in one month.

    EMPTY IS `None`, NEVER `0.0`. A month with no event in this population has not been
    measured at zero shock -- it has not been measured. `0.0` is what this field published
    before the split and it reads as "measured, and no shock", which is an unobservable
    turned into a published measured zero.
    """
    if not sample:
        return {"n": 0, "avg_pct": None, "median_pct": None, "max_pct": None,
                "ci95_low": None, "ci95_high": None}
    lo, hi = _bootstrap_mean_interval(sample, seed_key)
    return {
        "n": len(sample),
        "avg_pct": round(statistics.mean(sample) * 100, 1),
        "median_pct": round(statistics.median(sample) * 100, 1),
        "max_pct": round(max(sample) * 100, 1),
        "ci95_low": round(lo * 100, 1) if lo is not None else None,
        "ci95_high": round(hi * 100, 1) if hi is not None else None,
    }


def _annual_shock_by_population(data, years):
    """Each year's computable bill shocks, split by which DEFINITION applies to the household.

    THE SUBJECT IS A DIFFERENT AND LARGER ONE THAN ``monthly_ops``'. That series covers the
    bills already FLAGGED as shocks; this covers EVERY bill with a computable shock -- 6,094
    against 1,748 on the run this was written for. It is the population
    ``financial.annual[].avg_bill_shock_pct`` has always been a mean over, and it has always
    been a mean over both definitions at once.

    Read off ``data["bills"]`` rather than off a per-year reducer field, because the reducer
    (``saas.reporting.annual_report``) publishes only the mixed scalar -- the per-bill
    ``bill_shock_population`` exists on every bill and stops at the year boundary. Computing
    the split here needs no change to the producer, which matters beyond convenience: that
    file was carrying another lane's in-flight work when this was written, and a publishing
    concern does not belong in the run reducer anyway.

    ``mixed_all_population`` is deliberately kept. It is what the pre-split field was, in the
    same units as its siblings, so the re-partition reconciles from the artefact alone rather
    than from this diff -- and because ``avg_bill_shock_pct`` beside it is a FRACTION under a
    ``_pct`` name, a reader needs one figure in each system to see that without being caught
    by it.
    """
    from collections import defaultdict as _dd
    by_year = _dd(lambda: _dd(list))
    for b in data.get("bills", []):
        pct = b.get("bill_shock_pct")
        if pct is None:
            continue
        yr = (b.get("period_end") or "")[:4]
        if not yr:
            continue
        # No attribution is "unknown" -- its own value, never folded into either definition.
        by_year[yr][b.get("bill_shock_population") or "unknown"].append(float(pct))
    out = {}
    # Keyed on the years being PUBLISHED, not on the years that happen to have bills, so a
    # year with no computable shock carries an explicit empty block rather than a missing key
    # a consumer would read as "not applicable".
    for yr in years:
        pops = by_year.get(yr, {})
        block = {
            p: _shock_stats(pops.get(p, []), f"annual::{yr}::{p}")
            for p in ("payment", "bill", "out_of_scope", "unknown")
        }
        block["mixed_all_population"] = _shock_stats(
            [v for s in pops.values() for v in s], f"annual::{yr}::mixed"
        )
        out[yr] = block
    return out


def extract_monthly_ops(data):
    from collections import defaultdict as _dd
    shock_m = _dd(list)
    # The same events partitioned by WHICH DEFINITION applies to the household, which is decided
    # entirely by how it pays. Before 2026-09-01 these were averaged into one percentage across
    # populations that experience different things -- the failure the director named as this
    # project's most expensive recurring shape.
    shock_m_by_pop = _dd(lambda: _dd(list))
    likely_seasonal_count = 0
    genuine_shock_count = 0
    for yr, yd in data.get("years", {}).items():
        for e in yd.get("bill_shock_events", []):
            m = e.get("period_end", "")[:7]
            if m:
                pct = float(e.get("bill_shock_pct", 0))
                shock_m[m].append(pct)
                # An event with no attribution is "unknown" -- its own value, never silently
                # folded into either definition.
                shock_m_by_pop[m][e.get("bill_shock_population") or "unknown"].append(pct)
            # Additive 2026-07-10 (docs/design/BILL_SHOCK_DEFINITION_FINDING.md):
            # split the raw MoM shock count into "likely just seasonal" (large
            # MoM, small YoY, prior month wasn't itself a shock) vs "genuine"
            # -- a real business-surface consumer of the new YoY fields,
            # not just a computed-and-unused pair of dict keys.
            if e.get("bill_shock_likely_seasonal"):
                likely_seasonal_count += 1
            else:
                genuine_shock_count += 1
    comm_m = _dd(int)
    for yr, yd in data.get("years", {}).items():
        for wu in yd.get("committee_wake_ups", []):
            m = wu.get("settlement_date", "")[:7]
            if m:
                comm_m[m] += 1
    ret_m = _dd(lambda: {"offers": 0, "retained": 0})
    for r in data.get("retention_log", []):
        m = r.get("event_date", "")[:7]
        if m:
            ret_m[m]["offers"] += 1
            if r.get("outcome") == "retained":
                ret_m[m]["retained"] += 1
    all_months = sorted(set(list(shock_m.keys()) + list(comm_m.keys()) + list(ret_m.keys())))
    CRISIS = {"2021", "2022"}
    rows = []
    for m in all_months:
        sh = shock_m.get(m, [])
        rt = ret_m.get(m, {"offers": 0, "retained": 0})
        by_pop = shock_m_by_pop.get(m, {})
        pops = {
            p: _shock_stats(by_pop.get(p, []), f"{m}::{p}")
            for p in ("payment", "bill", "out_of_scope", "unknown")
        }
        # THE HEADLINE IS DEFINITION B ONLY. `avg_shock_pct` used to be the mean over every
        # population at once; it is now the mean over the households the arithmetic is actually
        # valid for. This does NOT flatter the figure -- the peak moves UP, from 315.6% (2016-08,
        # mixed) to 465.3% (2017-02, definition B) -- because 2016-08 had no definition-B event
        # in it at all. That the split makes the headline worse is the evidence it was not
        # chosen for its answer.
        b = pops[SHOCK_DEFINITION_POPULATION]
        rows.append({
            "month": m,
            "shock_count": b["n"],
            "avg_shock_pct": b["avg_pct"],
            # The bound the sample size earns, per the standing rule. `shock_count`
            # alone was never it: a reader handed "315.6% over 5 events" still has
            # no way to tell that month from a typical one, and five of the six
            # worst surviving months carry fewer than 20 events.
            "median_shock_pct": b["median_pct"],
            "avg_shock_pct_ci95_low": b["ci95_low"],
            "avg_shock_pct_ci95_high": b["ci95_high"],
            "max_shock_pct": b["max_pct"],
            # What the headline is a mean OVER, in the artefact rather than in a source comment.
            "avg_shock_pct_definition": SHOCK_DEFINITION_POPULATION,
            # Every population's own figures, so the 70.8% the headline no longer speaks for is
            # visible rather than deleted. `payment` is a bill-to-bill difference for households
            # who do not pay the bill: NOT a shock measure, and named so on the surface.
            "shock_by_population": pops,
            # Kept so a reader can see exactly what the pre-split series was, and so the size of
            # the re-partition is checkable from the artefact alone rather than from this diff.
            "mixed_all_population_avg_pct": (
                round(statistics.mean(sh) * 100, 1) if sh else None
            ),
            "mixed_all_population_count": len(sh),
            "committee_interventions": comm_m.get(m, 0),
            "retention_offers": rt["offers"],
            "retained": rt["retained"],
            "is_crisis": m[:4] in CRISIS,
        })

    # Demand-estimation accuracy per year (Operations tab KPI expansion backlog
    # item, 2026-07-10 -- PRIORITIES.md: real data already computed/rendered on
    # the Regulatory tab via saas/reporting/annual_report.py::
    # _section_demand_estimation(), just never surfaced as its own Operations
    # KPI. Same aggregation logic, reused here rather than duplicated
    # differently.)
    dem_by_year: dict[str, list[float]] = _dd(list)
    dem_source_counts: dict[str, dict[str, int]] = _dd(lambda: {"prior_billing": 0, "oracle_fallback": 0})
    for entry in data.get("demand_estimation_log", []):
        yr = entry.get("term_start", "")[:4]
        if not yr:
            continue
        dem_by_year[yr].append(abs(entry.get("error_pct", 0.0)))
        if entry.get("source") == "prior_billing":
            dem_source_counts[yr]["prior_billing"] += 1
        else:
            dem_source_counts[yr]["oracle_fallback"] += 1

    demand_estimation_annual = []
    for yr in sorted(dem_by_year.keys()):
        errs = dem_by_year[yr]
        n = len(errs)
        demand_estimation_annual.append({
            "year": int(yr),
            "renewal_count": n,
            "mean_abs_error_pct": round(sum(errs) / n, 1) if n else 0.0,
            "max_abs_error_pct": round(max(errs), 1) if errs else 0.0,
            "prior_billing_count": dem_source_counts[yr]["prior_billing"],
            "oracle_fallback_count": dem_source_counts[yr]["oracle_fallback"],
        })

    return {
        "monthly": rows,
        "demand_estimation_annual": demand_estimation_annual,
        # WHICH BILLS THIS SERIES IS A MEAN OVER, on the surface a reader is served
        # rather than in a source comment. `monthly[].avg_shock_pct` and
        # `financial.annual[].avg_bill_shock_pct` are both "the average bill shock"
        # and are means over different populations -- 110.6% and 30.8% for the same
        # 2016, a factor of 3.6 -- so a reader moving from the year row to the
        # monthly chart saw the number treble with nothing to tell them why.
        "avg_shock_pct_population": (
            "bills already flagged as a bill shock (month-on-month increase >=20%, "
            "bill_shock_tracker.BILL_SHOCK_THRESHOLD) -- NOT all bills. The "
            "all-bills mean is financial.annual[].avg_bill_shock_pct and is a "
            "different and much smaller number. SINCE 2026-09-01 it is ALSO restricted "
            "to the 'bill' population only -- see avg_shock_pct_definition_note."
        ),
        # THE DEFINITION, on the surface, because a reader cannot infer it from a number.
        "avg_shock_pct_definition_note": (
            "Bill shock is TWO experiences in two populations, not one experience with "
            "three causes (docs/market_research/what_bill_shock_is.md, sourced from Ofgem's "
            "credit-balance and Direct Debit Market Compliance publications and SLC 27.15/21BA "
            "-- there is no SLC 27B). "
            "Which one applies to a household is decided entirely by HOW IT PAYS. For standard "
            "credit ('bill', ~13% of GB households) the shock IS the bill, and the difference "
            "between two bills is the right quantity -- that is what avg_shock_pct now means, "
            "and only that. For a level direct debit ('payment', ~74% of GB households and "
            "70.8% of this book's events) the bill is a statement that arrives and is filed; "
            "the shock is a material change in the amount COLLECTED, which this codebase "
            "CANNOT YET MEASURE because the direct-debit amount is not a modelled quantity. "
            "Its bill-to-bill difference is published under shock_by_population.payment and is "
            "NOT a shock measure. Until 2026-09-01 these two were averaged into one percentage: "
            "the worst month on record, 2016-08 at 315.6%, contained ZERO 'bill'-population "
            "events and was therefore computed entirely from households the definition says the "
            "bill does not shock. Prepayment ('out_of_scope', ~13% of GB households) has neither "
            "a bill to be shocked by nor a direct debit to be changed; it is 0 here because this "
            "world has no prepayment channel, which is a known gap and not a measured zero."
        ),
        "avg_shock_pct_bound_note": (
            "avg_shock_pct is a mean over a right-skewed distribution (whole-book "
            "p99 is 19.8x the median), so median_shock_pct and the 95% bootstrap "
            "interval are published beside it and neither alone is the figure. A "
            "wide interval is this series saying it cannot tell that month from a "
            "typical one; months with fewer than 2 events cannot bound themselves "
            "and publish a null interval rather than a false one."
        ),
        "likely_seasonal_shock_count": likely_seasonal_count,
        "genuine_shock_count": genuine_shock_count,
    }


def extract_arrears_case_load(data):
    """Operations tab KPI expansion candidate (c), 2026-07-10 (PRIORITIES.md).
    Real per-year arrears/collections case load: reuses the exact same real
    data + DESNZ-anchored RAG bands already computed for the Regulatory-
    adjacent Population Anchoring section (saas/reporting/annual_report.py::
    _section_population_anchoring()) -- GREEN <8% (non-crisis)/<12% (crisis
    2021-23) active customers with an open arrears case that year, AMBER
    <15%/<18%, RED above. Reads the real billing ledger's arrears_history,
    same as that section, rather than duplicating a different definition.

    Availability is reported, not swallowed (2026-08-12): the shared reader in
    saas.reporting.arrears_ledger distinguishes an absent/unparseable ledger from a
    genuine zero, because this function used to render the first as a `green` row."""
    from saas.reporting.arrears_ledger import load as _load_arrears

    arrears = _load_arrears(PROJECT / "site" / "state" / "billing_ledger.json")

    rows = []
    for yr, yd in sorted(data.get("years", {}).items()):
        yr_int = int(yr)
        is_crisis = yr_int in (2021, 2022, 2023)
        active = yd.get("active_customer_ids", [])
        n_active = len(active)
        case_count = arrears.count_for(yr_int)
        if not arrears.available:
            # Distinct from "unknown" (which means zero active customers): here the
            # denominator is fine and the NUMERATOR's source never loaded.
            rate = None
            status = "unavailable"
        elif n_active > 0:
            rate = round(case_count / n_active * 100, 1)
            green_hi = 12.0 if is_crisis else 8.0
            amber_hi = 18.0 if is_crisis else 15.0
            status = "red" if rate > amber_hi else "amber" if rate > green_hi else "green"
        else:
            rate = None
            status = "unknown"
        rows.append({
            "year": yr_int,
            "case_count": case_count,
            "active_customers": n_active,
            "arrears_rate_pct": rate,
            "status": status,
            "is_crisis": is_crisis,
        })
    return {
        "annual": rows,
        "ledger_available": arrears.available,
        "ledger_unavailable_reason": arrears.unavailable_reason,
    }


def extract_dd_rails(data):
    """W5_1_banking_payment_rails (2026-07-12, L2->L3 attempt): the
    rails-timed DD collection book (mandate setup/collection/amendment,
    real AUDDIS/ARUDD/ADDACS timing, simulation/dd_collection_book.py) --
    exposed on a business surface for the first time. An Expert Hour review
    named "zero live pipeline callers, so it cannot live in time" as this
    atom's decisive remaining gap; this is the wiring plus surface that
    closes it. Portfolio summary plus one real, named customer example
    (EVIDENCE_IN_BUSINESS_SURFACES.md's own requirement -- a spec/aggregate
    alone is not evidence)."""
    book = data.get("dd_collection_book") or {}
    summary = book.get("summary") or {}
    mandates = book.get("mandates") or []
    attempts = book.get("attempts") or []

    attempts_by_customer = defaultdict(list)
    for a in attempts:
        attempts_by_customer[a.get("customer_id")].append(a)

    example = None
    if mandates:
        # The customer with the most observed rails history (most fully
        # evidenced instance), not just the first one alphabetically.
        best_cid = max(
            attempts_by_customer, key=lambda cid: len(attempts_by_customer[cid])
        ) if attempts_by_customer else mandates[0].get("customer_id")
        mandate = next((m for m in mandates if m.get("customer_id") == best_cid), None)
        if mandate:
            cust_attempts = sorted(
                attempts_by_customer.get(best_cid, []), key=lambda a: a.get("attempt_date", "")
            )
            example = {
                "customer_id": best_cid,
                "mandate_reference": mandate.get("mandate_reference"),
                "monthly_amount_gbp": mandate.get("monthly_amount_gbp"),
                "setup_confirmed_date": mandate.get("setup_confirmed_date"),
                "last_amendment_confirmed_date": mandate.get("last_amendment_confirmed_date") or None,
                "attempts": [
                    {
                        "attempt_date": a.get("attempt_date"),
                        "amount_gbp": a.get("amount_gbp"),
                        "outcome": a.get("outcome"),
                        "failure_reason": a.get("failure_reason", ""),
                    }
                    for a in cust_attempts[:12]
                ],
            }

    return {"summary": summary, "example_customer": example}


def extract_run_history(history_path=None, max_entries=10):
    """Return last N run history entries, or [] if absent/invalid."""
    path = history_path or RUN_HISTORY_PATH
    if not Path(path).exists():
        return []
    try:
        history = json.loads(Path(path).read_text())
        return history[-max_entries:] if len(history) > max_entries else history
    except (json.JSONDecodeError, ValueError):
        return []


def count_run_history_total(history_path=None):
    """Full count of every run ever recorded, not just the last N kept by
    extract_run_history() for display. The Project tab's "Sim runs" KPI used
    to read len(run_history) off the truncated list, so it always showed
    exactly max_entries (10) no matter how many runs had actually happened
    -- a dead counter (PROJECT_TAB_OVERHAUL.md critique)."""
    path = history_path or RUN_HISTORY_PATH
    if not Path(path).exists():
        return 0
    try:
        history = json.loads(Path(path).read_text())
        return len(history)
    except (json.JSONDecodeError, ValueError):
        return 0


# The 23 SLC/regulatory obligations shown on the Supplier Regulatory tab, each
# mapped onto one of the 10 compliance_scorecard.py domains so a real RAG status
# can be attached per row -- replaces the old hardcoded "Phase XXX" column
# (SUPPLIER_TAB_OVERHAUL.md: in-world rule + "add RAG compliance status per
# obligation from the compliance scorecard, not just 'tracked'").
_SLC_OBLIGATIONS = [
    ("SLC 2B", "Deemed Contract Register", "governance"),
    ("SLC 14", "Credit Refund (10 working days)", "billing_metering"),
    ("SLC 21B", "Account Closure & Final Bill (42 days)", "billing_metering"),
    ("SLC 21C", "Fuel Mix Disclosure (REGO-backed)", "environmental"),
    ("SLC 22", "Contract Notice & Renewal Obligations", "information_transparency"),
    ("SLC 25C", "Communication Channel Choice", "complaints"),
    ("SLC 26B", "Priority Services Register (9 categories)", "vulnerable_customers"),
    ("SLC 27", "Debt / Disconnection Moratorium Rules", "payment_debt"),
    ("SLC 27A", "Ability-to-Pay & Payment Plan Adequacy", "payment_debt"),
    ("SLC 31A", "Back-billing 12-Month Cap (May 2018+)", "billing_metering"),
    ("BSC SVA", "DA/DC Metering Agent Appointments", "network_balancing"),
    ("LC 30A", "Supplier Fitness & Proper Person Test", "governance"),
    ("UNC TPD", "Gas Nomination / Shipper Code", "network_balancing"),
    ("GDPR/PECR", "Data Breach Notification (72h ICO)", "governance"),
    ("UK EMIR", "Trade Repository Reporting (T+1)", "governance"),
    ("EBRS/EBSS", "Energy Bill Relief / Support Schemes", "billing_metering"),
    ("FRA", "Financial Resilience Assessment (12m min)", "financial_resilience"),
    ("IFRS 9", "Hedge Effectiveness (80-125% band)", "financial_resilience"),
    ("Consumer Duty", "Vulnerable Customer Outcomes & PSR", "vulnerable_customers"),
    ("WAM/WHD", "Warm Home Discount Phase 2", "vulnerable_customers"),
    ("FiT/SEG", "Smart Export Guarantee", "environmental"),
    ("RO/CfD", "Renewable Obligation / CfD Levy", "environmental"),
    ("CCL", "Climate Change Levy Ledger", "environmental"),
]


def extract_regulatory(data):
    """Per-obligation RAG for the Regulatory tab, sourced from the real
    ComplianceScorecard (company/regulatory/compliance_scorecard.py) already
    computed for the annual report -- not from build/phase metadata."""
    # NOT from saas.reporting.annual_report: a report is a rendering, never a thing
    # other code reads (director ruling 2026-08-19). The population step it used to
    # hold now has its own module and this is its only production caller.
    from saas.reporting.compliance_scorecard_population import (
        populate_compliance_scorecard,
    )
    from company.regulatory.compliance_scorecard import ComplianceDomain
    import datetime as dt

    years = sorted(data.get("years", {}).keys())
    scorecard = populate_compliance_scorecard(data) if years else None

    if scorecard is None:
        obligations = [
            {"code": code, "description": desc, "domain": domain_key,
             "status": "GREEN", "notes": ""}
            for code, desc, domain_key in _SLC_OBLIGATIONS
        ]
        return {"latest_year": None, "overall_rag": "GREEN", "obligations": obligations}

    latest_yr = years[-1]
    as_of = dt.date(int(latest_yr), 12, 31)
    obligations = []
    for code, desc, domain_key in _SLC_OBLIGATIONS:
        check = scorecard.latest_check(ComplianceDomain(domain_key))
        obligations.append({
            "code": code,
            "description": desc,
            "domain": domain_key,
            "status": check.status.value if check else "GREEN",
            "notes": check.notes if check else "",
        })

    return {
        "latest_year": latest_yr,
        "overall_rag": scorecard.overall_rag(as_of).value,
        "obligations": obligations,
    }


def extract_risk_tiered_compliance():
    """DOMAIN_SENSE_AND_COMPLIANCE.md Phase 4: the risk-tiered compliance
    report (company/compliance/compliance_report.py), distinct from
    extract_regulatory()'s existing RAG scorecard above -- this one carries
    the director's impact x likelihood risk tiering and, for the two
    obligations the Phase 3 pre-bill gate actually enforces, a LIVE status
    read from site/state/billing_ledger.json's held_bill_count (the gate's
    own real exception-queue count), not a build/phase metadata guess."""
    from company.compliance.compliance_report import build_compliance_report

    ledger_path = PROJECT / "site" / "state" / "billing_ledger.json"
    held_bill_count = 0
    if ledger_path.is_file():
        try:
            ledger = json.loads(ledger_path.read_text())
            held_bill_count = ledger.get("meta", {}).get("held_bill_count", 0)
        except (json.JSONDecodeError, OSError):
            held_bill_count = 0
    return build_compliance_report(held_bill_count=held_bill_count)


def extract_reputation(data):
    """Phase RU (FEEDBACK_AND_REPUTATION.md Layer 1): company CSAT/NPS
    dashboard reading only solicited survey responses, plus the Global
    Reputation Index trajectory -- now live off real complaint-resolution
    events (simulation/feedback_survey.py) instead of pinned at baseline 50."""
    nps_annual = data.get("nps_annual_summaries", {}) or {}
    complaint_annual = data.get("complaint_annual_summaries", {}) or {}
    gri_trajectory = data.get("gri_trajectory", []) or []
    reputation_events = data.get("reputation_events_log", []) or []

    years_with_responses = sorted(
        (yr for yr, s in nps_annual.items() if s and s.get("responses")),
        key=lambda y: int(y),
    )
    latest_nps = nps_annual.get(years_with_responses[-1]) if years_with_responses else None
    latest_gri = gri_trajectory[-1] if gri_trajectory else None

    return {
        "nps_annual": nps_annual,
        "complaint_annual": complaint_annual,
        "gri_trajectory": gri_trajectory,
        "reputation_events": reputation_events,
        "latest_nps": latest_nps,
        "latest_gri": latest_gri,
        "total_reputation_events": len(reputation_events),
    }


def extract_nudge_discovery(data):
    """Nudge Physics Layer 1 (NUDGE_PHYSICS.md): company-observable
    discovered-lift table (framing_type x segment retention rate) plus a
    Consumer Duty concentration check -- the company never reads the
    SIM-side loss-aversion susceptibility that actually drives the effect.
    """
    from company.analytics.nudge_discovery import (
        compute_framing_lift_by_segment, assess_framing_consumer_duty,
    )
    from dataclasses import asdict
    # Book resolved through the single `live_population()` seam (generator
    # draw-wiring, PRODUCT-FIRST item 2, report-lookup generator #2):
    # BYTE-IDENTICAL while `SE_DRAW_POPULATION` is off, additively carrying the
    # SYN acquisition cohort into the lift table when the flag is on.
    _CUSTS = _resolve_book()

    retention_log = data.get("retention_log", []) or []
    lift = compute_framing_lift_by_segment(retention_log, _CUSTS)
    as_of = data.get("years", {})
    latest_year = max((int(y) for y in as_of.keys()), default=2025)
    assessment = assess_framing_consumer_duty(lift, str(latest_year) + "-12-31")
    return {
        "lift_by_segment": [asdict(x) for x in lift],
        "consumer_duty": {
            "rag": assessment.rag.value,
            "metric_name": assessment.metric_name,
            "metric_value": assessment.metric_value,
            "narrative": assessment.narrative,
            "assessment_date": assessment.assessment_date,
        },
    }


#: How many accounts the NL-query context may NAME. Enough to answer "who makes and loses
#: the money" from the extremes, far short of a per-account ledger. The block this bounds
#: was 94% of the context and had no bound at all; see the note inside the function.
QUERY_CONTEXT_NAMED_CUSTOMERS = 12


def extract_query_context(data):
    """Build compact text summary (~2-4k chars) for NL query API context."""
    if not data:
        return ""
    lines = ["=== UK Energy Supplier Simulation (2016-2025) ===", ""]
    ledger = data.get("ledger_pnl", {})
    lines.append("PORTFOLIO 10-YEAR TOTALS:")
    lines.append("  Revenue: GBP{:,.0f}".format(ledger.get("revenue_gbp", 0)))
    lines.append("  Gross margin: GBP{:,.0f}".format(ledger.get("gross_margin_gbp", 0)))
    lines.append("  Net margin: GBP{:,.0f}".format(ledger.get("net_margin_gbp", 0)))
    lines.append("  Bad debt: GBP{:,.0f}".format(ledger.get("bad_debt_gbp", 0)))
    lines.append("")
    lines.append("ANNUAL PERFORMANCE:")
    for yr in sorted(data.get("years", {}).keys()):
        ydata = data["years"][yr]
        net = ydata.get("net_gbp", 0)
        gross = ydata.get("gross_gbp", 0)
        rev = ydata.get("revenue_gbp", 0)
        active = len(ydata.get("active_customer_ids", []))
        shocks = len(ydata.get("bill_shock_events", []))
        worst = max((e.get("bill_shock_pct", 0) for e in ydata.get("bill_shock_events", [])), default=0)
        hf_data = ydata.get("hedge_fractions", {})
        avgs = [v.get("avg_hf", 0) for v in hf_data.values() if isinstance(v, dict)] if isinstance(hf_data, dict) else []
        hf_str = "  hedge={:.0f}pct".format(statistics.mean(avgs) * 100) if avgs else ""
        row = "  {}: net=GBP{:,.0f}  gross=GBP{:,.0f}  rev=GBP{:,.0f}  customers={}  bill_shocks={}".format(
            yr, net, gross, rev, active, shocks)
        if worst:
            row += "  worst_shock={:.0f}pct".format(worst * 100)
        row += hf_str
        lines.append(row)
    lines.append("")
    # BOUNDED, NEVER DROPPED (2026-08-27) -- the same shape as `doorbell_redaction`'s
    # MAX_NAMED_DOCUMENTS, and for the same reason.
    #
    # This block enumerated EVERY account. On the book of 2026-08-15 that was a couple of dozen
    # lines; measured today it is 24,833 characters of 26,368 -- 94% of a summary whose own
    # docstring promises "~2-4k chars" -- and it broke the 8,000-char limit
    # `test_extract_query_context_under_size_limit` sets for the API context window. The book
    # grew (drawn population, then a gas leg per dual-fuel home) and an unbounded per-row
    # enumeration grew with it. Nothing here malfunctioned; the shape was always O(book) inside
    # a function that had promised to be O(1).
    #
    # THE EXTREMES ARE KEPT, not the alphabetical head. A question worth asking this context is
    # "who makes and loses the money", so the best and worst by net margin are what survive; a
    # `sorted(...)` prefix would have returned whichever accounts happen to sort first, which
    # answers nothing. The remainder becomes a COUNT and a pointer, so a reader always knows
    # what was left out and where the whole list lives.
    per_customer = data.get("per_customer_lifetime", {})
    ranked = sorted(per_customer.items(), key=lambda kv: kv[1].get("net_gbp", 0), reverse=True)
    shown = ranked[:QUERY_CONTEXT_NAMED_CUSTOMERS] if len(ranked) > QUERY_CONTEXT_NAMED_CUSTOMERS \
        else ranked
    tail = ranked[-QUERY_CONTEXT_NAMED_CUSTOMERS:] if len(ranked) > 2 * QUERY_CONTEXT_NAMED_CUSTOMERS \
        else []
    lines.append("CUSTOMER LIFETIME NET MARGIN ({} accounts{}):".format(
        len(ranked),
        "" if not tail else ", best and worst {} shown".format(QUERY_CONTEXT_NAMED_CUSTOMERS)))
    for cid, cdata in shown:
        lines.append("  {} ({}, {}): net=GBP{:,.0f}  revenue=GBP{:,.0f}".format(
            cid, cdata.get("segment", ""), cdata.get("commodity", ""),
            cdata.get("net_gbp", 0), cdata.get("revenue_gbp", 0)))
    if tail:
        omitted = len(ranked) - len(shown) - len(tail)
        if omitted > 0:
            lines.append("  ... {} further accounts omitted -- the full per-account book is "
                         "`per_customer_lifetime` in docs/reports/run_output_latest.json"
                         .format(omitted))
        for cid, cdata in tail:
            lines.append("  {} ({}, {}): net=GBP{:,.0f}  revenue=GBP{:,.0f}".format(
                cid, cdata.get("segment", ""), cdata.get("commodity", ""),
                cdata.get("net_gbp", 0), cdata.get("revenue_gbp", 0)))
    lines.append("")
    retention = data.get("retention_log", [])
    retained = sum(1 for r in retention if r.get("outcome") == "retained")
    churned = data.get("churned_billing_accounts", [])
    lines.append("CUSTOMER RETENTION:")
    lines.append("  Retention offers: {}  retained: {}  churned accounts: {}".format(
        len(retention), retained, len(churned)))
    lines.append("")
    bills_total = data.get("bills_total", 0)
    committee_total = data.get("committee_wake_ups_total", 0)
    lines.append("OPERATIONS:")
    lines.append("  Total bills: {}  Risk committee interventions: {}".format(bills_total, committee_total))
    return chr(10).join(lines)


def _load_frozen_baseline(path=None):
    """Load site/state/frozen_policy_baseline.json (FROZEN_POLICY_BASELINE_DESIGN.md
    option B) if it exists. This is a periodic, on-demand artifact -- a full
    decade replayed twice (current vs naive policy) -- not regenerated every
    sim cycle, so it may be older than the rest of this dashboard. Returns
    {} if not yet generated."""
    if path is None:
        path = PROJECT / "site" / "state" / "frozen_policy_baseline.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def generate(run_json_path=None):
    if run_json_path is None:
        run_json_path = _find_latest_run_json()
    if run_json_path is None:
        print("No run output JSON found", file=sys.stderr)
        return False

    run_json_path = Path(run_json_path)
    print(f"Loading run output: {run_json_path.name}")
    with open(run_json_path) as f:
        data = json.load(f)

    print("Loading Elexon SSP (may take a few seconds)...")
    spot_monthly = load_spot_monthly()
    print(f"  {len(spot_monthly)} monthly spot price points")

    # Extract meta
    cache_meta = data.get("_cache_meta", {})
    # Provenance must name a commit or admit it cannot. The old fallback parsed
    # the RUN FILENAME -- run_output_latest.json yielded the literal string
    # "latest", which every published door then carried as its git_commit. That
    # is the textbook fail-open: it satisfies any presence check forever and can
    # never contradict a claim, breaking the audit chain at its root while
    # looking populated (cold-eyes Expert Hour 2026-07-29). Real HEAD, or the
    # honest string "unknown" -- never a filename fragment dressed as a SHA.
    git_commit = cache_meta.get("git_commit") or _git_head() or "unknown"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    build_phase, build_test_count, build_modules = _load_build_info()
    portfolio = extract_portfolio(data)
    insights = extract_insights()

    dashboard = {
        "meta": {
            "generated_at": generated_at,
            "git_commit": git_commit,
            "source_file": run_json_path.name,
            "spot_monthly_count": len(spot_monthly),
        },
        "portfolio": portfolio,
        "financial": extract_financial(data),
        "trading": extract_trading(data, spot_monthly),
        "customers": extract_customers(data),
        "market": extract_market(data, spot_monthly),
        "regulatory": extract_regulatory(data),
        "risk_tiered_compliance": extract_risk_tiered_compliance(),
        "reputation": extract_reputation(data),
        "nudge_discovery": extract_nudge_discovery(data),
        "insights": insights,
        "run_history": extract_run_history(),
        "run_history_total": count_run_history_total(),
        "query_context": extract_query_context(data),
        "management_accounts": extract_management_accounts(data),
        "monthly_ops": extract_monthly_ops(data),
        "arrears_case_load": extract_arrears_case_load(data),
        "dd_rails": extract_dd_rails(data),
        "flexibility": extract_flexibility(data),
        "opex_ledger": extract_opex_ledger(data),
        "b2_taxonomy": extract_b2_taxonomy(data),
        "churn_model_performance": data.get("churn_model_performance", {}),
        "frozen_baseline": _load_frozen_baseline(),
        "build": {
            "current_phase": build_phase,
            "phases_built": f"Phase {build_phase} (300+ total)",
            "test_count": build_test_count,
            "test_suite": f"{build_test_count:,}+ (non-sim)",
            "company_modules": build_modules,
            "simulation_window": "2016-2025",
            "regulatory_modules": 48,
        },
    }

    # RETIRED 2026-08-20 (director): the dashboard-vs-exec-summary comparison used to
    # sit here and contribute to the verdict below. It compared a PUBLISHED number
    # (dashboard totals, which /proof/ and /world/ render) against an UNPUBLISHED one
    # (run_insights.json, written to docs/observability/ and fetched by no page on the
    # site), and raised a director-facing real_alarm every time two derived snapshots
    # of the same run drifted apart. Nothing read the second surface, so keeping the
    # two consistent was the entire job it did.
    #
    # The seven checks that REMAIN all compare the dashboard against its own sources or
    # against itself, and each one declares the page it guards in PUBLISH_VERDICT_CHECKS
    # below. tools/reader_reachability.py answers whether a reader can open that page,
    # and tests/tools/test_publish_blockers_guard_a_reachable_page.py fails the commit if
    # any of them cannot -- so this class cannot come back by accretion.
    population_ok = _check_population_consistency(data, dashboard)
    _basis_ok = _check_basis_labels_present(portfolio)
    # The label being PRESENT and the label being TRUE are two checks; the
    # margin-basis finding got past the first one for the whole life of the
    # defect (2026-08-17).
    _parentage_ok = _check_derived_basis_parentage(portfolio)
    _bridge_ok = _check_bridge_reconciles()
    _bad_debt_ok = _check_bad_debt_reconciliation_present(dashboard["financial"])
    _period_ok = _check_period_coverage_present(dashboard["financial"])
    mix_claim_ok = _check_front_door_segment_claim(dashboard)
    # Only the checks whose figures a reader can actually reach decide the verdict. The other
    # five still ran above and printed their diagnosis; see REPORTED_NOT_BLOCKING for why they
    # are reported rather than gating, and what would put them back.
    consistency_ok = population_ok and mix_claim_ok

    # THE OPENING DIRECT DEBIT, BOTH ARMS. Written on the publish path rather than
    # composed into `dashboard` because the block is a comparison of two runs of one
    # organ, not a figure of this run -- and because a fail-closed block belongs in a
    # feed the page fetches, so an absent artefact renders a stated absence on screen
    # instead of a key the renderer silently skips.
    _write_dd_opening_arms_feed()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(dashboard, f, separators=(",", ":"))

    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"Wrote {OUTPUT_PATH} ({size_kb:.1f} KB)")
    return consistency_ok


# ── WHAT EACH PUBLISH-BLOCKING CHECK IS FOR ──────────────────────────────────────────────
# Director ruling, 2026-08-20: "a surface no reader can reach must never be able to block
# publishing." generate()'s verdict decides whether a run raises the consistency alarm, so
# every check in that conjunction is a publish blocker and must name the reader-facing page
# whose figures go wrong if it fires. A check that cannot name one is guarding nobody.
#
# This is a RATCHET with all three directions, driven from
# tests/tools/test_publish_blockers_guard_a_reachable_page.py:
#   - a check in the conjunction with no entry here          -> FAIL (undeclared blocker)
#   - an entry naming a page a reader cannot reach           -> FAIL (the ruling itself)
#   - an entry for a check that is no longer in the verdict  -> FAIL (stale declaration)
# The third direction is the one that rots quietly: without it this table becomes a list of
# what the gate used to do, which is how the exec-summary comparison survived a month past
# the redirect that made it pointless.
PUBLISH_VERDICT_CHECKS = {
    # RE-HOMED 2026-08-20, and this control caught it rather than a person noticing. The fold
    # deleted /proof/ and /world/ -- the only two pages that fetched dashboard.json -- so for a
    # few minutes all seven checks guarded figures no reader could reach, and
    # tests/tools/test_publish_blockers_guard_a_reachable_page.py went red naming every one.
    #
    # THE TWO THAT STAYED guard something a reader now meets on the front page: the account
    # count and the years-settled figures added there on the same day, and the segment-mix
    # sentence that has always been there.
    "_check_population_consistency": ("/", "the account count and settlement window on the front page"),
    "_check_front_door_segment_claim": ("/", "the front door's segment-mix claim matches the book"),
}

#: REPORTED, NEVER BLOCKING -- and the reason is a genuine conflict between two director
#: instructions, which is not this module's to resolve.
#:
#: RC7 (DIRECTOR_RULING_IDEA_FIRST_EXTERNAL_REGISTER, 2026-07-24) forbids any cohort-derived
#: pound aggregate from leading a public surface: "a share of revenue and an account count,
#: never a total". DIRECTOR_BRIEF_WEBSITE_STRUCTURE (2026-08-17) §4 asks Home for "three live
#: figures ... book size, margin, carbon". Margin cannot be both forbidden and required.
#:
#: While that stands, net margin, gross margin, enterprise value, the margin bridge, bad debt
#: and period coverage are published on NO page a reader can open. By the director's rule of
#: 2026-08-20 -- "a surface no reader can reach must never be able to block publishing" -- they
#: therefore cannot gate a publish. They still RUN and still print their diagnosis to stderr on
#: every cycle, so the moment the conflict is resolved and the figures get a home, re-declaring
#: them above is a one-line change and nothing has rotted in the meantime.
#:
#: This is deliberately not a quiet weakening: it is written down, it names the two
#: instructions in tension, and the checks are still executing.
REPORTED_NOT_BLOCKING = {
    "_check_basis_labels_present": "net margin / enterprise value carry a clock",
    "_check_derived_basis_parentage": "those figures state the cost basis beneath them",
    "_check_bridge_reconciles": "the settled-to-billed margin gap is fully explained",
    "_check_bad_debt_reconciliation_present": "bad debt reconciles against the ledger",
    "_check_period_coverage_present": "the period a figure covers is stated",
}


# Headline figures that must carry a basis label (CLAUDE.md standing rule,
# CLOCK_TRUTH_AND_THE_BRIDGE.md 2026-07-12): "No financial figure is
# published without its clock. A number whose basis is unstated is a defect,
# not a formatting choice."
#
# WHICH FIGURES ARE THE SUBJECT IS DERIVED, NOT A HAND-KEPT LIST
# (2026-08-22, E5_carbon_three_ledger FRAME control C4, promoted from the
# instance to the class per R10.)
#
# This was `_BASIS_REQUIRED_PORTFOLIO_KEYS = ("net_margin_gbp",
# "enterprise_value_gbp")` -- a two-name allowlist. R14 says EVERY published
# financial figure carries its clock; an allowlist inverts that, because a
# figure is checked only if somebody remembered to name it. So every new
# headline figure was BORN UNCHECKED and passed this gate by never being its
# subject: fail-silent, the third of R15's three killer patterns.
#
# E5's FRAME surfaced it as one instance -- a published tCO2e figure "would
# pass the R14 basis gate BY NEVER BEING CHECKED" -- and named the class-fix
# explicitly ("extend the gate's subject set rather than append two keys").
# Running the derived rule over the real extract_portfolio before changing
# anything showed the class was already live, not hypothetical: SEVEN keys
# carry a published-money suffix and only TWO were named. The other five --
# gross_margin_gbp, treasury_start_gbp, treasury_end_gbp, cost_to_serve_gbp,
# net_after_cts_gbp -- have been published with no clock at all, invisible to
# the one gate that exists to see exactly that.
#
# Those five are NOT silently grandfathered, and they are NOT given invented
# labels either: asserting a clock nobody has established is precisely the
# false claim R14 exists to prevent. They are declared BY NAME with a reason
# below, which makes the debt enumerable and, the point of the exercise,
# NON-GROWABLE -- a figure added tomorrow is not on the list, so it fails.
#
# Three-direction ratchet, same shape as the publish-blocker table further
# down, driven from tests/tools/test_generate_dashboard_data_basis_subject_set.py:
#   - a suffixed portfolio key with no basis entry and no declaration -> FAIL
#   - a declaration for a key extract_portfolio no longer emits        -> FAIL (stale)
#   - a declaration for a key that HAS acquired a real basis entry     -> FAIL (stale)
_BASIS_REQUIRED_SUFFIXES = ("_gbp", "_tco2e")

#: Figures that predate the derived rule and publish WITHOUT a clock. Each
#: entry is an admission of debt, never a finding that no clock is needed.
#: Removing an entry is the repair; adding one needs the same justification
#: in writing, and the ratchet test above will not let one rot here unread.
_BASIS_DECLARED_UNLABELLED = {
    "gross_margin_gbp": (
        "settlement-derived like net_margin_gbp but has never been given its own "
        "basis entry; inherits that line's settled/billed divergence and would need "
        "its own bridge row before a clock could be asserted honestly"
    ),
    "treasury_start_gbp": (
        "a treasury BALANCE, not a margin -- its clock is 'banked', but the "
        "banked-clock definition for opening/closing balances has not been written "
        "down anywhere a reader can check, so stating it here would be an assertion"
    ),
    "treasury_end_gbp": "same as treasury_start_gbp -- the closing side of the same unwritten balance clock",
    "cost_to_serve_gbp": (
        "activity-derived (G11_activity_cost_utilisation), whose own coverage limit is "
        "an open finding; a clock label would imply a completeness this figure does not have"
    ),
    "net_after_cts_gbp": "computed FROM net_margin_gbp and cost_to_serve_gbp, so it cannot carry a cleaner basis than the latter",
}


def _write_dd_opening_arms_feed():
    """Publish the two-arm opening-direct-debit comparison, or a named absence.

    `tools.dd_opening_arms.publish_view` decides what a reader meets; this function
    only decides WHEN. A missing or unparseable artefact is handed to it as `None`,
    which is why there is no path here that writes an empty block: an absent
    comparison and a comparison that found nothing must not render the same, and
    this feed was created because for one publish they did.
    """
    from tools.dd_opening_arms import publish_view

    result = None
    if DD_ARMS_ARTEFACT.is_file():
        try:
            result = json.loads(DD_ARMS_ARTEFACT.read_text())
        except (json.JSONDecodeError, OSError):
            result = None
    block = publish_view(result)
    DD_ARMS_FEED.parent.mkdir(parents=True, exist_ok=True)
    DD_ARMS_FEED.write_text(json.dumps(block, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {DD_ARMS_FEED} (available={block.get('available')})")


def _basis_required_portfolio_keys(portfolio):
    """The gate's subject set, DERIVED from the portfolio being published
    rather than declared ahead of it -- see the block above for why an
    allowlist here is fail-silent by construction. Any key naming a published
    money or carbon quantity is a subject unless it is explicitly declared
    unlabelled."""
    return tuple(sorted(
        key for key in portfolio
        if isinstance(key, str)
        and key.endswith(_BASIS_REQUIRED_SUFFIXES)
        and key not in _BASIS_DECLARED_UNLABELLED
    ))


def _check_basis_labels_present(portfolio):
    """Extends the page-consistency invariant (CLOCK_TRUTH_AND_THE_BRIDGE.md):
    any published financial figure lacking a basis label fails the gate. A
    missing/incomplete portfolio.basis entry for a headline GBP figure is a
    defect, caught here rather than shipping an unlabelled number to the
    front door (the exact failure this rule exists to prevent)."""
    basis = portfolio.get("basis", {}) or {}
    missing = []
    for key in _basis_required_portfolio_keys(portfolio):
        if portfolio.get(key) is None:
            continue
        entry = basis.get(key)
        if not entry or not entry.get("clock") or "provisional" not in entry or not entry.get("note"):
            missing.append(key)
    if missing:
        print(
            "BASIS-LABEL GATE FAILED: headline figure(s) missing a basis label -- {}".format(
                ", ".join(missing)
            ),
            file=sys.stderr,
        )
        return False
    # The declared-unlabelled debt is REPORTED on every cycle, never silent --
    # a register nobody reads is how five figures got here in the first place.
    declared = sorted(k for k in portfolio if k in _BASIS_DECLARED_UNLABELLED)
    if declared:
        print(
            "BASIS-LABEL DEBT: {} published figure(s) still carry no clock -- {}".format(
                len(declared), ", ".join(declared)
            ),
            file=sys.stderr,
        )
    return True


# ---------------------------------------------------------------------------
# FRONT-DOOR SEGMENT-CLAIM COHERENCE GATE
# (SITE_EH1_segment_disclosure, 2026-07-30, scope item 2 + R10 class fix)
#
# The front door states the book's revenue mix in words BEFORE the mission claim,
# because a household-carbon mission read over a ~99%-non-domestic book misleads by
# ordering alone. That surface renders no live figure and carries no inline script
# (the documented post-condition of DIRECTOR_RULING_FRONT_MISSION_BLOCK), so the
# sentence is hand-authored -- which means it can ROT into a false public claim the
# moment the drawn book changes shape. Irretractable public claims are a one-way
# door (CLAUDE.md door 3), so a false one must BLOCK the publish, not be noticed
# later by a human.
#
# The claim is machine-readable: site/index.html carries
#   data-mix-claim="non_domestic_revenue_share_gt_<NN>"   -- an I&C-dominated book
#   data-mix-claim="non_domestic_revenue_share_lt_<NN>"   -- a domestic book
# and this gate recomputes the real share from the run's OWN segment split and
# fails if the claim no longer holds.
#
# WHY BOTH DIRECTIONS EXIST (2026-08-30). The gate was born when the book was ~99%
# non-domestic, so `gt` was the only shape the disclosure ever needed. On 2026-08-24 the
# director suspended I&C supply and the book flipped to 98.35% domestic; the prose in the
# bookmix section was rewritten that day to say so ("This book is households"), but its
# machine-readable form could not be: there was no way to WRITE "this book is domestic" in
# a grammar that only says "greater than". The attribute was left at `gt_95` asserting the
# exact opposite of the paragraph beneath it, and the gate correctly went red and stayed
# red -- the front door carried a false machine claim for six days.
#
# The fix is NOT to weaken the claim to something 1.65% happens to satisfy (`gt_0` passes
# today and would go on passing if the book flipped back to I&C -- a control keyed to
# today's answer instead of to the property, which is the failure this project keeps
# paying for). It is to give the disclosure the direction it actually makes, so a `lt`
# claim fails the moment the book stops being domestic.
#
# INDEPENDENCE (R15 anti-tautology): the CLAIM is parsed from the hand-authored HTML;
# the VALUE is computed from dashboard.financial.segment_annual. Two different
# sources, so they can genuinely disagree -- which is the entire point.
# FAIL-CLOSED: a missing/malformed claim attribute, an unparseable threshold, an
# unreadable front door, or an unavailable mix all FAIL. An unavailable check is a
# FAILED check (R15 fail-silent), and "no claim found" must never mean "claim fine".
# ---------------------------------------------------------------------------
FRONT_DOOR_PATH = PROJECT / "site" / "index.html"
_MIX_CLAIM_RE = re.compile(r'data-mix-claim="non_domestic_revenue_share_(gt|lt)_(\d{1,3})"')
#: The comparison each claim direction asserts, and the symbol its refusal prints. An
#: attribute whose direction is neither of these does not match the regex at all, so it
#: reads as "no claim found" -> FAIL, never as a pass by absence.
_MIX_CLAIM_OPS = {"gt": (operator.gt, ">"), "lt": (operator.lt, "<")}


def _check_front_door_segment_claim(dashboard, front_door_path=FRONT_DOOR_PATH):
    from tools.generate_company_data import segment_revenue_mix

    try:
        html = front_door_path.read_text()
    except OSError as exc:
        print(
            "FRONT-DOOR MIX-CLAIM GATE FAILED: front door unreadable ({}) -- an "
            "unavailable check is a FAILED check, not a pass".format(exc),
            file=sys.stderr,
        )
        return False

    matches = _MIX_CLAIM_RE.findall(html)
    if not matches:
        print(
            "FRONT-DOOR MIX-CLAIM GATE FAILED: no data-mix-claim="
            '"non_domestic_revenue_share_gt_<NN>" (an I&C book) or '
            '"non_domestic_revenue_share_lt_<NN>" (a domestic one) on the front door. The '
            "segment disclosure that must precede the mission claim is missing or was edited "
            "into an unverifiable form (SITE_EH1_segment_disclosure). NAMING BOTH DIRECTIONS "
            "deliberately: for six days in August 2026 this refusal offered only `gt`, while "
            "the book was domestic and the true claim was unwritable -- a refusal that names "
            "only half its grammar reads as 'you typed it wrong' when the answer is 'the "
            "vocabulary cannot say what is true'.",
            file=sys.stderr,
        )
        return False

    mix = segment_revenue_mix((dashboard.get("financial") or {}).get("segment_annual"))
    if not mix.get("available"):
        print(
            "FRONT-DOOR MIX-CLAIM GATE FAILED: the book's segment mix is unavailable "
            "({}), so the front door's published mix claim cannot be verified".format(
                mix.get("reason")
            ),
            file=sys.stderr,
        )
        return False

    actual = mix["non_domestic_revenue_share_pct"]
    for direction, raw in matches:
        compare, symbol = _MIX_CLAIM_OPS[direction]
        threshold = float(raw)
        if not compare(actual, threshold):
            print(
                "FRONT-DOOR MIX-CLAIM GATE FAILED: the front door claims non-domestic "
                "revenue share {} {:.0f}%, but this run's book is {:.2f}% non-domestic "
                "({} composition). The published sentence is now FALSE -- fix the "
                "sentence (it is a disclosure, not a target: never reweight the book to "
                "make it true, R12/R13).".format(symbol, threshold, actual,
                                                 mix["composition_class"]),
                file=sys.stderr,
            )
            return False
    return True


MARGIN_BRIDGE_PATH = PROJECT / "site" / "data" / "margin_bridge.json"
BRIDGE_TOLERANCE_GBP = 5.0


def _check_bridge_reconciles():
    """D2_three_clocks (2026-07-12, ADVISOR_STEER_TWIN_READONLY.md): the
    settlement<->billed reconciliation this atom exists to build must be a
    first-class, ALWAYS-ON mechanism, not a script someone remembers to run.
    process_run_complete.py now regenerates site/data/margin_bridge.json
    every cycle before this gate runs; this function is that gate --
    unexplained_remainder_gbp drifting beyond a rounding tolerance means the
    bridge (or the two clocks it reconciles) has silently broken, and that
    must fail loudly here rather than ship a front door nobody can trust.
    Missing file degrades gracefully (True) rather than blocking every other
    dashboard generation on this one atom's own bridge existing yet."""
    if not MARGIN_BRIDGE_PATH.exists():
        return True
    try:
        bridge = json.loads(MARGIN_BRIDGE_PATH.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"BRIDGE-RECONCILE GATE FAILED: margin_bridge.json unreadable -- {exc}", file=sys.stderr)
        return False
    remainder = bridge.get("unexplained_remainder_gbp")
    if remainder is None:
        print("BRIDGE-RECONCILE GATE FAILED: unexplained_remainder_gbp missing", file=sys.stderr)
        return False
    if abs(remainder) > BRIDGE_TOLERANCE_GBP:
        print(
            f"BRIDGE-RECONCILE GATE FAILED: unexplained_remainder_gbp={remainder:,.2f} "
            f"exceeds tolerance ({BRIDGE_TOLERANCE_GBP:,.2f}) -- the settlement<->billed "
            "reconciliation no longer holds, investigate the mechanism (R4), do not raise "
            "the tolerance to make this pass.",
            file=sys.stderr,
        )
        return False
    return True


def _check_bad_debt_reconciliation_present(financial):
    """SITE_EH3_figure_reconciliation_and_periods MAJOR-4 (R10 class-closure):
    bad debt was previously published TWICE (129.6x apart) with no bridge --
    this gate fails CLOSED, never open, on: the reconciliation block missing
    entirely; any required field missing/empty; a non-finite total (reject
    non-finite FIRST); or the STORED annual total silently drifting from an
    INDEPENDENT re-sum of financial['annual'] (anti-tautology -- this gate
    re-derives the total from the raw per-year rows rather than trusting the
    stored aggregate back at itself)."""
    br = financial.get("bad_debt_reconciliation")
    if not isinstance(br, dict):
        print("BAD-DEBT RECONCILIATION GATE FAILED: bad_debt_reconciliation missing", file=sys.stderr)
        return False
    required = (
        "annual_series_total_gbp", "ledger_total_gbp", "authoritative",
        "note", "annual_series_basis", "ledger_basis",
    )
    missing = [k for k in required if br.get(k) in (None, "")]
    if missing:
        print(f"BAD-DEBT RECONCILIATION GATE FAILED: missing field(s) {missing}", file=sys.stderr)
        return False
    annual_total = br["annual_series_total_gbp"]
    ledger_total = br["ledger_total_gbp"]
    # Reject non-finite FIRST, before any arithmetic/comparison on these values.
    if not (isinstance(annual_total, (int, float)) and math.isfinite(annual_total)):
        print("BAD-DEBT RECONCILIATION GATE FAILED: annual_series_total_gbp is not a finite number", file=sys.stderr)
        return False
    if not (isinstance(ledger_total, (int, float)) and math.isfinite(ledger_total)):
        print("BAD-DEBT RECONCILIATION GATE FAILED: ledger_total_gbp is not a finite number", file=sys.stderr)
        return False
    rows = financial.get("annual", [])
    resum = round(sum(r.get("bad_debt_gbp", 0.0) for r in rows), 2)
    if abs(resum - annual_total) > 1.0:
        print(
            f"BAD-DEBT RECONCILIATION GATE FAILED: stored annual_series_total_gbp="
            f"{annual_total} disagrees with an independent re-sum of financial['annual']="
            f"{resum}", file=sys.stderr,
        )
        return False
    if br["authoritative"] != "ledger":
        print(
            "BAD-DEBT RECONCILIATION GATE FAILED: authoritative figure must be 'ledger' "
            "(the plausible, in-Ofgem/EUA-band figure) -- never silently switched",
            file=sys.stderr,
        )
        return False
    return True


_PERIOD_COVERAGE_PARTIAL_THRESHOLD = 0.999


def _check_period_coverage_present(financial):
    """SITE_EH3_figure_reconciliation_and_periods MAJOR-6 (R10 class-closure):
    every published annual row must state its own period coverage so a
    part-year stub can never again render as an undifferentiated annual row.
    FAIL-CLOSED guards: a row missing the fields entirely fails (not silently
    skipped); a non-finite/out-of-range fraction fails (reject non-finite
    FIRST); a row whose period_partial flag disagrees with its OWN
    period_coverage_fraction fails (catches a future edit that updates one
    without the other -- not tautological, since it cross-checks two
    independently-settable stored fields against each other, not a value
    against its own source)."""
    rows = financial.get("annual", [])
    if not rows:
        return True  # nothing published yet -- degrade like the bridge gate's first-run case
    problems = []
    for r in rows:
        yr = r.get("year")
        if "period_coverage_fraction" not in r or "period_partial" not in r:
            problems.append(f"{yr}: missing period_coverage_fraction/period_partial")
            continue
        frac = r["period_coverage_fraction"]
        partial = r["period_partial"]
        if frac is not None:
            if not (isinstance(frac, (int, float)) and math.isfinite(frac)):
                problems.append(f"{yr}: period_coverage_fraction is not a finite number ({frac!r})")
                continue
            if not (0.0 <= frac <= 1.0001):
                problems.append(f"{yr}: period_coverage_fraction out of [0,1] range ({frac})")
                continue
            expected_partial = frac < _PERIOD_COVERAGE_PARTIAL_THRESHOLD
            if bool(partial) != expected_partial:
                problems.append(
                    f"{yr}: period_partial={partial} disagrees with period_coverage_fraction={frac}"
                )
                continue
            if expected_partial and not r.get("period_note"):
                problems.append(f"{yr}: partial year has no period_note")
    if problems:
        print("PERIOD-COVERAGE GATE FAILED: " + "; ".join(problems), file=sys.stderr)
        return False
    return True


def _check_population_consistency(data, dashboard):
    """Page-internal POPULATION reconciliation gate (R10 class fix for
    defect 3, ADVISOR_STEER_THESIS_CHART.md).

    R10 forbids closing an absurdity-class defect with an instance fix: the
    class here is "two different populations rendered on one page, both called
    'accounts/households', silently diverging". This gate asserts that EVERY
    count-of-accounts/households figure on the Front Door derives from the SAME
    final-year active_customer_ids population, so a future new count that reverts
    to a different population (e.g. the all-time, all-segment master list, the
    exact defect-2/3 bug) fails automatically here rather than shipping stale.

    Three assertions against the one canonical population:
      (1) the pulse-strip Book Size (book_annual last entry, active_elec+gas)
          equals len(final-year active_customer_ids) -- the book count reconciles
          to its source population;
      (2) the opex ledger household_count equals the resi-only, deduplicated
          household count derived from that SAME final-year population -- the opex
          count reconciles to the source population, resi-filtered (defect 2);
      (3) the resi household set is a subset of the full active household set --
          the opex population is a principled subset of the book population, not a
          separately-sourced list that merely happens to look plausible.
    """
    mismatches = []
    active_ids = _final_year_active_ids(data)

    book_annual = dashboard.get("customers", {}).get("book_annual", [])
    if book_annual:
        last = book_annual[-1]
        book_legs = last.get("active_elec", 0) + last.get("active_gas", 0)
        if book_legs != len(active_ids):
            mismatches.append(
                "Book Size ({}) != final-year active_customer_ids ({})".format(
                    book_legs, len(active_ids)
                )
            )

    resi_hh = _resi_household_ids_from_active(active_ids)
    opex_hh = dashboard.get("opex_ledger", {}).get("household_count")
    if opex_hh is not None and opex_hh != len(resi_hh):
        mismatches.append(
            "opex household_count ({}) != resi households in final-year "
            "active population ({})".format(opex_hh, len(resi_hh))
        )

    from saas.opex_ledger import _household_base_id
    all_hh = {_household_base_id(cid) for cid in active_ids}
    if not set(resi_hh) <= all_hh:
        mismatches.append(
            "resi household set {} is not a subset of the final-year active "
            "household population {}".format(sorted(resi_hh), sorted(all_hh))
        )

    if mismatches:
        print(
            "POPULATION CONSISTENCY GATE FAILED: {} mismatch(es) -- {}".format(
                len(mismatches), "; ".join(mismatches)
            ),
            file=sys.stderr,
        )
        return False
    return True


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    ok = generate(path)
    sys.exit(0 if ok else 1)
