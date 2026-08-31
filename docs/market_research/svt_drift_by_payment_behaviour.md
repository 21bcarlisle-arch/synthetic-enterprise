# Does a domestic account's payment record predict whether it leaves the default tariff?

Researched 2026-08-31, for `company/crm/churn_desk.estimate_svt_drift` v2. Opened by
`WORKER_PREREGISTRATION_WHAT_THE_SVT_DRIFT_BELIEF_V2_MUST_SHOW_2026-08-31.md`.

**Short answer: the DIRECTION is established and the MAGNITUDE is not.** Only the direction is used.
This file exists so that the difference between those two sentences is on the record rather than in
the head of whoever wrote the constant.

## The question, and why it had to be asked before a line was written

The SVT belief needed an observable that varies across households **at the same instant**. Payment
method, arrears, payment failures, account age, meter type and prior switching history were the
candidate set. The rule here is that a number you need is a question to research, never a value to
pick — so the question is what a real GB domestic supplier holds, and what the published record says
about its relationship to leaving.

## What a GB domestic supplier actually holds on an SVT account

Uncontroversial and not really a research question — these are the supplier's own systems, not an
inference about the customer:

- **Payment method** (Direct Debit / standard credit / prepayment) — a contractual field.
- **Payment outcomes**: whether each bill was paid on time, paid late, or the Direct Debit was
  returned. Direct Debit returns arrive as an explicit **Bacs ARUDD** report; a missed
  standing-order or prepayment top-up arrives only as the *absence* of an expected remittance
  (`simulation/payment_seam_adapter.py` documents that asymmetry and this repo already models it).
- **Arrears balance and ageing**, and any repayment arrangement (SLC 27.8).
- **Account age, meter type, tariff history** — all its own records.

This is the same channel the fixed-term belief already uses:
`CustomerExperienceDesk.observe_payment` → `RenewalObservation.behaviour_score`. v2 joins the SVT
route to an existing legal door rather than opening a second one.

## The direction: ESTABLISHED

An indebted domestic customer is **materially less able to leave**, and the mechanism is regulatory
rather than behavioural:

- **Domestic debt objections.** A supplier may object to the transfer of a domestic customer who
  owes it money. Ofgem, *Decision on review of domestic objections* (2016) and its accompanying
  impact assessment, are the governing publications.
- **Debt Assignment Protocol.** Indebted prepayment customers switch through the DAP rather than
  freely, with a debt threshold above which the switch is blocked outright.

An objection legally stops the transfer, so the direction is not in doubt: **worse payment record →
lower probability of drifting off the default tariff.** Ofgem's own engagement work points the same
way — the most inert segment is also the least able to pay — which is why §4 of
`svt_rates_active_passive_2016_2025.md` gives *"Ofgem engagement surveys: most inert segment"* as
the basis for its lowest band.

## The magnitude: NOT ESTABLISHED, and the attempt failed in a way worth recording

**Both Ofgem source PDFs refused text extraction.** `impact_assessment_on_review_of_domestic_
objections.pdf` and `decision_on_review_of_domestic_objections.pdf` both returned compressed stream
data rather than readable text on 2026-08-31.

A web-search summary offered several specific figures — a proportion of indebted-customer transfers
completing without objection, an average debt of debt-blocked customers by year, and a completion
rate for indebted prepayment switches. **None of them is quoted, cited or used anywhere in the
code**, because none could be checked against the source document. A citation that cannot be
checked is this project's own recorded defect class
(`WORKER_FINDING_THE_STANDING_CHARGE_IS_FOUR_DECLARATIONS_AND_A_CITATION_THAT_CANNOT_BE_CHECKED_
2026-08-31.md`), and a figure carried at second hand from a search summary is exactly that.

**Also not published, separately and more importantly:** no source found gives a within-band
structure for the SVT drift rates — nothing says where inside 15–20% a particular kind of account
sits. So there is no magnitude to source even if the debt figures had been readable.

| what | status | used in code? |
|---|---|---|
| Supplier may object to an indebted domestic customer's transfer | **Established** (Ofgem 2016 decision) | Direction only |
| Indebted PPM switches run through the DAP | **Established** | Direction only |
| Proportion of indebted transfers objected to | **Not established** — PDF unreadable, search summary uncheckable | **No** |
| Average debt of debt-blocked customers | **Not established** — same | **No** |
| Within-band position of an account by payment record | **Not published anywhere found** | **No** |

## What the code does with this, and why it is honest

`estimate_svt_drift` spreads the five payment grades **evenly** across the published band. Even
spacing is the uninformative choice where nothing establishes a structure, and it has a property
that makes it safe: the belief is graded by a **ranking** statistic within a band, so every
strictly-monotone spacing produces an identical verdict. The spacing cannot have made the result.

The middle grade and an absent payment record both return the band midpoint — the exact value v1
used — so the new term changes the answer only where the company genuinely knows something.

## What would close the gap

A readable extraction of the 2016 Ofgem objections impact assessment, giving objection rates by debt
level; or any published cross-tabulation of default-tariff tenure against payment method. Ofgem's
Retail Market Indicators publish default-tariff stock and switching counts, but the default-tariff
engagement panel this repo already cites is explicitly **non-prepayment domestic accounts**
(`ASSUMPTIONS.md` line ~176) — so the published series excludes the payment group where the effect
should be largest. That exclusion is itself worth knowing and is the most likely reason no
payment-method split of the SVT band exists to be found.
