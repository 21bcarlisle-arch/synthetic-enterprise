**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`
**Class:** `measurements_that_mirror`

# The selection switch is one account's churn roll, and the £5,350 it moves is the write-off rule, not margin

**2026-09-27.** Root cause of the two-state selection residual, for the director's question of
2026-09-26 ("What I want is the root cause"). Graded against
`SEAT_PREREG_WHICH_ACCOUNTS_THE_TWO_STATE_SELECTION_SWITCH_LIVES_IN_AND_WHETHER_PER_ACCOUNT_CONTRIBUTIONS_ARE_INDEPENDENT_2026-09-27.md`
as amended by `SEAT_PREREG_AMENDMENT_THE_TWO_SEED_DIFF_READ_FROM_ITS_LOG_BECAUSE_ITS_JSON_WAS_DELETED_2026-09-27.md`
(filed before any per-account number below was computed). Source: the log of
`longjob-two-state-account-diff-20260927` (seeds 11111 and 88888, level arm on, run at `ca80a7d0a`),
preserved at `/var/tmp/two_state_diff_20260927.log.keep`. Its JSON was deleted by a worktree reset
(see the amendment).

## The answer

**One account, `PROS-2016-0098`, and one renewal.** At its 2017-03-23 renewal the churn roll is
**0.3763 in every arm at both seeds** (common random numbers). Only the re-drawn elasticity moves
its retention probability, and it moves it across the roll only in the level arm:

| run | p_retain at 2017-03-23 | fate |
|---|---|---|
| control, both seeds | 0.788 / 0.758 | stays to 2020-03-22 |
| value, both seeds | 0.768 / 0.760 | stays to 2020-03-22 |
| **level, seed 11111** | **0.3398** | **churns 2017** |
| **level, seed 88888** | **0.6433** | stays to 2020-03-22 |

It is the only account in the book whose fate differs between the two level runs. The mixing rate
the previous result measured (4 of 18 seeds low) is the probability that this household's elasticity
draw, under the level arm's uplift, puts its p_retain below 0.3763.

**The money is bad debt, not margin.** Keeping the account three more years earns **+£1,415.95** of
term margin (98.7% of the level runs' whole £1,422.50 term-margin difference). The published
`settled-realised` net nevertheless falls by £5,344.10, so the realised-minus-provisioned bad-debt
line moves **−£6,766.59**. That line is `compute_emergent_bad_debt`
(`simulation/arrears_engine.py:519`). It writes off **every failed or disputed bill in full, if the
customer is in `churned_ids`**, meaning it leaves at any point in the window. PROS-2016-0098 leaves in
both runs, so each of its 36 extra bills (49 against 13; the book's bill count differs by exactly
36) is exposed to that rule. Every other account's bills are identical, and each is drawn from its
own `(seed, customer, period_end, commodity)` substream with the same churn membership. So the
−£6,766.59 is this account's, by construction. The per-account sum reconciles:
+£1,415.95 − £6,766.59 + £6.55 for the rest of the book = **−£5,344.10**, the published state
distance to the penny.

**This is derived, not measured per account on the realised clock.** The log prints term margin and
provisioned bad debt per account, not the emergent write-offs. The attribution rests on the
identity plus the substream keying. The confirming run is handed on, writing outside any worktree.

The sign of the seed-11111 residual follows. The level arm "wins" by −£4,238 because its uplift
drove out a customer whose margin was positive but whose staying would have turned three more years
of failed bills into write-offs. The value arm retained it, as control does.

## Why the shard could not see it

The 18-seed shard's `scored_decisions` are the **value** arm's. There PROS-2016-0098 is retained in
2017 on all 18 seeds (p 0.32–0.33 believed, retained). The switch is in the level arm, which no
seed row records per account. That is why 14 of 14 recorded fields failed to separate the states.

## Graded predictions — wrong ones kept

| | prediction | result |
|---|---|---|
| **P0** | seeds reproduce the shard within £1 | **FAILED.** −£4,238.56 / +£1,105.54 against −£3,802.80 / +£1,548.26. The residual's level moved about −£440 on both seeds; the state distance moved 0.13% (£5,344.10 against £5,351.06). **The instruction said a P0 failure voids P1–P5.** Deviation, made openly: L0 below shows the run's own two seeds are one world and two draws, so P1–P6 are graded on that within-run contrast and **nothing is compared with the shard**. |
| L0 | control and value identical across seeds; level differs | **PASS.** Control and value runs are identical in every term row (0 of 3,136 and 0 of 3,176 differ); only the level run differs (11 terms in one run only, 26 differing). |
| L1 | log's term-margin diff within 10% of £5,344.10 | **FAILED, with the wrong sign** (+£1,422.50). This failure is the finding: the switch is below the term margin. |
| P1 | ≤ 3 accounts hold ≥ 90% | **CONFIRMED.** One account: 98.7% on term margin, and about 99.9% on the published basis (derived). |
| P2 | a roster difference, or an account moving > £3,000 | **CONFIRMED both ways:** 11 terms present in one run only, and −£5,350.64 on one account. |
| P3 | within-seed Herfindahl > 0.10 | **REFUTED on the term-margin basis** (0.091 at 11111, 0.073 at 88888: 11–14 effective accounts). **Ungradable on the published basis** from the log, because per-account write-offs are not printed. |
| P4 | per-account depth explains nothing | **Ungradable** (declared in the amendment). |
| P5 | gross/net > 2 | **CONFIRMED on the term-margin basis** (2.45, 6.29). |
| P6 | exactly one or two accounts flip fate, and the flipping account is P1's top account | **CONFIRMED.** One account flips, and it is the top-ranked account. |

## The director's hypothesis, answered

*"Luck dominates because few accounts have enough renewals for a choice to compound."*

- **"Luck dominates": confirmed, and sharper than expected.** One household's elasticity draw against
  one fixed coin decides the sign of the published selection figure.
- **"Because of too few renewals": refuted as the mechanism.** PROS-2016-0098 is not a shallow
  account (12 terms when kept). The swing is large because the write-off rule scales a leaver's
  losses with how long it stayed. The account's renewal count matters only through that rule.
- **Would a deeper book let selection be measured?** Per-account fates are independent (a
  per-account roll, a per-household elasticity), so the independence premise of the 1/k ladder
  (`d678f063a`: ×10 book → about 83 seeds) holds. What it misses is the **tail**: the variance is
  carried by the few churn-marginal, failure-prone accounts whose write-off exposure is large, and
  a deeper book of typical households adds such accounts only in proportion. So depth helps at the
  ladder's rate at best. **The larger lever is upstream.** If the write-off rule is not how the
  industry works, the £5,350 swing is an artefact of the world, and correcting it changes what
  selection is measuring before any depth question arises. That is a fidelity question, filed as
  `SEAT_FINDING_A_FAILED_BILL_IS_WRITTEN_OFF_IN_FULL_IFF_THE_CUSTOMER_EVER_LEAVES_2026-09-27.md`
  and put to the director.

No published figure changes. The 2026-09-26 ruling stands.

## Reproduce

    python3 /var/tmp/parse_two_state.py   # six runs from the log; run order = control, value, level per seed

The parser is a scratch script outside the tree and will not outlive this box. It splits the log on
`=== Phase 2b` headers and reads the `term N (...) actual_net=£` and `p_retain=… roll=…` lines. The
durable reproduction is the confirming run handed on, whose JSON carries the per-account column.
