**Severity:** ADVISORY · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: the world-D value arms retaken at HEAD `0bac2b8be`

**Claim:** `retake-the-value-arms-on-heads-world-before-the-10-05-publish`
**Written 2026-10-01T23:50Z, before either run had produced output.** Both jobs were launched
minutes earlier from the locked clean worktree `/var/tmp/wt-arms-retake-1002` at origin/main
`0bac2b8be`, which contains `592596b44`:

- `longjob-arms-d-head-1002`: `python3 -m tools.run_value_cycle_ab --level-arm --out
  …/value_cycle_ab_s1_three_arm_20261002.json`, launched 23:41:39Z.
- `longjob-floor-d-head-1002-s123`: `python3 -m tools.run_value_cycle_ab --level-arm
  --noise-floor-seeds 11111,22222,33333 --redraw-mode all --out
  …/value_cycle_ab_s1_noise_floor_20261002.json`, launched 23:41:50Z and waiting on the arms' pid,
  as the 10-01 pair did.

These are the 10-01 commands (`.launch_records.json` rows `pb4-three-arm-d` and
`pb4-floor-d-s123`). Only the tree differs.

## What changed since the run on the page

The run on the page is `0407ce0e3` plus the PB4 patch. Since then, these commits touched the
world, the company or the runner. Each one applies to all three arms:

- `cd0c7c39c`: the portfolio premium reads only terms that had ended. This is the renewal
  foresight leak. In one default world it raised book net margin by £7,331.
- `6f5bb8b68`: the 2025 standing charge is now tabled. It was clamped to 2024.
- `5803d08c3`: the DD opening reads the rewritten registry EAC (phase 4c, which does not settle
  margin).
- `8c29e03d9`: a ToU term is graded against the multi-register cap.
- `592596b44`: the SVT segment is held at the published cap. 630 of 2,333 capped-year SVT
  segments had been billed above it.
- `ed7b4666f`: VAT is declared once. No value changed. `0bac2b8be` changes no value either.

The arms differ only in `renewal_margin_arm`. So every change above enters the contrast only
through how the change interacts with that margin.

## Predictions

The 10-01 figures were: whole advantage +£7,708, level leg +£8,967, selection −£1,259, and
floor level leg £8,548 / £9,796 / £12,098.

- **P0 (world).** `world_identity.digest` stays `cf823b185f8ca51c`. None of the commits above
  touches the departure-level anchors.
- **P1 (sign of the whole advantage).** Positive (value arm net > control net). Held firmly.
- **P2 (sign of the level leg).** Positive in the three-arm run, and positive on all three floor
  seeds. Held firmly.
- **P3 (direction of size).** Both P1 and P2 come out *smaller* than on 10-01. The reasoning: a
  binding cap clips the arm that prices higher, and both the value arm and the level arm price
  above control. Held weakly. The foresight fix raised margin in the one arm measured, and its
  mechanism is not attributed, so the opposite direction is plausible.
- **P4 (selection).** All three floor seeds again fall on one side of zero, and that side is
  negative. Held weakly. At n=3 the page states no verdict either way, and this predicts nothing
  about whether one becomes stateable.

## How it is graded

The grading goes beside this file in the result record, once
`CURRENT_WORLD_THREE_ARM_PATH` and `CURRENT_WORLD_NOISE_FLOOR_PATH` have moved together onto
these two artefacts. The DONE condition does not depend on the sign.

If either run fails, or both cannot be landed before 2026-10-05T03:00Z, the world-D reading comes
off `site/data/value_arms.json` instead. In that case this pre-registration is graded "not run".
