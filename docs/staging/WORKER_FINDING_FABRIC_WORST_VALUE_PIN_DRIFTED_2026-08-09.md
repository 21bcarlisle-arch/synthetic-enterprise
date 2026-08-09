# WORKER FINDING — a pinned generated value in the fabric control has drifted red

**Found:** 2026-08-09, incidentally, by the `D13` DISCOVER tick running `tests/tools/` in full.
**Not fixed on sight** (SELF_INTERRUPT_DISCIPLINE — queued as a finding, the machine is not blocked).

## The observation

```
FAILED tests/tools/test_couple_fabric.py::
       test_the_LAST_RED_CELL_closed_by_the_BAND_being_conditioned_not_moved
E   assert 0.1782008038098004 == 0.1804 ± 5.0e-04
```

`tests/tools/` is otherwise green: **1 failed, 2110 passed, 4 skipped, 2 xfailed**.

## Attribution — observed, not inferred (R9)

It is **not** from this tick's changes. The D13 tick touched exactly four paths
(`docs/design/D13_SELF_RATIONING_NEGATIVE_POPULATION_DISCOVER.md`,
`docs/design/maturity_map.yaml`, `docs/observability/gate_authorizations.jsonl`,
`tools/couple_w2_11_d5.py`). `tools/couple_fabric.py` imports
`simulation.fabric_physics`, `simulation.premise_population`, `simulation.premise_trace`,
`company.pricing.thermal_inference`, `company.pricing.fabric_intervention`,
`background.fabric_gap_ledger` — **none of them**. The two places the test reads
`maturity_map.yaml` are different assertions (atom-id and coupling-registration checks) and both
pass; the failing assertion is `texture.worst_value`, pure fabric physics with no map input.
No fabric source file is dirty in the working tree (`git status` shows only the derived
`docs/observability/fabric_settlement_gap.json`), so the failure reproduces at HEAD.

Most likely cause, **inferred** and not yet confirmed: `25d317076 W2_15 L0->L2` is the most recent
commit touching `simulation/`. Whoever picks this up should bisect rather than trust that guess.

## Why this is worth an atom rather than a one-line re-pin

This is the **"never pin a generated value in a control"** class again. The test's own name says
the cell was closed *by the band being conditioned, not moved* — its job is to prove the closure
was not goal-seek. But it discharges that job by pinning `worst_value` to a four-decimal literal,
so **any** upstream fidelity change to the physics turns the control red without saying anything
about goal-seek either way. Two failure modes, both live:

1. **False red** (probably today): an honest physics improvement moved the worst home 0.1804 →
   0.1782 and the control reports it as a regression.
2. **The re-pin reflex**: the cheap fix is to edit the literal to 0.1782, which trains exactly the
   habit R12 forbids — moving the expected number to match the produced one. If that is done
   without re-deriving *why* the value moved, the control's real assertion (band conditioned, not
   moved) is silently discharged by a number nobody re-checked.

The fix is to assert the **invariant the test is named for** — that the worst cell sits inside the
conditioned band and that the band was not widened to admit it — rather than the specific value.
The value can stay as a reported diagnostic (R12) with a tolerance wide enough to survive fidelity
work, or be dropped entirely in favour of the relational assertion.

## Suggested disposition

Mint as a HARNESS atom against `tests/tools/test_couple_fabric.py`, level target 2, with an R15
mutation proving the replacement still fires on its own named defect (a band **widened** to admit
the worst cell must go red) — otherwise the reshape just fail-opens the control it replaced.
