# The headline concordance is the estimand now, and the withheld reason had two homes in one field

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Lane 0 delivery, 2026-09-23.** Item: `the-headline-verdict-is-the-survivor-cut-not-the-estimand`.
Subject: `tools/generate_value_arms_data.py` and `site/capabilities/index.html`.

## The duplicate-work check, answered first

The draw flagged one live claim on the same file —
`how-to-read-this-is-the-one-truthiness-reader-and-it-withdraws-on-the-tie`. **It is genuinely
different work on the same subject**, so this one carried on. That lane holds three hunks in
`tools/generate_value_arms_data.py` (`_NO_STAMP_THIS_PAGE_COULD_READ`, the `_how_the_two_runs_order`
format defaults, and the `how_to_read_this` truthiness split at base line 14358); this item touches
none of them. Landed with `isolate_hunks --keep` + `surgical_land --content`, so their in-place
edits stayed in the tree and out of this commit.

## What was wrong

**1. The published headline answered a narrower question than its caption.**
`method_skill.concordance` — 0.482 on 54 decisions — led the method block under *"Does the method
work?"*. The block's own `survivorship` split says all 44 decisions that figure could NOT score are
renewals the world recorded as departures, and that **not one scored decision is**. So the figure a
reader met first answers *"given the household stayed, did the arm's price rank the joint value?"*,
and its own text says a larger book does not fix it. The estimand that does answer the caption —
`method_skill.fixed_horizon.every_priced_decision_pounds_outcome`, 0.4396 on 85 decisions, null
0.412–0.588, p 0.1836 — was already computed, already in the payload one key away, and points the
unflattering way. One concept, two populations, the split chosen before the definition, with the
flattering cut published as the headline.

**2. `headline` carried the same ~1,000-character paragraph twice, verbatim.** `_seed_spreads`
withholds every bound on a clock for ONE reason; `_selection_sentence` composes TWO refusals from
it; both legs were withheld on the published run. `_cannot_resolve`'s own docstring had already
argued the rule for the REMEDY — *"a remedy stapled to each printed the same forty words twice in
one paragraph"* — and the reason was left behind when the remedy was lifted to the caller. A
half-finished repair, not an oversight of a different kind. 4,514 characters → 3,273.

## What changed

* `_skill_reading_order` returns the two cuts **as a list in publication order**, unconditioned
  first. The ordering is now a property of the PAYLOAD, measurable where the populations are known
  — it was previously a property of which paragraph was typed first in an HTML file, which no
  control over the producer could see.
* Each row carries its own `concordance`, its own null, its own n, its own accounts, and a sentence
  naming its population. Nothing differences them; `not_combined` says so on the surface.
* The conditioning clause is **read** off `survivorship.the_concordance_is_conditioned_on_survival`,
  three-valued. `cannot_tell`'s subject is derived the same way — it read *"whether this method
  carries any information"* (the unconditional question) on the conditioned cut for a month.
* Fail-closed: a run with no estimand leads with the survivor cut and **says why**, naming
  `fixed_horizon`'s own reason. A page that reverted silently is indistinguishable from one that
  checked.
* `_once` + `_withheld_spread_reason`: the withheld reason is a TAKE handed to whichever refusal
  reaches it first, not a flag. A flag would have to re-derive `_arm_vs_control_clause`'s gate in
  the caller — a second copy, drifting on first touch. The second leg still refuses (*"Its
  DIRECTION is not stated here either, and for the same reason"*) and does **not** fall through to
  *"no seed spread has been measured"*, which would name a cause nobody observed.
* `site/capabilities/index.html`: `readingOrder()` renders the feed's order; `fixedHorizonBlock`
  gates its estimand verdict on `reading_order.the_estimand_verdict_is_in_the_lead` so the sentence
  has one home. A feed with no ordering still renders its figure with its interval.

## What a reader now meets first

> Over EVERY decision the arm priced — 85 of them, scored on the joint pounds each one actually
> produced within 365 days of its own term start, a household that left counting the nothing its
> term produced rather than dropping out of the sample — the arm's own price ranks that value at
> **0.440**, against 0.5 for a signal carrying no information, and between 0.412 and 0.588 is where
> a signal carrying no information lands on those 85 decisions across 59 accounts (two-sided
> p 0.18).
>
> On whether the arm's price ranks the pounds EVERY decision it priced produced, **we cannot tell**.

The 0.482 survivor cut follows, in a sentence that names why it is conditional on survival.

## The gate refused my first draft, and it was right

`test_every_undriven_pointer_is_true_from_the_region_it_lands_in` red:

> `_skill_sample_size_explanation:6942 'beside this' points at something that renders nowhere on
> this door`

The first draft COPIED each reading's "we cannot tell" onto its row. The words still reached the
reader — and `.method_skill.cannot_tell`, the field that OWNS that sentence and the registered
referent of `_skill_sample_size_explanation`'s *"the figure beside this"*, then rendered nowhere.
A reader following that pointer would have found nothing. **One sentence under two keys is the same
defect this whole item is about, one rung down, and I wrote it into the repair.**

Repaired by having each row NAME its verdict (`verdict_key`, relative to `method_skill`) and the
page resolve it at render. `test_a_readings_verdict_is_NAMED_and_never_copied_onto_the_row` is the
control that keeps it that way. Worth recording plainly: nothing I reasoned about caught this; the
census did, on a branch I had driven and looked at.

## Controls, and the mutations that prove they can fail

`tests/tools/test_the_unconditioned_estimand_leads_the_reading_order.py` (7 legs) and three new
legs in `site/test_the_baseline_comparison_reaches_the_reader.py`.

| Mutation | Leg that fired |
|---|---|
| `readings: [survivor, unconditioned]` | `test_the_unconditioned_estimand_is_the_reading_a_reader_meets_first` |
| `said = withheld_because` (reason printed per leg again) | `test_one_withheld_reason_reaches_the_headline_once_and_both_legs_still_refuse` |

Both reverted, verified by sha1. The ordering leg is keyed to `conditioned_on_survival is False`,
**not** to the key name or to 0.4396 — the day the estimand clears its null it still leads, and the
day a third cut lands it still leads.

The door legs are driven through the REAL producer (`_skill_reading_order` composing from the
published block), because the published feed predates the ordering and the live rung exercises the
fallback. Without that the ordered branch would have shipped unseen.

## What is NOT done

`site/data/value_arms.json` was **not** landed. It is not in `published_feed_regeneration_check
.COVERED_FEEDS`, its working copy is another lane's 08:05 regeneration (which independently dropped
the `churn_belief_size` block), and landing it by pathspec would have made that drop mine. The
publish lane regenerates it; the page's fallback keeps the current published feed rendering
correctly until it does, and the ordered branch is proved by the door legs above. **So the LIVE
page shows the new order only after the next regeneration of that feed.**

## A red I did not cause

`tests/architecture/test_static_quality_ratchet.py` is red on F401 264 → 269. Measured per dirty
file: the whole delta is `tools/refresh_to_head.py` (HEAD=1, working tree=7), another lane's
in-flight edit. None of this item's three Python files carry an F401.
