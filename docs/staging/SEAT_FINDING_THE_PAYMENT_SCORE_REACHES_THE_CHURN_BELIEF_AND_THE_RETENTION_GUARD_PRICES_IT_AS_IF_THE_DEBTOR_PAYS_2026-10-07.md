**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C29_decisions_stop_being_lookup_tables` · **Direction item:** `the-payment-score-reaches-a-decision-or-says-why-not` · **Claim:** released on landing

# The payment score reaches the churn belief, and the retention guard prices it as if the debtor pays

Opened by `docs/staging/records/SEAT_RESULT_THE_CHOSEN_BOOKS_EXCESS_BAD_DEBT_IS_TWO_ZERO_WEIGHT_ACCOUNTS_AND_WEIGHTED_IT_IS_THE_LOWER_2026-10-07.md`
§3 and "What this changes" item 2. That record said the score "reaches no collections or retention
decision on this record". **Correction beside that claim: half of it is wrong.** The score reaches the
retention decision, and in the direction that spends money on the worst payers. Read from the code
at HEAD `f71fcc176`. The run was not re-executed, so this establishes the routes, not their pounds.

## Where the score goes (company side, `_cx_desk.payment_behaviour_score`)

| Decision | Reads the score? | What it does with it |
|---|---|---|
| Renewal churn belief (`estimate_renewal_churn`, `run_phase2b` decision leg) | **yes** | CRITICAL +0.20, POOR +0.10 on the churn belief (`payment_churn_model.CHURN_UPLIFT_BY_SCORE`) |
| Retention offer (`company_est_pre > RETENTION_THRESHOLD` 0.30) | **yes, through that belief** | a worse payer is likelier to be offered a discount |
| Retention guard (`retention_value_protected`) | no | protects `(unit_rate − forward) × EAC` + acquisition saved. **No bad-debt term.** |
| SVT drift belief (`estimate_svt_drift`) | yes | recorded beside the roll, reaches no hazard, by design |
| Value-arm renewal price (`margin_arm_uplift` → `decide_margin`) | **no** | passes `arrears_state` and the learned `default_belief_rate`, never `behaviour_score`, so its churn term reads every account as having no history. `DISTRESS_SCORES` in `value_based_renewal.py` is defined and read by nothing. |
| Collections (`arrears_engine`, `collections_journey`) | no | driven by days overdue. In the run nothing selects a dunning step, and `advance_collections_journey` has no caller in `simulation/`. |
| Refusing the renewal | not a lever | a domestic fixed term ends at the customer's choice. Doing nothing rolls them to the default tariff (SLC 22C.7–8, `docs/market_research/what_a_renewal_decision_is_for_a_gb_domestic_customer.md`). PROS-2016-0098's two renewals were not a company decision to keep a debtor. |
| Objecting to the switch away | separate | `docs/market_research/domestic_debt_objection_rates_gb.md` and its own finding |

## What this means

**The score's honest route is the churn belief, and it is wired.** The defect is downstream. The
retention guard values the account as if it will pay, so the inference "this payer is in difficulty,
and so is likelier to leave" turns into a discount offered to it. That is value transferred to the
accounts least likely to pay for it. The company already holds the right correction, its own learned
bad-debt rate by arrears state (`PaymentObservationConsumer.default_belief_rate`), and the run reads it
at the renewal chain (`_chain_default_belief`). The guard is the one place that does not.

**Collections should not read the score yet, and this turn did not wire it.** The 2026-07-25 ruling
reserved collections action to the director, and C33 is framed and waits on his ranking. The canon
of 2026-10-05 puts dunning under step 4, per-customer decisions. A score-driven dunning step built
here would pre-empt both.

**The value-arm price not reading the score is named, not fixed.** Wiring it would move every
value-arms control (the world digest is unchanged, but the arm's outputs move). Its churn term would
then raise a debtor's believed leave probability inside a price, a judgement C29 owns.

## The dual-fuel one-leg read: fixed in this commit

The departure is rolled on the electricity leg, and both company beliefs at that roll read
`payment_behaviour_score(cid)` for that leg alone. The gas leg's record never reached them. Now
`CustomerExperienceDesk.account_payment_behaviour_score(supply_points)` scores **every bill on the
account**. That is the score's own definition applied to the account's history, with no rule for
combining two scores and no new threshold. Both decision-leg sites in `run_phase2b` read it over the
account's supply points. A single-leg account gets exactly its leg's score.

Printed at the record's rates for PROS-2020-0002 (gas 32% on time, 17% DD-failed, equal bill counts):

| electricity leg | electricity score | account score | churn uplift, leg → account |
|---|---|---|---|
| 60% / 10% DD-failed | FAIR | POOR | +0.03 → +0.10 |
| 79% / 14% | FAIR | POOR | +0.03 → +0.10 |
| 85% / 4% | GOOD | POOR | +0.00 → +0.10 |

The account reads POOR, not CRITICAL, because half its bills are paid. **This makes the guard defect
bite harder on these accounts**: a dual-fuel debtor is now likelier to cross 0.30 and be offered a
discount. That is the right belief feeding a wrong valuation, and it is why the guard is the next item.

*Correction, 2026-10-07, measured: the guard never binds on the chosen book. All 73 calls offered;
value protected is 4.9 to 15.7 times the cost, and netting the learned bad debt (at most 7.9% of
value) withdrew nothing. The transfer is decided at the 0.30 threshold, not at the guard.
`records/SEAT_RESULT_THE_RETENTION_GUARD_NETS_BAD_DEBT_AND_ON_THE_CHOSEN_BOOK_IT_WITHDRAWS_NOTHING_2026-10-07.md`.*

Controls: `tests/company/crm/test_a_dual_fuel_accounts_score_reads_both_legs.py`. There are planted,
null and partition legs, plus a chain control over the run's AST. Mutated: a first-leg-only read reds
4 of 6, and one run site reverted to the leg read reds the chain control.

## Next

`retention-guard-nets-the-companys-own-bad-debt-belief`: net the company's learned
`default_belief_rate` from the value the retention guard protects. Put it behind a `DecisionPolicy`
flag whose off-arm is bit-identical, with a planted debtor whose offer it withdraws. Pre-register the
count of retention offers to CRITICAL/POOR accounts on the chosen book before running it.

*Correction, 2026-10-07 afternoon: the netting landed as `5c0ed0a9d` (and its first cut, `4c300feb9`)
in a worktree and was never promoted. Origin carried this finding and `49f2587f1`'s record of the
arms, but not the flag, the guard change, the controls, the pre-registration or the result. When the
item was re-drawn, the landing check graded only this file, which was already on origin, so it read
"already landed". `5c0ed0a9d` is re-landed onto origin unchanged. None of its paths had moved on
origin since its base `4088674a4`, and its 24 tests pass on the new base.*
