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

---

## RESOLVED 2026-08-09 — and this finding's own attribution was wrong

Actioned by the W1_12 tick that landed the cold-appliance coupling. Fixed as the class fix this
finding asked for, **not** re-pinned.

### The attribution above is corrected (R9 — measured, not inferred)

This finding reasoned: *"No fabric source file is dirty in the working tree ... so the failure
reproduces at HEAD"*, and guessed commit `25d317076`. **Both are wrong.**

`simulation/premise_trace.py` **was** dirty — it held the entire, uncommitted W1_12
cold-appliance coupling. The finding's `git status` read looked for *fabric* files and the
dirty file was the *generator*, which is upstream of the same statistic.

Measured directly, rather than bisected on a guess — restore HEAD's copy of that one file and
run the test:

```
HEAD's premise_trace.py      -> 1 passed          (worst_value 0.1804)
working-tree premise_trace.py -> 1 failed          (worst_value 0.1782)
```

So the cause was **the very work whose completion the maturity map had already recorded**. The
finding's *class* diagnosis was right and its "false red — an honest physics improvement moved
0.1804 → 0.1782" line was exactly right; only the attribution paragraph was wrong.

**The generalisable bit:** this finding cleared HEAD by checking that no file *in the failing
test's own subsystem* was dirty. The dirty file was one layer upstream, in a subsystem the test
never names. "Reproduces at HEAD" needs the HEAD binary actually run, not an inventory of which
files look clean — which is what the two-line experiment above cost.

### What was done

`tests/tools/test_couple_fabric.py`: the `worst_value == approx(0.1804, abs=5e-4)` literal is
**gone**, not retyped to `0.1782` (retyping is the R12 reflex this finding predicted). The test
now pins the mechanism it is named for — the band is a floor at an **unmoved** 0.15, its
direction is asserted rather than assumed, and the worst home clears it on its own.

R15 both ways, so the reshape is not a fail-open:

- **band-moved arm** — monkeypatches the real gas band down to 0.10, re-runs the real
  measurement, and watches the "not moved" assertion reject it. This is the mutation this
  finding specified.
- **regression arm** — hands the real measured cell, worst value pushed under its own real
  floor, to the *same* expression the closure test depends on (extracted as
  `_worst_cell_clears_its_own_floor`, so the mutation exercises the control and not a re-typed
  copy beside it), and requires it to raise. An unmutated call runs first, so a control that
  raises on everything cannot pass.

An `assert 0.14 < 0.15` arm was written and then deleted: it proves only that Python compares
floats — the tautology shape that keeps reappearing inside this project's own R15 evidence.

**Not minted as a separate atom** (the suggested disposition): the control was red *under the
change being landed*, so fixing it was the cost of committing rather than a queued finding acted
on out of order.

Evidence: `docs/design/maturity_map.yaml`, `W1_12_premise_trace_generator`, final evidence entry.
