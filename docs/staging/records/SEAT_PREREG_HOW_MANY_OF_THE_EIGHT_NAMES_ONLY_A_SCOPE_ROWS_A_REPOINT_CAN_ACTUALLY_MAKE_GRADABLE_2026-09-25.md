**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION — how many of the 8 `NAMES_ONLY_A_SCOPE` rows a repoint can actually make gradable, and how many were never that class's shape at all

Written BEFORE the repoint was applied and BEFORE the post-repoint census was run. Drawn on the
scheduled tick of 2026-09-25 as LANE 0 DELIVERY, claim
`repoint-the-eight-names-only-a-scope-rows-at-the-controls-inside-the-scopes-they-already-name`.

Predecessor, read first and not re-derived:
`docs/staging/SEAT_FINDING_FOURTEEN_OF_THE_SIXTEEN_ROWS_TOLD_THEIR_CONTROL_WAS_NEVER_WRITTEN_HAD_NO_ABSENT_PATH_AT_ALL_2026-09-25.md`
(`f0470836e`) — split `CONTROL_NEVER_WRITTEN` into `CONTROL_UNNAMED` and reached
`NAMES_ONLY_A_SCOPE` through a second branch, leaving the census at CONTROL_UNNAMED 10,
NAMES_ONLY_A_SCOPE 8, NOTHING_IN_THE_ROW 6, POINTER_ROT 2, HONESTLY_UNBUILT 2,
CONTROL_NEVER_WRITTEN 2 over 28 candidate rows.

## Premise, re-measured before the work

* `f0470836e` IS an ancestor of `origin/main` and IS this worktree's HEAD. The draw's premise note
  is correct and the premise is NOT spent in the sense that would release the claim: the item cites
  that commit as the census it is repairing the output of, not as work to land.
* The DUPLICATE-WORK note names this id itself as an already-held live claim. It is this draw's own
  write: `docs/observability/.seat_work_in_hand.json` holds exactly ONE entry, this id,
  `claimed_at: 1790336538.59`, 60 seconds old when read. One write, not two writers. Carrying on
  with the work, not the disposition.
* The PATH CHECK grades all 4 named paths `directory` — it has no opinion about a whole tree, which
  is the same fact this item is about.
* The 8 rows are re-measured live and are exactly the 8 the item names: `G4_unified_failure_register`,
  `SP2_2_rng_substream_primitive`, `W2_non_dd_miss_vocabulary`, `H40_full_suite_pollution_bisect`,
  `OPS6_scoped_publish_path_suite`, `W2_18_the_housing_joint_the_sample_and_the_ceiling`,
  `W2_19_who_lives_where_money_and_composition`,
  `H48_the_parked_document_audit_is_the_idle_hole_at_scale`. 28 candidates, unchanged.

## The claim in the item I do NOT believe, stated before I test it

The item's WHY says NAMES_ONLY_A_SCOPE *"is the only class whose repair can move graded off 1
WITHOUT writing new tests, because the controls demonstrably already exist inside the scopes these
rows name."*

**The word doing the work there is "demonstrably", and nothing demonstrated it.** What the census
established is `_is_a_control_scope(rel)` — *a* `test_*.py` exists somewhere beneath the directory.
That is not the same proposition as *this atom's* control exists beneath it, and for the widest
scopes the two come apart completely: `G4` names `tests`, `H40` names `tests/`. Every atom in the
repository would satisfy `_is_a_control_scope` on those, so the property is uninformative exactly
where the row is vaguest.

First counter-evidence, already in hand before the repoint: `site/knowledge/` (W2_18, W2_19) holds
7 controls, and their subjects are wholesale prices, review dates, the index, consolidated-page
rendering, four charts, and weather-cell maps. **Not one is about housing stock, a space-filling
sample, a technical ceiling, household composition, or small-area income.** The directory is a
control scope and contains no control for either row that names it.

## Predictions, before the measurement

1. **Fewer than 8 become gradable; my point prediction is 2.** The two I expect to carry a real
   per-atom control inside the directory they name are `OPS6_scoped_publish_path_suite`
   (`tests/background/` against `background/process_run_complete.py`) and
   `W2_non_dd_miss_vocabulary` (`tests/company/crm`, `tests/harness`).
2. **`W2_18` and `W2_19` do not become gradable by a repoint at all**, because no control for
   either subject is inside `site/knowledge/`. They are `CONTROL_UNNAMED` wearing
   `NAMES_ONLY_A_SCOPE`'s clothes, and the honest repair is to say so, not to point them at
   somebody else's test.
3. **The 4 rows flagged through the `if not files` branch (`G4`, `SP2_2`, `H40`, `H48`) cannot be
   repaired by naming controls alone, and naming only controls makes their verdict WORSE, not
   better.** `ungradable_causes` computes `subject_on_disk = [files not in controls]`; adding only
   `test_*.py` entries leaves that empty with nothing rotted, which returns `HONESTLY_UNBUILT` —
   "the atom is unbuilt and its zero is the true answer". A repoint that names a real, passing
   control and thereby produces the verdict *unbuilt* is a strictly worse reading than the one it
   replaced. Any repoint of those 4 must name a SUBJECT file too, or must not be made.
4. **Of any row that does become gradable, I expect at least one to return
   `CONTROL_PREDATES_ROW`** — H41's shape, named by the item itself.
5. **`graded` therefore ends at 1 or 2 of 28, not at 9.** I do not expect this item's stated goal
   ("move graded off 1") to be reachable by the repoint it prescribes for more than one row.

## What would refute each

* (1)/(5) are refuted by a post-repoint census reporting 3 or more graded rows.
* (2) is refuted by a `test_*.py` under `site/knowledge/` whose subject is W2_18's or W2_19's — I
  will name the file if one is found.
* (3) is refuted by a branch-1 row whose cause after a controls-only repoint is anything other than
  `HONESTLY_UNBUILT`. This one is a prediction about the INSTRUMENT, not about the world, and is
  therefore cheap and worth almost nothing on its own; it is here because acting on it silently
  would have been the defect.
* (4) is refuted by every newly-gradable row's controls postdating its row.

## Done means

Every one of the 8 rows either names its own control files, or carries a written reason in the
record why it cannot — and the post-repoint census's own numbers are reported beside these
predictions whichever way they fall, in this file's result note.
