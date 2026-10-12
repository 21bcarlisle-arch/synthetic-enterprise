# What bill shock is — a definition, before any more measuring

*Knowledge pass, delivery seat, 2026-09-01, on the director's instruction: "we have never defined
bill shock… go back to knowledge first and define it from published evidence before measuring it
again, including what share of households are on each payment method, since that decides which
definition applies to whom. Then the cause split follows from the definition rather than the
definition from the split."*

**This page supersedes the framing of Part 2 of
`satisfaction_drivers_and_the_three_bill_shocks.md`.** That page established three *causes* and was
right about each; it treated bill shock as one experience with three causes. It is the other way
round: there are **two experiences in different populations**, and the causes sit inside them.

---

## The failure this page exists to end

`bill_shock_pct` has always been *the percentage difference between two consecutive bill totals*.
That is not a definition of an experience — it is an arithmetic operation, applied uniformly to
households who would describe what happened to them in completely different words.

**For most GB households the bill is not the thing they pay.** They pay a fixed monthly amount. The
bill is a statement that arrives and is filed. Differencing two bills and calling the result a shock
measures something that household did not experience.

---

## The populations, and their published shares

| payment method | share of GB domestic | what the household actually pays |
|---|---:|---|
| **Direct debit** (fixed and variable together) | **~74%** | a monthly amount set by the supplier |
| **Standard credit** | **~13%** | the bill, in full, each period |
| **Prepayment** | **~13%** | credit at the meter, in advance |

*(Ofgem, 2026, already in this repository at `dd_attribution_confound_w2_10.md`; drives
`_TARGET_DD_SHARE = 0.74`.)*

Within direct debit, Ofgem's credit-balance publication counts **15 million households paying by
FIXED Direct Debit and in credit** (year ending June 2025), rising to ~17 million on the
12-months-ending-December-2025 window. Those are the households whose payment is a level amount
rather than the bill.

**The fixed-versus-variable direct-debit split is NOT published**, and it matters: a variable-DD
household pays the bill and therefore belongs, experientially, with standard credit. This is a real
gap and it is stated rather than filled — see "What is not settled" below.

---

## The definition, per population

### A. Households paying a level amount — fixed direct debit

**The bill shocks nobody. The payment change does.**

The shock is one of two things:

1. **A material change in the monthly payment.** The regulated trigger for a review is a variance
   beyond **±5%** — a band of OURS, not a licence rule: the duty is **SLC 27.15** and no threshold appears in the licence, there being no SLC 27B. Ofgem's own escalation cut in the 2022 DD Compliance
   Review was an increase **above 100%**, which put **over 900,000 direct debits** into a mandatory
   re-review; across Feb–Apr 2022 over 7 million SVT consumers saw an increase averaging **+62%**,
   with **8%** above 100%.
2. **A credit or debit balance they do not understand.** The published norm: **£200 average credit
   balance per household** (year ending June 2025, down from £244), **£3.09 billion** held in total
   across ~15 million households, **£178** average at the end of June 2025.

**A balance building and unwinding across the seasons is normal**, and a household not understanding
that is itself part of the experience rather than evidence of a supplier failure. The shock is not
the balance existing; it is the balance being *unexpected* — which is a communication property, not
an arithmetic one.

### B. Households paying the full amount — standard credit, and variable direct debit

**The shock is the bill**, and it has three published triggers:

1. **Cold weather** — a seasonal consumption rise the household did not anticipate.
2. **A usage change** — a new appliance, a new occupant, a change of circumstance.
3. **An actual read replacing a long-standing estimate**, arriving as a jump *plus* a catch-up.
   Ofgem's own words: *"suppliers estimating bills until they have an actual meter reading which may
   show that the customer's consumption is higher than expected. Suppliers then send a 'catch-up'
   bill to recover the difference."* Capped at **12 months** by SLC 21BA; **median domestic backbill
   £1,160** (2016/17); one of the largest single reasons domestic consumers contacted Citizens Advice
   (**>15%** of cases) and the Energy Ombudsman (**12%**) in 2016.

### C. Prepayment — neither definition applies

**~13% of households have no bill to be shocked by and no direct debit to be changed.** They top up
in advance. Their equivalent experience is self-disconnection or an unaffordable top-up, which is a
different measurement with a different remedy and is **out of scope of "bill shock" entirely.**
Including them in either definition would be the same error one level down.

---

## How the three causes map onto the two definitions

The director's three causes were right; they were not three cases of one thing.

| cause | population it lands in | responsibility |
|---|---|---|
| catch-up after estimates | **B** (the bill) | supplier — an inference failure |
| DD set wrong, then reset | **A** (the payment) | supplier — an operational failure |
| genuine renewal price rise | **both**, experienced differently | supplier — a commercial choice |

The renewal rise is the one that crosses: a full-payment household sees it in the next bill; a
fixed-DD household sees it only when the DD is next reviewed, possibly months later, and by then it
is entangled with any balance drift. **Same commercial decision, two different experiences, two
different lags.** That alone makes a single scalar untenable.

---

## What is not settled by the published record

1. **The fixed-versus-variable direct-debit split.** Ofgem publishes fixed-DD credit balances and the
   overall DD share; it does not publish how many DD households pay a level amount versus the actual
   bill. Without it, the boundary between definition A and definition B cannot be drawn from
   published data alone. **This is the single most load-bearing gap on this page.**
2. **Debit balances.** Ofgem publishes **credit** balances only — the money suppliers hold. The debit
   side, which is half of the director's definition A ("an unexpected credit *or debit* balance"), is
   not in the same series. An asymmetry worth naming: the regulator measures what suppliers hold, not
   what customers owe.
3. **Any seasonal breakdown of balances.** The publication is 12-month windows; it does not show the
   build-and-unwind cycle that the definition calls normal. So "normal seasonal swing" cannot
   currently be quantified from this source.
4. **What magnitude of DD change a household actually notices.** ±5% is a regulatory review trigger
   and >100% was a regulatory escalation cut. Neither is a measurement of noticing.

---

## What follows for measurement

**The cause split follows from the definition, not the reverse.** Concretely, before any further
measuring:

* A shock measure must know **which population a household is in**. Payment method is therefore an
  input to the measure, not a covariate of it.
* For population **A**, the quantity to measure is the **change in the amount collected**, and the
  balance alongside it. Not the bill.
* For population **B**, the quantity is the **bill**, and the existing cause split (catch-up /
  price / consumption) applies to it.
* For **C**, neither, and it should be excluded explicitly rather than by accident.

A single percentage difference between two bills is definition B's quantity applied to everybody,
including the ~74% for whom the bill is not what they pay.

*(What this project's own world currently does about that is a simulation reading and does not belong
on a commons page. It is measured in
`WORKER_FINDING_THE_WORLD_KNOWS_HOW_EACH_HOUSEHOLD_PAYS_AND_BILL_SHOCK_IS_THE_ONE_ORGAN_NOT_TOLD_2026-09-01`.)*

---

## Sources

- [Ofgem, Domestic Energy Customer Credit Balances, July 2024 – June 2025](https://www.ofgem.gov.uk/data/domestic-energy-customer-credit-balances-july-2024-june-2025) — £3.09bn total, £200 average per household, £178 at end-June, ~15m fixed-DD households in credit.
- [Ofgem, Domestic energy customer credit balances, January – December 2025](https://www.ofgem.gov.uk/data/domestic-energy-customer-credit-balances-january-2025-december-2025) — £3.17bn, ~17m households.
- [Ofgem, Direct Debit Market Compliance Review / press release, July 2022](https://www.ofgem.gov.uk/press-release/ofgem-requires-improvements-energy-suppliers-customer-direct-debits) — >7m SVT increases, +62% average, 8% above 100%, >900,000 re-reviewed.
- [Ofgem, back-billing ban beyond 12 months (SLC 21BA)](https://www.ofgem.gov.uk/press-release/ofgem-bans-suppliers-backbilling-customers-beyond-12-months); [Energy Ombudsman, What is back billing](https://www.energyombudsman.org/advice-for-consumers/what-is-back-billing).
- Payment-method mix (~74/13/13): Ofgem 2026, recorded in `docs/market_research/dd_attribution_confound_w2_10.md`.

*Fetched live 2026-09-01. No figure on this page is simulation output.*

---

## Addendum 2026-10-11 — reassessment cadence, winter handling, and the catch-up dose-response (for a personal payment plan)

*Research pass, discovery agent, for the director's 2026-10-11 instruction: "credit risk sets how
far a customer's balance may drift from zero, not how much they pay over the year... low-risk
customers get smoothing, prompt refund of surplus credit and no catch-up shocks; higher-risk
customers are kept near zero without winter bill shock." Scope: how often a GB supplier reassesses
a fixed DD in practice, how winter is handled, and the evidence on dose (size/frequency of a DD
change) versus failed payments, complaints, churn and debt. Written into **population A** (fixed
direct debit) of this page, since it is the payment-change half of the shock, not the bill half.*

### 1. Reassessment cadence — ESTABLISHED: there is no mandated or industry-standard cadence

Ofgem's **Decision on Statutory Consultation: Credit Balances — Strengthening existing Direct Debit
rules** (26 Aug 2022) is the primary source and settles this directly, because suppliers themselves
asked for a cadence and Ofgem explicitly declined to set one:

> "The key issue raised by suppliers was whether the changes would mean that fixed DDs would need to
> be reset every time they received a new piece of information... Five respondents proposed new or
> alternative SLC wording... Two other respondents requested SLC wording changes to require
> **quarterly or 'on-demand' DD reviews**."
> — Ofgem's own decision: **"we do not anticipate a supplier needing to reset a DD where a new meter
> reading reports a minimal change in consumption"**; instead, new information "should feed into a
> broader picture... and suppliers should reassess a customer's fixed DD when they receive
> information that is **likely to have a material impact** on the DD amount. Where any reassessment
> determines that a change to a DD would be immaterial, suppliers should use their discretion."

**ESTABLISHED (H):** the obligation (SLC 27.15, strengthened Oct 2022) is *event/materiality*
triggered, not calendar-scheduled. Ofgem considered and rejected mandating quarterly or on-demand
review. There is no published "N times per year" industry figure, and per Ofgem's own framing there
is not meant to be one — it is explicitly left to supplier discretion once a material-impact test is
met.

**DERIVED (M), practice varies by supplier and improved post-2022:** the DD Market Compliance Review
progress update (Ofgem, undated, "Direct Debit Market Compliance Review: Progress Update") lists
supplier remediations including *"Increased frequency of Direct Debit adequacy assessments to ensure
consumers continue to pay the correct amount in line with energy usage"* as one of the concrete fixes
suppliers made across 56 identified concerns (53 of 56, 95%, resolved by the review's close). This
confirms frequency **was** a live compliance issue and **did** vary supplier-to-supplier before 2022,
but no post-remediation frequency number (e.g., "now reviewed quarterly") was published for any
supplier. **GAP: the cadence a "good" supplier now runs is not published anywhere; it is a
practitioner question, same shape as the DD-failure-threshold gap already flagged in
`what_a_supplier_holds_to_size_a_direct_debit.md`.**

### 2. Winter / seasonal handling — ESTABLISHED mechanism, NOT ESTABLISHED magnitude or shape

Same source, direct quote (also already cited in `satisfaction_drivers_and_the_three_bill_shocks.md`
§(b), reconfirmed here against the primary PDF rather than the press release):

> "Where a consumer is in a credit position, **we expect suppliers to reduce the associated Direct
> Debit level with the intention of returning the account as close to a zero balance over the next
> 12 months**. Similarly, where a consumer account is in a debit position, **suppliers commonly add
> this amount on to the Direct Debit amount and smooth the cost over the next 12 months**."

**ESTABLISHED (H):** the *mechanism* is a 12-month glide, both directions — credit is given back
gradually, debit (which includes a winter-driven catch-up) is spread over a year, not collected in a
lump sum or concentrated into the following winter. This is the regulatory expectation across the
whole DD book, not a special winter rule — there is no separate published "winter catch-up" product
or rule distinct from ordinary DD adequacy review.

**NOT ESTABLISHED (gap, unchanged by this pass):** the glide path's *shape*. "Over the next 12
months" is the only parameter published — no supplier is required to publish, and none was found to
publish, whether the £X debit is spread evenly (1/12 per month), front-loaded, or weighted to avoid
landing the increase in December–February specifically. **A plan that explicitly avoids loading a
catch-up into the coldest months would currently be ahead of the published norm, not behind it** —
there is no rule it would be competing against, only the 12-month outer bound.

### 3. Size and frequency of a DD change versus failed payments, complaints, churn, debt — largely NOT ESTABLISHED; one real proxy found

**No published source crosses DD-change magnitude or frequency against failed-payment rate,
complaint rate, churn or debt at household level.** This matches and extends the existing gap already
recorded in `satisfaction_drivers_and_the_three_bill_shocks.md` Part 2 ("What the published record
does NOT settle", item 2: no per-unit dose-response). Two things were newly found this pass that
bound the problem rather than solve it:

1. **The 2022 re-review's own error rate was low.** The *Progress Update* page states: "Almost
   **1 million** Direct Debits fell into the scope of the review exercise [>100% increases,
   Feb–Apr 2022] and to date issues have been confirmed with approximately **4,000**." That is
   **~0.4%** of the reviewed, large-jump population found to be genuinely wrong (as opposed to a
   justified reflection of real cost increases). **DERIVED (M):** even at the most extreme dose in
   the record (>100% single-step increase), the overwhelming majority of large DD jumps were
   *accurate*, not supplier error — which says the failure mode this project should model is not
   "large jumps are usually wrong" but "even a correct large jump is poorly tolerated," a distinct
   claim the published record does not test either.
2. **Compensation, where paid, was small per head.** £117,580 total compensation against ~4,000
   confirmed issues is **~£29/case** (DERIVED, simple division, M) — consistent with the finding
   being a process/communication failure rather than a large sustained overcharge.

**GAP, explicitly not closed this session:** no Citizens Advice complaint-volume breakdown specific to
Direct Debit changes (as opposed to "billing" generally) for 2022–2024 was reachable — Citizens
Advice's own site returned empty/JS-blocked responses to a scripted fetch this session (same
search-engine/JS constraint logged in `gb_payment_method_migration_rates.md`'s sources section and
`dd_failure_basis_and_live_arrears_provision_rates.md`'s epistemic note). The existing
Ombudsman/CAB figures already on this repo's pages (billing = 58% of Ombudsman complaint volume,
2024, per `satisfaction_drivers_and_the_three_bill_shocks.md`) are the closest published proxy and
are not DD-change-specific.

### 4. What this means for a personal payment plan merged with debt management

The director's framing — **credit risk bounds the drift, not the annual total** — has direct support
and direct gaps in what is published:

* **Supplier-controlled, with published cover to act on now:** the 12-month glide for both directions
  is already the regulatory norm (§2), so a plan that smooths a low-risk customer's surplus back
  faster, or more gradually, than the generic "12 months" is *inside* what suppliers already do
  case-by-case under SLC 27.15 discretion — it is not a departure from the regulated norm, because the
  norm itself has no fixed shape, only an outer bound.
* **Supplier-controlled, ahead of the published norm:** avoiding a winter-timed catch-up for a
  higher-risk customer is not something any rule requires OR forbids; no supplier practice publishes
  doing this, so it would be a novel commitment, not a verified industry benchmark. State it as a
  design choice, not an established practice.
* **Reassessment cadence is a dial with no published right answer** (§1) — "how often" is therefore a
  genuine design decision for the plan, not a figure to source, and should be recorded as such in the
  design doc rather than attributed to a number nobody published.
* **The dose-response the director's framing implicitly assumes — that a bigger or more frequent
  change costs more in failed payments/complaints/churn — is not established at the magnitude level**
  (§3). The one real data point found (the 2022 re-review) suggests the *correctness* of a large jump,
  not its *size*, may be what is poorly tolerated — which is a different, and testable, claim from
  "keep changes small." This should be flagged as a prediction to test inside the simulation, not
  imported as a validated real-world dose-response, consistent with CLAUDE.md's rule against
  publishing a dose-response the record does not contain.

### Sources added this pass

- Ofgem, *Decision on Statutory Consultation: Credit Balances — Strengthening existing Direct Debit
  rules*, 26 Aug 2022 — <https://www.ofgem.gov.uk/sites/default/files/2022-08/Decision%20letter%20DD%20rules.pdf>.
  Retrieved 2026-10-11. (Primary PDF read directly; supersedes reliance on the press summary alone for
  §1–§2 above.)
- Ofgem, *Direct Debit Market Compliance Review: Progress Update* —
  <https://www.ofgem.gov.uk/decision/direct-debit-market-compliance-review-progress-update>.
  Retrieved 2026-10-11. Source of the 56-concerns/53-resolved, "almost 1 million"/"~4,000
  issues"/£117,580 compensation figures in §1 and §3.

*Fetched live 2026-10-11. No figure in this addendum is simulation output.*

---

## DD4b: how the world responds to a direct-debit shock -- rules, evidence, GAPs, and the build's choices (2026-10-11)

*Knowledge pass, world lane, for the director's 2026-10-11 instruction (seat proposal
`SEAT_PROPOSAL_A_PERSONAL_PAYMENT_PLAN_AND_DEBT_AS_A_NEXT_BEST_ACTION_DESIGNED_AS_ONE_2026-10-11.md`
§7 item 5 and §9g): a household that meets a large DD increase can cancel its mandate, fail its
collections, complain or leave. Until this pass the world could only make it leave. Population A
(fixed direct debit) throughout. No figure in this section is simulation output.*

### 1. The rules -- ESTABLISHED

- **The duty to set and review a DD** is SLC 27.15 ("best and most current information"); the ±5% band
  is a supplier convention, not licence text (corrected 2026-09-03; see the addendum above and
  `what_a_supplier_holds_to_size_a_direct_debit.md`).
- **A change in amount needs advance notice** under the Direct Debit Guarantee, and a collection that
  differs from its notice entitles the payer to an immediate refund from their bank, reclaimed from the
  supplier as an indemnity claim (`dd_failure_basis_and_live_arrears_provision_rates.md` §5).
- **The payer can cancel at any time at their bank.** The supplier hears it on ADDACS (code 0/1, the
  working day after the bank inputs it, to be acted on within 3 working days), and a collection already
  in flight returns ARUDD 1 "instruction cancelled". The supplier must then agree another way to pay
  what is owed (same page, §4 and the ARUDD code table).

### 2. The published evidence -- what it supports

| quantity | figure | source | grade |
|---|---|---|---|
| DD rises in the 2022 shock | **>7m** SVT DDs rose Feb-Apr 2022, **+62%** on average, **8%** (~500k) above 100% | Ofgem press release, July 2022 (re-fetched 2026-10-11) | H |
| Wrong among the largest rises | ~**4,000** of almost **1m** >100% rises confirmed wrong, **~0.4%**; £117,580 compensation (~£29/case) | Ofgem DD MCR progress update (addendum §3 above) | H (derived ratio M) |
| DD share across the shock | **72%** electricity / **73%** gas at Sep 2025, **up 3-4 points** on Sep 2020 | DESNZ QEP Dec 2025, "Payment methods", p.9 (fetched 2026-10-11) | H |
| Complaining at all | **2-6%** of consumers "made a complaint" a year (three waves 2025-26); ~**1%** of accounts per quarter (Ofgem complaints data) | `satisfaction_drivers_and_the_three_bill_shocks.md` | H |
| Billing as a complaint cause | billing **58%** of Energy Ombudsman volume (2024); back-billing **>15%** of Citizens Advice energy cases (2016) | same page; this page's population B | H, not DD-specific |
| Departure after a shock | PB4's hazard, level refitted against the published departure band | `simulation/experienced_bill_shock.py`, 2026-10-01 | built |

**What this supports, and no more.** (a) The 2022 shock was overwhelmingly *correct* (0.4% wrong), so
a response to a large rise is a response to its size, not to an error. (b) The rises did **not**
empty direct debit: the share rose across the period that contained them, so any lasting move off
DD after a shock was small against the background drift. (c) Complaints are bounded by all
complaints: no year's DD shocks can have produced more than the annual total.

### 3. What is NOT published -- the GAPs

1. **A dose-response from DD change size to anything.** No source crosses the size of a DD change
   with cancellation, failed collections, complaints or switching at household level (unchanged from
   the addendum's §3; re-confirmed on the Ofgem 2022 press release, which carries no behavioural
   figure). **GAP.**
2. **The household-initiated cancellation rate** (ADDACS 0/1 per mandate, or after a review). Behind
   the Bacs login or held as supplier data (`gb_payment_method_migration_rates.md`, 2026-10-03:
   "the one nothing publishes"). **GAP; practitioner question.**
3. **Returns by review outcome** -- whether a household fails more often while paying a raised
   amount. **GAP.**
4. **Complaints tagged to DD reviews** as distinct from billing generally. **GAP.**
5. **The "balance I did not expect" half of definition A.** It is a communication property, and the
   world holds no record of what a household was told. **GAP, unchanged.**
6. **Whether income is the cause.** Nothing publishes cancellation or complaint by income; the
   world's only stress-to-payment gradient is its own unsourced tier relativity (4x, 11.7x).

### 4. The build's choices, with reasons (`simulation/dd_shock_response.py`)

- **One trigger.** PB4's shock: a population-A household whose reviewed amount rises more than 15%
  over the amount in force. That 15% is itself inherited, not sourced (the page's "not settled" 4);
  using it again keeps one meaning of "shocked" across departure and the new responses.
- **No second departure term.** The shock already raises the departure hazard at the renewal it lands
  on, and that level was fitted against the published band. Another multiplier would count one shock
  twice.
- **Three new responses, each a labelled toggle shipped at 0** (`assumption_toggles.yaml`):

  | toggle | low | high | basis of the range |
  |---|---:|---:|---|
  | `dd4b_mandate_cancel_share_at_shock` | 0.01 | 0.10 | floor: smallest effect a 40-founder book can show. Ceiling DERIVED, weak: c x 7m / 28m off the DD share must sit inside a share that rose 3-4 points |
  | `dd4b_failure_uplift_after_shock` | 0.25 | 3.0 | floor, a modelling choice; ceiling = the world's own next-tier relativity (LOW failing like MODERATE) |
  | `dd4b_complaint_share_at_shock` | 0.02 | 0.24 | floor = lowest published annual complaint share; ceiling DERIVED = 6% of ~28m / 7m |

- **Hidden finances where they are the cause.** The cancel share is a LOW-stress household's, scaled by
  the world's stress relativity and capped at 1; at the high setting a HIGH-stress household therefore
  always cancels, which is the ceiling's job to show. The failure uplift multiplies the tier's own
  failure probability. Complaining is not scaled by income (gap 6).
- **How the supplier learns of it** -- only what a real supplier receives: the collection presented in
  the cancellation month comes back "instruction cancelled" (ARUDD, plus ADDACS through the existing
  mandate stream), and the household pays on receipt thereafter, as after a supplier stop. A
  complaint arrives as a contact through the run's one complaint booking. Simplification: a real
  ADDACS can arrive before any collection; here it rides on the returned one.
- **Window.** The failure uplift runs for the twelve billed months the reviewed amount is in force
  under today's annual review. A cancelled household stays on pay-on-receipt for the rest of its
  tenure; the supplier re-establishing a mandate is company work, not modelled here.
- **One reality.** The live payment triad, the Bacs rails and the arrears engine (published bad debt)
  all read the same response record, so returns, stops and write-offs move together.

### Sources added this pass

- Ofgem, *Ofgem requires improvements from energy suppliers on customer direct debits*, July 2022 --
  <https://www.ofgem.gov.uk/press-release/ofgem-requires-improvements-energy-suppliers-customer-direct-debits>.
  Re-fetched 2026-10-11: confirms >7m / +62% / 8% above 100%; carries no complaint, cancellation,
  failure or switching figure.
- DESNZ, *Quarterly Energy Prices*, December 2025, "Payment methods", p.9 --
  <https://assets.publishing.service.gov.uk/media/6942cb008f4636fa2c547df5/quarterly-energy-prices-december-2025.pdf>.
  Fetched 2026-10-11: 72% / 73% DD at end-September 2025, +3 / +4 points on September 2020.

## A changed amount or date: the world's answer (DD4c, 2026-10-12)

**2026-10-12, the world lane.** No new source read. The stimulus is what the household is TOLD:
a new monthly DD amount (at any point in the year, not only at the review), or the offer of a
collection date nearer its payday. Built in `simulation/dd_shock_response.py` beside DD4b.

**A new amount.** Answered exactly as a review is (DD4b): a rise of more than PB4's material
threshold (15% over the amount in force) is a shock, with DD4b's three responses and toggles, and
nothing smaller or any fall is. One meaning of "shocked" serves the review, the departure hazard and
a mid-year change. GAP: whether a household answers a FALL (relief, or suspicion that the amount is
wrong); nothing published, so nothing is drawn.

**A date nearer payday.**

| Choice the world makes | Range or rule | Evidence | Mark |
|---|---|---|---|
| Who it can help: a stretched household whose date now precedes its income | MODERATE or HIGH stress, and mismatched with share 0.53; a LOW-stress household is not drawn as mismatched | Diaz-Campo et al. (Tucuman, AAEP 2024): payday after the due date in 53% of low-income cases; Barrage et al.: the US effect "nearly vanishes" in high-income areas | ESTABLISHED share (analogue); direction |
| Whether it takes the offer | takes it if mismatched; a household whose date already suits it has nothing to gain | none on take-up (Illinois makes it a right on request; no uptake published) | choice from the mechanism, GAP on take-up |
| The effect on its failed collections | x (1 - r) from the change month on, r in 0.10-0.36 (`dd_date_alignment_failure_reduction`); compounds with any shock uplift in force | floor: Moneyline VRP trial, arrears 10% lower than standard DD (second-hand, flexible timing and amount); ceiling: Barrage et al., 36% fewer bills not paid on time (bill-receipt timing for pay-on-receipt accounts, so above a DD date choice); Diaz-Campo et al. "nearly 30%" | GB effect NOT ESTABLISHED; analogue range from 0.10 to the analogue's upper bound |

**Shipped off.** The reduction defaults to 0. No supplier in the run offers a date change, and no
seam carries the offer yet (the company lane's), so the response is the world's side for the day
one does; a response is recorded on the run's one mandate book, which the triad, the rails and the
arrears engine already read.

**GAPs:** any GB measurement of a DD date choice (Pay.UK returns by alignment unpublished); the
take-up of an offered date; a household's response to a fall in its DD; whether income timing is
known to a household at all in a world that draws no payday (the 53% stands in for a payday draw).
