**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# RESULT — the settled book is chosen for difference and carries per-account weights, and 4 of 10 predictions failed

**Filed 2026-09-11, delivery seat.** Graded against
`SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_2026-09-11.md` (P1–P7)
and `SEAT_PREREGISTRATION_WHAT_FORCING_THE_YEAR_MARGINAL_COSTS_THE_DEMAND_AXES_2026-09-11.md`
(P8–P10). Both were filed and landed before the arms they grade were run.

---

## The headline

The systematic 1-in-5.57 count cull is replaced. The settled book is chosen for difference over
four demand axes and every settled account carries its own weight in the company's own wins.

```
seed 42, origin/main    ARM A  cull      ARM B  chosen+weighted
settled accounts          90                84
customer-years          1195.4            1197.0   (ceiling 1200.0)
worst-axis KS            0.12798           0.08241  →  1.553x
distinct fabric vectors     47                59    (of 109 in the population)
per-account inflation      5.57 flat        0.057 – 14.774  (259.7x spread)
worst per-year error     0 by construction   0.1%  (fitted, and can fail)
```

## The grading — 6 hold, 4 fail

| | prediction | measured | |
|---|---|---|---|
| **P1** | worst-axis KS ratio ≥1.25×, kill below 1.10× | **1.553×** | **HOLDS** |
| **P2** | distinct fabric vectors ≥70 | 59 | **FAILS** |
| **P3** | every year within ±25% | +84.9% on 2017 | **FAILS** |
| **P4** | 80–100 settled, ceiling never crossed | 84, 1197.0 of 1200.0 | **HOLDS** |
| **P5** | weight spread ≥3.0× | 259.7× | **HOLDS** |
| **P6** | \|Δ margin\| > 1.0% | **not measured** | **WITHHELD** |
| **P7** | null case byte-identical | identical but for two added keys | **HOLDS, corrected** |
| **P8** | every year within ±5% after the repair | 0.1% | **HOLDS** |
| **P9** | P1 falls into 1.20×–1.45× under the constraint | **1.553×** | **FAILS** |
| **P10** | dropping the duplicate axes moves P1 by <0.15× | +0.109× | **HOLDS** |

**P2 failed because the question was asked as a count and the answer is a share.** The 502
candidates contain only **109 distinct fabric vectors between them** — a ceiling I had not measured
when I wrote the band. Arm B holds 59 of those 109 in 84 accounts (54%) against arm A's 47 (43%).
≥70 of 84 was never available on this base's coarse homes.

**P3 failed and it was a real defect, now repaired.** `customer_years` as one CDF axis among the
others reconstructed 2017 at **+84.9%** of its funnel wins while the campaign total was exact —
a correct headline over a false growth curve. The repair makes the year marginal a *constraint*
(`fit_weights(groups=...)`) rather than an axis. P8 grades the repair at 0.1%.

**P9 is the interesting failure: I over-predicted what the constraint would cost.** I predicted
forcing ten year rows would pull P1 down into 1.20×–1.45×. Measured within one axis set:

```
4 axes, NO year rows   worst-KS 0.07808   ratio 1.639x   worst year error 72.8%
4 axes, year rows      worst-KS 0.08241   ratio 1.553x   worst year error  0.1%
```

The constraint cost **5.2% of the ratio** and bought year reconstruction from 72.8% error to 0.1%.
I reasoned that mass forced onto the year marginal is mass unavailable to the demand axes, which is
true, and I was badly wrong about the magnitude — the year marginal and the fabric axes are close
to orthogonal here, so satisfying one barely constrains the other. **That is a fact about this
population I did not know and could not have argued my way to.**

**P7 holds and its wording needed correcting.** A campaign that fits inside its budget takes
neither path: rate 1.0, all 502 winners in the same order, no settlement note, every pre-existing
field identical. It is *not* byte-identical in the strict sense — `by_year` rows gained
`settlement_weight` and `settlement_selection`, and the outcome gained `settlement_selection` and
`settlement_weights`. Under the null those are 1.0, `"uniform_count"` and all-ones respectively.
Additions, not changes, and I should have written the prediction that way.

**P6 is WITHHELD rather than reported.** Measuring the P&L requires the full run, which did not fit
this turn beside the defect found in §"what a control caught" below. **It is the first thing the
next turn should take, and until it is taken nobody should claim this change is P&L-neutral or
P&L-positive.** The composition of the book moved materially — 84 accounts instead of 90, chosen
from different homes — so the margin has certainly moved; by how much is unmeasured. Recording
that `0d86d6dfe` predicted the same band for a comparable change and measured −0.37%.

## The defect no test would have caught, and the one a test did

**Three of my six axes were the same number.** `volume_m3`, `solar_aperture_m2` and
`internal_gain_kw` returned identical KS to five decimal places in both arms. Read off
`fabric_parameters`, they are `area × _STOREY_HEIGHT_M`, `area × _WINDOW_AREA_RATIO ×
_SOLAR_TRANSMITTANCE × _FRAME_FACTOR` and `area × _INTERNAL_GAIN_W_PER_M2 / 1000` — one quantity in
three units, by construction, on every base. Carrying all three weighted floor area **three times
against infiltration's once**, so the book was chosen for difference in *size* while every sentence
about it said *behaviour*. Caught by printing the table at real inputs; the arm still beat its
counterfactual by 1.53× while carrying the defect, so no test I would have written would have
failed. `test_no_two_choice_axes_are_the_same_quantity_in_different_units` is the control that now
would, keyed to correlation over a real spread of dwellings rather than to today's axis list.

**And a year with no chosen account has a structurally zero bar.** The weights are solved over the
chosen accounts only, so a year none of them belongs to has no column to put mass on — its
published figure is zero whatever the company won, and no fitting can move it. **On the real
campaign all ten years happened to be covered and this never appeared.**
`test_the_sample_is_PROPORTIONAL_in_every_year_and_not_merely_non_empty`'s ten-year fixture put
2022's 40 funnel wins against an estimate of **0.0** on the first run after wiring.
`_with_year_cover` now adds the medoid of any year the chooser left out, before the cost is
priced — medoid and not cheapest, because cheapest would load every covered year onto its shortest
tail, which is the first-come bias the two-pass design exists to remove.

## Two existing controls were re-keyed, and neither was deleted

**`test_the_sample_is_PROPORTIONAL_in_every_year...`** asserted `wins / rate` tracks `funnel_wins`.
What it is FOR is that no year is over- or under-represented in what the page reports the company
won; under the cull the count *was* the estimator. It is now keyed to `settlement_weight`, which
equals `wins / rate` under the cull — the same claim on both branches and a strictly wider one.
Keyed as it was, it would have gone red on a design that reconstructs the years *better*.

**`test_the_same_prospects_win_with_and_without_the_stock`** asserted the settled ids are identical
with and without the world's premise stock. Half of that is now false by design — the settled book
is deliberately a function of the homes. The half it existed for is still true and is now asserted
directly: the **company's** quotes, spend and funnel verdicts are identical, because our settlement
ceiling is invisible to the company by construction. *My first repair of it assumed the no-stock
arm would fall back to counting. Wrong: `iter_prospects` mints a premise when handed no stock, so
both arms choose and the books differ because the homes differ.*

## What the page can no longer say

Two published sentences asserted the sample is **uniform** and one told the reader to **divide by
the rate**. Both are false of a chosen sample, and the divide instruction is the dangerous one: it
is an arithmetic a reader can carry out that returns a wrong number silently. Both selections give
a rate below one, so this cannot be inferred at the page — `settlement_selection` is carried from
the campaign through `live_population` and `generate_book_growth_data` to the feed, and the page
branches on it.

**THE PAGE CHANGE IS INERT UNTIL THE FEED IS REGENERATED.** `site/data/book_growth.json` on disk
predates this and carries no `settlement_selection`, so the JS takes the uniform branch and the
existing doors stay green. That is the correct fail-closed default — a record written before the
chooser existed describes a uniform sample — but it means **no reader sees the chosen-sample prose
yet**, and a door test over that branch cannot be written against a feed that cannot produce it.
Regenerating the feed and landing the door for the chosen branch is the second thing the next turn
should take.

## Per-year proportionality: REPLACED, and the drawn item asked to be told which

Replaced. Chosen-for-difference and proportional-by-count are opposed criteria, so culling within
each year to keep it would reinstate the count rule. `customer_years` is on the choosing axes (the
only thing stopping the medoids collapsing onto one year) and the year composition is a *fitted*
property reconstructed to 0.1% — which can fail, and on its first measurement did.

## Evidence

`tests/simulation/test_net_new_acquisition.py`, `test_opening_book_subset.py`,
`test_the_settled_book_is_chosen_and_weighted_not_culled_by_count.py`,
`tests/tools/test_generate_book_growth_data.py`: **117 pass**. Two controls mutation-proven:
re-adding `volume_m3` fires the axis-independence control (correlation 1.0000); disabling the
`groups=` rows fires the year-reconstruction control (2016 at 5.6 against 18). `epistemic_verifier`
PASS over 556 files. `finding_classes` PASS. `ruff --select I001` clean on every path landed.

The full `tests/simulation/` suite is **not** claimed: `0d86d6dfe` recorded it hitting a 3,500s
timeout without a verdict, and that is still its own open finding.
