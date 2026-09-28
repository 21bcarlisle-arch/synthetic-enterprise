**Severity:** LATENT · **Lane:** D_billing_metering · **Atom:** `unminted` · **Class:** `measurements_that_mirror`

# The C1 bracket, runs (a) and (b) graded. (b) predicts (c): the sign cannot turn

**2026-09-28, 13:20Z. This is a partial grading.** It grades the prereg
`SEAT_PREREG_THE_C1_BRACKET_THREE_RUNS_AT_ONE_COMMIT_2026-09-28.md` against (a) and (b).

Run (c) (`fallen_out_of_dd`) is still running. Its first start was voided at `6c34daa36` (see
`../SEAT_FINDING_TWO_PATTERN_WAITERS_ON_ONE_SUBJECT_SAW_EACH_OTHER_AND_STALLED_THE_C1_BRACKET_2026-09-28.md`).
It was relaunched at 12:39Z at `fcba478b7` as `longjob-c1-bracket-c-20260928`, and should return
around 16Z.

**Still open until (c) returns:** C3, C5, C6, the (c) half of C2, and the decision rule. The
prediction for (c) below was filed **after** reading (b) and **before** (c) returned. It is a
prediction, not a result.

## Validity

| run | `producing_commit` | verdict |
|---|---|---|
| (a) | `fcba478b7` | valid |
| (b) | `994602944`, a fork_salvage commit on top of `fcba478b7` | **deviation, recorded here, with the evidence below** |

`git diff --name-only fcba478b7 994602944` shows only `docs/` paths. "Docs-only" does not prove
"no effect", because the sim reads several of those files:

- `docs/observability/book_growth_campaign.json` is read by `simulation/net_new_acquisition.py`
  and others.
- `book_subset_verdict.json` is read by `simulation/live_population.py`.
- `coupled_gap_ledger.json` is read by `simulation/fabric_physics.py`.

So I measured the effect instead of arguing it. Between (a) and (b), each arm's net moved by
exactly that arm's own `[leg 4b]` charge, to the penny:

| arm (seed 11111) | (a) net | (b) net | change | leg 4b in (b) |
|---|---|---|---|---|
| control | 174,947.71 | 172,979.98 | −1,967.73 | 1,967.73 |
| value | 183,906.94 | 181,976.29 | −1,930.65 | 1,930.65 |
| level | 187,415.19 | 185,483.61 | −1,931.58 | 1,931.58 |

Seed 88888 behaves the same way: its level arm moves 183,200.27 → 181,268.69, which is −1,931.58.
Nothing besides the one variable moved any arm by even a penny. **(b) is accepted as a
one-variable run, and the deviation stays on the record.**

## Grades

- **C1: HELD.**
  - In (a), seed 11111's selection is −£3,508.25 and seed 88888's is +£706.67.
  - Herfindahl is 0.9926, with 1.01 effective accounts.
  - `PROS-2016-0098` moves £4,218.43 of the £4,234.22 gross, all of it through the level arm.
  - The state distance is −£4,214.93.
  - This is last night's shape, and the four world/ledger commits did not move the roster.
- **C2, (b) half: HELD.**
  - The six `[leg 4b]` lines total between £1,926.24 and £1,967.73, over 105–106 stayers.
  - The predicted band was £1,500–£4,000.
- **C4: HELD on its stated test, REFUTED on its stated mechanism.**
  - The stated test held. Each seed's selection moved by +£0.93, far under £1,000:
    - 11111: −3,508.25 → −3,507.32
    - 88888: +706.67 → +707.60
  - Both signs hold.
  - The mechanism was refuted. C4 said "7.4% × B is ≥ £500 on `PROS-2016-0098` alone". That
    account's state diff is −£4,218.43 in **both** runs. Leg 4b put nothing on it that differs
    between the two states.

## What (b) shows that the prereg did not expect

In (b), the level arm's leg-4b charge is **£1,931.58 in both seeds**, and the value arm's is
£1,930.65 in both. The provision is identical across the two states, so it cannot move the state
distance. The state distance is −£4,214.93 in (a) and in (b).

C5 and C6 assumed that the household that switches the state carries a failed-DD balance that
leg 4b would provision in one state and not the other. In (b) it does not.

I cannot yet say why. Two readings fit, and I have not run the control that separates them:

1. `PROS-2016-0098`'s £4,218 is not an open failed-DD balance at any 31 December. For example,
   it could be revenue, or a leaver-fate write-off that leg 4b excludes by design.
2. The `churned_ids` that the arrears engine receives do not carry the stay/leave split that
   the value cycle's state does.

Either reading predicts the same thing for (c).

## Prediction for (c), filed before it returns

leg 4b only rescales a charge that does not depend on the state. So:

- **State distance:** stays at −£4,214.93 ± £1.
- **Selection shift:** each seed moves by about 0.93 × the (c)/(b) leg-4b ratio, the same in
  both seeds. That is roughly +£6 to +£15.
- **Signs:** both hold. 11111 stays negative and 88888 stays positive.
- **C5:** FAILS. Seed 11111 moves by far less than £3,000.
- **C6:** HOLDS. It leaned 55% on the right answer for the wrong reason.
- **C3:** I do not predict separately. I keep the prereg's [6.8, 9.0].
- **Decision rule outcome:** "C1 does not matter to the sign." C1 stays a named gap, for the
  level figures only.
- **Confidence:** about 90%. The main way this is wrong: the `fallen_out_of_dd` row reaches a
  stayer set that `still_in_dd` does not, through a younger band's 4.5%-vs-0 row, and that set
  differs between states. (b) cannot see that, because its 0% cells hide it.

## Grading (c) when it returns

1. Run `--account-diff --json /var/tmp/se-c1-bracket-c/account_diff.json` on the (c) artefact.
2. Check that its `producing_commit` is `fcba478b7`.
3. Grade C2(c), C3, C5, C6 and the decision rule beside this record, and grade this record's
   prediction for (c) in the same place.
