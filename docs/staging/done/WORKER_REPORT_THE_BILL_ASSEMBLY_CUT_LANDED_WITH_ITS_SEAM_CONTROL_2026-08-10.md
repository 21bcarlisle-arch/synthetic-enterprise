# [WORKER-REPORT] KNIFE3 step 11 landed — and the seam it created had no control until now

**Severity:** RECORDED · **Lane:** W4_the_wall

**Atom:** `KNIFE3_wall_crossing_paydown` (KNIFE pass 3 of 4, lane H_harness)
**Date:** 2026-08-10
**Status:** step 11 landed; the pass continues (edges still owed to `A_composition_lift`)

## What was found

Step 11 — bill assembly moved out of the world and behind
`company/interfaces/bill_assembly.py` — was **built but never committed**. It sat in the
working tree: two untracked modules (`company/billing/monthly_bill_assembly.py`,
`company/interfaces/bill_assembly.py`), a 441-line deletion from
`simulation/run_phase4c_on_phase2b.py`, the `SimulatedReadFeed` adapter in
`simulation/meter_reads.py`, three tuples removed from `LEGACY_SIM_READS_COMPANY`, and the
register/docstring updates. Uncommitted work on this shared tree is not neutral — the gate
lints the working tree, so it wedges every other lane while it sits there.

It also had **no seam test**, alone among the seams this programme has produced. Passes 1
and 2 each shipped one (`test_supply_book_seam.py`, `test_renewal_offer_seam.py`), as did
B4 and B5 (`test_dd_review_outcome_seam.py`, `test_collections_communication_seam.py`).

## What the missing control was for (R15)

The wall ratchet polices the STATIC half of this cut and carries its own mutation proof. It
is blind to the two shapes this particular cut is most exposed to:

1. **A lazy import.** The ratchet's docstring states the limit: static imports only. The
   natural convenience change here is to make `read_feed` optional and construct the
   world's feed inside `build_monthly_bills` — which re-crosses the wall in the strictly
   forbidden direction with every static instrument in the tree still green. The new
   control runs the real billing run in a CLEAN interpreter and reports what loaded
   (in-process, `simulation.*` is already in `sys.modules`, so a lazy import would be
   served from cache and leave no trace). Observed: **2 bills built, zero sim/simulation
   modules loaded.** Its mutation injects `import simulation.meter_reads` into a copy of
   the module's real source and asserts the probe reds — it does.

2. **A reordered feed.** `ReadArrivalFeed` is `runtime_checkable`, which checks method
   PRESENCE only, never signatures — and every feed call site in `build_monthly_bills`
   passes POSITIONALLY. A swap of two parameters in `SimulatedReadFeed` would mis-bind a
   kWh float into a trailing-actuals list without raising. The control compares parameter
   names AND order; its mutation exhibits a reordered feed that `isinstance()` still
   accepts. **The `isinstance` check alone was not evidence.**

## Evidence

- `tests/company/interfaces/test_bill_assembly_seam.py` — 8 passed.
- `tests/architecture/test_epistemic_wall_ratchet.py` + `_single_source` + `_indirect_ratchet`
  + `tests/tools/test_wall_crossing_dispositions.py` — **98 passed in 33.9s**.
- `python3 -m tools.epistemic_verifier` — **PASS**, 541 company/saas files, no violations.
- `ruff check` clean on the new and changed files.

## What is NOT claimed

Neither the B4 nor the B5 **push** is built. Step 11 created the emitter both designs named
as their blocker; building a push on top of it in the same breath would be the "shape of a
push with the substance of a pull" both seam modules explicitly refuse. Both remain owed,
now against a live seam rather than a missing one.

`run_phase4c_on_phase2b.main()` keeps its other ten crossings, and `run_phase2b`'s 32 direct
+ 2 indirect are untouched. The pass is not finished; this is one step of it.

## Generalisable lesson

**A seam is not landed until the thing that can fail it is landed with it.** Every prior
pass in this programme shipped its seam test in the same commit as its seam; this one did
not, and the gap was invisible because the wall ratchet is green either way — it measures
the edge count, not whether the new chokepoint can rot. Where a cut's correctness rests on
an *inversion* rather than a *count*, the ratchet is the wrong instrument by construction
and a behavioural control is owed.
