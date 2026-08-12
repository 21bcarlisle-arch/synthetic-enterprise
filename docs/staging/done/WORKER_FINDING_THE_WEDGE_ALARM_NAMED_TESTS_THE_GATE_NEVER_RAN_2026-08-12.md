# WORKER FINDING — the wedge alarm named five tests the gate never ran

**Severity:** LATENT · **Lane:** H_harness

**Filed:** 2026-08-12 · **Lane:** H_harness · **Class:** R15 fail-silent / R5 payload
**Status:** FIXED — parser scoped to the last short-summary section; R15-proven both ways
(3 new tests fail on the pre-fix parser in a clean HEAD checkout, pass after; the 11
pre-existing payload tests pass in both arms). Change 1 of the proposed fix is built;
change 2 (the R15 mutation test) is built. The free scope cross-check is NOT built — filed
as the remaining half below.

## The claim

`observed-with-evidence` — For the 187-failure publish wedge that ended at 2026-08-12
01:57Z, the alarm's `blocking_tests` payload named five tests that the publish gate is
**structurally incapable of running**, while the actual blocker appeared nowhere in it.

Recorded in `docs/observability/.publish_gate_state.json`:

```
"blocking_tests": [
  "FAILED tests/background/test_supervisor.py::test_harden_suppression_is_content_driven_not_only_filename",
  "FAILED tests/background/test_supervisor.py::test_harden_suppression_ignores_parked_and_archived_rulings",
  "FAILED tests/background/test_supervisor.py::test_harden_suppression_ignores_daemon_markers",
  "FAILED tests/background/test_supervisor.py::test_ruling_mint_instruction_mints_from_block_and_flags_missing_block",
  "FAILED tests/background/test_supervisor.py::test_ruling_steer_missing_work_block_lists_only_blockless_rulings"
]
```

Three independent facts, each `observed-with-evidence`, say the gate never ran them:

1. **The whole module is deselected.** `tests/background/test_supervisor.py:2536` sets a
   module-level `pytestmark = pytest.mark.operational` (intentionally — the block above it
   declares the file a DAEMON-LIFECYCLE module). The gate's marker expression is
   `not operational and not join_report_only and not scale_report_only`. Measured:
   `pytest tests/background/test_supervisor.py -m 'not operational'` → **186 deselected,
   no tests collected**.
2. **The file is not in the blocking scope.** `_scoped_gate_argv` resolved to
   *"6 publish-path source(s) → 134 blocking test file(s)"*; `test_supervisor.py` is not
   one of the 134.
3. **They pass anyway.** Run without the marker filter: **5 passed, 181 deselected in 5.00s**.

The real blocker, from the same log block (`sim-runner-log.md`, 01:24Z):

```
FAILED tests/controls/test_daemon_loop_mutation.py::test_stall_alarm_fires_when_commit_stale_and_work_queued
1 failed, 945 passed, 192 deselected, 1 xfailed in 624.44s
E   OSError: [Errno 28] No space left on device   (background/deadmans_switch.py:135)
```

## The mechanism

`_parse_failed_node_ids` (`background/process_run_complete.py:1838`) is:

```python
return [ln.strip() for ln in (out or "").splitlines()
        if ln.startswith(("FAILED ", "ERROR "))]
```

It scans the gate subprocess's **entire combined stdout+stderr**. The gate runs with `-x`,
so pytest's own short summary contains **exactly one** `FAILED` line. But tests in the
blocking scope run *nested* pytest invocations and print their output — the
operational-layer signal is one, and it reports the COMPLEMENT marker set, which is
precisely where `test_supervisor.py` lives. Those lines arrive inside a
`----- Captured stdout call -----` block and are indistinguishable, to a `startswith`
check, from the gate's own summary.

So the twelve `test_supervisor.py` lines in the 01:24Z payload are the operational-layer
signal's failures, captured and re-emitted through the gate's stdout. The two surfaces are
documented as decoupled — *"it cannot block, skip, or alter what the content gate
publishes... Purely observational"* (`process_run_complete.py:260-266`). They are decoupled
in control flow and coupled in the **diagnostic payload**, which is the half nobody checked.

## Why it cost real time

The payload feeds the RUNG-1 priority-zero doorbell. This tick's doorbell instructed:
*"FILED FINDINGS ALREADY HOLDING THE SUSPECTS — draw these FIRST"* and named six findings
plus the five tests above. All eleven were wrong. The cause — a tmpfs at 67% throwing
ENOSPC through a `tmp_path` write — was named by none of them.

**It reaches the public surface.** `observed-with-evidence` — fetched from
`https://poesys.net/data/publish_provenance.json` at 2026-08-12 02:0xZ (HTTP 200):

```
"paused_reason": "scoped publish-path suite red at git=7d4d7fcad; blocking tests:
 FAILED tests/background/test_supervisor.py::test_harden_suppression_is_content_driven_not_only_filename, ..."
```

So the wrong list is not merely an internal diagnostic — it is published text on the
company's own site naming tests that the gate cannot run. (`paused_since` is now `null`,
so the string is vestigial rather than currently claimed, but it is still served.)

This is the same shape the file's own 2026-08-10 comment records for `filed_findings()`:
*"0/8, 0/8, 0/8, and this one's cause ... was not on the list either. The list was
near-identical every time while the cause differed every time, which is the tell."* The
cure replaced one wrong list with another wrong list.

## Proposed fix (not built this tick)

Under `-x` the blocker is provably the **last** `FAILED`/`ERROR` line in pytest's own short
summary, not every match in the stream. Two changes, both small:

1. Parse only within the `=== short test summary info ===` section, and take the trailing
   run of `FAILED`/`ERROR` lines — captured-output blocks are always above it.
2. **R15 mutation test:** feed the parser a real captured 01:24Z transcript with twelve
   nested `FAILED` lines plus one genuine summary line, and assert it returns exactly the
   one. Today's parser returns thirteen — so the test fails before the fix and passes after,
   which is the property R15 requires.

Cross-check available for free: a node ID that is not in the resolved 134-file scope cannot
be a blocker. Asserting that would have caught this without any parsing change.

## Related

- `feedback_a_control_false_positive_jams_pipeline` — a wrong payload sends every tick after it to the wrong place.
- `WORKER_FINDING_THE_NAMED_BLOCKING_TEST_PASSES_WHEN_YOU_RUN_IT_2026-08-10.md` — the same symptom filed two days earlier; this finding supplies its mechanism.
- `WORKER_FINDING_AN_OOM_KILL_IS_RECORDED_AS_A_TEST_REGRESSION_2026-08-10.md` — sibling: a resource failure recorded as a test regression. The ENOSPC above is `kind="test_regression"` in the state file for the same reason.
