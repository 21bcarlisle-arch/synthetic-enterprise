# A new account's first months: the opening estimate, the first direct debit, the opening read, and what goes wrong

**Knowledge:** payments-and-direct-debit

**Asked by** the director, chat 30 Oct 2026 07:30 GMT: "Create knowledge in this area and in unbilled.
What do different people do. What are the pros and cons. What do customers experience. What pain points
should we measure. Is the SIM making customers react and behave to pain points?" The advisor's evidence
pack is `docs/staging/advisor/done/DIRECTOR_EVIDENCE_A_NEW_ACCOUNTS_FIRST_MONTHS_ESTIMATE_DD_AND_PAIN_POINTS_2026-10-30.md`;
every URL below is in it beside its claim. This page is the knowledge, distilled and set against what we
have built. It changes no code except the one gap it closes (§1, PC2 TDCV 2026).

**How figures are marked.** **[H]** read in the primary document this session (two Ofgem PDFs, text
extracted locally, not through a summariser). **[P]** from the advisor pack with its URL, not re-read
here. **[A]** the pack's or this page's own reasoning, which no source states. **GAP** searched for by
the pack and not found; no number is supplied and none should be invented.

Neighbouring pages, not repeated here: `payments_and_direct_debit_2026-10-25.md` (method mix, cost to
collect, SLC 27.15 history), `what_a_supplier_holds_to_size_a_direct_debit.md` (the TDCV series, SLC
27.15's ordering), `how_a_supplier_shapes_an_estimate_for_an_unread_month.md` (§10, the director's
standard-practice baseline), `home_moves.md`, `switching-mechanics`.

---

## 1. Where the opening figure comes from, best to worst

A gaining supplier must forecast a year of use before it holds a single read of its own. Five sources,
roughly in order of quality:

| Rung | What it is | Quality and its failure | Grade |
|---|---|---|---|
| Smart history / the losing supplier's data after the switch completes | Octopus estimates first, then refines "once the switch completes" | Best, but arrives *after* the first DD is set | [P] |
| Industry EAC (electricity, D0019) / AQ (gas, Xoserve) | Per meter point, from successive reads and the profile | Good, but inherited: a bad change-of-supplier read corrupts the EAC the gainer receives (Elexon guidance names this root cause) | [P]; Xoserve AQ-at-switch mechanics GAP |
| Customer's declared use at quote | kWh from an old bill, a £ spend, or low/medium/high | Medium; depends on the customer | [P] |
| TDCV default | Ofgem's typical consumption, used "where actual consumption is unknown" | Large and *structurally* biased for anyone off the median | [H] |
| Previous occupier's history (home move) | The EAC/AQ belongs to the meter point, not the person | Large and biased: a single person inherits a family's profile, or the reverse | [P] mechanism; [A] size |

**The TDCV series, re-read from Ofgem's 27 May 2026 decision, Table 1 [H]** (in force 1 July 2026):
PC1 1,600 / 2,500 / 3,800 kWh; **PC2 1,900 / 3,400 / 6,100 kWh**; gas 6,000 / 9,500 / 14,000 kWh;
Economy 7 split unchanged at 58% day / 42% night (Table 2). The PC2 row was recorded as "not
established" in `what_a_supplier_holds_to_size_a_direct_debit.md` §3 and absent in
`company/billing/annual_consumption_estimate.TDCV_BY_DATE`; both now carry it. The company runs
2016-2025, so no book reads this row; it closes a stated gap, nothing more.

**What we build today.** The supplier's opening rungs are `BASIS_ORDER = (REGISTRY_EAC, TDCV_TYPICAL)`
in `company/billing/annual_consumption_estimate.py`, with the TDCV keyed to the date in force. The
customer-declared rung is excluded by name because the world draws no declared use
(`CUSTOMER_DECLARED`). The previous-occupier bias is not modelled as a distinct rung: GAP in the world.

---

## 2. The opening read at change of supplier

- **Smart (DCC-enrolled):** the gainer reads remotely. [P]
- **No read:** the gainer asks for a customer read or sends an agent within 10 working days. [P]
- **Deemed read (electricity, D0086):** if no valid read arrives, the data collector deems one. Elexon
  CP0768 records that many fall back on their *own old history* after SSD+8, "a significant risk that
  poor data will be used resulting in disputed reads". [P] The deeming formula: GAP.
- **Disputes:** either supplier or the consumer may raise one within **12 months**. Materiality is
  **250 kWh** electricity and **1,200 kWh** gas; below it the supplier normally offers an accommodation
  and keeps the read. [P] (Source is the 2018 REC v2.0 draft; whether the live REC schedule differs is
  GAP.) Frequency of change-of-supplier read disputes: GAP.

**Why it matters [A]:** a deemed opening read is a latent error. Nothing shows until the first actual
read, often months later, when it surfaces as a catch-up in either direction.

---

## 3. Setting and reviewing the first direct debit: what different suppliers do

**The rule.** Since about 21 October 2022, SLC 27.15 requires a fixed DD on the "best and most current
information available" in every case; the "all reasonable steps" qualifier and the Principal Terms
exemption were removed. Ofgem said a DD need not be reset on every new fact, only where the impact is
material, and it **rejected** mandated review intervals, quarterly reviews and a 12-month balance
limit. [P] **No rule sets a first review for a new customer.** The 3- or 6-month first review is a
supplier choice, and no named supplier's first-review point was found: GAP.

**What the 2022-23 compliance review secured as de facto commitments [P]:** more frequent adequacy
checks, tolerance-triggered extra reviews, surplus credit refunded or used to lower the DD, faster
refunds, written DD and refund policies, and an aim of a **near-zero balance over 12 months** for
customers in credit. Ofgem named "estimated billing that differs from later meter readings, often
leaving a debit balance" as a driver of DD rises.

**Four families of practice, with their trade-offs:**

| Family | Who (per MSE and help pages) [P] | For | Against |
|---|---|---|---|
| Level DD, periodic review | British Gas (1-2 reviews a year), EDF and E.ON Next (quarterly), Scottish Power (quarterly, background monitoring) | Predictable; summer credit funds winter | Credit is held; errors compound between reviews; infrequent reviews mean big steps |
| Level DD, continuous monitoring, a credit target | Octopus (about a month's credit by end of April), OVO (one month by end of March; new joiners aim for nothing owed after a year) | Smaller, earlier corrections | A deliberate buffer reads as overcharging to a customer who does not know the target; OVO's refund conditions (90 days, 2 payments, a recent read, at least £5) add friction |
| Variable DD (pay what you used) | Octopus variable DD, Fuse | No credit held; no forecast error to correct | Winter payments much higher; depends on smart reads |
| Customer-adjustable band | EDF, E.ON Next, OVO allow about 10% below the recommendation | Agency | Lets a customer under-pay into arrears |

General practice [P]: annual cost / 12; a debit or credit spread over the next 12 months; notice of a
change between 5 working days and a month, 14 days common.

**The step-up arithmetic [A].** A customer whose opening estimate was 30% low, found at month 6, meets
both a 30% higher run-rate *and* six months of under-payment spread over twelve, so the DD rises well
over 30%. This is why year one is the peak-risk year.

---

## 4. What customers meet

| # | Pain point | Definition (what is measured, for whom) | Evidence of reaction | Grade |
|---|---|---|---|---|
| P1 | Opening estimate wrong | Forecast error = opening annual figure / read-based annualised use at months 3 and 6, by rung | Ofgem names estimate-vs-read divergence as a cause of debit balances; no churn figure | [P]; reaction GAP |
| P2 | DD step-up at first review | % change of the DD at a review, for DD payers; separate from a bill | 13% of payment/bill/price complainants cited a DD rise without warning (Which? 2021); **46% of those whose DD doubled did not challenge it** (MSE 2022, self-selected); 62% average SVT DD rise Feb-Apr 2022, about 8% over 100% | [P] |
| P3 | DD too low, arrears | Debit balance and days past due on a DD account | 13% of credit-meter consumers fell behind (Q1 2022); 43% of those contacted the supplier, 31% of credit-meter customers first | [P] |
| P4 | Credit build-up, refund friction | Credit balance / monthly DD; refund requests and refusals | 9% of payment complainants struggled to get a refund (Which? 2021) | [P] |
| P5 | Estimated bills | Share of bills read-based (Citizens Advice: 6 months smart, 12 months other) | Billing-accuracy satisfaction 80% Jan 2026, down from 82% | [P] |
| P6 | Catch-up or back bill | First actual read reveals under-billing; catch-up £ / monthly DD | 61% said they *would* switch after a high bill (Opower, secondary, undated): stated intent, not a rate | [P]; realised rate GAP |
| P7 | Opening-read dispute | Disputes raised; accommodation paid | 12-month window; 250 / 1,200 kWh thresholds | [P]; frequency GAP |
| P8 | Deemed new tenant | Time on deemed terms; early loss | Placed on the default tariff on moving in | [P]; churn GAP |
| P9 | Default-based quote | Quote-to-actual gap where the quote used a TDCV | 2026 TDCV cut: a household at the old medium is quoted about 7% low on electricity and 17% low on gas | [H] TDCVs; [A] the gap |
| P10 | Complaint handled badly | Complaints per 100k; 8-week deadlock; signposting | 47% dissatisfied with handling (Which? 2021); Ombudsman signposting 48% (2025) | [P] |

**Three GAPs that matter most** (none published, all held privately by suppliers): the churn
elasticity to a DD rise of x%; the DD cancellation rate after a rise; the share who *actually* switch
after bill shock. The pack's only figures are stated intent or self-selected surveys. Under K2 none of
them is zero, so the world must carry each as a stated belief with a range, and a supplier strategy
counts as better only if it wins across that range.

---

## 5. Billing and settlement disagree most in the first months

- Settled volume for a non-half-hourly meter comes from the EAC, so a wrong EAC "shifts energy between
  Suppliers", with network charges following. [P] The supplier is settled on the EAC, bills on its own
  estimate and collects a level DD: three ledgers, each corrected on its own clock. [A]
- RF is at 14 months today; under MHHS it moves to 7 months from 1 April 2027 and 4 months from 2 July
  2027. [P]
- Unbilled revenue rests on the supplier's least reliable data, which sits on its newest accounts. [A,
  with Centrica's auditor treating unread revenue as a key audit matter, P]
- SLC 21BA ties the clocks: under-billing unnoticed for more than 12 months is unrecoverable while
  settlement has already charged for the energy. [P]

The billing-to-settlement gap is not measured on any of our books:
`how_a_supplier_shapes_an_estimate_for_an_unread_month.md` §10 already carries this GAP.

---

## 6. What a supplier could test, and what the world must do first

The pack lists fifteen levers. Grouped, with what each needs from the world before it can be graded:

| Lever | Needs the world to… | World today (audit, `SEAT_FINDING_THE_WORLD_REACTS_TO_ONE_PAIN_POINT_IN_SEVEN…`) |
|---|---|---|
| Opening-estimate rung (wait for EAC/AQ; TDCV with a margin) | Draw declared use and a previous-occupier bias | Neither is drawn |
| First-review timing (1, 3, 6 months, or at the first actual read); tolerance trigger; step cap and phasing | React to a DD step: cancel, fail, complain, leave | Leave: on. Cancel, fail, complain: built in `simulation/dd_shock_response.py`, **shipped at 0** |
| Credit target; proactive refunds | React to held credit and a refused refund | No reaction |
| Read capture at switch and move-in | Produce deemed opening reads and disputes | No deemed-read error modelled: GAP |
| Debit spreading; affordability-flagged spreading | Default with DD-to-income stress | Partly: payment-stress tiers feed departure |
| Complaint handling and signposting | Escalate on handling, not just on a renewal rise | A complaint roll per renewal term only |

The experiment itself is filed as `new-account-first-months-experiment` in
`docs/direction/priority_order.yaml` `customer_outcomes_candidates`, due 2026-12-15, drawn after the
correctness exit test. This page is its knowledge stage.

## 7. A correction carried from the pack

The pack notes that SLC 21B's read duty is **annual** (reasonable steps), and that the two-yearly duty
was a meter *inspection* duty (SLC 12.14-12.16) repealed from 1 April 2016. Checked: the invariant
library already holds it that way (`INV_READ_DUTY_ANNUAL`, upper 365 days, with a
`correction_to_brief` naming the repealed inspection duty), as do `read_access_and_theft_duties.md`
and the smart-meters page. Nothing to correct.

## 8. The pack's [unverified] items, checked against their primaries (30 Oct 2026)

Each item the pack marked [unverified] was checked through the harness's network on 30 Oct.
**VERIFIED** means the primary says it, **REFUTED** means the primary says otherwise, **PARTLY** names
the part that holds, and **GAP** means searched and not established. "Not fetched" is not a GAP: it
says the primary exists but could not be read this pass.

| Pack line | Claim | Verdict | Primary, and what it says |
|---|---|---|---|
| 43 | Rolling AQ recalculated monthly from reads (Nexus); the gaining shipper sees AQ at switch | **PARTLY**: monthly rolling AQ holds; what the gaining shipper sees at switch is **GAP** | Xoserve, *Q&A: AQ* (xoserve.com/media/7749/qa-aq.pdf): "A replacement read does not trigger a new Monthly Rolling AQ". The AQ BRD returned 404 (not fetched) |
| 60, 204 | Comparison sites default usage to TDCVs, and the quote passes to the first DD | **PARTLY**: Uswitch's footnotes assume medium usage at figures that vary by page (2,500 or 2,700 kWh electricity, 9,500 or 11,500 kWh gas); the estimator method and any pass-through to the DD are **GAP** | Ofgem's TDCV letters say TDCVs are used by comparison sites "when the actual annual consumption may not be known" (search snippet only) |
| 75 | The live REC holds the switch-meter-reading process | **VERIFIED** (name and place) | REC Portal, MHHS consequential change: "REC Schedule 30 - Resolution of Consumer Facing Switching and Billing Issues includes a number of exception processes". The Switch Meter Reading exception process is "mandatory for Non-Half Hourly (NHH) Metering Points". Schedule 30's own text was not fetched |
| 84 | A deemed CoS read rolls forward from the last valid read on EAC and profile | **PARTLY**: deemed read at CoS confirmed; the formula sits in BSC Annex S-2 (not fetched) | Elexon BSCP504 §4.5.2: "A Deemed Meter Reading shall be calculated … if a valid actual Meter register reading cannot be obtained … Change of Supplier", "using the formulae set out in Annex S-2 of the Code" |
| 117 | Ofgem's 2021 automatic annual credit refund was adopted as drafted | **GAP** on the outcome, and the August 2022 decision does **not** contain it | Ofgem 2021 consultation: "refund any balance above £0 each year on the anniversary". Ofgem decision on credit balances (Aug 2022) covers only SLC 27.15, making "best and most current information" absolute. It contains no auto-refund |
| 118 | Content of Ofgem's letter to the ESNZ Committee | **VERIFIED**, dated 29 Nov 2023 | "net domestic customer credit balance was around £4.1 billion, equating to around £140 per customer"; 900,000 customers' DDs reviewed; compliance action covered 12 suppliers and enforcement covered one; "Customers can ask their suppliers for a refund of their net balance at any time". The letter announces no new DD licence change |
| 130 | OVO sells "smart payments" | **REFUTED** on the pages read | OVO, *How to pay* (ovoenergy.com/help/article/how-to-pay) lists Direct Debit, card, one-off online, cheque and bank transfer. No product of that name was found |
| 144 | A named supplier states a first DD review point for new customers | **GAP** for a *first* review. The *recurring* cadence is published | Uswitch (2023, reporting supplier policy): "Ovo Energy: Every three months", "Shell Energy: Every three months", "EDF Energy: Twice a year", "E.ON Next: Automatic review with every bill" |
| 197 | Deemed contracts (SLC 7) and exit fees | **PARTLY**: terms must not be "unduly onerous" (SLC 7.3), and domestic deemed rates sit under the cap. Whether an exit fee can apply is **GAP** | Ofgem, *Guidance on Deemed Contracts* (Nov 2023) |
| 224 | Which Citizens Advice star-rating weights are live | **VERIFIED**: revised weights, first used on Oct-Dec 2025 data and published March 2026 | Citizens Advice decision document (Aug 2025), Table 2: ease of contact 30% (calls 18, email 6, other 6), billing and metering 25% (billing 15, smart 10), complaints 35%, customer commitments 10% |
| 250 | Opening-estimate error to churn | **GAP** | None found |
| 257 | DD cancellation rate after an increase | **GAP** | None found. Ofgem's 2022 review reports only the size of the rise (62% average, 8% over 100%) |
| 266, 338 | "61% would switch after a high bill" (Opower) | **PARTLY, primary not found**: the only source is secondary. A conflicting figure, "two-thirds … planned to switch in the next 12 months", is attributed to Opower in Utility Week (May 2015), which returned 403 (not fetched) | Treat as stated intent of about 61-67%, about 2015. It is not a rate |
| 275 | Frequency of CoS read disputes | **GAP** (not searched specifically) | None |
| 279, 340 | Deemed-customer complaint or churn rates | **GAP** | None |
| 310 | A supplier's contracted-vs-metered difference is cashed out at the imbalance price | **VERIFIED** | Elexon, *Imbalance pricing*: "BSC Systems compare a Party's contracted (traded) volume with the metered volume", and "there is a single price calculation, so SBP will equal SSP". Single price since P305, 5 Nov 2015 (search snippet) |

**Corrections to this page from the checks:** none of §1-§7's figures moves. The pack's OVO "smart
payments" row is refuted and is not used anywhere above.

The pain points' ranges have one home each, on the site pages (FM, UB and BB rows, b587ead30e).
