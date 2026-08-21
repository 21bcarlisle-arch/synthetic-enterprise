**Severity:** BLOCKING · **Lane:** H_harness

# FINDING — the publisher's internal gate timeout is recorded as a test regression, and the gate's own scope contains a single file costing more than the whole absolute cap

**Found by:** the scheduled worker tick of 2026-08-21 16:10-16:25Z, drawn on the director's
console instruction of 04:38Z — *"Publishing has been down about ten hours — take it first."*
**Companion:** the diagnostic half of this outage is FIXED in the same tick
(`tests/background/test_publish_failure_names_its_cause.py`); this document is the half that is
filed and not fixed, per SELF_INTERRUPT_DISCIPLINE (queue by default).

## Class registration

`CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12`

## Observed, with evidence

Every claim below is `observed-with-evidence` (R9), read off disk and `ps` at 2026-08-21 16:10-16:25Z.

### 1. The wedge is 32 hours old and 43 of its 46 refusals were genuine reds

`docs/observability/.publish_gate_state.json` carries `wedge_since: 1787212714.6` =
**2026-08-20T07:58:34Z**. Counted from `docs/observability/sim-runner-log.md` over
2026-08-20/21: **46** `Scoped publish-path gate FAILED`, of which **3** were preceded by
`Fast test suite timed out` (two at `>4500s`, one at `>300s`). The other 43 were completed,
genuinely red gates.

### 2. The red the wedge last named is GREEN at HEAD

`docs/observability/.last_gate_blocking_tests.json` (written 13:14Z, git `2c0ba712b`) names one
node:

```
FAILED tests/background/test_blocked_atom_visibility.py::test_on_the_live_map_the_rulings_named_subjects_are_covered_and_their_unparked_set_is_frozen
```

Run at HEAD `00da830c4` during this tick: **`1 passed in 0.29s`**. The record is also stale past
`GATE_BLOCKING_TESTS_MAX_AGE_SECONDS`, so `last_blocking_tests()` correctly returns `[]` — which
is why `.publish_gate_state.json` shows `blocking_tests: []` and `total_red: 0` while recording
two failures. **The wedge currently names no red at all**, and the one it last named is fixed.

### 3. A timeout is recorded as `test_regression` — the sibling half of a defect already closed once

`_classify_gate_failure` (`background/process_run_complete.py:4380`) maps **every** positive
return code to `test_regression`. The publisher returns `1` for a genuine red, for report-regen
failure, for a missing JSON — **and for its own internal gate timeout**, because
`Fast test suite timed out` sets `tests_ok=False` and falls into the same `return 1`.

This project has already closed this class **on the outer half**. `sim_runner.py` and
`background_worker.py` both pass `kind="deadline_kill"` with no invented return code, under a
comment stating the reason exactly: *"rc=124 WAS: the classifier maps any rc>0 to
`test_regression`, which is how a stopwatch became 145 recorded test failures and sent the RUNG-1
draw after a gate that was never judged."* The INNER timeout — the publisher's own gate clock —
still has no such carve-out.

**Live consequence, in the state file right now:** both recorded failures read `test_regression`
while `total_red` is `0`. The 16:03Z one is provably a stopwatch, not a test:

```
- [2026-08-21 16:03 UTC] [process_run] Fast test suite timed out (>300s) -- NOT committing.
- [2026-08-21 16:03 UTC] [process_run] Scoped publish-path gate FAILED - not committing content
```

### 4. The new 300s cap cannot be met by the scope it is applied to

`GATE_SUITE_TIMEOUT_SECONDS` and `PUBLISH_GATE_ABSOLUTE_CAP_SECONDS` were both set to **300** at
`8d6f4a2b4` (16:10Z today), correctly answering the director's 14:56Z instruction. The
justification is measured and is quoted in the constant's own comment: *"1,183 tests, 38.6s,
rc=0."*

**Two facts observed since, both of which post-date that measurement:**

- The live gate now reports a **larger scope than the one measured**:
  `- [2026-08-21 16:15 UTC] [process_run] Publish gate scope: 6 publish-path source(s) -> 197
  blocking test file(s) via the static import graph.`
- **One file in that scope exceeds the entire cap on its own.** Run in isolation during this
  tick, `tests/background/test_derived_artefact_register.py` was killed at 300s without
  completing, and again at 280s for `::TestStaleness` alone. Its `stale_in()` shells out to
  `python3 -m <module> --check` for all three registered artefacts, and
  `background.blocked_atom_visibility --check` was independently observed holding ~100% CPU for
  **3m05s** inside the live publisher (PID 2104504, 17:08 BST).

The first cycle run under the new bound timed out (§3 above). **A cap the scope cannot meet
converts every future publish into a timeout**, which — by §3 — will be recorded as a test
regression naming no test.

## Not a claim that the cap is wrong

The cap is right and the director's reasoning for it is right: *"A check that takes 75 minutes in
a repo changing every 15 isn't verifying the current state, it's reporting on the past."* The
defect is that the scope was not brought under the cap at the same time. The director named the
remedy in the same message and it is not raising the bound: *"Not by deselecting tests to move
the number — by deciding what genuinely must run before a publish and what belongs somewhere else
entirely, on its own cadence."*

`test_derived_artefact_register.py` is the clearest instance. It asks whether three committed
markdown projections are current — a **repo-invariant**, true or false at commit time, checked at
publish time for longer than the entire publish budget. By the split `8d6f4a2b4` itself states
("Repo-wide invariants -> commit time"), it belongs in the always-run commit list, not the gate.

## Recommendation (acting on it is the next tick's draw, not this one's)

1. **Give the inner timeout its own `kind`.** `record_publish_gate_outcome` should receive
   `kind="deadline_kill"` from the publisher's internal gate-timeout branch exactly as the two
   outer callers already do, so a stopwatch stops being filed as a red test. Smallest change,
   closes the sibling half, and is R15-testable both ways.
2. **Move the repo-invariant tests out of the gate scope onto the commit list** — starting with
   `test_derived_artefact_register.py` — and re-measure the scope's wall time against the 300s
   cap. Do NOT raise `GATE_SUITE_TIMEOUT_SECONDS`; `test_publisher_deadline_exceeds_its_gate.py`
   is correct to refuse that, and the seventh raise should have to argue in the open.
3. **Have the cap fail loudly on the SCOPE, not only on the run.** The cap currently discovers an
   over-budget scope by timing out a publish. A cheap pre-flight — the scope's own last measured
   wall time vs the cap — would name the offending file instead of killing the cycle.

**A measurement of the real gate wall-time was already in flight in another session during this
tick** (`_scoped_gate_argv` timed against the live tree, PID 2111308, still running at 8.5 min —
itself past the 300s cap). Reconcile with that record before re-measuring; do not duplicate it.

## Reversibility

Nothing here is a one-way door. Item 1 is a `kind=` argument. Item 2 moves test files between two
lists in `background/publish_scope.py` and is a `git revert` away. Item 3 is additive.
