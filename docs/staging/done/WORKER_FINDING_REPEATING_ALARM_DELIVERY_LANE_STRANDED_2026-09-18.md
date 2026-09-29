**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [SEAT] reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch was claimed, landed NOTHING, and its work is SITTING IN THE SHARED TREE

<!-- counts:begin -->
**Filed automatically by `background/alarm_repetition.py`, not by a person.** This condition
has been **observed to hold on 8 separate day(s)**, between **2026-09-18** and **2026-09-25**,
and **31 member(s)** of the family `delivery-lane-stranded` have fired. Both counts are DERIVED
from this document's own dated lines every time the alarm fires again, so they age with the
document rather than with its first firing.

This condition's observer calls `escalate()` directly rather than through `notify()`, so no
consecutive-firing count exists for it and `ESCALATE_AFTER_REPEATS` (= 3) was never applied.
That absence is stated rather than filled with a placeholder count.
<!-- counts:end -->

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
- `census-git-show-head-controls-that-mean-this-commit` (first seen 2026-09-24)
- `the-checkout-fast-forward-is-blocked-on-two-contested-files-not-on-a-judgement` (first seen 2026-09-24)
- `the-ahead-leg-is-filled-automatically-and-drained-by-hand` (first seen 2026-09-24)
- `the-fork-closer-is-running-from-bytes-in-no-commit` (first seen 2026-09-25)
- `the-last-residue-path-has-no-door-because-its-only-loss-is-a-comment` (first seen 2026-09-25)
- `bill-stress-hazard-from-the-arrears-ledger` (first seen 2026-09-25)
- `boot-sha-drift-reads-zero-stale-over-one-resolvable-daemon` (first seen 2026-09-25)
## Re-asked
- **2026-09-24** — re-asked: **still_holds**. observed 2026-09-23, within the 3-day bar.
- **2026-09-25** — re-asked: **still_holds**. observed 2026-09-24, within the 3-day bar.
- **2026-09-26** — re-asked: **still_holds**. observed 2026-09-25, within the 3-day bar.
- **2026-09-27** — re-asked: **still_holds**. observed 2026-09-25, within the 3-day bar.
- **2026-09-28** — re-asked: **cleared**. no observation since 2026-09-25, past the 3-day bar; the store holds no key for `delivery-lane-stranded` at all, so it can neither corroborate nor contradict this and the document's own lines are the only witness; and the machinery observed other conditions on 2026-09-27, so the silence is the observers running and not seeing it.

## Re-asked and cleared, 2026-09-28

Archived by `background/alarm_repetition.reask()`, not by a person, and not because anybody diagnosed it.

- **What was asked:** has the condition behind `delivery-lane-stranded:reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch` been observed to hold since it was last annotated?
- **Last observation:** 2026-09-25
- **The answer, and what carried it:** no observation since 2026-09-25, past the 3-day bar; the store holds no key for `delivery-lane-stranded` at all, so it can neither corroborate nor contradict this and the document's own lines are the only witness; and the machinery observed other conditions on 2026-09-27, so the silence is the observers running and not seeing it.
- **What this does NOT claim:** that the condition was fixed, or why it stopped. Only that nothing has observed it for 3 days while the observers were demonstrably running. If it returns it files a FRESH document — `escalate()` does not search `done/` — and that fresh document is an R3 two-strike signal worth more than this one was.

