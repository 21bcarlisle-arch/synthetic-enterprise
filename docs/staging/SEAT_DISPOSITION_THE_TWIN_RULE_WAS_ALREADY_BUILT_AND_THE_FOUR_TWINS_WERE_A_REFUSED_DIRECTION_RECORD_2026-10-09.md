**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The twin rule was already built, and the four "twins" were a refused direction record

*Seat executor, 2026-10-09, drawn item `clear-the-eighteen-paths-holding-the-shared-checkouts-fast-forward`.
Follows the 2026-10-09 section of `SEAT_FINDING_ONE_ITEM_LANDS_TWICE_AND_THE_SHARED_HEAD_FORKS_FROM_ORIGIN_2026-10-07.md`.*

## The premise is spent

The item asked for a reconciler rule that clears a working copy byte-identical to
`origin/main:<path>`, plus a control. Both were already on origin. `identical_tracked_twins` and
`identical_untracked_twins` are in `background/origin_reconcile.py`, deletion twins were added in
998814330, and the control is `tests/background/test_the_advance_refused_on_files_it_was_about_to_write_back_unchanged.py`.
The rule is all-or-nothing on purpose (its docstring says why). Twins are cleared only when every
other blocker clears too, so twins were never what held the advance.

## What the four recurring "twins" were at 03:45

Re-hashed against origin at 03:45 UTC, `DIRECTION.yaml`, `decisions.jsonl`, `SEAT_STRETCH_LOG.md`
and `delivery.json` were **not** twins. They held the 02:43 orientation's record. Its landing was
refused: `decisions.jsonl`'s last row reads `committed: false`, `landing_refused: GATE RED on the
resulting tree ...`. The refusal was cut at three lines and 300 characters and ends mid-word in
`[live-hook] core.hooksPath is NOT set here, s`. So nothing recorded which gate refused the
direction record. The record stayed off origin, and its four files held the shared fast-forward.

**Fixed here.** `delivery_seat.refusal_verdict` keeps the refusal's head line and the refusing
step's `❌` block. With no `❌` banner, it keeps the verdict lines (`FAILED`, the pytest count) and
drops the `✓` lines. This is the cut eaa94ed5f already made in the reconciler. Control:
`test_a_red_gates_refusal_names_the_refusing_step_and_not_the_boilerplate_above_it`. Restoring the
old cut reds it (run 2026-10-09). The 02:43 cause itself cannot be recovered. The next refused
orientation will name it.

## What still holds the advance (20 paths, 71 behind at 03:45)

- Three code and test copies from 09-24 and 10-05 (`background/delivery_lane.py`,
  `tests/background/test_supervisor.py`, the 09-24 headcount test). These are over 48h old, so
  `abandoned_copy_verdicts` will preserve them once nothing younger holds the advance.
- 10-08 and 10-09 docs and staging drafts. They are under 48h old, so by design they are live work
  until a lane lands them or they age out.
- **`docs/observability/test_execution_log.jsonl`, the new structural blocker.** Every test run in
  the shared tree appends to it, so it is always under 48h old and never a twin. Origin had not
  touched it since July, until d29dcddc3 (10-08 17:21) swept one line into a feature commit. Since
  then, the fast-forward overwrites it, and the all-or-nothing rule holds the whole advance on it
  for good. This copy cannot age out, so even when everything else clears, this one path keeps the
  daemons on old code. `tools/generate_evidence_data.py` and `tools/generate_phases_json.py` read
  it, so it is an input as well as exhaust, and which class it belongs to is a design call. That
  call is handed on as the next item, not taken here.

Nothing on the shared checkout was touched by this turn.
