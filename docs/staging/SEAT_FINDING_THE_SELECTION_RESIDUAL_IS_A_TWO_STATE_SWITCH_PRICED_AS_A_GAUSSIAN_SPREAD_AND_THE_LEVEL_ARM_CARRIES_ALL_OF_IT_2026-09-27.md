**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`
**Class:** `measurements_that_mirror`

# The selection residual is a two-state switch priced as a Gaussian spread, and the level arm carries 99.8% of it

**2026-09-27.** Evidence, graded predictions and the reproduce line:
`docs/staging/records/SEAT_RESULT_RENEWAL_COUNT_EXPLAINS_NONE_OF_THE_SELECTION_RESIDUAL_AND_THE_VARIANCE_IS_ONE_DISCRETE_EVENT_IN_THE_LEVEL_ARM_2026-09-27.md`.
Instrument: `tools/selection_residual_decomposition.py`.

**The defect.** Every error bar this project has published on `selection_gbp` — `selection_sem_gbp`,
`sems_from_zero`, `selection_distinguishable_from_zero`, `seeds_needed_to_state_a_sign` and the whole
`distance_to_a_sign` block — is `sd/√n` arithmetic, which is the bound for ONE quantity wobbling
about a mean. On the 18-seed family at HEAD the residual is not that. It is a switch between two
clusters £5,387.65 apart, each only £514.60 wide, firing in 4 of 18 elasticity draws: a separation of
9.4×. The sd is a state distance times a mixing rate, so the quantity actually unknown is the RATE,
and its bound is binomial, not normal.

**Why it is not merely a tighter/looser bound.** The honest interval on the family mean is the rate's
exact 90% interval (0.080–0.439 at 4/18) carried through: **−£997.69 to +£937.49**. That interval
contains both signs AND contains the served −£959.78 from 2026-09-10. Read correctly, the two runs
never disagreed and "the sign did not reproduce" was never a contradiction to explain — it is one
sample of an unpinned switch. The Gaussian reading instead produces `seeds_needed ≈ 717`, which
prices more seeds against the wrong unknown.

**Where the variance lives, by the identity that defines the residual.**
`var(selection) = var(value_net) + var(level_net) − 2cov` reconciles exactly, and the shares are
value arm **0.31%**, level arm **99.84%**, covariance **−0.15%**. sd(value net) £129.27 against
sd(level net) £2,309.76 — **17.9×**. `corr(value_net, level_net) = +0.0135`: two arms sharing every
draw whose outcomes are independent anyway, so **the paired design removes 0.15% of the arms'
variance**. Both nets are discrete — 4 and 8 distinct values across 18 seeds — so every normal
approximation on this instrument is fitted to a handful of lumps.

**What nothing in the artefact can say.** Of 14 recorded fields tested for disjoint ranges between
the two states, **zero** separate them (`level_arm_net_gbp` and `level_advantage_gbp` excluded by
construction and named as such — they are the response's own second term). The event is real, worth
about £5,388, fires in roughly a fifth of draws, and is invisible to every field recorded.

**Owed work, in order, and none of it needs more seeds.**

1. Carry **`selection_by_account_gbp`** (per `customer_id`, `value_arm_net − level_arm_net`) into the
   arm runner's output. Both sides already exist in every run — `simulation/run_phase1e.py` sums
   `net_margin_gbp` per `customer_id` off `phase2b.all_records` and the split is discarded when
   `_arm_measure` folds it to `total_net_gbp`. A field carried, not a model changed.
2. **Diff one low-state seed against one high-state seed** on that field. Low-state seeds are 11111,
   44444, 99999, 111111. Two runs name the £5,388 event; 700 more seeds would not.
3. Replace the Gaussian bound on this family with the mixture bound wherever it is consumed, or
   state on the surface that the instrument's shape is a switch. `tools/selection_residual_
   decomposition.residual_is_a_mixture_or_a_spread` is the check and it reports either verdict.

**No published figure changes and none is withdrawn.** The director's 2026-09-26 ruling stands and
this strengthens its reason: served −£960 and today's +£170 are two draws from one unpinned switch.

**Book depth is NOT the cause, though the director's picture of the book is right.** Renewal count
explains none of the variance (best of eleven pre-registered regressors R² 0.0284, 90% interval
0.0000–0.2845, permutation p 0.8245 against a null whose median best-of-eleven is 0.0971 — the
observed best is below chance). Half the scored accounts face exactly one priced renewal and only
1.5% face five or more, so a choice has almost nothing to compound through — but that shallowness is
a constant of the term calendar the elasticity re-draw does not move, and a constant cannot carry
seed-to-seed variance. Two of the depth regressors are identical on all 18 seeds.

## 2026-09-28: the write-off rule does not move the sign; C1 is the open question, and it is being run

- **The balance-at-close rule, alone.** Graded one-variable against its `cefd2c04a` baseline in
  `records/SEAT_RESULT_THE_TWO_STATE_DIFF_RERUN_UNDER_THE_BALANCE_AT_CLOSE_RULE_2026-09-28.md`:
  - both seeds keep their sign (−£4,834.56 / +£949.49);
  - `PROS-2016-0098` still holds the switch (Herfindahl 0.9946);
  - the rule widens it by £477.
- **What is left** is the stayer's provision (leg 4b). It acts in exactly the state where that
  account stays, and its rate turns on C1: is a sim DD failure a first bounce (7.4% at >90d) or
  net of retries (50.3%)? `fcba478b7` wires it with no default.
- **The bracket.** Three runs from that one commit are in flight:
  - (a) leg 4b off;
  - (b) the DD row;
  - (c) the pay-on-receipt row.
  They are pre-registered in `records/SEAT_PREREG_THE_C1_BRACKET_THREE_RUNS_AT_ONE_COMMIT_2026-09-28.md`
  and due back about 2026-09-28 17:00Z.
- **Which outcome holds is NOT YET KNOWN.**
  - If (b) and (c) agree on both seeds' signs, C1 does not matter to the sign.
  - If they disagree, "we cannot tell" goes on the page with C1 named as the reason.
  - The director was asked the practitioner question at 03:03Z (NTFY `N8U7crm2DRQP`).

## 2026-09-28: steps 1–3 are done, and the finding leaves BLOCKING

- **Steps 1 and 2** landed in `cefd2c04a`: the per-account field is carried, and the low/high diff
  puts the switch on `PROS-2016-0098`.
- **Step 3 has landed.** `selection_residual_decomposition.gaussian_or_mixture_bound` is the one
  door every producer and surface now asks before printing a standard error:
  - both floor writers in `run_value_cycle_ab`, through `bound_on_its_shape`;
  - the fold's `_leg`, for every leg and not only selection;
  - the page's cross-code row, which asks the seeds directly because every artefact on disk was
    written before the gate existed.
- **What the gate does on a switch.** No sem, no `sems_from_zero`, no seed price. The bound is the
  rate's exact 90% interval carried to the mean, and the sign is stated only when that interval
  sits wholly on one side of zero.
- **What the page now says.** The HEAD row reads *£169.60 on 18 seeds, which fall into two states
  … the mean's 90% interval from how often the switch fires is −£997.69 to £937.49*. It used to
  read "0.31 standard errors from zero". The served row is a spread (separation 0.40) and is
  unchanged.
- **Controls.**
  - `test_a_two_cluster_family_is_refused_the_gaussian_path_at_every_producer_door`, with the
    spread and too-small families in the same control.
  - `test_a_switch_wholly_one_side_of_zero_states_that_sign`, the rare branch.
  - `test_a_switch_family_publishes_its_mixture_interval_and_no_standard_error` (generator).
  - The door's `BOTH_readings` rung.
  - Mutation-checked at landing (2026-09-28): forcing `gaussian_licensed` True on the switch
    branch reds the two `selection_residual_decomposition` controls and the generator control.
    The door rung does NOT red on that mutation, and should not: it reads the committed feed,
    not the generator. Its own mutation (the renderer's `r.switch` branch forced false) reds it.
- **Why LATENT and not closed.** Nothing published now carries a Gaussian bound on a switch.
  - **Checked:** every floor artefact on disk was run through the check.
  - **Switches found:** the HEAD 18 (9.4) and `five_seed_head` (3.27), neither of them in a
    Gaussian sentence now. Also `20260909b` (2.07), whose selection verdict `current_world`
    already withholds with a null sem.
  - **Still open:** the C1 bracket above. It bears on the sign, not on the bound.
- **Worth knowing.** The gap statistic's cut of 2.0 is the instrument's convention, not a sourced
  number. `20260909b` clears it by 0.07 on nine draws, so a switch reading that marginal is weak.

## Landing note (2026-09-28)

- Landed from the shared tree's uncommitted edits as HEAD plus this work's hunks only.
- `tests/tools/test_fold_noise_floor_family.py` in the shared tree also carries two things that
  are NOT this work, so they were left out:
  - the `_producer_made_floors` witness selector, from the 09-10 fold-witness episode;
  - the deletion of both `value_arm_pairing` controls, which are live at HEAD. Landing the file
    whole would have deleted them.
- `site/data/value_arms.json` is HEAD's feed with only `selection_across_code` regenerated.
  A full regeneration also moved the memory-ceiling block and the publishing-commit stamps,
  which are environment drift and not this change.
