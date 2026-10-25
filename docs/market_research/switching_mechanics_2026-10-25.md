# How GB domestic switching works: loss notices, objections, saves, erroneous transfers and dual fuel

**Knowledge:** switching-mechanics

Written 2026-10-25 for the director's map steer of 24 Oct (item 4, second owed page), from the
advisor's cited evidence pack `docs/staging/advisor/done/DIRECTOR_EVIDENCE_SWITCHING_LOSS_OBJECTIONS_AND_DUAL_FUEL_2026-10-25.md`.
Figures marked **[derived]** are the pack author's arithmetic on published numbers. Items marked
**[unverified]** are not claims until sourced. The QEP Table 2.7.1 spreadsheet was not opened in the
pack's pass; its quarterly figures come from the QEP statistical-release PDFs, which are revised
between editions. `gb_domestic_switching_by_calendar_month.md` did open the spreadsheet (monthly,
Jan 2003 to Jun 2026) and is the better source for any monthly series.

Related notes already on other pages, read beside this one: `a_save_offer_against_the_switching_rules_and_the_seam.md`
(the save offer, SLC 14.4 and SLC 22B), `domestic_debt_objection_rates_gb.md` (the three objection
rates and their denominators), `gb_switching_rate_denominators.md` (which numerator goes over which
account count), `gb_domestic_switcher_split_cim_2022_2025.md` (internal against external switching).

## 0. What this project's world and company do today (read from code, not run)

- **The loss notice crosses the wall.** `interface/contracts/registration_loss_seam.py` (REC Schedule
  23 v2.2) carries one notice per meter point: the Secured Inactive notice, and from CSS go-live the
  Invitation to Intervene, dated at the latest submission day the one-working-day floor allows, so no
  save is flattered with warning a real loser might not get. The world emits it
  (`simulation/registration_loss_feed.py`); the company keeps it (`company/crm/cos_process.py`).
- **The debt objection is the company's (EP12, amended 2026-10-25).** On a domestic renewal departure
  the company reads its own ledger on the switch-request day
  (`company/market/transfer_objection_register.decide_debt_objection`, through
  `company/interfaces/transfer_objection.py`): it objects when debt on bills more than 28 days old
  exceeds £200 per fuel (the top of the published informal de-minimis range, "up to £200 per fuel"),
  and never to a prepayment debt under the £500 Debt Assignment Protocol ceiling. The world cancels
  exactly the switches it objected to (`simulation/debt_objection.py`) and keeps the household's
  own payment behaviour. Until this date the world drew the block itself at 0.283 (Ofgem 2016: about
  170k blocked against 430k allowed a year); those counts now grade the company's output. Choices
  and gaps: the per-fuel de-minimis is applied to an account ledger as threshold x fuels (objects
  less often than a per-fuel ledger would); the request is read on the ASAP floor in both regimes,
  which pre-CSS overstates objections; a blocked household is asked again only at its next renewal
  (the IA's repay-and-switch route, rows 22-23 of `domestic_debt_objection_rates_gb.md`, is not
  modelled).
- **The save is made on the Invitation to Intervene, from 18 July 2022 only.**
  `simulation/save_on_loss_notice.py` re-asks the household's own renewal roll at the company's
  Fixed Retention Tariff price (`company/crm/save_offer.py`), for a household leaving a fixed term at
  its renewal point only (a default-tariff leaver is offered nothing); it is switched on by the director
  (10 Oct). In the record a save only works if the household cancels with the gaining supplier, which
  withdraws; since REC R0287 (27 Feb 2026) annulment cannot be used for it. The run ends in 2025, so
  R0287 does not bite inside it.
- **There is no failed switch.** The seam's own `GAPS` say a switch never ends Cancelled, Withdrawn or
  Annulled, so the world has no erroneous transfer (0.5-1% of switches pre-CSS), no cooling-off
  cancellation and no customer-requested objection.
- **Dual fuel moves together.** The world decides departure per billing account, so both fuels of a
  dual-fuel household leave on one decision: the same shape as CSS's one-fail-all-fail linking.

Not checked here: whether the world's departure level sits in the quarterly bands below. That grade
belongs to `gb_switching_rate_denominators.md`, which states the matched numerator and denominator.

## 1. The switching process before and after CSS

**Before CSS (to 17 July 2022)**
- Ofgem's "as-is" map: the customer accepts a quote, a "Cooling off period (14 days)" follows, the
  gaining supplier registers the MPxN on MPAS (electricity, "an overnight batch process") or UK Link
  (gas), and the "Losing supplier has circa 1 week to register an objection; if it does, the switch is
  cancelled." Then agent appointments, the change-of-supplier read, final and opening bills. "Current
  average switching time are between 15 and 16 calendar days but can be longer."
  https://www.ofgem.gov.uk/sites/default/files/docs/2018/02/as_is_switching_arrangements.pdf
- Objection windows were "up to 7 working days for gas and 5 for electricity".
  https://www.ofgem.gov.uk/sites/default/files/docs/2017/09/policy_update_objections.pdf
- The three-week rule (2014): suppliers "take all reasonable steps" to switch within three weeks of
  the Relevant Date (end of cooling-off, or earlier if the customer agrees). Before it, more than 20%
  of domestic electricity and more than 80% of domestic gas transfers took longer than three weeks.
  https://www.ofgem.gov.uk/ofgem-publications/87151/statutoryconsultationenforcethreeweekswitchingandpreventerroneoustransfers.pdf
- November 2016: most switches took about three weeks, down from about five three years earlier.
  https://www.ofgem.gov.uk/press-release/switching-45-year-high-more-people-shop-around-better-deal

**After CSS (from 18 July 2022)**
- CSS went live on 18 July 2022 with REC v3.0.
  https://www.ofgem.gov.uk/sites/default/files/2022-10/Switching%20SCR%20closure%20letter.pdf ;
  https://xoserve.com/change/investment-change/switching-programme-css
- SLC 14A.1 (as drafted): the gaining supplier completes a transfer "within five Working Days" of the
  Relevant Date. https://www.ofgem.gov.uk/sites/default/files/2021-12/Electricity_Supply_SLC_Notice%20-%20SCR%20StatCon%20-%20FOR%20PUBLICATION.pdf
- REC Registration Services Schedule (June 2019 draft; the live v2.2 is read in
  `registration_loss_seam.py`): domestic supply start "at least one complete Working Day (starting at
  midnight) after the day on which the Switch Request is submitted", up to 28 days ahead; the domestic
  objection window closes "at 17.00 hours on the 1st Working Day after the day on which the Gaining
  Supplier submitted the Switch Request"; the losing supplier receives an "Invitation to Intervene"; a
  registration is "Secured Active" at 17:00 the day before the start date.
  https://www.ofgem.gov.uk/sites/default/files/docs/2019/06/rec_registration_services_schedule.pdf
- Compensation: £30 from 1 May 2020 if a switch took more than 15 working days; from 1 April 2024 the
  threshold is 5 working days. https://www.ofgem.gov.uk/publications/new-customer-compensation-payments-further-improve-switching ;
  https://www.ofgem.gov.uk/decision/supplier-guaranteed-standard-performance-switch-speed-decision
- Cooling-off cancellation: "It is for the Gaining Supplier to withdraw the switch".
  https://www.ofgem.gov.uk/sites/default/files/2026-02/R0287-and-R0287A-Authority-Decision.pdf

## 2. Objections

- Grounds (SLC 14): debt (14.4(a), "Outstanding Charges are due"), erroneous transfer, customer
  request, related meter points not all transferring. The debt must be asked for and "outstanding for
  more than 28 days". Debt Assignment Protocol: prepayment customers with debt under £500 (raised from
  £200) can switch if the new supplier agrees.
  https://www.ofgem.gov.uk/system/files/docs/2016/07/impact_assessment_on_review_of_domestic_objections.pdf
- Rates before CSS: 6% electricity and 5% gas annual objection rates (March 2016), over 90% for debt;
  374,463 debt objections in 2013, 285,697 in 2014; about 70% of indebted transfers went ahead.
  "Only around 5%" of switches faced an objection.
  https://www.ofgem.gov.uk/sites/default/files/docs/2016/06/agenda_item_5-objections_summary_paper.pdf
- Ofgem kept debt blocking: "unlikely to be in the interests of domestic consumers to remove the
  transfer blocking conditions".
- Under CSS an accepted objection on one part of a linked group (OFAF, "one fail all fail") cancels
  "all other Pending or Confirmed Registrations within the OFAF Group".

## 3. The losing supplier's view: loss notices and saves

- Its only regulated responses to a Pending/Invitation to Intervene are an objection or an annulment.
- REC R0287 (approved 20 Feb 2026, live 27 Feb 2026) limits annulment to cases where "the consumer
  has not entered into a contract with the Gaining Supplier"; R0287A (annul where the customer wants
  to stay) was rejected; the aim was to "prevent retention-based misuse".
- SLC 22B, the ban on acquisition-only tariffs, since 14 April 2022: new-customer deals must also be
  open to existing customers. Extended to 31 March 2027; Ofgem is "minded to extend ... until 31 March
  2028", decision due November 2026. A market-wide derogation allows "bespoke 'retention-only' deals"
  to customers "reaching the end of a fixed term contract".
  https://www.ofgem.gov.uk/sites/default/files/2024-11/Decision_Future_of_the_Ban_on_Acquisition_only_Tariffs_after_March_2025.pdf ;
  https://www.ofgem.gov.uk/sites/default/files/2026-08/Renewal-of-Ban-on-Acquisition-only-Tariffs-after-March-2027.pdf
- Market Stabilisation Charge (14 April 2022 to 31 March 2024): the gainer compensated the loser for
  part of its hedging cost. https://www.ofgem.gov.uk/sites/default/files/2024-07/Decision_on_removing_the_BAT_July_2024.pdf
- GAP: no domestic rule names "save" or "win-back" contact after a loss notice. **[unverified]**: the
  Standards of Conduct and general marketing rules would govern it.

## 4. Erroneous transfers

- About 1% of transfers (2014); about 0.5% among the six large suppliers, roughly 25,000 a year, and
  about 1% non-domestic (2016). Mostly address and MPxN mismatches; only "approximately 85%" of
  matching data was thought correct.
  https://www.ofgem.gov.uk/sites/default/files/docs/2016/08/erroneous_transfers-policy_issue_paper.pdf
- Automatic £30 for an ET from 1 May 2020; 27% of first-tranche payments were for mistaken switches.
- After CSS: the Switching Address Quality Plan cut unmatched addresses by 700,000 in 2025-26; no ET
  count given. https://retailenergycode.co.uk/recco-at-five-five-years-of-building-a-better-retail-energy-market/

## 5. Volumes

QEP Table 2.7.1 counts "meter points a supplier gains from another" after a customer chooses to
switch; it excludes internal and white-label moves, mergers and SoLR.
https://www.gov.uk/government/statistical-data-sets/quarterly-domestic-energy-switching-statistics

| Period | Electricity | Gas |
|---|---|---|
| 2016 | 4.4m | 3.4m |
| 2017 | 5.1m | 4.1m |
| Q4 2019 | 1,501k | 1,227k |
| Q4 2020 | 1,515k (about 5.3%) | 1,128k |
| Q4 2021 | 579k | 368k |
| Q1 2022 | 225k (0.8%), lowest since 2008 | 158k (0.7%) |
| Q4 2022 | 223k | 134k |
| Q4 2023 | 560k (1.9%) | 441k |
| 2024 **[derived]** | about 2.68m | about 2.09m |
| 2025 **[derived]** | about 3.15m | about 2.47m |
| Q2 2026 | 789k (2.6%) | 609k (2.5%) |

Per-edition URLs are in the evidence pack. ElectraLink: 6.34m electricity changes at the 2019 peak,
3.21m in 2024, peaks in April and October (https://www.electralink.co.uk/2025/01/switching-rises-38-in-2024/).
Dual fuel: about 70% of electricity and 80% of gas customers held dual-fuel accounts in 2016 (Ofgem
press release above). Internal switching ran about three times external in 2026 (Ofgem CIM; see
`gb_domestic_switcher_split_cim_2022_2025.md`). SoLR: 28 failures from June 2021, about 2.4m customers
moved, Bulb's 1.6m in special administration, about £2.7bn or £94 a customer
(https://www.nao.org.uk/press-release/the-energy-supplier-market/), all outside the voluntary counts.

## Headline bands for checking the world

| Metric | Band | Basis |
|---|---|---|
| Domestic electricity transfers per quarter, normal market | 0.75-0.86m (2.5-2.8% of customers) | QEP 2024-26 |
| Pre-crisis peak per quarter | about 1.4-1.5m (about 5%) | QEP 2019-20 |
| Crisis trough per quarter | about 0.22m (0.8%) | Q1 and Q4 2022 |
| Gas-to-electricity transfer ratio | 0.75-0.80 | **[derived]** |
| Objection rate (pre-CSS) | 5-6% of switches, over 90% for debt | Ofgem 2016 |
| Erroneous transfer rate (pre-CSS) | 0.5-1% of switches | Ofgem 2014, 2016 |
| Internal to external switching | about 3:1 (2026) | Ofgem CIM |
| Switch completion | 5 working days, £30 compensation | SLC 14A, GSoP |
| Seasonality | April and October peaks, December trough | ElectraLink |

## Named gaps (nothing published found)

1. Objection rates after CSS, and how many objections are withdrawn.
2. Erroneous-switch rates after CSS.
3. The share of switches completed next day against 2-5 working days (the seam's ASAP floor rests on this gap).
4. The share of switches that are dual fuel.
5. Save rates on loss notices, and any domestic rule on win-back contact.
6. Cooling-off cancellation rates.
7. Exact annual per-fuel QEP 2.7.1 totals 2018-2025 (the 2024 and 2025 rows are sums of quarters).
8. Ofgem says 2026 external switching "fell slightly"; QEP shows Q2 2026 up 15.2% on the year. The two may cover different periods.
9. Not consulted: CMA 2016, DCC CSS performance reports.

## Second read: the advisor's verification pass, 25 Oct 2026

The first outcome table for this page (advisor, GB-packs verification file, 25 Oct, pass 2 §8).

| Item | Prior outcome | Advisor | Reconciled | Source |
|---|---|---|---|---|
| Win-back contact after a loss notice is governed by the Standards of Conduct and general marketing rules (§3) | tagged, unchecked | still open: an interpretation | **still open**. Check SLC 0 and SLC 25 in the consolidated licence | — |

Named gap 5 stands.

**Counts: confirmed 0 · corrected 0 · still open 1.**
