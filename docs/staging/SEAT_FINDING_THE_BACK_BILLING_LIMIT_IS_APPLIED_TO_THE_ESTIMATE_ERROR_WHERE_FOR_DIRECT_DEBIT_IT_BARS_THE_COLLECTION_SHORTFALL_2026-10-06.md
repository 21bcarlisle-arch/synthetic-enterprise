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

---

**2026-10-06, the comparator slice landed (worker, claim `back-billing-comparator-follows-the-payment-method`).**
- `back_billing.barred_unrecovered_gbp` is the comparator. Each period's shortfall (true charge minus what was recovered) is barred for the share of its days before the window. The total barred is capped at what is still unrecovered. Scenario A bars £50.33 of a £170 shortfall that the estimate comparator ignored entirely. Scenario B bars £0 where the estimate comparator wrote money off.
- `_resolve_catchup(..., payment_channel)` takes the comparator from the payment method, and every catch-up is stamped `back_billing_basis`:
  - pay-on-bill (and unknown): true against billed, unchanged;
  - direct debit, with each period carrying `recovered_gbp`: true against collected;
  - direct debit without those figures: `direct_debit_collections_not_visible_estimate_error_stands_in`, with the old figure, named as a stand-in.
- `check_back_billing_cap_respected` re-derives a direct-debit catch-up from the periods stamped on the bill and fails closed without them.
- Microbusiness start corrected to 2018-11-01.
- Tests: `tests/company/billing/test_back_billing_follows_the_payment_method.py`.

**Not yet reached in production. Say so plainly.** `simulation/run_phase4c_on_phase2b.build_monthly_bills` passes no `payment_channel_feed`, so every production catch-up still takes the pay-on-bill basis. No caller supplies `recovered_gbp`, because the direct debits collected are built AFTER the bills (`simulation/dd_balance_book.build_dd_balance_book(bills, opening_dd)`). Scenario A has a second gap: it has no estimated run at all. An account billed on accurate reads with a short debit never reaches `_resolve_catchup`. So in production it belongs at the point where a direct debit is raised or a balance is billed, on the DD balance book. Owed next:
1. hand the payment channel to the assembly;
2. apply `barred_unrecovered_gbp` to the DD balance book at each charge recovery action;
3. only then re-read the D48 barred figure.

The DD-review balance treatment is still the assumption toggle. Nothing here decides it. Days apportionment is unchanged.
