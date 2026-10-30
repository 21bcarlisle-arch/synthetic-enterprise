# Unbilled energy: what suppliers do about it, what customers meet, and which pain points to measure

**Knowledge:** unbilled-energy-and-revenue-assurance

**Asked by** the director, chat 30 Oct 2026 07:30 GMT ("Create knowledge in this area and in unbilled.
What do different people do. What are the pros and cons. What do customers experience. What pain points
should we measure."). The advisor's evidence pack is
`docs/staging/advisor/done/DIRECTOR_EVIDENCE_UNBILLED_ENERGY_ESTIMATES_CATCH_UP_AND_BACK_BILLING_2026-10-30.md`;
every URL is in it beside its claim. The mechanics of unbilled energy (its kinds, settlement, the
accrual) are already in `unbilled_energy_and_revenue_assurance.md` and the law in
`back_billing_and_liability.md`. This page adds what those two lack: **how named suppliers have handled
held bills and exception queues, with the pros and cons, what the customer meets, and the pain points
defined well enough to measure.**

**How figures are marked.** **[H]** read this session in Ofgem's *Domestic billing performance
assessment* (July 2026), text extracted locally from the PDF, not through a summariser. **[P]** from the
advisor pack with its URL, not re-read here. **[A]** reasoning no source states. **GAP** searched for
and not found.

---

## 1. Where the industry stands (Ofgem, 2024 data, seven largest suppliers) [H]

- **81%** of bills based on an actual read at first issue, **89%** after reconciliation.
- **11 million bills (3%) issued late**, of which 3.5 million were between three and twelve months
  late, "concentrated among a smaller cohort of suppliers".
- Back-billing: charges written off for **almost 1 million customers, over £172m, just under £200
  each**. Average resolution time ranges from **about 2 to almost 10 months** by supplier.
- Back-billing is **about 5%** of Energy Ombudsman referrals; billing and meter reading are about 30%
  of supplier complaints and 55% of Ombudsman cases.
- Some suppliers record their use of back-billing *exceptions* weakly.
- Good practice named: proactive monitoring, unbilled-account alerts, account "health flags", and trials
  of booked read appointments instead of unannounced visits.

Set against the rule's own forecast [P]: in 2017 Ofgem expected SLC 21BA write-offs of £0.8m-£2.3m a
year. The 2024 figure is about 75 times the top of that range (172 / 2.3).

---

## 2. Why energy goes unbilled (named causes, all [P])

Estimates that drift until a read forces a catch-up; missing reads (just over 7% of consumers went a
year without an accurate bill in H1 2017); smart meters in dumb mode (about 8.3% in September 2025;
49% of people bringing an estimated-bill problem to Citizens Advice had a smart meter); reads received
and not used, and opening reads never loaded; meter exchanges; system migrations; crossed meters and
wrong MPANs; a wrong tariff loaded; prepayment debt not applied; unregistered or deemed occupiers; and
late final bills on loss. No GB rate was found for crossed meters or for lost exchange reads: GAP.

---

## 3. What different suppliers have done about held bills and exception queues

| Approach | Named case [P] | For | Against |
|---|---|---|---|
| Big-bang migration, then work the backlog by hand | npower SAP, 2011-13: 859k accounts late at peak; complaints 36k to 133k a month; £26m redress | One platform at the end | Queue outgrows staff; complaints closed unresolved; wrongful back bills |
| IT rollout without a contingency plan | ScottishPower 2013-15: 300k+ late final bills; a 12-day sales stop; £18m | Recoverable once the backlog is the focus (late bills fell 75%) | The regulator's sales stop is a direct revenue lever |
| Surge staffing | British Gas Business 2014: up to 350 specialists; £9.5m | Fast relief | Expensive; treats the symptom |
| Abandon the platform change | SSE FY2016/17: impairment, retail profit down 29% | Avoids migration harm | Sunk cost; the old system's exception limits remain |
| An unmonitored held-bill class | Octopus prepayment final bills 2014-23 (34k, about £1.5m); E.ON Next 2021-23 (about 250k, £14.5m, about £144 each, about 150k debts written off) | Each record is cheap to hold | It piles up silently into one mass redress event |
| Proactive monitoring, alerts, health flags | Named as good practice by Ofgem [H], suppliers unnamed | Catches an exception before it ages past 12 months | Investment in data and governance up front |
| Automatic 12-month write-off on known risk events | The old Energy UK code (meter exchange, smart install, migration) | Consistent outcomes; fewer escalations | Certain loss of older revenue |

**The pattern [A]:** every penalty case is a queue that nobody measured by *age*. The defect is not that
a bill was held, but that the held class had no clock on it. That is the property a supplier control
should key to: the age of the oldest unbilled energy, by class, against the 12-month line.

---

## 4. What the customer meets [P]

- **Unexpected high bill:** 27% had one in the last three months (July 2024), down from 33% in 2023.
- **Bill accuracy:** 77% satisfied, 9% dissatisfied, and 30% of the dissatisfied blame wrong estimates.
- **Catch-up at Citizens Advice:** 24% of its billing cases are a shock or catch-up bill; the average
  back bill it saw was £2,525 in 2023-24; 34% of billing clients also need debt help; 67% had a
  disability or long-term condition.
- **Contacts:** giving a meter reading is 19% of contacts and querying a bill another 19%.
- **Complaints never made:** 42% of those with a reason to complain did not.
- **At the Ombudsman:** back-billing complaints are upheld about 80% of the time; suppliers signpost the
  Ombudsman in only 48% of eligible cases.
- **Churn:** 52% of complainants had switched or planned to (2016). No source gives churn caused by a
  back bill specifically: GAP. No figure for DD cancellation after a catch-up: GAP.
- **Resilience:** 32% of adults could not meet an unexpected £300 bill without cutting essentials
  (2017).

---

## 5. The pain points, defined before they are measured

Each is one experience for one population. Where the pack's rows mixed two (a DD change and a bill
both called "bill shock"), they are split here, because that mix cost this project months once already.

| Pain point | What exactly is counted | Population | Evidence of reaction | World today (audit) |
|---|---|---|---|---|
| Run of estimates | Consecutive bills with read type E on one meter, and months since the last actual read | Credit meters | 30% of those unhappy with accuracy blame estimates [P] | **No reaction**: estimates are produced, nothing reads the run's length |
| Catch-up bill | One bill whose energy charge exceeds what the DD covers because an actual read follows estimates; size = catch-up £ / monthly DD | DD payers whose estimates ran low | 24% of Citizens Advice billing cases [P]; reaction size GAP | **Calls only** (`simulation/contact_propensity.py`) |
| Back bill over 12 months | Days of energy charged beyond 12 months before the charge recovery action | All payment methods, prepayment included | Upheld about 80% at the Ombudsman [P] | The supplier's own cap is graded (`INV_BACK_BILLING_12M`); no customer reaction |
| Late or held bill | Days since the last bill, by held class; separately, days from loss to final bill | Live accounts; separately, leavers | npower complaints rose about 3.7 times [P]; 3% of bills a month or more late [H] | **No reaction** |
| DD rise after a catch-up | % change of the DD at the review that follows a catch-up | DD payers | 62% average rise in 2022; 8% over 100% [P] | Departure on; cancel, fail, complain **built and shipped at 0** (`simulation/dd_shock_response.py`) |
| Non-communicating smart meter | Days in dumb mode on a meter sold as smart | Smart customers | 49% of estimated-bill clients had one [P] | GAP: no dumb-mode state found in the audit |
| Unaffordable catch-up plan | Instalment / income; failed plans | Customers in catch-up debt | 66k failed electricity plans in Q3 2024 [P] | Partly, through payment-stress tiers |
| Complaint unresolved or unsignposted | Complaint age; 8-week breach | Complainants | 44% dissatisfied with handling; 27% give up [P] | A roll per renewal term only; `complaint_generation.py` has no caller |

## 6. The supplier levers, and what each needs graded

From the pack's thirteen, the ones our supplier could run first, given what exists:

1. **Exception-queue order**: oldest first, highest value first, or nearest the 12-month line first;
   with or without a fallback estimated bill (npower's lesson). Graded on £ written off under SLC 21BA,
   days to clear, and the age of the oldest held energy. **This one needs no world reaction**: the
   write-off is the supplier's own cost, so it can be graded today.
2. **Unbilled-account alerts and health flags**, keyed to age against 12 months. Same grading.
3. **Read chasing** by months since the last actual read. Needs the world's read-submission response to
   chasing, and a fatigue term: GAP.
4. **Proactive catch-up notice and smoothing** over 12 months or more, set on ability to pay
   (SLC 27.8A). Needs the world to react to a catch-up beyond a call.
5. **Automatic write-off on risk events.** Needs the world to escalate a wrongful back bill.

The SIM side is filed as `unbilled-energy-pain-points-react` in `docs/direction/priority_order.yaml`
`customer_outcomes_candidates`, drawn after the correctness exit test. Under K2 and canon F11, each
unsourced reaction strength (cancellation after a catch-up, churn after a back bill) goes in as a
stated belief with a range, and a lever counts as better only if it wins across the range.

## 7. Policy that may move

The back-billing window is a candidate to tighten: Citizens Advice has asked for 6 months for smart
customers since 2017 and repeated it in 2026; the ESNZ Committee is considering 6 months with automatic
compensation; Ofgem plans to review SLC 21BA. [P] Our cap is a dated rule; a future change belongs in
the curriculum, not the baseline, because the company's 2016-2025 record is what happened.

## 8. A correction carried from the pack

The read duty is annual (SLC 21B, reasonable steps); the two-yearly duty was an *inspection* duty,
repealed 1 April 2016. The invariant library already holds this (`INV_READ_DUTY_ANNUAL`). Nothing to
correct.

## 9. The pack's [unverified] items, checked against their primaries (30 Oct 2026)

**VERIFIED**, **REFUTED**, **PARTLY** (with the part that holds named), or **GAP** (searched, not
established). "Not fetched" means a primary exists but could not be read this pass, which is not a GAP.

| Pack line | Claim | Verdict | Primary, and what it says |
|---|---|---|---|
| 53 | How many back bills come from reads lost at a meter exchange | **GAP** | Elexon's metering trading-operations data gives MPAN counts only. Its "Erroneous Large EACs and AAs" page was not fetched |
| 60 | How often crossed meters occur | **GAP** | No Ofgem or Elexon count found. Supplier guidance pages carry none |
| 66 | Whether a silent occupier is "manifestly unreasonable" (SLC 21BA) | **PARTLY**: not reporting estimated bills is **not** manifestly unreasonable; an occupier who never registered stays **GAP** | Ofgem statutory consultation (Nov 2017) ¶2.16. Written up beside rows B2 and B5 of `back_billing_and_liability.md` |
| 77 | Settlement run timetable | **VERIFIED**: initial run (SSF) 1 month, R1 2, R2 5, R3 7, RF 14, DF 28 months | Elexon glossary, *2nd Reconciliation* |
| 77 | EAC/AA mechanics | **PARTLY**: definitions verified ("An estimated rate of consumption, nominally expressed in kWh/Year"; AA is "the rate of consumption … between two meter readings"); spreading by profile and "AA updates EAC" not stated on the pages read (BSCP504 not fetched) | Elexon glossary, *Estimated Annual Consumption* and *Annualised Advance* |
| 211 | Which billing platform suppliers run | **PARTLY**: E.ON Next runs on Kraken, VERIFIED ("exclusively built on Kraken Technologies' industry-leading platform"; Octopus press release on the npower migration). **OVO runs on Kaluza, not Kraken** (trade report of OVO's SSE migration "onto the Kaluza platform") | octopus.energy/press; news.energyjobline.com |
| 219 | IFRS 15: revenue as the obligation is satisfied; variable consideration constrained | **VERIFIED** ("recognise revenue when a performance obligation is satisfied"; "highly probable that a significant reversal … will not occur", quoted in an IFRS Foundation staff paper, not ¶56 itself). That unbilled energy is booked as accrued income is supplier practice, not IFRS text | ifrs.org |
| 230 | Accrued (unbilled) income at four suppliers | **PARTLY**: Octopus Energy Group's *contract assets* were **£996.5m** at 30 Apr 2024 and **£955.8m** at 30 Apr 2025. These "include accrued income and the provision for expected credit losses" and "arise from unbilled revenue", so they are an upper reading, not accrued income alone. OVO and E.ON UK: not fetched. SSE retail: **GAP** (sold to OVO in 2020) | Octopus Energy Group FY25 annual report, trade and other receivables note |
| 257 | Whether UNC 0398 was implemented | **VERIFIED**: directed 1 Mar 2013, effective 1 Apr 2014. Superseded in direction by **UNC 0896** (approved 22 Aug 2025: 2-3 years). The pack's "proposed" is the wrong tense | Ofgem 395-398 decision; Ofgem 0896 decision page |
| 338 | Churn caused specifically by back bills | **GAP** | Two searches, none found |
| 340 | DD cancellations after a catch-up bill | **GAP** | Two searches, none found |

**Corrections from the checks:** the pack's platform line implies OVO is on Kraken. It is on Kaluza.
Nothing in §1-§8 moves.

The pain points' ranges have one home each, on the site pages (FM, UB and BB rows, b587ead30e).
