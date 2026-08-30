**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`

# Pre-registration: what C3 — the price the household is shown — must show

**Filed:** 2026-08-30, before a single line of C3 was written and before any run.
**Reads on:** `docs/design/CHOICE_AND_CHANNEL_ROADMAP.md` §C3 ·
`docs/staging/DIRECTOR_BRIEF_CHOICE_AND_CHANNEL_2026-08-30.md` §4.

A prediction filed after the answer is not a prediction. This exists so the run can refute me.

---

## The premise, checked rather than assumed

The roadmap asserts *"every household today responds to a true differential computed at its own
billed consumption"*. That was worth checking, because the differential itself
(`simulation.customer_events._price_differential_vs_market`) is a pure **unit-rate fraction** and
carries no consumption at all — so the premise could have been wrong and C3 empty.

It is not. Consumption enters one line later.
`market_switching_propensity.churn_position_multiplier` turns that fraction into POUNDS using
`_annual_bill_gbp(billing_account, ...)` — *"what we billed THIS household over the trailing year,
across ALL its supply points"*. Ofgem/BMG 2024 is the source for households valuing savings in
absolute terms, and that part is right. What no household can observe is **its own trailing-year
settled bill**, which is the number the world hands it.

## The change, and it is deliberately one variable

`shown_annual_bill_gbp = own_trailing_year_gbp × (TDCV_kwh / own_annualised_kwh)`

The same tariff, the same trailing window, the same standing charges, the same construction — at
**typical** volume instead of the household's own. Only the volume moves. The alternative
constructions (a fresh TDCV bill from unit rate × TDCV, or a commodity-only figure) would move the
LEVEL as well as the heterogeneity, and then no result could be attributed.

`TDCV_DUAL_FUEL_MWH = 14.2` already exists in `simulation/competitor_reference.py`, cited to
Ofgem's published TDCV (2,700 kWh single-rate electricity + 11,500 kWh medium gas). Reused, not
re-stated: one name, one number.

The **settlement** keeps the true bill. Only the switching decision moves to the shown one.

## Measured before the change, on the live book

162 domestic households, annualised from `site/data/customers.json`:

| | shown ÷ felt saving |
|---|---|
| median | **0.81** |
| mean | 0.97 |
| min / max | 0.19 / 5.54 |
| households who would perceive a **smaller** saving than today | **106 of 162** |

## The predictions

1. **Most households become less switchy, and the population level therefore falls.** The median
   household perceives 19% less saving than today. The level anchor is fitted to hold the realised
   rate inside the published band, so `test_the_worlds_realised_departure_rate_is_inside_the_
   published_band` should go **RED below the band** after this and before a re-fit. If it goes red
   ABOVE the band, my sign is wrong and the step must be re-read before it is believed.
2. **The company's measured advantage must not improve.** The world's truth becomes flatter — the
   per-household bill scale collapses from 162 values to three (electricity-only, gas-only,
   dual-fuel) — so there is LESS per-customer variation for a per-customer belief to discover.
   If the value arm's advantage over the flat control rises after C3, that is a signal the step is
   wrong, not a win. This is the roadmap's own filed direction and I am not softening it.
3. **The belief-vs-truth gap should widen, not narrow.** The company's estimator keys on its own
   view of the household; the world now keys on a convention the company is not using. A NARROWING
   gap here would mean the company accidentally became right, which needs explaining before it is
   published — and under the standing rule (`docs/design/INDEPENDENCE_IS_NOT_INFERENCE_2026-08-30.md`)
   a narrower gap is not evidence of skill in any case.
4. **2022 should reproduce as a price effect through the convention** rather than by assertion. The
   crisis year's switching collapse is a savings collapse; at TDCV volume it should still collapse.
   If 2022 only reproduces when the household's own bill is used, the convention is not carrying
   the mechanism and the roadmap's §C3 claim is overstated.

## What would make me abandon rather than re-fit

If the level moves so far that no anchor inside the published band can be fitted — i.e. the
shown-price world cannot reach the record at any level — then the convention is wrong for this
population and C3's simplification (one TDCV pair for everybody) is the thing to revisit, not the
anchor. **Widening the band is not on the table.**

## A defect noticed in passing, not fixed here

Several accounts labelled `resi` carry annualised **electricity-only** consumption of 11,700–14,300
kWh/year — up to **5.3× TDCV**, and industrial-looking. They receive the domestic switching curve
today. This is adjacent to `WORKER_FINDING_ELEVEN_DRAWN_HOUSEHOLDS_ARE_WEARING_A_BUSINESS_LABEL`
but is not the same accounts (these are founder `C`-series). Recorded here rather than folded into
C3, because it moves the same numbers and folding it in would leave neither attributable.

---

*Filed before the work. Whatever the run says, this document is not edited — the result is written
beside it.*

---

# THE RESULT, AND PREDICTION 1 IS REFUTED

**Measured 2026-08-31, two full captures in an isolated worktree at `915bfab9b`** — the same tree
in both arms, differing only by `simulation/shown_price.py` and the seam in `customer_events.py`,
so that another lane's uncommitted C1b work could not confound it. The world is seeded and
deterministic, so these differences carry no run-to-run noise: they are exact.

| year | band | baseline % | in? | C3 shown % | in? | move |
|---|---|---|---|---|---|---|
| 2016 | 17.0–17.6 | 17.60 | yes | 18.10 | **NO** | +0.50 |
| 2017 | 13.5–14.0 | 14.00 | yes | 14.31 | **NO** | +0.31 |
| 2018 | 19.5–20.0 | 20.00 | yes | 20.14 | **NO** | +0.14 |
| 2019 | 20.7–21.3 | 21.30 | yes | 21.83 | **NO** | +0.53 |
| 2020 | 22.5–23.0 | 23.00 | yes | 23.68 | **NO** | +0.68 |
| 2021 | 17.9–18.4 | 18.40 | yes | 18.02 | yes | −0.38 |
| 2022 | 2.9–4.3 | 4.30 | yes | 4.16 | yes | −0.14 |
| 2023 | 8.9–12.5 | 12.50 | yes | 12.44 | yes | −0.07 |
| 2024 | 12.5–16.1 | 16.10 | yes | 16.21 | **NO** | +0.11 |
| 2025 | 14.3–17.9 | 17.90 | yes | 17.77 | yes | −0.13 |

2017–2024 mean: **16.20% → 16.35%, +0.15pp.** Departures **79 → 79**. Renewal decisions 465 → 459.

## I predicted DOWN. It went UP. That is the refutation, in my own words

The pre-registration says: *"the population level therefore falls … should go RED below the band …
If it goes red ABOVE the band, my sign is wrong and the step must be re-read before it is
believed."* It went red **above** the band in five years. **My sign was wrong** and this section is
what the pre-registration was filed to make possible.

## Two things the table says that the prediction did not anticipate

**1. The band exits are mostly an artefact of the anchor, not a measure of C3's size.** Look at the
baseline column: 17.60 against a 17.0–17.6 band; 14.00 against 13.5–14.0; 23.00 against 22.5–23.0.
**The baseline sits exactly on the band's high endpoint in every year**, because
`departure_level_anchor` was fitted to that endpoint — §6's anti-flattering tie-break. There is
*zero headroom above*, so **any** upward movement, of any size, exits the band. A +0.11pp move in
2024 "leaves the published band" and means almost nothing.

That is worth more than this experiment: **the level control cannot distinguish a small honest
change from a large one in the upward direction, because the fit left it on the ceiling.** Filed
separately rather than buried here.

**2. The effect is small — 0.15pp on 16.2%, under 1% relative — and it moved no departures at all.**
79 either way. The 6 fewer renewal decisions are re-timing, not attrition.

## Why my sign was wrong, as a hypothesis to test rather than a conclusion

My 0.81 median shown/felt ratio was computed over **lifetime book totals annualised**, while the
world scales by the **trailing-year bill at each renewal**. Those are different populations, and I
compared one to reason about the other — the ratio-of-two-different-things error I have a standing
note about.

The candidate mechanism for the sign: `_savings_to_rate` is piecewise and flattens toward its
calibrated ceiling, so a household already deep in the saturated region loses little propensity
when its perceived saving is cut, while a low-consumption household — whose shown bill is up to
**5.5×** its own — gains a lot when lifted from the steep part of the curve. The gains at the
bottom would then outweigh the losses at the top. **This is not established.** Testing it means
splitting the per-decision `sim_price_response` change by where each household sat on the curve,
which is one pass over the two captured tables and is the next step.

## What is NOT answered

Predictions 2 and 3 — that the company's advantage must not improve, and that the belief-vs-truth
gap should widen — need the value-arms A/B, a separate run that has not been made. **C3 is
therefore measured but not cleared, and it is not landed on `main`.** The band exits above would
need the anchor re-fitted whatever the cause, and re-fitting to absorb a change whose mechanism I
cannot yet explain would be fitting the world to make a control green.

*The prediction above is left exactly as filed.*
