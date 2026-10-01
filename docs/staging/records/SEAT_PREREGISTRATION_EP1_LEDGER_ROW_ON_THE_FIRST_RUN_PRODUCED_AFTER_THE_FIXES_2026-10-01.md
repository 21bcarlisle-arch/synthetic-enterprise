**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# PRE-REGISTRATION — EP1's ledger row on the first run produced after the day's fixes

Filed 2026-10-01, before `tools.couple_clv` has been run on this output. Autonomous worker,
self-refill draw of `EP1_clv_three_horizon`.

## Why the row is owed

The ledger's EP1 row is stamped `run_git_commit: b1b4c284e`. That run predates every EP1 change
landed today: `81977a312`, `627f05756`, `7e2503507`, `127c007f0` and `9d6ad4551`. Two findings
said the row must wait for "a fresh run promoted through the ordinary publish path".
`docs/reports/run_output_latest.json` is now that run. It was generated at
`2026-10-01T09:33:41Z`, and its `producing_commit` is `af4709ff1`, which contains all five.

## What is being compared

The previous level, 1.066 on 66 rows (Spearman 0.122), was measured on snapshots REBUILT with the
fixed code over the OLD world (`b1b4c284e`). This run changes the world as well:

- `91214c720` (passive term end, SVT anniversary route);
- the year-one quote priced at the rate sold;
- the quote and the review on one basis.

The comparison therefore has two variables, the code and the world. **A move in the gap cannot be
attributed to EP1 by this row alone.** The row records the level. It does not grade a change.

## Predictions

- P1: `gap` lies in [0.85, 1.35]. The code that set 1.066 is unchanged, and the world change
  moves retention, which moves who is graded.
- P2: `counted_accounts` lies in [50, 90].
- P3: the belief still over-states on the majority of graded rows, but less than the old row's
  60 of 69. Selection on exit still favours over-statement.
- P4: Spearman(belief, realised) on the graded rows lies in [−0.1, +0.3]. Nothing shown at n≈66
  ranks lifetime margin.
- P5: `components.belief_provenance.grades_atom_estimator` is true.

The gap is a diagnostic, never a target (R12).

## Result (same day, after the predictions above were written)

`tools.couple_clv` over the `af4709ff1` output:

| | Prediction | Result |
|---|---|---|
| P1 | gap in [0.85, 1.35] | **1.081. HELD.** raw MAE £385.51 against g0 £356.62 |
| P2 | counted in [50, 90] | **69 of 248. HELD.** 158 right-censored |
| P3 | over-stated on a majority, fewer than 60 of 69 | **43 of 69. HELD.** Σ(belief − realised) is +£1.7k, down from +£41.3k |
| P4 | Spearman in [−0.1, +0.3] | **+0.172. HELD.** The old row read +0.110 |
| P5 | grades EP1's own estimator | **True. HELD** |

**The "two variables" section above was wrong, and it stays where it is so the record shows it.**
The world change did not reach the graded rows. They are the same 69 accounts with
bit-identical realised margins, and g0 is the same £356.62 to the penny. The cause is that every
world change in that list was either a finding with no code change (`91214c720`) or a new emitted
field that the hazard does not read yet (the experienced shock waits on PB4's swap). So on the
graded population, **the only thing that moved is the belief**. The ledger's 2.364 → 1.081 is a
one-variable reading of today's five EP1 commits taken together. It does not separate one commit
from another, and that split is the findings' arms. It agrees with the rebuilt-snapshot arm's
1.066 on 66 rows. The 3-row difference is that arm's own population.

What has not moved: the company's churn belief still sits at the 0.05 floor on every graded
renewal decision (38 decisions; 0.368 realised, so believed/realised is 0.14×). The book-wide life
table carries 6 distinct hazards across 69 accounts, so the tenure horizon still varies by tenure
position and never by account. That is the structural gap that
`SEAT_FINDING_EP1_THE_BELIEF_CARRIES_NO_PER_ACCOUNT_TENURE_…` names. It is not closed by this row.

**Not landed.** The gate refused the ledger write because of ten reds that are already on origin
and that this change does not touch (see the EP1 all-cause finding's last paragraph). This record
lands without the ledger. The number above is measured, not published.
