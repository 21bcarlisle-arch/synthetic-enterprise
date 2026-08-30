**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# The world's departure LEVEL has never been checked against a published switching rate — and it is the anchor C2's calibration was missing

**Found:** 2026-08-30, after C2's P0 calibration came back non-identifying and was correctly
refused (`54b9dfa72`). That commit found the P0 target was contaminated — the composed form lets
the price multiplier scale the bill-shock term, and the company is cheaper than the market
reference in 74.4% of renewals. **This is the other half of the same problem, and it is the larger
half: the target was not merely contaminated, it was never anchored to anything outside this
repository.**

**No published figure is known to be wrong.** This is about what the world's churn level IS, not
about a number on the site.

## What the world does

Departures per household-year, from the live run. Stated with what each number counts, because
the wrong denominator is the standing trap here:

* a departure is a **household-level** decision, rolled once per year and keyed to the electricity
  leg — confirmed, all 44 departures in the run carry `commodity: "electricity"`;
* `active_elec` is one account per household with power. `active_elec + active_gas` double-counts
  dual-fuel households and is the WRONG denominator for this numerator.

| year | departures | active elec | per household-year |
|---|---|---|---|
| 2017 | 1 | 81 | 1.2% |
| 2018 | 7 | 88 | 8.0% |
| 2019 | 6 | 94 | 6.4% |
| 2020 | 2 | 101 | 2.0% |
| 2021 | 3 | 108 | 2.8% |
| 2022 | 6 | 110 | 5.5% |
| 2023 | 1 | 117 | 0.9% |
| 2024 | 4 | 131 | 3.1% |

**2017–2024 mean: 3.6% of households leave per year.** (2016 has 3 renewals and 2025 is a partial
year; both excluded rather than averaged in.)

## What the published record says, on every denominator it will bear

The knowledge page `how-households-choose` already records that published switching counts are
**not one series** — some count electricity meter-point transfers, some gas, some changes of
supplier across both fuels — and refuses to publish a year series for exactly that reason. So the
comparison is done on every plausible reading rather than on a chosen one:

| source | numerator | denominator | rate |
|---|---|---|---|
| ElectraLink 2024 | 3.21m changes of supplier | ~51m domestic fuel accounts (28m elec + 23m gas) | **6.3%** |
| ElectraLink 2024 | 3.21m changes of supplier | ~28m domestic electricity meter points | **11.5%** |
| DESNZ 2019–20 | ~6M switches | ~28M accounts (its own pair) | **~21.4%** |

## The comparison, taken against the reading least favourable to the finding

**2024, our 3.1% against the most conservative published reading of the same year, 6.3%: a factor
of 2.0.**

**2019–20, our 4.2% against DESNZ's own matched numerator/denominator pair, 21.4%: a factor of
5.1.**

2024 is the fair test — it is the year the published record is at a post-crisis low and Ofgem
describes switching as still "below pre-crisis levels", so it is where our world has the best
chance of agreeing. It is still half the published rate on the most generous denominator
available, and a fifth of it on the one the source itself used.

**Our world is somewhere between two and five times too sticky.**

## Why this matters more than it looks, and why it is C2's blocker

C2's pre-registration put P0 first: calibrate so the population-mean churn matches today's, making
the level a control and the decomposition the only variable. That was the right shape and the
wrong target. Matching today's mean would have **locked a departure rate 2–5× below the published
record into the new mechanism**, and done it invisibly, because P0 would have reported a clean
±0.0000% match.

`54b9dfa72` refused the calibration on identifiability — every `a_shock` from 0.87 down hits P0
exactly while the reason mix runs 99.9% to 56.6%. That refusal was right, and this finding says
the calibration would have been unsafe even had it identified: **you cannot fit a decomposition to
a level nobody has checked.**

## What is owed, and it is a better job than the one C2 was blocked on

**Anchor the departure LEVEL externally before fitting the decomposition.** The published rate is a
per-year switching rate over a stated population, and the world can be held to it directly — a
target the tree does not generate, which is the whole point.

Two things have to be got right and both are the standing traps in this area:

1. **The denominator must be declared per comparison.** Our numerator is household-level
   departures; the published numerators vary by fuel. The table above is the shape any future
   comparison should take — every reading, not a chosen one.
2. **A supplier's churn is not the market's switching rate for free.** If 21% of accounts switch
   in a year and switching were uniform, ~21% of any supplier's book leaves. Switching is not
   uniform — engaged customers switch repeatedly and the disengaged never do — so the market rate
   is an upper bound on a book of average engagement and the gap between them is itself a
   modelling question, not a discrepancy to close by tuning. **The world already models
   engagement** (Ofgem RMI 45/35/20, wired), so it can be asked to reproduce both the aggregate
   rate and its concentration, which is a stronger check than either alone.

## R13, stated because this one runs toward us

Raising the world's departure rate to meet the published record makes the company's book **harder
to hold**: more departures, more revenue lost, more of the book to re-win. It is unambiguously
unflattering, which under the director's refinement of 2026-08-30 puts the correction on the
delivery seat's side of the line — *"if a curriculum-adjacent change is a correction rather than a
choice, and the honest version makes our position worse or leaves it unchanged, make it and tell
me."*

**But the SIZE of the move is a curriculum value and it is his.** How sticky a book this company
faces is a difficulty setting; "match the published rate exactly" is one defensible answer and
"land inside the published range, at the sticky end, because a supplier's book is less engaged
than the market" is another. Not chosen here. The measurement is the deliverable; the target is a
decision, and this is precisely the class he asked to see rather than have waved through.

## The falsifier this is owed

None yet, deliberately. A control asserting "the departure rate equals 3.6%" would pin today's
answer and go red when the world became more honest — the exact shape repaired this morning in
`test_as_of_r1_sees_r1_estimate_not_final`. The control worth writing is that **the world's
departure rate sits inside the published range on a declared denominator**, and it cannot be
written until the range and the denominator are settled, which is the work above.

---

## DISPOSITION 2026-08-30, delivery seat — the anchor landed; the level move has not

**Landed.** The comparison is settled and the instrument is permanent.

* `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json` — the published band
  per year, on ONE declared pair: external changes of supplier on a domestic **electricity** meter
  point, over **all** domestic electricity accounts including mid-fixed-term ones. 2017–2024 mean
  midpoint **15.5%**.
* `docs/market_research/gb_switching_rate_denominators.md` — every numerator and every denominator
  written beside each other, the sources, and what is refused.
* `tools/measure_departure_level.py` — the three-level table, reproducible.
* `tests/architecture/test_switching_rate_commons.py` — the control, keyed to the PROPERTY (inside
  the published band on a declared denominator), with three mutation legs. It is not pinned at
  today's answer and it passes when a reading is corrected toward the record.

**Corrections to this document, kept beside it rather than editing the claim above.**

1. **The "~21.4% DESNZ 2019–20" row was almost certainly a mismatched pair.** A both-fuel numerator
   over an electricity account base double-counts every dual-fuel household. The settled 2019 band
   is 20.7–21.3% on a matched electricity pair, which lands in the same place by a different route
   — so the conclusion survives and the arithmetic behind that row does not.
2. **"The market rate is an upper bound on a book of average engagement" is wrong, and the
   direction matters.** Total switches equal the sum of suppliers' external losses and total
   accounts the sum of their books, so the account-weighted mean supplier loss rate IS the market
   rate exactly. Concentration makes suppliers differ from each other; it does not lower the mean.
   Read as a ceiling it would license aiming low. It is an expectation, not a ceiling.
3. **The 3 tables here disagreed because two of them were unreconciled series, and the reconciled
   one was already in the repo.** `churn_price_elasticity.md` §1 held it, and
   `f5_simulated_competitor_field.md` §9 live-adjudicated it in July.

**The mechanism, which this finding did not have and which is the larger half of its own claim.**
The world is 3.15× short per renewal and ~4.3× short per account, and there are **two stacked
causes**:

* `market_switching_propensity._savings_to_rate` states in its own docstring that it is "calibrated
  from the DESNZ switching series 2015-2025". It runs at **half** that series (2.04× on the 2017–24
  mean) and is wrong in **shape**, not just level: 2020 reads 8.0% against a published 22.5–23.0%,
  while 2022 is right.
* `market_switching_multiplier` then **divides that absolute rate by its own 2024 value**. Whatever
  level the curve carries is cancelled one statement later, and the world's departure level is
  whatever `saas.churn_model`'s bill-shock base happens to produce. **The world took the SHAPE of
  the published switching series and normalised its LEVEL away** — which is why no control ever
  read the level: the only module that computed one destroyed it.

**NOT landed, and named rather than implied.** The world's departure rate has **not** been moved.
It is still 3.15× short. The move is a separate change with a blast radius of 27 files and a
pre-registered prediction filed before it (`gb_switching_rate_denominators.md` §8), including the
discriminating one: a pure level scale will push 2022 above its 2.9–4.3% band and must fail, because
the curve's error is not a flat scale. The `a_shock` discovery ran and **refuses to identify it** —
no domestic instrument splits "my own bill rose" from "someone else is cheaper", so the reason mix
is published as an interval over the feasible set (99.9%→56.6% bill-shock) and never as a point.

This finding therefore stays STAGED. Its measurement half is discharged; its correction half is not.

---

## 2026-08-30, later the same day: half the correction landed, and the other half is now measured

**Landed.** The two stacked causes above are separated. `market_departure_rate` is the world's
ABSOLUTE annual domestic departure rate, in per cent of domestic electricity accounts per year — the
units a publication can be compared against — and it is no longer cancelled a statement later.
`market_switching_multiplier` stays DIMENSIONLESS and 1.0 at 2024 on purpose, because
`company/pricing/renewal_desk.py:149` reads `pressure = max(0.0, multiplier - 1.0)` off it across
the wall; pushed an absolute rate, that expression is identically zero for every year in the record
and the desk's competitive ceiling goes quiet forever without complaining. The multiplier is now a
ratio **of the record** rather than of the curve, and
`test_the_company_facing_observable_is_still_a_ratio_and_still_carries_pressure` fires if either
half of that is undone.

**The finding's own claim, corrected beside itself.** It said the curve "is wrong in shape, not just
level". True, and understated: a function of savings alone **cannot be calibrated to the series at
all**. `MARKET_SAVINGS_BY_YEAR` gives 2017 and 2018 the same £200 and the record puts them 6pp
apart, so at least one is out of band under every possible recalibration. The level for a year the
record covers is therefore taken from the record — 2016–2025 domestic switching is historical ground
truth in the same sense as 2022 prices — and the curve keeps the job it is good for.

**Still NOT landed, and now with the blocker measured rather than assumed.** The world's realised
departure level has not moved. Correcting the ratio moves the SHAPE across years and cannot move the
LEVEL, because the reference year is 1.0 whatever the record says. And no single scale on that ratio
can reach the band: the non-market factor product varies 7× across years (0.0196 at 2017 to 0.1372
at 2022) with a shape unrelated to the record's, and the per-year divisors that would put each year
in band are disjoint (2017 needs 0.0193–0.0200, 2022 needs 0.115–0.170). That makes the level move
**C2's per-year level anchor**, not a constant anybody has yet to pick.

Held open where it can be seen rather than in this file:
`tests/architecture/test_switching_rate_commons.py::test_the_worlds_realised_departure_rate_is_inside_the_published_band`,
a **strict** xfail, so it breaks loudly the day the level lands.

**A second reading, found by following the thread.** `company/crm/market_conditions.py` carries a
second company-side reading of the same series shaped as a 2024-normalised multiplier — invisible to
a register that only held rate tables. Read back against the record it asserts 34.9% for 2016 and
15.3% for 2020. It is a live prior behind every enriched churn estimate, so it is registered and
xfailed, not overwritten in passing. See `gb_switching_rate_denominators.md` §10.

**Disposition unchanged: STAGED.** Measurement half discharged; correction half half-discharged.
