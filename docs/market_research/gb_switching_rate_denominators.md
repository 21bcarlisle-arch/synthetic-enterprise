# GB domestic switching: the published rate on every denominator it will bear

Research completed: 2026-08-30, delivery seat. Live sources probed this pass (HTTP 200): Ofgem State
of the Market retail highlights April 2025 and January 2026; Ofgem Retail Market Indicators data
portal; ElectraLink Energy Market Insight. In-repo sources followed rather than re-derived:
`churn_price_elasticity.md` §1 and `f5_simulated_competitor_field.md` §9.

Commons artefact: `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`.
Opened by: `docs/staging/WORKER_FINDING_THE_WORLDS_DEPARTURE_LEVEL_HAS_NEVER_BEEN_CHECKED_AGAINST_A_PUBLISHED_RATE_2026-08-30.md`.

---

## 1. Why the denominator has to be declared first

Every quotable switching figure in this area is a count of *something transferring*, and the things
counted are not the same thing:

| numerator | what one unit is | who publishes it |
|---|---|---|
| domestic electricity changes of supplier | one electricity meter point (MPAN) transferred to a different supplier | DESNZ *Quarterly Domestic Energy Switching Statistics*; Energy UK; Ofgem Retail Market Indicators (charted "by fuel type") |
| domestic gas changes of supplier | one gas meter point transferred | same |
| "changes of supplier", both fuels | a dual-fuel household moving both fuels counts **twice** | ElectraLink headline series |
| "switched supplier **or tariff** in the last 6 months" | includes an internal move to a different tariff with the *same* supplier | Ofgem Consumer Impacts of Market Conditions survey |

| denominator | count | note |
|---|---|---|
| GB domestic electricity accounts | ~27.5–28.3m over 2016–2025 | Ofgem Retail Market Indicators, as tabulated in `company/market/market_report.py::_UK_DOMESTIC_ACCOUNTS_M` |
| GB domestic gas accounts | ~23–24.6m | ~80% of gas customers are dual-fuel |
| all domestic fuel accounts | ~51–55m | the sum of the two, and the only denominator a both-fuel numerator may be divided by |

**The rule that follows, and it is the one this project keeps breaking:** a both-fuel numerator over
an electricity denominator double-counts every dual-fuel household. That single mismatch is enough
to turn a 12% rate into a 21% one, and it is the most likely provenance of the "~21%" figure the
opening finding attributed to a DESNZ 2019–20 pair.

## 2. The matched pair this world's departures bear

Our numerator is a **household-level** departure, rolled once per year and keyed to the electricity
leg: all departures in the run carry `commodity: "electricity"`. So the matched published numerator
is **domestic electricity changes of supplier**, and the matched denominator is **all GB domestic
electricity accounts, whether or not the account is at a decision point.**

That last clause is load-bearing. The published denominator contains households half way through a
fixed term who cannot appear in the numerator. Measuring our own rate over *renewals only* narrows
the denominator to accounts at a decision point and reads roughly a third high. Both readings are
given below and labelled; only the first is comparable with the published record.

## 3. The published series, and one series it is not reconciled with

Taken from `churn_price_elasticity.md` §1 — which `f5_simulated_competitor_field.md` §9 adjudicated
against live Energy UK and GOV.UK data this July and found corroborated at 2020 and 2021, in the same
pass that disconfirmed the competing in-repo series by ~3× at 2021. Bands are switch counts over a
flat 28.0m denominator; see the artefact for why the denominator's own drift is not what sets the
width.

ElectraLink's headline (3.21m changes of supplier in 2024; 6.34m peak in 2019) is **not folded into
the band**, because this pass could not settle whether it counts one fuel or two. Read as
electricity, its 2024 is 11.5%; read as both fuels, the electricity share is ~1.8m and its 2024 is
~6.5%. Those differ by 1.8×, and choosing between them to widen a band would be picking a number
because a number was needed. It sits in the artefact as an open cross-check with what would settle
it.

## 4. The measurement: three levels, and two of them were never checked

| year | published band % | the world's own savings curve % | world `E[depart]` per renewal % | world departures / active elec account % |
|---|---|---|---|---|
| 2016 | 17.0–17.6 | 14.7 | 3.50 | — |
| 2017 | 13.5–14.0 | 11.0 | 3.20 | 1.2 |
| 2018 | 19.5–20.0 | 11.0 | 8.54 | 8.0 |
| 2019 | 20.7–21.3 | 10.0 | 6.24 | 5.3 |
| 2020 | 22.5–23.0 | 8.0 | 2.74 | 2.0 |
| 2021 | 17.9–18.4 | 5.0 | 4.32 | 2.8 |
| 2022 | 2.9–4.3 | 3.0 | 6.09 | 3.6 |
| 2023 | 8.9–12.5 | 6.0 | 3.40 | 3.4 |
| 2024 | 12.5–16.1 | 6.8 | 4.88 | 3.1 |
| 2025 | 14.3–17.9 | 7.5 | 18.78 | — |

2017–2024 means: **published 15.5%**, world curve **7.6%**, world realised **4.93%** per renewal and
**3.6%** per active electricity account.

Columns three and four are measured from `docs/reports/c2_departure_factors.json`, the 708-renewal
capture the C2 calibration was run on; column five uses the active-account counts in the opening
finding. Reproduce with `tools/measure_departure_level.py`.

**Three results, and the middle one is new.**

1. **The world is 3.15× short of the published record per renewal, and ~4.3× short per account.**
   That is the finding's "two to five times too sticky", now stated against a series with a declared
   numerator and denominator rather than against three readings that could not be reconciled.

2. **`simulation/market_switching_propensity._savings_to_rate` says in its own docstring that it is
   "calibrated from the DESNZ switching series 2015-2025". It is not.** Evaluated at each year's own
   savings it runs at **half** the published series (2.04× on the 2017–24 mean) and is wrong in
   *shape* as well as level at the two years that matter most: 2020 is 8.0% against a published
   22.5–23.0%, and 2021 is 5.0% against 17.9–18.4%. It gets 2022 right. A curve that reproduces the
   crisis and misses the peak by 3× is not a calibration to this series.

3. **The level never reaches the world anyway.** `market_switching_multiplier` computes that
   absolute rate and then *divides it by the 2024 value* to return a multiplier normalised to 1.0.
   Whatever level the curve carries is discarded at that line, and the world's departure level is
   then whatever `saas.churn_model`'s bill-shock base rate happens to produce. **That is the
   mechanism behind the opening finding's headline: the world took the SHAPE of the published
   switching series and normalised its LEVEL away.** No control anywhere read the level, because the
   only module that computed one cancelled it in the next statement.

## 5. A correction to the opening finding, kept beside it

The finding says the market switching rate "is an upper bound on a book of average engagement".
**In aggregate that is not right, and the direction matters.** Total switches equal the sum of
suppliers' external losses; total accounts equal the sum of their books. So the account-weighted mean
supplier loss rate *is* the market switching rate, exactly. Concentration of switching in engaged
households makes suppliers differ from each other — it does not lower the mean. An
average-engagement book loses at the published rate; the published rate is the expectation, not a
ceiling.

Read as a ceiling it would license aiming low. Read correctly it does not, and it happens to agree
with the brief's tie-break rather than fight it.

## 6. Where inside the band the world should be aimed

The band is evidence and is settled here. **Where inside it the world sits is a curriculum value**,
and the director's brief of 2026-08-30 §7 supplies the rule rather than leaving it to preference:
*"where the evidence is ambiguous, choose the option that makes the company's advantage harder to
demonstrate."*

More departures means more of the book to re-win, more revenue at risk and a harder book to hold, so
the tie-break points at the **high end of each year's band**. §5 above says the same thing from the
evidence side. The choice and its direction are recorded here rather than in the code, and the
correction itself is the seat's under the refinement of 2026-08-30 — the present level was never a
decision anybody took, only the residue of a normalisation.

**This document does not move the level.** It establishes what the level should be. The move is a
separate change with a pre-registered prediction; see §8.

## 7. `a_shock`: the price family does not split, and the parameter stays free

The C2 pre-registration needs the "price" family of departures separated into *my own bill rose*
(bill shock) and *someone else is cheaper* (price position). A discovery pass this tick asked whether
any published instrument splits them for **domestic** GB households.

What the instruments actually offer:

| instrument | base | codes |
|---|---|---|
| Ofgem CIM wave 5, Jan–Feb 2024 | 174 switchers | cheaper tariff 44%; good reputation 19%; issues with current supplier or tariff 16%; poor customer service 16%; offers good service 15% |
| Ofgem CIM wave 6, Jan–Feb 2025 | 754 who switched tariff **or** supplier | cheaper tariff 50%; protected by the price cap 25%; the tariff I wanted 22%; reward or incentive 13%; better rated customer service 6% |
| Ofgem non-domestic 2024 | 365 business switchers | knew the contract was ending 29%; **a price-increase notification from the previous supplier 16%**; wanted a better deal 14%; renewal notice 12%; **offered a better deal by a new supplier 9%** |

**The domestic instrument does not split it.** "To get a cheaper tariff" is a single code and it
covers both halves — the household whose own bill rose and the household that saw a better offer
answer it identically. Wave 6 is the larger base and it is *further* from the split, because its
population includes internal tariff switches.

**Only the non-domestic instrument separates them**, and it may not be borrowed. The brief itself
records that the business list is dominated by a contractual event and the domestic list by a price
motive — "they differ in kind and not only in ranking" — so a mix lifted from the business
population would be a selection effect imported under the name of a measurement.

**Therefore `a_shock` stays free and is not picked.** The consequence for the pre-registration is
that P2's reason mix is published as an **interval over the feasible set, never as a point**: on the
708-renewal table every scale from 0.87 downward reproduces the population mean exactly, and the
bill-shock share across that family runs from **99.9% down to 56.6%**. The interval's own bound is
that family, and it is wide because the data are silent, not because the arithmetic is loose. A
single number quoted here would be a measurement of our own arithmetic.

**Explicitly not used to identify it:** the published mover-mix. The roadmap makes that a *check* on
P2, and using a check as an input makes P2 a tautology.

**What would settle it.** A stated-reason instrument fielded on domestic switchers that separates a
price-increase notification from a competitor offer — the shape Ofgem already fields for
non-domestic. Nothing published that this pass could find does it for households.

## 8. Pre-registered prediction for the level move, filed before the run

Written before the change that will test it, so it can refute me.

1. Raising the world's departure level to the published band **raises mean realised churn**, and the
   direction is not in doubt; the magnitude is. Predicted: mean realised departure probability per
   renewal moves from **4.93%** to inside **12.5–16.1%** at 2024 and to a 2017–24 mean inside
   **13–18%**.
2. The **shape** must move too, and this is the discriminating prediction. The curve's error is not a
   flat scale: 2020 is 2.9× low and 2022 is right. A pure level scale will therefore land 2022
   **above** its published band of 2.9–4.3% and fail. **If a single multiplicative scale fixes the
   mean and keeps every year in band, I am wrong about the shape** and the curve was closer to the
   series than §4 says.
3. Book economics: more departures, more re-acquisition spend, lower retained revenue. If any
   headline company result *improves* after this change, that is a defect in the change and not a
   finding about the company.
4. C2's P0 is restated by this: it is no longer "hold the level constant" — which would have
   preserved the bill-shock discount the composed form applies to cheaper-than-market households —
   but "the level MOVES, and lands inside the published band".

## 9. The predictions marked beside themselves, 2026-08-30

The change §8 was written against landed today: `market_departure_rate` in
`simulation/market_switching_propensity.py`, the record read from the commons, and
`market_switching_multiplier` rebuilt as a ratio **of the record** rather than of the savings
curve. §8 is left exactly as written; each prediction is marked here, right or wrong.

**1 — NOT MET, and it moved the wrong way.** Predicted: 4.93% → inside 12.5–16.1% at 2024 and a
2017–24 mean inside 13–18%. Measured, on a re-captured run (`docs/reports/c2_departure_factors.json`,
681 renewals): **2017–24 mean 4.50%**, 2024 **5.14%**. The level did not move, and the mean went
slightly *down* — 3.15× short of the record before, **3.45× short after**.

The shape did move, and where it moved it moved onto the record. Two years came **into** band that
were outside it: 2022 (6.09% → **3.19%**, band 2.9–4.3%) and 2025 (18.78% → **17.31%**, band
14.3–17.9%). 2021 rose 4.32% → 7.01% and 2016 fell 3.50% → 1.73%, both in the record's direction.

The reason the level did not follow is a thing §8 did not think about and should have: the market
term reaches the churn chain in
`simulation/customer_events.py` as a **dimensionless ratio**, `p_churn *= market_switching_multiplier(y)`,
normalised to 1.0 at 2024. Correcting *what the ratio is a ratio of* moves the **shape** across
years and cannot move the **level** at all, by construction — the reference year is 1.0 whatever the
record says. §8 assumed "raise the curve to the band" and "raise the world to the band" were one
change. They are two, and only the first of them landed.

**2 — CONFIRMED, and by more than it claimed.** The discriminating prediction was that a pure
multiplicative level scale pushes 2022 above its published 2.9–4.3% and fails. The scale, derived
rather than chosen (`_curve_level_scale()`, the ratio of the two means over the overlap), is
**1.99×**. At that scale:

| year | savings curve | ×1.99 | published band | |
|---|---|---|---|---|
| 2016 | 14.7% | **29.2%** | 17.0–17.6% | far above |
| 2020 |  8.0% | **15.9%** | 22.5–23.0% | still below |
| 2021 |  5.0% | **10.0%** | 17.9–18.4% | below |
| 2022 |  3.0% |  **6.0%** |  2.9–4.3%  | above — the year the curve had right |

So the scale fails in **both** directions, which is stronger than "2022 goes high".

And the pass found the reason, which §8 did not predict because it did not occur to me: **a function
of savings alone cannot reproduce the series under any recalibration.** `MARKET_SAVINGS_BY_YEAR`
gives 2017 and 2018 the *same* £200 saving, and the record puts them 6pp apart (13.5–14.0% against
19.5–20.0%). No function returns two values for one argument, so at least one of those years is out
of band for every possible curve. The record is not even monotone in savings: 2021 offered £0 and
switched more (17.9–18.4%) than 2016 at £300 (17.0–17.6%). That is why the level for a year the
record covers is now **taken from the record** rather than modelled, and the curve keeps the job it
is actually good for — the price-position response, and generating a level where the record is
silent.

**3 — FIRED. The trap-detector caught this change, and I am recording it rather than explaining it
away.** Mean realised departure probability per renewal fell **4.93% → 4.50%**: a book 0.43pp easier
to hold, which is a headline result moving in the company's favour, which §8 says is a defect in the
change.

It is a small effect and I can say exactly where it comes from, which is the part worth keeping.
The mean multiplier across 2017–24 fell 1.124 → 1.006, because normalising at 2024 divides by a year
the record puts *high* relative to its neighbours (16.1%) where the curve had it *low* relative to
its own (6.75%). **Nothing about the world changed to make the book easier — only which year the
ratio is divided by.** That is the diagnosis of prediction 4 arriving from the other side: a term
carrying only a ratio can move the company's fortunes by the choice of denominator alone, and a
quantity that behaves that way is not a fact about the world.

Two things stop this being a reason to revert. The direction of every *individual* year's correction
is the record's, not a choice — 2016's flattering 2.17 comes down to 1.09 and 2021's suppressed 0.74
goes up to 1.14, so the desk now sees undercut pressure in 2018–2021 that the curve hid. And the
band position was taken at the **high** end under §6's tie-break, which is the anti-flattering choice
at every single year. The aggregate still came out 0.43pp the company's way, and that is the finding:
it is the normalisation, and it goes when the level anchor lands.

Realised departures per active electricity account went **up** in 2022 (3.6% → 5.5%) and 2024
(3.1% → 6.9%) and **down** in 2018, 2019 and 2023. I am not attributing that: the run's renewal count
itself changed (708 → 681) because the trajectory differs, so those counts are not a clean
before/after and the mean probability is the only column that is.

**4 — RESTATED AGAIN, and now with the blocker measured instead of assumed.** "The level MOVES and
lands inside the published band" is still the target and is still open. What this pass establishes is
that **no single scale on the market term can reach it**, so it is not a constant anybody has yet to
pick. Decomposing the captured run into the market factor and everything else, the non-market
product (bill shock × felt price position × action propensity × dissatisfaction) is:

    2017 0.0198   2018 0.0530   2019 0.0405   2020 0.0233
    2021 0.0613   2022 0.1193   2023 0.0466   2024 0.0514

— a **6× spread** whose shape is unrelated to the record's (2022, the record's trough, carries the
*largest* value). Solving for the single divisor that would put each year inside its own band gives
disjoint intervals — 2017 needs 0.0198–0.0205, 2022 needs 0.1193–0.1770, and the intersection across
all eight is **empty**. One scale cannot do it, and fitting one would be choosing which years to be
wrong about.

That makes the level move **C2's per-year level anchor**, not a constant: the market rate has to set
the year's level with the household factors distributing it *within* the year, which is exactly the
competing-risks form `simulation/departure_risks.py` was opened for. Held open and visible rather
than filed: `tests/architecture/test_switching_rate_commons.py::test_the_worlds_realised_departure_rate_is_inside_the_published_band`
is a **strict** xfail carrying this reason, so it must break loudly the day the level lands rather
than sit green forever.

## 10. A second reading, found by following the thread

Widening the register turned one up. `company/crm/market_conditions.py` carries
`MARKET_SWITCHING_MULTIPLIER_BY_YEAR`, a ten-entry company-side table whose docstring says it is
"derived from the same public switching-rate series, normalised to 2024 = 1.0". It was invisible to
the control because it is shaped as a **ratio**, and the register only held tables shaped as rates.

A multiplier normalised to a reference year is a switching-rate reading — it states every year as a
fraction of the reference year's rate — so multiplying it back by the record recovers what it
asserts:

| year | table | implied rate | published band |
|---|---|---|---|
| 2016 | 2.17 | **34.9%** | 17.0–17.6% |
| 2020 | 0.95 | **15.3%** | 22.5–23.0% |
| 2021 | 0.57 |  **9.2%** | 17.9–18.4% |

This is not a spare constant. `company/crm/competitive_pressure.py` scales every enriched churn
estimate by it and derives its own log-spread from the table's values, so correcting it changes
company behaviour and needs its own before/after — it is not a number to overwrite in passing while
landing something else. Registered in `_MULTIPLIER_READINGS` and held by a **strict** xfail so it
cannot go quiet again, and left open for its own pass.

Note what the shape difference did: the register was written *specifically* so a second lane reading
could not arrive unheld, and a second lane reading was sitting in the tree the whole time, four weeks
older than the register. It was not hidden — it was the wrong shape to be seen. That is the same
lesson as the denominator: **what a control can see is set by the shape of its subject, not by the
diligence of the person who wrote it.**

## 11. Pre-registered predictions for the level ANCHOR, filed 2026-08-30 18:08Z

Filed while the capture that tests them was still running and before a single one of its numbers had
been read. §8 stands unchanged above it and is the standing pre-registration for the level move
itself; this section is the pass-specific set for the change that lands the anchor —
`simulation/departure_level_anchor.py`, a per-year level term inside
`departure_risks.build_departure_risks`, and the competing-risks form wired into the churn chain.

**A — the level moves, and it does not land clean first time.** The anchor is fitted on the
*pre-change* population, and raising departures roughly threefold changes the book underneath it:
accounts leave sooner, re-acquisition replaces them, and the renewal population the anchor was
solved against is not the one the next run has. So: the 2017–24 mean lands inside **13–18%** (up
from 4.50%), and **at least one year lands outside its own band** on the first capture. If every
year lands in band first time, the book is less sensitive to its own churn rate than this predicts
and the fixed-point argument in `tools/fit_year_level_anchor.py` is overstated.

**B — the trap-detector, still standing and still armed.** More departures means more re-acquisition
spend, less retained revenue and a harder book to hold. **If any headline company result improves,
that is a defect in the change and not a finding about the company.** It fired last pass, on a
0.43pp move; it is a stronger test this time because the move is ~11pp.

**C — retention offers retain strictly fewer accounts.** The offer now scales the price-position
hazard alone (P6) instead of the whole probability, so a discount can no longer retain a
service-driven churner. Predicted: the realised effect of a retention offer on departure probability
falls, and does not rise for any household.

**D — the reason mix is an interval and its width is large.** At the declared `a_shock`, no single
cause takes more than **70%** of the expected mix and price-position plus dissatisfaction together
take more than **30%** — i.e. all three risks are materially live. The interval across the feasible
family is **wider than 30pp on bill-shock**, because that is what "unidentified" means here.

**E — the desk's pressure signal is untouched.** `market_switching_multiplier(2024)` is exactly 1.0,
at least four years produce strictly positive undercut pressure, and the record's peak switching
year still buys a strictly lower ceiling than the reference year. This is a prediction about
something that must NOT move: the level anchor is a separate quantity and pushing it through the
company-facing ratio would zero that signal forever. Held by
`tests/simulation/test_market_switching_propensity.py::TestTheTwoQuantitiesStaySeparate`.

## 12. §11 marked beside itself, 2026-08-30

The change §11 was filed against landed the same evening: `simulation/departure_level_anchor.py`,
the competing-risks form wired into `simulation/customer_events.py`, and the level term inside the
hazards. §11 is left exactly as written; each prediction is marked here, right or wrong.

Measured on two full 2016–2025 runs captured by `tools/capture_departure_factors.py` and read
through `tools/measure_departure_level.py`. The committed table is the second one.

**A — CORRECT on both legs, including the leg that predicted its own failure.** The 2017–24 mean
went **4.50% → 16.04%** on the first capture, inside the predicted 13–18% and against a published
midpoint of 15.50%. And the first capture did **not** land clean: 2017 came in at 14.01% against a
13.5–14.0% band and 2020 at 23.72% against 22.5–23.0%, exactly the drift the fixed-point argument
said a once-fitted anchor would carry. Refitting on that capture and re-running closed it: every
year of the second capture sits on its band.

| year | pre-anchor | capture 1 | capture 2 | published band |
|---|---|---|---|---|
| 2017 |  1.72% | 14.01% | 14.00% | 13.5–14.0 |
| 2018 |  6.58% | 19.53% | 20.00% | 19.5–20.0 |
| 2019 |  5.36% | 21.21% | 21.30% | 20.7–21.3 |
| 2020 |  3.33% | 23.72% | 23.00% | 22.5–23.0 |
| 2021 |  7.01% | 18.37% | 18.40% | 17.9–18.4 |
| 2022 |  3.19% |  4.19% |  4.30% |  2.9–4.3  |
| 2023 |  3.62% | 12.32% | 12.50% |  8.9–12.5 |
| 2024 |  5.14% | 14.96% | 16.10% | 12.5–16.1 |
| **mean** | **4.50%** | **16.04%** | **16.20%** | **15.50%** |

**A′ — AN UNPREDICTED RESULT, and it is a defect in the CONTROL rather than in the change.** The
second capture landed on each band's **top edge to four decimal places**, because §6's tie-break
aims the world at the high end and the anchor hits its target. Five of the eight years then read
**0.0002pp ABOVE** their endpoint and three on or below it — pure rounding noise from
`realized_churn_probability` being stored to four decimals — and a strict float containment check
turned that into a coin flip. Repaired at the property: `tools/measure_departure_level.inside_band`
compares at the precision the commons publishes its endpoints to (0.1pp, derived from the artefact,
not written down). It still fails capture 1's 23.72% at 2020, and it fails the pre-anchor world at
every year by miles. A control decided by the thirteenth decimal place of a figure published to one
is not measuring the world.

**B — the trap-detector: CONFIRMED, and in the right direction this time.** Every quantity the
capture carries moved against the company:

| | pre-change | post-change |
|---|---|---|
| renewals reaching a decision | 681 | **465** |
| departures | 43 | **79** |
| departure share of renewals | 6.3% | **17.0%** |
| mean realised departure probability | 5.62% | **16.20%** |
| retention offers made | 8 | **29** |

The book turns over so much faster that a third fewer accounts survive to a renewal at all. Nothing
here improved. **The headline P&L set is NOT yet measured** and this is stated rather than implied:
these are the capture's own columns, and retained revenue, acquisition spend and CLV arrive with the
next sim-runner publish. §11 B applies to those too, unchanged, and they must be read against the
last published run before this change.

**C — NOT YET MEASURED, and it is the one piece of §11 this pass does not settle.** A retention offer
now scales the price-position hazard alone rather than the whole probability, so a discount cannot
retain a service-driven churner. The mechanism is in the code and pinned by
`test_a_retention_offer_cannot_retain_a_service_driven_churner`, but the realised effect across the
book is not measured here: offers rose 8 → 29 in the same change, so a before/after on retention
effectiveness would be comparing two different offer populations. It needs its own pass with the
offer count held.

**D — CORRECT.** At the declared pair the expected mix is **bill_shock 55.1% / price_position 23.0% /
dissatisfaction 21.8%** — no cause above 70%, and price plus service at 44.8%, above the predicted
30%. All three risks are materially live. The realised mix over the 79 actual departures is
**39 / 18 / 22**, which is the same shape from a different direction and is *not* published as a
result: 79 departures across a decade is far too few, and P2 reserves the realised mix for a
multi-seed measurement. The interval across the feasible family is **55.1% to 99.9%** on bill-shock —
44.8pp wide, well beyond the predicted 30pp.

**D′ — AND THE FIRST DRAFT OF THAT INTERVAL WAS WRONG BY 44pp, caught by printing it.** The sweep
initially moved `a_shock` alone at the declared scale and produced a comfortable-looking 55%–68%.
The feasible set is a family of `(a_shock, scale)` **pairs** — both coordinates moved together along
P0's constraint — and across the real family the mix runs to 99.9%. A one-coordinate slice reported
as an interval would have understated its own bound by more than the width it claimed.

**E — CORRECT, and checked rather than assumed.** `market_switching_multiplier(2024)` is exactly
1.0, six years produce strictly positive undercut pressure (2016, 2018–2021, 2025), and the peak
switching year still buys a strictly lower ceiling at
`renewal_desk._competitive_ceiling_gbp_per_mwh` than the reference year does. `TestTheTwoQuantitiesStaySeparate` passes unweakened; the level anchor is a
third quantity in its own module and never went near the company-facing ratio.
