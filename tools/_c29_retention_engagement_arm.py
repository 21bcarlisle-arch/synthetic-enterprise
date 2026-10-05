"""Run ONE arm of the C29 retention-guard pair: `DecisionPolicy.retention_weighs_engagement` off or on.

The pair is the same world and the same book, differing in that one field (`dataclasses.replace` on
`CURRENT_POLICY`), each in its own process because the run loop's module state must not carry from
one arm into the other. What it asks: does weighting the guard's value by the account's engagement
estimate save more retention cost than the departures it adds would lose?

THE GUARD IS OBSERVED, NOT RE-DERIVED. `run_phase2b` reaches the guard through two names it imports
from the growth desk. This process rebinds both on the module: the estimate wrapper records the full
`EngagementEstimate` (so `prior_strength` is read, not inferred), and the value wrapper returns a
float that records the one comparison the guard makes against it -- the offer's cost. So a refusal
BY THE WEIGHTING is exact: the unweighted value beat the cost, the weighted one did not. Nothing the
run decides changes; `float.__gt__` gives the same answer it would have.

The live payment triad's gap ledger is pointed at a scratch file, so an arm publishes nothing.

Usage: python3 -m tools._c29_retention_engagement_arm <off|on> <out.json> [report_end]
"""
from __future__ import annotations

import dataclasses
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _observe_guard(rp2b, record_estimate: bool) -> list[dict]:
    """Rebind the guard's two names on the run loop's module; return the list each decision fills."""
    from company.crm.engagement_estimate import engagement_at

    guard: list[dict] = []
    pending: dict = {}
    desk_value = rp2b.retention_value_protected

    def observed_engagement(account_id, as_of, **kw):
        est = engagement_at(account_id, as_of, **kw)
        pending.clear()
        pending.update(account=account_id, date=as_of, fuel=kw.get("fuel"),
                       estimate=None if est is None else est.estimate,
                       prior_strength=None if est is None else est.prior_strength,
                       anniversaries=None if est is None else est.anniversaries,
                       channel=None if est is None else est.channel)
        return None if est is None else est.estimate

    class _Seen(float):
        def __gt__(self, other):
            row = dict(pending) if record_estimate else {}
            pending.clear()
            row.update(unweighted=self.unweighted, weighted=float(self), cost=float(other),
                       offered=float(self) > other, offered_unweighted=self.unweighted > other)
            guard.append(row)
            return float(self) > other

    def observed_value(expected_margin, acq_cost_saved, engagement):
        seen = _Seen(desk_value(expected_margin, acq_cost_saved, engagement))
        seen.unweighted = expected_margin + acq_cost_saved
        return seen

    rp2b.retention_engagement = observed_engagement
    rp2b.retention_value_protected = observed_value
    return guard


def main() -> int:
    arm, out = sys.argv[1], Path(sys.argv[2])
    report_end = sys.argv[3] if len(sys.argv) > 3 else None
    if arm not in ("off", "on"):
        print(f"REFUSED: unknown arm {arm!r}; one of off, on")
        return 2

    import simulation.run_phase2b as rp2b
    from company.policy.decision_policy import CURRENT_POLICY, policy_scope

    policy = dataclasses.replace(CURRENT_POLICY, retention_weighs_engagement=(arm == "on"))
    guard = _observe_guard(rp2b, record_estimate=(arm == "on"))

    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    with tempfile.TemporaryDirectory() as scratch, policy_scope(policy):
        result = rp2b.main(report_end=report_end, policy=policy,
                           gap_ledger_path=Path(scratch) / "gap_ledger.json")

    events = result.get("customer_events") or []
    out.write_text(json.dumps({
        "arm": arm, "head": head, "report_end": report_end,
        "retention_weighs_engagement": policy.retention_weighs_engagement,
        "guard": guard,
        "retention_offers": len(result.get("retention_log") or []),
        "retention_cost_gbp": round(sum(r.get("retention_cost_gbp") or 0.0 for r in
                                        result.get("retention_log") or []), 2),
        "churned_billing_accounts": len(result.get("churned_billing_accounts") or []),
        "renewal_departures": sum(1 for e in events if e.get("event_type") == "churned"
                                  and e.get("departure_occasion") == "renewal"),
        "total_gross": result.get("total_gross"),
        "total_net": result.get("total_net"),
        "final_treasury": result.get("final_treasury"),
        # The WORLD's own P(stay) with and without the offer, per renewal roll. A single roll per
        # refused offer says almost nothing about what the offer was worth; the difference of these
        # two, summed over the refusals, is the departures the weighting is expected to add.
        "renewal_rolls": [
            {k: e.get(k) for k in ("customer_id", "event_date", "commodity", "event_type",
                                   "retention_offered", "random_roll",
                                   "effective_retention_probability",
                                   "realized_churn_probability")}
            for e in events if e.get("departure_occasion") == "renewal"
            or e.get("event_type") == "renewed"],
    }, indent=2, default=str), encoding="utf-8")
    print(f"[{arm}] -> {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
