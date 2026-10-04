# C31: time as a currency. DISCOVER/FRAME passes 1 and 2

**Atom:** `C31_time_is_the_currency_that_does_not_exist` · lane `C_customer_ops` · epoch 4 ·
`level_current: 0` · `level_target: 3` · `loop_stage: idle` · depends on
`A47_the_score_has_no_household_side`, `PB4_engagement_separated_from_elasticity`.

**This pass is DISCOVER/FRAME only. It adds no BUILD code and the level stays at 0.** It is the first pass on
this atom. The supervisor log shows the atom drawn and deprioritised about 1,900 times with nothing written
against it (`docs/observability/supervisor-log.md`, 2026-09-24).

---

## 1. What the thing is, before anything is measured

"Household time" here means **the minutes of a household's attention that its energy supply
consumes**. That is not one experience. It splits into four, and each has a different population, trigger
and remedy. They must be measured separately, as CLAUDE.md's bill-shock rule requires:

| Class | Who meets it | Trigger | Who controls the minutes |
|---|---|---|---|
| **T1 shopping**: searching and switching | the engaged minority, at a fix end or a price event | the household's own choice | mostly the market (PCWs, switch speed), partly us (quote clarity) |
| **T2 servicing**: contacting the supplier, waiting, being handled | anyone with a query, a bill they don't understand, or a DD change | a supplier event or a household question | **us**: queue length, first-contact resolution |
| **T3 recovery**: a complaint, a delayed or erroneous switch, a late final bill or refund | the households a process failed | a supplier or industry failure | **us**, and the regulator prices it (§2.3) |
| **T4 routine admin**: meter reads, checking bills, managing payment | everyone, all the time | how the account is set up | **us**: smart reads, DD sizing, bill legibility |

**Time SAVED** is a difference in minutes, per class, between this household with us and the same
household in the counterfactual. As with money (`THE_MODEL_ON_A_PAGE.md` §2), the counterfactual is
the hard half. **The unit is minutes. Do not convert to £** until the director rules otherwise (§5 Q1).
Three currencies means three units, and folding time into money removes the currency the mission names.

## 2. What the published record establishes (fetched and read this pass)

### 2.1 Hassle is real and widespread, but it is published as a perception, not as minutes
- **Ofgem Consumer Engagement Survey 2017**: **46%** agree "switching is a hassle that I've not got
  time for"; **41%** "I worry that if I switch things will go wrong"; **27%** "switching energy
  suppliers takes too long". The source is the Ofgem GSOP switching-compensation consultation, 12 June 2018, exec summary
  and footnotes 3–4. I read the text directly from the PDF, not from a summary.
- **CMA Energy Market Investigation, final report, 24 June 2016**: it found the *perceived* complexity
  and burden of switching worse than the reality, and found that PCWs significantly reduce search and
  switching costs. Low-income and less-educated households are less likely to use PCWs. That is a
  distributional fact. The households with the highest search cost are the ones it falls on.

**What this does NOT establish:** how many minutes a switch actually takes, or how much perceived
hassle converts into inaction. Neither source publishes a minute figure for T1.

### 2.2 Call waiting time IS published as minutes, per supplier per quarter (T2)
- **Citizens Advice supplier ratings**: the average wait to speak to an energy supplier was **224 s**
  (Jan–Mar 2021), **340 s** (Oct–Dec 2021) and **391 s** (Jan–Mar 2022), and one supplier averaged
  **over 16 minutes**. Source: Citizens Advice press release "Worst customer service on record", 2022.
  I read the figures directly from the page.
- `docs/market_research/company_customer_comms.md:103` already holds "~7 min (2022) → ~2 min
  (mid-2024)" against the Consumer Standards (Dec 2023). I did not re-verify it this pass.

T2 is the only class with a published, supplier-attributable minute series in the 2016–2025
window. It is therefore the natural first instrument.

### 2.3 The regulator monetises T3 per event, not per hour
- **Ofgem Guaranteed Standards of Performance, switching compensation (consultation 2018)** sets
  **£30** for a delayed switch, an erroneous switch, a final bill not issued within six weeks, and a credit refund not made
  within two weeks of the final bill. Some legs carry **£15**. Ofgem's words (§1.11): *"Typically,
  Guaranteed Standards aim to reflect consumer inconvenience."* The incidence it cites for 2017 is that
  **~9%** of switches took over 21 days and **8%** of final bills were not sent within six weeks.
- This is the one place where a GB authority puts money on a household's lost time. It is priced
  **per failure event** and is not derived from minutes × a rate. It is also a **transfer**: £30 paid by
  us to the household. It is not value created, and the mission's first rule applies.

### 2.4 A general UK value of non-work time exists, and it is NOT established for this use
- DfT TAG Data Book table A1.3.1 values non-work travel time in £/hour. I did not fetch the figure this
  pass. Moving a travel-time valuation onto energy admin would be a modelling *choice*. It is not an
  established fact, and §5 Q1 says it should not be made.

## 3. What the code does today (re-measured this pass, not inherited)

- **No time-as-value symbol exists.** A grep of `company/ simulation/ saas/ sim/ tools/` for
  `time_saved|hours_saved|minutes_saved|household_minutes|hassle|value_of_time` returns only the
  `tools/generate_value_arms_data.py:9861` prose that states the absence. The canon's 2026-08-28
  observation still holds.
- **The nearest primitive is world-side friction, held in unsourced points and routed only to churn.**
  `simulation/resentment_ledger.py` scores friction events (e.g. `CALL_WAIT_LONG (>30min): +6`,
  `COMPLAINT_UNRESOLVED (>14d): +20`) into a resentment stock that triggers churn. **`CALL_WAIT_LONG` is
  declared and never emitted.** `run_phase2b.py` emits only `BILL_SHOCK`, `COMPLAINT_UNRESOLVED` and
  `COMPLAINT_RESOLVED_WELL`. The world has no contact queue, so no household ever waits.
  This ledger measures *feeling* in points, not *time* in minutes, and none of its point values cites a
  source. A time ledger must not be grafted onto it. The two are separate quantities, and resentment's
  points would be read as established.
- **Company-side time is the supplier's cost, not the household's.**
  `company/crm/contact_centre_metrics.py` computes agent average handle time.
  `company/crm/switching_cost_model.py` prices *our* staff time in £. Both are legitimate observables,
  and neither is time the household spent.

## 4. FRAME: levels and their falsifiers

**The wall decides the shape.** A household's minutes are a fact about the world: they are hidden, and
they sit beside the other household traits. The company may see only **its own service clocks**: its
queue wait, its complaint-to-resolution days, its switch completion dates, its final-bill and refund
lags. This mirrors money: the household side lives world-side, and our side is what a supplier records.

| Level | What is true | Falsifier |
|---|---|---|
| **L1** | A world-side **household minutes ledger**, keyed by class T1–T4 and by event, exists and is fed by events the world ALREADY emits (complaints opened/resolved, DD failures, switches, bills). **Each per-event minute cost is a declared `None` with a named reason unless §2 sources it.** Initially the ledger counts EVENTS, and minutes stay unknown. | A test that drives one complaint through the run finds no T3 event on that household. Or any per-event minute value is a bare number with no origin (`test_a_domain_constant_carries_its_origin`). |
| **L2** | T2 is real: the world has a contact queue whose wait is calibrated to the Citizens Advice series (§2.2), and `CALL_WAIT_LONG` is emitted from it rather than declared dead. The company sees its own wait as an observable through the seam. The household's minutes stay world-side. | The world's 2022 Q1 mean wait is outside the published band, or the company reads a household's minutes rather than its own queue. |
| **L3** | Time is the **third column of the two-sided score (A47)**, in minutes per class, beside money, and it is published per arm. A decision that saves minutes and costs money shows as a trade, not as a transfer. | An arm that adds queue capacity moves no published minute figure, or the minutes figure moves on an arm that changed nothing household-facing. |

**Cheapest first BUILD increment when the epoch opens:** L1 with every minute cost at `None`. It is a pure
event census, and it lights up T3, the class the regulator already prices. No new number is invented.

## 5. Open questions, each with a recommendation

- **Q1. Is time scored in its own unit, or converted to £ at a value of time?** *Recommendation: its
  own unit, minutes, per class, and never summed across classes.* The mission names three
  currencies, and a conversion makes one of them disappear into money. The GSOP £30 shows that even the
  regulator prices *events* rather than hours. This is canon intent, so it is the director's to rule. It
  does not block L1, which works in minutes either way.
- **Q2. Does T1 belong to us at all?** Most switching time is spent with the market. We save it only by
  making staying the right answer (no need to shop) or by making a move to us cheap in attention.
  *Recommendation:* defer T1 to C30 (advice reaching a household) and PB4 (engagement). T2–T4 are the
  classes this supplier controls.
- **Q3. Minutes per event for T1, T3 and T4.** No published source was found. *These go to the knowledge
  map as named gaps*, and the next DISCOVER pass should search Ofgem's 2018 qualitative
  research on unreliable switching (GSOP consultation, footnote 9) and the Citizens Advice/Ofgem complaints
  evidence for any hours-spent figure.

## 6. Not established this pass, stated so it is not read as done
- The CSS (faster-switching) go-live date and the switch duration before and after it. Not fetched.
  *Pass 2: the date is now established (§7.3). The measured durations still are not.*
- The DfT TAG non-work £/hour figure. Not fetched, and not recommended for use (Q1).
- Any published minutes-per-switch, minutes-per-complaint or minutes-per-meter-read figure. None found.
- The `~7 min → ~2 min` call-wait series in `company_customer_comms.md`. Inherited, not re-verified.
  *Pass 2: re-verified against the source series (§7.1). The peak median was 388 s (6.5 min, Q1 2022)
  and Q2 2024 was 106 s (1.8 min). The shape holds; "~7" rounds up.*

Sources: [Ofgem GSOP switching compensation consultation, 2018](https://www.ofgem.gov.uk/sites/default/files/docs/2018/06/policy_consultation_on_gsop_switching_compensation_for_publn_v2.pdf) ·
[CMA EMI final report summary, 2016](https://assets.publishing.service.gov.uk/media/576c23e4ed915d622c000087/Energy-final-report-summary.pdf) ·
[Citizens Advice, "Worst customer service on record", 2022](https://www.citizensadvice.org.uk/wales/about-us/media-centre/press-releases/worst-customer-service-on-record-from-energy-companies-says-citizens-advice/)

---

## 7. DISCOVER pass 2 (2026-10-04): answering Q3 and the §6 gaps from source

The level stays at 0 and there is no BUILD code. MATURITY_MAP L1 means "built in any form".

### 7.1 T2 has a full quarterly series, per supplier, Q4 2017 to Q2 2024 (the L2 calibration target)
Citizens Advice publishes its star-rating call-wait data as a CSV per supplier per quarter, under
"Historic Star Rating Data", chart 5. I downloaded it this pass (2,613 bytes, sha256 `064c0b84…5ad6dbe`).
The **median across suppliers** of each supplier's average wait, in seconds:

| | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| 2017 | | | | 121 |
| 2018 | 95 | 82 | 133 | 170 |
| 2019 | 170 | 146 | 123 | 154 |
| 2020 | 125 | 79 | 157 | 175 |
| 2021 | 200 | 150 | 278 | 283 |
| 2022 | **388** | 328 | 277 | 372 |
| 2023 | 245 | 138 | 231 | 200 |
| 2024 | 119 | 106 | – | – |

From Q3 2024 the chart's column is `-`. The CA press figures for 2025–26 (e.g. a median of 77 s, then
68 s, in 2026) come from a newer methodology that I did not reconcile with the series.
**Two things this statistic is NOT**, said before anyone differences it:
(a) It is a **median of supplier means**, not the mean household wait. The press release's 224 s for
Q1 2021 is a different statistic from this series' 200 s for the same quarter.
(b) The chart covers **current suppliers only**, so failed suppliers drop out. The 2021–22 peak is
therefore probably an UNDER-statement, because the suppliers that failed are absent. I have not tested this.
The per-supplier spread is wide (Q1 2022 runs from 30 s to 944 s), so an L2 queue should be calibrated
to a band, not to the median.

### 7.2 T3 is published as CONTACTS and ELAPSED DAYS, not minutes
Ofgem *Complaints handling survey 2014* (Ofgem report, 8 Aug 2014). It surveyed 2,744 telephone
interviews with people who complained in Dec 2013, base 2,457 domestic. I read it directly from the PDF:
- The **average domestic complainant contacted their supplier six times** about one complaint, and a
  micro business nine times. Nine in ten complaints were made by telephone.
- Elapsed time to resolution, domestic, base 1,326 resolved: same day 17%, ≤1 day 2%, ≤2 days 3%,
  3–7 days 12%, 8–14 days 10%, 15–28 days 15%, **>28 days 38%**, don't know 3%. That makes 53% over two weeks.
- 11% of domestic complainants said "I have given up". The jointly commissioned Ofgem/CA 2019 survey
  (n=3,300) put "gave up" at 27% (Energy Ombudsman, 12 Mar 2019).
- The 8-week deadlock rule (a complaint can go to the Ombudsman after eight weeks) is the regulatory
  clock on T3 elapsed time.

**This does not establish minutes per complaint.** "Six contacts × the §7.1 wait" is a *composition*.
It omits handle time and any non-phone contact, and it uses a 2013 cohort, outside the 2016–2025
window. It is not a published figure, and it must not enter code as one. The L1 ledger can count
contacts per complaint as events, and each contact's minutes stay `None`.

### 7.3 T1 (switching): the date is established, the minutes are not
CSS go-live was **18 July 2022** (Ofgem, formal designation of "CSS Go-Live"; REC Co, "green light
for go-live"). After it, a domestic switch is next-working-day unless the customer chooses a later
date. Before it, Ofgem's 2018 GSOP consultation (§2.3) gives the incidence: ~9% of switches took over
21 days. This changes **elapsed days**, not the household's minutes of effort, so it remains a T1/T3
event clock, not a time saving. The household minutes of a switch remain unpublished.

### 7.4 What pass 2 changes in the FRAME
- **L2's falsifier is now concrete:** the world's quarterly median wait must sit inside the §7.1 band
  for 2018–2024, with the 2021 Q3 to 2023 Q1 crisis rise present, before the company may read its own
  queue as an observable.
- **L1 gains one countable:** contacts per complaint. Six is published (2014, pre-window) and can be a
  bound for a test. It is not a constant. If a constant is ever written, it is pre-window and must say so.
- **Q3 is answered:** no published minutes-per-event figure exists for T1, T3 or T4 in the sources
  searched (Ofgem 2014 complaints survey, Ofgem 2018 GSOP consultation, CA star rating, Energy
  Ombudsman 2019). T2 is the only class published in time units. The gap stays named.

Pass 2 sources: [CA Historic Star Rating Data](https://www.citizensadvice.org.uk/policy/publications/historic-star-rating-data/) ·
[CA chart 5 call-wait CSV](https://docs.google.com/spreadsheets/d/e/2PACX-1vTmgaUkvHeN8ZU92hrnvr9FILte56_RU_z3v442AiY2Gaos52ZE-xmaWtpa9ahb0Lw9i8ZF-NWRcVIn/pubhtml) ·
[Ofgem Complaints handling survey 2014](https://www.ofgem.gov.uk/sites/default/files/docs/2014/09/ofgem_complaints_report_final_8_august_2014_0.pdf) ·
[Energy Ombudsman, 2019](https://www.energyombudsman.org/news/how-good-are-energy-suppliers-at-handling-complaints) ·
[Ofgem, CSS go-live designation](https://ofgem.gov.uk/decision/formal-designation-css-go-live) ·
[REC Co, go-live 18 July 2022](https://www.retailenergycode.co.uk/switching-programme-gives-green-light-for-go-live-on-18-july-2022/)
