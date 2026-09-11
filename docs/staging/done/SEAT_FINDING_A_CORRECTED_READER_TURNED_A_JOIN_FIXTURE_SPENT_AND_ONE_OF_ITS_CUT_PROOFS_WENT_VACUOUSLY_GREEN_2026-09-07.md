**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** AO3_join_test_tier ·
**Class:** controls_that_cannot_fail

# FINDING: a corrected reader turned a join fixture spent, and one of its cut-proofs went vacuously green

**2026-09-07 · seat · operational-layer persistent red, RUNG 1b · closed in this commit**

## The signal

`.operational_layer_signal.json` had been RED for five consecutive hourly checks — past paging, so
paging had not fixed it. Collection was healthy (1169 operational tests collected, no errors), so
this was not the collection-interrupt masquerade `process_run_complete` already catalogues. Four
genuine failures, all in one tier:

```
FAILED tests/system/test_join_cut_mutation.py::test_every_chain_passes_uncut
FAILED tests/system/test_join_cut_mutation.py::test_work_loop_fires_when_the_draw_stops_returning_work
FAILED tests/system/test_join_cut_mutation.py::test_work_loop_fires_when_the_draw_re_offers_finished_work
FAILED tests/system/test_join_work_loop.py::test_the_work_loop_join_conducts
```

## The cause — one defect, and it was a CORRECT fix upstream

On 2026-09-06 `supervisor._publish_gate_wedge_active` gained the window it had always documented:
`failures` is trimmed to a 1h window *by the writer*, and the writer only runs on a publish
**attempt** — so when the run-complete queue drains, a spent wedge's last failures sit in the file
forever and RUNG 1 draws at priority zero on a healthy pipeline. The repair applied the writer's
window to the reader's **count**. It is proven both ways in
`tests/background/test_publish_gate_wedge_draw.py` (134 green), and it is right.

`tests/system/chains.py::run_work_loop_chain` built its wedged fixture with **one clock**: every
failure stamped `now - wedge_age_seconds`, the same instant as `wedge_since`. A "2h old wedge" was
therefore five failures all two hours old and nothing since — which is not a live wedge, it is the
exact spent shape the repair exists to declassify. The reader correctly returned `None`, and chain 1
of the join tier went red with it.

**A live wedge has two clocks.** Its AGE is `wedge_since` (deliberately un-trimmed, so a long
wedge's true age stays measurable); its LIVENESS is failures inside the window — a wedge that is
still wedged fails every ~10 min. The fixture asserted the first and forgot the second.

Two of the four reds are pure masking: `test_work_loop_fires_when_the_draw_*` match on
`JOIN CUT (work → draw)`, and the publish→draw assertion above it now fired first.

## The part worth keeping — the fifth test, which stayed GREEN

`test_work_loop_fires_when_a_wedged_publish_gate_stops_reaching_the_draw` cuts
`_publish_gate_wedge_active` to `lambda: None` and asserts the join notices. It passed throughout —
**vacuously**. The uncut verdict was *already* `None`, so the cut removed nothing. A cut-proof that
cannot fail, inside the one module whose own docstring says the fail-open shape it exists to hunt is
"a join test that PASSES when the chain it spans is disconnected".

Nothing in the red pointed at it. The four failures named the two tests that broke loudly; the test
that broke *silently* was the one that mattered, and it is only visible by asking the R15 question
of the passes as well as the failures. **A green beside a red from the same cause is a suspect, not
a control.** (`[[feedback_prove_reachability_with_a_poison_round_before_a_mutation_battery_because_survived_means_two_opposite_things]]`)

## The fix

`run_work_loop_chain` now stamps failures inside the writer's window and takes the wedge's age from
`wedge_since`. Spacing is **derived** from `PUBLISH_GATE_WINDOW_SECONDS`, imported from
`process_run_complete` and never mirrored — so raising `wedge_failures` cannot quietly walk the
oldest failure back out of the window, and the reader and the fixture cannot disagree about what
"in-window" means. A premise guard refuses outright if the oldest stamp lands outside it, rather
than silently describing a spent wedge again.

**Keyed to the property, not to today's answer**: the fixture now says *live wedge, hours old*,
which is what the assertion claims to be testing. The old fixture said *a wedge, hours ago*, which
was only ever readable as live by a reader with a bug in it.

## Evidence

- `tests/system/test_join_work_loop.py` + `test_join_cut_mutation.py`: 20 passed.
- POISON ROUND on the vacuous cut-proof — cut removed, test re-run: `DID NOT RAISE` (rc=1). The
  proof now has reach. Restored, green.
- `tests/background/test_publish_gate_wedge_draw.py`: 134 passed — the upstream repair is untouched.

## The class

A fixture is a claim about the world. When a reader is corrected, every fixture that encoded the
*old* reader's tolerance becomes a claim about a world that no longer exists — and the ones that go
red are the lucky ones. The dangerous residue is a fixture that still satisfies its assertions for a
reason the assertion never named.
