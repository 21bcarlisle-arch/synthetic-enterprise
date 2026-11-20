**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Triage of the supplier-lane findings, batch 1 of about 5 (2026-11-20)

Plan item 2, second half, of `docs/operations/WEEKLY_BALANCE_REVIEW_2026-11-16.md` §5, claim
`triage-the-supplier-money-findings-batch-1`. It follows
`docs/staging/SEAT_RECORD_TRIAGE_OF_THE_BLOCKING_FINDINGS_2026-11-20.md` (the BLOCKING ten:
7/2/0/1) and is a reading for Monday 23 Nov's balance review.

**Scope.** Every file at `docs/staging/` root on origin whose header names lane B, C, D or E: **91
on 20 Nov** (92 on 16 Nov). This batch is the **20 oldest by filename date** (7 Oct to 17 Oct).
71 remain.

## Counts

| Disposition | Count | Findings (# below) |
|---|---:|---|
| **fixed** | 8 | 5, 8, 10, 11, 12, 14, 15, 17 |
| **real** | 0 | |
| **parked** | 5 | 1, 2, 7, 9, 16 |
| **obsolete** | 7 | 3, 4, 6, 13, 18, 19, 20 |

Fixed and obsolete files are archived to `docs/staging/done/` with a `**Disposition:**` line at
the top. Parked files stay at root with a dated triage line under the header.

**Zero real is a claim worth doubting, so here is why.** Every still-true premise in this batch
waits on something named: a world mechanism (W2_38's price-reading payment draw, for 9 and 16), a
published rate nobody publishes (C34's plan take-up, 2), a curriculum switch that is off (B7's
move-with-us offer, 7), or a pre-registered arm whose launch gates are unmet (C29, 1). In this
batch "real" would mean work that could start today, and none can. Parked rows that share a
blocker can be revisited together. 9 and 16 are both E6 on W2_38.

## How the premises were re-measured

Each file was read on origin at 0a859d31be and its premise checked against the code, the commits
and the publisher's gate on the 18 Nov book (`docs/reports/domain_invariants.json`, run
6af7fd0bfd). Two read-only readers split the batch ten and ten, and the seat checked their work.
**All 20 commit ids cited below are ancestors of origin/main**, checked with `git merge-base
--is-ancestor`. The 7cec44a4b8 branch is at `tools/generate_billing_ledger.py:605`. INV_VAT_RATE
reads CLEAN on 6af7fd0bfd. Unlike the BLOCKING ten, **the gate settled few of these.** It has no
row for renewal floors, retention offers or the provision, so most premises were settled from the
code and from commits.

## One disposition each

| # | Finding (docs/staging/) | Disposition | Evidence / reason |
|---|---|---|---|
| 1 | `SEAT_FINDING_THE_PAYMENT_SCORE_REACHES_THE_CHURN_BELIEF_AND_THE_RETENTION_GUARD_PRICES_IT_AS_IF_THE_DEBTOR_PAYS_2026-10-07` | **parked** | Waits on the re-armed retention-netting arm (prereg 460c370441; launch gates unmet, 81042a7c3c). If it moves no debtor offer, an arrears-state rule on the guard is a G9 question for the director. Atom C29. Revisit 2026-11-27. |
| 2 | `SEAT_FINDING_C34_DEBT_ARMS_ARE_TIED_BY_CONSTRUCTION_BECAUSE_NO_DEBT_ACTION_REACHES_A_WORLD_THAT_ANSWERS_2026-10-10` | **parked** | Waits on a sourced plan take-up and instalment keep rate (all None in simulation/plan_offer_response.PUBLISHED_BASIS), or a curriculum world the director names. C34 parked 17 Oct. Knowledge gap: yes. Revisit 2026-12-18. |
| 3 | `SEAT_FINDING_THE_PRICE_MATCH_SAVE_RAN_UNPREDICTED_OFFERS_TWO_IN_TWENTY_THREE_AND_CANNOT_YET_TELL_2026-10-10` | **obsolete** | A record of an unpredicted pair. Its open questions were answered: re-grade b234e27bd, below-floor cause 03a0b66da, VAT basis d1e37f45c; near-zero saves are what the world predicts (WORKER_RESULT ...ZERO_OF_23...). |
| 4 | `SEAT_PROPOSAL_A_PERSONAL_PAYMENT_PLAN_AND_DEBT_AS_A_NEXT_BEST_ACTION_DESIGNED_AS_ONE_2026-10-11` | **obsolete** | A design proposal the director ruled on, 12 Oct. Its work is rehomed: W2_41 and W2_42 closed at L2; DD4b sits on DD_seasonal_cashflow_physics (blocked, amplitude unpublished); the engine is E6. |
| 5 | `SEAT_FINDING_B8_EXPERT_HOUR_THE_RUNS_HOLDOUT_FLIPPED_ITS_COIN_BEFORE_THE_GUARD_AND_KEPT_ONE_ARM_ONLY_2026-10-11` | **fixed** | Q11 (holdout coin before the guard) fixed by 88ca351563; Q5 decided by d5ba38b12c; the record is superseded by the second blind pass 9bdd1757ed. |
| 6 | `SEAT_FINDING_B8_Q5_THE_PRICE_MATCH_AGAINST_THE_RISK_TIERS_OVER_THE_FULL_WINDOW_2026-10-11` | **obsolete** | A recommendation the file itself withdrew (13 Oct). d5ba38b12c found price-match minus risk tiers negative on all four fresh seeds; CURRENT_POLICY keeps risk_tiers. |
| 7 | `SEAT_FINDING_THE_MOVER_OFFER_ON_FRESH_SEEDS_FIVE_PREDICTIONS_HOLD_AND_STAYER_PRICES_MOVE_WHERE_A_FOLLOWER_IS_SUPPLIED_2026-10-12` | **parked** | Stayer price moves where a follower is supplied are still unattributed (the one-variable arm never ran), but the offer is OFF (curriculum move_with_us_activation false). Must run before any activation. Atom B7. Knowledge gap: yes (move-with-us take-up). Revisit at an activation proposal or 2026-12-18. |
| 8 | `SEAT_FINDING_ON_FRESH_SEEDS_THE_SAVE_NEVER_FIRES_BECAUSE_RENEWALS_SIT_BELOW_THEIR_OWN_COST_FLOOR_AND_THE_PRICE_MATCH_RENEWAL_CUT_LOSES_NET_2026-10-13` | **fixed** | Held renewals below floor 23/27 -> 4/28 after 03a0b66da; tier cut floored by 5c137eb5b (DISCRETIONARY_RATE_NOT_BELOW_OWN_COST_FLOOR); VAT mix d1e37f45c; cut decided d5ba38b12c. The floor's definition residue is B12. |
| 9 | `SEAT_FINDING_THE_CASH_FORECAST_PROVISION_DOES_NOT_YET_BEAT_THE_AGE_BANDS_IT_LAGS_IN_CALM_YEARS_AND_RANKS_WORSE_2026-10-13` | **parked** | Still true: the cash-forecast provision has no oldest-unpaid-age state and no external roll-rate prior, and is not the run's provision. Waits on W2_38 (payment draw reads price). Atom E6. Knowledge gap: yes (no published GB roll rates). Revisit 2026-12-04. |
| 10 | `SEAT_NOTE_THE_DD_DESIGN_PILE_IS_IN_THE_CONSOLE_SEATS_LANDING_SEQUENCE_2026-10-13` | **fixed** | term_end_iso and the forward rate are wired into the DD review by c6317ca9ff (dd_review.review_forecast_inputs, read by dd_balance_book and dd_book_legs). |
| 11 | `SEAT_FINDING_RENEWALS_SIT_AT_THEIR_COST_FLOOR_BECAUSE_THE_FLOOR_CARRIES_THE_STANDING_CHARGES_NETWORK_AND_THE_PREMIUM_READS_THE_STANDING_CHARGE_AS_MARGIN_2026-10-14` | **fixed** | One unit-rate floor and the standing charge out of margin: e3b5ed01a6, B12 L1 455adef1aa; world side c71d2521d7, graded 3d75dfd74e (median ratio 1.000). Recounting held renewals at the floor is B12's L2 grade. |
| 12 | `SEAT_FINDING_THE_UNIT_RATE_MARGIN_STILL_READS_ABOVE_ITS_TARGET_ON_FIXED_TERMS_2026-10-14` | **fixed** | Fixed terms only in the margin lookback: badd57e8e9 (FIXED_PREMIUM_BOOK_TARIFF_TYPES), pre-registered 03ee2fd094. |
| 13 | `WORKER_FINDING_A_SAVE_GRADE_COUNTS_REALISED_SAVES_WHERE_THE_LOG_ALREADY_HOLDS_THE_EXPECTED_ONES_2026-10-15` | **obsolete** | A method lesson about a scratch script never in the repo. Answered by WORKER_RESULT ...ZERO_OF_23...; save grades since read expected value (ee995aadc9, 0674199b89). |
| 14 | `WORKER_FINDING_THE_LEDGER_DRAWS_A_PAYERS_OUTCOME_ON_BILLS_THE_ENGINE_NEVER_ASKS_THEM_FOR_2026-10-15` | **fixed** | Bills inside the occupier window go to the deemed account, not a drawn payer: 7cec44a4b8 (tools/generate_billing_ledger.py:605). INV_OVERDUE_WITHIN_PAGE_BALANCE CLEAN, 0 of 6,115, on 6af7fd0bfd. |
| 15 | `WORKER_FINDING_TWO_STATEMENT_CONTROLS_ARE_RED_AT_ORIGIN_ON_THE_2248E3BAF_LEDGER_AND_NO_CENSUS_HOLDS_THEM_2026-10-15` | **fixed** | Both causes fixed by 5624e36046 (part_paid_gbp on failed payments; SME VAT); post-publish tests 2427a5830e close the no-census half. INV_VAT_RATE CLEAN on 6af7fd0bfd. |
| 16 | `WORKER_FINDING_THE_ROLL_RATE_PROVISION_TRAILS_THE_RUNS_ARREARS_BY_THREE_QUARTERS_2026-10-15` | **parked** | Still true: the learned roll-rate provision lags (strict xfail stands; ROLL_RATE_PROVISION False, so nothing published moves). Waits on W2_38. Atom E6. Knowledge gap: yes (forward-looking adjustment practice). Revisit 2026-12-04. |
| 17 | `SEAT_FINDING_B11_THE_FLAT_SUPPLIER_ARM_HAS_NO_DOOR_ON_A_VARIED_BOOK_2026-10-16` | **fixed** | FLAT_SUPPLIER_POLICY and the seed_family columns: bf0997494b, f692b1b80e, abe7ce5336. |
| 18 | `WORKER_FINDING_C7_AND_286_OTHER_RUNS_OVER_TWELVE_MONTHS_NONE_BILLED_PAST_THE_BAR_AND_NOTHING_ASKS_FOR_A_READ_2026-10-16` | **obsolete** | A census record: no bill crosses the 12-month bar (INV_BACK_BILLING_12M 0 breached of 38,367 on 6af7fd0bfd) and the read-duty register landed in c5963a5c0a. Read-chase effort stays a GAP in read_access_and_theft_duties.md. |
| 19 | `SEAT_FINDING_B11_RESCALING_THE_KEY_OVER_THE_CUT_CLOSES_THE_LEVEL_TO_FLAT_AND_MOVES_IT_AWAY_FROM_THE_REALISED_RATE_2026-10-17` | **obsolete** | An experiment record whose question is answered in the file: the rescale default stays fit_window (forward_clv.py). Slice 13 carries on. |
| 20 | `SEAT_FINDING_B11_THE_FLAT_LEVEL_MISS_IS_THE_PRE_CRISIS_SWITCHING_AND_NO_WINDOW_INSIDE_THE_FIT_YEARS_CURES_IT_2026-10-17` | **obsolete** | An experiment record whose question (why the flat level misses) is answered. The regime-band design is needed only once something consumes the per-customer level; nothing does. B11 parked. |

## Found on the way (not new files; routed here)

- **W3_3's map row looks stale.** It reads "PARKED 2026-11-18 ... unpark when that book is
  graded", but 3d75dfd74e graded that book on 19 Nov. B12 (L1, `depends_on: W3_3`) is the next
  move: its L2 grade should recount held renewals at the floor (21 of 21 on d55598dd6, not
  recounted since the fixes) and grade the gas book on the new basis, which nobody has done.
- **`DISTRESS_SCORES` in `company/pricing/value_based_renewal.py` has no reader.** The value arm
  never receives the payment behaviour score (from #1). This is routed to C29, not filed again.
- **The director's 12 Oct ruling to grade the payment plan's shock-avoidance cannot be met yet.**
  It needs DD4b, and DD4b is blocked on an unpublished amplitude (PB4 residual b). That is not yet
  checked against `for_the_director`. It goes to batch 2's reader as a check.

## Next

Batch 2: the next 20 oldest supplier-lane files (from 17 Oct). Same method. It is handed on as
continuation `triage-the-supplier-money-findings-batch-2`.
