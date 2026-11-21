# How GB households respond to bill shock: two families, three moments, by payment method, and the customer-voice coding scheme

**Knowledge:** how-households-behave-toward-a-supplier

**Written 2026-11-21** by the delivery seat for the director's steer of 21 Nov 07:15 and its 07:20
addendum
(`docs/staging/advisor/done/DIRECTOR_STEER_BILL_SHOCK_RESPONSES_EMERGE_FROM_HOUSEHOLD_BEHAVIOUR_AND_ARE_CHECKED_AGAINST_HISTORY_2026-11-21.md`),
and the 07:23 steer that makes the customer's own voice a standing source
(`..._THE_CUSTOMER_VOICE_IS_A_STANDING_KNOWLEDGE_SOURCE_TRAWLED_FOR_EVERY_THEME_2026-11-21.md`).
Commitment `bill-shock-responses-knowledge-page-with-the-customer-voice-coding-scheme`, due 4 Dec.

This page is the K8 step: it says what is known before anything is built. It does **not** repeat
four pages it builds on, and reads them as settled unless it says otherwise:

- `what_bill_shock_is.md`: what the event *is* per payment population (a change in the payment for
  the ~74% on a level DD; the bill itself for standard credit).
- `BILL_SHOCK_EVENT_TYPES_ANCHORS.md`: contract-end reversion and DD recalculation, sourced.
- `does_a_bill_shock_event_raise_the_odds_a_household_shops.md`: no published instrument measures
  switching after an event; the aggregate series cannot identify it.
- `satisfaction_drivers_and_the_three_bill_shocks.md`, and the 7 Nov evidence pack
  `docs/staging/advisor/done/DIRECTOR_EVIDENCE_WHAT_HOUSEHOLDS_DO_AFTER_A_PAIN_POINT_2026-11-07.md`
  (its rates and their grades P / S / A are cited by section, not copied).

## 0. The split that governs this page

The director's account is the practitioner hypothesis (K4). It is tested here against two kinds of
evidence, which answer different questions and must never be swapped:

| Question | Source kind | Why |
|---|---|---|
| **Which responses exist, and in what order they chain** (paths) | Coded customer accounts: Ombudsman case studies, Citizens Advice case studies, MSE reader accounts, review sites | Self-selected and skewed to the angry and the delighted (the U-shape `simulation/feedback_survey.py` already models). Good at *existence and order*; useless for *how often* |
| **How often** (rates) | Representative sources: Ofgem surveys (CIM, CES), Ofgem trials (EFTC, CMOC, collective switch), DESNZ QEP 2.7.1 switching, Ombudsman volumes | Sampled or census; each carries its own denominator |

A rate read off coded accounts is a defect on this page and on every page that reuses the scheme.

## 1. Two families of shock

### 1.1 Catch-up and correction

| Cause | What makes it | Established by |
|---|---|---|
| Stale estimates corrected | 19% of first-issue bills in 2024 not on actual reads, ~11% after reconciliation | Ofgem *Domestic Billing Performance Assessment* (Jul 2026), via 7 Nov pack §5.3 — P |
| Usage changed under a fixed DD | the DD was sized from past bills, not true use | `a_suppliers_annual_dd_review_is_sized_from_its_own_issued_bills_not_true_consumption_2026-10-13.md` |
| Supplier mistake | wrong opening read; account never created; wrong meter; meter exchange not recorded | coded accounts O1, O3, O4, O6 (§5) |

The back-billing rule bounds what can be recovered: 12 months where the supplier is at fault
(Ombudsman case O4: a multi-year gas demand cut to 12 months). Back-billing cases at the
Ombudsman: 3,216 (2025), 3,238 (2024); billing is 56% of disputes reviewed in 2025 (Energy
Ombudsman annual data 2025, read 21 Nov) — P.

### 1.2 Price shocks

| Cause | Mechanism | Established by |
|---|---|---|
| Default (SVT/cap) rise | Pre-2019 a supplier's own announcement; from Jan 2019 Ofgem's cap announcement, then each supplier's notice | `ofgem_cap_windows.md`, `cheapest_fix_against_the_default_tariff_gb_2016_2025.md` |
| End of fix | Roll onto the default unless the household acts; 49-day no-fee window; SLC 22A no auto-rollover onto a fix | `BILL_SHOCK_EVENT_TYPES_ANCHORS.md` §1; EFTC (7 Nov pack §2.3) |

**The three moments of an SVT rise** (the director's point, kept): the **announcement** (public,
dated, reaches a household through media and its own engagement), the **effective date** (the unit
rate changes; a household on a quarterly standard-credit bill sees it on the next bill), and the
**DD change** (the payment moves, at the supplier's next DD review, which is not standardised —
Ofgem's DD Market Compliance Review found "big differences between firms ... how frequently
payments are reassessed": `BILL_SHOCK_EVENT_TYPES_ANCHORS.md` §2). For a DD household the third
moment can lag the second by months; for a prepay household the second moment *is* the shock, at
the meter, the same day.

## 2. Responses by family and payment method — the paths

The director's response sets, set against what the coded accounts (§5) and the representative
sources show. "Exists" means at least one coded account shows it; the rate column cites a
representative source or says it has none.

### 2.1 Catch-up and correction

| Response | DD | Standard credit | Prepay | Exists? | Rate, from a representative source |
|---|---|---|---|---|---|
| Does not notice for a while | Typical: the bill is not the payment; the shock arrives as a DD re-level | Unlikely: the bill is the demand | Not applicable as a bill; a debt recovery rate on the meter | MSE accounts (§5) | **None published.** 46% of MSE respondents whose DD doubled did not challenge it (MSE 2022) is self-selected and is a *did-not-challenge*, not a *did-not-notice* |
| Notices and calls | Prompted by the DD-change letter | Prompted by the bill | Prompted at the meter | O1, O3, O6 | 42% with cause did not complain (Which? 2020) — S; contact-by-size bands in the 7 Nov pack §7 row 1 are **A** (analyst), not published |
| Refuses to pay / disputes | Cancels the DD | Withholds payment | — | O4 | **None published** for the share; the debt objection then blocks a switch (`why_households_switched_by_arrears_and_age_..._debt_objection_rule_2026-11-02.md`) |
| DD fails for lack of funds | Yes, on the Bacs rails | — | Self-disconnection is the analogue | MSE accounts (§5) | **None published** per event; standing DD failure rates live in `payment_behaviour_source` |
| Complains, escalates | via 8-week deadlock | same | same | O1, O3, O4, O6 | ~2–2.5% of complaints reach the Ombudsman (A, from Which? ~4m complaints and EO 80–93k cases); suppliers signpost in 48% of cases (EO 2025) — P |
| Switches | Hazard after the event | same | Blocked by debt | none in the Ombudsman sample | **None published** (`does_a_bill_shock_event_raise...` §3) |

**Handling moves the outcome — what the accounts show.** In every Ombudsman account the escalation
followed a *handling* failure, not the shock itself: the complaint logged and never answered (O1,
20+ calls), an apology without investigation (O3), the customer blamed (O4), the bill insisted
correct after a visit (O6). The remedy came from the Ombudsman, not the supplier. That is the path
the director names ("how the issue is handled then affects the likelihood to churn"), and it shows
the *escalate* branch exists and chains through handling. It does **not** show the *churn* branch:
no Ombudsman account records a switch, because a case there has, by selection, stayed to fight.
The churn-after-bad-handling link needs a different source (§6, gap G3).

### 2.2 Price shocks

| Response | Moment it fires | Rate, from a representative source |
|---|---|---|
| Lapse onto the default | End of fix | ~81% in EFTC control within 6 weeks (Ofgem 2019) — P |
| Take the supplier's next deal | End of fix | ~14% internal re-fix, rising to 23% with a better letter; external flat at 6% (EFTC) — P |
| Shop around and leave | End of fix | ~6% external in 6 weeks (EFTC) — P |
| Shop around and leave | SVT announcement / effective date | Single-supplier: Centrica's net-loss rate ~4× for 1–2 months around its 2018 5.5% rise — S/A (7 Nov pack §2.1). Whole market: see §3.2 — far smaller |
| Do nothing at an SVT rise | all three moments | 2.6% of 3-year+ SVT customers switched over ~3 months in the collective-switch control arm (Ofgem 2018) — P |
| Leave a fix mid-term | any | **None found** — gap G2 |

**The comparison offer gates all of it.** 2022 is the proof in the record: QEP 2.7.1 electricity
switching fell from 15.6% (2021) to 3.1% (2022) while every bill rose, because nothing beat the
cap (`does_a_bill_shock_event_raise...` §3.4; recomputed here, §3.1). So the world's response to a
price shock must run through the household's visible best alternative; a shock with nothing better
on offer moves rationing, arrears and complaint, not switching (7 Nov pack §2.4).

## 3. Validation targets, named before any run

These are what the emergent behaviour is checked against (steer item 5). A miss is a finding about
the behaviour, never a dial to turn. Tolerances are set from the spread in the record itself, so
none is a choice about how close the company's world "should" look.

All monthly figures below are recomputed on 21 Nov from DESNZ QEP Table 2.7.1 (sheet
"2.7.1 (Monthly)", cached at `sim/cache/desnz_switching/table_271__2_.xlsx`), **electricity**
meter-point transfers over the year's mean electricity customer count. They count meter transfers
between supplier groups, not households, and exclude internal tariff moves
(`gb_domestic_switching_by_calendar_month.md` §2; `gb_switching_rate_denominators.md`).

### 3.1 T1 — annual external switching, by year

| Year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| Electricity transfers / customers | 15.8% | 18.2% | 19.1% | 20.8% | 20.2% | 15.6% | 3.1% | 6.3% | 9.0% | 10.4% |

**Tolerance:** the world's annual rate within ±2.5 percentage points of each year in 2016–2020 and
2023–2025 (the largest year-on-year move in 2016–2020 is 2.4pp, 2016→17, so a miss beyond 2.5pp is
larger than any move the calm record made); and for 2022 **below 5%**, the ordinal test that
matters: switching collapses when nothing beats the cap. 2021 is graded on its two halves (§3.2),
because its annual figure averages a normal half and a collapse.

### 3.2 T2 — the monthly shape, and where announcement spikes show

Seasonal index (median ratio of the month to its year's monthly mean, 2016–2019):

| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.72 | 0.94 | 1.19 | 1.05 | 0.96 | 0.90 | 0.90 | 0.99 | 1.13 | 1.25 | 1.03 | 0.95 |

Each month's level against its own year and its season (1.00 = expected), selected months:

| Month | Ratio | What happened (dated in the cited page) |
|---|---|---|
| Sep 2017 | 1.07 | British Gas electricity +12.5% from mid-Sep 2017 (`svt_rates_active_passive_2016_2025.md` §1b) |
| May–Jul 2018 | 1.08, 1.12, 1.09 | British Gas +5.5% in 2018 (7 Nov pack §2.1; effective date carried there as unverified) |
| Apr 2019 | **1.23** | Cap up £1,137 → £1,254 on 1 Apr 2019, the largest rise of the cap's first two years (`cheapest_fix_against_the_default_tariff_gb_2016_2025.md`), announced Feb 2019 (Feb ratio 0.94) |
| Oct 2019 | 0.85 | Cap down to £1,179 |
| Nov–Dec 2021 | 0.26, 0.37 | Fixes withdrawn, supplier failures; collapse begins |

**What this says, plainly.** In the whole-market series an SVT rise is a **small** excess over the
season: 7–23%, not the 4× a single supplier's net-loss rate showed. Both are true at once and the
world must reproduce both: one supplier's book can lose four times its usual rate while the market
moves by a tenth, because most of that supplier's leavers are another supplier's gainers in a
month that was already seasonally busy. And the largest excess in 2016–2019 fell in the **effective**
month of the April 2019 cap rise, not its announcement month. That one observation is not enough
to say which moment drives response, and the media-coverage input that would separate them does
not yet exist (G1).

**Targets.**
- **T2a, seasonal shape.** The world's monthly index, 2016–2019, has its trough in Jan and its peaks
  in Mar and Oct; each month within ±0.20 of the index above. 0.20 is the largest gap the record
  itself shows in 2016–2019 outside the event months above (Dec 2016 at 1.20; Mar 2018 at 0.82;
  Aug–Sep 2016 at 0.84–0.85), so it is the record's own month-to-month noise, not a choice.
- **T2b, whole-market spike size.** In Apr 2019 the world's ratio sits in **1.10–1.35**; in Sep 2017
  and May–Jul 2018 in **0.95–1.25**. A world whose market-wide ratio at a rise exceeds 1.5 is
  reacting far harder than anything in the record. **Note what T2a's band does to T2b:** the largest
  event month (1.23) sits only just outside the record's own noise (±0.20), and the 2017–18 rises sit
  inside it. In the whole-market series an announcement spike is at the edge of detectability, which
  is the director's "smaller ones are hard to see" in numbers. T2b is therefore a ceiling test (the
  world must not over-react) far more than a floor test, and T2c carries the floor.
- **T2c, single-supplier spike size.** A large incumbent's monthly net-loss rate in the 1–2 months
  around a ~5% default rise runs at **2–6×** its own prior four-month average (the Centrica 2018
  reading, ~4×, net of gains, period boundaries approximate — S/A, so the band is wide).
- **T2d, the 2022 collapse.** From Nov 2021 to the end of 2022 the world's monthly rate stays below
  0.35% of customers (the record: 0.22–0.30% through 2022).

### 3.3 T3 — the end-of-fix window

Within 6 weeks of a 1-year fix ending, with an ordinary end-of-term letter: **~19% act (±4pp),
~14% internally, ~6% externally** (EFTC control arm, n=9,776). Offline-only account holders at about
half the online-only rate (12% against 23%). Source P (internal/external split read from a chart, so the parts do not sum exactly); the
±4pp is about half the 9pp a better letter moved the internal share in the same trial.

### 3.4 T4 — mid-term leaving by fixed customers

**No published rate was found.** The target is therefore ordinal, and named before any run:
- the world's monthly external leaving rate among households mid-way through a fix without an exit
  fee is **below** the monthly rate among its SVT households in the same month, in every calm year
  (2016–2020, 2024–2025); and
- it rises materially only where (a) the gap to the best visible fix is large, or (b) the supplier
  itself offers a lower-priced deal (the director's exception, which is internal, not external).
How far below is G2, not a number to pick.

## 4. The customer-voice coding scheme

One scheme for every theme (the 07:23 steer). Each coded account is one row; a field the account
does not state is coded `not_stated`, never inferred. Text is a ≤25-word paraphrase; no names,
account numbers, locations or verbatim identifying phrases are kept (W11).

| Field | Codes |
|---|---|
| `source` | `ombudsman_case`, `citizens_advice_case`, `mse_reader`, `review_site`, `forum`, `other_published` |
| `url`, `year` | where read; year of the events (or of publication, flagged) |
| `theme` (multi-valued, §5.3 item 2) | the 07:23 theme list: `billing_error_catch_up`, `estimates_and_reads`, `dd_change`, `price_rise_svt`, `end_of_fix`, `switching_onboarding`, `smart_meter`, `debt_collections_prepay`, `home_move`, `final_bill_refund`, `supplier_failure_solr`, `service_access`, `vulnerability`, `green_ev` (open list: evidence may add) |
| `trigger` | `catch_up_estimates`, `catch_up_usage_change`, `supplier_mistake`, `svt_rise`, `end_of_fix`, `dd_increase`, `other:<short>` |
| `moment` (price shocks) | `announcement`, `effective_date`, `dd_change`, `not_applicable` |
| `payment_method` | `dd_fixed`, `dd_variable`, `standard_credit`, `prepay`, `payment_plan`, `not_stated` |
| `meter` | `credit_traditional`, `smart`, `prepay_key_card`, `smart_prepay`, `not_stated` |
| `circumstance` | any of `vulnerable`, `debt`, `home_move`, `recent_switch`, `low_income`, `none_stated` |
| `first_response` | `did_not_notice`, `ignored`, `refused_to_pay`, `dd_failed`, `dd_cancelled`, `called`, `complained`, `shopped_around`, `switched`, `cut_usage`, `agreed_higher_payment` |
| `chain` | the ordered responses after the first, e.g. `called>complained>deadlock>ombudsman`; escalation routes `ombudsman`, `ehu`, `citizens_advice` |
| `supplier_handling` | `resolved_first_contact`, `resolved_after_chase`, `apologised_no_fix`, `no_reply`, `blamed_customer`, `insisted_correct`, `offered_plan`, `offered_better_deal`, `promise_broken`, `passed_to_debt_collection`, `offered_choice_under_pressure`, `not_stated` |
| `outcome` | `stayed_satisfied`, `stayed_resentful`, `switched`, `escalated_won`, `escalated_lost`, `in_debt`, `not_stated` |
| `time_effort` | stated duration and contacts, e.g. `weeks:16;contacts:20+` (M3 time need, household minutes where stated) |
| `tone` | one of `calm`, `confused`, `frustrated`, `distrustful`, `shocked`, `distressed`, `resigned`, `relieved` (M3 certainty and control needs) |

The `chain` field is what the paths in §2 are read from. The `supplier_handling` × `outcome` cross is
what the supplier lane later learns from (steer addendum item 4).

## 5. The scheme proven on a first sample

**Sample:** every residential case study the Energy Ombudsman publishes that concerns billing (6 of
its 10; read 21 Nov at `energyombudsman.org/case-studies`), and published Citizens Advice and
MoneySavingExpert accounts (§5.2). **Trustpilot was not read**: its terms prohibit automated
access, and a hand sample is the 23 Nov advisor pass's to offer, under the site's terms.

### 5.1 Energy Ombudsman case studies

| id | theme / trigger | pay / meter | circumstance | first response > chain | supplier handling | outcome | time / effort | tone |
|---|---|---|---|---|---|---|---|---|
| O1 | billing_error / supplier_mistake (wrong opening read, first bill >£2,200) | not_stated / not_stated | recent_switch | called > complained > ombudsman | no_reply (complaint logged, never investigated) | escalated_won (rebilled to £93, written off, £100 goodwill) | months:3; contacts:20+ calls and emails | frustrated |
| O2 | smart_meter / catch_up_estimates (meter not sending reads) | not_stated / smart | none_stated | not_stated (explainer, not a decided case) | not_stated | not_stated | not_stated | resigned |
| O3 | estimates_and_reads / supplier_mistake (exchange not recorded, 6 months high estimates) | not_stated / credit_traditional | none_stated | complained > ombudsman | apologised_no_fix (blamed query volumes) | escalated_won (rebill, apology, award) | months:6 | distrustful |
| O4 | billing_error_catch_up / supplier_mistake (gas account never created; >£2,000 demand) | not_stated (regular monthly, method unnamed) / not_stated | home_move | refused_to_pay > complained > ombudsman | blamed_customer (demanded full sum) | escalated_won (limited to 12 months; £1,550 removed) | years:6 unbilled | shocked |
| O5 | debt_collections_prepay / other:income_fall | payment_plan / not_stated | debt | called > complained > ombudsman | insisted_correct (refused to revisit plan) | escalated_won (plan reassessed, award) | not_stated | distressed |
| O6 | billing_error / supplier_mistake (billed on a neighbour's meter) | payment_plan / credit_traditional (all-electric) | vulnerable, home_move | called > cut_usage > complained > ombudsman | insisted_correct (visit, said billing right) | escalated_won (refund, significant award) | years:2+ | distressed |

### 5.2 Citizens Advice and MoneySavingExpert accounts

Citizens Advice, *Footing the bill: how the energy bill protection gap is putting strain on
households* (29 Nov 2024; report PDF read 21 Nov), case boxes C1–C9. The report's own names are
pseudonyms and are **not** kept. MoneySavingExpert: the 2022 DD-survey article quotes no reader; the
one reader account found is M1 (MSE guide *lower energy direct debits*, undated). "EHU" is the
Extra Help Unit, the Citizens Advice escalation route for vulnerable consumers, which sits beside
the Ombudsman as an escalation code.

| id | theme / trigger | pay / meter | circumstance | first response > chain | supplier handling | outcome | time / effort | tone |
|---|---|---|---|---|---|---|---|---|
| C1 | estimates_and_reads, debt / catch_up_estimates (reads given, estimates continue) | not_stated / not_stated | debt | called > called | no_reply (no accurate bill sent) | in_debt, not_stated | not_stated | frustrated |
| C2 | supplier_failure_solr, estimates_and_reads / catch_up_estimates (£500 estimate after SoLR transfer) | dd_variable / not_stated | recent_switch (SoLR) | called > agreed_higher_payment > second estimate (£400) | promise_broken (said DD would not be taken; took it), blamed_customer | stayed_resentful | not_stated | distressed |
| C3 | smart_meter, debt_collections / catch_up_estimates (meter silent 2 years) | not_stated / smart | vulnerable, low_income | called (could not get through) > refused_to_pay | no_reply; passed_to_debt_collection (>£2,700) | in_debt | years:2 | distressed |
| C4 | smart_meter, billing_error_catch_up / catch_up_estimates (silent after switch; £1,500 catch-up for a year) | dd_fixed / smart | vulnerable, recent_switch | did_not_notice > catch-up on a manual read | not_stated | not_stated | months:12 unbilled | shocked |
| C5 | dd_change, billing_error_catch_up / supplier_mistake (DD set far below use; £7,000 debt; DD £50 → £350) | dd_fixed / not_stated | vulnerable | did_not_notice > ehu | not_stated | escalated_won (part written off under back-billing; ~£1,500 still owed) | years:1+ | shocked |
| C6 | dd_change / supplier_mistake (usage miscalculated ten-fold; DD raised; £500 taken) | dd_variable / not_stated | vulnerable | called (readings rejected) > citizens_advice > ehu | insisted_correct | escalated_won (rebilled on actual reads, bill fell) | not_stated | distressed |
| C7 | billing_error_catch_up / not_stated (£7,000 unexpected bill) | not_stated / credit_traditional → smart | vulnerable, low_income | called > agreed smart meter > ehu | offered_choice_under_pressure (pay or take a smart meter) | escalated_won (detail not given) | not_stated | confused |
| C8 | dd_change / dd_increase (DD raised ~7×, "usage increased") | dd_variable / not_stated | vulnerable (deaf) | not_stated | not_stated | not_stated | not_stated | confused |
| C9 | estimates_and_reads, service_access / supplier_mistake (billing-platform migration; bills unrelated to reads) | not_stated / credit_traditional | none_stated | called > called (70+) | no_reply (promised call-backs not made) | stayed_resentful | contacts:70+ | distressed |
| M1 | dd_change / other:overpaying (DD calculator showed ~£3.8k credit) | dd_fixed / not_stated | none_stated | shopped_around (calculator) > submitted reads > reset DD | resolved_first_contact | stayed_satisfied (refund) | days:1 | relieved |

### 5.3 What proving it showed

Sixteen accounts, coded on 21 Nov. Five things the coding showed, each of which changed or
confirmed the scheme:

1. **Every account was codable, and `not_stated` carries real weight.** Payment method is stated in
   8 of 16, meter type in 7 of 16, supplier handling in 12 of 16. A scheme that forced a value would
   have invented the most important field for the steer's "varies by payment method". The rule
   stands: `not_stated` is a code, never a gap to fill.
2. **`theme` must be multi-valued.** Six of 16 sit in two themes at once (a silent smart meter
   *causing* a catch-up bill: C3, C4; a SoLR transfer *causing* an estimate: C2). One account
   feeding two pages is the 07:23 steer's "coded once, read many ways", and the scheme now allows
   it. A meter or read failure (silent smart meter, wrong or unrecorded meter, reads given and
   ignored) is the root cause in 7 of 16 (O1, O2, O3, O6, C1, C3, C4): existence, not frequency.
3. **Codes the sample added.** `first_response`: `agreed_higher_payment` (C2, and implicitly C5).
   `supplier_handling`: `promise_broken` (C2), `passed_to_debt_collection` (C3),
   `offered_choice_under_pressure` (C7). Escalation route: `ehu` and `citizens_advice` beside
   `ombudsman` in `chain`. `outcome`: `stayed_resentful` was needed for C2 and C9, where the
   household neither left nor won. These are now part of §4.
4. **Paths that exist (catch-up and correction family).** Read off `chain`:
   - *silent*: did_not_notice → catch-up arrives → (shock) — C4, C5;
   - *call loop*: called → called … (no reply) → stays resentful — C1, C9;
   - *call → escalate*: called/complained → handling failure → Ombudsman or EHU → remedy — O1, O3,
     O4, O5, O6, C6, C7;
   - *pay more*: agrees a higher payment → further estimate — C2;
   - *withhold → debt*: cannot or will not pay → debt collection — C3;
   - *self-serve good path*: checks own position → resets DD → refund — M1.
   **In every escalated account the escalation followed a handling failure** (no reply, broken
   promise, blame, insisted-correct). This is the director's "how the issue is handled then affects
   the likelihood to churn" with one correction from the evidence: in these sources the branch that
   handling moves is **escalation and resentment**, not observed switching. No account records a
   switch (G3).
5. **Price shocks are absent from every published case-study source.** Not one of the 16 is an SVT
   rise or an end of fix: the Ombudsman and Citizens Advice publish disputes, and a price rise
   applied correctly is not a dispute. So the price-shock *paths* (lapse, take the next deal, shop
   around; the three SVT moments) **cannot come from case studies**. They come from the trials and
   the switching series (§2.2, §3), and their customer-voice side must come from forums and review
   sites. That is the first job for the advisor's offered pass after 23 Nov, and it is the reason
   no `moment` code is yet exercised by a real account.

**What "proven" means here, and does not.** The scheme is proven *usable*: sixteen accounts from
three publishers coded without a field it could not hold, and the five amendments above folded back
in. It is **not** yet proven on the price-shock family. The theme map
(`customer-voice-theme-map-after-the-bill-shock-scheme-is-proven`) may start on catch-up themes now;
it should not code price-shock accounts until the forum/review sample has exercised `moment`.

## 6. Gaps, filed and not filled

- **G1 — media coverage as a dated world input.** No count of national news stories per price-rise
  announcement exists in the repo or was found published. Steer item 3 forbids inventing one. Route:
  a harness-side count over a news archive (GDELT's event database or a licensed press index) of
  stories naming an energy price rise, per week, 2016–2025, landed as documentation and a dated
  series, never a runtime input the company reads (W6). Until then the world's announcement moment
  carries no media term, and T2b is graded on the effective month only.
  **Filled for announcement days, 21 Nov 2026:**
  `media_coverage_of_energy_price_announcements_gdelt_2016_2025.md` counts national news
  coverage of every dated announcement over GDELT's daily files. Its 28-day baselines and the
  full weekly series are still being pulled; that page carries the status.
- **G2 — mid-term leaving by fixed customers.** No published rate. Routes: Ofgem CIM/CES microdata
  (a question on switching before the end of a fix, if one was asked); a practitioner figure from a
  retention desk. Carried as `None`; T4 is ordinal until then.
- **G3 — churn after bad handling of a catch-up.** The Ombudsman sample cannot show it (cases that
  reach it have stayed to fight). Routes: CIM satisfaction-by-switching tables already on file
  (`what_a_supplier_can_observe_about_switching_propensity_cim_w6.md`), and review-site accounts that
  record leaving, for the path only.
- **G4 — the share who do not notice a DD change, by payment method.** None published.
- **G5 — the effective dates of the 2016–2018 supplier price rises**, beyond British Gas Sep 2017,
  to date T2b's pre-cap months by moment rather than by month. **Filled, 21 Nov 2026**, except
  four announcement days and any second 2018 rise by npower or SSE:
  `energy_price_announcements_gb_2016_2025.json`, read in §3 of the media-coverage page. British
  Gas's 2018 rise took effect 29 May (announced 10 Apr), not in Jun–Jul.

## 7. What this changes

- **Code: nothing in this commit.** The world build that consumes this (extending
  `simulation/activation_energy.py`, `simulation/resentment_ledger.py`,
  `simulation/payment_behaviour_source.py`, `simulation/bacs_rails.py`,
  `simulation/contact_propensity.py`, with no parallel shock table) is handed on, after G1.
- **`simulation/household_segments.BILL_SHOCK_ENGAGEMENT_MULTIPLIER` stays `None`.** This page
  replaces the question it refuses ("by how much does a shock raise the odds of shopping") with a
  design in which no such constant exists: each family and moment fires the household's own
  responses, and the aggregate is graded against T1–T4.
