# Pre-registration: the theft screen switched on in the billing run, graded against the 19 Oct published run (2026-10-17, written before either run exists)

**Subject:** `DecisionPolicy.theft_screen_in_billing_run` (False everywhere today; built by
`3161365d3`). Finding:
`docs/staging/WORKER_FINDING_W2_36_THEFT_NOW_ARISES_AT_A_PREMISE_AND_AT_THE_IAS_OWN_VOLUME_IT_LOOKS_LIKE_A_VOID_2026-10-16.md`
("The screen reaches the billing run, behind a switch that is off").

## The one-variable run

- **Arm A (control):** the run the 2026-10-19 Monday publish promotes: the commit in its own
  `producing_commit.commit`, the default book seed (`SE_POPULATION_SEED` unset, base seed
  20260724), and the curriculum's default env.
- **Arm B (treatment):** that same commit with ONE line changed, `theft_screen_in_billing_run: bool
  = True` in `company/policy/decision_policy.py`, run through `simulation.run_phase4c_on_phase2b`
  under `background.launch_long_job` in a clean scratch worktree, with the same env. This is NOT the
  DD-review arm: each switch gets its own B.
- **Admission:** B passes `background.code_closure --arm`, and its `world_identity.digest` equals
  A's. Otherwise nothing below is graded.
- **Third instrument:** `python3 -m tools.theft_void_screen_probe --occupied-run <A's output>
  --billing-screen` on A's output must produce the same table as B's own `theft_screen` key.

## Where the sizes come from

The probe's switch-on arm on the 78f77c34e published book (987 accounts, 38,854 bills, 4 incoming
electricity accounts unlinked):

| Fuel / status / act | Flags | Accounts | Assessed kWh | Assessed £ | Unrecorded kWh (truth) |
|---|---|---|---|---|---|
| electricity / void / `bill_the_void` | 16 | 16 | 0 | 0.00 | 0 |
| electricity / investigate / `refer_for_investigation` | 0 | 0 | 0 | 0.00 | 0 |
| gas / not_screened / `none` | 0 | 0 | 0 | 0.00 | 0 |

The seat's structural grade of the same book agrees: 16 spans, all void. The run draws no theft:
the world's theft lives in `premise_theft_study`, not in the settled run, and nothing on origin
since 78f77c34e wires it in.

## Predictions (B against A, same commit)

**T1. No bill moves, and nothing else in the run moves either.** `bills` are identical in count and
amount, and so are revenue, gross margin, the ledger, the DD book and arrears. The only new content
is B's `theft_screen` key, which A lacks. The control asserts this for bills. **A difference anywhere
else refutes "one variable" and is read first.** Range: exactly zero.

**T2. Flags.** About 16 electricity flags, all `void` → `bill_the_void` (range 6-30). I cannot sign
the direction from 78f77c34e. Since then `600be30bc` makes the world's closing read actual only with
a reason, which should give fewer actual-to-actual empty spans, and `89250ba5a` opens an incoming
account on the outgoing closing read, which gives the boundary check a span to judge. The two can
push opposite ways. Gas flags: 0, all `not_screened`.

**T3. Acts.** `refer_for_investigation`: 0 (range 0-1). Any lead in a run that draws no theft is a
false lead. Each one must be named with its account and span, and if there are 2 or more this is
refuted. `bill_the_void` equals the void flag count in T2.

**T4. Unbilled kWh.** Assessed unrecorded kWh (RPCoP Appendix 7) = 0, and world-truth unrecorded
kWh on flagged accounts = 0. Range: exactly zero, because the settled run has no theft.

**T5. £ recovered.** £0.00 exactly, and the ledger gains no recovery line.

## What this run can and cannot say

It grades whether the switch is inert apart from its own record, and whether the screen keeps voids
off the lead list. It cannot grade recovery. That needs theft in the settled run, a world build that
waits for the post-publish world queue. A T3-T5 zero here says nothing about the screen's power.

Graded in the W2_36 finding after both runs exist. T1 failing voids T2-T5.
