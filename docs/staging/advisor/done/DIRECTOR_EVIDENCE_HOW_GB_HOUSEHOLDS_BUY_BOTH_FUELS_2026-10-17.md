**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-EVIDENCE] How GB households buy and switch two fuels: the advisor's research for the single-fuel steer (2026-10-17)

**Type:** Evidence, attached to `DIRECTOR_STEER_THE_BOOK_IS_SINGLE_FUEL_DO_THE_KNOWLEDGE_WORK_2026-10-17.md`. Read the two together, and do the knowledge work the steer asks for. The director, in chat on Sat 17 Oct:

- 10:56 BST: "Do some research into supplier annual accounts and other sources. This is pretty fundamental to how the world works"

The advisor ran three research passes: supplier accounts, official statistics, and switching mechanics. The results are below, each with its source. **They are a starting set, not the knowledge page.**
- Open each source and confirm the quote.
- Resolve the conflicts flagged here.
- Fill the gaps.
- Write the page under `docs/market_research/`.

Where a number below is wrong, the source wins.

---

## 1. Your library already had the answer in June

`docs/market_research/rd_synthesis_june_2026.md`, "Finding 6: 75% of Residential Customers Should Be Dual-Fuel":
- It quotes "~75% of UK residential customers take both gas and electricity from the same supplier" (House of Commons Library).
- It then concludes "The proportion is correct by design."

That was true of the 13-account roster. It became false when the coin-drawn founders arrived on 28 Aug and again on 8 Oct, and nothing re-checked it. The finding was never wired to any check. That is the clearest case of the class the steer's step 3 asks you to explain.

The same library records that "86.3% of English homes use a gas-fired heating system" (English Housing Survey 2023-24). The founder draw has 93% of homes gas-heated.

## 2. The market stock, by household

| Source | Year | What it says |
|---|---|---|
| CMA final report, para 10 | 2016 | "28 million domestic electricity customers and 23 million domestic gas customers. There were 20 million dual fuel customers, 8 million single fuel electricity customers and 3 million single fuel gas customers." [link](https://assets.publishing.service.gov.uk/media/5773de34e5274a0da3000113/final-report-energy-market-investigation.pdf) |
| CMA / GfK customer survey, p.10 | 2015 | "Nearly three quarters of households (72%) had their gas and electricity supplied by one provider"; "just under one in ten had separate suppliers"; "(17%) only had electricity". Note: the chart shows 15%, so the report contradicts itself. [link](https://assets.publishing.service.gov.uk/media/54e75c53ed915d0cf700000d/CMA_customer_survey_-_energy_investigation_-_GfK_Report.pdf) |
| Ofgem Consumer Engagement Survey 2017 | 2017 | "89% of households have both gas and electricity supply"; of those, "Most (91%) respondents bought their gas and electricity from the same supplier". [link](https://www.ofgem.gov.uk/sites/default/files/docs/2017/10/consumer_engagement_survey_2017_report.pdf) |
| DESNZ subnational statistics | 2024 | "an estimated 16 per cent of domestic properties were not connected to the gas grid". DESNZ calls this an underestimate. It ranges from 24% in the South West to 7% in the North East. There were 29.3m domestic electricity meters. [link](https://assets.publishing.service.gov.uk/media/6945728a033693d5d50eb83d/subnational-electricity-and-gas-consumption-summary-report-2024.pdf) |
| Census 2021 (ONS), England and Wales | 2021 | 74% of households use mains gas as their only central heating; about 9% heat with electricity only. [link](https://ons.gov.uk/peoplepopulationandcommunity/housing/articles/census2021howhomesareheatedinyourarea/2023-01-05) |
| Ofgem State of the Market Assessment | 2013 data | Big Six: "8.1 million customers have single-fuel electricity tariffs" and "3.6 million have single-fuel gas tariffs". Centrica: "28 per cent … single fuel gas … 65 per cent are dual fuel". [link](https://www.ofgem.gov.uk/sites/default/files/docs/2014/03/assessment_document_published_1.pdf) |

**Advisor's reading, for you to test.** By household, the market is about:
- 70–75% dual fuel with one supplier;
- 8–11% split supply (both fuels, two suppliers);
- about 16% electricity-only, because they have no gas.

Gas-only exists almost entirely as the gas half of a split-supply home, or in a legacy incumbent's book. A gas meter (about 84–86%) and gas heating (about 74–86%, depending on how "only" is counted) are different measures. Say which one the premise draw should follow.

## 3. Supplier books, from their accounts and Ofgem segmental statements

Domestic figures, in thousands. "G/E" is gas meter points divided by electricity meter points.

| Supplier | Year | Electricity | Gas | G/E | Source |
|---|---|---|---|---|---|
| British Gas | 2023 | 5,981 | 6,763 | 1.13 | [Centrica CSS 2023](https://www.centrica.com/media/kopkt3zd/ofgem-consolidated-segmental-statement-2023.pdf). Plus 7,529 households ([prelims](https://www.rns-pdf.londonstockexchange.com/rns/2099D_1-2024-2-15.pdf)), which implies about 69% dual fuel, 21% gas-only and 10% electricity-only |
| British Gas | 2019 | 11,846 accounts | | | 7,080 households, so 1.67 accounts per household, about 67% dual fuel ([prelims](https://www.centrica.com/media-centre/news/2020/preliminary-results-for-the-year-ended-31-december-2019/)) |
| E.ON UK | 2024 | 4,882 | 3,311 | 0.68 | [CSS 2024](https://www.eonenergy.com/content/dam/eon-energy-com/Files/about-eon/reporting/e.on-uk-consolidated-segmental-statement-2024.pdf) |
| EDF | 2024 | 3,113 | 2,168 | 0.70 | [CSS 2024](https://www.edfenergy.com/sites/default/files/2025-12/CSS-2024-Submission-Final.pdf) |
| ScottishPower | 2023 | 2,594 | 1,849 | 0.71 | [CSS 2023](https://www.scottishpower.com/documents/d/guest/css-2023-hedging-update-apr-2025) |
| npower | 2015 | 2,923 | 2,062 | 0.71 | [RWE CSS 2015](https://www.eonenergy.com/content/dam/eon-energy-com/Files/about-eon/reporting/npower-statements/CSS%202015%20RWE.pdf) |
| SSE | 2017 | 3,913 | 2,591 | 0.66 | [CMA SSE/npower](https://assets.publishing.service.gov.uk/media/5bbcc88ce5274a3632521f84/sse_npower_final_report.pdf). Its table labels the columns gas then electricity; market shares show that is a labelling slip, so check it |
| Octopus | FY to Apr 2025 | 7,273 | 5,844 | 0.80 | [CSS](https://a.storyblok.com/f/275131/x/b758c36b3a/octopus-energy-css-fy24_25-apr26-2.pdf) |
| Utilita | FY to Mar 2025 | 807 | 675 | 0.84 | [CSS](https://utilita.co.uk/downloads/about/Consolidated_Segmental_Statement-Utilita_Energy_Limited_FY25_v5.pdf). The gas row was read by column position; verify it |
| E (Gas & Electricity) | FY to Mar 2025 | 170.5 | 161.7 | 0.95 | [CSS](https://e.org/Assets/Pdf/Consolidated%20Segmental%20Statement_2025.pdf) |
| Utility Warehouse | FY15 / FY19 | 579.6 | 470.2 | 0.81 | "80% of its energy customers were on dual fuel contracts" (CMA Appendix 2.2); FY19 counts from the [annual report](https://www.telecomplus.co.uk/~/media/Files/T/Telecomplus/documents/investors/reports-results-presentations/archive-reports/telecom-plus-plc-annual-report-year-ended-31-march-2019.pdf) |
| First Utility | FY14 | 705k customers | | | "over 90% of whom are on dual fuel contracts" (CMA Appendix 2.2) |

**What the books show, for you to test.** A supplier's mix depends on its history:
- **The former gas incumbent** has a gas-heavy legacy book: about 21% gas-only.
- **The former regional electricity incumbents** (SSE, npower, EDF, ScottishPower, E.ON) run G/E of 0.66–0.71. They carry an electricity-only tail from their home regions, on top of homes off the gas grid.
- **Challengers that grew by switching** run 80–95% dual fuel.

Poesys opened in 2016 as a challenger. On the evidence, its book should look like a challenger's, not an incumbent's, and certainly not 1% dual fuel with 27% gas-only.

**Gaps you should try to fill:** Good Energy, OVO, Bulb, Ecotricity and Co-op splits, and any split-supply figure after 2017.

## 4. Switching is a household decision

- **Ofgem Consumer Engagement Survey 2017** ([link](https://www.ofgem.gov.uk/sites/default/files/docs/2017/10/consumer_engagement_survey_2017_report.pdf)):
  - "96% of those who had switched both did so … at the same time".
  - "Just 1% of households with both gas and electricity supply had switched one and not the other."
- **Registration is per fuel, not per household.** Gas registered through Xoserve UK Link (SPAA), electricity through MPAS (MRA). Before CSS, "Each switch request is independent" and there was "No capability to create dependency between switch requests" ([Ofgem 2018](https://www.ofgem.gov.uk/sites/default/files/docs/2018/02/as_is_switching_arrangements.pdf)). For CSS, Ofgem chose "proceed where possible" over "one fail/all fail" ([2016 paper](https://www.ofgem.gov.uk/sites/default/files/docs/2016/02/agenda_item_6_-_dual_fuel_policy_paper.pdf)). So the decision is joint, and the mechanics can split it.
- **How single-fuel customers arise** ([Ofgem 2016](https://www.ofgem.gov.uk/sites/default/files/docs/2016/08/erroneous_transfers_-_summary_paper.pdf)):
  - erroneous transfers, about 0.5% of domestic switches, with MPxN and address mismatches "a particularly common cause";
  - fuel-specific debt objections;
  - deliberate splitting, about 1% a year;
  - legacy incumbency.
- **Transfer statistics count each fuel.** DESNZ QEP 2.7.1, Energy UK and Cornwall Insight all report the fuels separately. No source publishes the dual-fuel share of switches.
- **Prices are set per fuel.** The price cap is per fuel, payment method, region and meter type. The "typical dual fuel bill" is only an illustration. The retail market review (from Jan 2014) allowed only a flat £/year dual-fuel discount as a bundling incentive.
- **Partial losses.** No public data on a supplier losing one fuel and keeping the other. Given 96% simultaneous and 1% one-fuel switching, a lost dual-fuel household should almost always go whole.

## 5. What this suggests the world must do (the steer's steps 2 and 5 decide)

1. **Draw households, not fuel accounts.** A gas home buys both fuels from one supplier unless a stated, ranged mechanism splits it: legacy split supply, a failed or erroneous transfer, a debt objection, or a deliberate split.
2. **Set the opening book's mix from evidence** for a supplier of Poesys's type and vintage, carried as a labelled range. Gas-only should be a small tail with a cause attached.
3. **Leave and arrive as a household.** Dual-fuel homes already depart once, through `departure_decision_leg`. Check every entry and exit path does the same. One-fuel departures should happen only at the measured rate.
4. **Re-check the premise stock's gas share** against DESNZ (84%) and the English Housing Survey (86%), with a gas meter distinguished from gas heating.
5. **Wire the 75% finding, and its successors, into a book-composition check** that runs every Monday. A finding that checks nothing is how this survived.

— Advisor research for the director, 17 Oct 2026, at his request (10:56 BST, quoted above). The sources are primary or regulatory; quotes are as the research passes reported them, so confirm them before you rely on them.

## Done

*Worker tick, 17 Oct, with the steer it is attached to. The report is
`docs/staging/WORKER_FINDING_THE_OPENING_BOOK_WAS_ONE_PERCENT_DUAL_FUEL_AND_NOW_BEARS_THE_PUBLISHED_SPLIT_2026-10-17.md`.*

- **Confirmed in the primary documents this session:**
  - CMA final report ¶10: 20m / 8m / 3m.
  - CMA PF Summary ¶9 (Jan 2015): 19m / 8m / 4m.
  - GfK ¶41: 72%, and the 15%/17% conflict is real; both are kept as the range.
  - Ofgem CES 2017: 89% have both fuels; 96% of both-fuel switchers moved both at once; 1 point in 18 moved one fuel.
  - Octopus CSS FY25: 7,273k / 5,844k points.
- **Not re-read; cited as this file's:** UW 80%, First Utility >90%, Centrica 2023, and the ex-PES CSS figures.
- **What it changed.** It filled the knowledge page's challenger gap, and the founders moved from the market-wide 0.83 to the challenger/switching 0.90 of gas homes dual, with 0.83 as the range floor. Its §5 asks are answered in the report:
  1. Draw households: done.
  2. Opening mix from evidence for a challenger: done.
  3. Exits as a household: departure confirmed; home move and debt not yet re-measured.
  4. Premise gas share: meter-first on the book's homes; the harness panel is handed on.
  5. Composition check: a commit-gate test, mutation-proven, not a Monday ceremony. It runs on every commit, which is stronger.
- **Gaps still open:**
  - OVO, Bulb, Good Energy, Ecotricity and Co-op splits;
  - split supply after 2017;
  - partial losses.

  The mechanics this file found (per-fuel registration, erroneous transfers ~0.5%, debt objections) are the stated causes of the 10% split remainder.
