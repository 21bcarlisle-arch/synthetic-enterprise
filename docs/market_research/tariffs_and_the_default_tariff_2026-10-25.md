# GB domestic tariffs: fixed deals, the default tariff, time-of-use, and the cap

**Knowledge:** tariffs-and-the-default-tariff

Written 2026-10-25 for the director's map steer of 24 Oct (item 4, fourth owed page), from the
advisor's cited evidence pack `docs/staging/advisor/done/DIRECTOR_EVIDENCE_TARIFFS_AND_THE_DEFAULT_TARIFF_2026-10-25.md`.
Its [UNVERIFIED] items were checked while drafting, as the 25 Oct verify steer asks; the outcomes
are in the table below and are marked beside each item in the pack text.

Read beside this note: `tools/published_tariff_mix.py` (the one home of the default-share series, with
its prepayment basis) and its write-up `gb_domestic_default_tariff_share_2016_2025.md`;
`svt_drift_by_payment_behaviour.md`; the price-cap page (`site/knowledge/price-cap/`) for the cap's
own method.

## 0. What this project's world and company do today (read from code, not run)

- **The default tariff is a world product priced at the cap.** `simulation/svt_product.py` settles an
  SVT account in cap periods, with no term boundary and no renewal decision. Its rate is the published
  cap from `simulation/svt_rates.py`, and the household's charge in Oct 2022-Jun 2023 is the EPG rate,
  not the cap. The published fixed/default split is a check on the output, never an input
  (`tools/published_tariff_mix.py`, refused as a `simulation/` import).
- **A new reading for a declared gap.** `published_tariff_mix.DEFAULT_TARIFF_SHARE[2021]` is `None`.
  The pack's August 2021 reading (about 15m on the cap and 13m fixed, so about 54% default; Commons
  Library CBP-9714) is the first published figure for that year. Its base may include prepayment, so
  it is recorded here and not yet written into the module. Writing it is a one-row change with its
  basis named.
- **The company's exit-fee rule disagrees with the licence, and nothing calls it.**
  `company/billing/exit_fee.py` waives a fee within **42** days of the end; the rule the pack cites
  (Which?, SLC 22C) is no fee in the final **49** days. It also prices the fee at 1.5p/kWh electricity
  and 1.0p/kWh gas, "published tariff schedules" with no source, where every published fee is flat per
  fuel. No module outside its test imports it.
- **No restricted meter.** The world has no Economy 7 or other multi-register home (14-17% of
  electricity accounts in the record). The asset steer of 25 Oct makes a two-rate meter an attribute
  of a home with storage or off-peak load, with the restricted-meter share as the population check.
- **Time-of-use is a flat-rate split, offered by the company.** `company/pricing/tou_desk.py`, behind
  the door `company/interfaces/tou_offer.py`, offers a smart-metered fixed-term customer a peak/off-peak
  pair that splits its contracted flat rate revenue-neutrally (1.5x/0.79x, `simulation/tou_periods.py`).
  A default-tariff account is single-rate. No household is on an Agile- or Go-shaped product, and none
  has a restricted meter.
- **The default-tariff letter is graded.** C30's three-seed grade of 25 Oct (2e14c5ce0) found that the
  once-per-stint letter to default-tariff households, with a re-fix, costs the company on all three
  books, and the households who stay gain £0.9k-£1.4k a book. That is the first graded supplier action
  on this page's subject.

## Verification of the pack's [UNVERIFIED] items (2026-10-25, seat; web search, accessed 2026-10-25)

| # | Item | Outcome | Source |
|---|---|---|---|
| V1 | Share of fixes by length (12/18/24 months) | **still unpublished**: no Ofgem or CMA series found | — |
| V2 | Crisis-era exit fees above £30 per fuel | **corrected** band: typical £75 per fuel on a 12-month fix and £200 per fuel seen on a 2-year fix (Which?); MSE (May 2022) typical £60 dual fuel, some homes facing up to £600; Warm This Winter average £42 (early 2021) to a peak of £187 | which.co.uk "How to get out of your fixed energy tariff"; moneysavingexpert.com news 2022/05 "energy suppliers are charging higher exit penalties"; endfuelpoverty.org.uk tariff watch |
| V3 | CMA detriment averaged over 2012-2015, above £2bn in 2015 | **confirmed**, with "almost £2bn" in 2015 (direct approach; 9% of a dual-fuel bill). Secondary source: Littlechild's critique, quoting the final report | EPRG WP1703, jbs.cam.ac.uk |
| V4 | Prepayment joined the default cap in 2021; levelisation from 2024 | **confirmed**: the PPM cap was folded into the default cap when it expired at the end of 2020 (£1,156 PPM against £1,138 DD from 1 Apr 2021). Levelisation from 1 Apr 2024: PPM about £49 a year less, DD about £10 more | ofgem.gov.uk default tariff cap level letter, Feb 2021; Default Tariff Cap Letter, 1 April 2024 (Feb 2024) |
| V5 | Agile about 2018, Go about 2019 | **corrected**: Octopus Go launched June 2018 (5p/kWh, four-hour night window). Agile February 2018 rests on a forum post, so it stays weak | fleetnews.co.uk 11 Jun 2018; zapmap.com |
| V6 | RMR's three permitted cash discounts | **partly confirmed**: dual fuel and online account management are named in Ofgem's 2014 Ecotricity letter on SLC 22B; payment method is **still open** | ofgem.gov.uk ecotricity_cover_letter_and_directions_02_07_2014 |
| V7 | Date the BAT ended | **corrected**: it has not ended. It was extended to 31 Mar 2025 (Feb 2024), retained against the minded-to removal on 30 Jul 2024, extended to 31 Mar 2026 (Nov 2024), and Ofgem's outcome page extends it to 31 Mar 2027 | ofgem.gov.uk Decision_on_removing_the_BAT_July_2024; Decision_Future_of_the_BAT_after_March_2025 (Nov 2024); "Renewing the BAT after March 2026" |
| V8 | Date the RMR simpler rules were formally removed | **still open** | — |

**Count: 2 confirmed, 1 partly confirmed, 3 corrected, 2 still open.** No world claim used a
corrected item: the world draws no exit fee, no BAT and no time-of-use product.

## The pack: fixed deals, the default tariff, time-of-use and how households sit across them, 2016-2025

*Evidence pack for the simulation's knowledge layer. Every figure comes from a source I fetched for this pack, unless it is marked **[UNVERIFIED]**. Ofgem retail market indicator (RMI) time series are mostly published as charts, so where only chart data exists this pack uses figures quoted in the text.*

---

### 1. How households split between default and fixed tariffs, 2016-2025

**Before the cap (2016-2018)**
- The CMA's final report (June 2016) found that "around 70% of the customers of the Six Large Energy Firms are currently on a standard variable tariff" (Summary, paras 24 and 102). It also found that "56% of respondents said they had never switched supplier, did not know it was possible or did not know if they had done so" (para 100(c)). https://assets.publishing.service.gov.uk/media/576c23e4ed915d622c000087/Energy-final-report-summary.pdf
- Ofgem, September 2017: "around 57% of people with the 10 largest suppliers – around 13 million customers – are on non price-protected SVTs". This was 2 percentage points lower than April 2017. The share varied a lot by supplier: SSE 71%, British Gas 67%, E.ON 61%, First Utility 23%, OVO 28%, Co-operative Energy 35%. The base is non-prepayment accounts. https://ofgem.gov.uk/publications/standard-variable-tariffs-latest-trends-september-2017

**Just before the crisis (August 2021)**
- About 15 million domestic customers were covered by the price cap and about 13 million were on fixed tariffs. That is roughly 46% fixed and 54% default. The 46/54 split is my arithmetic, and the base is ambiguous because it may or may not include prepayment. https://researchbriefings.files.parliament.uk/documents/CBP-9714/CBP-9714.pdf

**During the crisis (2022-2023)**
- Fixed deals priced below the cap disappeared. By 2022 "most customers cannot currently get a deal below the tariff cap" (Commons Library). https://researchbriefings.files.parliament.uk/documents/CBP-8081/CBP-8081.pdf
- July 2023: about 29 million households were on the cap and about 3 million were still on fixed tariffs, which is roughly 90% default. https://researchbriefings.files.parliament.uk/documents/CBP-9714/CBP-9714.pdf

**Recovery (2023-2025)**
- Fixed-term contracts came back in the second half of 2023. Their share of electricity accounts rose "from 11% to 27%" by about January 2025 (Ofgem State of the Market 2025). https://www.ofgem.gov.uk/sites/default/files/2025-04/OFG2296_State%20of%20the%20Market%20Report.pdf
- "By July 2025, around one-third of customers were on FTCs, twice the proportion recorded in July of the previous year" (Ofgem State of the Market, January 2026). https://www.ofgem.gov.uk/sites/default/files/2026-01/State-of-the-Market-Energy-Retail-Highlights-January-2026.pdf
- Ofgem's ban on acquisition-only tariffs (BAT, SLC 22B) was introduced in April 2022 and was due to end in March 2025. Ofgem consulted on lifting it early, possibly by October 2024. https://www.moneysavingexpert.com/news/2024/05/energy-suppliers-restart-offering-exclusive-new-customers-tariff/ ; https://www.ofgem.gov.uk/decision/future-ban-acquisition-only-tariffs-post-march-2024-decision. The Market Stabilisation Charge was set to "expire at the end of March 2024" (same Ofgem decision). The date the BAT actually ended is **not verified**. *Seat: corrected. It has not ended; see V7.*
- From 14 April 2022 Ofgem granted all suppliers a market-wide derogation from SLC 22B so they could keep offering fixed **retention** tariffs to existing customers. https://www.ofgem.gov.uk/sites/default/files/2022-03/SLC%20Derogations%20-%20market-wide%20derogations%20letter.pdf

### 2. How fixed tariffs work

- **Contract lengths:** 12, 18 and 24-month fixes are common in the market. I found no Ofgem source giving the share of fixes at each length **[UNVERIFIED]**.
- **Exit fees:** Which? says "Exit fees vary from £5 to £30 per fuel", so up to £60 for dual fuel. https://www.which.co.uk/news/article/how-to-avoid-paying-an-exit-fee-when-you-switch-energy-tariffs-akHUy3u8H1Se. I found **no regulatory cap** on the size of an exit fee. My recollection that some fixes during and after the crisis charged much higher fees per fuel is **[UNVERIFIED]**. *Seat 2026-10-25: confirmed and the band corrected, see V2.*
- **End-of-fix notice:** SLC 22C.4(a) requires the renewal statement to be sent "no earlier than 49 days and no later than 42 days before" the fixed term ends. https://www.ofgem.gov.uk/system/files/docs/2017/10/notice_of_modifications_and_reasons_-_default_tariffs_for_domestic_customers_at_the_end_of_fixed-term_tariffs_electricity.pdf
- **No exit fee near the end:** Which? says "Your supplier cannot charge you an exit fee in the last 49 days of your tariff." (Which? also gives a 42-49 day phrasing.) https://www.which.co.uk/news/article/how-to-avoid-paying-an-exit-fee-when-you-switch-energy-tariffs-akHUy3u8H1Se
- **Rollover (SLC 22C.7, in force from 6 December 2017):** If the customer does nothing, they move to a default tariff. The supplier may instead use a "Relevant Fixed Term Default Tariff", which must:
  - be similar in nature to the expiring contract;
  - carry no termination fee;
  - cost no more than the supplier's "Relevant Cheapest Evergreen Tariff".

  Source: the Ofgem notice above. In practice the rollover lands on the SVT, which is "often pricier" (Which?).

### 3. The gap between the cheapest fix and the default ("loyalty penalty")

| Date | Gap | Source |
|---|---|---|
| Q2 2015 | Possible saving for dual fuel SVT customers "around £330" a year. Average gain over the whole period £164 (CMA para 128) | CMA summary (link above) |
| Jun 2016 | CMA: customers could save "over £300" by switching | https://commonslibrary.parliament.uk/research-briefings/cbp-7543/ |
| Sep-Nov 2017 | Average SVT "around £300 or more" above the cheapest tariff on the market (£806) | Ofgem 2017 (link above) |
| Jul 2022 | Cheapest tariff £1,872 against an average legacy SVT of £1,970. Most fixes were priced above the cap | CBP-8081 |
| Feb 2025 | "around £140" | Ofgem SoM 2025 |
| Oct 2025 | "approximately £265" | Ofgem SoM Jan 2026 |

**CMA detriment estimates.** The Commons Library and the CMA archive summary quote domestic detriment as "about £1.4 billion a year" (https://researchbriefings.files.parliament.uk/documents/CBP-8081/CBP-8081.pdf ; https://regulation.org.uk/archive-energy-2016_cma_report.html). A Commons Library page gives £1.7bn a year (https://commonslibrary.parliament.uk/research-briefings/cbp-7543/), which I take to include microbusinesses. My recollection that the period was 2012-2015 and that detriment rose above £2bn in 2015 is **[UNVERIFIED]**. *Seat: confirmed as "almost £2bn", see V3.* The CMA's prepayment cap was expected to cut bills by "£300 million a year" (CBP-7543).

**Restricted meters.** In Q2 2015 restricted-meter customers who would have been better off on the cheapest single-rate tariff lost about £42m in total. That is about £158 per customer, or 17% of their bill. https://assets.publishing.service.gov.uk/media/577521a9e5274a0da3000123/fr-appendix-9-5-restricted-meters.pdf

### 4. The default tariff cap and the Energy Price Guarantee

**Legal basis.** The Domestic Gas and Electricity (Tariff Cap) Act 2018 received Royal Assent on 19 July 2018. The cap started on 1 January 2019 at £1,137 a year for typical dual fuel paid by direct debit (£1,221 for standard credit). https://researchbriefings.files.parliament.uk/documents/CBP-8081/CBP-8081.pdf ; https://www.ofgem.gov.uk/system/files/docs/2018/11/decision_-_default_tariff_cap_-_overview_document_0.pdf

**Structure (from the Ofgem 2018 decision overview):**
- **Per fuel:** "We do not set a 'dual fuel' cap. We set caps for each fuel separately."
- **Payment method:** separate caps for direct debit and standard credit. Prepayment was originally covered by the CMA's prepayment cap. My recollection that prepayment moved into the default cap from 2021, and that payment-method levelisation started in 2024, is **[UNVERIFIED]**. *Seat: confirmed, see V4.* Ofgem's call for evidence on levelisation is at https://www.ofgem.gov.uk/sites/default/files/2023-04/Levelisation%20of%20payment%20method%20cost%20differentials_Call%20for%20evidence_2604231682350750835.pdf
- **Region:** the cap varies across the 14 electricity distribution regions. The network allowance ran from £234 to £298, averaging £258 for typical dual fuel.
- **Multi-register:** "We set a different cap for customers with multi-register tariffs", based on 4,200 kWh a year.
- **Typical consumption values:** 3,100 kWh a year electricity and 12,000 kWh gas. Caps at other volumes fall on a straight line between the nil-consumption cap and the typical-consumption cap.
- **Example levels, Q1 2019, direct debit:**
  - Electricity: 23p/day standing charge and 16.5p/kWh
  - Gas: 26p/day and 3.7p/kWh
  - Electricity multi-register: 23p/day and 15.4p/kWh

**Update frequency.** The cap was reset every six months on 1 April and 1 October from April 2019. Ofgem's August 2022 reforms moved it to a "three-month (quarterly) price cap period". https://researchbriefings.files.parliament.uk/documents/CBP-9714/CBP-9714.pdf

**Cap levels (typical dual fuel, current consumption values, from CBP-9714):**

| Period | £/yr |
|---|---|
| Winter 2021/22 | 1,093 |
| Summer 2022 | 1,673 |
| Q4 2022 | 2,972 |
| Q1 2023 | 3,582 |
| Q2 2023 | 2,762 |
| Q3 2023 | 1,766 |
| Q4 2023 | 1,641 |
| Q1 2024 | 1,723 |
| Q2 2024 | 1,520 |
| Q3 2024 | 1,414 |
| Q4 2024 | 1,543 |
| Q1 2025 | 1,561 |
| Q2 2025 | 1,655 |
| Q3 2025 | 1,541 |
| Q4 2025 | 1,576 |

On the old consumption values, Jan-Mar 2023 was £4,059.

**Energy Price Guarantee (from 1 October 2022):**
- Unit rates, direct debit, including VAT: electricity **34.0p/kWh**, gas **10.3p/kWh**.
- Illustrative bill: £2,500 a year on the old consumption values, or £2,380 on current values.
- Government planned a £3,000 level from July 2023, but it "was never implemented". The EPG formally "ended on 31 March 2024".
- The same rates also acted as a floor for fixed-tariff support.

Source: https://researchbriefings.files.parliament.uk/documents/CBP-9714/CBP-9714.pdf

Standing charges were not changed: "The reductions will come on unit rates rather than standing charges, which will stay as set by Ofgem for October 2022". Average direct debit standing charges were about **46p/day** for electricity and **28p/day** for gas. Prepayment customers on meters received £67 a month in vouchers, which comes from the government's separate Energy Bills Support Scheme rather than the EPG. https://www.which.co.uk/news/article/liz-trusss-energy-guarantee-puts-price-cap-at-2500-for-two-years-calculate-your-new-bills-aitQB9G0bkD5

### 5. Time-of-use tariffs

**Restricted meters (2015, CMA):**
- About 4.4 million restricted meters, roughly 17% of 26.4 million accounts (likely an overestimate).
- Economy 7 accounted for 3.7 million of them (84% of restricted meters, 14% of all accounts). Economy 10 accounted for 0.1 million and other restricted meters for 0.6 million.
- Source: https://assets.publishing.service.gov.uk/media/577521a9e5274a0da3000123/fr-appendix-9-5-restricted-meters.pdf

**Restricted meters (2020, Ofgem):**
- "Around 4 million out of a total of 29 million domestic electricity customers" had restricted meters.
- Non-Economy 7 restricted meters numbered fewer than 500,000, down from about 700,000.
- SLC 22G (from the CMA Order) makes large suppliers offer all their single-rate tariffs to restricted-meter customers. Ofgem proposed extending it to 30 June 2025.
- Source: https://www.ofgem.gov.uk/system/files/docs/2020/08/statutory_consultation_extending_protections_for_non-e7_restricted_meter_customers_slc_22g.pdf

**Modern time-of-use tariffs (Ofgem State of the Market reports):**
- To January 2025: 395k rising to 664k (+68%), of which EV tariffs went from 243k to 502k. Penetration was 2.3%. https://www.ofgem.gov.uk/sites/default/files/2025-04/OFG2296_State%20of%20the%20Market%20Report.pdf
- To July 2025: 497k rising to **835k**, of which EV tariffs went from 354k to **653k**. Penetration was **2.8%**. https://www.ofgem.gov.uk/sites/default/files/2026-01/State-of-the-Market-Energy-Retail-Highlights-January-2026.pdf

**Octopus products (as described on Octopus's current pages):**
- **Agile:** half-hourly rates "tied to wholesale prices", published daily between 4 and 8pm for the next 24 hours, with a 100p/kWh ceiling. Needs a SMETS2 meter or a compatible SMETS1 meter, and bills from half-hourly reads. https://octopus.energy/smart/agile/
- **Intelligent Octopus Go:** off-peak window 23:30-05:30, smart EV charging "from only 8p/kWh" (the current 2026 rate, not historical), and the car or charger must pass an eligibility check. https://octopus.energy/smart/intelligent-octopus-go/
- **Uptake:** Octopus says "More than one million customers have benefitted" from Intelligent Octopus Go, Agile and Cosy. That is a cumulative count, not a live base. https://www.businessgreen.com/news/4531206/smart-tariffs-saved-octopus-energy-customers-1bn-2017
- Launch dates (Agile about 2018, Go about 2019) are **[UNVERIFIED]**. *Seat: Go corrected to June 2018; Agile February 2018 on a weak source, see V5.*

**Prerequisites:**
- **Smart meters:** "over 40 million installed ... by the end of September 2025", which is 70% of domestic meters. About 8.3% of smart meters are not operating in smart mode. (Ofgem January 2026, link above.)
- **Market-wide half-hourly settlement (MHHS):** the start of migration (M10) moved to September 2025, with supplier migration from October 2025. Cutover to the new settlement timetable moved from December 2026 to July 2027. https://www.elexon.co.uk/2024/11/29/ofgem-approval-of-change-request-055-to-allow-for-robust-testing-time/

### 6. Dual fuel discounts and the RMR tariff rules

- **The rules being removed (SLC 22A/22B, introduced 2013):**
  - a cap of "more than four core tariffs per fuel per metering arrangement in any region" (SLC 22B.2);
  - limits on discounts beyond three permitted cash types;
  - a single standing charge per tariff;
  - rules on bundles and reward points;
  - a ban on tariffs exclusive to new or existing customers.

  Source: https://www.ofgem.gov.uk/sites/default/files/docs/2016/08/rmr_simpler_removal_stat_con_-_open_letter_august_2016.pdf
- **Other RMR rules described by SSE:** two-tier tariffs were banned, and tracker tariffs were banned unless linked to an external index. https://www.sse.com/news-and-views/2013/12/retail-market-review-what-does-it-mean-for-you/
- My recollection that the three permitted discounts were dual fuel, online account management and payment method is **[UNVERIFIED]**. *Seat: two of three confirmed, see V6.*
- **CMA view:** "the RMR four-tariff rule limits the ability of suppliers to compete and innovate" (para 174).
- **Removal:** Ofgem said on 14 April 2016 that it would "not intend to enforce these rules" (https://www.ofgem.gov.uk/publications-and-updates/changes-our-retail-market-review-reforms). It opened a statutory consultation on formal removal on 3 August 2016. The date the formal decision took effect is **not verified**.
- No source I fetched gives the size of dual fuel discounts in £.

---

### Headline figures and bands for checking a simulated world

| Metric | Band |
|---|---|
| Default/SVT share, large legacy suppliers, 2016-17 | 57-70% (whole-market share lower) |
| Fixed share, August 2021 | ~45-48% |
| Fixed share, mid-2023 (low point) | ~9-11% |
| Fixed share, January 2025 | ~25-30% |
| Fixed share, July 2025 | ~30-35% |
| Gap, cheapest fix vs default, normal market | £140-£330 a year for typical dual fuel |
| Gap during 2022 | ≤£100, and many fixes priced above the cap |
| Exit fees | ~~£0-£30 per fuel~~ **corrected (V2):** £5-£30 per fuel before 2021; about £75 per fuel on a 12-month fix and up to £200 on a 2-year fix in 2022-23. None in the final 49 days. Renewal notice sent 42-49 days before the end |
| Cap Q1 2019 | £1,137 (direct debit, typical dual fuel) |
| Cap Q1 2023 (peak) | £3,582 (current consumption values) |
| Cap Q4 2025 | £1,576 |
| EPG Oct 2022-Jun 2023 | 34.0p/kWh electricity and 10.3p/kWh gas. Standing charges about 46p and 28p a day |
| Restricted meters | 14-17% of electricity accounts (Economy 7 ~12-14%) |
| Modern time-of-use, mid-2025 | 0.8-0.9m accounts (~2.5-3%), of which ~75-80% EV tariffs |
| Smart meter penetration, September 2025 | ~70%, with about 8% not operating in smart mode |

### Gaps the pack could not fill

1. **Ofgem RMI tariff-type monthly series, 2016-2025:** it exists only as chart data. A CSV download from the data portal is needed.
2. **Share of fixes by length (12/18/24 months)** and how that mix changed over time.
3. **Exit fee levels over time, and whether any rule limits them:** I found no regulatory cap. Crisis-era fee levels are not verified.
4. **Current SLC 22C wording after the 2022-2024 changes**, including whether the 42-49 day window still applies unchanged.
5. **Nil-consumption cap values by region** and how the standing charge share moved, including the EPG standing charges by region.
6. **When prepayment joined the default cap and the levelisation details.**
7. **Customer numbers for each Octopus product** (Agile, Go, Intelligent Go, Cosy), plus OVO and British Gas EV tariff disclosures.
8. **Current Economy 7 count**, after 2020.
9. **Date the RMR simpler rules were formally removed**, the permitted discount types, and dual fuel discount values in £.
10. **Date the BAT actually ended.**
11. **Whether CMA detriment figures are averages for 2012-2015, and how they split between domestic and microbusiness customers.**