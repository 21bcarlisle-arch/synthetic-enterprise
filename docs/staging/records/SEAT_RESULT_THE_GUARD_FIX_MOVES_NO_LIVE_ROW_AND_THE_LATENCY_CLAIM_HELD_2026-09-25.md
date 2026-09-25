**Severity:** INFO · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Result: the `HONESTLY_UNBUILT` narrowing and the eighth cause move ZERO live rows — both halves of the prediction held

Answers `docs/staging/records/SEAT_PREREG_WHETHER_NARROWING_HONESTLY_UNBUILT_AND_CLOSING_THE_SUBJECT_HOLE_MOVES_ANY_LIVE_ROW_2026-09-25.md`,
which was written before the run.

## The measurement

`HEAD`'s `ungradable_causes` and the working copy's, loaded as two modules in ONE process, over
the same 28 candidate rows of `docs/design/maturity_map.yaml`, sharing one `git log --all` answer
cache so the only variable is the module.

| cause | HEAD | after |
|---|---|---|
| `NOTHING_IN_THE_ROW` | 10 | 10 |
| `CONTROL_UNNAMED` | 10 | 10 |
| `NAMES_ONLY_A_SCOPE` | 4 | 4 |
| `HONESTLY_UNBUILT` | 2 | 2 |
| `CONTROL_NEVER_WRITTEN` | 2 | 2 |
| `SUBJECT_NEVER_WRITTEN` (new) | — | 0 |

**Rows whose cause list changed: 0.**

## Against the prediction

* **Half one — the narrowing moves nothing.** Predicted 0, measured 0. The finding's latency
  claim held: the two live `HONESTLY_UNBUILT` rows (`G14`, `G15`) each name a file that is
  genuinely absent, so the narrowed guard reaches them exactly as the old one did.
* **Half two — `SUBJECT_NEVER_WRITTEN`, predicted 0–3 and a bet I had not measured.** Measured 0,
  at the bottom of the band. No live row names a subject that is absent AND unknown to git
  alongside a file that is on disk. The branch is correct and, today, unreached.
* **The refuting direction did not appear**: no row moved INTO `HONESTLY_UNBUILT` and no row lost
  a cause without gaining one.

## What a zero does and does not license

It does NOT say the eighth cause is unnecessary. `NOTHING_IN_THE_ROW` asserts *"every named path
is on disk"* on its own surface, and before this change that sentence was reachable while false.
A partition whose only defence against a false claim is that nobody has written the row that
triggers it is the same shape as the defect being repaired — the route in was the census's own
printed repair, followed by a later turn taking it at its word.

It DOES mean the repoint of the four `NAMES_ONLY_A_SCOPE` rows that name no module can now
proceed without manufacturing a silence, which is the whole reason the guard was fixed first.

## Controls, and the mutations that prove they can fail

`tests/tools/test_level_zero_contradicted_by_its_own_controls.py`, 49 passed.

| mutation | reds |
|---|---|
| guard reverted to `if not subject_on_disk and not (rotted or unknown)` | `test_a_row_whose_ONLY_named_file_is_a_control_ON_DISK_is_not_read_as_HONESTLY_UNBUILT` — and ONLY that leg, so the leg written for the defect is the leg that catches it |
| `never_subjects` branch deleted | `test_NOTHING_IN_THE_ROW_is_never_claimed_while_a_named_path_is_ABSENT` + the partition control |
| `HONESTLY_UNBUILT` branch made unreachable | the positive arm of the first test + the partition control |

The third mutation is why both new tests carry a positive arm. A control asserting only that a
cause does not fire is passed by deleting the branch, and "the guard refuses everything" is the
shape this repository has entered three times.

The partition control was renamed `test_all_seven_causes_are_reachable_in_one_pass` →
`test_every_cause_is_reachable_in_one_pass` and now asserts `set(CAUSE_REPAIR)` equals the set of
causes its worlds reach. The count in the old name was a bound written as a literal: it went stale
on the commit that made the partition better. The new assertion reds when a ninth cause is
declared with no world reaching it, or a world reaches a cause with no declared repair.
