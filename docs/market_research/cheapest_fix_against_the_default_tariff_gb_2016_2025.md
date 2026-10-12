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
