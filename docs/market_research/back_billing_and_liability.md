# Back-billing and liability for unbilled energy in GB domestic supply

**Knowledge:** back-billing-and-liability

**Asked by** the director, 2026-10-06: back-billing and liability "deserve proper knowledge work,
not a re-check of a toggle value. Treat them like the step-1 areas: sources, what's established,
what isn't, written up as knowledge. Then set the toggles from what you find." Knowledge work
only. The one file this pass changes besides this one is `assumption_toggles.yaml` (§7). Researched
2026-10-06.

**How figures are marked.** **[H]** = read in the primary document this session, as text (PDF
through `pdftotext`, web pages as raw HTML). **[M]** = from a secondary source, a summary, or an
earlier repo document that did not read the primary. **[D]** = derived here; the arithmetic is
shown. **GAP** = searched for and not found. Nothing here is unmarked.

**What this pass could and could not reach.** The session's web-search budget ran out early, so
the sources are the ones reachable by direct URL. Read in full: Ofgem's April 2017 open letter,
the November 2017 statutory consultation (with the draft SLC 21BA text and Ofgem's annotations),
the March 2018 decision, Ofgem's May 2020 open letter on SLC 21BA, Ofgem's 2019 licence guide on
billing, Ofgem's consumer page on back bills, Energy UK's *Energy UK Explains: Back billing* (Feb
2025), the Energy Ombudsman's *Our backbilling stance*, its annual data for 2025 and H1 2026, and
the Ombudsman Services / Trust Alliance Group annual reports for 2016–2020 and 2022–2025. **Not
reached:** the consolidated SLC 21BA text as finally made (the draft is used; the decision says only
Part B's start date changed), any Citizens Advice report after 2017, the Ombudsman's back-billing
counts for 2017–2023, any supplier's disclosed back-billing write-off, and UNC/BSC text.

---

## 1. What back-billing is

**Definition.** A back bill is a supplier's demand for payment for energy a customer has already
used, and which the supplier has not previously asked them to pay for correctly. Ofgem's licence
wording turns on one act: the **charge recovery action**. That is a bill, or any other way of
seeking to recover charges, "including via a Prepayment Meter". The supplier "must only do so in
respect of units … which could reasonably be considered to have been consumed within the 12 months
preceding the date the charge recovery action was taken", plus standing and other supply charges
accrued in that window. [H] SLC 21BA.1, draft text, statutory consultation 16 Nov 2017, Appendix 2.

Three consequences follow from defining it by the *action*, not by the bill or the read.

1. **The 12 months run back from the date of the demand, not from the read and not from when the
   error was found.** [H] 21BA.1. The voluntary principle before May 2018 ran from "the error being
   detected and a corrected bill being issued". [H] Ofgem open letter, 3 Apr 2017, p.1.
2. **A statement is not a demand.** The Ombudsman's stance: "A direct debit statement is not charge
   recovery action … a supplier sending statements showing an increasing balance, even if these are
   based on accurate meter readings, does not amount to charge recovery action." A demand is a bill
   asking for payment, taking or raising a direct debit, or setting a debt recovery rate on a
   prepayment meter. [H] Energy Ombudsman, *Our backbilling stance* (supplier portal). Ofgem lists
   "accurately setting a customer's Direct Debit payments" as charge recovery action. [H] Ofgem open
   letter on SLC 21BA, 7 May 2020, p.1.
3. **Money taken counts as recovery.** If the payments taken covered the energy, nothing is barred,
   however wrong the bills were. Ombudsman Scenario B: no bills for 17 months, DD of £50 a month, a
   £7.43 credit when billing resumes. "Backbilling isn't applicable … Backbilling is not intended to
   refund customers' payments made for energy that they have used." [H] same stance page.

So **the quantity 21BA bars is not "the under-estimate".** It is the part of the customer's
*unrecovered* charges for energy used more than 12 months before the supplier first sought them.
For a customer who pays each bill on receipt, that comes to the same thing as the under-estimate.
For a direct-debit customer, it is the shortfall of collections against true charges. The
estimate's error matters only through the DD level.

Refunds are never limited: the condition "does not preclude a supplier from reimbursing consumers
for overcharging in the past, regardless of whether this was in the last 12 months". [H]
consultation, Appendix 3.

### The cases, kept apart

| # | Case | What has gone wrong | How it surfaces |
|---|---|---|---|
| B1 | **Estimate corrected by an actual read** | Bills on estimates under-stated use; a read arrives | A catch-up at the next actual read |
| B2 | **Meter never read** | B1 with a long gap: no access, a lost card, a locked cupboard, a landlord holding the key | A read or a meter exchange, often a **smart install** |
| B3 | **Billing-system failure** | The supplier had reads and did not use them, or sent no bills | The supplier finds the fault, or the customer complains |
| B4 | **Crossed meter** | The customer was billed on someone else's meter point | Usually the customer, or a neighbour's dispute |
| B5 | **New occupier never billed** | Supply ran on a deemed contract to someone the supplier never named | A name arrives, a debt trace, or a new account |
| B6 | **Direct debit set too low** | The account was billed, maybe on actual reads, but the DD collected less than the charges and was not raised | An annual DD review, a final bill, a switch |
| B7 | **Erroneous transfer returned** | Supply was wrongly switched away and comes back | The returning supplier bills the gap |
| B8 | **Prepayment debt not applied** | A debt or tariff was not loaded onto the meter | The supplier finds the missing debt |

All six cases the 2017 consultation published are B3, B5 or B8. In five of the six, the supplier
held reads or failed to bill or load a debt. None is a plain B2 no-access case. [H] consultation
¶2.3 and ¶2.9, case studies 1–6. That matters for §7: the complaint data the register has used as
evidence of **persistent non-reading** is at least partly evidence of **billing failure**, a
different mechanism.

---

## 2. Who is liable, case by case

**The rule.** From 1 May 2018 for domestic customers, and 1 November 2018 for microbusinesses, the
12-month limit applies in every case except four. [H] Ombudsman stance, which gives both dates. The
decision gives 56 days for Part A and six months more for Part B. [H] decision pp.13–14.

1. (a) The charge recovery action was taken before the condition took effect.
2. (b) A compliant demand was made and is being chased for non-payment.
3. (c) The supplier "has been unable to take a charge recovery action for the correct amount …
   due to obstructive or manifestly unreasonable behaviour" of the customer.
4. (d) Anything else Ofgem later specifies after consultation. None was found.

[H] 21BA.2. **The burden is the supplier's**, and it must keep evidence. [H] decision p.9; the
Ombudsman: "It is the supplier's responsibility to show the exception. The Energy Ombudsman will not
try to find this."

**What counts as obstruction.**
- **Counts:** theft; not keeping one's own meter in order; preventing physical access. The
  consultation's threshold is preventing "more than one reasonable attempt to gain access". [H]
  consultation ¶2.18–2.19.
- **Does not count:** "We do not consider a consumer to be obstructive or manifestly unreasonable
  when he or she does not supply a meter reading." [H] decision p.10. Nor does failing "to notice or
  report that they are being billed on estimates" (p.9). Nor does taking "all reasonable steps" to
  read under SLC 21B.4, which "is not an exception". [H] Ombudsman, *Reading the meter*.
- **Can count:** the Ombudsman's one worked exception. The supplier sends readers, writes four
  times, emails twice and phones, and warns the customer that "this could potentially result in a
  large balance". The customer still does not engage, so the supplier "could justify that there is
  an exception". [H] Ombudsman, *Exceptions*. **The warning is what moves it.**
- Ofgem expected customers dodging payment by passive non-cooperation "to be an issue in very few
  cases". [H] decision p.10.

| Case | Customer pays | Supplier bears | Industry (via settlement) | Status |
|---|---|---|---|---|
| B1 estimate corrected | Units used in the 12 months before the catch-up demand | Under-charged units older than that: their **revenue**. Their **wholesale cost** too, where settlement reconciles them (below) | Electricity energy settled past RF on an under-stated EAC goes into GSP group correction, shared across suppliers in the group | Rule [H]; settlement split [D]/[M] |
| B2 never read | As B1. All of it only if the supplier can evidence obstruction (21BA.2(c)) | As B1, usually larger. Gas is reconciled up to the line in the sand (AUGE: four years), so the supplier pays for gas it may only bill for 12 months | Gas read after the line in the sand stays in UIG ("no read at line in the sand", 55 GWh in 2024-25 [H] AUG table) | Rule [H]; settlement [M] |
| B3 billing failure | 12 months; nothing at all if payments taken covered the use (Scenario B) | Everything older and unrecovered | As B1 | [H] case studies; Ombudsman |
| B4 crossed meter | 12 months of their own meter's use, after correction | The rest; the customer is not at fault | Settlement was on the right meter points, so nothing to socialise unless reads were also missing | **GAP**: no source addresses crossed meters under 21BA. Liability inferred from the rule and the Ombudsman's erroneous-transfer stance [D] |
| B5 new occupier never billed | 12 months. A Deemed Contract is a "Relevant Contract" (21BA.6) | The rest, unless not telling the supplier is "manifestly unreasonable" | The occupier's use was settled to the supplier, so the supplier carries its wholesale cost | Deemed contract in scope [H]. **Whether silence on moving in is manifestly unreasonable: GAP.** Suppliers asked in 2017–18 (decision p.8, "has not told the landlord they are moving in or out") and Ofgem gave no further guidance (p.10) |
| B6 DD set too low | Shortfall within 12 months of the first demand: a DD increase or a bill | Shortfall older than that, **even with accurate bills** (Ombudsman Scenario A) | None: billing was not the problem | [H] Ombudsman; Ofgem consumer page; Ofgem 2020 letter |
| B7 erroneous transfer | 12 months | The rest. "A consumer's lack of action to rectify an erroneous transfer does not constitute obstructive or unreasonable behaviour" | — | [H] Ombudsman |
| B8 PPM debt not loaded | 12 months | The rest | — | [H] consultation ¶2.13, case study 3 |
| Theft / own meter not kept in order | All of it: the exception applies | Detection and back-assessment cost | Undetected theft: UIG / GSP correction | [H] consultation ¶2.18 |

**The direct-debit case, and Energy UK's reading.** Energy UK says back-billing "stops energy
suppliers legitimately billing energy customers for energy costs where after 12 months … The
customer's Direct Debit amount was previously set too low to cover any charges due". [H] *Energy UK
Explains: Back billing*, Feb 2025, p.1. That list matches Ofgem's own consumer page word for word.
[H] Ofgem, *What to do if you get a back bill*. Read alone, it looks wider than the licence text.
The Ombudsman's stance reconciles the two:
- A DD that was set too low and never raised means **no demand was made for the shortfall**.
- Statements showing the growing balance do not count as a demand.
- So once the supplier does raise the DD or bill the balance, shortfall older than 12 months is
  barred.

By 2019 the Ombudsman was already seeing exactly this failure: "Suppliers failing to apply a
backbilling reduction in situations where it'd failed to complete an accurate direct debit review
within a 12-month period." [H] Ombudsman Services, *Energy Sector Report 2019*, p.10. **This is the
link to SLC 27.15:** the DD must be set on "the best and most current information" [H] consultation
¶1.15. A DD review that does not seek the balance it finds lets that balance age past recovery.

**Microbusiness.** Part B from 1 November 2018 [H]. Before that there were voluntary standards of
three years (electricity) and four years (gas), with 12 of 17 signatories already at 12 months by
May 2016. [H] consultation ¶1.20, ¶2.10. Larger non-domestic customers are not protected.

**Before May 2018 (2016 to April 2018 of our window).** Ofgem's 2007 principle applied "if a
supplier is at fault", over the 12 months before the error was found. [H] open letter 2017. It was
written into Energy UK's Billing Code. Its signatories were the six largest suppliers, with 81% of
domestic gas and 83% of domestic electricity customers in Q1 2017. [H] consultation ¶2.43. The
"large majority" of other domestic suppliers also followed at least 12 months [H] decision fn 11,
and the Ombudsman applied the principle to all domestic cases [H] decision p.12. The Billing Code
closed in 2019. [H] Energy UK 2025.

**Where unbilled energy lands in settlement** ([D] from [M] mechanics, set out in
`unbilled_energy_and_revenue_assurance.md` §2 K6; the BSC and UNC text was not read this pass):
- **Electricity.** NHH volumes are reconciled at reads up to RF at 14 months. A settlement day that
  reaches RF without an actual read stays settled on its EAC, and any GSP-level difference is spread
  by GSP group correction. So under-charged energy **12–14 months** old is paid for in settlement but
  cannot be billed: the supplier loses revenue *and* carries the cost. Beyond RF the cost is
  socialised and the supplier loses only the margin.
- **Gas.** Reconciliation runs about four years (AUGE [H]), so the supplier pays for nearly all
  under-charged gas and can bill only 12 months of it. **For the same gap, gas exposure is larger
  than electricity's.**

---

## 3. Scale

| Year | Measure | Value | Source |
|---|---|---|---|
| 2012–2015 | Back-billing cases at Citizens Advice / Ombudsman | Chart only, rising; values not given as numbers | [H] consultation Fig. 1–2 (no table) |
| 2016 | Domestic back-billing cases | **>6,000** Citizens Advice Consumer Service (**>15%** of its cases); **>4,000** Ombudsman (**12%**) | [H] consultation ¶2.1 |
| 2016 | Microbusiness back-billing cases | **375** Citizens Advice, **399** Ombudsman, about 10% of each body's microbusiness cases | [H] consultation ¶2.7 |
| 2016 | Share of Citizens Advice back-billing cases at the six largest suppliers | **>60%** | [H] consultation ¶2.5 |
| 2016/17 | Median domestic back bill (complaints) | **£1,160**; median length **24 months**; extremes **>£10,000** (n = 203 CA cases, Oct 2016–Mar 2017, customer-reported) | [H] consultation ¶2.1 and fn 16 |
| 2016/17 | £ that should have been written off under a 12-month limit, CA consumers only | **£0.8m–2.3m a year**; Ofgem calls it a likely understatement | [H] consultation ¶2.2, ¶2.48 |
| 2015/16 | Households hit by large late bills | "As many as 2.1 million", averaging **£206**, 15% over £250 | [M] CA press release 29 Feb 2016, via `practitioner_questions_as_assumption_toggles.md` (quote read there; survey method not given) |
| H1 2017 | Domestic consumers with no accurate bill for over a year | **just over 7%** (CA data) | [H] consultation ¶1.1 |
| Q1/Q2 2017 | Median supplier (>5,000 accounts) with a read-based bill in the year | **94.80% / 94.40%** | [H] decision p.10 |
| Q2 2017 | Smart: domestic smart bills estimated; smart customers >6 months without an accurate bill | **6%** (range 4–24% by supplier, BEIS); **2.9%** (CA RFI) | [H] consultation ¶2.28 |
| 2012–13 | Microbusiness back bills (RFI) | Majority under 3 years and under £2,000; a minority over £20,000 or over 5 years | [H] consultation ¶2.8 |
| 2017 | Industry cost of the rule | "around £60m", one supplier's estimate (meter readers plus write-offs). **Ofgem did no impact assessment** under s5A Utilities Act | [H] decision p.12; consultation ¶2.41 |
| 2017 | Ombudsman | "Switching replaces back-billing as the hot topic"; no count given | [H] OS *Energy Sector Report 2017* |
| 2018–19 | Ombudsman | Inconsistent application after the licence change; DD-review failures; no count given | [H] OS *Energy Sector Report 2019* p.10 |
| 2020 | Supplier T&Cs | 63 domestic suppliers checked; all said they adhered; **34** had T&Cs that misstated the rule | [H] Ofgem letter 7 May 2020 |
| 2020–2023 | Ombudsman back-billing count | **GAP**. Annual reports name back-billing among the top five categories; counts not given | [H] TAG ARs 2024–25 |
| 2024 | Ombudsman back-billing cases | **3,238** (of 92,938 accepted cases, ≈3.5% [D]) | [H] EO *Annual data 2025* |
| 2025 | Ombudsman back-billing cases | **3,216** (of 80,256 accepted, ≈4.0% [D]); billing overall 56%; 71% of all cases upheld (not back-billing-specific) | [H] same; TAG AR 2025 |
| 2024 | Energy UK | back-billing "only 4–5% of total complaints to the Energy Ombudsman" | [H] Energy UK Feb 2025 |

**What the ratios count.** The 3.5% and 4.0% are back-billing cases over all accepted cases in the
same year: one count over another in the same scheme. The Ombudsman also says "as many as 75% of
consumers who could use Energy Ombudsman do not do so" [H], so escalations are a lower bound on
disputes, and disputes are a lower bound on back bills.

**Around the 2018 change.** Ofgem expected the rule to bring "a significant decrease in cases".
[H] consultation ¶2.37. Ombudsman back-billing cases went from **>4,000 in 2016 to ~3,200 in
2024–25**, while total Ombudsman cases roughly doubled over the crisis. These are two endpoints with
no series between them. They cannot separate the rule from smart meters, the crisis or the Billing
Code's closure: **I cannot attribute the fall.**

**Not established (GAP):**
- how many back bills are issued a year;
- their size distribution across the population (only the complaint median is published);
- how much revenue suppliers write off under 21BA, by supplier or in total;
- what share of back bills carry any write-off;
- the 2017–2023 Ombudsman series.

No supplier disclosure of 21BA write-offs was found. Centrica's 2024 accounts, read in the sister
document, report unread revenue and provisions but not 21BA write-offs.

**Scale against our book.** [D] 3,216 escalated back-billing disputes in 2025, over roughly 28–29m
GB domestic households [M], is about 1 per 9,000 households a year. A 175-account book would expect
about 0.02 escalated disputes a year. **Escalations cannot be observed at our book size.** Any
back-billing figure the company publishes must be in barred energy and money, not complaints.

---

## 4. What a supplier sees, and what it must decide

**Sees (its own books):**
- every bill, its basis (actual, customer or estimated read) and its date;
- every read and its source;
- every payment taken, the DD amount and its review dates;
- every charge recovery action and its date;
- its own record of access attempts and warnings, which is the only evidence that can carry
  21BA.2(c);
- at an actual read, the **register advance over the whole unread run**.

**From the industry:** EAC/AQ for its points; its settled volumes per run and the reconciliation
charges.

**Does not see:** true use in each month between reads. So it must *apportion* the advance to say
which units "could reasonably be considered" to fall inside the 12 months. The licence asks for a
reasonable apportionment, not a day count. The natural one is the supplier's own consumption profile.

**Decisions, and what the rule does to each:**
1. **When to read.** SLC 21B.4 requires all reasonable steps to read at least once a year [H]. The
   rule turns that into a money cliff. Once an account has been unread for more than 12 months,
   each further month bars about one more month of any under-charge. So **the value of a read is
   concentrated on accounts approaching 12 months unread**, and on accounts whose DD sits below
   their use.
2. **When to estimate, and how.** Every unread period. Under-estimates are cheap inside 12 months
   and lost beyond them. A biased-low method costs money only on long gaps.
3. **When to bill the catch-up.** At once. **Each month a found under-charge goes unbilled moves a
   month of it out of the window.** [D] from 21BA.1.
4. **What a DD review must do.** Seek any balance it finds (a DD increase or a bill) inside 12
   months. A review that only resets the DD to forward use leaves the balance unsought.
5. **How far back.** Twelve months from the demand. Further only on evidence of an exception. The
   decisive evidence is documented access attempts **with a warning of the consequence**.
6. **Whether to treat a long gap as obstruction.** Only with that evidence. The Ombudsman decides
   against a supplier that cannot tie its conclusion to one of the four exceptions.

---

## 5. What our code does (discovery)

| Element | Where | Verdict |
|---|---|---|
| The 12-month cap | `company/billing/back_billing.py` (`BackBillingAssessment`, 365 days back from `billing_date`, start 2018-05-01) | **Right** for a domestic pay-on-receipt catch-up. Anchored on the bill date, as 21BA.1 is |
| Microbusiness | Same module, `is_microbusiness` | **Wrong start date**: Part B starts **2018-11-01**, but the module applies 2018-05-01 to both. No caller sets `is_microbusiness` yet (`obligations_register.microbusiness_back_billing_cap`) |
| Before May 2018 | `cap_applies` returns False before 2018-05-01 | **Too harsh to customers.** The voluntary principle applied to 81–83% of the market and was applied by the Ombudsman. New toggle `q2_pre_2018_voluntary_cap_coverage` (§7) |
| Which units are barred | `barred_fraction` apportions the run **by days** | **Approximate.** 21BA asks for units "reasonably considered" consumed in the window. The company already holds a published monthly profile (`company/billing/unread_month_estimate.py`). A winter-heavy gas run split by days misplaces the boundary units |
| The comparator | `monthly_bill_assembly._resolve_catchup` writes off `(true − estimated bills) × barred_fraction`, for **every** payment method | **Wrong for direct debit.** Under the Ombudsman's Scenario B, payments taken are charge recovery. A DD account whose collections covered its use has nothing barred, yet the code writes off. Under Scenario A, a DD account billed on **actual** reads, with a shortfall not sought within 12 months, has the old shortfall barred, yet the code writes off nothing, because there was no estimate to correct |
| DD review | `company/billing/dd_review.review` sets the DD from forward annual spend, ±5% band | **Does not seek the balance.** It never makes a charge recovery action for the accumulated shortfall, so under 21BA that shortfall ages out after 12 months. Whether any other path (final bill, `dd_collections_desk`) seeks it was **not traced**. No module applies 21BA to a DD balance (grep: no `21BA` or back-billing reference in `dd_review*`, `dd_balance_book`, `dd_collections_desk`) |
| Compliance gate | `company/compliance/domain_invariants.check_back_billing_cap_respected` | Re-derives the same days-based, estimate-based test. **It inherits the comparator defect.** It is green on a DD account where 21BA bars nothing, and silent on Scenario A |
| The read process | `simulation/meter_reads.py` (two classes, easy rate solved to `q2_no_read_12m_share`, no forced read) | **Right shape**, and it now lets the cap bind. The hard class stands for *no access*. **Billing failure (B3), the main source of the published complaint cases, is not a read process** and is absent. Our own company never fails to bill |
| Energy measure | `company/billing/billing_accuracy.py` (K3 barred kWh, D48) | Measures barred energy on the estimate comparator. Decade run: 1.05% (electricity) and 1.25% (gas) of undercharge kWh barred, 17 and 6 barred true-ups (`unbilled_energy_and_revenue_assurance.md` §5). **No published comparator exists** (§3 GAP) |
| Deemed / unnamed occupier | `sim/customer_state_layer.py` `unnamed_kwh_expected` (W2_36 slice 3); billed from the move date (B7 slice 3), the window booked as occupier debt (B7 slice 4) | Billed, not collected. 21BA applies to the deemed leg (21BA.6). The default unnamed spell (`q1_unnamed_months_per_cot` = 3, high 6) sits inside 12 months, so it bites only in the tail |
| Settlement side | `EP5_settlement_true_ups` 0/3 | Barred energy is a revenue loss only. The 12–14-month electricity band and the gas reconciliation window, where the supplier pays for energy it may not bill, do not reach cost |
| Theft | `company/billing/revenue_protection_register.py` (3-year back-bill) | Consistent with the theft exception. The world generates no theft (sister doc K4) |

---

## 6. Gaps

**Knowledge not established (searched, or not reachable this pass):**
1. Population counts and sizes of back bills, and £ written off under 21BA, 2016–2025 (§3).
2. Ombudsman back-billing counts for 2017–2023.
3. **Whether a bill addressed to "The Occupier" is a charge recovery action** against an occupier
   named later. It decides how much of B5 the rule bars. **Practitioner question.**
4. **Whether a normal annual DD review seeks the balance** (raises the DD to recover arrears) or only
   resets to forward use. It decides how much of B6 arises in a well-run supplier. **Practitioner
   question.**
5. How often suppliers successfully invoke 21BA.2(c) (obstruction) in practice. Ofgem says "very
   few"; no count exists.
6. Crossed meters under 21BA: no published treatment; liability here is inferred.
7. The final made text of SLC 21BA (only the draft and the decision were read; the decision says only
   Part B's timing changed).
8. Share of smart meters in the 2017 base behind the 7% (needed to restate it for traditional meters
   only; §7).
9. BSC/UNC text on reconciliation cut-offs (RF/DF; the gas line in the sand). Used here as [M].

**Commons gap:** `docs/domain_artefact_library/regulatory/` still has no SLC 21BA artefact. The
draft text in Appendix 2 of the 2017 consultation, with the dates from the decision and the
Ombudsman, would make one.

**Code gaps, in the order other work rests on them:**
1. The barred amount uses the wrong comparator for DD customers, and DD balances carry no 21BA at
   all (§5). The compliance invariant has the same defect.
2. The DD review never seeks a balance, so it cannot make the charge recovery action the rule
   expects.
3. Units are apportioned by days, not by the company's own profile.
4. The microbusiness start date is wrong, and the voluntary regime before 2018 is missing.
5. The deemed-occupier leg (B7 slice 3), when built, must carry 21BA.
6. Barred energy does not reach settlement cost (EP5).

---

## 7. Toggles set

| Toggle | Old | New | Basis |
|---|---|---|---|
| `q2_no_read_12m_share` | 0.07 (0.054–0.07) | **0.07 (0.054–0.08)** | Default and low unchanged ([H] consultation ¶1.1; decision p.10). **High raised.** The world applies the share to read-exposed traditional meters, but Ofgem's 7% is over all domestic consumers, and smart customers were read far better (only 2.9% went more than 6 months without an accurate bill, [H] ¶2.28). For a smart share s of the base, the traditional-only share is about 0.07/(1−s); for s ≤ 0.15 that is ≤ 0.082 [D]. s is [M], unverified (gap 8) |
| `q2_persistent_unread_share` | 0.01 (0–0.03) | **0.01 (0–0.03), basis restated** | Values kept; the evidence for the default is weaker than the register said. The complaint median of 24 months is real [H]. But every published case study behind it is a billing failure, an ignored read, or a debt not loaded, not a no-access meter (§1). So the 24-month evidence argues for a **billing-failure mechanism** at least as much as for persistent non-reads. The no-access class is still evidenced qualitatively: locked cupboards, landlords holding keys (decision p.8) |
| `q2_mean_under_estimate_on_a_catch_up` | 0.10 (0.05–0.20) | **0.10 (0.05–0.20), meaning narrowed** | Values kept. Since D48 slices 3–4 the company makes the estimate, so this is a **check on the company's estimator**, not a world input; no code reads it (grep). And it sets barred revenue **only for customers who pay on receipt**. For DD customers the barred quantity is the collection shortfall older than 12 months (Ombudsman Scenarios A/B) |
| **new** `q2_pre_2018_voluntary_cap_coverage` | — | **0.83 (0.0–1.0)** | Share of domestic catch-ups billed before 1 May 2018 to which a 12-month limit applied. Default: signatory share of domestic electricity, Q1 2017 [H] ¶2.43. Low: the code's current behaviour, treating estimate under-reads as not the supplier's fault. High: the Ombudsman applied the principle to all domestic cases [H] decision p.12, and most non-signatories followed it [H] fn 11 |
| **new** `q2_obstruction_exception_share` | — | **0.0 (0.0–1.0)** | Share of the persistent-unread class whose gap would qualify under 21BA.2(c) **if the company has documented repeated access attempts and a warning**. Default: Ofgem's "very few cases" [H] decision p.10; not supplying reads is not obstruction [H]. High is a bound only. It is conditional on a company action the code does not yet take (logging attempts and warnings) |

**A toggle not added: "the share of back-bills written off under the limit".** That share is an
**output** of the world's read process and the company's billing and DD behaviour, not an input.
No published value exists to calibrate it against (§3 GAP 1). It belongs on the D48 page as a
measured figure with its interval, not in the register as a dial.

---

## 8. What this says about the order of work

1. **Fix the comparator before any further measurement of barred revenue.** This is company-side,
   needs no world change and no new number, and decides what every back-billing figure means.
   - Give each account a **date of last charge recovery action**: a bill demand, a DD taken or
     raised, a PPM recovery rate.
   - Bar the part of the **unrecovered** balance that relates to units used more than 12 months
     before the next action.
   - For pay-on-receipt accounts this reproduces today's figure. For DD accounts, which are most of
     the credit book [M], it removes write-offs that are not owed (Scenario B) and adds the ones the
     code misses (Scenario A).
   - `check_back_billing_cap_respected` must move with it, or it will red on the correction.
2. **Then make the DD review seek the balance it finds**, inside 12 months. That is the
   SLC 27.15 / 21BA link the Ombudsman saw suppliers fail in 2019. It shares one definition of
   "charges due" with the debt work (`debt_and_collections.md`). **Ask the director gap 4 first**:
   whether a normal review raises the DD to recover arrears is practitioner knowledge, and it
   decides the design.
3. **Cheap corrections, in passing:**
   - apportion barred units by the company's own profile;
   - Part B from 2018-11-01;
   - read `q2_pre_2018_voluntary_cap_coverage` for 2016 to April 2018.

   Each one moves the measured barred share. Measure each against the current figure **one variable
   at a time**, and write the predicted direction down first.
4. **B5 waits for B7 slice 3**, and for the director's answer on gap 3.
5. **EP5 carries 21BA's cost side.** The 12–14-month electricity band, and gas up to the line in the
   sand, are where the supplier pays for energy it cannot bill.
6. **Billing failure (B3) is not a world mechanism.** It is the company's own. Our company bills
   perfectly by construction. If the evidence of large, long back bills is mostly B3, then the
   world's persistent-unread class is not the right place to reproduce it. That is a reason to keep
   π small, not to raise it.

Nothing found argues for the read rate (`q2_no_read_12m_share`) as the next lever. Calibration of
reads is done to the published moment. The open error is in **what the company counts as barred**.

---

## Sources

- Ofgem, *Open letter – notifying of our intention to launch a project to protect consumers from
  back billing*, 3 Apr 2017, with annex of supplier smart back-billing limits:
  <https://www.ofgem.gov.uk/system/files/docs/2017/04/open_letter_backbilling_new_project.pdf> [H]
- Ofgem, *Protecting consumers who receive backbills – Statutory Consultation*, 16 Nov 2017
  (incl. draft SLC 21BA and annotated policy intent):
  <https://www.ofgem.gov.uk/system/files/docs/2017/11/protecting_consumers_who_receive_backbills_-_statutory_consultation.pdf> [H]
- Ofgem, *Modification of the electricity and gas supply licences to introduce rules on backbilling*
  (decision), 5 Mar 2018:
  <https://www.ofgem.gov.uk/sites/default/files/docs/2018/03/backbilling_final_decision_policy_document_-_march_5_-_website.pdf> [H]
- Ofgem, *Expectations for energy suppliers and insolvency practitioners … when undertaking charge
  recovery action* (SLC 21BA open letter), 7 May 2020:
  <https://www.ofgem.gov.uk/sites/default/files/docs/2020/05/open_letter_slc_21ba.pdf> [H]
- Ofgem, *Supply licence guide: Metering, billing and payments*, Feb 2019:
  <https://www.ofgem.gov.uk/sites/default/files/docs/2019/02/licence_guide_metering_billing_and_payments_1.pdf> [H]
- Ofgem, *What to do if you get a back bill*:
  <https://www.ofgem.gov.uk/information-consumers/energy-advice-households/what-do-if-you-get-back-bill> [H]
- Energy UK, *Energy UK Explains – Back billing*, Feb 2025:
  <https://www.energy-uk.org.uk/wp-content/uploads/2025/02/Energy-UK-explains-back-billing-February-2025.pdf> [H]
- Energy Ombudsman, *Our backbilling stance* (supplier portal):
  <https://portal.energyombudsman.org/resources/our-backbilling-stance> [H]
- Energy Ombudsman, *Annual data 2025* (20 Mar 2026) and *H1 data 2026*:
  <https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025> [H]
- Ombudsman Services, *Energy Sector Reports* 2017, 2018, 2019; Trust Alliance Group *Annual
  Reports* 2024, 2025, via <https://www.energyombudsman.org/reports-and-data/annual-reports> [H]
- Citizens Advice press release, 29 Feb 2016 (2.1m households, £206) [M], via
  `practitioner_questions_as_assumption_toggles.md`.
- Repo documents relied on: `unbilled_energy_and_revenue_assurance.md` (settlement, UIG, Centrica),
  `practitioner_questions_as_assumption_toggles.md` (Q2 derivations), `debt_and_collections.md`,
  `elexon_settlement_run_timetable_verified.md`.
