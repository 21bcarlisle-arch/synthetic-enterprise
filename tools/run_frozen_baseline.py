"""Frozen-policy baseline replay: last-generation vs current company decisions.

FROZEN_POLICY_BASELINE_DESIGN.md option B (WEBSITE_AS_SHOWCASE.md tab 2,
SUPPLIER_TAB_OVERHAUL.md line 26 -- "the value of learning"): replays the
same historical decade twice through the real simulation entry point,
`simulation.run_phase4c_on_phase2b.main()`, once under CURRENT_POLICY (the
live retention/hedging decisions) and once under NAIVE_POLICY (the
superseded pre-Phase-14a/15b/43b decisions company/policy/decision_policy.py
reconstructs) -- everything else (market data, weather, customer roster,
acquisition/churn dice rolls) held identical. Both runs are real executions
of the same decision code, not a recompute from stored records: retention
and hedge decisions change realized settlement outcomes (churn timing,
revenue, margin), so a different policy produces a genuinely different book.

This is deliberately NOT run every sim cycle -- doubling a full-decade
simulation is expensive and "last-generation policy" is a fixed historical
reference point, not something that needs to be live every run. Call
`run_frozen_baseline()` on demand / periodically (see
`should_refresh_baseline()` for the staleness gate process_run_complete.py
uses).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from company.policy.decision_policy import CURRENT_POLICY, NAIVE_POLICY
from simulation.run_phase4c_on_phase2b import main as run_phase4c

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_DIR / "site" / "state" / "frozen_policy_baseline.json"

# Refresh at most this often (seconds) -- a full decade replay runs the sim
# entry point twice, so this is a periodic artifact, not a per-cycle one.
REFRESH_INTERVAL_SECONDS = 7 * 24 * 60 * 60  # weekly


def _portfolio_metrics(result: dict) -> dict:
    """Extract the headline metrics used for the delta-EV comparison from one
    run_phase4c_on_phase2b.main() result."""
    phase2b = result["phase2b"]
    retention_log = phase2b.get("retention_log", [])
    retained = sum(1 for r in retention_log if r.get("outcome") == "retained")
    # retention_cost_events' amount_gbp is stored negated (cash-out convention,
    # matching saas/ledger.py's other cost events) -- negate back to a positive cost.
    retention_cost_total = -sum(
        e.get("amount_gbp", 0.0) for e in phase2b.get("retention_cost_events", [])
    )
    return {
        "enterprise_value_gbp": result["enterprise_value"]["portfolio"]["enterprise_value_gbp"],
        "account_count": result["enterprise_value"]["portfolio"]["account_count"],
        "total_net_gbp": phase2b.get("total_net", 0.0),
        "final_treasury_gbp": phase2b.get("final_treasury", 0.0),
        "retention_offers_made": len(retention_log),
        "retention_offers_retained": retained,
        "retention_cost_gbp": retention_cost_total,
        "churned_accounts": len(phase2b.get("churned_billing_accounts", [])),
    }


def run_frozen_baseline(report_end: str | None = None) -> dict:
    """Run the same historical window under CURRENT_POLICY and NAIVE_POLICY,
    returning both portfolios' headline metrics plus the delta.

    Both runs reuse the identical locally-keyed dice rolls (churn/acquisition
    are keyed by `f"{billing_account}_{term_start_str}"`, not one global
    seed -- see simulation/customer_events.py and run_phase2b.py's
    acquisition roll), so any divergence between the two runs is
    attributable to the policy change alone.
    """
    current_result = run_phase4c(report_end=report_end, policy=CURRENT_POLICY)
    naive_result = run_phase4c(report_end=report_end, policy=NAIVE_POLICY)

    current = _portfolio_metrics(current_result)
    naive = _portfolio_metrics(naive_result)

    delta_ev_gbp = current["enterprise_value_gbp"] - naive["enterprise_value_gbp"]

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report_end": report_end,
        "current_policy": current,
        "naive_policy": naive,
        "delta_ev_gbp": delta_ev_gbp,
        "delta_net_margin_gbp": current["total_net_gbp"] - naive["total_net_gbp"],
        "narrative": (
            "Replaying the same decade under the naive pre-learning policy "
            "(flat 5% retention discount, margin-only offer guard, no VaR-constrained "
            "hedge decision -- the pre-Phase-14a/15b/43b state) instead of today's "
            "decisions changes enterprise value by £{:,.0f} ({} offers made under "
            "current policy vs {} under naive, {} vs {} retained)."
        ).format(
            delta_ev_gbp,
            current["retention_offers_made"], naive["retention_offers_made"],
            current["retention_offers_retained"], naive["retention_offers_retained"],
        ),
    }


def should_refresh_baseline(path: Path = OUTPUT_PATH) -> bool:
    """True if no baseline exists yet, or the existing one is older than
    REFRESH_INTERVAL_SECONDS."""
    if not path.exists():
        return True
    try:
        existing = json.loads(path.read_text())
        generated_at = datetime.strptime(existing["generated_at"], "%Y-%m-%dT%H:%M:%SZ")
        generated_at = generated_at.replace(tzinfo=timezone.utc)
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        return True
    age_seconds = (datetime.now(timezone.utc) - generated_at).total_seconds()
    return age_seconds >= REFRESH_INTERVAL_SECONDS


def generate(path: Path = OUTPUT_PATH, force: bool = False) -> dict | None:
    """Refresh site/state/frozen_policy_baseline.json if stale (or `force`).

    Returns the baseline dict if regenerated, None if skipped as fresh.
    """
    if not force and not should_refresh_baseline(path):
        return None
    baseline = run_frozen_baseline()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(baseline, indent=2))
    return baseline


if __name__ == "__main__":
    result = generate(force=True)
    print(json.dumps(result, indent=2))
