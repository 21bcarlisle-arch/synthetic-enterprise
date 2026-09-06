**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: three of `fuel_mix`'s eight unproved contracts now die, and the fingerprint they were asked for no longer exists

**Measured 2026-09-06 07:29–07:38 BST, shared tree at `eaac64f49`. Claim
`fuel-mix-M3-to-M10-are-proved-by-nothing`. Instrument
`python3 -m tools.grid_intensity_feed_contract_battery --only M5 M6 M8 --suites explore_carbon`.
Results `/var/tmp/grid_intensity_fuel_mix_M5_M6_M8_AFTER_controls_d892342119e8.json`, log
`/var/tmp/fuel_mix_M5_M6_M8_after.log`. Exit 0, subject restored (`git status` clean on
`tools/generate_grid_intensity_feed.py` after the run).**

## The premise check, which found one half of the item spent and the other half live

The drawn item says to re-run three rows **at fingerprint `d7eb36a0b901`**, and reasons from it:
*"Adding controls does NOT move the fingerprint — so the new rows are directly comparable to the
landed ones."*

**That fingerprint no longer exists.** The live one is **`d892342119e8`**, and it moved before this
lane touched anything. The reasoning in the item is still correct and the conclusion it supports is
still available — but not for the reason it gives, so it is set out here rather than assumed.

`tools/contract_battery.fingerprint` hashes a payload of the spec's *declarations*. Three keys were
added to that payload after `03387ff1e` — `direct_nodes`, `mixed_nodes` and `repair_suite`, at
`35109bb09` and after — and **adding a key to the payload re-fingerprints every spec in the family
at once**, including specs that do not use the new field and whose runs are byte-for-byte the same
work. The engine then fails closed on the old results file (`stored fingerprint … this spec …`,
*"its rows are not evidence"*), which is right, and the cost is that every result document in this
family that cites a fingerprint now cites one no live run can reproduce.

**What makes the rows comparable is therefore not the fingerprint. It is this, measured rather than
asserted:** every field of the hashed payload that describes what a run *does* — `suites`,
`direct_suites`, `control_suites`, the eleven mutations' ids and their `old`/`new` text, the poison
pair and the null pair — is **identical between `03387ff1e` and now**, checked by executing the
spec module as it stood at that commit and comparing member by member. All six compare equal. The
three keys that moved the hash are the three the spec does not populate.

> **A fingerprint that hashes the engine's field LIST, not only the spec's content, expires every
> landed grid in the family the moment the engine gains a field — and it expires them for a change
> that cannot alter one cell.** Filed here rather than as its own document because it is a property
> of this measurement and its remedy is a judgement about the instrument, not a repair anyone can
> make blind: fail-closed is the right default and versioning the payload would weaken it.

## What was built

Three controls in `tests/tools/test_grid_intensity_feed_and_explore_carbon.py`, the subject's own
direct suite, each naming the battery row it closes:

| row | the contract | the control |
|---|---|---|
| M5 | the THERMAL FLOOR reaches the published feed | `test_the_THERMAL_FLOOR_the_MIX_MEASURES_reaches_the_published_feed_and_MOVES_the_series` |
| M6 | the ZERO-CARBON MUST-RUN block reaches the published feed | `test_the_ZERO_CARBON_MUST_RUN_BLOCK_the_MIX_MEASURES_is_the_ONE_THE_FEED_PUBLISHES` |
| M8 | the BIOMASS ENVELOPE is returned | `test_the_BIOMASS_ENVELOPE_the_MIX_MEASURES_reaches_the_published_feed_TO_THE_LATEST_YEAR` |

They share one module-scoped fixture that does **one real publish off the real caches** — `fuel_mix()`
on 235 MB of outturn, then `generate()` to a `tmp_path` — because the gap they close is exactly the
stretch between the two: the controls that existed proved that an unusable *cache* raises out of
`fuel_mix()`, and that `build()` renders an envelope *handed to it*. Between those sits the tuple,
and a member replaced by `{}` on the way out satisfies both.

Each control has a coverage leg and a materiality leg, and both had to be measured at real inputs
before they were written, not after:

- **M5** — the published `thermal_floor_mw` covers **exactly** the years `by_year` covers (keyed to
  the feed's own coverage, so it survives the record extending); each row's `floor_mw <= p1_mw` over
  a positive `half_hours`; and knocking the floor out of the publishing call changes the series,
  with the published records carrying the *with-floor* shape.
- **M6** — the must-run block is the one correction with **no published field of its own**
  (`zero_carbon_must_run_coverage` is a different member of the tuple), so the only place its loss
  is visible is the series. The control asserts the block covers half hours the feed actually
  prices, that the with-block and flat shapes differ, that the records are the with-block one **and
  that they are not also the flat one** — the last leg being the one that stops the control passing
  when it cannot tell the two apart.
- **M8** — the envelope covers a subset of the published years and reaches the **latest** of them
  (the first year is deliberately not asserted: the biomass cache starts after the demand record
  does, and pinning that would key the control to today's coverage rather than to the property),
  with `floor <= p1 <= mean <= p99 <= capacity` on every row.

Printed at real inputs first, before any test was written: all **959** published records match the
shape built with the corrections, and all **959** would have been published differently under the
flat must-run block. Both legs discriminate; neither is a formula shipped unprinted.

## The grid

Three rows, the subject's own direct suite, all four floors run:

| round | result |
|---|---|
| BASELINE | `rc=0 failed=0`, **29.7s** — the data-present timing (this file is under a second with no `sim/cache/`), so nothing below is a vacuous pass |
| POISON | `explore_carbon` **reaches the subject** (0.9s); both control suites stayed GREEN, so the floor discriminates |
| NULL | `behaviour only` — no kill below is the suite reading the subject's bytes |
| M5 | **DIED** (26.5s), by `…::test_the_THERMAL_FLOOR_the_MIX_MEASURES_reaches_the_published_feed_and_MOVES_the_series` |
| M6 | **DIED** (30.0s), by `…::test_the_ZERO_CARBON_MUST_RUN_BLOCK_the_MIX_MEASURES_is_the_ONE_THE_FEED_PUBLISHES` |
| M8 | **DIED** (33.3s), by `…::test_the_BIOMASS_ENVELOPE_the_MIX_MEASURES_reaches_the_published_feed_TO_THE_LATEST_YEAR` |

`held_through_run: true` on all three; no `error` on any. Each row names exactly one killing node,
and it is the control written for it — not a neighbour reddening for an unrelated reason.

## What this does NOT establish

- **`survived_all` is still `null` on all three rows.** This run graded ONE suite by choice, so all
  eight callers are `ungraded_callers` and `killed_by` is `[]`. The verdict field reads
  `PROVED ONLY BY THE SUBJECT'S OWN SUITES (no caller kills these): ['M5', 'M6', 'M8']`, which is
  the honest statement and is a promotion from *killed by nothing*, not from *unproved by callers*.
  **Nothing here changes the finding that `fuel_mix` has exactly one caller whose suite can go red
  for it and that suite proves none of its contracts.**
- **M3, M4, M7, M9 and M10 are untouched.** Five of the eight remain killed by nothing. They were
  outside the drawn work and are not implied by it.
- **A control proved by the subject's own suite is the weaker of the two kinds** this sweep exists
  to tell apart, and these three are that kind. What they buy is that a silent revert to the 2024
  shape now reddens *something*; what they do not buy is a caller that would notice.
- **The three rows were run against ONE suite**, so this is not a re-grade of the landed 99-cell
  grid and must not be read against it as if it were. The landed file at `d7eb36a0b901` is the
  BEFORE and stays as it is; this file at `d892342119e8` holds three AFTER cells and nothing else.

## Beside the claim: a tree red that is not this lane's

`tests/architecture/test_static_quality_ratchet.py::test_ruff_no_stale_baseline_entries` and
`::test_ruff_baseline_matches_frozen_census` are RED in the shared tree — `I001: baseline 1326, now
1325`, the *stale* direction (the tree is better than the frozen floor). **It is not this change:**
the edited file yields 0 `I001` findings both at HEAD and after the edit, checked directly. It is
another lane's uncommitted improvement with the baseline not yet lowered, and lowering it from here
would freeze a floor that only holds while their unlanded work is in the tree. Left for the lane
that earned it; this work landed by `tools/surgical_land`, which gates the commit the tree *would*
create rather than the tree.
