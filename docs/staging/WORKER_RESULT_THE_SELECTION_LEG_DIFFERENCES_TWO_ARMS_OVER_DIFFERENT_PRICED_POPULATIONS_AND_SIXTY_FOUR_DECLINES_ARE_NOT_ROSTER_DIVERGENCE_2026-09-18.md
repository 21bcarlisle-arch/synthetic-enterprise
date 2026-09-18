**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The selection leg differences two arms over different priced populations, and the sixty-four declines are not roster divergence

**Claim:** `the-selection-leg-is-negative-and-nobody-has-asked-which-customers-it-loses-on`
**Drawn parts:** ONE (blocked, evidence below) · TWO (already in force, refuted) · THREE (delivered)
**Read entirely off disk. Nothing was re-run.**

---

## The headline

`selection_gbp = value_advantage_gbp - level_advantage_gbp` differences an advantage earned over
**214 priced renewals** against one earned over **281 priced renewals**, on the same book, in the
same run. The gap is **67 renewals**, and **64 of them are renewals the value arm SAW and DECLINED
while the level arm priced them**.

The level arm's margin on those 64 sits inside `level_advantage_gbp` and is absent from
`value_advantage_gbp`, so it lands in the residual with a negative sign. The residual is published as
the worth of the choosing. It is not: it is the worth of the choosing on 214 renewals, minus the
whole level-arm margin on 64 renewals the chooser refused to price.

**So the answer to "which customers does the selection leg lose on" is: the 64 it never priced.**
Not a mispriced segment, not a discount to a customer who would have stayed, not a retention it
should have let go — a population the two arms do not share, differenced as though they did.

## The asymmetry is in the code, and it is one bound wide

`company/pricing/value_based_renewal.py`, `decide_margin`:

| | lawful ceiling (`max_offered_rate_gbp_per_mwh`) | churn support bound (`current_rate x 1.831`) | can it decline? |
|---|---|---|---|
| `FLAT_AT_LEVEL` (level arm), L806–854 | **CLAMPS** — `level = min(level, headroom)` | **never applied** | **no** |
| `VALUE_BASED` (value arm), L856–884 | **FILTERS** — `lawful = (m for m in candidates if ...)` | **FILTERS** — `allowed = (m for m in lawful if ...)` | **yes** — raises `MarginDecisionUnavailable` when `allowed` is empty |

A clamp always yields a price. A filter can yield nothing. The value arm declines exactly where no
candidate survives the conjunction of the two bounds; the level arm applies one of them, as a clamp,
and therefore prices every renewal it reaches.

The clamp's own comment says why it is there:

> *"an unclamped level would let it price where the value arm may not and reproduce exactly the
> confound that made the 2026-08-27 whole-book attempt return a 9.4x artefact."*

That reasoning was applied to the **lawful ceiling and not to the support bound**. The confound the
clamp was written to prevent is still live through the second predicate. This is the repo's own
catalogued shape — a guard extended to one of two ANDed bounds — and it is worth £3,900 a run.

## The measurement, nine same-world runs at the same level point

Every full three-arm artefact on disk at `level_gbp_per_mwh = 20.00` and world `39a192ce04c1eda8` —
the 18-seed family's own world and operating point:

| run | value priced | value declined | level priced | level declined | level_adv | £/priced |
|---|---|---|---|---|---|---|
| `s1_three_arm` | 215 | 65 | 281 | 0 | 17,125 | 60.9 |
| `s1_three_arm_20260908` | 214 | 64 | 281 | 0 | 17,468 | 62.2 |
| `s1_three_arm_20260908b` | 214 | 64 | 281 | 0 | 17,129 | 61.0 |
| `s1_three_arm_20260909` | 214 | 64 | 281 | 0 | 17,125 | 60.9 |
| `s1_three_arm_20260909b` | 214 | 64 | 281 | 0 | 17,125 | 60.9 |
| `s1_three_arm_20260909c` | 214 | 64 | 281 | 0 | 17,125 | 60.9 |
| `s1_three_arm_20260910` | 215 | 65 | 281 | 0 | 17,125 | 60.9 |
| `s1_three_arm_departure_20260909` | 215 | 65 | 281 | 0 | 17,129 | 61.0 |
| `current_book_2026-09-08` | 214 | 64 | 281 | 0 | 17,468 | 62.2 |

The level arm declines **zero** renewals in every run ever recorded. The value arm declines 63–65 in
every one. This is not seed-sensitive and it is not a property of the redraw.

**Scale.** 64 declines x ~£61 of level-arm advantage per priced renewal ≈ **£3,900–£3,980**. The
published selection residual is **-£959.78**. The population gap alone is **4.1x the magnitude of
the number it is being read as**.

> **The £61 is an average over the priced population and the declined renewals are NOT average** —
> they are where the support bound bites, i.e. where the base rate has risen far against the current
> rate. The figure is an order-of-magnitude bound on whether this mechanism is big enough to own the
> residual, and it is. It is **not** a point estimate of the declines' worth, and it must not be
> subtracted from anything. Naming what it counts is the point: it counts *level-arm advantage per
> renewal the level arm priced*, applied to a count of *renewals the value arm refused*.

What follows from the bound, and it is the part worth the director's attention: if the population gap
is worth roughly +£3,900 to the level arm and the published residual is only -£960, then **the
chooser is worth something substantially positive on the 214 renewals it actually prices** — the
instrument is currently netting that against a structural gap and publishing the difference as
"selection". The sign of the choosing on a like-for-like population has never been measured.

## The artefact already names a 67 and attributes all of it to the wrong cause

`decision_population` in every one of those runs publishes `largest_denominator_difference: 67` and
explains it:

> `the_mechanism`: *"Sequential A/B roster divergence. The arms are identical in eligibility —
> `renewal_margin_uplift` passes `flat_at_level` through every guard the value arm passes, so
> neither arm can see a renewal the other cannot. They differ in WHICH renewals still exist: a
> different price changes who churns..."*

> `why_this_is_not_a_defect`: *"Equalising the denominators would mean pricing renewals for customers
> who had already left, which is not a world any supplier operates in."*

**Both sentences are false for 64 of the 67.** The reconciliation, from the same block:

```
renewals offered     value 2035   level 2050   ->  15  genuine roster divergence (churn)
renewals logged      value  278   level  281   ->   3  reached the arm
renewals PRICED      value  214   level  281   ->  67  the published denominator gap
  of which declined  value   64   level    0   ->  64  = 96% of the gap
```

The eligibility claim is true and irrelevant: both arms *see* the same renewals. The value arm then
**refuses** 64 of them. Those customers had **not** left — the value arm met them and declined.
Equalising there does not mean pricing departed customers; it means the level arm should decline them
too, or the residual must exclude them.

And the licence the block grants is the one `level_vs_selection` takes:

> `what_a_reader_must_not_do`: *"Arm-level totals (net margin, treasury, enterprise value) ARE
> comparable — they are sums over the whole run and carry the roster difference inside them, which
> is the effect being measured."*

True of the roster difference. Not true of the declines, which are the arm's own decision and not the
world's, and which is 96% of what the totals carry.

`level_vs_selection`'s docstring makes the claim outright:

> *"`flat_at_level` applies ONE uplift to EXACTLY the renewals the value arm priced, through the same
> guards and under the same lawful ceiling, so the two arms differ by the CHOOSING and by nothing
> else."*

**281 against 214, on every run on disk.** "Exactly the renewals the value arm priced" has never once
been true.

## The next change to `company/pricing/value_based_renewal.py`

**Give `FLAT_AT_LEVEL` the support bound the value arm has, and let it decline.** In the branch at
L806, before `_score(level)`, apply the same `ceiling_from_support = current_rate x (1 + support_pct
/ 100)` test the value arm applies at L874, and raise `MarginDecisionUnavailable` with the same
reason when the clamped level does not survive it. One bound, in the branch whose comment already
argues for exactly this treatment of the other bound.

That makes the two arms' priced populations equal by construction, and `selection_gbp` becomes the
quantity its own docstring already claims it is.

**Three things that must travel with it, and they are why I have not made the change in this turn:**

1. **It moves the LEVEL leg, which is the published +£19,277 at 63 sems.** Removing ~64 priced
   renewals from the level arm changes the one figure on the page that currently states a sign
   confidently. That is a director-visible change to a published headline and it should land as a
   deliberate step, not as a side effect of a finding.
2. **It changes the value-arm file set**, so every family drawn before it is unpoolable with every
   family drawn after. `longjob-floor-next12-20260917` (PID 3819244) is mid-flight and would be
   split by it. Land it *after* next12 lands, or knowingly spend that run.
3. **The control must key to the property, not to today's answer.** The honest control is
   `value_arm.priced == level_arm.priced` in `decision_population` — it reds today, which is correct
   and which is why it must land *with* the fix and not before it, in a tree several lanes are
   committing to.

## Part ONE — blocked, with the evidence

Not done, and it cannot be done in this invocation. The `next12` draw is **still running**:

```
PID 3819244  elapsed 21369s (5.9h)  at 2026-09-18 00:07 UTC
  python3 -u -m tools.run_value_cycle_ab --noise-floor-seeds 3100001..3100012
     --redraw-mode all --redraw-key elasticity
     --out /var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json
```

The output path **does not exist yet**. The corrected ETA the drawn item carries — 2026-09-18
11:31:24 — is ~11.4 hours after this turn, and the item's own ETA arithmetic is confirmed by the
elapsed time. There is no partial family to read alone, so its mean, sem and sems-from-zero cannot be
reported and are not guessed at here. **The item's instruction to read it before folding stands and
is untouched.**

## Part TWO — the remedy is already in force, and it reaches the reader

The drawn item asks that the page "state plainly that the two figures come from different families".
`origin/main` already does, in the payload and in the pixels:

- `tools/generate_value_arms_data.py::_family_discrimination` returns
  `state: "asked_and_unanswerable"` for the eighteen and republishes the fold's own refusal verbatim.
- `_auc_against_its_own_null(..., is_the_advantages_family=False)` labels the reading
  `source: "the 3-seed AUC-carrying floor of 2026-09-17"` and
  `is_the_family_the_advantage_is_bounded_over: false`.
- `site/data/value_arms.json` carries the sentence: *"measured over a DIFFERENT family from the one
  the advantage above is bounded over (the 3-seed AUC-carrying floor of 2026-09-17), so it bounds
  nothing on this page"*, with the exact null (0.3870–0.6130, p=0.231) and `demonstrated: false`.
- `site/capabilities/index.html::familyDiscrimination` renders it on **every** branch, refusal
  included, via `ownNull(d.against_the_statistics_own_null)`.

No work was owed. The other half of the item's part TWO — *"compute the auc for the seeds whose
artefacts permit it"* — is **not reachable**: the 18 rows predate the field entirely
(`seeds_carrying_an_auc: 0`), and the floor discards the per-seed `result` after writing its row, so
no re-derivation from disk is possible at any sample size. That is the fold's own stated reason and
it is correct.

## One thing I could not do, and the drawn item assumed I could

> *"the per-seed and per-account arm values are ALREADY in the run artefacts"*

**Per-seed, yes. Per-account, no.** `noise_floor` (L5520–5580) writes one row per seed carrying
`value_advantage_gbp`, `level_advantage_gbp`, `selection_gbp`, `level_share_of_advantage` and the
draw counts — and discards the full `result` dict. No floor artefact on disk carries a per-account
figure for any arm. The richest per-account data anywhere in the tree is:

- `churn_roster_diff.only_in_value_arm` — **4 accounts**, and against the **control** arm, not the
  level arm (`C5_2` £1,176.78, `PROS-2019-0024` £345.63, `PROS-2021-0324` £322.73, `SYN-2016-034`
  £182.81)
- `method_skill.scored_sample` / `dropped_sample` — **20 rows each**, samples, not populations
- the **64 declined accounts are named nowhere**

So "name the customers" is answerable today only as a *population* — the 64 the value arm declines —
and not as a roster of ids. **That is itself the repair the decomposition needs**: `value_arm_log`
already holds one entry per renewal with `declined` set, and the runner throws it away. Emitting the
declined accounts (id, term start, base rate, current rate, and the level arm's realised margin on
each) would turn the £3,900 order-of-magnitude bound above into an exact figure, from one run, with
no family and no re-draw. That is the cheapest next measurement in this whole line of work and it is
a change to `tools/run_value_cycle_ab.py`, not to the pricing arm — so it does not split the family
and can land while next12 is in flight.

## Corrections to my own work in this turn, kept beside the claim

- I first read the 64 declines as a *candidate* mechanism and was about to attribute the negative
  residual to them directly. The nine-run table refutes that as stated: the declines are **constant**
  at 63–65 across runs whose `selection_gbp` ranges from -£335 to +£1,192, so they cannot explain the
  *variance* and they are not what moves the sign seed to seed. What they own is the **level**: a
  structural, always-present offset inside the residual. The corrected claim is the one above — the
  residual is not a selection effect at all, because it is not taken over one population.
- I took `decision_population.the_mechanism` at face value on first read and nearly filed the
  denominator gap as known-and-dispositioned. The reconciliation arithmetic in the same block refutes
  its own prose, 64 of 67.

## What is in this document that a control cannot yet see

Nothing here is enforced. The three named next steps — the support bound on `FLAT_AT_LEVEL`, the
`priced == priced` control, and the declined-account emission — are the repair, and they are
sequenced against next12 above rather than taken now.
