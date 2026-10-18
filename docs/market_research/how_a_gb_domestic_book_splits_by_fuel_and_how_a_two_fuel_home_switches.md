# How a GB domestic book splits by fuel, and how a home with both fuels switches

**Knowledge:** how-households-choose

Research completed: 2026-10-17, worker tick, on the director's steer of the same day
(`docs/staging/advisor/DIRECTOR_STEER_THE_BOOK_IS_SINGLE_FUEL_DO_THE_KNOWLEDGE_WORK_2026-10-17.md`).
Every figure below was read in the primary document this session; page or paragraph given.

---

## 1. Why this page exists

The opening book drawn on 17 Oct held 400 supply points in 395 homes, and 5 of those homes were
dual fuel (1%). Each of the 387 drawn founders was one single-fuel account, its fuel picked by an
account-level coin (`population_draw.DEFAULT_COMMODITY_WEIGHTS = {"electricity": 0.72, "gas":
0.28}`, labelled a "documented placeholder" on 13 July). 357 of the 382 drawn founder homes were
gas homes, and every one was split supply, with the other fuel at an unseen rival.

**The answer was already in the repo.** `ons_consumption_profiles.md` §"Dual-Fuel Customer
Proportions" (21 June) says ~75% of residential customers take both fuels from one supplier and
that gas-only is under 5%. `rd_synthesis_june_2026.md` Finding 6 checked this against the 13
hand-written accounts and concluded "the proportion is correct by design". The draw that replaced
those accounts was written three weeks later and never read it. §6 below records the cause.

## 2. How GB domestic customers split by fuel

| Source | What one unit is | Dual fuel, one supplier | Electricity only | Gas only | Two suppliers for two fuels |
|---|---|---|---|---|---|
| **CMA, Energy Market Investigation, Provisional Findings Summary (July 2015), ¶9**, at 31 Jan 2015 | supplier customer counts | **19m** | **8m** | **4m** | not stated (see below) |
| **CMA, Energy Market Investigation, Final Report (June 2016), ¶10** | supplier customer counts | **20m** | **8m** | **3m** | not stated |
| **CMA customer survey, GfK NOP (Feb 2015), ¶41 and Figure 2**, n = 6,999 households, fieldwork Sept 2014 | household | **72%** | **15% (chart) / 17% (text)**, no mains gas | — | **9%** (5% + 4%) |
| **Ofgem Consumer Engagement Survey 2017 (Ipsos MORI), §2.3 and §3**, n = 4,001 GB | household | 91% "bought gas and electricity from the same supplier" (the base is not stated to exclude electricity-only homes) | **11%** have electricity and no gas | <1% | the remainder |
| CMA PF Summary Table 1 (Q1 2012–Q2 2014) | share of each fuel's customers | 82% of gas customers, 69% of electricity customers | 31% of electricity customers | 18% of gas customers | — |

**Reading the CMA counts.** 27m electricity customers and 23m gas customers give about 4m homes
with no gas. That leaves about 4m of the 8m electricity-only customers as **split-supply homes**:
homes with gas whose electricity is with someone else. Their gas is the 4m gas-only customers.
So, among homes with gas:

- **one supplier for both: 19 / 23 = 83%** (administrative counts, CMA PF ¶9);
- **two suppliers: about 17%.** Each split home is one electricity-only customer at one supplier
  and one gas-only customer at another, so a split home is equally likely to show up in a given
  supplier's book as its electricity or as its gas: **about 8–9% each**.
- The GfK household survey puts one-supplier at 72 / 81 = **89%** of homes with gas. The range
  **83–89%** brackets the published record; the administrative figure is the central one, because
  it counts customers rather than asking them.

**Gas-only is a split-supply artefact, never a home with no electricity.** Ofgem 2017 finds under
1% of households with gas and no electricity. A gas-only account is always a home whose
electricity is with another supplier.

## 3. What share of GB homes have no gas

| Source | Measure | Share without |
|---|---|---|
| DESNZ, *Subnational electricity and gas consumption summary report 2024* | domestic properties not connected to the gas grid | **16%** GB (7% North East, 24% South West) |
| EHS 2017-18 Energy Report, Annex Table 3.5 (already in `premise_population.EHS_AT3_5_FUEL_BY_GAS_METER`) | dwellings without a gas meter, England | **14.0%** (3,363 of 23,949 thousand) |
| DESNZ NEED 2026 anon 50k (`mains_gas_is_a_meter_fact_not_a_grid_fact_need_2026.md`) | no gas meter matched **or** under 1,000 kWh in three years | 19.1% (a different definition, and larger) |
| CMA/GfK 2014 | household reports no mains gas | 15–17% |
| Ofgem CES 2017 | household reports electricity and no gas | 11% |

**A gas meter and gas heating are not the same thing, and the account follows the meter.** A
supplier sells a gas account to a home with a gas meter point. EHS AT3.5 shows that 98.7% of
metered homes are gas-heated, so the two nearly coincide in that direction. They do not coincide
the other way: a home without a meter can still burn LPG. The anchor the draw needs is
**P(gas meter) ≈ 84–86%** (EHS 86.0%, DESNZ 84%).

**The drawn founder homes are 93% gas, and that is a separate defect.** `draw_premise` (the
per-customer path founders take) draws heating from `published_heating_weights()`. That
function renormalises over the systems the model can represent and drops oil, communal and solid
fuel, so gas heating comes out at **90.7%**, against EHS's 86.0% metered. Founder homes also carry
`has_mains_gas_supply=None`. The premise-stock path (campaign and trickle) has drawn the meter
first and heating given the meter since 7 Oct (W2_20); the founders' path never got that change.

## 4. How a home with both fuels switches

| Source | Population | Both fuels, at once, to one company | Both, to two companies | Electricity only | Gas only |
|---|---|---|---|---|---|
| **Ofgem Consumer Engagement Survey 2017, §3**, n = 4,001 | households with both fuels that switched in the past 12 months (18% of them) | **17 of the 18 points switched both; 96% of those at the same time** (≈ 90% of switching homes) | not separated | **1 point switched one and not the other** (≈ 6%), fuel not given | — |
| Ofgem Customer Engagement Survey 2008 (Ipsos MORI), Q20, n = 538 | gas customers who switched in the past 12 months | **71%** | 5% | 12% | 7% (4% don't know) |

**So a GB home with both fuels switches as one household, and increasingly so.** By 2017,
inside this run's window, about 90–94% of switching homes with gas moved both fuels together. The
2008 figure of 71% is the bottom of the range, before the 2014–17 dual-fuel discounts and online
switching made it the norm. A **departure** follows the same logic: a household that leaves takes
both legs, because the comparison it acted on was a dual-fuel quote. The published record does not
separate departure from arrival. **GAP:** no published figure gives the share of saves or
win-backs that keep both legs; the departure-symmetry statement is reasoning from the arrival
data, not a measurement.

**Read QEP 2.7.1 with this in mind.** DESNZ counts transfer events, and a dual-fuel switch counts
as two (`population_draw.GB_DOMESTIC_TRANSFERS_BY_MONTH_THOUSANDS`). It counts meter points, not
households, so it bears on the seasonal shape and never on the dual-fuel share.

## 5. Incumbent books, challenger books, and Poesys's

**A supplier's split depends on its history, and the published books show it.** "G/E" below is
domestic gas meter points ÷ electricity meter points.

| Supplier | Year | Reading | Source |
|---|---|---|---|
| Octopus | FY to Apr 2025 | 7,273k electricity, 5,844k gas points: **G/E 0.80** | Consolidated Segmental Statement FY24/25, "Meter points" row — **read this session** |
| Utility Warehouse | FY15 | **80% of energy customers dual fuel** | CMA EMI Appendix 2.2, as reported by the advisor's research (17 Oct), not re-read here |
| First Utility | FY14 | 705k customers, **"over 90% … on dual fuel contracts"** | CMA EMI Appendix 2.2, as above |
| British Gas | 2023 | 5,981k electricity, 6,763k gas, 7,529k households: **~69% dual, ~21% gas only** | Centrica CSS 2023 and prelims, as above |
| Ex-regional electricity incumbents (E.ON, EDF, ScottishPower, npower, SSE) | 2015–2024 | **G/E 0.66–0.71**: an electricity-only tail from their home regions | their CSS statements, as above |

G/E barely moves with the dual share. A book whose every gas home is dual still reads about 0.86,
so G/E speaks to a book's share of gas homes, not to how they buy. **The dual-share anchor for a
challenger is the household share:** 80% (UW) to 90%+ (First Utility) of customers. At 84–86% gas
homes, 80% of customers means about 0.93 of gas homes.

**The market-wide 83% is the floor, not the centre, for Poesys.** It is pulled down by legacy
tails: British Gas's gas-only book and the ex-PES electricity-only books. Ofgem 2008 named "the
strong regional identities of the former regional electricity incumbents" and "the relatively high
number of electricity only customers" as reasons for low switching. Poesys opened in 2016 as a
challenger, and a challenger's book is built of switchers.

## 5a. What this means for each route into the book

| Route into the book | Published shape it should bear | Central | Range | Source |
|---|---|---|---|---|
| **Every drawn route: founders, trickle, campaign** | P(both fuels with us \| home has gas) | **0.90** | 0.83 (market stock) – 0.94 | Ofgem CES 2017 §3; UW / First Utility; CMA PF ¶9 as floor |
| | the remainder, one fuel | split evenly | — | CMA PF ¶9 (4m split electricity ≈ 4m gas-only); 2017 does not say which fuel |
| | P(home has a gas meter) | **0.86** | 0.84–0.86 | EHS AT3.5; DESNZ 2024 |
| A home with no gas | electricity only | 1.0 | — | by construction |

**Corrected the same day:** a first draft of this page gave the founders the market-wide 0.83
("a held book"), and called the challenger split a GAP. The advisor's supplier-accounts research,
landed at 10:03 UTC, fills that gap, and the founders now take the challenger shape. The
pre-registration records both.

## 6. Why the placeholder held for three months

Three separate failures, each with its own evidence:

1. **The knowledge existed and nothing pointed at it.** The 21 June pages held the answer. The
   13 July draw labelled its coin "documented placeholder, not claimed as anchored" and named no
   page to anchor it from. A labelled placeholder reads as owned debt, so no-one looked for its
   anchor. The founder count then rose from 13 to 80 (28 Aug) and to 400 (8 Oct), and nothing
   connected "this constant is unanchored" to "the population it shapes just grew thirtyfold".
2. **The 26 Aug ruling was applied where it was observed.** The director saw the funnel winning
   only electricity, and the fix (`_gas_leg_for`) was built in the funnel. The founders and the
   trickle reached the same coin through `iter_acquisition_events`. Nobody searched for every
   caller of `DEFAULT_COMMODITY_WEIGHTS`, so the ruling reached one of three routes.
3. **The 16 Sept finding accepted the book as a fact about the world.** "Eighteen gas-only
   accounts that cannot leave" was explained, and the accounts were given a way out. Nobody asked
   whether 27% gas-only accounts is a plausible book: published gas-only is about 8% of supplier
   customers (4m of ~50m fuel accounts) and comes from split homes.

The mechanism that would have caught all three is a **book-composition reality check against the
published aggregates in §2–§5**, run on the drawn book itself. It is the steer's first candidate,
and it is built: `tests/simulation/test_the_opening_book_bears_the_published_fuel_split.py`.

## 7. What is not established (GAP)

- **The supplier-type split** (§5): challenger figures are 2014–15 (UW, First Utility) plus one 2025 G/E (Octopus); OVO, Bulb, Good Energy and Co-op splits are not found.
- **Departure, save and win-back as one decision or two**: inferred from arrival data (§4).
- **Which fuel a single-fuel switcher moves**: 2008 says electricity more often (12% vs 7%); 2017
  does not say. Split evenly here, as a stated simplification.
- **Change over 2016–2025**: the anchors are 2014 (CMA), 2015 (CMA) and 2017 (Ofgem). Ofgem
  stopped publishing a dual-fuel share in its retail indicators after these; none was found for
  2020–2025.

## 8. What a supplier does with a customer who takes both fuels

*Added 2026-10-18, before the census of the company's decision routes (K8). Licence text read this
session in Ofgem's consolidated electricity supply standard conditions, "Consolidated to 1 August
2025". The gas licence mirrors it, and its paragraph numbers were not re-read here.*

**The licence knows the dual-fuel customer as one person.** SLC 1 defines the **Same Domestic
Customer** as one who "can reasonably be identified as being the same person which is supplied with
both electricity and gas from the licensee ... at the same Domestic Premises". It also defines a
**Dual Fuel Discount** as one applied "on the basis that the Same Domestic Customer is supplied with
both". So the regulator expects the supplier to recognise the household and allows it to price the
pair.

| Question | What the rules require or allow | Practice | Status |
|---|---|---|---|
| **One account?** | The licence speaks of a "Dual Fuel Account" (SLC 31H, 31I.5(b)) without requiring one. Each fuel is still its own supply contract, and its own registration (MPAN / MPRN, §4). | Suppliers hold one customer account with two supply points. This is universal in published supplier sign-up journeys, and no supplier is found publishing a share. | Practice: **GAP** for a measured share. Practitioner-obvious. |
| **One bill?** | Allowed. SLC 31H lets a Dual Fuel Account carry **one** optical label holding both fuels' data items. Each fuel's consumption, charges and comparison must still be shown. | A single combined bill or statement. | Allowed; practice is **GAP** for a measured share. |
| **One direct debit?** | No condition requires or forbids it. SLC 27.8 requires instalments to reflect the customer's **ability to pay**, which is a fact about the payer and not about a fuel. | One DD amount covering both fuels is the common practice. Some suppliers show a per-fuel split of it. | **GAP:** no published share of dual accounts on one DD. Practitioner-obvious, as with the half-month DD (CLAUDE.md, K4). |
| **One renewal / retention offer?** | SLC 31I.5(b): a price-change or end-of-fixed-term notice "may be provided as a **Combined** Relevant Contract Change Notice where the Domestic Customer is subject to a Dual Fuel Account". It must meet each fuel's requirements "in a single document". Optional, not required. | Fixes are sold and renewed as dual-fuel products, with one term and one end date. Each fuel's rates are still set per fuel, because the cap is per fuel (§4). | Rule read. Practice of a single end date is **GAP** for a measured share. |
| **A loss on one fuel: what does it say about the other?** | **Objections are per fuel.** SLC 14.4(a) lets the electricity supplier block a transfer when Outstanding Charges are due, and "Charges" means Charges for the Supply of Electricity (SLC 1). So a gas debt cannot block the electricity switch under the electricity licence. Ofgem's 2016 objections review saw the duplication: debt-objected customers are "around half the number of objections raised (partly because of dual fuel customers trying to switch gas and electricity accounts ...)". | A loss notification arrives per meter point. By §4, 17 of 18 switching dual homes move both fuels, and 96% of those move them at once. **A loss notice on one fuel of a dual household is therefore, about nine times in ten, the household leaving.** The other fuel's notice follows within days, or has already arrived. | Mechanism read. Departure symmetry is **inferred** (§4, §7). |
| **The final bill** | SLC 27.17: a final bill within 6 weeks of the transfer or termination, **per fuel's contract**. A move-out ends both contracts at once, because the premises is the same. | One closing statement for the account. | Rule read. |
| **Collections** | Debt is owed per fuel's Charges, and the ability-to-pay duty (27.8) is per customer. | Payment plans, when the payer holds both fuels, are set against the account balance. | **GAP:** no published practice on netting one fuel's credit against the other's debit. |

**What this means for the company's decisions.** The licence makes the rate, the objection and the
final bill per fuel. It makes everything that rests on the customer's own position per household:
ability to pay, the household's ability to recognise the bundle, and above all its **decision to
stay or leave**, which by §4 is one decision about nine times in ten. So a supplier decision that
rests on whether the customer stays has two sides that must be read together:
- what the household is worth, from both legs' margins;
- whether it leaves, which is one hazard and not two.

Such decisions include a save, a retention price, a renewal cut and an advice offer. A decision
priced on one leg prices half a household. A save made on one fuel's loss notice, sized on that
fuel's margin, values the departure at about half of what is actually leaving.

**Design choices the build makes (K8), and why.**
- The household is the company's **billing account** (`billing_account`), which the world fills
  from the premises. That is the "Same Domestic Customer" of SLC 1, as a real supplier would
  recognise it at sign-up. It never reads `simulation.household.household_of` (the epistemic wall).
- Rates and objections stay per fuel, as the licence sets them.
- A decision on staying or leaving, and the value at stake in it, is taken once per billing
  account over the sum of its legs. Where a route still decides per leg, the census in
  `docs/staging/` names it, and the fix sits behind a default-off decision-policy switch until it is
  measured.

## Sources

- CMA, *Energy market investigation: Summary of provisional findings report*, 7 July 2015, ¶9 and
  Table 1. https://assets.publishing.service.gov.uk/media/5a8059e6e5274a2e8ab4fa64/EMI_PFs_Summary.pdf
- CMA, *Energy market investigation: Final report*, 24 June 2016, ¶10.
  https://assets.publishing.service.gov.uk/media/5773de34e5274a0da3000113/final-report-energy-market-investigation.pdf
- Octopus Energy, *Consolidated Segmental Statement, FY ended 30 April 2025*.
  https://a.storyblok.com/f/275131/x/b758c36b3a/octopus-energy-css-fy24_25-apr26-2.pdf
- The advisor's research for the director, 17 Oct 2026:
  `docs/staging/advisor/DIRECTOR_EVIDENCE_HOW_GB_HOUSEHOLDS_BUY_BOTH_FUELS_2026-10-17.md`. It also
  holds the switching mechanics (per-fuel registration, erroneous transfers ~0.5% of switches).
- CMA / GfK NOP, *CMA customer survey — energy investigation*, Feb 2015, ¶41, Figure 2.
  https://assets.publishing.service.gov.uk/media/54e75c53ed915d0cf700000d/CMA_customer_survey_-_energy_investigation_-_GfK_Report.pdf
- Ofgem / Ipsos MORI, *Consumer engagement in the energy market since the Retail Market Review:
  2017 survey findings*, §2.3 and §3.
  https://www.ofgem.gov.uk/sites/default/files/docs/2017/10/consumer_engagement_survey_2017_report.pdf
- Ofgem / Ipsos MORI, *Customer Engagement Survey*, 29 Aug 2008, Summary and Q20.
  https://www.ofgem.gov.uk/ofgem-publications/57592/customerengagementsurveyfinal1-pdf
- DESNZ, *Subnational electricity and gas consumption summary report 2024*.
  https://www.gov.uk/government/statistics/subnational-electricity-and-gas-consumption-summary-report-2024
- EHS 2017-18 Energy Report, Annex Table 3.5, as transcribed in `simulation/premise_population.py`.
- Ofgem, *Electricity supply licence: standard conditions*, consolidated to 1 August 2025 (SLC 1
  definitions of Same Domestic Customer and Dual Fuel Discount; 14.4; 27.8; 27.17; 31H; 31I.5).
  https://www.ofgem.gov.uk/sites/default/files/2023-03/Electricity%20Supply%20Standard%20Consolidated%20Licence%20Conditions%20-%20Current.pdf
- Ofgem, *Decision on review of domestic objections*, July 2016 (the dual-fuel doubling of debt
  objections). https://www.ofgem.gov.uk/system/files/docs/2016/07/decision_on_review_of_domestic_objections.pdf
