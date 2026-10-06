# The back-billing limit is applied to the estimate error where, for direct debit, it bars the collection shortfall

**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Claim:** `back-billing-comparator-by-payment-method` (Lane 0 delivery)

**2026-10-06.** Found by the back-billing knowledge pass (`docs/market_research/back_billing_and_liability.md`).
SLC 21BA bars a *charge recovery action* — a bill demanding payment, a direct debit taken or raised,
or a debt rate on a prepayment meter — for energy more than 12 months before it. The Energy Ombudsman's
published stance: "A direct debit statement is not charge recovery action." Its worked scenarios:
- **A:** bills on actual reads, with a direct debit falling short, raised after 17 months. The shortfall older than 12 months is lost.
- **B:** no bills for 17 months, but the direct debit covered use. Nothing is barred.

**The defect.** `company/billing/monthly_bill_assembly._resolve_catchup` writes off the old part of
(true use − estimated bills) for EVERY payment method. For direct debit the comparator is wrong in both
directions:
- it writes off money still owed when the direct debit covered the use (scenario B);
- it misses the loss when bills were accurate but the direct debit fell short (scenario A).

`company/compliance/domain_invariants.check_back_billing_cap_respected` encodes the same comparator,
so it must change with the fix.

**Related:**
- **The direct debit review never asks for the balance.** `company/billing/dd_review.review` resets the debit to future spend and never seeks the balance it finds. Whether a GB supplier's annual review normally recovers arrears through the debit is unpublished. Per the director's 2026-10-05 ruling, it is an ASSUMPTION TOGGLE, tested for whether any decision changes across it, not a question for him.
- **The split is by days.** `back_billing.barred_fraction` splits the unread stretch by days, not by the company's own monthly profile (`unread_month_estimate.py`).
- **The start dates are wrong.** The microbusiness start is coded as 1 May 2018; it is 1 Nov 2018. The pre-2018 voluntary regime is absent; see toggle `q2_pre_2018_voluntary_cap_coverage`.

**Owed (a D48 slice).** Make the comparator follow the payment method: for direct debit, true charges against what was asked or taken. Move the invariant with it. Give the review's balance treatment a toggle and run its sensitivity. Correct the microbusiness date. Each fix gets a test named for its defect, starting with scenarios A and B as written by the Ombudsman.
