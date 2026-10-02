**Severity:** ADVISORY · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The world-D retake at `f18e8b5dc`: the three-arm half, graded, with the floor still running

**Claim:** `land-the-world-d-retake-at-f18e8b5dc`. Written 2026-10-02 ~06:45Z. It grades
`SEAT_PREREG_THE_WORLD_D_VALUE_ARMS_RETAKEN_AT_HEAD_0BAC2B8BE_2026-10-02.md` and its addendum
`SEAT_PREREG_ADDENDUM_THE_WORLD_D_VALUE_ARMS_RETAKEN_AT_F18E8B5DC_2026-10-02.md`, but only on the
legs the three-arm run can answer.

## The state of the unit

`longjob-arms-floor-d-head-1002b` is alive. The three-arm run exited 0 at 05:56Z and wrote
`/var/tmp/wt-arms-retake-1002b/docs/observability/value_cycle_ab_s1_three_arm_20261002b.json`.
Its `producing_commit` is `f18e8b5dc`, resolved at process start. The floor
(`--noise-floor-seeds 11111,22222,33333 --redraw-mode all`) started straight after and should finish
around 09:30Z. Both paths move together, so **neither is copied into `docs/observability/` yet**,
and `site/data/value_arms.json` still reads `0407ce0e3`.

## The three-arm figures, against 10-01

| | 10-01 (`0407ce0e3`) | 10-02 (`f18e8b5dc`) |
|---|---|---|
| whole advantage (value − control net) | +£7,708 | **+£14,856** |
| level leg (level − control net) | +£8,967 | **+£15,115** |
| selection (value − level net) | −£1,259 | **−£259** |

Control net is £85,910, value arm £100,766, level arm £101,025. The level used is £49.25/MWh, the
value arm's own median margin in this run. Two accounts churned.

## Grades so far

- **P0 (world): HELD.** `world_identity.digest` = `cf823b185f8ca51c`.
- **P1 (whole advantage positive): HELD.** +£14,856.
- **P2 (level leg positive, three-arm and all three floor seeds):** three-arm leg HELD at +£15,115.
  The floor legs are **pending**.
- **P3 (both smaller than 10-01): REFUTED** on the three-arm run. Both figures roughly *doubled*.
  As the addendum said, more than one thing changed, so this cannot be attributed to any single
  commit. I cannot yet say which commit did it. The prediction was "a binding cap clips the arm
  that prices higher". It missed, which fits `9cfb1817f` taking chosen fixed renewals out of the
  cap. That is a hypothesis, not a finding.
- **P4 (selection negative on all three floor seeds): pending.** The three-arm selection is
  negative, at −£259, but P4 is about the floor.

## The substrate: one path set moved, and it cannot be exempted

Between `f18e8b5dc` and origin/main (`5bff4f7d2`), exactly one commit touches the run's substrate.
`28eb35ec7` changes `company/interfaces/growth_desk.py`, `saas/growth_mandate.py` and
`simulation/run_phase2b.py`. It passes the supplier's fixed strike into the acquisition no-offer
gate, and the gate prices both fuels ex-VAT against the default on the day.

`run_value_cycle_ab` settles every arm through `run_phase2b`. `run_phase2b.py:2821` asks that gate
whether to replace each lost supply point, and each arm loses different points. So the change
reaches the settled book on an arm-coupled path. That is the addendum's "cannot be argued" class.
**No exemption is written.** Once the paths move, the page will withdraw this run against any HEAD
that carries `28eb35ec7`. That withdrawal is the right outcome, and the run will be named on the
page as the one withdrawn. Another retake belongs to a later claim, not beside this one. A world
run of this size must not run next to a second one (see the addendum's OOM history).
