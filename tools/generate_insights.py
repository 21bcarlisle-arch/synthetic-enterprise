"""
Run Insight Generator -- Phase 257.

Transforms raw simulation run output into "so what" interpretations
for 5 areas: trading, customers, risk, financial, operations.

Called by process_run_complete.py after every full sim run. Output:
  docs/observability/run_insights.json   -- current run
  docs/observability/run_history.json    -- cumulative (one entry per run)
"""
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

PROJECT = Path(__file__).resolve().parent.parent
RUN_INSIGHTS_PATH = PROJECT / "docs" / "observability" / "run_insights.json"
RUN_HISTORY_PATH = PROJECT / "docs" / "observability" / "run_history.json"

_INDUSTRY_MARGIN_LOW = 0.02
_INDUSTRY_MARGIN_HIGH = 0.05


class InsightArea(str, Enum):
    TRADING = "trading"
    CUSTOMERS = "customers"
    RISK = "risk"
    FINANCIAL = "financial"
    OPERATIONS = "operations"


@dataclass(frozen=True)
class AreaInsight:
    area: InsightArea
    headline: str
    narrative: str
    key_metrics: dict


@dataclass(frozen=True)
class RunInsights:
    git_hash: str
    generated_at: str
    net_margin_gbp: float
    executive_summary: str
    insights: tuple


def _fmt_gbp(v: float) -> str:
    sign = "-" if v < 0 else ""
    return sign + chr(163) + format(int(round(abs(v))), ",")


def _fmt_pct(v: float, decimals: int = 1) -> str:
    return format(v, "." + str(decimals) + "f") + "%"


def _committee_count(years: dict, yr: str) -> int:
    raw = years.get(yr, {}).get("committee_wake_ups", 0)
    return raw if isinstance(raw, int) else len(raw)


def _trading_insight(data: dict) -> AreaInsight:
    years = data.get("years", {})
    actual_total = 0.0
    naked_total = 0.0
    worst_yr_label = ""
    worst_cost = 0.0
    for yr in sorted(years):
        he = years[yr].get("hedge_effectiveness", {})
        a = he.get("actual_net_gbp", 0.0)
        n = he.get("naked_net_gbp", 0.0)
        actual_total += a
        naked_total += n
        cost = a - n
        if cost < worst_cost:
            worst_cost = cost
            worst_yr_label = yr
    hedge_cost = actual_total - naked_total
    if hedge_cost >= 0:
        headline = "Hedging added {} vs going naked (commodity basis)".format(_fmt_gbp(hedge_cost))
    else:
        headline = "Hedging cost {} vs going naked (85% mandate price)".format(_fmt_gbp(abs(hedge_cost)))
    worst_part = ""
    if worst_yr_label:
        worst_part = " Worst year: {} (hedging cost {} vs naked).".format(
            worst_yr_label, _fmt_gbp(abs(worst_cost)))
    narrative = (
        "Whole-run commodity basis: actual net {} vs naked {}. "
        "The 85% minimum hedge mandate {} {} over the 10-year window.{} "
        "Hedging reduces variance (survival objective) at the cost of expected P&L."
    ).format(
        _fmt_gbp(actual_total), _fmt_gbp(naked_total),
        "added" if hedge_cost >= 0 else "cost",
        _fmt_gbp(abs(hedge_cost)), worst_part)
    return AreaInsight(
        area=InsightArea.TRADING, headline=headline, narrative=narrative,
        key_metrics={
            "whole_run_actual_net_gbp": round(actual_total, 2),
            "whole_run_naked_net_gbp": round(naked_total, 2),
            "hedging_cost_gbp": round(hedge_cost, 2),
            "worst_year": worst_yr_label,
            "worst_year_cost_gbp": round(worst_cost, 2),
        })


def _customers_insight(data: dict) -> AreaInsight:
    years = data.get("years", {})
    all_shocks = []
    for yd in years.values():
        all_shocks.extend(yd.get("bill_shock_events", []))
    crisis_shocks = [s for s in all_shocks if s.get("period_end", "")[:4] in ("2021", "2022")]
    extreme_shocks = [s for s in all_shocks if s.get("bill_shock_pct", 0) > 1.0]
    ret_log = data.get("retention_log", [])
    no_offer = data.get("no_offer_churn_log", [])
    churned = data.get("churned_billing_accounts", [])
    offers = len(ret_log)
    retained = sum(1 for r in ret_log if r.get("outcome") == "retained")
    retention_rate = (retained / offers * 100) if offers > 0 else 0.0
    ev = data.get("enterprise_value_gbp", 0.0)
    ev_accounts = data.get("enterprise_value_account_count", 0)
    headline = "{} bill shock events ({} in crisis years); {}/{} retention offers accepted".format(
        len(all_shocks), len(crisis_shocks), retained, offers)
    narrative = (
        "Bill shocks across 2016-2025: {} events, {} extreme (>100%). "
        "2021-22 accounted for {} shocks as wholesale prices spiked. "
        "Retention: {}/{} offers accepted ({}); "
        "{} customers churned without an offer (margin guard blocked). "
        "Enterprise value: {} across {} accounts."
    ).format(
        len(all_shocks), len(extreme_shocks), len(crisis_shocks),
        retained, offers, _fmt_pct(retention_rate, 0),
        len(no_offer), _fmt_gbp(ev), ev_accounts)
    return AreaInsight(
        area=InsightArea.CUSTOMERS, headline=headline, narrative=narrative,
        key_metrics={
            "total_bill_shocks": len(all_shocks),
            "crisis_year_shocks": len(crisis_shocks),
            "extreme_shocks_over_100pct": len(extreme_shocks),
            "retention_offers": offers,
            "retained": retained,
            "no_offer_churns": len(no_offer),
            "total_churned": len(churned),
            "enterprise_value_gbp": round(ev, 2),
        })


def _risk_insight(data: dict) -> AreaInsight:
    years = data.get("years", {})
    committee_total = data.get("committee_wake_ups_total", 0)
    crisis_wake_ups = _committee_count(years, "2021") + _committee_count(years, "2022")
    admin = data.get("administration_event")
    survived = admin is None
    admin_str = (
        "SURVIVED full 2016-2025 window" if survived
        else "ADMINISTRATION EVENT: {}".format(admin))
    headline = "Risk committee: {} interventions; {}".format(committee_total, admin_str)
    narrative = (
        "The risk committee (Context Handshake) intervened {} times over 10 years, "
        "with {} in the 2021-22 crisis. "
        "Business {}: {}. "
        "The 85% minimum hedge mandate limited worst-case exposure."
    ).format(
        committee_total, crisis_wake_ups,
        "survived" if survived else "failed",
        "No administration event -- Ofgem solvency floor maintained." if survived else str(admin))
    return AreaInsight(
        area=InsightArea.RISK, headline=headline, narrative=narrative,
        key_metrics={
            "committee_interventions_total": committee_total,
            "crisis_year_interventions": crisis_wake_ups,
            "survived": survived,
            "administration_event": admin,
        })


def _financial_insight(data: dict) -> AreaInsight:
    lh = data.get("_ledger_headline", {})
    net = lh.get("net_margin_gbp", data.get("total_net_gbp", 0.0))
    gross = lh.get("gross_margin_gbp", data.get("total_gross_gbp", 0.0))
    revenue = lh.get("revenue_gbp", data.get("total_revenue_gbp", 0.0))
    net_pct = (net / revenue * 100) if revenue else 0.0
    pcl = data.get("per_customer_lifetime", {})
    ic_net = sum(cv.get("net_margin_gbp", 0) for cid, cv in pcl.items() if "IC" in cid)
    resi_net = sum(cv.get("net_margin_gbp", 0) for cid, cv in pcl.items() if "IC" not in cid)
    total_pcl = ic_net + resi_net
    ic_pct = (ic_net / total_pcl * 100) if total_pcl else 0.0
    cts = data.get("cost_to_serve_portfolio_gbp", 0.0)
    net_after_cts = data.get("net_margin_after_cost_to_serve_gbp", 0.0)
    net_frac = net_pct / 100
    benchmark_pos = "below" if net_frac < _INDUSTRY_MARGIN_LOW else (
        "above" if net_frac > _INDUSTRY_MARGIN_HIGH else "within")
    headline = "Net margin {} ({} of revenue -- {} 2-5% benchmark)".format(
        _fmt_gbp(net), _fmt_pct(net_pct), benchmark_pos)
    concentration_warning = ""
    if ic_pct >= 80:
        concentration_warning = " WARNING: I&C accounts for {} of margin -- high concentration risk.".format(
            _fmt_pct(ic_pct, 0))
    narrative = (
        "Gross margin {}, net {} ({} of revenue). "
        "Industry benchmark: 2-5% -- this business sits {} that range. "
        "I&C customers contribute {} of net margin ({}); residential {} ({}).{} "
        "Cost to serve: {}; net after CTS: {}."
    ).format(
        _fmt_gbp(gross), _fmt_gbp(net), _fmt_pct(net_pct), benchmark_pos,
        _fmt_pct(ic_pct, 0), _fmt_gbp(ic_net),
        _fmt_pct(100 - ic_pct, 0), _fmt_gbp(resi_net),
        concentration_warning, _fmt_gbp(cts), _fmt_gbp(net_after_cts))
    return AreaInsight(
        area=InsightArea.FINANCIAL, headline=headline, narrative=narrative,
        key_metrics={
            "net_margin_gbp": round(net, 2),
            "gross_margin_gbp": round(gross, 2),
            "revenue_gbp": round(revenue, 2),
            "net_margin_pct": round(net_pct, 2),
            "ic_net_margin_gbp": round(ic_net, 2),
            "ic_net_pct_of_total": round(ic_pct, 1),
            "cost_to_serve_gbp": round(cts, 2),
            "net_after_cost_to_serve_gbp": round(net_after_cts, 2),
        })


def _operations_insight(data: dict) -> AreaInsight:
    bills = data.get("bills_total", 0)
    clarity = data.get("avg_clarity_total", 0.0)
    sq = data.get("service_quality_score", 0.0)
    cts = data.get("cost_to_serve_portfolio_gbp", 0.0)
    accounts = data.get("enterprise_value_account_count", 1) or 1
    cts_per_account = cts / accounts
    clarity_grade = "excellent" if clarity >= 0.90 else ("good" if clarity >= 0.75 else "below target")
    sq_grade = "excellent" if sq >= 0.90 else ("good" if sq >= 0.75 else "below target")
    headline = "{} bills issued; service quality {}/1.0, clarity {}/1.0".format(
        bills, format(sq, ".3f"), format(clarity, ".3f"))
    narrative = (
        "{} bills issued over 2016-2025 (avg {}/yr). "
        "Service quality: {} ({}). Bill clarity: {} ({}). "
        "Cost to serve: {} portfolio total, {}/account/run."
    ).format(
        bills, format(bills / 10, ".0f"),
        format(sq, ".3f"), sq_grade,
        format(clarity, ".3f"), clarity_grade,
        _fmt_gbp(cts), _fmt_gbp(cts_per_account))
    return AreaInsight(
        area=InsightArea.OPERATIONS, headline=headline, narrative=narrative,
        key_metrics={
            "bills_total": bills,
            "avg_clarity": round(clarity, 4),
            "service_quality_score": round(sq, 4),
            "cost_to_serve_gbp": round(cts, 2),
            "cost_to_serve_per_account_gbp": round(cts_per_account, 2),
        })


def _executive_summary(data: dict, insights: list) -> str:
    admin = data.get("administration_event")
    survived_str = (
        "Business survived the full 2016-2025 window including the 2021-22 crisis."
        if admin is None else "ADMINISTRATION EVENT: {}.".format(admin))
    area_map = {i.area: i for i in insights}
    parts = [survived_str]
    for area in (InsightArea.FINANCIAL, InsightArea.TRADING, InsightArea.CUSTOMERS):
        ins = area_map.get(area)
        if ins:
            parts.append(ins.headline + ".")
    return " ".join(parts)


def generate_insights(data: dict, git_hash: str = "unknown") -> RunInsights:
    insight_list = [
        _trading_insight(data), _customers_insight(data),
        _risk_insight(data), _financial_insight(data), _operations_insight(data),
    ]
    summary = _executive_summary(data, insight_list)
    lh = data.get("_ledger_headline", {})
    net = lh.get("net_margin_gbp", data.get("total_net_gbp", 0.0))
    return RunInsights(
        git_hash=git_hash,
        generated_at=datetime.now(timezone.utc).isoformat(),
        net_margin_gbp=round(net, 2),
        executive_summary=summary,
        insights=tuple(insight_list),
    )


def _to_dict(insights: RunInsights) -> dict:
    return {
        "git_hash": insights.git_hash,
        "generated_at": insights.generated_at,
        "net_margin_gbp": insights.net_margin_gbp,
        "executive_summary": insights.executive_summary,
        "insights": [
            {"area": i.area.value, "headline": i.headline,
             "narrative": i.narrative, "key_metrics": i.key_metrics}
            for i in insights.insights
        ],
    }


def save_insights(insights: RunInsights, path: Optional[Path] = None) -> None:
    out = path or RUN_INSIGHTS_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(_to_dict(insights), indent=2))


def append_run_history(insights: RunInsights, history_path: Optional[Path] = None) -> None:
    hp = history_path or RUN_HISTORY_PATH
    hp.parent.mkdir(parents=True, exist_ok=True)
    history = []
    if hp.exists():
        try:
            history = json.loads(hp.read_text())
        except (json.JSONDecodeError, ValueError):
            history = []
    entry = {
        "git_hash": insights.git_hash,
        "generated_at": insights.generated_at,
        "net_margin_gbp": insights.net_margin_gbp,
        "executive_summary": insights.executive_summary,
        "headline_metrics": {
            area.value: next((i.key_metrics for i in insights.insights if i.area == area), {})
            for area in InsightArea
        },
    }
    history = [h for h in history if h.get("git_hash") != insights.git_hash]
    history.append(entry)
    hp.write_text(json.dumps(history, indent=2))


if __name__ == "__main__":
    import sys
    run_json_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if not run_json_arg:
        reports = PROJECT / "docs" / "reports"
        candidates = sorted(
            reports.glob("run_output_*[0-9Z].json"),
            key=lambda p: p.stat().st_mtime, reverse=True)
        run_json_arg = candidates[0] if candidates else None
    if not run_json_arg or not run_json_arg.exists():
        print("No run output JSON found", file=sys.stderr)
        sys.exit(1)
    data = json.loads(run_json_arg.read_text())
    parts = run_json_arg.stem.split("_")
    git_hash = parts[2] if len(parts) > 2 else "unknown"
    insights = generate_insights(data, git_hash)
    save_insights(insights)
    append_run_history(insights)
    print("Generated insights: {}".format(RUN_INSIGHTS_PATH))
    print("Executive summary: {}".format(insights.executive_summary))
