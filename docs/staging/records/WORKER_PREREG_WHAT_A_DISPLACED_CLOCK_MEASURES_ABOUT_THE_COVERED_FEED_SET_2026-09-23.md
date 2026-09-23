**Severity:** ADVISORY · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `control_cannot_fail`

# Pre-registration: what a displaced clock measures about the covered feed set

**Claim:** `three-latent-reds-gate-the-feed-regeneration-test-file-and-each-is-a-different-defect`
**Written before any of the measurements below was run.** The diagnosis it tests is in
`SEAT_FINDING_THREE_LATENT_REDS_GATE_THE_FEED_REGENERATION_TEST_FILE_AND_EACH_IS_A_DIFFERENT_DEFECT_2026-09-23.md`.

## The mechanism this is about, restated because the finding named only half of it

The finding says `knowledge_review.json` entered `COVERED_FEEDS` because `NONDETERMINISTIC` is
probed by two runs seconds apart while `age_days` changes once a day — the probe's resolution is
shorter than the period it hunts. Reading `check()` shows that is the *second* of two reasons, and
the first is larger:

**the determinism tree is only built when the first tree DISAGREES** (`needs_second = ... and any(
committed.get(n) != b ...)`). A feed that AGREES is never probed for determinism at all. So on the
day `knowledge_review.json` was promoted its committed bytes were fresh, it agreed, and no
determinism question was ever asked of it. Widening the probe's resolution without also asking it on
the agreeing path would repair the half that was not load-bearing.

Both halves are repaired here: the second tree runs its generator under a **displaced wall clock**
(a `sitecustomize` shim on `PYTHONPATH` shifting `time` and `datetime` by a fixed offset — no system
`faketime`, no redirected `OUT_PATH`), and `check()` gains a mode that builds it even on agreement.
`compare()` excludes `generated_at` by name and nothing else, so a displaced clock only trips
`NONDETERMINISTIC` when the clock reaches a field that is not the publication timestamp — which is
exactly the discrimination the membership rule wants.

## Predictions, registered before running

| # | Question | Prediction |
|---|---|---|
| P1 | Of the 8 feeds now in `COVERED_FEEDS`, how many measure `NONDETERMINISTIC` under a displaced clock with the determinism tree forced? | **1** — `knowledge_review.json` alone |
| P2 | How many of the 8 generators fail (crash, timeout, write nothing) under the displaced clock? | **0** |
| P3 | Does the cheap promotion sweep, re-confirmed under the displaced clock, find any feed outside `COVERED` that reproduces deterministically? | **0** — the promotion leg is green today, and displacement can only ever remove candidates |
| P4 | Re-derived floor for `test_the_feed_the_defect_happened_on_is_covered`: how many feeds survive as a function of their commit? | **7** |

**P2 is the one that can cost something.** A generator that dies under a displaced clock leaves no
second observation, and the current code would fall through to `DIVERGES` — a false red. The build
therefore falls back to the undisplaced probe when the displaced run does not write the feed, rather
than letting the widening turn into a red. If P2 is wrong, that fallback is what the answer is about
and it is recorded, not the count.

**What would refute the whole approach:** P1 > 1 with the extra feeds being ones whose clock
dependence is confined to a key `compare()` should be ignoring anyway — that would mean the
displacement is measuring the instrument rather than the feeds, and the right response is to widen
`THE_CLOCK` rather than to demote the feeds.

## The result

Recorded beside each prediction in
`SEAT_RESULT_A_DISPLACED_CLOCK_SEPARATES_THE_FEEDS_THAT_ARE_A_FUNCTION_OF_THEIR_COMMIT_2026-09-23.md`
when the measurement has run. A prediction filed after the answer is not a prediction.
