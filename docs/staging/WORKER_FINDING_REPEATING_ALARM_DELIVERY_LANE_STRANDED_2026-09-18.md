**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [SEAT] reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch was claimed, landed NOTHING, and its work is SITTING IN THE SHARED TREE

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **1 times without its state changing**, over **1.7h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 1th page does not.

## The alarm, verbatim

```
[SEAT] reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch was claimed, landed NOTHING, and its work is SITTING IN THE SHARED TREE
4 path(s) hold uncommitted bytes on the shared tree, unchanged since before the window closed -- oldest background/process_run_complete.py at 14.5h: background/process_run_complete.py, tests/tools/test_fold_noise_floor_family.py, tools/run_value_cycle_ab.py, tests/tools/test_value_cycle_ab_noise_floor.py
These are bytes, not a plan: the work exists and has never been in a commit, so redoing it would be doing it twice. Land them by the ordinary route (`python3 -m tools.surgical_land -m "..." <paths>`), then `python3 -m background.delivery_lane --landed reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch`.
```

## What is known without diagnosing anything

- Signature: `delivery-lane-stranded:reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-18T07:35:49+00:00
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
- **2026-09-19** — still live. 1 repeats over 1.7h without the state changing. No second document filed: this condition already has one.
- **2026-09-20** — still live. 1 repeats over 1.7h without the state changing. No second document filed: this condition already has one.
- **2026-09-21** — still live. 1 repeats over 1.7h without the state changing. No second document filed: this condition already has one.
- **2026-09-22** — still live. 1 repeats over 1.7h without the state changing. No second document filed: this condition already has one.
- **2026-09-23** — still live. 1 repeats over 1.7h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch` (first seen 2026-09-18)
- `the-ordinary-not-done-sweep-still-returns-an-empty-reason` (first seen 2026-09-18)
- `land-the-svt-origin-exit-that-is-already-built-and-sitting-in-this-tree` (first seen 2026-09-18)
- `kill-the-duplicate-floor-run-and-free-the-only-box` (first seen 2026-09-19)
- `churn-truncation-destroys-the-decision-surface-before-the-arm-is-asked` (first seen 2026-09-19)
- `land-the-shape-and-box-repair-the-lane-already-called-done` (first seen 2026-09-19)
- `the-landed-unbound-binder-counts-a-heartbeat-as-a-landing` (first seen 2026-09-19)
- `land-the-stranded-shape-and-box-repair` (first seen 2026-09-20)
- `pages-root-anchor-block-publishes-internal-voiced-documents` (first seen 2026-09-20)
- `finish-the-churn-truncation-residual-the-census-is-computing-now` (first seen 2026-09-20)
- `the-five-reading-partition-is-red-at-head-on-its-premise-spent-leg` (first seen 2026-09-21)
- `name-the-35-remaining-bare-keyerror-refusals-on-raise-on-missing-registers` (first seen 2026-09-21)
- `the-publish-gate-has-been-red-since-saturday-on-one-uncovered-carrier` (first seen 2026-09-21)
- `re-rule-the-memory-ceiling-against-measured-whole-run-rss` (first seen 2026-09-21)
- `the-settlement-ceiling-can-move-now-that-its-curve-has-landed` (first seen 2026-09-21)
- `widen-membership-guarded-to-see-the-early-return-guard-so-the-surveys-bare-count-means-what-it-says` (first seen 2026-09-21)
- `ten-of-eighteen-premises-get-a-climate-normal-instead-of-the-worlds-weather` (first seen 2026-09-22)
- `the-live-page-still-publishes-the-coin-flip-as-a-settled-no` (first seen 2026-09-22)
- `the-arms-error-bar-is-taken-over-a-different-book-from-the-figure-it-bounds` (first seen 2026-09-22)
- `four-declared-daemons-have-written-nothing-since-they-started` (first seen 2026-09-22)
- `advance-the-base-read-the-census-honestly-and-enact-the-two-decided-files` (first seen 2026-09-22)
- `how-to-read-this-is-the-one-truthiness-reader-and-it-withdraws-on-the-tie` (first seen 2026-09-23)
- `the-regeneration-check-clones-at-head-so-it-cannot-see-the-producer-edit-that-wedges-the-publisher` (first seen 2026-09-23)
- `the-refuted-bill-stress-knee-is-unbounded-beside-a-saturating-size-term` (first seen 2026-09-23)

## Re-asked
- **2026-09-24** — re-asked: **still_holds**. observed 2026-09-23, within the 3-day bar.
