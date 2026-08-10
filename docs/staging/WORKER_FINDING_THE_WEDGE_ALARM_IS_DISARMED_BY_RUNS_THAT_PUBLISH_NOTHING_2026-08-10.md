# [WORKER-FINDING] The publish-wedge alarm is disarmed by rc=0 from paths that never ran the gate (2026-08-10)

**Found during:** the fifth publish-wedge unwedge (the H36/H38/H39 note-store mismatch).
**Disposition:** QUEUED. Not fixed on sight — the wedge itself was the P0 and is closed; this is the
*measurement* of wedges, and it is the third time the same class has been closed at one instance.

## Observed, with evidence

At **00:59 UTC** `sim-runner-log.md` records:

```
- [2026-08-10 00:59 UTC] [process_run] Publish gate recovered -- cleared wedge state, re-armed alarm.
```

**HEAD was provably RED at that moment.** `observed-with-evidence`:

* HEAD was `192e29792` from 01:30 BST (00:30Z) until my unwedge commit at **01:02:16Z**.
* The 00:44Z gate run on that exact SHA **failed** —
  `FAILED tests/design/test_atom_notes_store.py::test_declarations_match_the_store`, logged 00:53Z.
* That test is deterministic (it reads the map and the store out of the gate's own HEAD checkout).
  Nothing in HEAD changed between 00:53Z and 01:02Z.
* The fix that makes it pass — the four missing note files — was written to the working tree at
  **01:00:55Z**, *after* the "recovered" line, and committed at 01:02Z.

So no completed gate run on `192e29792` could have been green, and the timing rules one out anyway:
a full gate takes ~8.5 min (the 00:44Z run measured 514s) and only ~2 min elapsed.

## The mechanism

`_record_publish_gate_outcome` (`process_run_complete.py:~2431`) routes on the **exit code alone**:

```python
if rc == EXIT_LOCK_SKIPPED:
    return "skipped"
if rc == 0:
    record_publish_gate_success()      # <-- clears failures + alerted_at
```

`rc == 0` is treated as "a clean publish". But `_process()` has **two early `return 0` paths that
never reach the gate**:

1. **Already-archived duplicate** (`process_run_complete.py:~2523`) — marker already in `done/` or
   the exhaust tree → `log("Already archived ... (duplicate run)")` → `return 0`.
2. **Change-detection SKIP** (`~2583`) — fingerprint identical to the last processed run → the log
   line says it in as many words, *"no regen/test/commit"* → `return 0`.

Neither published anything. Neither ran a test. Both disarm the wedge alarm.

Path 1 is observed firing repeatedly during yesterday's wedge (16:16, 16:25, 16:26, 16:29, 17:04,
19:17, 19:36, 21:50 UTC — all on the same stale marker `run_complete_20260808T235122Z.md`).
`inferred`, not observed: which of the two fired at 00:59Z specifically — the log line for that
cycle is terse and several instances interleave. The defect does not depend on which.

## Why this is R10, not an instance

This exact class was already closed **once**, and the code says so at `main()`'s own docstring:

> *"It used to return 0, so no caller could tell a skip from a real publish — and
> `background_worker`'s sweep therefore fed rc==0 into `record_publish_gate_success()`, wiping the
> H15 wedge streak for a marker it had never published (fail-open: the detector disarmed by its own
> input)."*

That fix invented `EXIT_LOCK_SKIPPED = 75` for **one** of the non-publishing exits and left the
other two returning 0. R10 forbids closing an absurdity class one instance at a time: the population
is "every path that exits `_process()` without publishing", and it is open-ended — the next such
path will silently join it.

It is also the same shape as PW2 (2026-08-09), which fixed `record_publish_gate_success` so a
no-op could not zero `wedge_since`. PW2 repaired what the success *does*; it did not repair *who is
allowed to call it*. The episode counter survived last night (`episode_failures: 65` is intact,
which is PW2 working) while `failures`/`alerted_at` were cleared repeatedly — so the alarm kept
re-arming from zero against a wedge that never lifted.

**Consequence, measured:** the rung-1 draw needs ≥3 in-window failures. Every disarm resets that
count, so a 10.5-hour outage repeatedly presented as a fresh one — the same sentence an earlier
finding already had to write ("why a ten-hour outage alarmed as a fresh hour").

## What closing it looks like

1. Give the non-publishing exits their own codes the way the lock-skip got one — or better, invert
   the contract so `record_publish_gate_success()` is reachable **only** from the branch that
   actually ran the gate and got a green, rather than inferred from an exit code at the caller.
   *Success should be an assertion by the gate, not a deduction from rc.*
2. **R15, the mutation it must fire on:** feed the router an rc=0 produced by the change-detection
   SKIP path and assert the wedge state is **unchanged**. Today it clears, so the control cannot
   fail on its own named defect.
3. Cross-check `background/self_clearing_alarm_census.py` — it already names
   `record_publish_gate_failure`/`record_publish_gate_success` as an instance of the self-clearing
   class. This is a second, live instance of exactly what that census exists to enumerate.

## Related

* `WORKER_FINDING_THE_PRE_COMMIT_GATE_MAPS_NO_TESTS_TO_A_DATA_FILE_2026-08-09.md` — the blind spot
  that let this wedge reach HEAD in the first place (a `maturity_map.yaml`-only change selects zero
  tests). Now implicated in its **second** wedge.
* `WORKER_FINDING_DERIVED_ARTEFACT_STALENESS_IS_A_WEDGE_CLASS_2026-08-09.md` — the second red at
  HEAD in this same unwedge.

— Worker finding, 2026-08-10, during the fifth publish-wedge episode.
