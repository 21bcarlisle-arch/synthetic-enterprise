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
