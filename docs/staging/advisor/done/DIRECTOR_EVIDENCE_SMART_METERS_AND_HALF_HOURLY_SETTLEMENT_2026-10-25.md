# Director evidence: smart meters and half hourly settlement

**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** unassigned · **Atom:** `unminted`

## Why this is here

- 05:15 GMT: "Is there no way to use the spare tokens productively? On knowledge creation for example ? Or improving the website? Things that don't impact it's need to run tasks in series"

The advisor spent spare allowance outside your serial gate on research for the knowledge pages the map found missing. This file is one of seven cited evidence packs landed in one commit.

## What to do with it

- Turn it into a published Knowledge page under the map steer (DIRECTOR_STEER_THE_MAP_ONE_CONCEPT_REGISTER_FOUR_SPINES_AND_A_KNOWLEDGE_PLAN). Register its concepts in the concept register.
- The headline-bands table at the end gives candidate world claims for the knowledge-checks-the-world gate. Grade the simulated world against them and say where it falls outside.
- Items marked [derived] are arithmetic you can re-run. Items marked [unverified] are not claims until you source them.
- Each named gap is a research task. Close it, or record that nothing is published.
- This is drafting work. Do it without displacing the serial queue. The research cost has already been spent.

---

# Smart meters, half-hourly data and market-wide half-hourly settlement in GB

*Evidence pack for the Poesys knowledge layer. Compiled 25 October 2026. Every figure carries its source. Where a figure came from a secondary source or from recollection, it is marked.*

---

## 1. Smart meter rollout (DESNZ / BEIS quarterly statistics)

**Year-end snapshots.** Only these points were confirmed from report text. A full quarter-by-quarter series is listed under Gaps.

| Point | Domestic smart, operating in smart mode | Domestic smart, any mode | SMETS1 / SMETS2 / advanced (all sectors) | Traditional (dumb) mode | Source |
|---|---|---|---|---|---|
| 30 Sep 2016 | 4.05m, "8 per cent of all domestic meters operated by large energy suppliers" | n/a | n/a | n/a | [BEIS Q3 2016](https://bpec.org.uk/wp-content/uploads/2017/02/2016_Q3_Smart_Meters_Report_Final.pdf) (mirror) |
| 31 Mar 2019 | 13.19m (26%) | n/a | 630k domestic SMETS2 connected to DCC | "2.3 million smart meters were known to be operating in traditional mode" | [BEIS Q1 2019](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/804767/2019_Q1_Smart_Meters_Report.pdf) |
| End 2019 | 15.2m, "29% of all domestic meters" (of 51.8m) | n/a | 3.3m domestic SMETS2 on DCC | "just under 4.0 million" | [BEIS Q4 2019](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/872155/2019_Q4_Smart_Meters_Statistics_Report.pdf) |
| End 2020 | 19.1m in smart mode, all sectors (34%); 23.6m installed | 42% of all meters | n/a | about 4.5m (derived) | [POST](https://post.parliament.uk/smart-meters/) (secondary) |
| End 2021 | 22.0m | 26.1m (50%) | 15.3m / 11.1m / 1.3m | 4.18m domestic | [BEIS Q4 2021](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1059591/Q4_2021_Smart_Meters_Statistics_Report.pdf) |
| End 2022 | 26.4m | n/a | 15.1m / 14.8m / 1.3m | 3.2m | [Enlit](https://www.enlit.world/library/over-31-3-million-smart-meters-in-gb) (secondary) |
| 31 Mar 2024 | 56% (large suppliers) | 63% | n/a | 3.857m | [DESNZ Q1 2024](https://assets.publishing.service.gov.uk/media/66589b088f90ef31c23ebc73/Q1_2024_Smart_Meters_Statistics_Report.pdf) |
| End 2024 | 60% | 66% (about 36m) | about 14m / 23m / 1.3m | 6.4% of all meters | [DESNZ Q4 2024](https://assets.publishing.service.gov.uk/media/67d95f7c4ba412c67701ed58/Q4_2024_Smart_Meters_Statistics_Report.pdf) |
| End 2025 | "65%… in smart mode", over 35m, up 9.3% | 38m (71%) of over 54m domestic meters | "13 million were SMETS1, 27 million SMETS2 and 1.3 million advanced" | 5.6% of domestic meters | [DESNZ Q4 2025](https://assets.publishing.service.gov.uk/media/69b80e30b84f01b2be53a2b1/Q4_2025_Smart_Meters_Statistics_Report.pdf) |
| 31 Mar 2026 | 66% of all meters in smart mode or advanced | 72% | n/a | 5.3% of all meters | [DESNZ Q1 2026](https://assets.publishing.service.gov.uk/media/6a17646365bc5f798327f424/Q1_2026_Smart_Meters_Statistics_Report.pdf) |

**Other end-2025 figures** ([Q4 2025](https://assets.publishing.service.gov.uk/media/69b80e30b84f01b2be53a2b1/Q4_2025_Smart_Meters_Statistics_Report.pdf)):
- 41m smart and advanced meters in total, and "92.3% of all smart and advanced meters were operating in smart mode".
- 2.7m domestic installs in 2025, down 4.9% on 2024. Q4 2025 installs were 572k.
- 11.3% of domestic smart meters are in prepayment mode.

**Non-communicating meters.**
- In 2023 the Public Accounts Committee reported 3m (9%) smart meters not fully functioning, and about half of those had "transitory" issues ([POST](https://post.parliament.uk/smart-meters/)).
- Causes cited in the same briefing:
  - SMETS1 meters lost smart mode on switching before DCC enrolment. "70% of SMETS1 meters lost smart mode functionality" when the customer switched supplier.
  - 0.75% of homes were outside WAN coverage in 2023.
  - The NAO estimates 7m meters are at risk from the 2G/3G phase-out.
- The SMETS1 count fell from 15.3m (2021) to 13m (2025). That is consistent with replacements, but the reason for the fall is not confirmed.

**Small inconsistency to note.** Several reports give large-supplier-only domestic figures (2016, Q1 2019, Q1 2024). These are not strictly comparable with the all-supplier figures from 2020 onwards.

## 2. Domestic settlement before MHHS: profile classes and elective HHS

- Elexon defines the profile classes as follows ([Elexon profiling](https://www.elexon.co.uk/bsc/settlement/profiling/)):
  - PC1: Domestic Unrestricted
  - PC2: Domestic Economy 7
  - PC3: Non-Domestic Unrestricted
  - PC4: Non-Domestic Economy 7
  - PC5–PC8: Non-Domestic Maximum Demand, banded by load factor (<20%, 20–30%, 30–40%, >40%)
- "Profile Classes 1 and 2 are for domestic premises and Profile Classes 3 to 8 are for non-domestic premises."
- **How profiling works.** An annual quantity (Annualised Advance or EAC) "is allocated under the Profile shape" using regression coefficients. The coefficients are refreshed twice a year from a sample of about 2,500 sites ([Elexon](https://www.elexon.co.uk/bsc/settlement/profiling/)).
- **Share on profiles vs HH.** At the April 2021 decision, "most customers are currently settled on a non-half-hourly basis, using estimated usage profiles" ([S&P Global on Ofgem decision](https://www.spglobal.com/commodity-insights/en/news-research/latest-news/electric-power/042021-uk-regulator-approves-half-hourly-settlement-in-retail-power-market)).
- **Elective domestic HHS.** I found no published count. *Recollection, unverified:* uptake was in the low hundreds of thousands of MPANs, concentrated in suppliers offering time-of-use tariffs.

## 3. Market-wide Half-Hourly Settlement (MHHS)

**Decision.** Ofgem approved MHHS on **20 April 2021**.
- Estimated consumer net benefits: £1.6bn–£4.5bn by 2045.
- Original plan: about 4.5 years, completing by October 2025.
- Elexon was appointed programme manager.
- Anna Rossington, for Ofgem: "This decision marks a major milestone in the transition to the smart, flexible energy system."
- Source: [S&P Global](https://www.spglobal.com/commodity-insights/en/news-research/latest-news/electric-power/042021-uk-regulator-approves-half-hourly-settlement-in-retail-power-market); decision document [here](https://www.ofgem.gov.uk/system/files/docs/2021/04/mhhs_draft_ia_consultation_decision_document_final_version_for_publication_20.04.21.pdf) (the PDF was not machine-readable to me).

**Replan (CR022, published 12 June 2023).**
- Dates moved:
  - Migration start (M11): Oct 2024 → Apr 2025
  - Migration completion (M15): Oct 2025 → Oct 2026
  - New settlement timetable cutover (M16): Nov 2025 → Dec 2026, with a range out to May 2027
- Ofgem called the original timetable "unrealistic and unachievable since mid-2022".
- The migration window was widened from 12 to 18 months because 12 months would have meant peaks of over 300,000 MPANs per day.
- Source: [Ofgem CR022](https://www.ofgem.gov.uk/sites/default/files/2023-06/Decision%20on%20MHHS%20Change%20Request%20CR22.pdf)

**Current milestones** ([Elexon MHHS](https://www.elexon.co.uk/bsc/operational/market-wide-half-hourly-settlement/)):

| Milestone | Date |
|---|---|
| M10: central systems live | 22–24 Sep 2025 |
| M11/M12: migration starts | 22 Oct 2025 |
| M14: all suppliers qualified | 28 Oct 2026 |
| M15: migration complete | 7 May 2027 |
| M16: shorter timetable cutover | 2 Jul 2027 |

Elexon on M11/M12: "the culmination of five years' work across the sector" ([Elexon, 22 Oct 2025](https://www.elexon.co.uk/2025/10/22/suppliers-start-moving-meters-to-half-hourly-settlement-hitting-a-major-milestone-for-clean-power-2030/)).

**Progress at June 2026.** "More than 11.3 million migrations completed", which is about a third of metering systems.
- 11 suppliers are migrating, and two have completed about 75% of their migrations.
- About 80% of meters are forecast to be migrated by October 2026.
- Elexon expects "up to 500 billion half-hourly meter readings" a year.
- Source: [Elexon](https://www.elexon.co.uk/bsc/article/two-suppliers-complete-75-of-their-migrations-under-the-mhhs-programme/)

**What changes for suppliers.**
- Settlement uses actual consumption for each half-hour, "rather than estimates or monthly readings". Non-smart and non-communicating meters are settled through the Load Shaping Service, switched on at M13 ([Elexon](https://www.elexon.co.uk/bsc/operational/market-wide-half-hourly-settlement/)).
- The final reconciliation window shrinks from 14 months to 4 months (see section 6).

## 4. Data access and consent

**Original Data Access and Privacy Framework** (DECC consultation, April 2012) ([DECC](https://assets.publishing.service.gov.uk/media/5a79b55c40f0b642860da234/Data_access_and_privacy.pdf)):
- **Monthly data:** no consent needed, for billing and statutory obligations including settlement.
- **Daily data:** usable "for any purpose except marketing, with clear opportunity for the customer to opt out".
- **Half-hourly data:** "explicit (opt-in) consent" required.
- **Marketing:** opt-in whatever the granularity.
- Settlement access was to be reviewed if settlement rules changed.

**Settlement change (Ofgem decision, June 2019).**
- The party responsible for settlement gets a legal obligation to process domestic HH data, with consumer opt-out replacing opt-in ([Ofgem](https://www.ofgem.gov.uk/decision/decision-access-half-hourly-electricity-data-settlement-purposes); [open letter June 2020](https://www.ofgem.gov.uk/sites/default/files/docs/2020/06/open_letter_-_clarification_on_issues_around_access_to_data_for_settlement_purposes_-_june_2020_0.pdf)).
- The microbusiness opt-out was removed.
- Export data cannot be opted out.

**SLC 47 as modified** (decision 7 Sep 2022, effective 3 Nov 2022) ([Ofgem](https://www.ofgem.gov.uk/sites/default/files/2022-09/Decision%20on%20Modifying%20SLC%2047%20of%20the%20electricity%20supply%20licence.pdf)):
- **"New System" domestic customers** (new smart install or new contract): HH data by default, with opt-out to daily.
- **"Old System" domestic customers:** daily data by default, with opt-in to HH or opt-out to monthly.
- **HH time-of-use tariff customers:** must share HH data and cannot opt out.
- **Notice:** suppliers must wait seven days after notice before moving to finer data, unless the customer consents explicitly.

**Consent and opt-out rates.**
- I found no outturn data.
- Ofgem's experiment (April 2021, n=1,615, hypothetical) found 76% would "definitely or probably allow" HH sharing, 19% were unsure and 5% would not ([Ofgem consumer research](https://www.ofgem.gov.uk/sites/default/files/2022-09/MHHS%20Consumer%20Research%20FINAL.pdf)).
- Opt-out risk was 19–27% depending on letter design.

## 5. Read frequency for non-smart meters and estimated bills

**Correction to the brief.**
- SLC 21B requires suppliers to "take all reasonable steps to obtain meter readings at least annually" ([Ofgem licence guide, 2019](https://www.ofgem.gov.uk/sites/default/files/docs/2019/02/licence_guide_metering_billing_and_payments_1.pdf); restated in [Ofgem billing assessment, July 2026](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf)).
- The "at least once every two years" wording belongs to the old **SLC 12.14 meter *inspection*** duty for NHH meters. It was removed with effect from **1 April 2016** ([Ofgem notice](https://www.ofgem.gov.uk/sites/default/files/docs/2016/02/notice_of_licence_modifications_to_the_standard_conditions_of_the_electricity_supply_licences.pdf); [proposal](https://www.ofgem.gov.uk/sites/default/files/docs/2015/11/notice_of_proposed_licence_modifications_to_the_standard_conditions_of_the_elec_supply.pdf)).

**MHHS changes.** I found no licence change to the 21B read frequency. Under MHHS, non-smart meters remain read-dependent and are settled using Load Shaping Service shapes.

**Estimated bills** ([Ofgem, published 27 Jul 2026](https://www.ofgem.gov.uk/sites/default/files/2026-07/domestic-billing-performance-assessment.pdf)):
- In 2024, "81% of bills are based on actual meter readings at first issue" and "89%… after reconciliation". By implication, about 19% were estimated at first issue.
- "Customers with smart meters experience higher accuracy and fewer estimated bills". No split by meter type is published.

## 6. Reconciliation run timetable

**Legacy timetable**, measured from the settlement period ([Elexon glossary](https://www.elexon.co.uk/bsc/glossary/1st-reconciliation/)):

| Run | Timing |
|---|---|
| Interim Information | 1 week (no money moves) |
| Initial Settlement (SF) | about 1 month |
| R1 | 2 months |
| R2 | 5 months |
| R3 | 7 months |
| RF | 14 months |
| Dispute Final (DF) | 28 months |

- A more recent Elexon article puts SF at 15 working days ([Elexon](https://www.elexon.co.uk/bsc/article/new-settlement-timetable-reducing-from-14-months-to-seven-months-from-april-2027/)).
- **How volumes are trued up:** each run replaces estimated or profiled values with actual reads as they arrive, and the cash difference is re-charged. The performance target is 97% of energy on actual data by RF ([Elexon RF glossary](https://www.elexon.co.uk/bsc/glossary/final-reconciliation-volume-allocation-run/)).
- *Recollection, unverified:* an Elexon slide deck suggests about 30% of energy is on actual data at the Interim Information run, rising through the reconciliation runs ([Ofgem/Elexon 2014](https://www.ofgem.gov.uk/sites/default/files/docs/2014/06/slides_elexon_0.pdf)). The axis mapping is ambiguous.

**Transition timetable** ([Elexon](https://www.elexon.co.uk/bsc/article/new-settlement-timetable-reducing-from-14-months-to-seven-months-from-april-2027/)):
- RF falls to **7 months from 1 April 2027**, then to **4 months from 2 July 2027 (M16)**.
- SF moves to **7 working days**, subject to an April 2027 decision.
- The intermediate runs under the target timetable were not confirmed.

---

## Headline figures and check bands for a simulated world

| Metric | Reference value | Suggested band |
|---|---|---|
| Domestic meters smart (any mode), end 2025 | 71% | 68–74% |
| Domestic meters smart and in smart mode, end 2025 | 65% | 62–68% |
| Smart meters in traditional mode (share of domestic meters), 2024–25 | 5.6–6.4% | 4–8% |
| Smart-mode share of smart and advanced meters | 92.3% | 90–94% |
| SMETS1 : SMETS2 ratio, end 2025 | 13m : 27m (about 1:2) | 0.4–0.6 |
| Domestic smart in smart mode, trajectory | 8% (2016, large suppliers) → 29% (2019) → about 42% (2021, derived: 22.0m of about 52m) → 60% (2024) → 65% (2025) | monotone, +4–6 pp a year after 2021 |
| Annual domestic installs | 2.7m (2025) | 2.4–3.2m |
| Domestic prepay share of smart | 11.3% | 10–13% |
| MHHS migrated share | about 33% (Jun 2026) → about 80% (Oct 2026) → 100% (May 2027) | ±10 pp of the plan |
| RF window | 14 → 7 (Apr 2027) → 4 months (Jul 2027) | exact |
| Bills on actual reads, first issue | 81% | 75–85% |
| HH settlement opt-out rate (New System) | hypothetical risk 19–27% | 5–25% (outturn unknown) |

## Named gaps

1. **Quarterly series.** A full quarter-by-quarter series for 2016–2025 is only in the DESNZ data tables (Tables 1–4), which I did not read. The figures for 2017, 2018, 2020 (all-supplier) and 2023 are missing or secondary.
2. **Profile-class populations.** I have no published MPAN counts per profile class (PC1 vs PC2), and no total domestic electricity MPAN count.
3. **Elective domestic HHS uptake.** No primary figure was found.
4. **Opt-out outturns.** No actual HH consent or opt-out rates under SLC 47 have been published.
5. **Ofgem 2021 decision text.** The PDFs were unreadable. Net benefits are taken from a secondary source.
6. **Target intermediate runs.** The R1/R2/R3 timings under the MHHS target timetable are not confirmed.
7. **Estimated bills by meter type.** No split between smart and traditional meters is available.
8. **Non-communicating SMETS1/SMETS2 counts.** The latest DCC figures were not retrieved.
## Done

2026-10-25, seat-executor, claim `knowledge-pages-tariffs-smart-meters-vulnerability` (owed page 5 of
the 24 Oct map steer).

- Published as `site/knowledge/smart-meters-and-half-hourly-settlement/` (theme: billing, after
  metering-and-reads). The pack is kept as the note
  `docs/market_research/smart_meters_and_half_hourly_settlement_2026-10-25.md`, with a section on what
  the world and company do, read from code.
- **Verified while drafting:** 2 confirmed (end 2022 at the DESNZ primary bulletin), 1 corrected (the
  "30% at the Interim Information run" is 30% at R1) and 3 still open. One of the three open items
  is a conflict: Elexon's glossary puts R2 at 5 months, and Elexon's 2014 slides, which the world
  uses, put it at 4.
- Four concepts: `meter.smart_meter`, `settle.reconciliation_run`, `settle.mhhs` and
  `meter.hh_data_consent`. The two notes owed to this page now attach.
- **Found from code:**
  - The smart-meter share has two homes. The world's (`simulation/premise_population`, DESNZ Table 5a)
    is within about 5 points of the record. `saas/smart_meter_rollout` runs 4-10 points higher, and it
    gates the time-of-use offer. Its 72% divides meters by households.
  - `company/market/mhhs_tracker.py` holds a go-live date of 5 June 2025, which the record does not.
  - Filed in `docs/staging/SEAT_FINDING_TWO_SMART_METER_SERIES_AND_A_DISPUTED_R2_DATE_2026-10-25.md`.
