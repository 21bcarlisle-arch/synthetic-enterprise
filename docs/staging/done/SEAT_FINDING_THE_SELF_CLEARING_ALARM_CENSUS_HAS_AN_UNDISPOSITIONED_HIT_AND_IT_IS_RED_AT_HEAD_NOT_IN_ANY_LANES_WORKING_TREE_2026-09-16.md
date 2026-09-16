**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Class:** controls_that_cannot_fail · **Atom:** (none — found in passing)

# `test_every_live_hit_is_dispositioned` is RED at HEAD on `.launch_records.json`, and it is nobody's working-tree pollution

**Filed 2026-09-16, delivery seat**, found while sweeping the publish-gate test population after
landing `8dfb28f9f`. Not mine, and recorded rather than routed around.

**Discharged:** 2026-09-16 by the delivery seat, commit 76e74f854 (promoted to origin/main). The
row is written and `python3 -m background.self_clearing_alarm_census --check` is rc=0 with all 31
tests in `tests/background/test_self_clearing_alarm_census.py` green. Severity drops BLOCKING →
RECORDED because the red is gone, not because the judgement was easier than this document said it
would be: the verdict is `benign`, and the reason is a READER fact — `launched_at` IS an
episode-start timestamp that `record()` resets, but no alarm reads it for severity. The
`_scope_of_benign` half was answered separately and is the destructive one: `load()` cannot tell
ABSENT from PRESENT-BUT-UNREADABLE, and `record()` destroys every other job's record on a corrupt
read while `check()` does not. **What this document warned about was real and is NOT closed by the
row.** `record()` deletes an unsettled `live` claim on relaunch, so a `[LAUNCH DIED]` page can be
suppressed; that is filed as
`docs/staging/SEAT_FINDING_A_RELAUNCH_DELETES_THE_UNSETTLED_LIVE_RECORD_OF_THE_DEATH_IT_IS_RELAUNCHING_AFTER_2026-09-16.md`
(LATENT), with the reason it is not graded `real` — the append-or-monotonic remedy is vacuous on a
timestamp every legitimate relaunch moves forward.

## The red, verbatim

```
FAILED tests/background/test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned
E  AssertionError: undispositioned self-clearing-alarm hits: .launch_records.json.
   Disposition each as `real` (and guard the episode field) or `benign` WITH a reason.
E  assert not ['.launch_records.json']
```

## It is at HEAD, proven in a clean extract and not inferred

This repo's recurring trap is a red that is really another lane's uncommitted working-tree state,
and the opposite trap is calling a real red pollution. So it was measured rather than argued:

```
git archive ad3a9acb9 | tar -x -C ~/.cache/lcp_extract_parent     # the PARENT of my commit
cd ~/.cache/lcp_extract_parent && pytest tests/background/test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned
-> 1 failed in 2.28s, identical message
```

`ad3a9acb9` contains none of this turn's work, and an extract contains no working-tree state from
any lane. **The red is in the committed tree.** It also reproduces in the live worktree
(1 failed, 806 passed across the 37-file publish-gate population), so it is not an artefact of the
extract either.

Attribution of the subject, not of the defect: `.launch_records.json` was last written by
`8a8e99ea1` ("the register repair landed in the one tree the pair move is forbidden to use…").
This finding does not claim that commit caused the red — only that the census's live-hit set now
contains a key `docs/design/self_clearing_alarm_dispositions.json` has no row for.

## Why it is BLOCKING and what it is NOT

The census's own contract (`background/self_clearing_alarm_census.py`, line 35 onward) is that
`--check` exits 1 on **any** undispositioned hit, precisely so that a newly-written self-clearing
store cannot appear without someone answering for it. So this is the control working. What is
wrong is that the answer was never written, and a standing red is how a control stops being read.

**It is not a one-line append.** A `benign` verdict answers exactly ONE question — *can a write to
this store SHORTEN an episode* — and the module is emphatic (lines 952-966) that `benign` says
nothing about whether a read-modify-write store destroys its own history. Guessing the verdict to
clear the red is the failure mode this register exists to prevent. It needs `.launch_records.json`'s
writer read, and that is a piece of work, not a chore.

## The remedy, and it is deliberately not done here

Read the writer of `docs/observability/.launch_records.json`, decide `real` vs `benign` against
`_scope_of_benign`, and write the row with its reason — plus the episode-field guard if `real`.
Not done in this turn because this turn's claim was the publish-gate timestamp, the two are
unrelated, and a mistake in a verdict I guessed would ride into the same commit as a change that is
mutation-proven. Handed off rather than bundled.

## THIS DOCUMENT IS IN `done/` BY THE CONSOLIDATION RULE, NOT BECAUSE IT IS DISCHARGED

`background.finding_classes --check` refuses any live finding that belongs to a consolidated class
and is not listed in its register, and the register in turn requires its members to be in the
archive. So filing this at all moves it to `done/`. **The `done/` move normally IS the discharge in
this repo, and here it is not** — it is where the register keeps its members while the register
carries the debt. The open remedy above is live and is recorded under
`docs/staging/reference/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md`, in that document's
`## What is owed` section, which is rendered from the BLOCKING members and is what gets drawn.
Anyone reading this file in the archive should read that section, not the directory it is in.
