**Severity:** LATENT · **Lane:** D_billing_metering · **Atom:** `unminted` · **Class:** `measurements_that_mirror`

# The C1 bracket: does the failed-DD stayer's bucket decide the selection sign? Predictions before any run

**2026-09-28.** Filed in the same commit as the code it measures. Every run below starts after this
commit exists, and its artefact's `producing_commit` must equal this commit or the run is void.
This follows `SEAT_RESULT_THE_TWO_STATE_DIFF_RERUN_UNDER_THE_BALANCE_AT_CLOSE_RULE_2026-09-28.md`
and the C1 finding
(`docs/staging/SEAT_FINDING_THE_STAYER_PROVISION_RATE_IS_SOURCED_BUT_WHICH_BUCKET_A_FAILED_DD_STAYER_SITS_IN_TURNS_ON_C1_WHICH_HAS_NO_SOURCE_2026-09-27.md`).

## What this commit wires

Leg 4b of `simulation/arrears_engine.py` now works as follows:

- It provides on each **stayer's** open failed-DD balance, net of netted credits.
- The provision is a 31-Dec stock at Centrica's 2025 age×method rates, and the P&L is charged its
  yearly change.
- The rates are in `LIVE_ARREARS_PROVISION_RATES`, cited to
  `docs/market_research/dd_failure_basis_and_live_arrears_provision_rates.md`.
- Which row applies is the C1 gap. It is read from `SIM_STAYER_FAILED_DD_BUCKET`, and it has **no
  default**: unset means leg 4b is off, which is the behaviour before this commit.
- A value that names no bucket is refused, with the reason.
- The two rows at >90 days are 7.4% (`still_in_dd`) and 50.3% (`fallen_out_of_dd`).
- Leavers are excluded because their provision releases into the write-off at close.

## The runs

All three run from one clean detached worktree of this commit at `/var/tmp/se-c1-bracket-src`.
They run one after another, never together, each as a `launch_long_job` unit. The command is
`python3 -u -m tools.run_value_cycle_ab --level-arm --noise-floor-seeds 11111,88888 --out <artefact>`.

| run | `SIM_STAYER_FAILED_DD_BUCKET` | artefact |
|---|---|---|
| (a) | unset: HEAD's rule | `/var/tmp/se-c1-bracket-a/value_cycle_ab.json` |
| (b) | `still_in_dd` | `/var/tmp/se-c1-bracket-b/value_cycle_ab.json` |
| (c) | `fallen_out_of_dd` | `/var/tmp/se-c1-bracket-c/value_cycle_ab.json` |

Logs are at `/var/tmp/longjob-c1-bracket-{a,b,c}-20260928.log`. (b) waits on (a)'s pid. (c) waits
on (a) and then on (b). Each takes about 4.5h, so all three return about 13–14h after launch.
Grading: run `--account-diff --json <dir>/account_diff.json` on each, then grade below, in a
`SEAT_RESULT_` record beside this one.

**Each of (b) and (c) differs from (a) in ONE variable, the bucket.** (a) differs from last
night's `d993a9797` run in four world/ledger commits (`2bb03a094`, `ba1b6c259`, `a4116acea`,
`b33f08d2e`). That comparison is reported as context, never attributed.

## Predictions

- **C1.** (a) keeps last night's shape: seed 11111's selection is negative, 88888's positive,
  and Herfindahl > 0.9 on `PROS-2016-0098`. *Weakest of the six*: the gas summer base and the
  lost consumption floor add real bills, so the roster can move.
- **C2.** The `[leg 4b]` line each sim run prints totals between £1,500 and £4,000 in (b), and
  between £12,000 and £25,000 in (c). The basis is the £37,109.27 stayer open total at mostly
  >90 days. Credit netting and the younger bands pull it down.
- **C3.** The (c)/(b) ratio of those totals lies in [6.8, 9.0]. It is 50.3/7.4 = 6.8 at >90
  days, and every younger band's ratio is higher (15.1/1.4; 4.5/0).
- **C4.** (b) moves each seed's selection by less than £1,000 from (a), and both signs hold.
  7.4% × B is ≥ £500 on `PROS-2016-0098` alone.
- **C5.** (c) moves seed 11111's selection (the state where `PROS-2016-0098` stays in the level
  arm) toward zero by at least £3,000 from (a). That is p·B with B ≥ £6,766.59.
- **C6. The sign in (c).** I lean, weakly (55%), that seed 11111 stays negative. The crossover
  needs B ≥ ~£9,600 at 50.3%. The stay fate is billed for longer, so B exceeds the leave-fate
  £6,766.59, but I do not know by how much. This is the prediction the run exists to refute.

## The decision rule, fixed now

- If (b) and (c) both keep both seeds' signs, **C1 does not matter to the sign**. The selection
  finding says so, and C1 stays a named gap for the level figures only.
- If (b) and (c) disagree on any seed's sign, the page carries **"we cannot tell"**, with the
  reason named: *the sign turns on whether a sim DD failure is a first bounce or net of retries,
  and no published source says which.* The director's practitioner answer then decides which
  row is the live one.

## How to reverse

Unset the variable: leg 4b is off by default. To remove the wire, revert this commit.
