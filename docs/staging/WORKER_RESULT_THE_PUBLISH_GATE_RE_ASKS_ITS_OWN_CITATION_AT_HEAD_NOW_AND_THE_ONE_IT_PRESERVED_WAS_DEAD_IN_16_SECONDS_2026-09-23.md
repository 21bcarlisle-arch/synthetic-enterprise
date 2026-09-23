# The publish gate re-asks its own citation at HEAD now, and the one it was preserving was dead in 16.8 seconds

**Severity:** RECORDED · **Lane:** H_harness

**Landed:** `2b6bdea95` — `background/process_run_complete.py`,
`tests/background/test_the_publish_gates_citation_is_re_asked_at_head.py`.
**Item:** `the-publish-gates-state-preserves-a-dead-citation-in-the-field-readers-believe` (LANE 0
delivery, direction not atom — no exit test was written for it, so DONE was decided here).

## The premise was NOT spent

The draw's premise check flagged both cited commits (`6e984858f`, `5e078b4d8`) as already
ancestors of `origin/main`. They are — and they were never the work. They are the two SHAs the
record was disclaiming ITSELF with. Re-measured on the live file at draw time, the defect was
exactly as the item described it:

```
"blocking_tests":     ["FAILED tests/design/test_atom_notes_store.py::test_declarations_match_the_store"],
"red_at_head":        "not_established",
"red_at_head_reason": "the red was measured at git=6e984858f and HEAD is now git=5e078b4d8 ..."
```

The cited test passes in 0.53s. The record had already computed that its own citation described
a different commit's tree, and wrote the citation out unchanged beside the disclaimer.

**The duplicate-work check named a different item.**
`the-churn-belief-renderer-is-unstaged-so-the-site-lane-refuses-every-commit` holds
`site/test_the_flat_churn_belief_reaches_the_reader.py` — the tests the LIVE refusal named at the
time the item was written. That claim is about staging a renderer so the site lane stops
refusing; this one is about the record's *citation discipline* and touches neither path. Both
were carried on: not the same work under two names.

**The PATH CHECK graded all three of the item's named paths as landed-or-dirty, and it was
right** — none of them was the subject. The subject was the writer, which the item's path list
never named.

## What was built

`red_at_head_verdict` settles WHICH TREE the named red was measured on, and it is scrupulous
about saying `not_established` when that tree is not HEAD. It never asks the question again. The
disclaimer therefore loses to the citation, because the citation is the concrete part and it is
what the RUNG-1 draw and the seat brief quote.

Now, at the moment the record is written, the cited node ids are re-run against a clean
`_head_checkout()` — the same door the gate's own subject comes through
(DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09). Re-asking in the shared working tree would
answer about whatever the lanes have uncommitted, which is a confident answer to the wrong
question — a smaller version of the defect, not a fix for it.

* A citation whose every id passes is recorded `citation_at_head: dead`, the withdrawn ids kept
  in the reason, and it **leaves `blocking_tests`**. The depth claim and the suspects blame trail
  go with it: `total_red: 3` beside an empty list is this module's own
  accusation-with-no-accused shape, inverted.
* Ids that have gone green *individually* are dropped and the still-red ones kept. That is this
  module's own 2026-08-30 rule — *"no green test may appear in a blocking list"* — **measured**
  rather than argued from the cause that named them. The old enforcement could only suppress the
  whole list on causes where nothing was judged, so it could never see a citation that was
  honestly judged on a tree which has since moved.

**MEASURED BEFORE THE CONTROL WAS WRITTEN, against the live file: 16.8s end-to-end (checkout +
run), verdict `dead`.** That is well inside `PUBLISH_PATH_ALLOWANCE_SECONDS` (900s), which was
the one thing that could have made this the wrong mechanism.

**Keyed to the property, never to those two test names.** The question is put exactly when it is
open: `RED_AT_HEAD_YES` means the publisher's own scoped gate graded a clean checkout of exactly
HEAD, so the citation reproduces by construction and is not re-run.

**Every refusal keeps the citation whole.** An entry that is not a runnable node id (`ERROR
tests/x.py - ImportError` names a FILE, and running the file answers a wider question than the
one cited), a checkout that will not materialise, a timeout, and an id the run returned no
verdict for all read `not_established` with a named reason. Retiring a citation is the fail-open
direction here, so only a positive reading that an id PASSED retires it — and a green gate writes
`not_established`, never `dead`, because nothing was re-run.

## R15

Five mutations, each caught by the leg written for it (not by a different one):

| mutation | leg that caught it |
|---|---|
| drop `blocking = live_node_ids` — keep the dead citation | `..._does_not_survive_in_the_field_readers_reach_for_first` |
| read a missing verdict as green | `test_an_id_the_run_never_reported_on_is_unknown_and_never_green` |
| re-ask even when the gate graded HEAD | `test_a_red_the_scoped_gate_measured_at_head_is_not_re_run` |
| count SKIPPED as still red | `test_a_skipped_test_is_not_a_live_citation` |
| remove the call entirely | 6 legs, incl. the entry/history one |

One partition control asserts all four verdicts are reachable **and distinct** across five
shapes, and that the two shapes sharing `not_established` still tell a reader which refusal they
are.

## It is live

A publish cycle ran 62 seconds after the landing and the field is in the file:

```
"blocking_tests":           [],
"citation_at_head":         "not_established",
"citation_at_head_reason":  "no red is named on this failure, so there is no citation to re-ask.
                             This is not evidence that HEAD is green."
```

The dead citation is gone from the field a reader reaches for first, and the record now says in
its own words what it does and does not establish.

## Not mine, and measured rather than assumed

Six reds and a +5 F401 ruff-ratchet drift showed up in the shared working tree during this turn.
All are green in a clean `git archive HEAD` extract, and all come from other lanes' uncommitted
`background/supervisor.py`, `tests/background/conftest.py`, `tools/refresh_to_head.py` and one
test file that is not at HEAD at all. The commit's own tree (HEAD + these two files) carries no
red this change adds — established by diffing the red set of the extract with and without them,
not by reading the diff.

## What is left open

`liveness_surface_refusal` — the field that held the LIVE refusal while `blocking_tests` held the
dead one — was not touched. It records a publish *cause*, not a test citation, so the re-ask has
no subject there. The reader's remaining hazard is which of the two fields to believe, which is
the separate finding
`feedback_the_publish_gate_state_has_two_refusal_fields_and_the_stale_one_is_the_one_readers_believe`
already names. Not folded in here: it is a different question and a different mechanism.
