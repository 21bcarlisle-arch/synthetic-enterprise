**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `value-arms-error-bar` · **Claim:** `read-selection-with-and-without-arrears-write-offs` (Lane 0 delivery)
**Class:** `no_caller_and_never_runs`

# The selection leg is a churn-pricing part and a credit part. Without write-offs it is positive in both runs, and the value arm never sees arrears

**2026-10-02.** Answers the delivery seat's item `read-selection-with-and-without-arrears-write-offs`
(`5d0d9b122`). No new run. No pricing code changed. Sources:

- **1002c:** `/var/tmp/se-retake-belief/value_cycle_ab_s1_three_arm_20261002c.json`, produced at `0cc052102`.
- **1002b:** `docs/observability/value_cycle_ab_s1_three_arm_20261002b.json` on origin, produced at `f18e8b5dc`.

Both producing commits contain `ae101f936`.

## The split

Per billing account, selection is value-arm net minus level-arm net on the settled-realised clock,
which is the artefact's own `level_vs_selection`. Each arm's `arrears_lines_by_billing_account_gbp`
reconciles to its net to the penny on all 124 accounts (`arrears_reconciliation.reconciles: true`).
So net splits exactly into two parts:

- **credit part** = DCA recovery + unbooked recovery − write-off at close − statute-barred write-off
  − stayer provision − unbooked bad debt. This is what the arrears engine realised.
- **churn-pricing part** = net − credit part. This equals `pre_4c_net + placeholder_bad_debt_released`,
  which is margin with no bad debt charged at all.

| run | published selection | churn-pricing part (no write-offs) | credit part | PROS-2016-0098: with / without / credit | rest of book: with / without |
|---|---|---|---|---|---|
| 1002b | **−£259.07** | **+£7,736.25** | −£7,995.32 | −£5,613.33 / **+£2,181.23** / −£7,794.56 | +£5,354.26 / +£5,555.02 |
| 1002c | **−£4,207.93** | **+£5,475.19** | −£9,683.12 | −£8,136.05 / **+£1,756.15** / −£9,892.20 | +£3,928.12 / +£3,719.04 |

**Exactly one account changes sign when write-offs are removed, in both runs: `PROS-2016-0098`.**
That is a census over all 124 accounts, counting any non-zero selection. Its credit part is 97.5%
of the book's credit part in 1002b and 102.2% in 1002c. Every other account's credit part is
under £133 in absolute value. Removed from the book, the credit part is −£200.76 in 1002b and
+£209.08 in 1002c, which is noise in both directions.

**On the churn-pricing leg, the per-customer view beats the flat level by £7,736 and £5,475.** The
selection leg is negative only because of one account's realised bad debt. The direction's
"193%" checks: 8,136.05 / 4,207.93 = 1.93.

## PROS-2016-0098: what decided it, and what the company could see

| | control | value arm | level arm (£49.25 in 1002b / £60.00 in 1002c) |
|---|---|---|---|
| 2017-03-23 renewal, world p_retain against roll 0.3763 | 0.7375, renewed | 0.7271, renewed (offered at **£11.50** margin; believed p_retain 0.2774) | 0.2165 / **0.064**, churned |
| left | 2021-03-22 | 2021-03-22 (1002b) / still on book (1002c) | 2017-03-23 |
| bills issued | 60 | 60 / 69 | 12 |
| write-off at close | £8,638.50 / £8,659.73 | £8,857.45 / **£11,241.13** | **£0.00** |

**The flat rule did not choose against a bad payer. The control (flat company margin) kept this account
too, and wrote off about £8,650.** Only the level arm's high flat margin pushed it over its churn
roll. The value arm did what its churn belief told it: it believed p_retain 0.28, cut the margin to
£11.50 to hold the account, and held it.

**At 2017-03-23 the account was clean, and no observer could have seen its credit risk.** This is
derived from the artefacts, not read from a ledger. The world writes off every failed or disputed bill
of a leaver in full (`compute_emergent_bad_debt`, per the 2026-09-27 result). The level arm churned
the account at 2017-03-23 with all 12 of its acquisition-term bills issued, and booked £0.00 of
write-off and £0.00 of DCA recovery. Those 12 bills fall before the first renewal, so they are
identical across arms (same acquisition rate, per-bill substreams). **So no bill had failed when the
decisive renewal was priced.** Caveat: a failed bill that was cured before close would not show.
That would mean a debt which existed on the day and was paid after the household left, which is
possible but not evidenced. Every pound of the write-off comes from bills 13–69, after the 2017 decision.

At the later renewals (2020-03-22 and 2021-03-22, value arm only) the losses had begun accruing.
The artefacts do not say how much of the arrears was on the ledger at those dates, because no
artefact logs the company's ledger state per renewal. **This is not measured.** On those dates the
value arm chose £33.00 and £31.00 margins (1002b), and £51.50 and £20.25 (1002c). In 1002c the 2021
renewal was priced down to £20.25 on a believed p_retain of 0.38: the arm cut the price to retain
what was by then probably a debtor.

## Did ae101f936's arrears state reach the value arm's price? No, by construction, on every account

`ae101f936` routes `LivePaymentTriad.arrears_state` to the **desk's booked churn belief**
(`run_phase2b` → `RenewalObservation.arrears_state` → `estimate_renewal_churn`). That leg is live. It
also added `arrears_state=` to `decide_margin` and forwarded it into `_score`. **But the only
production caller of `decide_margin`, `renewal_margin_uplift` (`company/pricing/value_based_renewal.py`,
called from `company/pricing/renewal_rate_chain.py:437`), does not pass `arrears_state`.** Nor does it pass
`credit_risk`, `payment_delay_days`, `behaviour_score`, `bill_shock_count` or `satisfaction_score`.
`renewal_rate_chain` has no arrears or credit input to forward. So every value-arm and level-arm price in
both runs was scored with `arrears_state="unknown"` and `credit_risk="medium"` (`DEFAULT_CREDIT_RISK`).
That holds for PROS-2016-0098 at all three of its renewals, whatever the ledger held.

The controls in `tests/company/crm/test_the_arrears_state_reaches_the_renewal_from_the_companys_own_ledger.py`
call `decide_margin(arrears_state=...)` directly. None goes through `renewal_margin_uplift`. So they
stay green while no production price reaches the state. This is the `no_caller_and_never_runs` shape,
at the production layer under a conditional layer that works.

**Effect on PROS-2016-0098: none.** The renewal that decided the account fell on a clean record. If the
state had been forwarded, the ledger would most plausibly have read `no_debt` (0.79× hazard). That
would have *raised* the arm's believed p_retain and its margin. Whether by enough to cross the world's
roll, I cannot say, and that is not computed here.

**And wiring it would not price credit.** Inside `decide_margin`, `arrears_state` reaches only
`enriched_churn_estimate`, the churn hazard. The bad-debt cost in `expected_annual_costs` is taken
from `credit_risk` through `bad_debt_provision_gbp` and never from the arrears state. A `worsening`
household therefore reads as *more likely to leave* (1.28×), and the value search answers that by
cutting the margin to keep it. **On a debtor, the one signal that reaches the price pushes it towards
retention, and no signal reaches the expected cost of not being paid.** That is a second, latent
defect behind the gap.

## Verdict, as the item asked

- **Gap, not a defect of the "sees and ignores" kind.** The value arm cannot see arrears. The
  observable exists in the company (`PaymentObservationConsumer.arrears_state`, and it reaches the desk),
  but the pricing adapter does not forward it. Filed as
  `docs/staging/SEAT_FINDING_THE_VALUE_ARM_CANNOT_SEE_ARREARS_BECAUSE_THE_PRICING_ADAPTER_NEVER_FORWARDS_IT_2026-10-02.md`.
- **What the floor's verdict means.** A negative selection leg on these runs does not show the value arm
  choosing badly on churn. On the churn-pricing part it chose well on both runs. The sign is set by one
  account whose credit loss arrived after a decision no observer could have priced. At the later
  renewals the arm was blind to its own receivable. Any seed mean of `selection_gbp` should be published
  beside its churn-pricing/credit split. Otherwise it reads as the wrong cause.
- **Not settled here:** what the ledger held at 0098's 2020 and 2021 renewals. That needs one run that logs
  `_company_arrears_state` per priced renewal. It is named, not launched.
