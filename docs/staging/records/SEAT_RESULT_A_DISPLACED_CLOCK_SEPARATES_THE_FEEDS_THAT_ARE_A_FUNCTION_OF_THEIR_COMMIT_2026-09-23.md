**Severity:** ADVISORY · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `control_cannot_fail`

# Result: a displaced clock separates the feeds that ARE a function of their commit

**Claim:** `three-latent-reds-gate-the-feed-regeneration-test-file-and-each-is-a-different-defect`
**Pre-registered in** `WORKER_PREREG_WHAT_A_DISPLACED_CLOCK_MEASURES_ABOUT_THE_COVERED_FEED_SET_2026-09-23.md`,
written before any line below was run. **Finding it answers:**
`SEAT_FINDING_THREE_LATENT_REDS_GATE_THE_FEED_REGENERATION_TEST_FILE_AND_EACH_IS_A_DIFFERENT_DEFECT_2026-09-23.md`.

## The predictions, beside what happened

| # | Prediction | Measured | |
|---|---|---|---|
| P1 | 1 of 8 covered feeds is `NONDETERMINISTIC` under a 400-day displacement | **1** — `knowledge_review.json` alone | ✓ |
| P2 | 0 of 8 generators fail under the displaced clock | **0** — no stderr, no timeout, no degraded probe | ✓ |
| P3 | 0 feeds outside `COVERED` reproduce, re-confirmed under displacement | **0**, over 51 cheap generators | ✓ |
| P4 | Re-derived floor: 7 feeds survive as a function of their commit | **7** | ✓ |

`knowledge_review.json` moved `/topics[*]/age_days` 26 → 426 and swung `/tally` from 16 fresh / 0
due to 0 fresh / 16 due. The other seven were byte-identical 400 days out, which is a stronger
statement about them than anything this module could previously make.

## What the finding got half-right, and the half it missed

The finding attributed the wrong promotion to probe RESOLUTION — two runs seconds apart cannot see a
quantity whose period is a day. True, and not the binding constraint. Reading `check()` shows the
determinism tree is **only built when the first tree disagrees**. A feed whose committed bytes are
fresh AGREES on the first tree and is never asked the determinism question at all, so on the day
`knowledge_review.json` was added the probe that would have refused it did not run — at any
resolution. Widening the probe alone would have repaired the half that was not load-bearing.

Both are repaired: `check(..., always_probe_determinism=True)` builds the second tree even on
agreement, and that tree runs its generator under a `sitecustomize` shim displacing `time` and
`datetime` by 400 days. No system `faketime`, no redirected `OUT_PATH` (the two failure modes the
module already refuses), nothing installed outside a scratch directory. `artefact_rerun_diff.compare`
excludes exactly one key by name — `generated_at` — so displacement trips `NONDETERMINISTIC` only
when the clock reaches a field that is not the publication timestamp, which is precisely the
question membership asks.

**P2's hazard was real and is handled rather than hoped about.** A generator that dies under a
displaced clock leaves no second observation, and `_verdict` would read that as DIVERGES — a
widening manufacturing a red. `_second_observation` retries undisplaced and RETURNS the degradation
into the row's `detail["probe"]`, so the narrower question is never answered under the wider one's
name. It did not fire on any of the 51.

## Where the three reds went

1. **`knowledge_review.json` demoted**, into `NOT_A_FUNCTION_OF_ITS_COMMIT` with the measurement
   beside it — not deleted. It is not an exclusion any sweep consults: the promotion leg re-measures
   it every run, so if the generator ever stops reading the wall clock it goes straight back with
   nobody editing a list.
2. **The `len(COVERED) >= 8` floor was re-derived, not decremented.** A floor you edit to fit would
   have gone green for a set gutted one feed at a time. What it stood in for is that the set may
   only shrink through a named door, so it is now
   `len(COVERED) + len(NOT_A_FUNCTION_OF_ITS_COMMIT) >= 8` — monotone non-decreasing whatever
   happens to either side, plus legs that red on an unexplained departure or a feed in both.
3. **Both standpoint legs accept a self-explained `NO_STANDPOINT`.** The account is read off the
   feed's reserved provenance block directly, by a different route from
   `recorded_publication_commit`, so the two can disagree — asserting on the refusal's prose would
   have been a control typed against its own subject's current output. An ungraded candidate that
   does NOT self-explain (`WROTE_NOTHING`, a dead generator, a vanished stamp, or a stamp that
   claims its commit DOES describe its inputs) is still a red.

**And a fourth thing, found while fixing the third.**
`test_a_candidate_standpoint_is_observed_from_the_feed_not_asserted` read
`site/data/<feed>` off the WORKING TREE. In the shared tree several lanes hold dirty copies of
`site/data/` at any moment, so it was asking about another lane's unfinished edit — the exact
fail-open that `test_an_uncommitted_working_copy_edit_does_not_move_the_verdict` exists to refuse,
sitting four tests away from it in the same file. Now reads HEAD's bytes.

## Still outstanding, and it is a producer defect, not a comparator one

`capabilities_door.json` and `evidence.json` have no standpoint because the publisher writes them
from a **dirty working tree** — they stamp `git rev-parse HEAD` beside content read off disk. That
is recorded in `PROVENANCE_IS_NOT_THE_INPUT_DESCRIPTION` and no comparator can repair it. It wants
its own item: the fix is at the publisher, and until it lands `COVERED_AT_THEIR_OWN_COMMIT` stays
empty for a measured reason rather than an unfinished one.
