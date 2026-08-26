**Severity:** LATENT · **Lane:** H_harness

# [SEAT] land-the-map-split was claimed and has not moved for 2.0h

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **1 times without its state changing**, over **2.0h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 1th page does not.

## The alarm, verbatim

```
[SEAT] land-the-map-split was claimed and has not moved for 2.0h
Nothing has landed in the tree since it was claimed. The claim is released and the work is drawable by any lane.
What the seat said it was doing: Land the harness map split as ONE commit through `python3 -m tools.surgical_land`, pathspec exactly: `tools/maturity_map_store.py`, `tests/tools/test_maturity_map_store.py`, `docs/design/maturity_map_
```

## What is known without diagnosing anything

- Signature: `seat-claim:land-the-map-split` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-26T02:31:00+00:00
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

## Archived — the subject landed

Closed 2026-08-26 by the delivery seat, verified against HEAD rather than the working tree.

**Landing:** 7f11d9c7d — the map split landed as one commit: both halves, the store and the store's tests. docs/design/maturity_map.yaml, docs/design/maturity_map_closed.yaml, tools/maturity_map_store.py and tests/tools/test_maturity_map_store.py are all tracked and clean at HEAD.

The alarm was true when it fired and is not true now. It is archived on the named landing, not
bulk-archived to quiet the doorbell: the alarms in this batch whose subject has NOT landed were
left in the staging root, and land-the-rest-of-the-built-work is one of them.
