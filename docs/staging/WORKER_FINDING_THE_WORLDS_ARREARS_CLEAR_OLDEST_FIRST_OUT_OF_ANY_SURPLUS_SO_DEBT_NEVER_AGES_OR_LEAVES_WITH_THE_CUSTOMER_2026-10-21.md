**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `say-whether-the-crisis-bad-debt-gap-is-arrears-volume-or-provision-rate` (Lane 0 delivery)
**Knowledge:** none -- grades the world against the aged-debt and arrears-stock figures already recorded in docs/market_research/ASSUMPTIONS.md (2026-10-04 arrears-prevalence row) and docs/market_research/bad_debt_provisioning.md §3.1-3.2; no new domain claim

# The world's arrears clear oldest-first out of any surplus, so its debt never ages or leaves with the customer (2026-10-21)

**What it unblocks:** the BLOCKING crisis bad-debt finding
(`SEAT_FINDING_THE_CRISIS_BAD_DEBT_CONTROL_HAS_SKIPPED_..._2026-10-14.md`, section "2026-10-21 (night)").
That section splits the company's 2.5x shortfall under the 1% floor. Arrears volume carries x1.84 to
x2.25 of it and provision rate x1.11 to x1.36. The volume side is this item.

**What the switch-on run (ec7fd9942) shows, at year-ends:**
- **The receivable is the right size.** It is 8.8% of revenue in 2022, against Centrica's derived 8.9%.
- **The debt is the wrong age.** Live pay-on-receipt debt over 90 days is 8.8% of the PoR balance in
  2022 and 30.6% in 2023. Centrica's implied share is about 60% and about 75%.
- **Almost no debt leaves with a closing account.** The final-bill balance is 0.01% and 0.11% of
  revenue in 2022 and 2023, against Centrica's 1.8% and 1.9%.
- **No live DD balance ever reaches 30 days.** Centrica held GBP 66m of DD debt over 90 days in 2022.
- **2024 releases the aged debt.** Live PoR over 90 days falls from 4,589 to 1,942 and is paid, not
  written off. Over the same period Ofgem's arrears rose and Centrica's provision rose.

**The suspected mechanism:** `simulation/household_budget.BudgetPaymentBook.settle_month` pays
unpaid bills whole and oldest first out of any month's surplus. A household whose margin turns
positive clears its oldest debt first. The record says the opposite: aged debt (>12 months) is 52-65%
of the arrears stock, and PPM repayment plans average 6.6-7 years.

**Work, in order:**
1. **Grade first, before any change.** Extend `tools/grade_world_debt_against_ofgem.py` to report the
   world's arrears by age (>12 months share of the >91-day stock). Grade it against the 52-65% band.
   No tuning toward company results.
2. **Trace the DD zero.** Is a failed DD always re-presented and paid in the world, or does the
   company's method register re-file the account as PoR? Find out which side it is before counting
   it as world volume.
3. **Trace why leavers carry no debt.** Look at the 70% of indebted switchers who are allowed to
   leave (ASSUMPTIONS row 634), and at home-move leavers. Where does their unpaid balance go?
4. **Only then a world change,** knowledge page first (K8). Candidate: a household back in surplus
   repays at a plan rate, not by clearing everything at once. The rate must be sourced, or carried
   as a GAP.

**Prediction for step 1, filed before it runs:** the world's share of >91-day arrears that are
older than 12 months sits below 52% in 2022-23, and below 30% at Q4 2024.
