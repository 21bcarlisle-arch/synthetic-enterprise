**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`
**Class:** `measurements_that_mirror`

# Pre-registration: which accounts the two-state selection switch lives in, and whether per-account contributions are independent

**2026-09-27, written before the run was launched and before any per-account number was computed.**
Continues `SEAT_RESULT_RENEWAL_COUNT_EXPLAINS_NONE_OF_THE_SELECTION_RESIDUAL_AND_THE_VARIANCE_IS_ONE_DISCRETE_EVENT_IN_THE_LEVEL_ARM_2026-09-27.md`
(commit `d678f063a`), which established that the residual's variance is 99.84% the level arm's own
net, moving as a two-state switch £5,387.65 apart in 4 of 18 elasticity draws, and that **none of
the 14 fields the shard records has disjoint ranges between the two states**. The switch is driven
by something no artefact on disk carries.

## What was built first, because the measurement is impossible without it

`tools/run_value_cycle_ab.py` now carries a per-account column: `realised_metrics` publishes
`net_by_billing_account_gbp` (the same `settled-realised` sum it already folds to `total_net_gbp`,
cut by billing account) and `renewals_priced_by_account` (distinct priced term starts per account,
declines excluded); `level_vs_selection.by_account` differences the two arms' columns and publishes
the concentration reading; and the noise-floor row carries the whole column per seed. **A field
carried, not a model changed** — nothing crosses the epistemic wall, and `sum(column)` is asserted
equal to `value_net − level_net` to a penny, which is what stops the column being published beside
a residual it is not a decomposition of.

## The design: a ONE-VARIABLE diff, and the seeds are chosen for it

The 18-seed family's `value_arm_net_gbp` takes only four distinct values, and **two seeds share one
of them exactly** while sitting in opposite states:

| seed | state | `selection_gbp` | `level_arm_net_gbp` | `value_arm_net_gbp` |
|---|---|---|---|---|
| **11111** | low | −£3,802.80 | £184,236.35 | **£180,433.56** |
| **88888** | high | +£1,548.26 | £178,885.29 | **£180,433.56** |

So on this pair the value arm's net is *identical* and the entire £5,351.06 difference in the
residual is the level arm's. That is a one-variable contrast, and it is a better instrument than a
pair drawn at random from the two clusters (where both arms move and neither difference can be
attributed). World `39a192ce04c1eda8`, `--redraw-key elasticity --redraw-mode all`, clock
`settled-realised`.

## P0 — the reproduction control, and every reading below is void if it fails

The shard was folded at commit `ba9bc6733`; this runs at `d00e0a309` plus the carried field. **Seed
11111 must return `selection_gbp` within £1 of −£3,802.80 and seed 88888 within £1 of +£1,548.26,
and both must return `value_arm_net_gbp` = £180,433.56.** If they do not, the tree has moved this
quantity between the two commits and the diff is between two worlds rather than two draws — in
which case the result is that finding and nothing else. This is stated first because it is the leg
most likely to fail and the one whose failure is easiest to explain away after the fact.

## The predictions

**P1 — the difference is concentrated in at most 3 billing accounts.** Ranking the two seeds'
`selection_by_account_gbp` columns by the absolute size of their difference, **≤ 3 accounts hold
≥ 90% of the total absolute difference**. *Refuted if* it takes 10 or more, which would mean the
"one discrete event" reading of the £5,388 was wrong and the state distance is many small shocks
that happen to be bimodal in aggregate.

**P2 — it is a ROSTER difference, not a repricing difference.** At least one billing account either
(a) settles in the level arm at one seed and not at the other, or (b) has a level-arm net differing
between the seeds by more than £3,000. *Reasoning:* the level arm applies ONE uplift, so its price
per renewal is the same in both states; a £5,351 swing is the order of a whole account's lifetime
settled margin, which a margin-per-MWh difference at one renewal cannot produce. *Refuted if* the
largest single-account level-arm difference is under £1,000 — which would point at a diffuse
consumption or bad-debt mechanism instead, and would make P1 false too.

**P3 — per-account contributions are NOT independent, so the 1/k book-depth ladder is optimistic.**
Within a single seed, the Herfindahl of absolute per-account contribution is **> 0.10** (effective
accounts < 10, against ~164 settled). *Why it matters:* `selection_residual_decomposition.
seeds_needed_under_a_deeper_book` reports 826.9 seeds falling as 1/k under a k-fold book, and that
scaling assumes contributions are i.i.d. so the mean grows as k while the sd grows as √k. At
effective-accounts < 10 the premise is false and a deeper book of similar households buys far less
than the table claims. *Refuted if* the Herfindahl is below 0.02 (effective accounts > 50), which
would mean the ladder is sound and the honest recommendation is to buy the seeds.

**P4 — per-account renewal depth still explains nothing.** `depth_against_money.spearman_rho` has
|ρ| < 0.4 on both seeds. This is the first version of the director's book-depth hypothesis the data
can refute rather than decline: at seed level two of the depth regressors were literally constant
across all 18 seeds, so their R² of zero was a fact about the instrument. Per account there is
variance. *Refuted if* ρ > 0.4 — in which case depth IS the lever per account and the seed-level
null was an aggregation artefact, which would be the more interesting result.

**P5 — the instrument's own reading, stated separately because a pre-registered count predicts the
INSTRUMENT and not the world.** `gross_absolute_movement_gbp` will exceed |residual| by more than
2×, i.e. the residual is the small difference of larger offsetting per-account flows. This is a
claim about how much cancellation the column shows and it is separable from P1–P3: a concentrated
column with little cancellation and a concentrated column inside heavy cancellation imply the same
Herfindahl and different remedies.

## What the instrument was shown to be able to say, before it was pointed at the world

Printed across four synthetic books of 154 accounts with the same shape as the real one, because a
concentration statistic that cannot separate the hypotheses is not worth running:

| book | residual | gross | gross/net | Herfindahl | effective accounts | accounts for 90% | largest |
|---|---|---|---|---|---|---|---|
| diffuse noise only | £502 | £5,175 | 10.3 | 0.0093 | 107.9 | 104 | £97 |
| one £5,388 account | £5,890 | £10,563 | 1.8 | **0.2661** | **3.8** | 83 | £5,426 |
| one account in one arm only | £1,596 | £6,268 | 3.9 | 0.0389 | 25.7 | 100 | £1,132 |
| both | £7,356 | £12,014 | 1.6 | 0.2204 | 4.5 | 79 | £5,426 |

The Herfindahl moves 29× between the diffuse book and the one-big-account book, and
`gbp_from_accounts_in_one_arm_only` isolates the roster cause from the repricing cause. So P1, P2
and P3 are separately answerable by this instrument and not three readings of one number.

## Reproduce

    python3 -m tools.run_value_cycle_ab --level-arm --noise-floor-seeds 11111,88888 \
        --out docs/observability/value_cycle_ab_s1_two_state_diff_20260927.json
