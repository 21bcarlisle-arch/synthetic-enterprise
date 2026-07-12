#!/usr/bin/env python3
"""
Generate site/data/dashboard.json from the latest sim run output + Elexon SSP cache.
Called by process_run_complete.py after every full sim run, or manually:
  python3 tools/generate_dashboard_data.py [path/to/run_output.json]
"""
import json
import re
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from company.analytics.retention_deferral_economics import (
    compute_realized_deferrals, serial_saver_summary,
)
from company.trading.hedge_decision import VAR_REVENUE_LIMIT

PROJECT = Path(__file__).resolve().parent.parent
SSP_CACHE = PROJECT / "sim" / "cache" / "elexon_ssp_full.json"
OUTPUT_PATH = PROJECT / "site" / "data" / "dashboard.json"

RUN_INSIGHTS_PATH = PROJECT / "docs" / "observability" / "run_insights.json"
RUN_HISTORY_PATH = PROJECT / "docs" / "observability" / "run_history.json"
BUILD_INFO_PATH = PROJECT / "docs" / "observability" / "build_info.json"

# Fallback only -- canonical phase/test-count values live in build_info.json,
# updated at phase close (CLAUDE.md phase-close checklist step 1) so this page
# never bakes in a stale phase/test-count label.
_BUILD_PHASE = "OL"
_BUILD_TEST_COUNT = 15148


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
    idx = text.find("## Current state")
    if idx < 0:
        return None, None
    section = text[idx:]
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
                "bridge_url": "./data/margin_bridge.json",
                "note": (
                    "Settlement-derived (total_net_gbp). Diverges from the "
                    "bill-derived ledger view (financial.ledger.net_margin_gbp) "
                    "-- see the reconciliation bridge."
                ),
            },
            "enterprise_value_gbp": {
                "clock": "settled",
                "provisional": True,
                "derived_from": "net_margin_gbp",
                "note": (
                    "Derived from the settled-clock net margin above -- "
                    "inherits its divergence from the bill-derived view until "
                    "the bridge is applied to recompute it."
                ),
            },
        },
    }


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
    annual = []
    for yr in sorted(data.get("years", {}).keys()):
        ydata = data["years"][yr]
        csplit = ydata.get("commodity_split", {})
        elec = csplit.get("electricity", {})
        gas = csplit.get("gas", {})
        net = ydata.get("net_gbp", 0)
        total_revenue = mgmt_accounts.get(yr, {}).get("income_statement", {}).get("revenue_gbp")
        annual.append({
            "year": int(yr),
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
        })

    # Segment annual
    segments_seen = set()
    for yr in data.get("years", {}).keys():
        segments_seen.update(data["years"][yr].get("segment_split", {}).keys())

    segment_annual = []
    for yr in sorted(data.get("years", {}).keys()):
        ydata = data["years"][yr]
        ssplit = ydata.get("segment_split", {})
        row = {"year": int(yr)}
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
            "bad_debt_gbp": _fmt(ledger.get("bad_debt_gbp", 0)),
            "vat_remittance_gbp": _fmt(ledger.get("vat_remittance_gbp", 0)),
            "non_commodity_cost_gbp": _fmt(ledger.get("non_commodity_cost_gbp", 0)),
            "acquisition_spend_gbp": _fmt(ledger.get("acquisition_spend_gbp", 0)),
            "fixed_cost_gbp": _fmt(ledger.get("fixed_cost_gbp", 0)),
            "operating_net_margin_gbp": _fmt(ledger.get("operating_net_margin_gbp", 0)),
        },
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

    return {
        "spot_monthly": committee_enriched,
        "hedge_annual": hedge_annual,
        "forward_terms": forward_terms[:500],  # cap for payload size
        "var_annual": var_annual,
        "var_limit_pct_of_term_revenue": VAR_REVENUE_LIMIT,
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

    # Lifetime per customer — pull tariff_type from CUSTOMERS master list
    from saas.customers import CUSTOMERS as _CUSTS
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

def extract_monthly_ops(data):
    from collections import defaultdict as _dd
    shock_m = _dd(list)
    likely_seasonal_count = 0
    genuine_shock_count = 0
    for yr, yd in data.get("years", {}).items():
        for e in yd.get("bill_shock_events", []):
            m = e.get("period_end", "")[:7]
            if m:
                shock_m[m].append(float(e.get("bill_shock_pct", 0)))
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
        rows.append({
            "month": m,
            "shock_count": len(sh),
            "avg_shock_pct": round(statistics.mean(sh) * 100, 1) if sh else 0.0,
            "max_shock_pct": round(max(sh) * 100, 1) if sh else 0.0,
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
    same as that section, rather than duplicating a different definition."""
    ledger_path = PROJECT / "site" / "state" / "billing_ledger.json"
    arrears_by_year: dict[int, set[str]] = defaultdict(set)
    if ledger_path.is_file():
        try:
            ledger = json.loads(ledger_path.read_text())
            for cid, cdata in ledger.get("customers", {}).items():
                for case in cdata.get("arrears_history", []):
                    opened = case.get("opened_date", "")
                    if opened:
                        try:
                            arrears_by_year[int(opened[:4])].add(cid)
                        except ValueError:
                            continue
        except (json.JSONDecodeError, OSError):
            arrears_by_year = defaultdict(set)

    rows = []
    for yr, yd in sorted(data.get("years", {}).items()):
        yr_int = int(yr)
        is_crisis = yr_int in (2021, 2022, 2023)
        active = yd.get("active_customer_ids", [])
        n_active = len(active)
        case_count = len(arrears_by_year.get(yr_int, set()))
        if n_active > 0:
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
    return {"annual": rows}


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
    from saas.reporting.annual_report import populate_compliance_scorecard
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
    from saas.customers import CUSTOMERS as _CUSTS
    from dataclasses import asdict

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
    lines.append("CUSTOMER LIFETIME NET MARGIN:")
    for cid, cdata in sorted(data.get("per_customer_lifetime", {}).items()):
        net = cdata.get("net_gbp", 0)
        seg = cdata.get("segment", "")
        comm = cdata.get("commodity", "")
        rev = cdata.get("revenue_gbp", 0)
        lines.append("  {} ({}, {}): net=GBP{:,.0f}  revenue=GBP{:,.0f}".format(
            cid, seg, comm, net, rev))
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
    git_commit = cache_meta.get("git_commit", run_json_path.stem.split("_")[2] if "_" in run_json_path.stem else "unknown")
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

    consistency_ok = _check_consistency(portfolio, insights, run_json_path.name)
    population_ok = _check_population_consistency(data, dashboard)
    basis_ok = _check_basis_labels_present(portfolio)
    bridge_ok = _check_bridge_reconciles()
    consistency_ok = consistency_ok and population_ok and basis_ok and bridge_ok

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(dashboard, f, separators=(",", ":"))

    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"Wrote {OUTPUT_PATH} ({size_kb:.1f} KB)")
    return consistency_ok


# Headline metrics checked across surfaces (Part C of the website-integrity fix:
# the Part A gate only ever compared net_margin_gbp; this widens it to the full
# set of numbers a board member would actually read off the page). Each entry is
# (portfolio_key, label, insights_area, insights_key). insights_area=None means
# the field lives at the top level of run_insights.json rather than nested under
# one of its per-area "insights" blocks.
_CONSISTENCY_CHECKS = [
    ("net_margin_gbp", "net margin", None, "net_margin_gbp"),
    ("gross_margin_gbp", "gross margin", "financial", "gross_margin_gbp"),
    ("enterprise_value_gbp", "enterprise value", "customers", "enterprise_value_gbp"),
    ("bills_total", "bills total", "operations", "bills_total"),
    ("committee_interventions_total", "committee interventions", "risk", "committee_interventions_total"),
    ("retention_offers", "retention offers", "customers", "retention_offers"),
    ("retention_retained", "retention retained", "customers", "retained"),
    ("churn_count", "churn count", "customers", "total_churned"),
]


def _insights_metric(insights, area, key):
    """Look up key_metrics[key] from the named per-area block in run_insights.json's
    'insights' list (or the top-level field when area is None)."""
    if area is None:
        return insights.get(key)
    for block in insights.get("insights", []) or []:
        if block.get("area") == area:
            return block.get("key_metrics", {}).get(key)
    return None


def _check_consistency(portfolio, insights, source_file, tolerance_gbp=1.0):
    """Guard against surfaces on the same page disagreeing (Part A #3 / Part C of
    the website-integrity fix): the exec-summary insights are generated from a
    separate run_insights.json snapshot, not from the run_output.json this call
    just loaded, so a step-ordering regression upstream can silently re-introduce
    a stale/mismatched exec summary next to correct totals. Checks the full set
    of headline numbers (net/gross margin, enterprise value, bills, committee
    interventions, retention, churn), not just net margin."""
    if not insights:
        print("CONSISTENCY GATE: no run_insights.json present -- skipping check", file=sys.stderr)
        return True

    mismatches = []
    for p_key, label, area, i_key in _CONSISTENCY_CHECKS:
        p_val = portfolio.get(p_key)
        i_val = _insights_metric(insights, area, i_key)
        if p_val is None or i_val is None:
            continue
        tol = tolerance_gbp if p_key.endswith("_gbp") else 0
        if abs(p_val - i_val) > tol:
            mismatches.append("{}: dashboard={} vs insights={}".format(label, p_val, i_val))

    if mismatches:
        print(
            "CONSISTENCY GATE FAILED (source={}): {} surface(s) disagree -- {}".format(
                source_file, len(mismatches), "; ".join(mismatches)
            ),
            file=sys.stderr,
        )
        return False
    return True


# Headline figures that must carry a basis label (CLAUDE.md standing rule,
# CLOCK_TRUTH_AND_THE_BRIDGE.md 2026-07-12): "No financial figure is
# published without its clock. A number whose basis is unstated is a defect,
# not a formatting choice."
_BASIS_REQUIRED_PORTFOLIO_KEYS = ("net_margin_gbp", "enterprise_value_gbp")


def _check_basis_labels_present(portfolio):
    """Extends the page-consistency invariant (CLOCK_TRUTH_AND_THE_BRIDGE.md):
    any published financial figure lacking a basis label fails the gate. A
    missing/incomplete portfolio.basis entry for a headline GBP figure is a
    defect, caught here rather than shipping an unlabelled number to the
    front door (the exact failure this rule exists to prevent)."""
    basis = portfolio.get("basis", {}) or {}
    missing = []
    for key in _BASIS_REQUIRED_PORTFOLIO_KEYS:
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
