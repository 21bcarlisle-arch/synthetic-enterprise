# PROCEED BY DEFAULT — the director is not an approval queue (P0, standing)

**Staged:** 2026-07-12 by advisor. **Director-decided, verbatim in force:**
*"Why am I the bottleneck? That's a terrible setup. There are very few true
one-way doors. The vision is reasonably stable. There is loads of work to do,
it's just not getting done."* He is right. This corrects a design error the
ADVISOR introduced and the agent inherited.

## The error being corrected
We built a governance model appropriate to a company handling real customers'
money, and then applied it to BUILDING THE SIMULATION. Those are different
things:
- **The simulated company's governance** (decision rights, approval interface,
  scrutiny dial) is a FEATURE we are building. Keep it. It is the point.
- **The builder's governance** (what needs the director's OK before you write
  code) must be MINIMAL. Caution from the first has been leaking into the
  second and it is costing the project its velocity.

## The reversibility test (new default)
This is a simulation in version control. Code reverts. Runs re-run. Levels
demote. Atoms re-rank. A wrong decision costs an hour and yields a finding.
**Therefore: PROCEED unless the action is genuinely irreversible.**

**The complete one-way-door list — escalate ONLY for these:**
1. Spending real money.
2. Real-world commitments: legal, regulatory, contractual; anything binding
   outside the repo.
3. Public claims that cannot be retracted (published figures/claims that would
   mislead if wrong — note: labelled PROVISIONAL figures are retractable).
4. Irrecoverable data loss (canonical state with no backup).
5. Security posture / secrets exposure / safety-control changes.
6. **Values decisions defining what the company is FOR** (e.g. the Epoch-4
   fitness function). These are the director's by right, not by process.
7. Anything touching a real customer or a real market (none exist yet).

**Everything else: PROCEED.** Build it, log the decision and its rationale,
carry on. The director reviews the decision log at digests/boundaries and
REVERSES anything he disagrees with. Reversal is cheap; waiting is not.

## Consequences (apply immediately)
1. **Stop asking permission for reversible work.** Ambiguity is not a reason to
   stop; it is a reason to choose, log, and continue.
2. **Decision log:** every non-trivial autonomous choice gets a one-line entry
   (what, why, how to reverse). Surfaced in the digest and on the site. This
   is the audit trail that MAKES the autonomy safe.
3. **The plan must MINIMISE director-hours, not schedule around them.** Rewrite
   the forecast objective: maximum map movement per director-hour. Report
   which of the last 20 escalations were actually reversible (expect: nearly
   all) — that number is the measure of the error.
4. **Expert Hours: delegate.** Run cold-eyes personas as the standing quality
   bar; the director spot-checks rather than gating. His eye is a sample, not
   a queue.
5. **The vision is stable.** Epoch arc, laws, methods, map: settled. You have
   what you need to make ~95% of decisions. Make them.
6. **Advisor's own correction:** the advisor will stage less and let the
   self-refill draw more. A hand-fed queue is a second bottleneck, and it is
   the advisor's fault, not the agent's.

## The one thing that does NOT change
Exit tests, invariants, honesty about levels, and the Historical Ground Truth
/ epistemic wall laws are NOT approvals — they are physics. Autonomy means
proceeding without permission, never lowering the bar. If anything, with the
approval friction gone, the tests must be stricter.

## DoD
Reversibility test + one-way-door list in CLAUDE.md, replacing the current
escalation defaults; decision log live and in the digest; escalation-audit of
the last 20 asks reported (how many were reversible?); plan objective changed
to director-hours-minimised; then DRAW AND WORK — there are 23 atoms at L0 and
a stable vision. Go.
