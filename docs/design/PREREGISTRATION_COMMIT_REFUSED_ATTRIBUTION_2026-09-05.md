# Pre-registration — what `commit_refused` publish cycles actually died of

*Written 2026-09-05, BEFORE the attribution counts were run. The counts follow in
`docs/observability/commit_refused_attribution_2026-09-05.md`. Predictions below are not revised;
where the measurement refuted one, the refutation is recorded beside it and this file stays as
written.*

Subject: `docs/observability/sim-runner-log.md`, the retained span 2026-06-19 → 2026-09-05.

---

## Why this needed a pre-registration at all

The Lane 0 direction arrived carrying a number — *"commit_refused 272"* — and the first thing that
happened when I opened the log was that the number dissolved. That is the shape this project pays
for most often, so the counting rules are fixed here before any attribution is run.

## What each number counts (stated before it is divided by anything)

- **A publish cycle** = one occurrence of `[process_run] Committing and pushing`. This is the
  attempt. It is the denominator, and it is the only denominator used below.
- **A refusal** = one occurrence of `[process_run] Commit/push failed (commit_refused)`. One line
  per cycle, emitted since 2026-06-24. This is the numerator.
- `Done, but THE PUBLISH DID NOT LAND (outcome: commit_refused)` is **not** a second refusal. It is
  a second line about the same cycle, added 2026-08-19. It is used here only to date-partition, and
  never added to anything.
- **Named-red refusal** vs **non-test-gate refusal**: the split is carried in the evidence string
  that `process_run_complete` writes at the refusal branch (`the pre-commit hook chain named N red
  test(s)`), and `N == 0` is what `NON_TEST_REFUSAL_CAUSE` marks. The split is read from the
  refusal's own recorded observation, never inferred from what a later cycle's blocking list says.

## Predictions

**P1 — the split.** More than half of the refusals named **zero** red tests, i.e. the refusing
gate was a non-test gate. Reasoning: the three named non-test gates (orphan ratchet, finding-class,
staging-room) refuse on whole-tree state that no single lane clears, so they refuse repeatedly;
a red test is fixed once and stops refusing.

**P2 — clustering.** The refusals are not an independent per-cycle hazard. They arrive in wedges:
consecutive cycles sharing one unfixed cause. Concretely: the single largest contiguous run of
refusals accounts for **≥15%** of all refusals in the span.

**P3 — the rate is not stable, so the lifetime figure is not a rate.** The refusal share of publish
cycles in the last 14 days is **higher** than the lifetime share. Reasoning: the whole-tree gates
that produce non-test refusals were added over the span, so early cycles could not have been
refused by them.

## What "done" means for this direction

The direction is not an atom and carries no exit test. Done, for this turn, means:

1. The denominator is named and the lifetime rate is stated as a rate, not a lifetime count.
2. The 175 refusals are split into named-red and non-test-gate, with the refusing gates named.
3. Each prediction above is marked CONFIRMED or REFUTED against the measurement, in the record.

What it explicitly does **not** mean: building a mechanism. Nothing has looked at this number yet;
the first pass is measurement, and a control written before the distribution is known would be
keyed to today's answer.

---

## Outcome, appended after measuring — the predictions above are unedited

Full result: `docs/observability/commit_refused_attribution_2026-09-05.md`.

- **P1 REFUTED.** Predicted >50% non-test-gate refusals; measured **48%** (84/175), against 40%
  named-red and 12% unattributable. It reaches 55% only by discarding the unattributable bucket,
  which is exactly the move a pre-registration exists to stop, so it is not made. Non-test gates
  are the plurality and not the majority, and the reasoning behind the prediction — that
  whole-tree gates refuse repeatedly while a red test is fixed once — is contradicted by the data
  in its own terms: the longest same-cause streak in the span is **26 consecutive red-test
  refusals**. Red tests recur too.
- **P2 CONFIRMED.** Longest contiguous run 41 refusals = 23.4% of all refusals, against a
  threshold of 15%. Runs of ≥5 hold 61%.
- **P3 CONFIRMED, on the wrong mechanism.** The recent rate does exceed the lifetime share
  (39.6% vs 9.2%). The stated reasoning was that the refusing gates were added over the span. The
  real cause is that the *named-outcome vocabulary* was added on 2026-08-13, so 77% of the
  lifetime denominator is a span in which a refusal could not be recorded at all. Right direction,
  wrong reason — which is worth recording, because a confirmation obtained through wrong reasoning
  would have licensed the next inference and that inference would have been false.

---

## Follow-on, appended 2026-09-05: `RED TEST` split by failing node id

**No prediction was pre-registered for this split, and none is written now.** The Lane 0 direction
arrived after the outcome above was scored, so this section records a measurement, not a scored
call — saying so is the point, because a prediction filed after the answer is not a prediction.

Result: `docs/observability/commit_refused_attribution_2026-09-05.md`, section *"RED TEST, split by
WHICH test"*. In one line: of 17 established re-arrival steps, 7 show an identical failing-test set
— but **none of those 7 carries the observation that the gate passed in between**, so not one of
them demonstrates a control re-breaking. Every step that does carry that observation (3, all of
them) shows different or only partly-overlapping tests. The flaky-control reading has no supporting
case; the standing-red reading has two independent ones. Three steps is the whole strong sample and
it licenses a direction, not a threshold.
