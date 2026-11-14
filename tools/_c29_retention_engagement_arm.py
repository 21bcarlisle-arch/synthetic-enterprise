"""Run ONE arm of a C29 retention-guard pair: `off`, `on` (`DecisionPolicy.retention_weighs_engagement`)
or `net` (`DecisionPolicy.retention_nets_bad_debt`, 2026-10-07).

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

Every guard row also carries the account's payment behaviour score as the churn belief read it
(`CustomerExperienceDesk.account_payment_behaviour_score`, observed on the class) and, in the `net`
arm, the bad-debt charge netted -- so `offered_unweighted` against `offered` is exactly the offers
the netting withdrew.

(2026-11-14, SEAT_PREREG_THE_RETENTION_GUARD_NETS_BAD_DEBT_2026-11-14.md, Instrument.) The guard
returns `None` where the term has no contribution; that row records `unweighted` None and
`offered_unweighted` False rather than crashing, which is why the 21 Oct pair ran from an
out-of-tree probe. Every row also carries the probe's fields (`margin`, `acq`, `billed`,
`belief_rate`) and the renewal's keys: `customer_id` (supply point), `billing_account` (the key
`retention_log` uses) and `event_date`, read from the company's own `arrears_state` call for the
leg, together with that call's answer, `arrears_state`, the cell the bad-debt belief is keyed on.
It is the company's receivable state, read through the triad door, never the world's arrears.

Usage: python3 -m tools._c29_retention_engagement_arm <off|on|net> <out.json> [report_end]
"""
from __future__ import annotations

import dataclasses
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: Renewals whose churn belief read each payment behaviour score, filled by `_observe_guard`.
SCORES_READ: dict[str, int] = {}


def _observe_guard(rp2b, record_estimate: bool) -> list[dict]:
    """Rebind the guard's two names on the run loop's module; return the list each decision fills."""
    from company.crm.customer_experience_desk import CustomerExperienceDesk
    from company.crm.engagement_estimate import engagement_at
    from company.interfaces.growth_desk import retention_bad_debt_charge

    guard: list[dict] = []
    pending: dict = {}
    renewal: dict = {}
    desk_value = rp2b.retention_value_protected
    desk_score = CustomerExperienceDesk.account_payment_behaviour_score
    desk_arrears = rp2b.LivePaymentTriad.arrears_state

    def observed_arrears(self, customer_id, as_of, segment="resi"):
        """The company's own arrears cell for the leg, and the renewal's keys. The renewal chain
        and the guard both ask it for the same leg and term start just before the guard reads its
        value, so the latest call is the guard's leg; rows keep `event_date` to check that."""
        state = desk_arrears(self, customer_id, as_of, segment=segment)
        renewal.update(customer_id=customer_id, billing_account=rp2b.household_of(customer_id),
                       event_date=as_of.isoformat(), arrears_state=state, segment=segment)
        return state

    def observed_score(self, supply_points):
        """Every renewal the churn belief reads, so `scores_read` is the denominator per score."""
        score = desk_score(self, supply_points)
        name = getattr(score, "name", str(score))
        SCORES_READ[name] = SCORES_READ.get(name, 0) + 1
        pending.update(behaviour_score=name, supply_points=list(supply_points))
        return score

    def observed_engagement(account_id, as_of, **kw):
        est = engagement_at(account_id, as_of, **kw)
        pending.update(account=account_id, date=as_of, fuel=kw.get("fuel"),
                       estimate=None if est is None else est.estimate,
                       prior_strength=None if est is None else est.prior_strength,
                       anniversaries=None if est is None else est.anniversaries,
                       channel=None if est is None else est.channel)
        return None if est is None else est.estimate

    class _Seen(float):
        def __gt__(self, other):
            # The run can compare one value twice (the gate's log re-asks it): one row per value.
            if getattr(self, "recorded", False):
                return float(self) > other
            self.recorded = True
            row = dict(pending) if record_estimate else {
                k: pending.get(k) for k in ("behaviour_score", "supply_points")}
            pending.clear()
            row.update(self.keys, unweighted=self.unweighted, weighted=float(self),
                       cost=float(other), bad_debt_charge=self.charge,
                       offered=float(self) > other,
                       offered_unweighted=(self.unweighted is not None
                                           and self.unweighted > other))
            guard.append(row)
            return float(self) > other

    def observed_value(expected_margin, acq_cost_saved, engagement, **kw):
        keys = dict(renewal, margin=expected_margin, acq=acq_cost_saved,
                    billed=kw.get("billed"), belief_rate=kw.get("default_belief_rate"))
        value = desk_value(expected_margin, acq_cost_saved, engagement, **kw)
        if value is None:
            # No contribution on the term: the guard weighs nothing and offers nothing. The
            # run's own `is not None` test decides; the row records that it was asked.
            row = dict(pending) if record_estimate else {
                k: pending.get(k) for k in ("behaviour_score", "supply_points")}
            pending.clear()
            guard.append(dict(row, **keys, unweighted=None, weighted=None, cost=None,
                              bad_debt_charge=None, offered=False, offered_unweighted=False))
            return None
        seen = _Seen(value)
        seen.keys = keys
        seen.unweighted = expected_margin + acq_cost_saved
        seen.charge = retention_bad_debt_charge(kw.get("default_belief_rate"),
                                                kw.get("billed", 0.0))
        return seen

    CustomerExperienceDesk.account_payment_behaviour_score = observed_score
    rp2b.LivePaymentTriad.arrears_state = observed_arrears
    rp2b.retention_engagement = observed_engagement
    rp2b.retention_value_protected = observed_value
    return guard


def main() -> int:
    arm, out = sys.argv[1], Path(sys.argv[2])
    report_end = sys.argv[3] if len(sys.argv) > 3 else None
    if arm not in ("off", "on", "net"):
        print(f"REFUSED: unknown arm {arm!r}; one of off, on, net")
        return 2

    import simulation.run_phase2b as rp2b
    from company.policy.decision_policy import CURRENT_POLICY, policy_scope

    policy = dataclasses.replace(CURRENT_POLICY, retention_weighs_engagement=(arm == "on"),
                                 retention_nets_bad_debt=(arm == "net"))
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
        "retention_nets_bad_debt": policy.retention_nets_bad_debt,
        "scores_read": SCORES_READ,
        "guard": guard,
        "policy": dataclasses.asdict(policy),
        "retention_log": result.get("retention_log"),
        "total_bad_debt": result.get("total_bad_debt"),
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
