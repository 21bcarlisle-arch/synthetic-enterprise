# [WORKER-FINDING] The wedge episode memory was WIPED mid-episode, and the next alarm narrated a fresh hour (2026-08-09)

**Severity:** LATENT · **Lane:** H_harness

**Found during:** Draw 1 of `DIRECTOR_PRIORITY_UNWEDGE_AND_ALARM_TEETH_2026-08-08` (unwedge publish).
**Disposition:** QUEUED as a finding, not fixed on sight (SELF_INTERRUPT_DISCIPLINE — publishing is
unwedged, the machine is not blocked, and the supply of harness findings is infinite).

This matters because it is the exact disease Draw 2(a) was built to cure. The cure — `wedge_since`,
`episode_failures`, `cited_findings`, `markers_pending` — **is built and is live**
(`process_run_complete.py:1866-1945`, `supervisor.py:2895-2925`). The finding is that something
still **resets** it, so a built episode memory can be zeroed while the episode is still running.

## Observed, with evidence

`docs/observability/.publish_gate_state.json` at 04:53 UTC, mid-episode:

```json
{"alerted_at": 1786248879.6, "wedge_since": 1786248202.8, "failures": [ ...10 entries... ]}
```

`wedge_since` = 2026-08-09T04:03:22 UTC, ten consecutive `test_regression` failures across five
git hashes (`745361231`, `cccf6b418`, `b4e1dfb19`, `4e13770a8`, `a48accaa7`) — a ~50-minute episode.

At 04:54 UTC, `docs/observability/sim-runner-log.md` records these two lines **consecutively**:

```
- [2026-08-09 04:54 UTC] [process_run] Another process_run_complete instance is already running -- skipping run_complete_20260809T004355Z.md
- [2026-08-09 04:54 UTC] [process_run] Publish gate recovered -- cleared wedge state, re-armed alarm.
```

The state file immediately after:

```json
{"alerted_at": null, "cited_findings": [], "episode_failures": 0, "failures": [], "wedge_since": null}
```

At 04:55 UTC the next failure was recorded, producing a **fresh** wedge:

```json
{"failures": [{"git_hash": "a48accaa7", "rc": 1, "ts": 1786251304.3}], "wedge_since": 1786251304.3}
```

So a 50-minute, 10-failure, 5-hash episode became a 1-failure episode zero minutes old, while the
underlying cause (the red ruff ratchet) was still red and 23 markers were still unpublished. Any
alarm firing after 04:55 would have described a fresh minute — the precise failure the director's
census named ("every alarm truthfully described a 60-minute window and forgot the episode"), now
occurring *after* the episode-memory fields exist.

## Not asserted (R9)

**Which call site cleared it.** I could not establish this from the available evidence and did not
bisect it — that is the work, not the finding. What was ruled out by reading:

* `main()` returns `EXIT_LOCK_SKIPPED` (75) on a lock-skip and does not itself record an outcome
  (`process_run_complete.py:2054-2062`).
* `record_publish_gate_outcome` returns `"skipped"` for rc 75 and clears nothing
  (`process_run_complete.py:1981-1983`) — the fail-open closed on 2026-07-29 has NOT regressed.
* `record_publish_gate_success` has exactly one non-test caller, the rc==0 branch of that router
  (`process_run_complete.py:1984`), and `test_sim_runner_publish_gate_outcome.py:180` still asserts
  no publisher calls it directly.

Two candidates remain and are indistinguishable from the log alone: (1) a genuine rc==0 publish by
another process in that window whose marker archived elsewhere, or (2) a path that reaches the
rc==0 branch without having published. **The adjacency of the two log lines is suggestive and is
NOT evidence** — the log is written by several processes and interleaves.

Note also that `record_publish_gate_success`'s own docstring says it clears on "a clean publish
**(or a clean skip)**" — that parenthetical contradicts the router's documented three-outcome
contract directly above it. Whichever candidate is true, that sentence should not survive.

## What closing it looks like

1. Establish the call site: log the caller + rc inside `record_publish_gate_success`, or assert on
   the archive side (a real rc==0 publish must leave an archived marker in `done/`/exhaust with a
   matching timestamp — at 04:54 UTC none was found).
2. If it is candidate (2): close it as a CLASS per R10 — the invariant is *episode memory may only
   be cleared by an outcome that demonstrably published a marker*, not by any path that reaches the
   success branch.
3. R15: mutation-test the guard. The named defect it must fire on is exactly this one — clear the
   state while `markers_pending > 0` and the cause is still red. A control that cannot distinguish
   "recovered" from "nobody published" is the fail-open shape, and the current test suite passes
   with the wipe having happened, so today it cannot fail on it.
4. Reconcile the `record_publish_gate_success` docstring with the router's three-outcome contract.

## Related

* `DIRECTOR_PRIORITY_UNWEDGE_AND_ALARM_TEETH_2026-08-08.md` — Draw 2(a) is what this defends.
* `WORKER_FINDING_SECOND_WEDGE_CAUSE_LANDED_AFTER_THE_FIRST_2026-08-09.md` — same episode, adjacent class.

— Worker finding, 2026-08-09, during the unwedge draw.
