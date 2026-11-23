# How far below the default tariff was the cheapest fix, GB domestic, 2016-2025?

**Knowledge:** acquisition-and-retention-economics

**Held as data (2026-10-12):** the quarterly gap series is `docs/domain_artefact_library/regulatory/gb_best_deal_gap_to_default.json`, read by the company through `company/interfaces/save_offer.published_best_deal_gap_share`.

**Research completed 2026-10-10, discovery agent.** Answers the question behind a save offer's
size: when a supplier price-matches a leaving household (CSS Invitation to Intervene, from 18 July
2022; see `a_save_offer_against_the_switching_rules_and_the_seam.md`), what gap to the market's best
deal is it actually matching? Read against what the repo already holds: `churn_price_elasticity.md`
(its "Savings" column, qualitative, not independently re-sourced per its own refutation notice),
`svt_rates_active_passive_2016_2025.md` (SVT/cap unit rates, confirmed consistent below), and
`what_a_renewal_decision_is_for_a_gb_domestic_customer.md`. **Per the discovery agent's epistemic
wall, `simulation/market_switching_propensity.py` was not read.** The comparison below is against
`churn_price_elasticity.md`'s own published "SIM Calibration" savings column, which is the nearest
in-scope description of what `MARKET_SAVINGS_BY_YEAR` holds; whoever owns that constant should diff
it against the table here directly.

## 0. The source, and why it settles this at H confidence

Ofgem's Retail Market Indicators data portal page renders its charts as client-side Highcharts via
`app.everviz.com`; the static HTML is JS-rendered and un-scrapable (consistent with five other
findings in this repo noting the same). **The everviz embed itself, however, serves the full
underlying data table as a CSV string inside its page JSON** — not just the rendered chart.
Fetched 2026-10-10 from `https://app.everviz.com/embed/g53GfRDaf`, which is the embed behind the
chart Ofgem titles **"Retail price comparison by company and tariff type: Domestic (GB)"** on
`https://www.ofgem.gov.uk/news-and-insight/data/data-portal/retail-market-indicators` (chart
catalogue confirmed via the page's own `data-js-chart-modal-data` attributes, matching chart id to
title exactly). Ofgem's own methodology note on this chart (fetched the same pass): *"Source:
Energylinx (Until May 2017) and Energyhelpline (June 2017 to May 2022) and Cornwall Insights (June
2022 onwards) ... compares [suppliers'] average standard variable tariffs with the default tariff
cap and the cheapest tariffs available in the market (including white label tariffs) ... All figures
are based on a typical domestic dual fuel customer paying by direct debit."* This is Ofgem's own
published series, monthly, January 2012 to August 2026, with columns:

| column | what it is |
|---|---|
| Average SVT (large legacy suppliers) | the pre-cap "default tariff" proxy for 2012-2018 |
| Average SVT (other suppliers) | same, mid-tier/challenger suppliers |
| **Average fixed tariff** | average price of *all* fixed-term deals on sale that month (not capped; this is what a new switcher would be quoted on average) |
| Cheapest tariff (large legacy suppliers) | average, across the legacy suppliers, of each one's own cheapest tariff |
| **Cheapest tariff (all suppliers)** | average, across *every* supplier, of each one's own cheapest tariff — Ofgem's own text calls this **"the market cheapest tariff"** (e.g. its Aug-2026 commentary: *"The market cheapest tariff increased to £1,499"*, which matches this column exactly) |
| Cheapest tariff (basket) | a market-share-weighted basket of cheapest tariffs (methodology not fully read this pass) |
| Default tariff cap level | the published Ofgem cap, present from January 2019 |

Ofgem's own methodology text excludes "tariffs restricted to certain regions" and (for the sibling
"Average tariff prices by supplier" chart, same publisher, same methodology section) excludes
**acquisition-only and retention-only tariffs**, so this is a *generally-available* cheapest deal,
not a hidden/returning-customer-only one. **ESTABLISHED, confidence H**: this is Ofgem's own
published number, not a re-derivation.

## 1. TDCV basis, confirmed against Ofgem's own text (fetched the same pass)

> *"As of July 2026, typical domestic consumption values (TDCV) for a medium consumer are
> 9,500kWh/year for gas and 2,500kWh/year for electricity... The previous TDCV that came into effect
> as of October 2023, was 11,500kWh/year for gas and 2,700kWh/year for electricity... "* and
> separately, on the sibling chart's methodology: *"As of October 2023, TDCV... are 11,500kWh/year
> for gas and 2,700kWh/year for electricity... The previous TDCV that came into effect as of April
> 2020, was 12,000kWh/year for gas and 2,900kWh/year for electricity."*

| Period | Elec (kWh/yr) | Gas (kWh/yr) | Confidence |
|---|---|---|---|
| to Mar 2020 | 3,100 | 12,000 | **M** — not re-quoted in this pass's Ofgem text; standard figure from the 2019 cap launch, consistent with the 2019 cap levels below |
| Apr 2020 – Sep 2023 | 2,900 | 12,000 | **H** — directly quoted above |
| Oct 2023 – Jun 2026 | 2,700 | 11,500 | **H** — directly quoted above, and matches the task's expectation exactly |
| Jul 2026 onward (out of window) | 2,500 | 9,500 | **H** — context only, outside 2016-2025 |

The chart itself is computed "using the TDCV applicable at each date", so every row below already
carries the right-for-its-date consumption basis; the table does not need a separate adjustment.

## 2. The headline table: default tariff vs. the market's cheapest, 2016-2025

Gap = default − "cheapest tariff (all suppliers)". Share = gap ÷ default. 2016-2018 default is the
large-legacy SVT average (no cap existed); from Jan 2019 it is the published cap level. All
**ESTABLISHED** (read directly off the Ofgem series) unless marked.

| Period | Default (£/yr) | Cheapest fix, market (£/yr) | Gap (£/yr) | Gap as % of default | Mark |
|---|---|---|---|---|---|
| 2016 (annual avg, n=12mo) | 1,071 | 750 | 322 | 30.0% | ESTABLISHED |
| 2017 (annual avg) | 1,117 | 828 | 289 | 25.9% | ESTABLISHED |
| 2018 (annual avg) | 1,175 | 847 | 328 | 27.9% | ESTABLISHED |
| Jan 2019 | 1,137 | 941 | 196 | 17.2% | ESTABLISHED |
| Apr 2019 | 1,254 | 880 | 374 | 29.8% | ESTABLISHED |
| Oct 2019 | 1,179 | 864 | 315 | 26.7% | ESTABLISHED |
| Apr 2020 | 1,127 | 758 | 369 | 32.7% | ESTABLISHED |
| Oct 2020 | 1,042 | 823 | 219 | 21.0% | ESTABLISHED |
| Apr 2021 | 1,138 | 859 | 279 | 24.6% | ESTABLISHED |
| Jul 2021 | 1,138 | 859 | 279 | 24.6% | ESTABLISHED, but see §3 — fixed-tariff quotes already rising fast |
| **Sep 2021** | 1,138 | 1,078 | 60 | 5.3% | ESTABLISHED — the gap collapses inside one month |
| Oct 2021 | 1,277 | 1,213 | 64 | 5.0% | ESTABLISHED |
| Apr 2022 | 1,971 | 1,872 | 99 | 5.0% | **ESTABLISHED but flagged — see §3**: identical to Jul/Sep 2022 |
| Jul 2022 | 1,971 | 1,872 | 99 | 5.0% | flagged, as above |
| Sep 2022 | 1,971 | 1,872 | 99 | 5.0% | flagged, as above |
| Oct 2022 | 2,500 | 2,375 | 125 | 5.0% | **flagged — this "default" is the EPG level, not the cap ceiling; see §4** |
| Jan 2023 | 2,500 | 2,375 | 125 | 5.0% | flagged, as above (unchanged for 6 straight months) |
| Apr 2023 | 2,500 | 2,450 | 50 | 2.0% | flagged, as above |
| Jun 2023 | 2,500 | 1,975 | 525 | 21.0% | ESTABLISHED, one-month transitional spike as EPG wound down |
| Jul 2023 | 2,074 | 1,974 | 100 | 4.8% | ESTABLISHED — quarterly cap cadence begins |
| Oct 2023 | 1,834 | 1,763 | 71 | 3.9% | ESTABLISHED |
| Jan 2024 | 1,928 | 1,753 | 175 | 9.1% | ESTABLISHED |
| Apr 2024 | 1,690 | 1,539 | 151 | 8.9% | ESTABLISHED |
| Jul 2024 | 1,568 | 1,509 | 59 | 3.7% | ESTABLISHED |
| Oct 2024 | 1,717 | 1,565 | 152 | 8.8% | ESTABLISHED |
| Jan 2025 | 1,738 | 1,628 | 110 | 6.3% | ESTABLISHED |
| Apr 2025 | 1,849 | 1,591 | 258 | 14.0% | ESTABLISHED |
| Jul 2025 | 1,720 | 1,531 | 189 | 11.0% | ESTABLISHED |
| Oct 2025 | 1,755 | 1,491 | 264 | 15.0% | ESTABLISHED |

**What this answers for 2022 Q3 – 2025, directly:** the published "market cheapest" gap never goes
negative in this series — it bottoms at 2.0% (Apr 2023) and 3.7% (Jul 2024), never zero or below.
If that column is taken at face value, there was *always* a nominally cheaper deal somewhere in the
market, even at the worst of the crisis. **Section 3 is why that reading should not be trusted for
2021 H2 through mid-2023, and why the task's expectation of a negative/zero gap in that window is
right — just not visible in this particular column.**

## 3. Why 2021 H2 – mid-2023 needs the "average fixed tariff" column too, not just "cheapest"

Three spans of the "cheapest tariff (all suppliers)" column repeat **the exact same figure for
4-6 consecutive months**: Oct 2021 – Mar 2022 (£1,213.48, 6 months flat), Apr – Sep 2022 (£1,872.01,
6 months flat), and Oct 2022 – Mar 2023 (£2,374.77, 6 months flat). A live, competitive market does
not reprice its single cheapest deal to the exact penny for half a year running. **DERIVED, M
confidence**: this is much more consistent with a stale or carried-forward read — the same single
surviving product being counted every month because nothing else was on sale to undercut it — than
with genuine month-to-month repricing. It lines up exactly with the market history already on
record in `svt_rates_active_passive_2016_2025.md` (29 suppliers failed Jul 2021 – May 2022; fixed
deals withdrawn; Acquisition Tariff Ban in force 14 Apr – 1 Oct 2022).

The same Ofgem series' **"average fixed tariff"** column — average price of everything actually on
sale that month, not just the cheapest — tells the opposite, and un-stale, story, and this is
**ESTABLISHED** at H confidence (same source, ticking monthly throughout):

| Month | Default (£/yr) | Average fixed tariff on sale (£/yr) | Gap (£/yr) | Gap as % |
|---|---|---|---|---|
| Jun 2021 | 1,138 | 1,147 | **−9** | **−0.8%** |
| Jul 2021 | 1,138 | 1,214 | **−76** | **−6.7%** |
| Sep 2021 | 1,138 | 1,626 | **−488** | **−42.9%** |
| Oct 2021 | 1,277 | 2,096 | **−819** | **−64.2%** |
| Apr 2022 | 1,971 | 3,026 | **−1,055** | **−53.5%** |
| Jul 2022 | 1,971 | 3,851 | **−1,880** | **−95.4%** |
| Sep 2022 | 1,971 | 4,599 | **−2,628** | **−133.3%** |

**This is the negative-gap evidence the task asked for.** From June 2021 — three months before the
crisis is conventionally dated — the average new fixed-term quote already cost more than the
default tariff, and by September 2022 it cost **more than double**. No "average fixed tariff" data
point exists for Oct 2022 – May 2023 (the column is blank in the source, itself evidence the market
had largely stopped quoting new fixed terms during the EPG period), and it resumes only once the
cap/EPG regime stabilises. The series' own silence over that eight-month span is itself the
evidence: **ESTABLISHED that no "average fixed tariff" reading was published Oct 2022 – May 2023,
consistent with a market that had nothing to quote.**

**Which reading is the fairer proxy for the deal a switching household was leaving for?** Neither
column is exactly right on its own, and this is a "say what it counts before differencing" case
(CLAUDE.md). The "cheapest, all suppliers" column averages each supplier's own best tariff — which
during the freeze was often a single surviving, possibly-restricted product, not something a
household notifying a switch was actually about to receive. The "average fixed tariff" column is an
average of everything on sale, not the cheapest, so it overstates what the best available deal cost
by including worse offers too. **For 2021 H2 – mid-2023, the right read is: the market's *cheapest*
figure is NOT ESTABLISHED as a genuinely accessible deal (flagged stale, §3), and the market's
*average new-fix* figure is unambiguously and increasingly worse than the default — so a save offer
sized off "the market's best" in this window should be floored at zero, not computed as a positive
gap, exactly as the task anticipated.** From Jul 2023 onward, with quarterly cap cadence and the
"average fixed" and "cheapest" columns moving independently month to month (no more stale repeats),
both readings can be trusted and the headline table in §2 is the one to use.

## 4. One more flag: what "default" means Oct 2022 – Jun 2023

The series' own "Default tariff cap level" column reads **£2,500** for every month Oct 2022 – May
2023 — this is the **Energy Price Guarantee** level, not the headline Ofgem cap ceiling Ofgem was
publishing at the same time (£3,549 from Oct 2022, ~£4,279 from Jan 2023 per
`svt_rates_active_passive_2016_2025.md`, both **ESTABLISHED** there). Ofgem's own chart is plotting
the price a typical household actually paid (cap-then-EPG-reduced), which is the right quantity for
"what a household was actually being charged by its own supplier" and so the right denominator for
a save-offer gap — but it is a **different quantity** from "the cap level" quoted elsewhere in this
repo, and the two should never be differenced against each other. Flagged, not corrected, because
both figures are independently sourced and both correct for what they each measure.

## 5. Against `churn_price_elasticity.md`'s SIM Calibration "Savings" column

That document's own savings-by-year figures, compared to this pass's findings (annual/representative
points above):

| Year | churn doc's figure (£) | This pass's figure(s) (£) | Agreement |
|---|---|---|---|
| 2016 | 300 | 322 (annual avg) | close |
| 2017 | 200 | 289 (annual avg) | **understated by the doc, ~£90** |
| 2018 | 200 | 328 (annual avg) | **understated by the doc, ~£130** |
| 2019 | 175 | 196 / 374 / 315 (Jan/Apr/Oct) | **the doc is well below every reading this year** |
| 2020 | 125 | 369 / 219 (Apr/Oct) | **the doc is well below both readings** |
| 2021 | 0 ("H2 near zero") | 279 (Apr) collapsing to 60-64 (Sep/Oct) | directionally right for H2; the doc's flat "0" omits a H1 still near 25% |
| 2022 | **−200** ("strongly negative, no viable alternative") | "cheapest" column: **+99 to +125** (flagged stale, §3); "average fixed" column: **−1,055 to −2,628** | **the doc's sign is right against the average-fixed reading but the magnitude is an order of magnitude too small; against the (stale) cheapest-tariff reading the sign is wrong.** This is the clearest case in this file of two different published quantities needing to be told apart before a single "savings" constant is set for this year. |
| 2023 | 100 (range 50-150) | 100 (Jul), 71 (Oct) | **matches well** |
| 2024 | 150 (range 100-200) | 175/151/59/152 (quarterly) | matches except Jul (59, below range) |
| 2025 | 175 (range 100-250) | 110/258/189/264 (quarterly) | roughly matches; Oct slightly above the stated upper bound |

**Recommended action for whoever owns `MARKET_SAVINGS_BY_YEAR`:** 2017, 2018, 2019 and 2020 look
under-anchored against this pass's reading and are worth a second look; 2022 needs an explicit
choice between the two published quantities in §3 rather than a single blended number, because they
disagree in sign; 2023-2025 are already well anchored. This note does not change the constant
itself — only `ASSUMPTIONS.md` and this document are in scope here.

## 6. What this does not establish

- **The single literal cheapest tariff on the market**, as opposed to the average of each supplier's
  own cheapest (the "all suppliers" column). The true rock-bottom deal would read lower still.
  NOT ESTABLISHED from this source.
- **Whether a switching household's actual leaving-for deal tracked the market cheapest or something
  closer to the average** — no published series gives the distribution of what switchers actually
  signed up to, only market-wide tariff menus. NOT ESTABLISHED.
- **Electricity-only or gas-only gaps** — every figure above is dual-fuel, per Ofgem's own stated
  basis. NOT ESTABLISHED separately for single-fuel accounts.
- **Standard credit / prepayment gaps** — the companion chart ("Cheapest tariffs by payment method")
  exists and was read for its text commentary only (§0); its own full monthly series was not pulled
  this pass. NOT ESTABLISHED at the same granularity as direct debit above.
- **The basket-weighted "cheapest tariff (basket)" column's methodology** — present in the raw data
  pulled this pass but not read in its own methodology detail; not used in the headline table.

## Sources

- Ofgem, Retail Market Indicators data portal, chart "Retail price comparison by company and tariff
  type: Domestic (GB)" — `https://www.ofgem.gov.uk/news-and-insight/data/data-portal/retail-market-indicators`,
  underlying data fetched via its everviz embed `https://app.everviz.com/embed/g53GfRDaf`,
  2026-10-10. Publisher-stated sub-sources: Energylinx (to May 2017), Energyhelpline (Jun 2017 – May
  2022), Cornwall Insight (Jun 2022 onward).
- Same page, chart "Cheapest tariffs by payment method: Typical domestic dual fuel customer (GB)"
  (`xq5ftxo02`) — text commentary only, read 2026-10-10.
- Same page, TDCV methodology text attached to the above charts, read 2026-10-10.
- `docs/market_research/svt_rates_active_passive_2016_2025.md` — cross-checked cap levels, §4.
- `docs/market_research/churn_price_elasticity.md` — compared in §5.

## 7. How the growth campaign reads this (2026-11-22)

The net-new campaign asks for the company's first-term quote **before** the world decides the win
(`simulation.live_population.first_term_offer_fn`, through `company.interfaces.growth_desk.quote_first_term`).
The prospect's price position, which the funnel's quote-to-application stage responds to, is the
company's fixed strike against **the market's cheapest deal on the day**:

`market = default charged to the household (net of the EPG) × (1 − this quarter's gap) ÷ (1 + 5% VAT)`

Design choices, and why:

- **The parity point is the cheapest fix, not the cap.** A household shopping for a fix compares
  fixes. Measured against the cap, a typical 2016–20 first term saturates the funnel.
- **The default is the one charged, net of the EPG** (§4). The gate the company asks also reads the
  default net of the EPG, so both sides read the same default.
- **The dual-fuel gap share is applied to each fuel's unit rate.** That is a stated belief: §6 says
  single-fuel gaps are NOT ESTABLISHED.
- **2021 Q4 – 2023 Q2 read a gap of 0.0** (§3: floored, not negative). The household's alternative
  to a dearer fix is the default it already has.
- **The strike is the desk's base strike** (`strike_fixed_unit_rate`), not the full renewal chain.
  So the quote can differ from the rate the account is later contracted at, while
  `ACQUISITION_HELD_AT_CAP_TARIFF_TYPES` still holds first terms at the cap.
- **GAP, so no position is read for default-tariff prospects.** Their rate is the cap and there is
  no strike to price. The funnel stays at the run-level position for them, as before.

Measured at real inputs (seed `run_base_seed()`, 3,301 offers asked, all electricity; 951 of them
default-tariff and so unpriced):

| year | priced | median position vs cheapest | declined (strike above default) |
|---|---|---|---|
| 2016 | 296 | +10.8% | 0 |
| 2017 | 311 | +3.2% | 0 |
| 2018 | 310 | +26.5% | 0 |
| 2019 | 315 | +0.8% | 5 |
| 2020 | 317 | +0.6% | 0 |
| 2021 | 154 | +13.3% | 150 |
| 2022 | 17 | −17.7% | 70 |
| 2023 | 146 | −27.5% | 2 |
| 2024 | 254 | −20.3% | 0 |
| 2025 | 39 | −12.5% | 8 |

The campaign went from 210 wins on 3,250 quotes to 230 wins on 3,066 quotes, with 235 quotes withheld.

**Open, and not settled by this page.** The 2023–24 strikes sit 20–28% below Ofgem's cheapest deal.
Either the company's spot-EWMA forward underprices a market that was pricing off forward curves, or
the per-fuel application of the gap is wrong for electricity in those years. I cannot yet say which.

**Attributed 2026-11-23: neither of the two explanations above.** Both were tested one variable at a
time, at real inputs, on electricity quotes dated the 15th of each quarter. The position is the
strike against the cheapest deal, both ex-VAT.

| date | position | with gap 0 (vs default) | with the outturn as the forward | market's implied wholesale | company forward | 12-month SSP outturn |
|---|---|---|---|---|---|---|
| 2022-10 | +19.6% | +19.6% | −30.2% | 210.2 | 272.8 | 113.7 |
| 2023-01 | +14.0% | +14.0% | −34.8% | 201.7 | 245.5 | 93.1 |
| 2023-04 | −25.1% | −25.1% | −37.2% | 192.2 | 113.9 | 76.0 |
| 2023-07 | −17.8% | −21.8% | −27.0% | 143.2 | 96.3 | 72.0 |
| 2023-10 | −4.7% | −8.4% | −18.2% | 114.7 | 103.4 | 70.7 |
| 2024-01 | −10.4% | −18.5% | −15.1% | 109.8 | 85.0 | 73.6 |
| 2024-04 | −15.6% | −23.1% | +0.8% | 80.3 | 48.4 | 82.0 |
| 2024-07 | +4.3% | +0.4% | +5.5% | 73.1 | 81.6 | 84.1 |

The market's implied wholesale is the forward at which the company's strike would equal the cheapest
deal. The outturn is used as an instrument only and is never a company input.

- **The per-fuel gap is refuted for 2023 H1.** The gap there is 0.0 (§3, floored), so how the gap is
  split between fuels cannot move the reference at all. Yet the position is −25%. From 2023 Q3 the
  split can move the position by 4–8 points, but in the direction that makes it more negative, not
  less.
- **"The forward underprices" is refuted for 2023.** The company's spot-EWMA forward sat *above* the
  12-month outturn at every 2023 date. Pricing on the outturn makes the strikes cheaper still. The one
  date where the forward does explain the position is **2024-04** (48 against an outturn of 82, which
  closes the position to +0.8%). That is the EWMA following the early-2024 spot trough.
- **What the evidence leaves.** From 2022 Q4 to 2023 Q4, the market's cheapest deal implies a wholesale
  cost 1.6 to 2.5 times the outturn, well above any spot-based forward. Real fixes were not priced off
  the cost of energy at the time they were sold.
- **The Market Stabilisation Charge explains only a minority of it** (`the_market_stabilisation_charge_2022_2024.md`,
  Ofgem's 102-week published series). The MSC was a one-off charge in £/MWh on the switching customer's
  annual consumption, paid by the gaining supplier to the losing one. Here is the electricity rate in
  force at each quote date, against the gap between the strike and the cheapest deal:

  | date | MSC (£/MWh) | cheapest deal − strike (£/MWh) | share of the gap |
  |---|---|---|---|
  | 2023-04 | about 17 | 81 | about 20% |
  | 2023-07 | about 5 | 49 | about 10% |
  | 2023-10 | about 4 | 12 | about 1/3 |
  | 2024-01 | 10 | 26 | about 40% |
  | 2024-04 | 0 (expired 31 March) | 33 | 0; the forward explains it |

  *Seat, corrected the same day:* a first draft of this section treated the MSC as the leading
  explanation, and read the MSC's end matching the 2024 Q3 turn as support for it. That was written
  before the charge's size was known. It is wrong at every date. The size is known now: the MSC is a
  real cost that the strike leaves out, but it is not the main cause.
- **The remainder is not attributed.** Ofgem names more than one constraint (Feb 2023 MSC decision,
  §3.3): suppliers did not price fixes below the EPG's £2,500. Two other published rules also bear on
  it: the ban on acquisition-only tariffs (SLC 22B), which put any cheap acquisition fix in front of
  the whole book, and the cap's lagged wholesale index, which carried crisis-era hedges. Neither has
  been sized here. A second candidate sits on the company's own side: the strike reads a spot-EWMA
  forward and ignores the cost of the company's own hedge book. A supplier still holding hedges bought
  in 2022 would not strike off 2023 spot. Which of these carries the remainder, **I cannot yet say**.

**What this means for removing the hold.** Deleting `ACQUISITION_HELD_AT_CAP_TARIFF_TYPES` now would
let the 2023 Q2 – 2024 Q2 strikes win at 10–25% under the market. Some of that undercut is a cost real
law imposed and the simulation leaves out (the MSC). The rest is not yet attributed. Winning on a
missing rule would be value transferred, not created. So two things come before the deletion. First,
the world charges the MSC to the gainer for each win from 14 April 2022 to 31 March 2024, from
Ofgem's published weekly rates, and the company sees the charge in its own settlement. Second, the
hedge-cost candidate is tested: strike on the cost of the company's own book against strike on
spot-EWMA, at the same dates.

**The hedge-cost candidate, tested 2026-11-23.** The predictions were filed before any number was
computed. The method uses the same dates, the same 2,900 kWh domestic fixed electricity quote and the
same `strike_fixed_unit_rate`, and changes **only the forward** handed to it:

- **A** is the company's spot-EWMA. It reproduces the table above to the decimal, which is the control.
- **B** is Ofgem's published 12-month forward that could be dealt on the quote date
  (`sim.forward_curve.published_forward_quote`).
- **C6** and **C12** are the mean of that published forward over the trailing 6 or 12 months, counting
  only weeks a trader could have seen by the quote date. This stands for the cost of a book hedged
  evenly on a ladder. The run's own hedge records are not used.

| date | cheapest deal | A spot-EWMA | B dealable forward | C6 ladder | C12 ladder |
|---|---|---|---|---|---|
| 2022-10 | 323.8 | 272.8 / +19.6% | 414.9 / +64.0% | 301.8 / +28.6% | 231.1 / +6.5% |
| 2023-01 | 323.8 | 245.5 / +14.0% | 194.9 / −2.2% | 348.5 / +47.0% | 273.8 / +23.1% |
| 2023-04 | 323.8 | 113.9 / −25.1% | 148.3 / −14.0% | 233.9 / +13.4% | 267.8 / +24.2% |
| 2023-07 | 273.0 | 96.3 / −17.8% | 124.1 / −7.3% | 141.7 / −0.6% | 245.1 / +38.7% |
| 2023-10 | 250.3 | 103.4 / −4.7% | 102.4 / −5.1% | 122.4 / +3.2% | 178.2 / +26.3% |
| 2024-01 | 247.8 | 85.0 / −10.4% | 77.3 / −13.6% | 107.7 / −0.9% | 124.4 / +6.1% |
| 2024-04 | 212.6 | 48.4 / −15.6% | 74.5 / −2.9% | 85.6 / +2.5% | 103.6 / +11.4% |
| 2024-07 | 205.1 | 81.6 / +4.3% | 81.6 / +4.3% | 76.5 / +1.7% | 92.4 / +9.7% |

Each cell is the forward (£/MWh), then the strike's position against the cheapest deal. Both sides
are ex-VAT. The cheapest deal is a retail unit rate; the forwards are wholesale.

**Seat, corrected 2026-11-23 (later): both tables above priced the strike on the wrong network
cost, and the ±3.2% result is an artefact of it.** Both probes passed the segment as `"domestic"`.
`simulation.policy_costs.get_electricity_network_cost_per_mwh` does not know that label, so it
falls through to the SME volume table: 75 £/MWh in 2023-07, where the residential cap allowance the
campaign uses (`"resi"`) is 42.4, and 69 against 29.0 in 2024-07. The strike was 30–40 £/MWh too
dear at every date from 2023. Re-run with `"resi"`, nothing else changed (probe:
`/var/tmp/se-ftq-probe/hedgecost_seg.py`):

| date | cheapest deal | A spot-EWMA | B dealable forward | C6 ladder | C12 ladder |
|---|---|---|---|---|---|
| 2022-10 | 323.8 | +11.3% | +55.7% | +20.3% | −1.8% |
| 2023-01 | 323.8 | +5.7% | −10.5% | +38.7% | +14.8% |
| 2023-04 | 323.8 | −35.8% | −24.7% | +2.7% | +13.5% |
| 2023-07 | 273.0 | −29.8% | −19.2% | −12.5% | +26.8% |
| 2023-10 | 250.3 | −17.7% | −18.1% | −9.8% | +13.3% |
| 2024-01 | 247.8 | −23.5% | −26.7% | −14.0% | −7.0% |
| 2024-04 | 212.6 | −33.4% | −20.7% | −15.3% | −6.5% |
| 2024-07 | 205.1 | −15.2% | −15.2% | −17.8% | −9.7% |

What survives: a lagged ladder sits nearer the market than the spot-led forward at every date from
2023-04 to 2024-04, so the direction of P3 holds. What does not: **no instrument closes 2023 H2 –
2024.** C6 sits 10–18% under the cheapest deal there, which is 25–40 £/MWh. The "within ±3.2%"
sentence below and the "attributed" reading of 2023 H2 – 2024 are withdrawn. The undercut is
narrowed, not explained. The attribution table further up carries the same defect. Its directions
stand (a per-fuel gap of 0.0 still cannot move 2023 H1, and the outturn is still below the
forward), but every position in it is about 8–12 points too high.

All four predictions held:

- **P1.** B does not close 2023-04. It reaches −14.0%.
- **P2.** C12 overshoots 2023 H1. It reaches +24.2% at 2023-04, carrying the August 2022 peak.
- **P3.** A ladder closes 2023-07 to 2024-01. C6 sits at −0.6%, +3.2% and −0.9% there, where A sat
  between −5% and −18%.
- **P4.** At 2024-04 both ladders sit above A.

What the table shows:

- **From 2023-07 to 2024-07, the cheapest fix on the market was priced about where a six-month ladder
  of the dealable forward sits.** All five dates fall within ±3.2%. The gap that remains is not the
  per-fuel split and not the MSC: the MSC is 0 to 10 £/MWh across these dates and sits on top of
  this.
- **This does not separate the supplier's own hedge cost from the cap's lagged index.** Both are
  trailing averages of the same forward, so this probe cannot tell them apart. What it does establish
  is narrower: real fixes in that period were priced off a **lagged forward cost, not the spot-led
  forward.** Our strike ignores that lag, and that is the larger part of the 2023 H2 – 2024 undercut.
- **2022 Q4 – 2023 Q2 is not explained by any ladder.** The published gap was 0 in that period. The
  cheapest deal *was* the default, under the EPG. In 2022-10 and 2023-01 every instrument except B
  prices above it, so no fix could win; that agrees with the market of the time. At 2023-04 the
  instruments disagree: A is at −25%, B at −14% and C6 at +13%. The MSC (about 17 £/MWh, about 20%
  of A's gap) and the EPG floor (Ofgem, February 2023) remain the candidates. **I cannot yet say**
  which.

What it means for the company. A supplier striking a fixed first term prices the energy at what it
will cost them, and a hedged book costs a lagged average, not today's spot-led forward. The
published forward is something a real supplier sees. Building this is a change to the company's
strike, not the world's. It means pricing the first term off the cost of its own hedge ladder, as
the company buys it, with the ladder's length the company's own choice. That build comes before the
hold can come off. Until it lands, deleting `ACQUISITION_HELD_AT_CAP_TARIFF_TYPES` would let the
2023 H2 – 2024 strikes win on a cost the company has not modelled. That is a transfer, not value
created. Probe and predictions: `/var/tmp/se-hedgecost/` (outside the repo, reproducible from the
two committed inputs).


## 8. The company's first-term forward is its hedge ladder (K8, 2026-11-23)

**What the rules require.** Nothing in the licence sets how a supplier prices a fix. SLC 22B bans
acquisition-only tariffs, so a first-term fix is also priced to the existing book (§7). The cap's own
wholesale allowance is a trailing average of the published 12-month forward: a 6-month observation
window until June 2022 (index 6-2-12) and 3 months after (3-1.5-12)
(`the_published_forward_gets_its_delivery_axis_from_the_cap_indexation_rule_2026-10-10.md`). That is
the regulator's own model of what a hedged supplier's energy costs.

**What the design does.** `company.pricing.renewal_desk.quote_first_term` strikes a fixed first term
on `laddered_forward`. That is the mean of the published weekly 12-month forward over the trailing
`FIRST_TERM_LADDER_MONTHS` (6), counting only weeks a trader could read by the quote day. The world
hands over exactly those rows (`sim.forward_curve.published_forward_knowable_by`). The ladder is
refused, and the spot-led forward stands in, in two cases. First, where the series does not reach
back a whole window: it starts 2021-02-08, so every quote before about August 2021 is unchanged.
Second, where its newest row is a week or more stale. The no-offer rule reads the laddered strike.
A default-tariff prospect has no strike, so its gate still reads the spot-led forward.

**Choices, and why.** Six months is the cap's own window for most of the period with a published
series. Three months (the cap from June 2022) is the other published choice. The company may change
it, and nothing here grades which is better. The ladder is a modelled book bought evenly, not the
run's own hedge records. The campaign is resolved before the run hedges anything, so there is no
book yet to read.

**GAP.** Before 2021-02-08 no forward is published, so pre-2021 strikes stay spot-led. A real
supplier then priced off broker forwards we do not hold. The renewal chain (`quote_renewal`) still
strikes on the spot-led forward, so a first term and its renewal are priced on different bases
until that chain is moved too.

**Measured at real inputs** (seed `run_base_seed()`, one variable: the forward a fixed first term is
struck on; predictions filed first in `/var/tmp/se-ftq-probe/PREDICTION.md`):

| year | priced, before → after | median position vs cheapest | declined |
|---|---|---|---|
| 2016–20 | identical | identical | identical |
| 2021 | 154 → 244 | +13.3% → +10.1% | 150 → 60 |
| 2022 | 17 → 20 | −17.7% → −8.0% | 70 → 67 |
| 2023 | 146 → 121 | −27.5% → −12.5% | 2 → 27 |
| 2024 | 254 → 254 | −20.3% → −15.5% | 0 → 0 |
| 2025 | 39 → 51 | −12.5% → −13.9% | 8 → 0 |

The campaign goes from 230 wins with 235 quotes withheld to 225 wins with 159 withheld. The wins
per year in 2016–20 move although no position does: the settlement ceiling picks which wins settle
across the whole campaign. P1, P4 and P5 held. **P2 was refuted.** I predicted 2023 within
[−10%, +15%] and 2024 within [−8%, +8%] from the ±3.2% probe, and that probe was wrong (correction
in §7). P3 held for 2023 (37 → 27 wins) and failed for 2024 (43 → 47).

**What it means for the hold.** From 2023 Q2 to 2025 Q2, quarterly median positions on the ladder
still sit 11–19% under the market's cheapest fix. `ACQUISITION_HELD_AT_CAP_TARIFF_TYPES` must not
come off on this. What carries the remaining 25–40 £/MWh, **I cannot yet say**. The candidates are
the MSC (0–17 £/MWh, in its own lane), and cost lines the cap's unit rate carries that
`strike_fixed_unit_rate` may not (operating cost, the smart-metering and bad-debt allowances, the
EBIT and headroom allowances). There is also the stated belief that the dual-fuel gap share applies
to the electricity unit rate. The next step is a line-by-line comparison of the strike against the
cap's published unit-rate build at one date.

## 9. The strike, line by line, against the cap's unit-rate build (2026-11-23)

**Method.** Each cap component's unit-rate allowance is read from Ofgem's cap level model
(`Default-tariff-cap-level-v1.31.xlsx`, direct debit, single-rate electricity) using the same
construction as `tools/ofgem_cap_unit_rate_composition.py`: (benchmark £/yr − nil £/yr) ÷ 3,100 kWh,
taking the median over 14 regions. The strike is `strike_fixed_unit_rate` on §8's ladder, with the
residential network cost, at the dates §7 used. Its lines add to the strike exactly. Predictions were
filed after reading the cap's components and before computing any strike line
(`/var/tmp/se-capbuild/PREDICTION.md`). All figures are £/MWh ex-VAT.

| line | 2023-07 strike | cap (Jul–Sep 23) | gap | 2024-04 strike | cap (Apr–Jun 24) | gap |
|---|---|---|---|---|---|---|
| wholesale: ladder + capital charge vs DF + CM | 147.0 | 165.3 | −18.3 | 88.7 | 121.9 | −33.1 |
| policy vs PC | 47.5 | 41.8 | +5.8 | 58.3 | 48.6 | +9.7 |
| network vs NC | 42.4 | 42.4 | 0.0 | 31.1 | 31.1 | 0.0 |
| margin £2 vs EBIT + headroom (E + H) | 2.0 | 8.9 | −6.9 | 2.0 | 8.6 | −6.6 |
| operating cost (OC) | — | 15.3 | −15.3 | — | 15.9 | −15.9 |
| smart (SMNCC) + payment adj. (PAP) | — | 3.1 | −3.1 | — | 2.7 | −2.7 |
| adjustment allowance (AA) | — | 11.2 | −11.2 | — | 5.1 | −5.1 |
| **total** | **238.9** | **285.4** | **−46.6** | **180.0** | **233.5** | **−53.5** |
| market's cheapest fix (§7) | | 273.0 | | | 212.6 | |

The component gaps sum to −49.0 and −54.6. The cap totals differ from this by 2.4 and 1.1 because
a median of regional totals is not the sum of the medians.

**What carries the undercut.** The strike sits 34.2 and 32.5 under the cheapest fix. The cheapest fix
sits 12.4 and 20.9 under the cap.

- **The strike has no operating-cost line.** Ofgem allows 15.3–15.9 £/MWh of operating cost on the
  unit rate, plus 2.7–3.1 for smart and payment method. A fix seller must recover those somewhere.
  `price_fixed_tariff` recovers them nowhere on the unit rate. Alone they come to 18–19 £/MWh, more
  than half the undercut.
- **The wholesale line sits 11% (2023-07) and 27% (2024-04) under the cap's delivered commodity.**
  DF is priced on the delivered MWh, carrying shape, imbalance and transaction cost, and on Ofgem's
  own index and not a six-month baseload ladder. The strike's line is a baseload forward plus the
  capital charge. Neither the strike nor the world's settlement carries line losses: only
  `company/carbon/` reads a T&D loss factor. Whether the world should settle supplier volume grossed
  up for losses is a fidelity question. **GAP, not examined here.**
- **The margin is £2 against Ofgem's 6.6–8.9 of EBIT and headroom.** A market fix plausibly shaves
  headroom and the adjustment allowance (AA recovers past costs a new fix need not carry), and the
  cap-to-cheapest gap of 12–21 is the size of AA + H + part of E.
- **The policy line runs the other way**, 5.8–9.7 above the cap's PC. The company prices policy cost
  over the term ahead, and the cap prices it on the period's own allowance. That pushes the strike
  up, so it is not part of the undercut.

**Predictions.** P1 held: the allowances the strike has no line for sum to 38.5 and 32.3, inside
28–40. **P2 was refuted on policy**: the network line agrees exactly, but policy is +14% and +20%,
outside ±10%. P3 held: wholesale sits 11.1% and 27.2% under DF + CM, against a >10% prediction (the
2023-07 margin is thin). P4 held: the cap-to-cheapest gap (12.4 and 20.9) is smaller than P1's sum.

**What it means.** The remaining undercut is not a market-position puzzle. It is mostly cost lines
the company's own strike leaves out, operating cost first. A first term struck below the company's
cost to serve wins on value it transfers rather than creates (M2). The next build is the company's,
on the strike: an operating-cost line read from the company's own cost to serve, which is known to
the company, rather than Ofgem's allowance, which would be the regulator's number standing in for the
company's. Then re-measure the position at these dates before the hold comes off. The wholesale
shortfall (shape and losses) is second, and needs the world question above settled first.
