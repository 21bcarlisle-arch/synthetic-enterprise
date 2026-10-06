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

---

**2026-10-06, the bar reaches the DD balance book (worker, claim `back-billing-dd-comparator-reaches-production`).**

**One correction to the entry above.** Owed item 1 was spent before it was written: `simulation/run_phase4c_on_phase2b.build_monthly_bills` has passed `payment_channel_feed=simulated_payment_channel` since 2026-09-01 (`fc1c9a65c`). So since `e3e0a174e`, every production DD catch-up carries `direct_debit_collections_not_visible_estimate_error_stands_in`, not the pay-on-bill basis.

**What landed:**
- **The comparator places surplus on the oldest debt.** `barred_unrecovered_gbp` lets each period's collection pay its own charge first, and anything above that pays the oldest open shortfall (the running-account rule). Before, surplus was netted only against the total. A debt that was recovered and then built up again a year later read as old. Scenarios A and B are unchanged.
- **The door.** `company/interfaces/bill_assembly.barred_at_charge_recovery` (defined in `back_billing`; a seam may not name `gbp`) takes plain tuples and returns only the amount.
- **The book takes the bar at each charge recovery action.** `simulation/dd_balance_book.build_dd_balance_book(bills, opening, closed_ids, seek_balance_at_review)`:
  - the final bill of an account that left is a recovery action;
  - the annual review is one only when the toggle says the review seeks the balance;
  - an open account's figure is an exposure, not a loss.
  - Each bar is capped at the billed debit the action seeks.
  - With the toggle off, the trajectories are byte-identical.
- **The run.** It passes `churned_ids` and publishes the other arm as `dd_back_billing_if_review_seeks_balance`.
- **Tests:** `tests/simulation/test_dd_back_billing_at_charge_recovery_actions.py`. Two mutations were run, and each failed its named test: surplus not placed, and the cap removed.

**The D48 re-read.** This was measured over the bills of run `aa38800a1` (`docs/reports/run_output_latest.json`, 129 DD accounts, 87 closed). A fresh run will move it.

| | barred £ |
|---|---|
| Estimate comparator, written off on DD catch-ups (what is BOOKED today) | 901 |
| Review never seeks the balance (as built): at final bills of closed accounts | 17,667 |
| … plus exposure on open accounts if sought at run end | 23,408 |
| Review seeks the balance (toggle): at reviews | 13,079 |
| … at final bills | 183 |

- **The decision does not change across the toggle.** The estimate comparator understates the DD bar by more than an order of magnitude on either arm. Replacing the stand-in is right whichever way the review goes. The toggle moves the amount by about 3×, and it moves who bears it: lost at closure, or lost at the review.
- **K3 cannot carry it.** K3 is energy, and the DD bar is money not collected. The D48 measure needs a money line for DD beside K3. Until then, K3's DD share is the stand-in.
- **The cause is under-sized debits, not estimates.**
  - C9 opened at £27 a month against about £180 of use.
  - Through 2022 the review lagged prices by a year. Accounts carried four-figure debits that were never sought.
  - Separately, PROS-2024-0197 was billed about £125 a month on estimates against about £900 of true use. That is the D48 estimate domain, and it is not touched here.

**Not done, and owed (next slice):**
1. Stop the DD catch-up's stand-in write-off and book the book's bar as the write-off: a `BACK_BILLING_CREDIT` on the ledger, which reads `catchup_written_off_gbp` today. Until then the stand-in and the book's bar overlap, and only the stand-in is booked. The book touches no ledger; DD3 is owed.
2. Add a D48 money line for DD.
3. The toggle's credit side. Neither arm returns a held credit at review, so the seek arm ends at a +£44.8k portfolio credit. That is the existing review sizing from a year that included catch-ups. It is a separate assumption, and nothing here decides it.

**For the director (a practitioner question, not blocking):** when a raised direct debit recovers arrears, does a GB supplier apply it to the oldest debt? This change assumes yes. The Ombudsman's scenarios do not say.
