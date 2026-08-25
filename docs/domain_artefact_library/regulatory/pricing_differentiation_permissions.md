# What a GB supplier may and may not differentiate a price on — permissions register

**Type:** REGULATION COMMONS artefact. The regulatory TEXT is a shared commons readable by every
lane, because law is published in reality (`docs/design/REGULATION_COMMONS_DOCTRINE`). Each
lane's *reading* of it stays independently owned; what is recorded here is the text and the
citation, not an interpretation anyone is bound to.

**Why it exists.** Director, 2026-08-25, verbatim:

> "Real suppliers already differentiate on payment risk. Direct debit discounts exist and are
> permitted; the cap itself sets separate levels for direct debit, standard credit and prepayment
> because the costs genuinely differ. Withholding a low-margin fixed tariff from a credit risk is
> ordinary practice. ... So the shape isn't 'never price up a vulnerable household'. It's that
> pricing follows expected cost — and default risk, collections cost and bad debt are part of
> that cost. Put them inside the EV arithmetic and let the answer emerge rather than imposing a
> floor. Establish what's actually allowed rather than assuming ... Record what is explicitly
> permitted, what is prohibited, and what is tolerated-but-unwritten, with citations. That
> register is what the pricing arm should be constrained by — not my recollection and not yours."

**Primary sources read, not recalled.** Every quotation below is from the document named against
it, fetched and extracted 2026-08-25. Where a claim could not be sourced it is marked
`UNSOURCED` and carries no citation rather than a plausible one.

| # | source | what was read |
|---|---|---|
| S1 | Ofgem, *Electricity Supply Standard Licence Conditions, consolidated to 1 August 2025* (611pp PDF, ofgem.gov.uk/sites/default/files/2025-08/Electricity-Supply-Standard-Consolidated-Licence-Conditions.pdf) | SLC 0, SLC 7, SLC 7A, SLC 27, SLC 27A — quoted verbatim |
| S2 | Late Payment of Commercial Debts (Interest) Act 1998 s.5A, s.6 (legislation.gov.uk/ukpga/1998/20) | fixed compensation sums; rate-setting power |
| S3 | Late Payment of Commercial Debts (Rate of Interest) (No. 3) Order 2002 (legislation.gov.uk/uksi/2002/1675) | 8% over the Bank of England official dealing rate |
| S4 | Ofgem, *Energy price cap* (ofgem.gov.uk/energy-price-cap) | the cap sets different levels by payment method |
| S5 | Ofgem, *Compliance note — adherence to SLCs 0 and 27* | SLC 27.1 applies above 50,000 domestic customers |

S1 carries Ofgem's own caveat and it is repeated here rather than dropped: *"Consolidated
conditions are not formal Public Register documents and should not be relied on."* For anything
load-bearing, the Public Register version governs.

---

## A. EXPLICITLY PERMITTED

### A1 — Charging different prices by payment method, **to the extent of the cost difference**

> **SLC 27.2A** — "Any difference in terms and conditions as between payment methods for paying
> Charges for the Supply of Electricity shall reflect the costs to the supplier of the different
> payment methods." (S1)
>
> **SLC 27.2B** — "In this condition, 'terms' means all terms on which a supply of electricity is
> offered or provided, **including terms as to price**, which significantly affect the evaluation
> of that supply." (S1)

This is the load-bearing permission and it is a **two-sided constraint**, not a licence to
differentiate freely. Price differences between payment methods are lawful *and* they are capped
at the cost difference. A direct-debit discount larger than the cost saving is as much a breach
as an unjustified prepayment premium.

**The cap is built the same way.** Ofgem sets different cap levels for Direct Debit, standard
credit and prepayment (S4), with a levelisation allowance equalising the prepayment and Direct
Debit standing charge. So the regime does not merely tolerate payment-method differentiation, it
codifies it.

### A2 — Statutory interest and fixed recovery costs on a **non-domestic** late debt

> **s.5A** — "for a debt less than £1000, the sum of £40; for a debt of £1000 or more, but less
> than £10,000, the sum of £70; for a debt of £10,000 or more, the sum of £100" (S2), plus the
> excess of reasonable recovery costs over that fixed sum.
>
> **Rate** — "the official dealing rate of the Bank of England in force at the time when late
> payment interest becomes payable **plus 8 per cent**", fixed by reference to the rate in force
> on the preceding 30 June or 31 December (S3).

Statutory, not discretionary: it is an implied contract term and cannot be excluded. It applies
to **qualifying commercial debts** — business to business. It does **not** reach a domestic
customer.

### A3 — Requiring a security deposit from a domestic customer, within limits

> **SLC 27.3** — a licensee "must not require a Domestic Customer to pay a Security Deposit" if
> the customer agrees to a prepayment meter and it is safe and reasonably practicable, "or if it
> is unreasonable in all the circumstances of the case to require that customer to pay". (S1)
>
> **SLC 27.4** — "A Security Deposit must not exceed a reasonable amount." (S1)

So a deposit is permitted, gated on a prepayment alternative and a reasonableness test.

---

## B. PROHIBITED

### B1 — Any payment-method price difference **larger than the cost difference**
The other edge of SLC 27.2A (S1). Ofgem has run an enforcement investigation specifically under
27.2A (S5's sibling notice of decision), so this is enforced and not merely stated.

### B2 — Restricting the *availability* of payment methods
> **SLC 27.1** — the licensee "must offer the customer a wide choice of payment methods ... and
> those methods must include ... payment by cash ... and payment in advance through a Prepayment
> Meter". (S1)

Applies where the licensee supplies **more than 50,000** domestic customers (SLC 27.2(b), S5).
Ofgem's compliance note names as detriment "restricting payment method access to specific
customer groups" (S5). **Withholding a PRODUCT is not withholding a payment METHOD**, and the
director is right that withholding a low-margin fixed tariff from a credit risk is ordinary
practice — nothing read here prohibits it. But it must not become a route to denying a payment
method the licence requires be offered.

### B3 — Charging for the payment-difficulty services themselves
> **SLC 27.5A** — "the licensee must not charge the Domestic Customer for providing the
> facilities or information set out in paragraph 27.6." (S1)

So the forbearance machinery is free. The debt is still owed; the *support* cannot be a revenue
line.

### B4 — Deemed contract terms that are "unduly onerous"
> **SLC 7.3** — "The licensee must take all reasonable steps to ensure that the terms of each of
> its Deemed Contracts are not unduly onerous." (S1)
>
> **SLC 7.4** — a term is unduly onerous for a class of customers if the revenue from that class
> "significantly exceeds the licensee's costs of supplying electricity to such premises; **and**
> exceeds such costs ... by significantly more than the licensee's revenue exceeds its costs of
> supplying ... the generality of its Domestic Customers or ... Non-Domestic Customers". (S1)

**This is a margin test with a comparator, and it is the closest thing in the licence to a
direct constraint on a value-based pricing arm.** It does not forbid a higher margin; it forbids
a *class* margin significantly above the book's general margin, on a deemed contract. It applies
to domestic AND non-domestic classes.

> **SLC 7.6** — on a Deemed Contract "the licensee must not charge the Customer a Termination
> Fee." (S1)

### B5 — Terminating or re-terming a microbusiness mid-contract because it stopped qualifying
> **SLC 7A.3** — the licensee "must not include a term ... which enables it to terminate the
> Contract or apply different terms and conditions to that Contract during a fixed term period
> on the grounds that the Customer no longer satisfies the definition of Micro Business
> Consumer." (S1)

Note **SLC 7A.1**: for any non-domestic contract the supplier must either take all reasonable
steps to identify whether the customer is a microbusiness, **or deem it to be one** (S1). The
cheap path is the protective one.

---

## C. REQUIRED — duties that bind the arithmetic rather than forbidding an outcome

### C1 — Ability to pay must be ascertained and used, when setting instalments
> **SLC 27.8** — "The licensee must take all reasonable steps to ascertain the Domestic
> Customer's ability to pay and must take this into account when calculating instalments". (S1)
>
> **SLC 27.8A(a)(ii)** — credit management policies must include "**Linking staff incentives to
> successful customer outcomes not the value of repayment rates**". (S1)

27.8A(a)(ii) is the sharpest sentence in this register for a machine that optimises. It is a
prohibition on incentivising *collection value* over *customer outcome*, written for humans and
applying with more force to an optimiser. An arm that maximises recovery is exactly the
incentive this paragraph forbids attaching to a person.

**Scope, stated precisely: 27.8 governs INSTALMENTS, not the unit rate.** It is a debt-repayment
duty, not a pricing duty. Reading it as "never price up a struggling customer" — which is what
the current backstop does — is a reading the text does not support.

### C2 — Proactive contact on a trigger the supplier can compute
> **SLC 27.5B** — proactive contact "no later than after: (a) two consecutively missed monthly
> scheduled payments; or (b) one missed quarterly scheduled payment; or (c) a customer has
> informed the licensee that they are unable to make the next scheduled payment." (S1)

A hard, checkable trigger, and one this simulation can evaluate from its own payment ledger.

### C3 — Standards of Conduct, and the vulnerability limb
> **SLC 0.3** — the licensee must "behave and carry out any actions in a Fair, honest,
> transparent, appropriate and professional manner", provide information that "does not create a
> material imbalance in the rights, obligations or interests of the licensee and the Domestic
> Customer **in favour of the licensee**", and in relation to customers in Vulnerable Situations
> "seek to identify each Domestic Customer in a Vulnerable Situation" and apply (a)–(c) "in a
> manner which takes into account any Vulnerable Situation". (S1)

Note **SLC 0.6**: standard condition 0 does not apply to non-domestic supply "apart from any
matters relating to Deemed Contracts" (S1).

### C4 — Self-disconnection duties (prepayment)
> **SLC 27A.1** — where a domestic customer uses a prepayment meter, take "all reasonable steps
> to identify on an ongoing and continuous basis, whether that Domestic Customer is
> Self-Disconnecting", and if so offer appropriate support. **SLC 27A.2** — offer Emergency
> Credit and Friendly-hours Credit. **SLC 27A.5** — offer Additional Support Credit to a
> vulnerable customer who has self-disconnected or self-rationed. (S1)

---

## D. TOLERATED BUT UNWRITTEN — practice with no citation found

Recorded separately and honestly. Each of these is something the director named or that follows
from the sources, for which **no prohibition and no explicit permission was found in the text
read**. They are the cases where a supplier's judgement, not the licence, is the constraint.

| D# | practice | status after reading the sources |
|---|---|---|
| D1 | Withholding a low-margin **fixed** tariff from a poor credit risk | No prohibition found. SLC 27.1 governs payment METHODS, not products. Constrained in practice by SLC 0.3 (fairness, no material imbalance in the supplier's favour) and by the SLC 7.4 comparator if the customer ends up on a deemed contract. |
| D2 | Pricing a **higher expected default cost** into the unit rate of a credit-risk customer | No prohibition found for a contract price. SLC 27.2A binds only differences BY PAYMENT METHOD; SLC 7.4 binds deemed contracts. UNSOURCED whether Ofgem has taken a view on risk-priced domestic fixed tariffs — none was found. |
| D3 | Charging a **domestic** customer late-payment interest | The 1998 Act does not reach domestic debt (S2 — qualifying commercial debts). No affirmative permission found in the licence; treat as not available. |
| D4 | A prepayment premium | Now largely closed by the cap's levelisation of the prepayment standing charge (S4), which is a cap mechanic rather than a licence prohibition. |
| D5 | Withdrawing a discount when a direct debit fails | No prohibition found; falls under SLC 27.2A cost-reflectivity if it is framed as a payment-method difference. |

---

## E. WHAT THIS SIMULATION CANNOT CURRENTLY EXPRESS — a fidelity gap this register exposes

`docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json` carries **one
level per fuel per window**. The real cap sets **different levels for Direct Debit, standard
credit and prepayment** (S4).

So the world's cap cannot express the payment-method differential that the licence explicitly
permits and the cap itself codifies. Any company-side arm that prices on payment method is
today bounded by a ceiling that does not know payment methods exist. That is a world-side
fidelity gap, it is named here rather than worked around, and it belongs to whoever next touches
the cap artefact.

---

## F. HOW THE PRICING ARM MUST USE THIS

1. **Expected cost, not a floor.** Default risk, collections cost and bad debt belong inside the
   EV arithmetic. Nothing read here forbids a price that reflects them; C1 constrains
   INSTALMENTS, not the unit rate, and the current vulnerability backstop is a stronger rule than
   the text supports.
2. **SLC 27.2A is a two-sided constraint on payment-method differences** — at least as much a
   ceiling on a direct-debit discount as on a prepayment premium.
3. **SLC 7.4 is the margin test with teeth**, and it has a comparator: a class margin
   significantly above the book's general margin, on a deemed contract, is unduly onerous. An arm
   that prices a class far above the book should expect to meet it.
4. **SLC 27.8A(a)(ii) is the sentence to re-read before optimising collections**: incentives must
   attach to customer outcomes, not the value of repayment rates.
5. **Non-domestic is a different regime**: statutory interest at base + 8% and fixed recovery
   sums are available there and nowhere else.

**Supersession.** A newer consolidated licence, or the Public Register text, supersedes this
file. Anything here that a later reader cannot verify against a named source should be deleted
rather than kept — a register that outlives its citations is worse than none.
