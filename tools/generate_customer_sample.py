#!/usr/bin/env python3
"""Generate site/data/customer_sample.json -- consolidated per-customer ground truth.

Pulls from run output: financial summary, annual P&L, renewal events, basis risk,
and churn accuracy.  Behavioral trajectory fields (income_stress, life_events,
satisfaction, payment_behaviour) are null until run_phase2b emits them.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"
OUT_PATH = PROJECT / "site" / "data" / "customer_sample.json"


def _base_id(cid):
    if cid.endswith("g") and len(cid) > 1:
        return cid[:-1]
    return cid


def _per_year(run, cid):
    out = []
    for yr in sorted(run.get("years", {}).keys()):
        ydata = run["years"][yr]
        cdata = ydata.get("per_customer", {}).get(cid)
        if cdata:
            out.append({
                "year": int(yr),
                "gross_gbp": round(cdata.get("gross_gbp", 0), 2),
                "net_gbp": round(cdata.get("net_gbp", 0), 2),
                "tariff_min_gbp_per_mwh": round(cdata.get("tariff_min_gbp_per_mwh", 0), 2),
                "tariff_max_gbp_per_mwh": round(cdata.get("tariff_max_gbp_per_mwh", 0), 2),
            })
    return out


def generate(run_json_path=None, out_path=None, state_path=None):
    import re
    from datetime import datetime, timezone
    path = Path(run_json_path) if run_json_path else RUN_OUTPUT
    run = json.loads(path.read_text())

    cache_meta = run.get("_cache_meta", {})
    # fall back to extracting commit hash from filename (run_output_<hash>_<ts>.json)
    stem = path.stem
    m = re.search(r"run_output_([0-9a-f]{8})_", stem)
    git_commit = cache_meta.get("git_commit", m.group(1) if m else "unknown")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    pcl = run.get("per_customer_lifetime", {})
    bba = run.get("by_billing_account", {})

    events_by_cid = defaultdict(list)
    for e in run.get("customer_events", []):
        events_by_cid[e["customer_id"]].append({
            "event_date": e["event_date"],
            "commodity": e["commodity"],
            "event_type": e["event_type"],
            "sim_churn_probability": e.get("realized_churn_probability", e.get("churn_probability")),
            "company_churn_estimate": e.get("company_churn_estimate"),
            "churn_estimate_error_pct": e.get("churn_estimate_error_pct"),
            "retention_offered": e.get("retention_offered"),
            "is_active_renewal": e.get("is_active_renewal"),
            "unit_rate_gbp_per_mwh": e.get("unit_rate_gbp_per_mwh"),
        })

    basis_by_cid = defaultdict(list)
    for t in run.get("basis_risk_terms", []):
        basis_by_cid[t["customer_id"]].append({
            "commodity": t["commodity"],
            "term_start": t["term_start"],
            "company_fwd_gbp_per_mwh": round(t.get("company_fwd_gbp_per_mwh") or 0, 4),
            "sim_fwd_gbp_per_mwh": round(t.get("sim_fwd_gbp_per_mwh") or 0, 4),
            "tariff_error_pct": round(t.get("tariff_error_pct") or 0, 4),
        })

    churn_acc_by_cid = defaultdict(list)
    for r in run.get("churn_basis_risk", []):
        churn_acc_by_cid[r["customer_id"]].append({
            "term_start": r.get("term_start"),
            "sim_churn_probability": r.get("sim_churn_probability"),
            "company_churn_estimate": r.get("company_churn_estimate"),
            "churn_estimate_error_pct": r.get("churn_estimate_error_pct"),
            "is_active_renewal": r.get("is_active_renewal"),
            "unit_rate_gbp_per_mwh": r.get("unit_rate_gbp_per_mwh"),
            "rate_vs_svt_pct": r.get("rate_vs_svt_pct"),
        })

    behavioral = run.get("per_customer_behavioral", {})

    # Phase RU: solicited feedback survey engine (FEEDBACK_AND_REPUTATION.md Layer 1).
    # Dispatched once per electricity renewal term, keyed by billing_account (== cid
    # for electricity legs -- see saas/customer_reaction.py::_billing_account_id).
    feedback_by_cid = defaultdict(list)
    for e in run.get("feedback_survey_log", []):
        feedback_by_cid[e["customer_id"]].append({
            "term_start": e["term_start"],
            "true_satisfaction": e.get("true_satisfaction"),
            "csat_responded": e.get("csat_responded"),
            "csat_score_0_10": e.get("csat_score_0_10"),
            "nps_responded": e.get("nps_responded"),
            "nps_score_0_10": e.get("nps_score_0_10"),
        })
    reputation_events_by_cid = defaultdict(list)
    for e in run.get("reputation_events_log", []):
        reputation_events_by_cid[e["customer_id"]].append({
            "date": e["date"],
            "event_type": e["event_type"],
            "days_to_resolve": e.get("days_to_resolve"),
        })

    # Nudge Physics Layer 1 (NUDGE_PHYSICS.md): SIM-side hidden companion log --
    # framing_type is company-observable (its own comms-cohort choice), but
    # susceptibility/effectiveness_multiplier are ground truth the company
    # never reads. Exposed here only for Sim-tab / Customer-360 verification.
    nudge_physics_by_cid = defaultdict(list)
    for e in run.get("nudge_physics_log", []):
        nudge_physics_by_cid[e["customer_id"]].append({
            "event_date": e["event_date"],
            "framing_type": e.get("framing_type"),
            "susceptibility": e.get("susceptibility"),
            "effectiveness_multiplier": e.get("effectiveness_multiplier"),
            "outcome": e.get("outcome"),
        })

    sample = {}
    for cid, cdata in sorted(pcl.items()):
        base = _base_id(cid)
        is_gas = cid.endswith("g") and cid != base
        clv_data = bba.get(base, {}) if not is_gas else {}
        _beh = behavioral.get(cid) or {}

        _segment = cdata.get("segment", "resi")
        _commodity = cdata.get("commodity", "electricity")
        _payment_channel = None
        _fuel_poverty = None
        if _segment == "resi":
            # Layer 2 dimensions 1-2 (2026-07-09): SIM-internal ground truth
            # (payment channel / fuel poverty archetype), shown here for the
            # SIM tab's own evidence-surface purpose only -- same caveat as
            # engagement_level above: MUST NEVER be read by company/** code.
            from simulation.household_segments import PaymentChannel, fuel_poverty_for_customer, payment_channel_for_customer
            _channel = payment_channel_for_customer(cid, _commodity)
            _payment_channel = _channel.value
            _fuel_poverty = fuel_poverty_for_customer(cid, _channel)

        sample[cid] = {
            "account_id": cid,
            "base_account_id": base,
            "segment": _segment,
            "commodity": _commodity,
            "payment_channel": _payment_channel,
            "fuel_poverty": _fuel_poverty,
            "acquisition_date": cdata.get("acquisition_date"),
            "lifetime_revenue_gbp": round(cdata.get("revenue_gbp", 0), 2),
            "lifetime_gross_gbp": round(cdata.get("gross_gbp", 0), 2),
            "lifetime_net_gbp": round(cdata.get("net_gbp", 0), 2),
            "cost_to_serve_gbp": round(cdata.get("cost_to_serve_gbp", 0), 2),
            "lifetime_net_after_cts_gbp": round(
                cdata.get("net_margin_after_cost_to_serve_gbp", 0), 2
            ),
            "clv_gbp": round(clv_data.get("clv_gbp", 0), 2),
            "latest_churn_probability": round(clv_data.get("latest_churn_probability", 0), 4),
            "expected_lifetime_periods": round(
                clv_data.get("expected_lifetime_periods", 0), 2
            ),
            "annual_pnl": _per_year(run, cid),
            "renewal_events": events_by_cid.get(cid, []),
            "basis_risk_by_term": basis_by_cid.get(cid, []),
            "churn_accuracy_by_renewal": churn_acc_by_cid.get(cid, []),
            "income_stress_trajectory": _beh.get("income_stress_trajectory"),
            "life_event_history": _beh.get("life_event_history"),
            "satisfaction_score_trajectory": _beh.get("satisfaction_score_trajectory") or None,
            "payment_behaviour_analytics": {
                "score": _beh.get("payment_behaviour_score"),
                "metrics": _beh.get("payment_behaviour_metrics"),
            } if _beh else None,
            "payment_miss_trajectory": _beh.get("payment_miss_trajectory") or [],
            "bill_shock_history": _beh.get("bill_shock_history") or [],
            # Phase RU: solicited feedback survey engine. Dispatched on the electricity
            # leg only (dual-fuel gas legs share the same household -- see base_account_id).
            "feedback_survey_history": [] if is_gas else feedback_by_cid.get(cid, []),
            "reputation_events": [] if is_gas else reputation_events_by_cid.get(cid, []),
            "nudge_physics_history": [] if is_gas else nudge_physics_by_cid.get(cid, []),
            "data_status": {
                "financial": "complete",
                "renewal_events": "complete",
                "basis_risk": "complete",
                "churn_accuracy": "complete",
                "income_stress_trajectory": "complete" if _beh else "pending_sim_emission",
                "life_event_history": "complete" if _beh else "pending_sim_emission",
                "satisfaction_score_trajectory": "complete" if _beh.get("satisfaction_score_trajectory") else "pending_sim_emission",
                "payment_behaviour_analytics": "complete" if _beh else "pending_sim_emission",
                "payment_miss_trajectory": "complete" if _beh.get("payment_miss_trajectory") else "pending_sim_emission",
                "bill_shock_history": "complete" if _beh else "pending_sim_emission",
                # Phase RU: complaints infrastructure (company/crm/complaints.py) is now
                # wired live via simulation/feedback_survey.py's dispatch_complaint_and_resolution
                # -- a customer with zero entries in reputation_events genuinely had no
                # complaint this run, not a missing-data gap.
                "feedback_survey_history": "complete" if not is_gas else "see_electricity_account",
                "complaint_history": "complete" if not is_gas else "see_electricity_account",
                "nudge_physics_history": "complete" if not is_gas else "see_electricity_account",
            },
        }

    meta = {
        "generated_at": generated_at,
        "git_commit": git_commit,
        "customer_count": len(sample),
        "note": (
            "Consolidated per-customer ground truth. Fields marked pending_sim_emission "
            "will be populated once run_phase2b emits behavioral trajectories."
        ),
    }

    out = {"meta": meta, "customers": sample}
    _out_path = Path(out_path) if out_path else OUT_PATH
    _out_path.parent.mkdir(parents=True, exist_ok=True)
    out_text = json.dumps(out, indent=2)
    _out_path.write_text(out_text)
    # Also publish to site/state/ for stable URL (poesys.net/state/customer_sample.json)
    _state_path = Path(state_path) if state_path else (PROJECT / "site" / "state" / "customer_sample.json")
    _state_path.parent.mkdir(parents=True, exist_ok=True)
    _state_path.write_text(out_text)
    print(f"Generated {_out_path} ({len(sample)} customers)")
    return _out_path


if __name__ == "__main__":
    generate(sys.argv[1] if len(sys.argv) > 1 else None)
