**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`
**Discharged:** `tests/tools/test_level_zero_contradicted_by_its_own_controls.py::test_a_row_that_names_NO_control_is_not_told_the_control_was_NEVER_WRITTEN`,
`tests/tools/test_level_zero_contradicted_by_its_own_controls.py::test_a_control_scope_is_measured_and_not_matched_on_a_tests_prefix`,
`tests/tools/test_level_zero_contradicted_by_its_own_controls.py::test_all_seven_causes_are_reachable_in_one_pass`,
`tools/level_zero_contradicted_by_its_own_controls.py` — the class is split, four mutations were
run against the three legs before landing and all four fire (recorded below), and the live
distribution is re-measured in
`docs/staging/records/SEAT_RESULT_THE_DOMINANT_UNGRADABLE_CAUSE_WAS_ITSELF_A_MIXED_CLASS_AND_THE_DEBT_IS_26_OF_28_2026-09-25.md`.

# The dominant ungradable cause was itself a mixed class: 14 of the 16 rows told "the control was never written" had no absent path at all, and nothing was measured about any of them

Answers `docs/staging/records/SEAT_PREREG_WHICH_CAUSE_DOMINATES_THE_UNGRADABLE_LEVEL_ZERO_ROWS_2026-09-25.md`.
Nine predictions: **four confirmed, five refuted**, all scored beside the predictions in the result
note rather than instead of them. Drawn on the scheduled tick of 2026-09-25 as LANE 0 DELIVERY,
claim `count-which-of-the-three-ungradable-causes-dominates-the-remaining-27-level-zero-rows`.

## The defect, in one paragraph

`ungradable_causes` publishes `CONTROL_NEVER_WRITTEN` as *"the subject is on disk and the control
that would grade it was never written"*, and the table in
`docs/staging/done/WORKER_RESULT_THE_THIRTY_ONE_UNGRADABLE_ROWS_ARE_FIVE_CAUSES_AND_ONLY_THREE_OF_THEM_OWE_NO_REPAIR_2026-09-16.md`
gives its decision rule as *"path absent AND unknown to git, subject on disk"*. Measured against the
live map at `208195dd4`: **16 of the 28 candidate rows carried it, and 2 of those 16 had an absent
path.** The other **14** reached it through the `elif not controls:` leg, where nothing is absent
and **nothing was measured about whether a control exists** — the row simply does not name one. They
were handed the repair *"write the named control and prove it can fail"*, naming a control that does
not exist in the row.

## Why that is BLOCKING and not a naming quibble

Three separate costs, and the third is the one that hides work:

1. **The instruction is unfollowable.** 14 readers are sent to write "the named control" and there
   is no name. A row's `paths` even carried the literal string `"(file_scope names no test_*.py)"`
   — a path-shaped token in a `paths` field, printed under a `CAUSE:` heading beside real paths.
2. **The claim may be FALSE in the direction that hides landed work.** This module's own docstring
   records `PB4` and `PB6` as rows whose build **did** write a control, under a name the row does
   not cite — the very instances the check was built for. "Never written" over a row that names no
   control picks one of two worlds without looking at either.
3. **It is the exact shape the split was built to end, one level down.** The 2026-09-16 ruling's
   own words: *"Three rows sharing one reason had three different causes and three different
   repairs. Counting those as one number is why the count did not move for twelve briefs."* The
   remedy then was to split by cause. The dominant cause was then itself a mixed class, and
   `background/delivery_seat._by_cause` — the only consumer — faithfully published the mixture as
   one heading with 16 rows under it.

A fourth, smaller: `NAMES_ONLY_A_SCOPE` was reachable only through `if not files:` — **every**
entry a directory. That gate is keyed to the rest of the row rather than to the property it
describes, so a row naming subject FILES **and** a test directory fell through it.
`W2_non_dd_miss_vocabulary` names `tests/company/crm` and `tests/harness`;
`OPS6_scoped_publish_path_suite` names `tests/background/`. Both were told to write a control that
is almost certainly already inside one of the directories they name.

## The claim was false on the first row I checked, which is why this is not a naming quibble

`OPS7_provenance_stamps_on_live_pages` names `tools/generate_dashboard_data.py`, `site/index.html`
and `site/data/`, no control, and was told its control "was never written". `tests/tools/` holds
`test_published_provenance_is_real.py`, `test_the_published_provenance_names_the_run_not_the_
generator.py`, `test_a_generators_stamp_describes_the_bytes_it_read.py`,
`test_a_stamped_page_at_the_pages_root_has_a_live_writer.py` and
`test_the_run_stamp_names_the_code_that_ran_not_head_at_the_end.py`. Whether any of those is THIS
atom's exit control is a judgement for the row's owner and not for this instrument — which is
precisely the point. The instrument was asserting one of the two answers, and on the first row
taken at random it asserted the one the tree contradicts. `CONTROL_UNNAMED` says "cannot tell, go
and look", and that is the true statement.

## The repair, and why it is not a map edit

A seventh cause, `CONTROL_UNNAMED`: *"the row names no control at all, so whether one was ever
written is not a question this row can answer"*. Its repair says to ask
`git log --all --oneline -- <subject>` **before** writing anything, names the PB4/PB6 shape as the
reason, and says out loud that nothing here is a verdict about the work yet. Its `paths` are the
subject files on disk — the paths that repair actually opens — so the placeholder token is gone.

`NAMES_ONLY_A_SCOPE` gained its second door and a re-keyed definition: *"the row's control evidence
is a DIRECTORY and not a file"*. A directory is a control scope when the **tree** says controls live
in it — a `test_*.py` beneath it, short-circuited on the first hit — and **not** when its path starts
with `tests`. That is not fastidiousness: `W2_18` and `W2_19` point their evidence at
`site/knowledge/`, which holds seven controls and no `tests` in its path, so a prefix literal would
have missed both. It is the "key to the property, not to today's answer" rule with a measured
instance.

`CONTROL_NEVER_WRITTEN` now holds only what it claims: a row that **names** a control git has never
heard of. Two rows — `PB5_pounds_or_percent_resolved` and `A51_the_plain_english_report...`.

**No map bytes were spent.** The repair is in the classifier, so the ratchet is untouched and
nothing had to be drained to pay for it. (That refutes P9, which predicted a map edit.)

## Mutation evidence, run before landing — four mutations, four fire

| mutation | fires |
|---|---|
| `elif not controls` appends `CONTROL_NEVER_WRITTEN` again (collapse the carve-out) | 3 red, incl. the leg written for it |
| `_is_a_control_scope` → `return here.is_dir()` (every directory is a scope) | 1 red, on its own negative leg |
| `_is_a_control_scope` → `rel.startswith("tests")` (the prefix literal) | 2 red |
| the `scopes` branch always empty (the second door unreachable) | 1 red, on the partition control |

Each fires on the leg written for it, not on a neighbour — the flattering reading was checked for.
The partition control is `test_all_seven_causes_are_reachable_in_one_pass`: **eight** worlds over
seven causes, because `NAMES_ONLY_A_SCOPE` now has two doors and one world would leave the second
unreachable while the control stayed green. The assertion is on the whole mapping, not on
per-cause reachability, because `NO_CONTROL` and `UNNAMED_CONTROL` differ by one property and a
two-shapes-one-state collapse is exactly what carried this defect.

## What this does NOT establish

The census still grades 1 of 28. Re-cutting the causes moves no row into `graded` and was never
going to: it changes what 14 rows are TOLD, not whether their controls can be run. The debt is
**26 of 28** rows owing a repair — `HONESTLY_UNBUILT` is the only cause owing none and it holds 2.
The item's hope that *"the real debt may be far smaller than 27"* is **refuted**, and that is the
reading for the next lane.

## A correction to the item's own premise, recorded because the item is an instruction others read

The item says *"nothing has COUNTED the distribution"*. That is false, and it was checkable before
the work: the distribution was counted on **2026-09-16** (the five-cause table in
`docs/staging/done/WORKER_RESULT_THE_THIRTY_ONE_UNGRADABLE_ROWS_ARE_FIVE_CAUSES...`, over 31 rows)
and again on **2026-09-25**, in a sibling prereg
(`docs/staging/records/SEAT_PREREG_HOW_FAR_THE_28_UNGRADABLE_LEVEL_ROWS_CAN_BE_DISCHARGED_2026-09-25.md`)
which names *"the 13 rows carrying `CONTROL_NEVER_WRITTEN`"* and *"the four `NAMES_ONLY_A_SCOPE`
rows (G4, SP2_2, H40, H48)"*. The count had been taken twice and the headline was believed twice.
What had never been done is the **sub-split of the dominant class**, which is where the defect was.

The item also asserts that two causes owe no repair (`HONESTLY_UNBUILT` **and**
`NAMES_ONLY_A_SCOPE`). `CAUSES_OWING_NO_REPAIR` in the module that defines the vocabulary holds
only `HONESTLY_UNBUILT`, and `CAUSE_REPAIR[NAMES_ONLY_A_SCOPE]` is a real instruction. The module
is right; the item was wrong, and had that framing been taken on trust the six scope rows would
have been written off as not-a-defect.
