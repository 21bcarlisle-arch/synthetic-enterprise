**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`
**Class:** `measurements_that_mirror`

# The per-account selection column is carried and its reader is built; the two-seed diff is still running

**2026-09-27, `ca80a7d0a` on origin/main.** Interim record so the next invocation does not re-derive
this. Graded against
`SEAT_PREREG_WHICH_ACCOUNTS_THE_TWO_STATE_SELECTION_SWITCH_LIVES_IN_AND_WHETHER_PER_ACCOUNT_CONTRIBUTIONS_ARE_INDEPENDENT_2026-09-27.md`,
written before the run was launched. **No prediction is graded here.** The full-window numbers do
not exist yet, and a partial answer stated now would be a prediction filed after seeing half of it.

## What is done and landed

`realised_metrics` publishes `net_by_billing_account_gbp` and `renewals_priced_by_account` per arm;
`level_vs_selection.by_account` differences the two arms' columns with the sum asserted equal to
`value_net − level_net` to a penny, and publishes the concentration reading and the
roster-versus-repricing split; the noise-floor row carries the whole column per seed plus **both
arms' own columns**, because a difference whose two terms are absent cannot say which term moved and
99.84% of the variance is the level arm's. `tools/selection_residual_decomposition.py
--account-diff` reads it: it cuts the seeds into the two states with the *same* largest-gap helper
`residual_is_a_mixture_or_a_spread` uses, differences the states' mean per-account columns, and
splits each account's move into the value arm's part and the level arm's.

25 new controls; 21 mutations fired. Three of them were green on the first pass and each named a
real gap rather than an equivalence: `moved_mostly_by` hard-wired to `"the level arm"` passed every
fixture drawn from a finding *about* the level arm; a one-seed shard reached an arithmetic error
three frames down instead of the loader's named refusal; and the movement Herfindahl taken over the
signed state distance was indistinguishable from the right denominator until a fixture moved two
accounts in opposite directions. One mutation is an **equivalence and is recorded as one** —
dropping `abs()` from inside the Herfindahl's square cannot fire, because `(-x)**2 == x**2`.

## The one real-data reading that exists, and what it is NOT

A three-arm pass over a **truncated 2016–2017 window** (`/tmp/smoke_by_account.json`, run to prove
the field reaches a real artefact before an hour was spent on the full window):

| | |
|---|---|
| accounts in the union | 91 |
| residual | −£1,351.47 — equal to `selection_gbp` to the penny |
| gross absolute movement | £2,064.55 |
| gross/net | 1.53 |
| Herfindahl | 0.179 → **5.6 effective accounts of 91** |
| accounts holding 90% of gross movement | 9 |
| largest single contribution | C5, −£695.93 |
| accounts in one arm only | 1 (C5_2, value arm, +£202.34) |
| `depth_against_money` | **REFUSED** — every one of the 29 priced accounts faces exactly one priced renewal on a two-year window, so depth has no variance |

**This is not the answer to P3 and must not be quoted as one.** It is a two-year window on a
smaller book, run for a different purpose, and the pre-registered reading is the full window at the
commit-pinned world `39a192ce04c1eda8`. It is recorded because it is the only per-account
concentration figure that exists at the time of writing, because its direction is worth knowing
before the run lands, and because the honest way to hold it is where the caveat is attached.

## What is in flight

`longjob-two-state-account-diff-20260927` — `--noise-floor-seeds 11111,88888` on the full window,
writing `docs/observability/value_cycle_ab_s1_two_state_diff_20260927.json`. Launched
2026-09-27T03:29:02Z; **45 minutes in, the first seed had not completed**, against a
`_HOURS_PER_FLOOR_SEED` estimate of 0.43h. That estimate is not wrong so much as measured on an
idle box: three other lanes were running full pytest suites concurrently. Expect ~2h, not ~1h.
Liveness: `python3 -m background.launch_liveness --check`. The artefact is written only after BOTH
seeds finish, so a killed run yields nothing and must be relaunched whole.

The seed pair is a **one-variable contrast and that is why those two**: across the 18-seed family
`value_arm_net_gbp` takes only four distinct values, and 11111 (low state, `selection_gbp`
−£3,802.80) and 88888 (high state, +£1,548.26) share one of them exactly (£180,433.56). So the
entire £5,351.06 difference in their residuals is the level arm's, and the diff has one term in it.

## What the next invocation does

1. `python3 -m background.launch_liveness --check` — if the claim has settled and the artefact
   exists, go to 2; if the unit died, relaunch the same command (the artefact is all-or-nothing).
2. `python3 -m tools.selection_residual_decomposition --account-diff
   docs/observability/value_cycle_ab_s1_two_state_diff_20260927.json`
3. **Grade P0 FIRST.** P0 is the reproduction control: seed 11111 must return `selection_gbp` within
   £1 of −£3,802.80 and 88888 within £1 of +£1,548.26, both with `value_arm_net_gbp` £180,433.56.
   The shard those came from was folded at `ba9bc6733`; this runs at `f7910cbc1` plus the carried
   field. **If P0 fails, that is the result and the rest is void** — the diff would be between two
   worlds rather than two draws.
4. Grade P1–P5 against the pre-registration and file the result beside it, wrong predictions kept
   next to the answers.
