# [WORKER FINDING] The cost instrument still requires the directory the R3 elimination deleted

**Filed:** 2026-08-11 · **Atom:** `OPS2_publish_gate_head_worktree` · **Status:** CLOSED
2026-08-11, drawn as the atom's own work. The recommendation below was taken as written: the
phase set is collapsed to `throwaway_checkout` vs `in_tree_baseline`, the reused-name
precondition is INVERTED rather than removed, and the ratio now measures the tax. One thing the
finding did not foresee and the repair had to add: collapsing `PHASE_ORDER` alone would have
dropped the banked `cold_checkout` from the record on the next launch and taken
`measured_gate_timeout_floor` to `None` — starving the fail-closed control this finding is
*about*. Retired phases are carried for the floor and barred from the ratio. See
`docs/design/OPS2_PUBLISH_GATE_HEAD_CHECKOUT.md` §"STATUS 2026-08-11" and the atom record.

## Observed, with evidence

`444402ee0` eliminated the reused HEAD checkout under R3 (`REUSE_HEAD_CHECKOUT = False`), so
`prc._head_checkout()` now always yields a throwaway named `publish-gate-head-<random>`.

`tools/measure_publish_gate_subject_cost.py` gates both of its checkout phases on getting the
SHARED name back:

```
1084:  if path.name != prc.REUSED_HEAD_CHECKOUT_NAME:
1085:      log("! got a THROWAWAY checkout ... another publisher holds the reuse lock ...")
1088:      results["aborted"] = "another publisher held the reuse lock"   # returns 1
1115:  if path is None or path.name != prc.REUSED_HEAD_CHECKOUT_NAME:
1118:      results["aborted"] = "lost the reused checkout between phases"  # returns 1
```

Since 444402ee0 that condition is true on **every** launch. The instrument cannot complete, and
it will record `aborted: "another publisher held the reuse lock"` — a cause that is not merely
wrong but points the next diagnosis at a lock that no longer has anything to protect.

## Why it matters — the consumer is a fail-CLOSED control

`prc.measured_gate_timeout_floor()` is the evidence `GATE_SUITE_TIMEOUT_SECONDS = 2600` rests on,
and `test_the_timeout_clears_the_floor_the_measurement_implies` asserts `floor is not None`, i.e.
an unanswerable record REDS the gate. Today the committed record still answers, from one banked
phase: `cold_checkout` at **1291.9s** → floor **2583s**, cleared by 2600s with **17s of slack**.

So the bound is not wedged — but it can never be *re-derived*, because the only instrument that
could refresh the record now aborts before timing anything.

## The sharper half: that 1291.9s is not the shipped subject

`observed` — the banked phase ran with `cwd: /tmp/publish-gate-head-reused`, and the record's own
`warm_cache_established_by: "an earlier launch or the live publisher"` says the directory's
bytecode came from outside that run. `inferred` — the shipped subject is now a genuinely cold
throwaway every cycle, which is at or above that number, and the atom's mint quotes ~2.5×
in-tree (~1500s) for a cold checkout. A floor derived from 1400s would be 2800s and would red the
control. **The bound's 17s of slack sits on a phase measured in a directory that no longer
exists.**

## What the repair has to decide (not a patch)

Post-elimination there is no warm phase, so `PHASE_ORDER = ("cold_checkout", "warm_checkout",
"in_tree_baseline")` and `RATIO_PHASES = ("warm_checkout", "in_tree_baseline")` are both
describing a dead configuration. The measurement the atom now needs is `throwaway_checkout` vs
`in_tree_baseline` — that ratio IS the permanent tax the elimination bought, i.e. the honest
successor to superseded exit criterion 1, and `in_tree_baseline` has never once been timed across
nine launches.

**Recommendation:** collapse the phase set to the two that still exist, drop the reused-name
preconditions, and let the surviving ratio measure the tax rather than the (now unavailable)
saving. Do NOT patch the name check to accept a throwaway while leaving the phase called "warm" —
that would leave the record claiming a comparison it did not make.

## Class

Same shape as `feedback_live_mechanism_with_a_dead_input` and
`feedback_a_measurement_tool_never_lands_the_evidence_its_control_reads`: an elimination moved the
mechanism and left an instrument whose *precondition* was the eliminated thing. The instrument
does not fail loudly — it fails with a confident, false, pre-written reason.

— Worker, scheduled tick 2026-08-11
