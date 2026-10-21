**Severity:** RECORDED · **Lane:** C_customer_ops · **Atom:** `C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv`

# Pre-registration: crediting the standing charge's opex allowance in the term contribution

Written 20 Oct 2026, before the code change landed and before any run of it. The finding this
note acts on is
`SEAT_FINDING_THE_MEDIAN_RENEWAL_READS_NEGATIVE_BECAUSE_THE_CONTRIBUTION_CHARGES_THE_COST_THE_STANDING_CHARGE_RECOVERS_AND_CREDITS_NONE_OF_IT_2026-10-20.md`.
The design is in `docs/market_research/next_best_action_and_cross_sell.md` §6.1 (K8, amended
first, in the commit that lands this note).

## The change

`term_contribution_per_year` (`company/crm/renewal_advice_desk.py`) gains a required `fuel` and
credits, per resi leg, Ofgem's nil-consumption opex allowance for that fuel. It uses the cap period
in force on the term's start: OC to June 2025, then CO (cap level model v1.31, direct debit, mean
of 15 regions). It credits no network, policy, SMNCC, EBIT or headroom. Non-resi segments are
unchanged. The C34 switch stays off.

## What each number counts

- **Per-leg contribution:** one leg, one year of the coming term, at the renewal rate. After the
  change it is (rate − `term_cost_floor`) × company EAC − £55 + the nil opex for that fuel and
  period. It still nets no bad debt.
- **Household decision state:** the sum of a household's legs on one start, per month, as C34
  reads it.
- **Book net** (`total_net_gbp`): every leg over the whole window, at the run's own clock. This is
  not the same quantity, and no ratio of the two is drawn.

## The baseline the predictions are against

The probe output `/var/tmp/se-med391-out/on_arm_legs.json` covers the C34 on arm (`b8c665948`) at
`768f41ed1`. Its median leg is −£2.89/month, with 85.0% negative over 487 held legs. Its median
household is −£3.66/month over 321 decision states. 4 of 963 rows were advised.

**Offline arithmetic, not a prediction.** Adding the credit to that run's own recorded legs, with
nothing else moved, gives a median leg of +£1.54/month (26.3% negative) and a median household of
+£2.29/month (16.5% negative). With the pre-July-2025 OC scaled to Ofgem's July 2025 CO share
(0.757 electricity, 0.839 gas), the lower bound in §6.1, the median leg is +£0.67 (39.4%
negative). These are arithmetic on a fixed book. The predictions below are about a re-run, where
the retention guard also reads the new value and the book moves.

## Predictions, on the same command as that probe with only the code change added

- **P1.** The median per-leg contribution is between +£0.50 and +£2.50 a month. The share
  negative is between 15% and 40%.
- **P2.** The median household decision state is positive, between +£1.00 and +£3.50 a month.
- **P3.** Advised rows stay rare: no more than 2% of rows. Every stated effect gives up at least
  £2/month, which is more than the median contribution, and the hazard cuts are 0.001–0.003/month.
  The credit removes a reason to advise nobody; it does not create a reason to advise.
- **P4.** The retention guard makes at least as many offers as on the baseline, and more where any
  move shows. A larger protected value can only pass more cuts through the same guard; it cannot
  refuse one it passed. A count that FALLS refutes the claim that the guard reads only this value
  monotonically.
  - **P4b, from printing the guard at real inputs before any run.** On a 2019 electricity leg,
    the risk-tier cut is capped at the floor, so its cost is at most (rate − floor) × EAC. The
    value protected is that same margin, plus £41.57 credited, less £55, plus the £27.50
    replacement spend avoided: the margin + £14.07. So **with no bad debt netted, the guard
    refuses no resi cut it can size.** Only the bad-debt charge (and, where it is on, the
    engagement weight) can refuse one now.
    - On the 2019 test leg, the guard offers at a 2% default belief and refuses at 8%.
    - `CURRENT_POLICY` nets no bad debt (`retention_nets_bad_debt` is False) and weighs no
      engagement. **On the default book, therefore, the guard stops refusing any resi renewal
      where a cut can be sized.** The offer count rises by every renewal it refused before for
      value. Its refusal branch stays reachable only on a policy that nets bad debt.
    - That makes the guard vacuous for resi on the default policy, and that is a finding about
      the guard, not about this credit. The credit makes the value honest. What the guard lacked
      all along was a weight for the chance that the offer changes the outcome, and C29's
      engagement weight is that weight, off by default. Filed beside this note, not fixed here.
    - On the default policy, before this change, the same leg read the margin − £27.43 and was
      refused unless the strike sat well above its floor.
    - This is the largest behaviour change this landing makes. It is reversible by one line.
- **P5.** Book net moves by less than 1% of its baseline magnitude, and if it moves, it falls
  (more discounts are given). The credit is a reading, not revenue: the book already bills the
  standing charge on every settled record.
- **P6.** The 2023 legs stay the most positive renewal year, and 2020 the least positive of
  2017–2021. The ordering comes from the spread, not from the credit, which varies by under £5 a
  year across 2017–2021.

## What would refute the design rather than the number

If P4 fails with a falling offer count, the guard reads the contribution through something
other than `expected_margin`. That has to be found before the C34 switch is regraded. If P1
lands below +£0.50, the spread moved more than the credit, and the owed rate-route attribution
(P1 of the earlier note, refuted) comes ahead of everything else on this subject.

*21 Oct 05:36Z: the arms died queued twice and were relaunched behind the per-customer-switch arms.
The launch history and the grading plan are in
`SEAT_RESULT_CREDITING_THE_STANDING_CHARGE_OPEX_IN_THE_TERM_CONTRIBUTION_2026-10-21.md`.*
