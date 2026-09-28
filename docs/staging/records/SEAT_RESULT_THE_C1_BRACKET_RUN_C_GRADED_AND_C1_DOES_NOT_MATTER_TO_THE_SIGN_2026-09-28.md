**Severity:** LATENT · **Lane:** A_strategy_governance · **Atom:** `value-arms-error-bar` · **Class:** `measurements_that_mirror`

# The C1 bracket, run (c) graded: C1 does not matter to the sign

**2026-09-28, ~16:50Z.** This closes the grading of
`SEAT_PREREG_THE_C1_BRACKET_THREE_RUNS_AT_ONE_COMMIT_2026-09-28.md`. Runs (a) and (b) were graded
in `SEAT_RESULT_THE_C1_BRACKET_RUNS_A_AND_B_GRADED_AND_C_PREDICTED_2026-09-28.md`, which also filed
a prediction for (c) before (c) returned. This record grades both.

## Validity

(c)'s artefact `/var/tmp/se-c1-bracket-c/value_cycle_ab.json` has `producing_commit`
`fcba478b7`, bound at 12:39:25Z, which is the relaunch. **Valid.** The voided first start is
recorded in the sibling record. (b)'s deviation stands as recorded there.

## The numbers

| | (a) unset | (b) `still_in_dd` | (c) `fallen_out_of_dd` |
|---|---|---|---|
| seed 11111 selection | −3,508.25 | −3,507.32 | −3,501.47 |
| seed 88888 selection | +706.67 | +707.60 | +713.40 |
| state distance | −4,214.93 | −4,214.93 | −4,214.88 |
| `PROS-2016-0098` state diff | −4,218.43 | −4,218.43 | −4,218.43 |
| Herfindahl / effective accounts | 0.9926 / 1.01 | 0.9926 / 1.01 | 0.9926 / 1.01 |
| `[leg 4b]` totals (six lines) | off | 1,926.24–1,967.73 over 105–106 | 13,200.51–13,482.57 over 109–110 |

(c)/(b) ratio of the `[leg 4b]` line totals, line by line: 6.852, 6.854, 6.854, 6.853, 6.854,
6.854.

## Grades against the prereg

- **C1: HELD** (graded in the sibling record).
- **C2: HELD.** (b) in £1,500–£4,000 (sibling record); (c) £13,200.51–£13,482.57, inside
  £12,000–£25,000.
- **C3: HELD, at the bottom edge.** 6.85 in [6.8, 9.0]. The >90-day row (50.3/7.4 = 6.80) carries
  almost all of it; the younger bands add 0.05.
- **C4: HELD on its test, REFUTED on its mechanism** (sibling record).
- **C5: FAILED.** Seed 11111 moved +£6.78 toward zero, not ≥ £3,000. The mechanism C5 assumed —
  `PROS-2016-0098` carrying a stayer's failed-DD balance in one state only — does not exist: that
  account's −£4,218.43 is a leaver's write-off at close and it leaves in both states
  (`SEAT_RESULT_PROS_2016_0098S_4218_IS_A_LEAVERS_WRITE_OFF_AND_IT_LEAVES_IN_BOTH_STATES_2026-09-28.md`,
  `875322e5a`). Leg 4b excludes leavers by design.
- **C6: HELD, for the wrong reason.** Seed 11111 stays negative. The 55% lean was about B crossing
  ~£9,600 on that account; B on that account is zero.

## The sibling record's prediction for (c), graded

- State distance −£4,214.93 ± £1: **HELD** (−£4,214.88).
- Selection shift roughly +£6 to +£15, the same in both seeds: **HELD** (+£6.78 and +£6.73).
  0.93 × 6.85 = £6.37 was the point estimate; the extra ~£0.40 is below.
- Both signs hold; C5 fails; C6 holds: **HELD**.
- The named way it could be wrong — `fallen_out_of_dd` reaching a stayer set that `still_in_dd`
  does not, through the 4.5%-vs-0 younger-band row — **happened, and did not matter.** (c)
  provisions 109–110 stayers against (b)'s 105–106, so four more households are reached. The
  state distance moved £0.05 and the seeds' shifts differ by £0.05. Whatever those four carry,
  they carry it in both states.

## The decision rule, applied

(b) and (c) both keep both seeds' signs. **C1 does not matter to the sign.** C1 stays a named gap
for the level figures only, where it is large: leg 4b moves each arm's net by about £1,930 under
`still_in_dd` and about £13,230 under `fallen_out_of_dd`, a £11,300 bracket on every arm's level,
and no published source picks the row. That bracket belongs on any level figure that is published
with leg 4b on; leg 4b is off at HEAD by default, so nothing published carries it today.

The director's NTFY `N8U7crm2DRQP` (the practitioner question: is a sim DD failure a first bounce
or net of retries) has no recorded answer. It no longer bears on the sign; it still decides the
level row, and it is not urgent while leg 4b is off.

## What this does NOT say

The selection sign was never shown to be stable — it is a two-state switch on one account, and
that is `SEAT_FINDING_THE_SELECTION_RESIDUAL_IS_A_TWO_STATE_SWITCH_…`'s subject. This bracket shows
only that C1 cannot move which state each seed lands in.
