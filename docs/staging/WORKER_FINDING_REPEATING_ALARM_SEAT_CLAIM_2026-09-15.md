**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [SEAT] close-the-fork-six-conflict-paths-each-with-a-named-resolution was claimed and has not moved for 95.5h

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **1 times without its state changing**, over **95.5h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 1th page does not.

## The alarm, verbatim

```
[SEAT] close-the-fork-six-conflict-paths-each-with-a-named-resolution was claimed and has not moved for 95.5h
NO PATHS WERE EVER BOUND to this claim, so nothing about it could be observed -- it is released on the clock, not because the work was seen to stall. Bind the paths of each landing as it lands (`delivery_lane.record_landing`) and this becomes a real signal. The claim is released and the work is drawable by any lane.
What the seat said it was doing: unprocessed staging -- CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md, CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md, CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md, CLASS_NO_CALLER_AND_NEVER_RUNS_2026
```

## What is known without diagnosing anything

- Signature: `seat-claim:close-the-fork-six-conflict-paths-each-with-a-named-resolution` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-11T07:56:32+00:00
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

- **2026-09-15, delivery seat, scheduled tick.** The released claim
  `close-the-fork-six-conflict-paths-each-with-a-named-resolution` was re-drawn this tick and its
  work advanced: all six conflicted paths now have a named resolution and the merge is mechanically
  complete. It is deliberately NOT landed — see
  `SEAT_FINDING_THE_MERGE_OPENS_THE_SIGN_GATE_AND_THE_HEADLINE_COMPOSER_REPUBLISHES_A_WITHDRAWN_SENTENCE_2026-09-15.md`
  for the one control still refusing and why it is right to.

  **No claim was taken and none was minted.** Both `.delivery_lane_claims.json` and
  `.seat_work_in_hand.json` were read and are `{}` — so there was no id to bind a landing to, and
  minting one for work that has already landed would put a rival id in the store rather than record
  anything. The two commits this tick are `f3d95cc46` and the archive commit that follows it; they
  are bound to this document instead, which is the thing a later tick will actually read.

  The alarm's own advice stands and is the real repair: **the claim carried no bound paths**, so
  nothing about it could ever be observed and it was released on the clock rather than on evidence.
  That is a defect in how the claim was taken, not in this work.

## Instances seen
- `close-the-fork-six-conflict-paths-each-with-a-named-resolution` (first seen 2026-09-15)
- `the-blind-envelope-reaches-a-reader` (first seen 2026-09-15)
- `the-lane-refuses-a-placeholder-id-and-the-settlement-row-is-bound` (first seen 2026-09-15)
