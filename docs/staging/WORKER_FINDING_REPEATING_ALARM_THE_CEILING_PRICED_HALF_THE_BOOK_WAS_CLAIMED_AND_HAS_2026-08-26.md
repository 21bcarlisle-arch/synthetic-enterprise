**Severity:** LATENT · **Lane:** H_harness

# [SEAT] the-ceiling-priced-half-the-book was claimed and has not moved for 1.7h

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **1 times without its state changing**, over **2.0h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 1th page does not.

## The alarm, verbatim

```
[SEAT] the-ceiling-priced-half-the-book was claimed and has not moved for 1.7h
No commit has touched its 7 claimed path(s) (docs/design/THE_VALUE_CYCLE_REALISED_AB.md, docs/observability/value_based_pricing_arms.json, docs/staging/WORKER_FINDING_THE_CHURN_MODELS_CAP_MAKES_THE_PROFIT_MAXIMISING_PRICE_UNBOUNDED_2026-08-25.md, tests/tools/test_couple_value_based_pricing.py, tests/tools/test_run_value_cycle_ab.py…) in that time. The claim is released and the work is drawable by any lane.
What the seat said it was doing: Establish why the value arm's maximiser still runs to its own bound on half the book, and either make the optimum interior for a reason that is about the customer, or report in the A/B artefact that t
```

## What is known without diagnosing anything

- Signature: `seat-claim:the-ceiling-priced-half-the-book` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-26T21:43:39+00:00
- Repeats before escalation: 1 (threshold `ESCALATE_AFTER_REPEATS`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. While this document is live
-- here or in `in_progress/` -- a continuing condition APPENDS a dated line below rather than
filing a second document (2026-08-24). A condition that returns AFTER this has been archived
files a fresh document, because that is a new episode and an R3 two-strike signal.

## Still live
