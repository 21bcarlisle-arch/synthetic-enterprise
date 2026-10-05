# C29: the value arms are re-taken on the refitted world, and the direction is filed first

**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `retake-the-value-arms-on-the-c29-refitted-world` (Lane 0 delivery)

## Premise, re-measured at draw (07:20Z)

The arms are still unspent, even though `ae552db75` is on origin. The published pair is `20261004h`,
moved by `d7169c720`, and its code does NOT descend from `ae552db75`
(`git merge-base --is-ancestor ae552db75 d7169c720` returns false). `ae552db75` touched
`simulation/household_segments`, which is inside `ARMS_SUBSTRATE_PATHS`. So
`_code_since_the_run` refuses the standing arms, and their current-world claim is withdrawn. The
duplicate claim the draw named is this item's own write: `claimed_at` is 07:20:17Z, the same second
as this draw. `ps` showed no rival arms run or seat.

## Pre-registration (written 07:22Z, before either leg started)

The refit raises the default tail's switching to Ofgem's control-arm rates (0.50/0.24/0.20), so the
tail shops about twice as often. The predictions below are about the CURRENT-WORLD three-arm
contrast. Its baseline is the published 20261004h figures: £20,889 for value against level, a
£1,756 floor spread across 3 seeds, and a £5,915 selection leg.

1. **Headline contrast (value minus level): DOWN**, to below £20,889. Mechanism: each retained
   account is held for fewer months, so a pricing difference that keeps an account is worth less per
   account. Confidence: about 0.6. The opposing mechanism is that more accounts are at stake at each
   renewal, so per-customer choosing has more decisions to act on. If that dominates, the contrast
   rises.
2. **Floor spread: UP**, to above £1,756. More switching means more stochastic departures per seed.
   Confidence: about 0.65.
3. **Selection leg: I cannot predict a sign.** It was not distinguishable from zero on the 20261004r
   floor (mean £8,920, sd £4,052). I make no directional claim.

This run is ONE variable against 20261004h only if nothing else in the substrate moved between
`efe1b7dee` and `a9e6f2144`. That is not established. The landing must list
`git diff --name-only efe1b7dee a9e6f2144 -- <ARMS_SUBSTRATE_PATHS>`. If anything besides
`simulation/household_segments*` appears there, a move cannot be attributed to the refit alone, and
the finding must say so.

**Answered at 07:23Z, after launch and before any result: NOT one variable.**
`git diff --stat efe1b7dee a9e6f2144 -- <ARMS_SUBSTRATE_PATHS>` lists 32 files (+2,447/−411). Besides
`simulation/household_segments.py`, the list includes:

- `simulation/run_phase2b.py`, `simulation/satisfaction_churn.py`, `simulation/final_bill_outcome.py`
  and `simulation/policy_costs.py`;
- `company/policy/decision_policy.py` and `saas/ledger.py`;
- the EP13/G14 grid-carbon modules under `sim/`.

So predictions 1 and 2 are graded as written, but a move cannot be credited to C29. A miss is also
not evidence against the mechanism. The newer arms are the current world's arms, and that is what
this retake is for. Attributing the move to C29 is the C29 book-arm off/on pair's job, not this
run's.

## The run

- Worktree `/var/tmp/se-c29-arms` at origin `a9e6f2144`. It contains `ae552db75`. It is locked and
  its owner file is written.
- `longjob-c29-arms-retake` runs `/var/tmp/se-c29-arms-handoff.sh`. This is the same producer and
  the same leg split as the 20261004h retake:
  1. `--level-arm`, writing `value_cycle_ab_s1_three_arm_20261005c.json` (about 70 min).
  2. Only if leg 1 produced a result: `--noise-floor-seeds 11111,22222,33333 --redraw-mode all`,
     writing `value_cycle_ab_s1_noise_floor_20261005c.json`. The three seeds run in ONE process,
     because the floor refuses a single seed. This takes about 3h20, so each leg ends in under 5h.

## Landing (continuation)

Once both artefacts exist:

- Copy them into an origin worktree.
- Move `CURRENT_WORLD_THREE_ARM_PATH` and `CURRENT_WORLD_NOISE_FLOOR_PATH` onto the `20261005c`
  pair, and regenerate `site/data/value_arms.json`.
- Re-key any control that pinned a 20261004h figure.
- Grade the three predictions above beside this section.
