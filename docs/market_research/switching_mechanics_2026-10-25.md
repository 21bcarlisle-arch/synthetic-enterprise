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
  and never to a prepayment debt under the £500 Debt Assignment Protocol ceiling (a design choice that
  departs from practice; see section 2). The world cancels
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
  The Relevant Date is the 2014 rule's: the end of the 14-day cooling-off unless the customer agrees
  to an earlier start, so a switch with cooling-off runs up to about three weeks from sign-up. The
  pre-CSS "15 and 16 calendar days" sits after "Cooling off period (14 days)" on Ofgem's map but the
  map does not say which date it counts from, so it is not like for like with five working days.
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
- **The DAP is a route through an objection, not an exemption from it** (read 26 Oct 2026, IA §4.3-4.5
  and footnote 23). "The DAP process required an objection to be raised first in the case where the
  Point of Acquisition model is not used (or if the customer does not provide the relevant consent
  when switching)"; under the POA model (ten suppliers including the six largest, from April 2015)
  the sale captures "customer agreement to debt assignment in the event of a debt objection". The
  gaining supplier buys "90% of the customer's debt from the losing supplier up-front" and recovers
  it from the customer; above £500 it "is not obliged to take on the customer's debt". Use was "less
  than 500 in 2014 and less than 1,000 in Jan-Sept 2015", against 285,697 debt objections in 2014, of
  which prepayment was 32-36% (IA §1.27). So the company's rule of never objecting to a prepayment
  debt under £500 is its own choice, not the protocol: it lets the household go with the debt left on
  its ledger, where a real supplier would object and might sell 90% of it. GAP: whether £500 is per
  fuel, and whether the DAP survived CSS unchanged, are not stated in this source.
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

## 6. The switching guaranteed standards, as the regulations write them (read 21 Nov 2026)

Read from legislation.gov.uk, the principal instrument as amended, not from press summaries. Every
switching standard pays the ONE flat "standard payment" of reg 8, not an amount of its own.

| Standard | Reg | In force | Duty and clock | Who pays |
|---|---|---|---|---|
| Identify an erroneous transfer | 6A | 1 May 2019 | old and new supplier "must within 20 working days of the customer notification, agree whether the customer has been transferred without a valid contract" | both (the duty is on both) |
| Tell the customer the outcome | 6B | 1 May 2019 | the supplier first notified writes within 20 working days | the supplier first notified |
| Return the customer | 6C | 1 May 2019 | "the old supplier must within 21 working days of the agreement ... re-register the customer" | **old (losing)** supplier |
| Refund credit after a switch | 6D | 1 May 2019 | within 10 working days of the final bill | old supplier |
| Avoid an erroneous transfer | 6ZB | 1 May 2020 | "the new supplier must only complete a supplier transfer where there is a valid contract"; the failure occurs "when the old supplier and the new supplier have agreed that the customer has been transferred without a valid contract" | **new (gaining)** supplier |
| Switch speed | 6ZA | 1 May 2020 | the new supplier completes the transfer within **15 working days** "beginning with the day of receipt by the new supplier of sufficient information" to confirm the customer and identify the meter point(s); a later date the customer asked for is met on that date | **new (gaining)** supplier |
| Switch speed, amended | 6ZA(3)(a),(d),(4) | **1 April 2024** (S.I. 2024/108) | **5 working days** (6 if the contract was made after 5pm on a working day), beginning with the information day if the customer asked to start inside cooling-off, otherwise with the latest of the two information days and the expiry of the 14 days beginning with the contract day | new supplier |
| Final bill after a switch | 6CA | 1 May 2020 | within 6 weeks of losing responsibility | old supplier |

- **The payment (reg 8(2)):** "for each such failure, make a payment of £40 (a "standard payment") to
  the customer who is affected", "within 10 working days of the supplier's initial failure". £30 from
  1 May 2019; £40 from 2 January 2025 (S.I. 2024/1166). A payment not made in time owes a further
  "additional standard payment" of the same amount (reg 8(3)-(4)).
  https://www.legislation.gov.uk/uksi/2015/1544/regulation/8 ;
  https://www.legislation.gov.uk/uksi/2015/1544/regulation/8/2019-05-01
- **Instruments:** S.I. 2019/218 (6A-6D, in force 1 May 2019),
  https://www.legislation.gov.uk/uksi/2019/218/made ; S.I. 2020/116 (6ZA, 6ZB, 6CA, in force 1 May 2020),
  https://www.legislation.gov.uk/uksi/2020/116/made ; the 2024 switch-speed amendment,
  https://www.legislation.gov.uk/uksi/2015/1544/regulation/6ZA and Ofgem's decision of 6 Feb 2024,
  https://www.ofgem.gov.uk/decision/supplier-guaranteed-standard-performance-switch-speed-decision
- **Exemptions that remove a payment:** a customer who withdraws after completion, suspected fraud
  (9(7AA)); no usable contact details despite reasonable endeavours (9(7AB), additional payment only).
- **Before 1 May 2019 there was no statutory switching payment.** The 2015 Regulations' standards were
  regs 3-6 (appointments, faulty meters, prepayment faults, reconnection); 2019/218 calls 6A-6D "new".
  This is read from the definitions the amendment replaces, not stated in a source in terms.
- **A correction this read makes.** `company/regulatory/gsop.py` gave the erroneous-transfer payment a
  20-working-day window. Twenty is the 6A agreement window; the payment is due within **10** working days
  of the failure, as for every standard. "Automatic £30 for an ET from 1 May 2020" (§4) is 6ZB, the
  gaining supplier's own failure, and is consistent with this table.

**What the supplier can observe for each, which is what the code may key on.** 6ZA: the day it received
sufficient information and the contract day (its own records), and the day the registration service
confirms it became responsible. 6ZB and 6C: the day the two suppliers agree a transfer had no valid
contract, which is an inter-supplier record both hold. None of these needs world truth.

**Not established, named rather than picked.** (a) Whether a switch whose information arrived before
1 April 2024 but completes after it is judged on 15 or 5 days; S.I. 2024/108's transitional text was not
read. The code keys the regime to the day the clock starts and says so. (b) How often a GB switch misses
15 or 5 working days, 2016-2025: no published count was found (named gap 3 above is the same hole). (c)
The erroneous-transfer rate after CSS (named gap 2). The world can therefore draw a 6ZA breach and a
post-CSS erroneous transfer only once these are found; until then it carries `None` with this reason.

**What the world and the company do with this, from 21 Nov 2026.** `simulation/gain_registration.py`
draws, per won switch before CSS go-live (18 Jul 2022), an erroneous transfer at 0.5% (§4, Ofgem 2016;
stated range 0.5-1%), agreed by the two suppliers on the last day reg 6A allows (20 working days from
the switch, a stated belief: the customer notices at the switch). After go-live none is drawn (gap (c)).
No registration delay is drawn (gap (b)): every switch completes on its supply start, so 6ZA is judged
on every gain and cannot be failed. `company/interfaces/switching_gsop.py` applies `gsop.py` to those
records and pays each payment by account credit on the 10th working day. Both gaps UNDERSTATE what the
book pays; ETs before 1 May 2020 owe nothing (6ZB not in force). Not yet built: the credit posted to
the account's ledger, and the erroneously transferred household returned to its old supplier.
