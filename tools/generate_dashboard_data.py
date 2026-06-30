#!/usr/bin/env python3
"""
Generate site/data/dashboard.json from the latest sim run output + Elexon SSP cache.
Called by process_run_complete.py after every full sim run, or manually:
  python3 tools/generate_dashboard_data.py [path/to/run_output.json]
"""
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SSP_CACHE = PROJECT / "sim" / "cache" / "elexon_ssp_full.json"
OUTPUT_PATH = PROJECT / "site" / "data" / "dashboard.json"

RUN_INSIGHTS_PATH = PROJECT / "docs" / "observability" / "run_insights.json"
RUN_HISTORY_PATH = PROJECT / "docs" / "observability" / "run_history.json"

_BUILD_PHASE = "FQ"
_BUILD_TEST_COUNT = 6727
_BUILD_COMPANY_MODULES = 303


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
    }


def extract_financial(data):
    annual = []
    for yr in sorted(data.get("years", {}).keys()):
        ydata = data["years"][yr]
        csplit = ydata.get("commodity_split", {})
        elec = csplit.get("electricity", {})
        gas = csplit.get("gas", {})
        annual.append({
            "year": int(yr),
            "revenue_gbp": _fmt(ydata.get("revenue_gbp", 0)),
            "gross_gbp": _fmt(ydata.get("gross_gbp", 0)),
            "capital_gbp": _fmt(ydata.get("capital_gbp", 0)),
            "net_gbp": _fmt(ydata.get("net_gbp", 0)),
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
    segment_annual = []
    for yr in sorted(data.get("years", {}).keys()):
        ydata = data["years"][yr]
        ssplit = ydata.get("segment_split", {})
        row = {"year": int(yr)}
        for seg, sdata in ssplit.items():
            key = seg.lower().replace(" ", "_")
            row[key] = {
                "gross_gbp": _fmt(sdata.get("gross_gbp", 0)),
                "net_gbp": _fmt(sdata.get("net_gbp", 0)),
            }
        segment_annual.append(row)

    ledger = data.get("ledger_pnl", {})
    return {
        "annual": annual,
        "segment_annual": segment_annual,
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

    return {
        "spot_monthly": committee_enriched,
        "hedge_annual": hedge_annual,
        "forward_terms": forward_terms[:500],  # cap for payload size
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
        book_annual.append({
            "year": int(yr),
            "active_elec": len(elec_ids),
            "active_gas": len(gas_ids),
            "acquisitions": acqs,
            "bill_shock_count": len(bill_shocks),
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
        })

    # Retention log
    retention = []
    for r in data.get("retention_log", []):
        retention.append({
            "customer_id": r.get("customer_id", ""),
            "date": r.get("event_date", ""),
            "company_est": round(float(r.get("company_churn_estimate", 0)), 3),
            "discount_pct": round(float(r.get("discount_pct", 0)), 3),
            "cost_gbp": _fmt(r.get("retention_cost_gbp", 0)),
            "outcome": r.get("outcome", ""),
        })

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

    return {
        "book_annual": book_annual,
        "per_year_net": dict(per_year_net),
        "events": events,
        "retention": retention,
        "lifetime": lifetime,
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
        })
    return {"annual": rows}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def extract_monthly_ops(data):
    from collections import defaultdict as _dd
    shock_m = _dd(list)
    for yr, yd in data.get("years", {}).items():
        for e in yd.get("bill_shock_events", []):
            m = e.get("period_end", "")[:7]
            if m:
                shock_m[m].append(float(e.get("bill_shock_pct", 0)))
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
    return {"monthly": rows}


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

    dashboard = {
        "meta": {
            "generated_at": generated_at,
            "git_commit": git_commit,
            "source_file": run_json_path.name,
            "spot_monthly_count": len(spot_monthly),
        },
        "portfolio": extract_portfolio(data),
        "financial": extract_financial(data),
        "trading": extract_trading(data, spot_monthly),
        "customers": extract_customers(data),
        "market": extract_market(data, spot_monthly),
        "insights": extract_insights(),
        "run_history": extract_run_history(),
        "query_context": extract_query_context(data),
        "management_accounts": extract_management_accounts(data),
        "monthly_ops": extract_monthly_ops(data),
        "build": {
            "current_phase": _BUILD_PHASE,
            "phases_built": f"Phase {_BUILD_PHASE} (300+ total)",
            "test_count": _BUILD_TEST_COUNT,
            "test_suite": f"{_BUILD_TEST_COUNT:,}+ (non-sim)",
            "company_modules": _BUILD_COMPANY_MODULES,
            "simulation_window": "2016-2025",
            "regulatory_modules": 48,
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(dashboard, f, separators=(",", ":"))

    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"Wrote {OUTPUT_PATH} ({size_kb:.1f} KB)")
    return True


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    ok = generate(path)
    sys.exit(0 if ok else 1)
