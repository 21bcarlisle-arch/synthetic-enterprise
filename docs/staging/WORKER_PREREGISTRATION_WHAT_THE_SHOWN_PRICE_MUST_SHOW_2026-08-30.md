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
