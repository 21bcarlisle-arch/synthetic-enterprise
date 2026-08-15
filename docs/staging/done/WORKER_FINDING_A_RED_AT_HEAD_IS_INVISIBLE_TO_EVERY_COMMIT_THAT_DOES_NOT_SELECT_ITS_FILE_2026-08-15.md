# WORKER FINDING (QUEUED) — a red at HEAD is invisible to every commit that does not select its file, so the tree was red for at least one commit and the gate said nothing until an unrelated data file pulled the tests in

**Severity:** LATENT · **Lane:** H_harness · **Disposition:** QUEUED (not fixed on sight; the INSTANCE was repaired because a red HEAD blocks every lane, the CLASS is queued)

**Found by:** the 2026-08-15 worker tick, discharging BLOCKING 1 of
`WORKER_FINDING_THE_CORRECTED_SENTENCE_NEVER_REACHED_THE_READER_AND_ITS_CONTROL_HAS_NO_CALLER_2026-08-15.md`.
Measured at HEAD `c6a4790ad`. Everything below is `observed-with-evidence` unless labelled
`inferred` (R9).

## Observed

A `surgical_land` of two DATA paths — `site/data/proof.json` and
`docs/observability/coupled_gap_ledger.json`, no code — was refused after a full 11-minute gate
cycle with **3 failed, 1288 passed**:

- `tests/tools/test_couple_cohort.py::test_measure_returns_gap_result_matching_score_worst_cell`
- `tests/tools/test_couple_cohort.py::test_write_gap_entry_mechanism_against_temp_ledger`
- `tests/tools/test_couple_w2_5_c7.py::test_this_pair_does_not_publish_another_dimensions_name`

all with `ValueError: GapResult(metric=...) declares no normalisation kind (got '')` from
`background/gap_metric.py:188`.

**None of the three has anything to do with the two files being landed.** The gated tree was
HEAD plus two JSON files, so the red is HEAD's own: the D44 normalisation contract (a REQUIRED
`normalisation` kind on every `GapResult`) is committed, and two of its consumers' declarations
— 9 lines across `tools/couple_cohort.py` and `tests/tools/test_couple_w2_5_c7.py` — were left
uncommitted in the working tree. `git show HEAD:tools/couple_cohort.py | grep -c normalisation`
→ **0**; the same grep on the working tree → 1. The three tests pass in the working tree and
fail at HEAD.

## Why nothing said so

`tools/pre_commit_test_gate.py` selects test files by NAME STEM. Every commit since the contract
landed touched paths whose stems select other suites — `c6a4790ad` (couple_w2_11_d5),
`f4144b4f0` (B_commercial) — so none of them ever ran `test_couple_cohort.py`. The red surfaced
only because a commit naming `docs/observability/coupled_gap_ledger.json` pulls **28** gap-related
test files into the selection.

So the gate's promise ("a red commit is structurally impossible") holds for the CHANGE, and not
for the TREE. A tree can be red for an arbitrary number of commits, and which commit discovers it
is decided by filename coincidence rather than by anything about the defect.

**This is the same shape as `WORKER_FINDING_THE_RUFF_RATCHET_IS_RED_AT_HEAD_AND_ONLY_SOME_COMMITS_CAN_SEE_IT_2026-08-14.md`,
one day later and in the test suite rather than the linter — which makes it a rate, not an
incident (R10).** The cost is paid by whichever lane's commit happens to select the file: this
tick paid a full 11-minute gate cycle and a diagnosis to discover a defect it did not cause, and
had to adopt another lane's hunks to make its own BLOCKING repair landable at all.

## What was done here, and what was not

**Repaired (instance):** the two consumer declarations were landed alone and disclosed in the
commit message — a red HEAD blocks every lane, so leaving it was not an option, and the two hunks
are exactly the declaration the contract demands and nothing else (9 added lines, no behaviour
change). D44's own record was not touched and the rest of that lane's work stays uncommitted and
stays theirs.

**Not built (class), and this is the finding:** nothing measures whether HEAD is green. Options,
with a recommendation:

1. **A periodic full-suite run against HEAD**, reporting reds to the same channel the daemons use.
   Catches every class of tree-red, costs one full suite per period, and does not slow any lane.
2. **Widen gate selection** so every commit runs more than its own stems. Slows every commit to
   fix a problem that is not the commit's, and the 28-file selection this tick paid for is already
   11 minutes.
3. **A HEAD-green precondition inside `surgical_land`** — check the tree BEFORE the expensive gate.
   Same cost as 2, and it makes every lane's landing wait on a defect it did not cause.

**Recommendation: 1.** The defect is that nobody is measuring the tree, not that individual commits
measure too little — and 2 and 3 both charge the wrong lane. The distinguishing evidence is in this
finding: the red was ownerless for at least two commits, so the fix has to be owned by something
that runs on a clock rather than on a commit.

## SECOND INSTANCE, same day, different suite — measured independently at HEAD `3e4037c1e`

`observed-with-evidence`, by the NEXT tick of the same discharge, which hit this defect again
without knowing this document existed:

A `surgical_land` of `site/data/proof.json` alone was refused with **2 failed, 685 passed** in
`site/proof/test_predictions_ledger_can_fail.py` — `test_live_surface_renders_the_derived_headline`
and `test_live_surface_states_the_horizon_and_names_the_stale_snapshot`. Both failures sit wholly
inside the predictions section, which that one-line caveat diff does not touch, and **both are
green in the working tree**. The cause is the same shape one layer along: `site/data/proof.json`
was committed at HEAD carrying values generated from two suppliers that were never committed with
it — `site/state/live_portfolio.json` (the outcome source: HEAD 2026-08-13T23:38:21Z against the
door's rendered 2026-08-15T04:41:16Z) and `site/state/track_record_scorecard.json` (the CLOCK,
`generate_proof_data.py:1134`: HEAD 2026-08-14 against the tree's 2026-08-15, which is why the
committed pair computes a `-1 day(s) old` snapshot).

Three things this instance adds to the class:

1. **It is the SITE lane, not the tests/ gate.** The mechanism is not stem-selection here but the
   site-lane step's own broad trigger (site/data, any `generate_*_data` producer, or a
   site-consumed ledger). A red can therefore sit at HEAD in `site/**` until some lane happens to
   touch a data file — same ownerless red, a second selection mechanism. Widening stem selection
   (option 2 above) would not have caught this one at all.
2. **The supplier/consumer split is the recurring generator.** Both instances are a committed
   consumer whose supplier stayed in the working tree. That is the same shape as the finding this
   whole tick was discharging, which makes it three in three days rather than two.
3. **The instance was repaired the same way, and disclosed.** The two suppliers were landed with
   the consumer at `272e35bb3`, making the committed tree self-consistent for the first time since
   2026-08-13. Neither file's content was authored or adjusted — they are the tree's own bytes,
   which HEAD's already-committed `proof.json` was already rendering.

**This does not change the recommendation, it sharpens it.** Option 1 (a periodic full-suite run
against HEAD) must cover `site/**` as well as `tests/`, because the two lanes have independent
selection rules and this class has now been observed once in each.

## Not established (R9)

* **How long HEAD has been red is not measured.** Only that it is red at `c6a4790ad` and that the
  two commits before it did not select the file. Bisecting the contract's landing commit was not
  attempted.
* Whether other suites are red at HEAD for the same reason is **not checked** — this tick observed
  only the 28 files its own selection pulled in.
