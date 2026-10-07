**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Direction item:** `the-seats-direction-record-reaches-origin-or-says-it-did-not` · **Claim:** released on landing

# The direction record retries until the unit's budget runs out, and a refusal is recorded and paged

**Duplicate-work note.** The draw said the "other live claim" was this same id, already in
`.seat_work_in_hand.json`. That is this draw's own claim, not a rival, so there was no disposition to
take and I did the work.

## What was wrong (read at HEAD `31a8356aa`)

`land_direction_on_origin` already re-based on each attempt: it re-cuts the worktree at the new
origin and writes the same bytes. What was wrong was the stopping rule and what happened after it:

1. **Two attempts, then give up.** On 10-07 origin moved twice in 50 minutes, so both attempts lost.
2. **A failure left no trace.** `orient()` appends its row as `oriented` before the landing, because
   that row is part of what lands. When the landing was refused, the row still read `oriented` and
   nobody was paged. Origin's record was three hours stale and nothing said so.
3. **A bound that never fit.** `delivery-seat.service` kills the whole run at `TimeoutStartSec=4500`.
   That covers the session (up to 1800s) and every gate run (15-25 min each). Any retry bound that
   ignores the unit risks a landing killed mid-gate, which writes no refusal and sends no page.

## What changed

- The loop runs **until a deadline, not a count**. The deadline is `TimeoutStartSec`, read from the
  unit file (fallback 4500, named), minus what this process has already spent, minus one 1500s gate
  run. A new attempt starts only while a full gate still fits inside the unit.
- **Re-base guard.** A re-base is allowed only while origin's `DIRECTION.yaml` is byte-identical to
  the copy the first attempt saw. If it changed, another writer edited the seat's file. That is
  refused by name rather than overwritten. The append-only check now runs against every origin the
  loop sees, not just the first.
- **On failure:** `record_landing_refused` appends a copy of the row with `outcome: refused` and
  `landing_refused: <reason>`, keeping the orientation's `at`. The file is append-only, so this is a
  new row, not an edit. It also pages `blocked_work` on NTFY.

## Controls (all mutations fire, one equivalence found)

`test_origin_moving_TWICE_under_the_gate_still_lands_...` covers three cases: two moves then a
landing, a refusal after the deadline, and a refusal when another writer edited the record.
`test_a_refused_landing_is_RECORDED_as_refused_and_PAGED`,
`test_a_record_that_did_not_reach_origin_ends_the_orientation_REFUSED_and_PAGED` (through `orient()`),
and `test_the_deadline_is_the_units_budget_less_one_gate_run`.

These mutations each turn a test red: the two-attempt give-up, dropping the deadline, dropping the
base guard, dropping the refused row, dropping the page, dropping the wiring in `orient()`, and
pinning the budget as a literal. Widening `_previous_concern_ids` to also read refused rows turned
out to be an **equivalence**. The refused row copies the oriented row directly before it, so the
same ids are found either way. I reverted that edit.

## What remains

- An attempt that starts just inside the deadline and then runs longer than 1500s is still killed by
  the cgroup with no refusal written. 1500s is the top of the measured gate range, not a guarantee.
- DONE also requires the next orientation's record to land on origin under its own commit. That can
  only be seen at the next `delivery-seat.timer` firing after this change is promoted.
