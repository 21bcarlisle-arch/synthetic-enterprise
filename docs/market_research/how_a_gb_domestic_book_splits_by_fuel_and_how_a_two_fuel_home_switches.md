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

**The campaign is the third route, and until 19 Oct it did not bear this shape.** It quoted every
prospect for electricity, then `_gas_leg_for` added a gas leg to every won home with a gas meter. So
100.0% of its won gas homes were dual, measured over 1,750 homes and 8 seeds
(`tools/world_claims.py`). Every published book in §5 has split homes; none is 1.0. A campaign win
now takes its fuel from the same coin as a founder or a trickle arrival
(`population_draw.fuel_arrangement`), drawn on the won home's own premise:

- **dual** (0.90 of gas homes): electricity and gas, one household, two supply points `X` and `Xg`;
- **split, electricity with us** (half the remainder): the electricity account only, and the home's
  gas stays with a rival;
- **split, gas with us** (the other half): the gas account only, under the home's own id `X`, as a
  gas-only founder is.

*Why both fuels and not electricity alone.* The campaign's quote is drawn as electricity because
the prospect draw needs a fuel to draw an EAC. But the win does not read the fuel: the funnel
decides on the credit check, the price differential and the prospect's own elasticity, none of
which is per fuel. So a gas-only win is no less consistent with the quote than an
electricity-only one, and the published split (CMA PF ¶9: about 4m split electricity against 4m
gas-only) is even. Making every split win electricity-only would give the campaign no gas-only
accounts. That is the same "always" shape this change removes, only on the other fuel. **GAP:** no
published figure says which fuel a one-fuel switcher moves (§4, Ofgem 2017 gives no fuel), so the
even split is the market stock's shape applied to switchers.

**Corrected the same day:** a first draft of this page gave the founders the market-wide 0.83
("a held book"), and called the challenger split a GAP. The advisor's supplier-accounts research,
landed at 10:03 UTC, fills that gap, and the founders now take the challenger shape. The
pre-registration records both.

## 5b. What the drawn world is checked against

These are the figures above, stated as claims the drawn book must bear. `tools/world_claims.py`
reads this block and measures each route into the book (founders, trickle, campaign) as the
production draw makes it, pooled over eight seeds (about 1,700 homes for the founders and for the
campaign, about 30 for the trickle). A claim outside its band fails
`tests/tools/test_world_claims.py`, and it is printed in the Monday step. Each band is the published
range, widened by 3 sd of sampling noise at that pool size (about 2 to 2.5 points). Change a figure
here and the check moves with it. This block is the only place the band is written.

```world-claims
- id: dual_share_of_homes
  measure: dual_share_of_homes
  band: [0.70, 0.85]
  source: "Floor: the whole market, 72% of households (CMA/GfK 2014 ¶41). Ceiling: a challenger built by switching, 80% (UW) to 90%+ (First Utility) of customers dual (CMA EMI App. 2.2), at 84-86% gas homes. §2, §5."
- id: dual_share_of_gas_homes
  measure: dual_share_of_gas_homes
  band: [0.81, 0.96]
  source: "§5a: P(both fuels with us | home has gas) 0.83 (market stock, CMA PF ¶9) to 0.94 (Ofgem CES 2017 §3; UW, First Utility)."
- id: gas_home_share
  measure: gas_home_share
  band: [0.815, 0.885]
  source: "§3: P(gas meter) 84% (DESNZ subnational 2024) to 86% (EHS 2017-18 AT3.5). The off-grid share is its complement, 14-16%."
- id: gas_only_share_of_homes
  measure: gas_only_share_of_homes
  band: [0.0, 0.15]
  source: "§2: a gas-only account is a split home's gas leg, 4m of 31m supplier customers (13%, CMA PF ¶9)."
- id: gas_only_homes_without_gas
  measure: gas_only_homes_without_gas
  band: [0.0, 0.0]
  source: "§2: Ofgem CES 2017 finds under 1% of households with gas and no electricity, so a gas-only account is a split home whose electricity is elsewhere. It sits on a home with a gas meter."
```

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
| **One collections journey?** | SLC 27.8 sets ability to pay as a fact about the payer, not about a fuel. Each fuel is still its own contract, so a credit is refunded on its own fuel (SLC 27.16), and from 22 Jan 2021 a credit on one may be set off against debt on the other. | One account in arrears gets one reminder ladder and one statement of what is owed across both fuels. | **GAP** for a published statement of it. Practitioner-obvious. **Built 2026-10-25:** the company's ledger is the billing account, and each fuel's bill is still its own item on it (`background/live_payment_triad.account_of`). Push payments clear oldest-first across both fuels. One mandate covers both. A debt meter recovers at the electricity rate. |
| **One renewal / retention offer?** | SLC 31I.5(b): a price-change or end-of-fixed-term notice "may be provided as a **Combined** Relevant Contract Change Notice where the Domestic Customer is subject to a Dual Fuel Account". It must meet each fuel's requirements "in a single document". Optional, not required. | Fixes are sold and renewed as dual-fuel products, with one term and one end date. Each fuel's rates are still set per fuel, because the cap is per fuel (§4). | Rule read. Practice of a single end date is **GAP** for a measured share. |
| **A loss on one fuel: what does it say about the other?** | **Objections are per fuel.** SLC 14.4(a) lets the electricity supplier block a transfer when Outstanding Charges are due, and "Charges" means Charges for the Supply of Electricity (SLC 1). So a gas debt cannot block the electricity switch under the electricity licence. Ofgem's 2016 objections review saw the duplication: debt-objected customers are "around half the number of objections raised (partly because of dual fuel customers trying to switch gas and electricity accounts ...)". | A loss notification arrives per meter point. By §4, 17 of 18 switching dual homes move both fuels, and 96% of those move them at once. **A loss notice on one fuel of a dual household is therefore, about nine times in ten, the household leaving.** The other fuel's notice follows within days, or has already arrived. | Mechanism read. Departure symmetry is **inferred** (§4, §7). |
| **The final bill** | SLC 27.17: a final bill within 6 weeks of the transfer or termination, **per fuel's contract**. A move-out ends both contracts at once, because the premises is the same. | One closing statement for the account. | Rule read. |
| **Collections** | Debt is owed per fuel's Charges, and the ability-to-pay duty (27.8) is per customer. **Since 22 Jan 2021, SLC 27.8D gives the customer a contractual right to offset one contract's credit against debt on any other supply contract, gas included (§8b).** | Payment plans, when the payer holds both fuels, are set against the account balance. At least one large supplier's terms let **either side** net across accounts (§8b). | Rule read (§8b). *Corrected 2026-10-18: this row said "no published practice on netting"; the licence itself has a netting right.* How often suppliers net unprompted is still **GAP**. |

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

### 8a. A save made to a household that is leaving with both fuels

*Added 2026-10-18, before the household save in `company/crm/save_offer.py` was built (K8).
Searched this pass: SLC 14 and 14A (read for the save page and re-read here for objections), Energy
UK's Energy Switch Guarantee, the CMA's 2016 final report, and
`a_save_offer_against_the_switching_rules_and_the_seam.md` §1c, §6 and §7.*

| Question | What the rules or published evidence say | Status |
|---|---|---|
| **May one save cover both fuels?** | Yes. Nothing read forbids it. A save is a Fixed Retention Tariff under the SLC 22B derogation (save page §1d), and SLC 1's **Dual Fuel Discount** lets a supplier price a tariff on the basis that the Same Domestic Customer takes both fuels. Each fuel's rate must still be set and shown per fuel (SLC 31H, 31I.5(b), §8). | Rule read. |
| **May the loser block either leg to keep the other?** | No. Objections are per fuel and only for that fuel's Outstanding Charges (SLC 14.4(a), §8). A save works only if the household chooses to stay (save page §1c). | Rule read. |
| **Does the Switch Guarantee say anything about saves?** | No. Its commitments cover the switch itself: no interruption, free, 21 days at most, the gainer arranges it, and an accurate final bill. A 2014 MoneySuperMarket response to Ofgem says a dual-fuel discount only applies once both supplies have transferred, because the two fuels transfer separately (found by search; the PDF was not read in full). | Read. Nothing on saves. |
| **What is the household leaving for?** | **A dual-fuel deal.** The best-deal gap the save matches is Ofgem's own series, and *"All figures are based on a typical domestic dual fuel customer paying by direct debit"* (`cheapest_fix_against_the_default_tariff_gb_2016_2025.md` §0). By §4, about nine switching homes in ten move both fuels together. | Published (the gap). Inferred for a departure (§4). |
| **How does a household weigh a save on one fuel when it is leaving with both?** | **Not published.** No survey, regulator or practitioner source found separates a one-fuel save from a two-fuel save, or gives the share of saves that keep both legs (§4 GAP). | **GAP.** |

**What follows from what is published.** The household's reason to leave is measured on its combined
bill: the market's cheapest dual-fuel deal against the default. A save that matches that gap on one
fuel answers the reason only on that fuel's share of the bill, and the household is asked to stay on
both fuels for it. A save that answers the reason matches the gap on **both** legs. Neither the rules
nor any published practice prevents that. The supplier then needs a second check: whether the save
loses money **on the household**, which is the sum of both legs' margins at the save rates, and not
on each leg alone. That is the same reasoning as C35 (§8).

**What our code does (discovery, not evidence).** The world rolls a dual household's departure once,
on its electricity leg (`simulation.customer_events.departure_decision_leg`), and sends a loss
notice for **every** point the household holds (`run_phase2b`, `supply_points_on_supply`). The
company then answers only the electricity point's notice. It prices the save on electricity's
renewal rate and electricity's floor. The gas point's Invitation to Intervene is received and filed,
and nothing reads it. The world's re-asked roll weighs only the electricity rate. Measured on the
live book at `27b6798ec` (`live_population()`, 6.3 s): **788 supply points in 447 households, 341
of them dual, and all 341 hold both legs from one acquisition date.** So every dual departure is a
pair of loss notices on one date: 341 of 447 households (76%) and 682 of 788 points.

**Design choices the household save makes, and why.**
- **One offer per billing account, over every leg whose notice the company holds.** Each leg keeps
  its own fuel's rate (the licence sets rates per fuel). Each leg's target is that fuel's published
  default × (1 − the published dual-fuel gap). No leg is ever offered more than its renewal.
- **The floor is the household's.** The match stands where the household's summed margin over cost
  at the save rates is at least zero: Σ annual consumption × (save rate − cost floor) ≥ 0. Where it
  is not, each leg falls back to its own floor, which is today's per-leg answer. This is a design
  choice. The rules allow it (Dual Fuel Discount), but it is not documented practice.
- **The household's own weighing stays the world's.** How a household weighs the pair is the GAP
  above. The company's offer must not depend on it. Wiring the world to weigh both legs' rates
  belongs to the run, and is the next item in the finding.
- **Off by default** (`DecisionPolicy.save_offer_decides_per_household`) until the world can weigh
  the pair. Under the switch off the company answers exactly as it does today.

**Where the run answers both notices (step 1b; added 2026-10-19, before the run caller was built).**
Nothing new was searched for this step. It is a choice about where in our run the one decision is
taken, and what each leg's inputs are at that moment. The rules above already allow it.
- **When.** At the departure roll on the decision leg, once the loss notices are filed. A supplier
  answers an Invitation to Intervene inside the objection window (save page §1c). Both legs' notices
  carry the same effective date, so both are answered in that one reply. A leg whose notice the
  company does not hold is left out of the decision. Before CSS (requests from 18 July 2022) no
  notice arrives in time, so no household is decided at all.
- **Each leg's inputs are what the company holds when it answers.** These are the leg's renewal offer
  as struck for that start, its fuel's published default ex VAT, its cost floor (`term_cost_floor`),
  and the company's own annual volume for the point. **Design choice, and a limit of our run:** the
  other leg's renewal offer is read as first struck for the start. The run's later adjustments to that
  leg's rate (premium, cap clamp) are applied only when that leg is priced, after the roll. A real
  supplier would have issued both renewal notices together, so it would hold both final offers.
  Where the later adjustment lands **below** the save, the leg is billed the lower rate. A save never
  raises a price.
- **What carries.** A household saved at the roll keeps both legs. The other leg is billed its save
  rate for that term. It does not teach the stayers' premium, for the same reason the decision leg's
  save does not. No rival's ledger reads it.
- **What does not change in 1b.** The world still re-asks the departure roll on the decision leg's
  rate alone. Weighing the combined bill is step 1c: a world fidelity choice under the GAP above, with
  its own prediction filed first.

### 8b. One fuel in credit, the other in arrears: may the supplier net them?

*Added 2026-10-18, before any netting build (K8), for item 3 of
`docs/staging/WORKER_FINDING_THE_COMPANY_DECIDES_A_DUAL_HOUSEHOLD_PER_LEG_AND_C35_CHARGED_IT_TWO_RISES_FOR_ONE_BENEFIT_2026-10-18.md`
§4. Read this pass at source: the electricity SLCs consolidated to 1 Aug 2025 (SLC 27 in full,
27.1–27.18) and to 14 Apr 2022 (27.8D present); Ofgem's Supplier Licensing Review decision of
17 Nov 2020, §5; Ofgem's DD compliance review progress update (2 Feb 2023); Ofgem's letter to the
ESNZ Committee on credit balances (29 Nov 2023); Citizens Advice, "Claim back credit from your
energy supplier"; EDF Energy, Residential Terms & Conditions R1436.06/24.v4 (June 2024). The gas
licence was not retrieved (its 2025 URL served HTML); the 2020 decision drafts 27.8D for both
licences with "[gas/electricity]".*

**Answer: the customer may, by licence; the supplier may, by its own terms; and nothing published
says a direct debit review must.**

| Question | What the published record says | Status |
|---|---|---|
| **May the customer net them?** | **Yes, since 22 Jan 2021.** SLC 27.8D: the licensee must ensure the terms of each Domestic Supply Contract provide "for the right for the customer to offset any amount owing to the customer pursuant to the contract against any amounts owed by the customer under any other Domestic Supply Contract or under any contract for the supply of gas to premises (whether or not the licensee continues to hold an Electricity Supply Licence or Gas Supply Licence)". 27.8E makes it survive the licence's end. It came from the Supplier Licensing Review (decision 17 Nov 2020, §5.7; in force 22 Jan 2021, "some suppliers may need additional time", §5.6). Its purpose was supplier failure: an administrator chasing a debt must honour the customer's credit (§5.1–5.2). | Rule read. |
| **May the supplier net them without being asked?** | **The licence neither grants nor forbids it.** 27.8D is the customer's right. EDF's residential terms (cl. 17.e) grant it both ways: "Either of us can use any credit you have on any energy account with us to pay off debt you owe us or our group companies, including in relation to other energy accounts." | Rule read; one supplier's terms read. Share of suppliers with such a term: **GAP**. |
| **Is the credit per fuel?** | **Yes.** SLC 27.16 defines "Credit" as the amount by which payments "under or in accordance with the relevant Domestic Supply Contract" exceed the Charges due "under that Domestic Supply Contract". Each fuel is its own contract (§8). | Rule read. |
| **May a refund of one fuel's credit be withheld for the other's debt?** | SLC 27.16: the supplier must refund accumulated Credit on request "save where it is fair and reasonable in all the circumstances" not to, and must give its reasons. No Ofgem text read says another contract's debt is, or is not, such a reason. Citizens Advice gives only "a small amount of credit on your account during summer" as an example of a good reason. | **GAP** (the rule is read; its application to cross-fuel debt is not published). |
| **Must the direct debit review net them?** | **Nothing says so.** SLC 27.15 sets "the fixed amount of the regular direct debit payment" per contract, on the quantity "of electricity" supplied under it. Ofgem's Feb 2023 update speaks of "a consumer account" in credit (lower the DD toward zero over 12 months) or in debit (commonly add it to the DD over 12 months) and does not say whether an account means one fuel or both. Its Nov 2023 letter's "net balance" is net of unbilled consumption, not of the other fuel. | **GAP.** |
| **Ability to pay** | SLC 27.8 and 27.8A: instalments must reflect "the Domestic Customer's ability to pay", using "all available information". A household's credit on the other fuel is information about what it can pay. | Rule read. Using that credit is an inference, not a rule. |

**Before 2021.** For 2016 to 21 Jan 2021 of the run window, no licence condition gave the customer
a netting right. Netting then rested only on the contract terms. Pre-2021 terms were not read:
**GAP**.

**What follows for the company.**
- When a dual household holds a credit on one leg and a debt on the other, it has a right, from
  2021, to have one set against the other. A supplier that chases the debt while holding the credit
  is chasing money that the household can lawfully set off. A supplier that refunds the credit while
  the other leg is in arrears pays out money that it may lawfully keep. Both are the billing
  accuracy problem in the finding's §4 item 3.
- A supplier that nets unprompted is acting on its own terms, not on a licence duty. So netting is
  a design choice the rules allow. It is not a choice the rules require.
- **The design choices are left to the build item, and nothing is built here.** Three open choices,
  each allowed: (a) net only when the customer asks (the licence floor); (b) net at the points
  where money moves: before a refund is paid, before a debt is chased, at the final bill; (c) also
  size one DD from the household's combined balance at the annual review. Only (a) is required.
  (c) needs the review GAP above answered first.

**GAP, as the practitioner question for the advisor channel (K4: the published record was read
first; the answer is not in it):**

> "Take a dual-fuel household on one supplier, paying both fuels by fixed direct debit, which is
> £120 in credit on gas and £80 in arrears on electricity. In practice, does a GB supplier:
> (1) net the two automatically, and if so, when: at each bill, at the annual DD review, or only
> before a refund or a debt action;
> (2) set one combined DD from the combined balance at the review, or review each fuel's DD on its
> own balance; and
> (3) when the household asks for the gas credit back, treat the electricity arrears as the 'fair
> and reasonable' ground under SLC 27.16 to keep the credit?
> And did this change when SLC 27.8D came in, in January 2021?"

**Design choices the offset makes (K8), and why.** *Added 2026-10-19, before the offset was built
in `simulation/dd_balance_book.py` behind `DecisionPolicy.dd_review_offsets_dual_fuel_legs`
(default off). It takes choice (b) above. (c) still waits on the review GAP.*

- **Where it acts.** It acts at the two actions where the company seeks a direct debit leg's debit:
  the annual review, when it seeks the balance (`dd_review.REVIEW_SEEKS_BALANCE`), and a closed leg's
  final bill. *What our code does (discovery, not evidence):* these are the only places a level-DD
  debit is asked for. The in-run dunning desk (`arrears_engine.select_dunning_step`) reads one leg's
  ledger of missed payments. That ledger takes each bill as billed, so it carries no level-DD credit
  to set off. An offset there would need the other leg's ledger. It is not built, and it waits until
  a reading shows a desk escalation on a leg whose other ledger is in credit.
- **The bar comes first.** SLC 21BA's bar is taken on the debit first, as today. The offset is the
  smaller of what is left to seek and the other leg's credit. So a credit never pays a charge the
  supplier may not recover. Whether SLC 21BA reaches a set-off at all is **GAP**. This order is the
  one that errs against the company.
- **The company offers the offset unprompted, at the action.** The licence gives the right to the
  customer (27.8D) and lets a supplier's terms net both ways (EDF cl. 17.e). The company does not
  wait to be asked. How many suppliers net unprompted is **GAP**.
- **The household is taken to accept.** The credit it holds is set against a debt it owes, and the
  right is its own. Nothing published gives a share of households who decline (**GAP**).
- **A leg covered in full is not escalated.** Where the other leg's credit is at least the debt left
  after the bar, the review adds no step-up. Where it covers part, the step-up recovers only the rest
  over 12 months.
- **The credit leg pays exactly what it spends.** Each contract keeps its own balance (SLC 27.16).
  The credit leg's balance falls by the offset from its next bill. The debit leg's oldest unbarred
  shortfall is settled first. A later bar then finds less old debt, so the bars fall when the switch
  is on. That is a real effect: the debt was recovered before it aged.
- **Only while both supplies are the company's.** At a review the other leg must still be billing.
  At a final bill it may close on the same day, which is how a dual household leaves (§4).
- **From 22 Jan 2021 only.** No offset is offered at an action dated earlier. Pre-2021 contract
  terms were not read (**GAP**), and inventing a netting habit for them would be a number picked
  because a number was needed.
- **Off by default, then on.** With the switch off, a leg is booked as if its household had no
  other fuel, byte for byte. *Switched on for every standing policy on 2026-10-19*, after its on
  arm was graded against a stated rule on `ad8afadc5`. On the never-seeks review it acts only at a
  dual leaver's final bills: 8 offsets, £263.65, and no barred pound moves
  (`docs/staging/records/SEAT_VERDICT_EACH_DEFAULT_OFF_DUAL_FUEL_SWITCH_ON_WITH_ITS_GRADE_OR_OFF_WITH_ITS_REASON_2026-10-19.md` §3).

**What it touches on the publish run** (`run_output_8b6fea024_20261019T033010Z`, read through
`tools/dual_leg_opposite_signs` and the book with the switch on; the prereg's grade is item 1's).
Of 289 dual households with both legs on DD, 114 are open at run end, and 12 of those (0.105) hold
opposite signs then. Across the run, 250 of 289 (0.87) hold opposite signs in at least one month, so
the right is common, not rare. The money it moves is small, because the bar takes old debt first:
- **On the standing review (never seeks the balance):** the final bill is the only action. 8
  households are offset, £263.91 in all.
- **On the review that seeks:** 72 review offsets (£2,754.62) and 4 at final bills (£86.69), in 65
  households. 47 of 1,146 review step-ups are never made, because the other leg covers the debt. The
  review bars fall from £26,750 to £26,041.

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
- Energy UK, *Energy Switch Guarantee* (energy-uk.org.uk/our-work/energy-switch-guarantee/), the
  commitments as listed by the save page's S11, read 2026-10-08.
- Ofgem, *Supplier Licensing Review: Ongoing requirements and exit arrangements*, decision,
  17 Nov 2020, §5.1–5.7 (SLC 27.8C–E; in force 22 Jan 2021).
  https://www.ofgem.gov.uk/sites/default/files/docs/2020/11/201117_-_slr_decision_doc_final_v.2.pdf
- Ofgem, *Electricity Supply SLC amendments*, consolidated to 14 April 2022 (27.8D present).
  https://www.ofgem.gov.uk/sites/default/files/2022-05/Electricity%20Supply%20SLC%20amendments.pdf
- Ofgem, *Direct Debit Market Compliance Review: Progress Update*, 2 Feb 2023.
  https://www.ofgem.gov.uk/decision/direct-debit-market-compliance-review-progress-update
- Ofgem, letter to the Chair of the ESNZ Committee on customer credit balances, 29 Nov 2023.
  https://www.ofgem.gov.uk/sites/default/files/2023-12/ESNZ%20Committee%20letter%20on%20CCBs.pdf
- Citizens Advice, *Claim back credit from your energy supplier*, read 2026-10-18.
  https://www.citizensadvice.org.uk/consumer/energy/energy-supply/claim-back-credit/claim-back-credit-from-your-energy-supplier/
- EDF Energy, *Residential Terms & Conditions*, R1436.06/24.v4, cl. 17.e.
  https://www.edfenergy.com/sites/default/files/r1436.pdf
- MoneySuperMarket, response to Ofgem, April 2014 (dual-fuel discount applies once both supplies
  transfer). https://www.ofgem.gov.uk/sites/default/files/docs/2014/04/moneysupermarket_response_0.pdf
