# WORKER FINDING — a phase was stamped with a commit made 23 minutes after its own suite started

**Severity:** LATENT · **Lane:** H_harness

**Filed** 2026-08-11 (OPS2 tenth tick) · **Atom** `OPS2_publish_gate_head_worktree` ·
**Status** FIXED this tick, mechanism + controls landed · **Class** a control graded on a label
that belongs to neither subject

## The claim, `observed`

`docs/observability/publish_gate_subject_cost.json`, launch 14, banked:

```json
"throwaway_checkout": {"cwd": "/var/tmp/publish-gate-head-qey8309l",
                       "head_sha_at_run": "a322429d1...", "seconds": 1873.7}
```

and the field's own comment in `tools/measure_publish_gate_subject_cost.py` called it *"the SHA
THIS phase actually ran against"*.

It was not. Reconstructed from the record and `git` alone, no inference:

| fact | value | source |
|---|---|---|
| launch started | 20:29:36Z | record `started_at` |
| next phase entered | 21:33:51Z | record `in_flight.since` |
| throwaway ran for | 1873.7s = 31m14s | record `seconds` |
| ⇒ its suite STARTED at | ~21:02:37Z | the two above |
| `a322429d1` was committed at | **21:26:07Z** | `git show -s --format=%cI` |

The stamped commit was made **23½ minutes after** the suite it labels had already started, into a
repo whose contents could not reach a `git archive` extraction that had already happened. The
stamp was `prc._head_sha()` — the LIVE repo, read AFTER the suite returned — so it named whichever
commit another lane happened to land during the run. For the throwaway phase it is the wrong repo
as well as the wrong moment: a checkout is a different repo, whose `.git/HEAD` is the extracted
SHA.

## Why it is not cosmetic

That field is the ONLY input to the cross-commit comparability guard — the rule ticks 4 and 8 both
exist to enforce, that this atom's ratio may not span two commits. End-stamping makes the guard
answer a question about neither subject, and it fails in **both** directions:

* **FAIL-OPEN, likeliest exactly when the harness runs.** Throwaway extracted at X, runs 31
  minutes while commits land to Z; baseline starts at Z and the box stays quiet, so it too ends at
  Z. Both stamps read Z, `spanned` sees one SHA, and the ratio is computed across subjects X and Z
  and published as the cost of the checkout — the precise defect the guard was written twice to
  prevent, arriving through the door it was watching. It requires a QUIET second phase, which is
  the condition this harness *waits for*.
* **FAIL-CLOSED the other way.** A pair that genuinely ran the same code is refused because one
  unrelated commit landed during phase two, and the atom pays another ~40 minutes.

## The repair — ask the subject, not the repo

`_subject_sha(cwd)` asks the tree the suite ran in what commit it is, BEFORE the suite starts
(`head_sha_at_run`) and again after (`head_sha_at_end`), with `subject_changed_during_run` and the
phase's own `started_at`/`ended_at`.

**A moved subject is REPORTED, not refused** (`ratio_subject_moved_during`), and the asymmetry
against the SHA rule is deliberate: a phase whose subject took a small edit part-way through is
one subject, not two, and the in-tree phase runs in a shared tree other lanes commit to every few
minutes — refusing on it would starve this atom's one owed number permanently, which is the
guard-that-waits-for-a-gap shape.

**R15 both ways, eight mutations RUN**, source restored byte-identical after each: stamp from the
live repo (3 red); stamp after the suite (1); the mid-run flag hardcoded False (1);
`ratio_subject_moved_during` dropped (1); a moved subject made a refusal (1); the writer stops
emitting `started_at` (2); the postdating criterion never fires (1); always fires (1).
101 passed in the module, 245 across the publish-gate family, ruff clean.

The new population control `test_no_banked_phase_stamps_a_commit_that_postdates_its_own_start`
grades the live record against git's own commit dates — an independent source — and would have
caught this from the repo alone. It currently grades ZERO phases (nothing banked carries
`started_at` yet), so it is **put on trial with an oracle**: a real repo and two records differing
in one value either side of the stamped commit's date, proving it both fires and discriminates.
The non-emptiable half is the writer test, per this module's own earlier lesson that a vacuity
guard keyed to a population a healthy mechanism legitimately empties is a second failure mode.

## Not done, deliberately

* **The mis-stamped banked phase is not relabelled.** The true SHA is bounded (between `88f851846`
  and `3f8ec3169`) but not known, and writing a plausible one would be fabricating evidence. It
  must be RE-TIMED. No action is needed: its stamp already differs from HEAD, so
  `_drop_incomparable_ratio_phases` drops it at the next launch.
* **The live record was not edited.** Launch 14 (pid 318057) is mid-`in_tree_baseline` and owns
  that file; racing its checkpoint would cost the run that answers the atom's owed item.
* **Pinning the pair — RECOMMENDED, QUEUED, not built.** The two phases will keep landing at
  different SHAs by luck. The design that removes luck: run `in_tree_baseline` first, take its
  start SHA S, and extract the throwaway from **S** rather than from live HEAD, so the pair is
  comparable *by construction* instead of by a quiet window this box does not give. It needs an
  optional SHA parameter on `prc._head_checkout()` — publish-path code, whose gate scope is the
  thing an undersized change wedges — so it is queued rather than taken beside a live measurement.
