**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

# INSTRUCTION — grade the two-seed per-account diff against its pre-registration, P0 FIRST

Filed 2026-09-27 on releasing the Lane 0 continuation
`carry-per-account-selection-out-of-the-arm-runner`. **The carry is done and landed** — the column
at `ca80a7d0a`, the missing level-only partition control at `f18918ebf`. This is the one step of
that item that could not be done in the same invocation, because it waits on a run that was still
in flight. `--hand-off` refuses a released item, so it is queued here instead: otherwise a two-hour
run lands its artefact and nothing is pointed at reading it.

## The precondition

`longjob-two-state-account-diff-20260927` was `active` at 2026-09-27T04:39Z, 1h10m in, against a
revised expectation of ~2h (`_HOURS_PER_FLOOR_SEED` was measured on an idle box; three lanes were
running full suites). The artefact is **all-or-nothing** — written only after both seeds finish, so
a killed run yields nothing and must be relaunched whole with the same command.

1. `python3 -m background.launch_liveness --check` — if the unit died with no artefact, relaunch:
   `python3 -u -m tools.run_value_cycle_ab --level-arm --noise-floor-seeds 11111,88888 --out
   docs/observability/value_cycle_ab_s1_two_state_diff_20260927.json`
2. `python3 -m tools.selection_residual_decomposition --account-diff
   docs/observability/value_cycle_ab_s1_two_state_diff_20260927.json`

## Done means

**P0 is graded FIRST and it is a gate, not a row.** P0 is the reproduction control: seed 11111 must
return `selection_gbp` within £1 of −£3,802.80 and 88888 within £1 of +£1,548.26, both with
`value_arm_net_gbp` £180,433.56. The shard those came from was folded at `ba9bc6733`; this runs at
`f7910cbc1` plus the carried field. **If P0 fails, that is the result and P1–P5 are void** — the
diff would then be between two worlds rather than two draws, and reporting the per-account reading
anyway is the exact error the seed pair was chosen to avoid.

If P0 holds, grade P1–P5 against
`docs/staging/records/SEAT_PREREG_WHICH_ACCOUNTS_THE_TWO_STATE_SELECTION_SWITCH_LIVES_IN_AND_WHETHER_PER_ACCOUNT_CONTRIBUTIONS_ARE_INDEPENDENT_2026-09-27.md`,
which was written before the run was launched. **Wrong predictions are kept beside the answers** —
that is the only evidence the experiment was designed before its answer was known. Land the result
as a record.

## Two things the grader must not do

* **Do not quote the truncated 2016–2017 smoke reading as the answer.** Herfindahl 0.179, 5.6
  effective accounts of 91, `/tmp/smoke_by_account.json`. Different window, smaller book, run to
  prove the field reached a real artefact. The pre-registered reading is the full window at the
  commit-pinned world `39a192ce04c1eda8`.
* **Do not read a level-only count of zero as the column working.** The smoke run had one
  one-arm-only account and it was value-arm-only; the landed controls never peopled the level-only
  branch at all until `f18918ebf`. If this run also reports zero level-only accounts, that is a
  fact about the book, not a check on the code — see
  `docs/staging/records/SEAT_FINDING_THE_LEVEL_ONLY_BRANCH_OF_THE_PER_ACCOUNT_COLUMN_IS_UNREACHED_BY_EVERY_CONTROL_AND_BY_THE_ONE_REAL_READING_2026-09-27.md`.

## Why it matters

The Herfindahl of per-account contribution decides the director's actual question: whether the 1/k
book-depth ladder's independence premise holds at all. `seeds_needed_under_a_deeper_book` reports
seeds falling as 1/k, which assumes per-account contributions are independent. If the residual is a
handful of large offsetting flows rather than a broad aggregate of small repricings, that ladder is
quoting a bound for a mechanism it does not describe.
