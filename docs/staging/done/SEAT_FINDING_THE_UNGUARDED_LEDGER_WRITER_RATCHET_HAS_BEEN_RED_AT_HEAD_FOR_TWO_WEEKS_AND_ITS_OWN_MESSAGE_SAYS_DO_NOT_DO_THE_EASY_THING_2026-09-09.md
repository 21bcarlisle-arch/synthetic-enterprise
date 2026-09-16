**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `contain-the-site-pipeline-so-a-test-cannot-publish-a-degraded-feed-set`) · **Class:** controls_that_cannot_fail

**Discharged:** 2026-09-10. `tests/background/test_live_ledger_guard.py::test_the_narrowing_to_measurement_ledgers_is_measured_not_assumed` is green at HEAD again, and its bound went DOWN — 74 → 56, not up to 86. Thirty writers across seventeen modules now route through the guard in `background/live_ledger_guard.py`; the census reads 86 → 56 in a clean HEAD extract, delta 30, the newly-guarded set a strict subset of the HEAD set. `background/process_run_complete.py` alone contributed eight of them, and the site-publish twin came home from its one-commit exile — `tests/background/test_the_site_publish_pipeline_is_contained.py::test_the_publish_pipeline_actually_calls_the_guard_first` grades it beside the ledger guard. **Item 3 — why nothing selected this test for two weeks — is NOT discharged by this** and remains open as its own defect.

# FINDING — the unguarded-ledger-writer ratchet has been red at HEAD for two weeks, and its own message says not to do the easy thing

Found on the way to the site-pipeline containment work: `tests/background/test_live_ledger_guard.py
::test_the_narrowing_to_measurement_ledgers_is_measured_not_assumed` is **red at HEAD**.

```
AssertionError: the un-guarded observability-writer population GREW to 86 ... assert 86 <= 74
```

## It is not the current lane's

Proved rather than assumed, because a red that refuses a landing is very often pre-existing. The
census was run over `background/` extracted clean at HEAD (`git archive HEAD background`) and over
the working tree, with the same predicate functions:

```
HEAD      86
WORKTREE  86
```

**Identical.** This turn's changes (an import and a guard call in `process_run_complete.py`, a new
function in `live_ledger_guard.py`) are neutral to this census — neither adds an unguarded
observability writer.

## How long

The bound was last set to `74` in `18e8d215e` (**2026-08-26**). It is now 86. **Twelve unguarded
observability writers have landed in the fourteen days since and nothing went red anywhere a lane
could see it.** The repository has been committing normally throughout — five commits on
2026-09-09 alone — so whatever test selection the publish gate runs is not selecting this file.
That is the part worth keeping: *the ratchet did not wedge anything, which is why nobody noticed it
had stopped ratcheting.*

It is present in `docs/observability/head_red_observed.json` and **absent from
`head_red_baseline.json`** — so it is an observed red that was never accepted into the baseline
either. It is unregistered in both directions.

> **CORRECTED 2026-09-10, beside the claim.** Two errors here. (1) The "present in
> `head_red_observed.json`" reading came from the **shared working tree**; at HEAD — the tree this
> finding correctly graded its redness in — that file holds only the 2026-09-02 `OSError` wreck and
> does **not** contain this test id. (2) This finding's own framing above, *"nothing anywhere can
> currently see it"*, is false. The nightly unscoped census named this test id red on seven of
> seven journalled nights and recorded it with age (`runs_red: 9`, `first_seen: 2026-09-02`); the
> supervisor doorbell named the resulting register **3,421** times. The red was surfaced
> continuously and read by nobody — a presentation defect, not a blindness one. Measurement:
> `SEAT_FINDING_THE_FOURTEEN_DAY_RED_WAS_SURFACED_3421_TIMES_AND_THE_REGISTER_EVERY_CLEAN_WORKTREE_READS_IS_THE_830_ROW_WRECK_2026-09-10.md`.
> Everything this finding says about the ratchet itself, and its refusal to raise the bound, stands.

## Why this is BLOCKING and not RECORDED

The guard this ratchet watches is the one that stops a test process overwriting a published
measurement. Its incident of record is a 276-invoice fixture book replacing a 1600-invoice
population and republishing the public Proof door's payment gap **2.68x too low**. A ratchet over
that population which has been silently 12 writers behind for two weeks is not a bookkeeping
discrepancy — it is the control that was supposed to notice the class growing, not noticing.

## The trap, which is why this is a finding and not a fix

The test's own failure message says:

> *"widen `live_ledger_guard` rather than this bound, which is now a move that actually lowers this
> number"*

**Raising `74` to `86` is the wrong move and the message names it in advance.** It banks the drift
and re-arms the ratchet at a number nobody chose on purpose, and the next reader inherits a bound
with no argument behind it. The right move is to work the 86 down by guarding the writers — the
list is in the failure output, fully enumerated, and `process_run_complete.py` alone contributes 14
of them.

Deliberately **not** done in this turn: it is a separate subject from the site-pipeline
containment, it is a dozen-plus writers of work, and doing it here would have hidden it inside a
commit about something else.

## What is next

1. **Do not raise the bound.** If a lane needs this green to land, that is a fact to state, not a
   reason to bank 12 writers of drift.
2. Guard the writers the failure output already enumerates, `process_run_complete.py`'s 14 first,
   and let the bound fall out of the work rather than be set to meet it.
3. **Separately, and cheaper: find out why nothing selected this test for two weeks.** A ratchet
   that goes red at HEAD and blocks nothing is the more general defect here, and it is not specific
   to this file — the same silence would cover any other ratchet in `tests/background/`.

---

## DISCHARGED 2026-09-10 — items 1 and 2. Item 3 is NOT discharged.

**The bound was not raised.** 30 write sites across 17 modules now route through
`guard_live_ledger_write`, taking the census **86 → 56**, and the floor moves DOWN to 56 — eighteen
below where it was frozen on 2026-08-26. Selection was by DESTINATION, not by the census's own
module-mentions-the-word proxy: five of the fourteen sites this finding named in
`process_run_complete.py` write to `docs/status/LATEST.md` or a scratch checkout's `.git/`, and
guarding those would have lowered the number while protecting nothing. They are still counted.
Reachability proved with a poison round before the green was believed: one extra un-guarded
observability writer reds the bound at 57, naming it, and green returns when it is reverted.

`guard_site_publish_pipeline` is back in `live_ledger_guard.py` beside its twin.

### The first attempt at this discharge published 87 → 57, and both figures were a dirty tree

An earlier draft of this block, and of the result page, censused the SHARED WORKING TREE — which
carries four other lanes' uncommitted modules and an untracked `standing_red.py`. It counted
writers that are not at HEAD and will not be at HEAD when this lands, then read the difference as
"one more had landed overnight, the drift continuing". Nothing had landed overnight. It was another
lane's in-flight work being called drift by a census that could not tell the two apart.

**A ratchet frozen against a number only the author's dirty tree can reproduce is a bound no other
lane can meet.** Every figure in this block is now from a clean HEAD extract at `8c53c35e5`
carrying this lane's hunks and nothing else: HEAD 86, guarded 56, delta 30 across 17 modules, the
newly-guarded set a strict subset of the HEAD set.

**Item 3 — why nothing selected this test for two weeks — is untouched.** It is the more general
defect and clearing this instance does nothing about it.

---

## ITEM 3 DISCHARGED 2026-09-10 — the whole finding is now closed

**The cause is selection by filename stem.** `tools/pre_commit_test_gate.py` runs a fixed
`CONTROL_TESTS` list on any code change, and otherwise maps a staged `background/X.py` to
`tests/**/test_X.py`. This test was not on the list, so its only selector was
`background/live_ledger_guard.py` — while its subject is every `background/*.py`. Proved by calling
`select_targets` on five of the modules the drift actually landed in (`supervisor`, `notify`,
`process_run_complete`, `worker_tick`, `disk_headroom`): 17–18 targets each, this test in none.

**Fixed:** it is now the eighth `CONTROL_TESTS` entry, with its ~1.6s cost stated against the live
hook-budget finding, and three controls in `tests/tools/test_pre_commit_test_gate.py` grade it —
keyed to the test's whole-package subject rather than to today's list, and poison-round proven to
go red when the entry is removed.

**This finding's closing claim — "the same silence would cover any other ratchet in
`tests/background/`" — was checked and is TRUE.** `test_seat_guard_daemons.py` is the same shape and
is red at HEAD right now: nine daemon entrypoints with no seat guard, one of them
`head_red_register.py` itself. Filed as `SEAT_FINDING_A_SECOND_WHOLE_BACKGROUND_RATCHET_IS_SILENTLY_
RED_AT_HEAD_AND_NINE_DAEMON_ENTRYPOINTS_ARE_UNGUARDED_2026-09-10.md`. It is deliberately NOT added
to `CONTROL_TESTS` while red — that would wedge every lane, which is worse than the defect.

The wider census found **27** such tests repo-wide against a pre-registered band of 5–20, so the
prediction was refuted and the class is 2.5x commoner than I estimated. Sized, not fixed, with a
recommendation: `SEAT_RESULT_THE_STEM_SELECTOR_CANNOT_REACH_TWENTY_SEVEN_WHOLE_TREE_RATCHETS_AND_MY_
BAND_SAID_TWENTY_2026-09-10.md`.

Written up: `SEAT_RESULT_THE_UNGUARDED_WRITER_RATCHET_IS_ARMED_AGAIN_AT_56_AND_THE_NUMBER_I_FIRST_
PUBLISHED_WAS_MY_OWN_DIRTY_TREE_2026-09-09.md`. A second population the census cannot see at all —
35 `open(..., "a")` writers — is filed as `SEAT_FINDING_THE_LIVE_RECORD_CENSUS_ONLY_SEES_WRITE_TEXT_
AND_THIRTY_FIVE_WRITERS_APPEND_THROUGH_OPEN_2026-09-09.md`.
