**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery (`a-floor-family-that-carries-its-own-discrimination-auc-per-seed`)

**Knowledge:** none new. No domain constant moves. One published statistic gains a ruler that was
always computable from a field already travelling beside it; nothing is invented.

# The AUC is measured for the first time, it does not clear its own null, and the floor family is the wrong ruler for it

Delivery seat, 2026-09-17. Scores
`docs/staging/records/SEAT_PREREG_WHAT_DOES_A_FLOOR_FAMILY_THAT_CARRIES_ITS_OWN_AUC_ACTUALLY_BOUND_2026-09-17.md`
(landed `201a6e44d`), written before the fold was run and unedited. **All four predictions hold.**

---

## The answer to the thesis question

The director's thesis is that the advantage must come from INFERENCE and never from ACCESS. This is
the first time the inference half has a figure with a ruler beside it. It reads:

| | n | figure | ruler | verdict |
|---|---|---|---|---|
| **level** leg (a flat rule, no per-customer view at all) | 21 | **+£17,480.98** | sem £1,037.72 → **16.85** sems from zero | **POSITIVE, determined** |
| **value** leg (what the arm beat the control by) | 21 | **+£17,264.08** | sem £872.20 → **19.79** sems | **POSITIVE, determined** |
| **selection** leg (what the inference itself was worth) | 21 | **−£216.90** | sem £428.73 → **0.506** sems | **no sign** |
| **discrimination AUC** (does the belief rank who leaves?) | 3 | **0.5697** | null sd **0.0576** → **1.21** null sds above 0.5 | **NOT demonstrated** |

**The demonstrable advantage is still the PRICE.** The inference half now has a reading rather than
a blank, and the reading is that the arm's belief about who leaves cannot be shown to carry
information: 0.57 on a population of 64 retained against 42 left is 1.21 standard deviations of its
own no-information null above a coin flip, and the bar is 2. That is not "the AUC is 0.5" — it is
"this sample cannot tell 0.57 from 0.5", which is a different and weaker statement than either
half of the thesis needs.

This is published as it reads. It is not a cue to re-draw until a seed agrees.

---

## The predictions, scored

**P1 — CONFIRMED. The drawn item's central claim is false.** The item states that
`error_bar.discrimination_across_the_family` "moves from state=asked_and_unanswerable to
state=measured ... with no code change". It does not. Folding the new AUC-carrying run into the
published family gives:

```
"available": false, "seeds_carrying_an_auc": 3, "seeds_in_family": 21
```

`_auc_across_seeds` fails closed on a single row without an AUC, by design and for a stated reason,
and 18 of the published family's rows have none. **Folding cannot answer this question at any
number of new seeds** while the published family keeps its pre-2026-09-17 members. The state moves
to `measured` only if the published family is REPLACED by one all of whose rows carry the figure —
which today means dropping the advantage legs from 21 seeds to 3, and buying a `measured`
discrimination block at the price of the leg the page's whole claim rests on. Held: that trade is
refused here, for the reason `NOISE_FLOOR_PATH`'s own comment gives about the wider-sampled figure
belonging in the flattering position.

**P2 — CONFIRMED, and this is the load-bearing finding. The elasticity floor cannot put an error
bar on the AUC, because the redraw does not reach it independently.**

| seed | `discrimination_auc` | `auc_population` | value adv |
|---|---|---|---|
| 1234567 | 0.5649181547619048 | 64 / 42 | £10,217.83 |
| 2345678 | 0.5649181547619048 | 64 / 42 | £10,217.83 |
| 3456789 | 0.5793650793650794 | 63 / 42 | £6,319.59 |

Two of the three seeds returned the AUC **identical to sixteen decimal places**, with identical
populations and identical total advantage — the elasticity redraw flipped no departure at all in
those two, so the rank statistic could not move. Only one of three draws is an independent draw of
this quantity.

The consequence is a number, not a worry. The family's own standard deviation is **0.00834**. The
statistic's no-information null standard deviation on its own population is
`sqrt((n1+n2+1)/(12·n1·n2))` = **0.0576** at 64×42. **The floor family's spread is 6.9 times
narrower than the statistic's own null.** Publishing it as "the AUC's error bar" would have put the
tightest and most misleading interval on the page — and it would have been the same shape as the
figure this page already retracted on 2026-08-30, where the same estimator scored 0.646, 0.672,
0.465, 0.465 and 0.130 across five runs in four days (a run-to-run sd of roughly 0.22, which an
elasticity floor reproduces none of).

So the drawn item's premise — "a floor family is the only thing in this repo that draws it more
than once" — is true as written and wrong in what it implies. The family draws the AUC three times
and draws it **once independently**. A floor over `elasticity` is the wrong instrument for this
statistic, and no number of seeds repairs that: the redraw key does not reach the quantity.

**P3 — CONFIRMED.** 0.5697 against a null sd of 0.0576 is 1.21 null sds above the no-information
point. Below 2. Registered before it was computed because it is the unflattering answer.

**P4 — CONFIRMED to the penny, and it matters to another lane right now.** Three new seeds moved
the selection leg from **1.798** sems from zero (18 seeds, mean −£624.13, sem £347.16) to **0.506**
(21 seeds, mean −£216.90, sem £428.73). The distance to a sign did not close — **it collapsed**,
because the three new draws raised the mean toward zero AND widened the spread (sd £1,472.89 →
£1,964.67, one of them an outlier at +£5,823.40). The sign count went 9/18 positive to 12/21.

**This refutes the forecast the sibling claim is acting on.** `seeds_needed_to_state_a_sign: 24`
was computed holding this family's mean and standard deviation fixed, and the artefact's own
`distance_to_a_sign.what_this_count_is` says so in words: *"the seeds this family would need IF its
mean and standard deviation stayed exactly where they are. New draws move both."* Three draws
moved both, in the direction that costs seeds. `longjob-floor-next12-20260917` is in flight as this
is written (launched 18:11:33Z under
`the-selection-leg-is-six-seeds-short-of-a-sign-and-its-point-estimate-is-negative`) drawing twelve
more. Twelve more seeds may well not close it either, and the count that says they will is not a
forecast. **Whatever comes back is the answer and gets published as it reads.**

---

## A second defect the fold surfaced, for whoever refolds next

Folding into the PUBLISHED family **loses the book the new run names**. `folded18` declares no
served book (it was folded from `..._20260909b.json`, which carries no `book_identity` block at
all), so `_book_identity` refuses on `folded18` itself and the 21-seed family states no book —
even though the new run declares `['resi', 'SME']` resolved from the curriculum.

The book-carrying route exists and is on disk: **`..._20260910.json` + `..._20260910b.json` +
`..._auc3_20260917.json`**. `..._20260910.json` is a re-run of the same nine seeds as `..._20260909b`
under a different tree (`4e7938f67`), and unlike `0909b` it **does** carry a book block declaring
`['resi', 'SME']`. Every member of that triple names the same book, so that fold publishes a family
that can show what it was drawn over. Not done here: it is inside the sibling claim's stated scope
(its item names this exact defect) and its `next12` run will change which members belong anyway.

---

## What landed

- `docs/observability/value_cycle_ab_s1_noise_floor_auc3_20260917.json` — the 3-seed AUC-carrying
  floor. 3h50m of compute (16:21→20:11 BST), world `39a192ce04c1eda8`, mode `all`, key
  `elasticity`, clock `settled-realised`, producing commit `c9bd2eae7`, rc=0. **It existed only in
  `/var/tmp` until this commit**, which is the `uncommitted_and_orphaned_work` class exactly: the
  one artefact in the repo that carries this statistic per seed, unreachable by any commit.
- `background/launch_liveness --check` settled `floor-auc-20260917`, which had claimed `live` since
  15:22:22Z and finished at 19:11:44Z.
- The folded 21-seed family is **deliberately not committed**: it is reproducible in seconds
  (`python3 -m tools.fold_noise_floor_family --out <p> docs/observability/value_cycle_ab_s1_noise_floor_folded18_20260917.json docs/observability/value_cycle_ab_s1_noise_floor_auc3_20260917.json`),
  it is wired to nothing, and `next12` is about to supersede which members belong in it. Its
  figures are in the table above.

## What this turn did NOT do, and what should happen next

**The reading above is in this document and not on the page.** Putting it there is a code change,
which the drawn item said would not be needed and P1 shows is needed. The change is small and it is
the right one:

`_family_discrimination` in `tools/generate_value_arms_data.py` should, when the family spread is
unavailable, publish **the per-row null reading** instead of only a count — because
`sqrt((n1+n2+1)/(12·n1·n2))` is computable from `auc_population`, which already travels with every
row that carries an AUC. That ruler needs **no family at all**: it is available at one seed, it is
the statistic's own null rather than a redraw's spread, and it is precisely what this page's
2026-08-30 retraction demanded ("composed from the figure's own exact null interval and states the
endogeneity at any sample size"). It also means the floor family's spread should NEVER be published
as this figure's interval, on P2's evidence — a guard worth writing as a control, because the
tempting version of this repair is the one P2 just refuted.

`tools/fold_noise_floor_family.py` was deliberately **not touched** this turn: the sibling claim
holds it and is mid-flight on it.
