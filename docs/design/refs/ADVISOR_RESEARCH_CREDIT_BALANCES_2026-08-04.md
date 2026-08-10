# [ADVISOR-RESEARCH] — Customer credit balances: the rules, the failure mode, and what the C7 defect is a symptom of (2026-08-04)

**Type:** [RESEARCH]. External sourcing the machine cannot do (no web access). Prepared while Skynet was down, so it is waiting on restart. Findings, not instructions — where it says "should", judge it and argue back if the code says otherwise.

## 0. Why this matters more than one bad ledger row

The director found a **−£202 "invoice"** on C7 dated 2018-08-01 that never clears: every subsequent payment returns the balance to exactly −£202 for three and a half years. The account sits in permanent credit and **nothing ever returns it.**

The real finding is not the row. It is that **the model can accumulate customer credit and has no path to release it.** That is precisely the mechanism at the centre of the 2021 UK supplier collapse, so this is a fidelity gap in the most load-bearing part of the commercial story, not a billing cosmetic.

Note also: the on-page reconciliation **passes** — collected + outstanding = billed — *because the credit note nets into "billed"*. The control is blind to this by construction. Same class as the frozen throughput gauge and the `if False:` guard: **a check that succeeds emptily.**

## 1. The regulatory position (sourced)

**Direct debits must be set on a reasonable, evidenced basis.** Ofgem requires DD amounts to be as accurate as possible on the information available, with suppliers reviewing them against estimated annual consumption using prior usage at the property. Payments should reflect realistic forecasts, not be inflated "just in case".

**Credit must be refunded promptly on request.** A customer can ask at any time; the supplier must return surplus credit or **explain in writing why it is withheld**. "Good reason" is the only permitted basis for refusing, and delay without good reason is a compliance failure. Ofgem's Direct Debit Market Compliance Review forced several suppliers to create formal DD and credit-balance refund policies **that did not previously exist**, and to improve refund timescales.

**Surplus credit must be returned OR reflected in a lower DD.** That review's stated outcome: *"ensuring that surplus customer credit balances are either returned to consumers or factored into a lower Direct Debit amount."* Two acceptable outlets, not one.

**The anniversary-reset principle.** Ofgem's 2021 auto-refund consultation proposed that suppliers **set payments so a customer's credit balance returns to £0 each year on the anniversary of the contract start**, with surplus above that automatically refunded. Ofgem measured **£1.4bn** of surplus credit balances in the market in October 2018 — about **£65 per household** — and stated the concern plainly: *"some suppliers may use customers' surplus credit balances to fund otherwise unsustainable business practices."*

**Material change triggers a review**, not only the annual anniversary: price changes, usage changes, household size, heating changes.

**Scope note:** these protections are domestic. Business credit balances are **not** protected in the failure process — relevant if any non-domestic book is ever modelled.

## 2. Why it killed suppliers (the mechanism, sourced)

Under the rules as they stood, **credit balances were available to suppliers as working capital.** A growing book collecting level DD through summer generates cash that is a *liability*, and a supplier can spend it. When it fails, that money is gone.

The failure process protects the customer: every pound of domestic credit is honoured by the incoming supplier. But **the incoming supplier does not receive the credit** — it inherits the obligation without the cash, and recovers the shortfall through an industry levy **mutualised across all consumers' bills**.

Scale, 2021–22: around **30 suppliers failed**, levy claims totalled **£2.35bn**, and the cost of transferring customers, replacing lost credit balances and covering green-levy obligations came to roughly **£94 per household**. Bulb alone cost government £0.9bn in 2021–22 with a further £1bn budgeted.

**The through-line for the sim:** spring/summer growth collects credit → credit is spendable → a price spike raises the cost of the winter energy that credit was meant to buy → the supplier cannot fund it → failure → the credit is mutualised onto everyone else. That is the Ponzi structure the director described, with the regulatory numbers attached.

## 3. What this implies for the model (findings, for the machine to judge)

**a. A credit balance needs at least four exit routes**, none of which appear to exist:
- refund on customer request (promptly, or a written reason);
- **annual review**: recalculate the DD so the balance trends to zero at the anniversary — surplus refunded or the monthly amount cut;
- **material-change review** on price, usage, occupancy or heating change;
- settlement on account closure.

**b. Credit is a liability with a cash-flow consequence.** The site already says this in words on the customer page. The question is whether the *balance sheet* treats it as one — and whether a solvency view can show cash-rich-but-insolvent. If held credit is not deducted from usable cash anywhere, the collateral/death work is measuring the wrong thing.

**c. The −£202 itself needs a cause.** A credit note posted as a negative invoice is legitimate accounting; a credit note that permanently shifts an account's floor and is never discharged is not. What raised it, and what should have discharged it?

**d. The reconciliation control is blind by construction.** Netting a credit note into "billed" makes the identity balance regardless. A control that would catch this: **no account should hold a credit balance older than one anniversary without a recorded refund, review, or written reason.** That is the regulatory rule expressed as an invariant — it is testable, and it fails today on C7.

**e. Mutualisation is a modellable consequence.** If the company dies holding customer credit, that cost does not vanish — it lands on the market. Whether the sim represents that is a scope question, but it is the honest end of the causal chain.

## 4. Suggested falsifiable checks (improve or replace)

1. No account holds credit older than one anniversary without a refund, a DD recalculation, or a recorded reason. **Fails on C7 today.**
2. The annual review moves the DD amount when the balance is materially off zero at the anniversary.
3. Aggregate held credit appears as a liability in any solvency or treasury view, and is excluded from usable cash.
4. Account closure settles the balance in both directions.
5. A material change (price, usage, occupancy) triggers a review event.

**Sources:** Ofgem press release and consultation on auto-refund of credit balances (£1.4bn, £65/household, anniversary-to-zero); Ofgem Direct Debit Market Compliance Review progress update (returned-or-lower-DD, formal refund policies, named suppliers); Ofgem SoLR levy and offset consultations (credit honoured, levy mutualised); Public Accounts Committee report on regulation of energy suppliers (Bulb costs); reported SoLR levy total £2.35bn and ~£94/household.

— Advisor research, prepared 2026-08-04 while the machine was offline.
