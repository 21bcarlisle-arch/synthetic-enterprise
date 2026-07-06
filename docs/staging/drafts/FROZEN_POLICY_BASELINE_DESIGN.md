[DESIGN NOTE] Frozen-Policy Baseline / Delta-EV -- Tier 3, proceeding in 4h unless redirected

## The ask (WEBSITE_AS_SHOWCASE.md tab 2, SUPPLIER_TAB_OVERHAUL.md line 26)

"Build the frozen-policy baseline: replay the same decade with last-generation policies
(pre-decision-loop, pre-deferral-pricing, naive retention) vs current policies -> delta-EV =
THE VALUE OF LEARNING." Explicitly flagged in both staged docs as needing its own Tier 3 design
note first because "policy snapshot/replay is a one-way-door-adjacent mechanic."

## What "policy" actually is today

There is no swappable policy object. The decisions that would need to vary between
"last-generation" and "current" are inlined as module-level constants and if/else branches
directly in `simulation/run_phase2b.py::main()`:
- Retention: `RETENTION_THRESHOLD=0.30`, `RETENTION_TIERS` (line 186-190, Phase 14a),
  `RETENTION_EFFECTIVENESS=0.20`, and the margin+acquisition-cost guard at the offer decision
  (Phase 15b) -- lines ~1069-1103.
- Hedging: `decide_hedge_fraction()` (`company/trading/hedge_decision.py`, VaR-forward, Phase 43b)
  is the live per-term hedge fraction; `company_evolve_hedge_fraction`
  (`company/risk/hedge_policy.py`, Phase 22b, backward-looking raise/trim) still runs every
  settled term.
- Deferral pricing: `ASSUMED_DEFERRAL_MONTHS=12` and `retention_deferral_economics.py` (Phase QM)
  are observational only right now -- they measure realized deferral windows but do not feed
  back into the retention guard. "Pre-deferral-pricing" is therefore not a real fork in the
  current code; a design note that pretended otherwise would be describing a feature that
  doesn't exist. Flagging this as an honest gap, not assuming a toggle that isn't there.
- `company/crm/customer_retention.py::CustomerRetentionBook` exists but is dead code on the live
  path -- `run_phase2b.py` never calls it. Any "old policy" module must not be confused with this.

"Last-generation" therefore has no separate implementation to point at -- it has to be
reconstructed as an explicit alternate parameter set, anchored to specific superseded phases:
naive retention = flat 5% discount, no tiers, margin-only guard (pre-14a/pre-15b, i.e. Phase 12d
state); pre-VaR hedging = `company_evolve_hedge_fraction` alone, no `decide_hedge_fraction` layer
(pre-43b, Phase 22b state).

## Why replay must be a full re-run, not a recompute from stored records

Retention/hedge decisions change realized SIM-side settlement outcomes (churn timing, revenue,
margin) -- `enterprise_value.py` and `cost_to_serve.py` are built from those realized records, so
a different policy produces a genuinely different book, not just a different label on the same
numbers. There is no way to recompute a counterfactual book after the fact; `run_phase2b.main()`
has to execute again with the alternate policy plugged in.

This is cheaper than it sounds because it is already replay-safe: churn and acquisition dice
rolls are locally keyed (`random.Random(f"{billing_account}_{term_start_str}")`,
`simulation/customer_events.py:98`; same pattern for acquisition at `run_phase2b.py:1204`), not
drawn from one global seed. Running the same decade twice with different policy constants
reuses the identical roll values -- any divergence in outcomes is attributable to the policy
change alone, not fresh randomness. That is what makes a real A/B replay possible instead of an
unfalsifiable comparison against a fresh noisy sample.

## Options

A. Refactor `run_phase2b.main()` to take a required policy struct, no default -- forces every
   caller (all tests, `run_phase4b/4c_on_phase2b.py`, `sim_runner`) to pass one explicitly.
   Correct in the limit but touches the signature of the core sim entry point everywhere at once
   -- large blast radius for a first cut.
B. Add an optional `policy: DecisionPolicy | None = None` parameter to `main()`, defaulting to
   today's exact behaviour (the module-level constants become the default struct's field
   values) -- zero behaviour change for every existing caller/test. A new
   `tools/run_frozen_baseline.py` calls `main()` twice over the same historical window: once with
   the default (current) policy, once with an explicit `NAIVE_POLICY` struct pinned to the
   pre-14a/15b/43b constants above, each citing its superseding phase number as a comment. Diff
   both books through `build_enterprise_value()` -> delta-EV. The baseline run is a periodic
   frozen artifact (recomputed on demand / at phase close, not on every sim cycle) since
   "last-generation policy" is a fixed historical reference point, not something that needs to be
   live every run -- bounds the cost of doubling a full decade simulation.
C. Build a standalone lightweight harness that duplicates just the retention/hedge decision
   branches outside `run_phase2b.py`, run against the same historical settlement inputs. Cheaper
   to build but the replay logic would drift from the real decision code over time -- rejected,
   a counterfactual has to run the same code path or it stops being a genuine counterfactual.

Recommendation: B. Backward-compatible (nothing existing changes signature-visibly or
behaviourally), the invasive part (introducing a DecisionPolicy struct) is additive, and the
expensive part (a second full decade run) is bounded to an on-demand/periodic artifact rather
than a per-cycle cost. First implementation slice: extract the retention/hedge constants above
into a `company/policy/decision_policy.py` dataclass with a `CURRENT_POLICY` default and a
`NAIVE_POLICY` (pre-14a/15b/43b) baseline; wire the optional param through `run_phase2b.main()`;
build `tools/run_frozen_baseline.py`; delta-EV surfaces on Supplier Overview per
SUPPLIER_TAB_OVERHAUL.md line 26 once this lands.

## Tier classification

Tier 3 per both staged documents' own framing -- introducing a parameterizable policy surface on
`run_phase2b.main()` (even backward-compatible/additive) touches the core simulation orchestrator
every other run mode depends on, which is one-way-door-adjacent: once other code starts branching
on `policy=`, reverting becomes progressively costlier. 4h opt-out window applies; proceeding with
option B unless redirected.
