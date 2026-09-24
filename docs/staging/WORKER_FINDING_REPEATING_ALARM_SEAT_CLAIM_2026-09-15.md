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
- **2026-09-16** — still live. 1 repeats over 0.8h without the state changing. No second document filed: this condition already has one.
- **2026-09-17** — still live. 1 repeats over 0.8h without the state changing. No second document filed: this condition already has one.
- **2026-09-18** — still live. 1 repeats over 1.7h without the state changing. No second document filed: this condition already has one.
- **2026-09-19** — still live. 1 repeats over 1.7h without the state changing. No second document filed: this condition already has one.
- **2026-09-20** — still live. 1 repeats over 1.7h without the state changing. No second document filed: this condition already has one.
- **2026-09-21** — still live. 1 repeats over 2.2h without the state changing. No second document filed: this condition already has one.
- **2026-09-22** — still live. 1 repeats over 1.7h without the state changing. No second document filed: this condition already has one.
- **2026-09-23** — still live. 1 repeats over 3.1h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `close-the-fork-six-conflict-paths-each-with-a-named-resolution` (first seen 2026-09-15)
- `the-blind-envelope-reaches-a-reader` (first seen 2026-09-15)
- `the-lane-refuses-a-placeholder-id-and-the-settlement-row-is-bound` (first seen 2026-09-15)
- `the-two-finished-runs-artefacts-reach-origin-and-the-envelope-renders` (first seen 2026-09-15)
- `close-the-fork-fix-the-composer-then-land-ead8f781a` (first seen 2026-09-15)
- `teach-the-write-keyed-oracle-to-follow-a-path-into-a-helper` (first seen 2026-09-15)
- `point-the-arm-at-the-renewals-that-are-genuinely-reachable-so-the-inference-verdict-becomes-stateable` (first seen 2026-09-16)
- `the-publisher-has-published-nothing-in-140-hours-and-30-consecutive-attempts` (first seen 2026-09-16)
- `a-gas-only-account-must-be-able-to-leave-before-the-158-can-be-priced` (first seen 2026-09-16)
- `the-gas-tariff-type-read-becomes-the-c1b-roll-now-that-the-18-can-leave` (first seen 2026-09-16)
- `drain-the-five-stale-copies-the-census-says-would-revert-a-landing` (first seen 2026-09-16)
- `the-publisher-has-never-recorded-a-clean-publish-in-this-episode` (first seen 2026-09-16)
- `does-the-publisher-actually-publish-now-the-here-relative-wedge-is-clear` (first seen 2026-09-16)
- `a-swept-row-must-ask-git-whether-the-work-landed-under-another-name` (first seen 2026-09-16)
- `some-id` (first seen 2026-09-16)
- `make-the-per-cell-weather-store-reproducible` (first seen 2026-09-16)
- `the-publish-gates-own-tests-are-red-at-head-and-the-finished-repair-is-unlanded` (first seen 2026-09-17)
- `discharge-the-six-freezers-because-archiving-is-not-discharge` (first seen 2026-09-17)
- `land-the-per-cell-weather-store-and-wire-its-reader` (first seen 2026-09-17)
- `the-blocking-tests-record-owes-its-reader-the-divergence-of-the-tree-it-graded` (first seen 2026-09-17)
- `era5-pull-the-last-23-cells-in-two-passes-an-hour-apart` (first seen 2026-09-17)
- `thirteen-background-controls-are-red-at-head-and-the-gate-selects-none-of-the-changes-that-broke-them` (first seen 2026-09-17)
- `playwright-lost-so-the-pixel-verification-door-cannot-run` (first seen 2026-09-17)
- `the-publisher-cannot-push-and-the-cause-has-moved-to-push-never-landed` (first seen 2026-09-17)
- `the-vm-backed-door-suites-still-have-no-browser-leg-and-only-one-of-twenty-four-was-ever-built` (first seen 2026-09-17)
- `the-publisher-has-never-graded-a-clean-publish-and-the-site-lane-is-red-right-now` (first seen 2026-09-17)
- `read-next12-alone-it-cannot-be-folded-into-the-eighteen` (first seen 2026-09-17)
- `fit-the-hook-chain-growth-series-because-the-deadlines-room-halved-in-a-fortnight-and-nothing-watches-it` (first seen 2026-09-17)
- `the-page-prices-a-sign-off-a-spliced-family-and-nobody-has-asked-where-the-variance-comes-from` (first seen 2026-09-17)
- `execute-the-reconcile-the-refusal-now-prints-instead-of-labelling-it-a-ninth-time` (first seen 2026-09-18)
- `the-two-arms-have-never-priced-the-same-population-and-the-page-says-they-have` (first seen 2026-09-18)
- `the-republish-is-blocked-on-six-controls-and-a-dead-tariff-branch` (first seen 2026-09-18)
- `reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch` (first seen 2026-09-18)
- `the-product-gate-census-answers-per-record-while-the-guard-refuses-per-term` (first seen 2026-09-18)
- `the-ordinary-not-done-sweep-still-returns-an-empty-reason` (first seen 2026-09-18)
- `the-svt-household-has-no-route-back-to-a-fixed-term` (first seen 2026-09-18)
- `land-the-svt-origin-exit-that-is-already-built-and-sitting-in-this-tree` (first seen 2026-09-18)
- `measure-whether-the-product-gate-is-the-real-ceiling-on-the-methods-reach` (first seen 2026-09-19)
- `kill-the-duplicate-floor-run-and-free-the-only-box` (first seen 2026-09-19)
- `price-the-discrimination-auc-against-its-own-null` (first seen 2026-09-19)
- `a-producer-of-default-tariff-arrivals` (first seen 2026-09-19)
- `value-arms-error-bar` (first seen 2026-09-19)
- `churn-truncation-destroys-the-decision-surface-before-the-arm-is-asked` (first seen 2026-09-19)
- `the-orientation-brief-misreports-the-machine-it-describes` (first seen 2026-09-19)
- `land-the-shape-and-box-repair-the-lane-already-called-done` (first seen 2026-09-19)
- `the-landed-unbound-binder-counts-a-heartbeat-as-a-landing` (first seen 2026-09-19)
- `the-churn-reconciliation-residual-says-minus-two-and-its-own-prose-says-zero` (first seen 2026-09-20)
- `land-the-stranded-shape-and-box-repair` (first seen 2026-09-20)
- `finish-the-churn-truncation-residual-the-census-is-computing-now` (first seen 2026-09-20)
- `pages-root-anchor-block-publishes-internal-voiced-documents` (first seen 2026-09-20)
- `close-the-fork-that-has-refused-eleven-publishes` (first seen 2026-09-21)
- `name-the-35-remaining-bare-keyerror-refusals-on-raise-on-missing-registers` (first seen 2026-09-21)
- `the-five-reading-partition-is-red-at-head-on-its-premise-spent-leg` (first seen 2026-09-21)
- `the-publish-gate-has-been-red-since-saturday-on-one-uncovered-carrier` (first seen 2026-09-21)
- `the-capacity-that-refuses-the-thesis-book-stands-on-nothing` (first seen 2026-09-21)
- `re-rule-the-memory-ceiling-against-measured-whole-run-rss` (first seen 2026-09-21)
- `the-settlement-ceiling-can-move-now-that-its-curve-has-landed` (first seen 2026-09-21)
- `widen-membership-guarded-to-see-the-early-return-guard-so-the-surveys-bare-count-means-what-it-says` (first seen 2026-09-21)
- `ten-of-eighteen-premises-get-a-climate-normal-instead-of-the-worlds-weather` (first seen 2026-09-22)
- `the-ceilings-downstream-still-fits-a-value-that-never-shipped` (first seen 2026-09-22)
- `the-live-page-still-publishes-the-coin-flip-as-a-settled-no` (first seen 2026-09-22)
- `the-two-legs-that-bind-the-arm-are-nine-seeds-and-one-censored-funnel` (first seen 2026-09-22)
- `restore-the-six-live-reverts-before-anything-regenerates-from-them` (first seen 2026-09-22)
- `the-arms-page-cannot-say-whether-the-advantage-is-choosing-or-the-price-level` (first seen 2026-09-22)
- `a-shared-canonical-constant-with-three-consumers-and-no-leg-that-reds-when-it-narrows` (first seen 2026-09-22)
- `the-belief-ceiling-names-no-world-and-the-grader-never-stamps-one` (first seen 2026-09-22)
- `the-arms-error-bar-is-taken-over-a-different-book-from-the-figure-it-bounds` (first seen 2026-09-22)
- `four-declared-daemons-have-written-nothing-since-they-started` (first seen 2026-09-22)
- `the-companys-churn-belief-is-flat-across-the-book-where-the-world-responds-nine-fold` (first seen 2026-09-22)
- `the-three-thousand-pound-knee-under-the-whole-finding-has-no-origin` (first seen 2026-09-22)
- `advance-the-base-read-the-census-honestly-and-enact-the-two-decided-files` (first seen 2026-09-22)
- `publish-the-corrected-one-book-baseline-comparison` (first seen 2026-09-22)
- `unwedge-the-publisher-so-the-belief-reading-reaches-a-reader` (first seen 2026-09-22)
- `land-the-bill-stress-knee-refutation-before-it-is-lost` (first seen 2026-09-23)
- `how-to-read-this-is-the-one-truthiness-reader-and-it-withdraws-on-the-tie` (first seen 2026-09-23)
- `the-regeneration-check-clones-at-head-so-it-cannot-see-the-producer-edit-that-wedges-the-publisher` (first seen 2026-09-23)
- `the-refuted-bill-stress-knee-is-unbounded-beside-a-saturating-size-term` (first seen 2026-09-23)
- `the-belief-landed-and-every-artefact-downstream-still-describes-the-old-one` (first seen 2026-09-23)
- `grade-the-paired-size-term-floor-against-its-five-pre-registered-predictions` (first seen 2026-09-23)
- `the-published-floors-width-is-made-of-repeated-draws` (first seen 2026-09-23)
- `the-churn-belief-renderer-is-unstaged-so-the-site-lane-refuses-every-commit` (first seen 2026-09-23)

## Re-asked
- **2026-09-24** — re-asked: **still_holds**. observed 2026-09-23, within the 3-day bar.
