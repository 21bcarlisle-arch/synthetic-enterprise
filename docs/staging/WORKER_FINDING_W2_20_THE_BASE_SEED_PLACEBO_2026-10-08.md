# W2_20 H2 placebo: does a floor seed equal to the base seed reproduce the default draw?

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_20_mains_gas_is_drawn_not_inferred_from_the_heating_system

The placebo matches, so the page's band is the right family. The three-seed band is too thin to hold the control arm's tail draw.
**Subject:** `tools/run_value_cycle_ab.py` noise floor vs default draw; H2 of
`SEAT_FINDING_W2_20_A_SIXTH_OF_DRAWN_GAS_BOILERS_HAVE_NO_GAS_SUPPLY_2026-10-07.md`.

## Why

H2 failed. The `20261007h` leg-1 value advantage (GBP 5,134) sits outside its own floor band
(GBP 7,970-12,965), and the gap is in the level leg (-6,102 against +1,651..+4,932). Both legs read
one SSP cache, so the SSP-source explanation is refuted.

## What the code says before anything runs

`noise_floor` runs in-process. It calls the same `run_value_cycle_ab(report_end, level_arm=True)`
with `price_elasticity_for_customer` patched. Under `--redraw-mode all`, every household gets
`real(id, seed)`. The production call site (`simulation/customer_events.py:917`) passes
`run_base_seed()`, which is `_DEFAULT_BASE_SEED = 20260724`. So at seed 20260724 the patch returns
exactly what the unpatched call returns. Any difference must come from something outside the
elasticity draw.

## Pre-registered 2026-10-08 01:57Z, before any run started

Three runs, serial, at origin `27af1a461`, all `--end-year 2017`, each in its own process:

- A: `--level-arm` (default draw)
- B: `--noise-floor-seeds 20260724,11111,22222,33333 --redraw-mode all`. The placebo is seed
  20260724; the other three are the published floor's seeds. *Corrected at 02:03Z:* B was first
  launched with the base seed alone, and `noise_floor` refused it with "a noise floor needs at
  least two seeds". The extra seeds are what the floor needs to run, and they also give a 2017 band.
- C: `--level-arm` again (default draw, second process)

| # | comparison | prediction | confidence |
|---|---|---|---|
| P1 | A vs C: `value_advantage_gbp`, `level_advantage_gbp`, `selection_gbp` | identical to the penny (the run is deterministic across processes) | ~0.75 |
| P2 | A vs B's seed-20260724 row on the same three figures | identical to the penny | ~0.7 |
| P3 (added 02:03Z, after A ended, before B started) | A's `value_advantage_gbp` against B's seeds 11111/22222/33333 | inside [min - 1 stdev, max + 1 stdev]. Over the full window H2 failed; the gap may build after 2017. | ~0.5 |

How to read the results:
- P1 and P2 both pass: the floor is the default draw's own family. Leg 1 is a tail draw, or the
  2016-2017 window is too short to show the gap. Owed next: the same placebo over the full window,
  and more floor seeds.
- P1 passes, P2 fails: the harness differs, so the published band does not bound the published figure.
- P1 fails: the run is not reproducible across processes (hash ordering, wall clock or cache state).
  Then no single-seed figure is a point, and P2 cannot be read.

## Result (graded 02:35Z)

Unit `longjob-w220-placebo` ran A from 01:57Z to 02:02Z. Unit `longjob-w220-placebo-b` ran B from
02:03Z to 02:23Z (about 295 s per seed, 78 elasticity draws, all re-drawn) and C to 02:28Z. Book:
110 accounts at 2017-12-31. Artefacts: `docs/observability/value_cycle_ab_s1_three_arm_2017_placebo_20261008.json`
(A) and `docs/observability/value_cycle_ab_s1_noise_floor_2017_placebo_20261008.json` (B). C is not
committed: its figures equal A's, and its file differs from A's by one byte.

| run | control net | value adv. | level adv. | selection |
|---|---|---|---|---|
| A default | 19,304.97 | 361.62 | 301.41 | 60.21 |
| C default, second process | 19,304.97 | 361.62 | 301.41 | 60.21 |
| B seed 20260724 (placebo) | 19,304.97 | 361.62 | 301.41 | 60.21 |
| B seed 11111 | 19,165.54 | 501.05 | 440.84 | 60.21 |
| B seed 22222 | 19,165.54 | 501.05 | 440.84 | 60.21 |
| B seed 33333 | 19,165.54 | 267.72 | 440.84 | -173.11 |

- **P1 PASS.** A and C are identical to the penny, so the run is deterministic across processes.
- **P2 PASS.** The placebo row equals A to the penny. The seeded floor is the default draw's own
  family. No harness difference separates the published figure from its band.
- **P3 PASS.** A's 361.62 lies inside [133.01, 635.76].

**What H2's failure actually is.** Re-reading the `20261007h` pair by arm, rather than by leg,
changes the attribution. These are full-window settled-realised nets, in GBP:

| | control | value | level |
|---|---|---|---|
| leg 1, default draw | 236,270 | 241,404 | 230,168 |
| floor seeds 11111 / 22222 / 33333 | 230,194 / 231,669 / 231,716 | 241,860 / 241,265 / 240,985 | 234,074 / 236,600 / 233,368 |

The default draw's value arm sits inside the re-draws. Its **control** arm is GBP 4,553-6,076 above
every re-draw. That alone puts `value_advantage_gbp` (value minus control) below the band. The level
leg's -6,102 combines that high control with a level arm GBP 3,200-6,400 below the re-draws.

**Correction to the W2_20 finding's H2 grading.** It says the gap "lives in the level leg". That is
not right. The value-advantage gap lives in the control arm. The level leg is where it shows,
because the control arm is subtracted from both legs. The 2017 placebo shows the same mechanism in
small: the default control is GBP 139.43 above all three re-draws, and that is the whole of A's
value- and level-leg difference from seeds 11111 and 22222.

**Reading.** The default draw is one draw of the per-household elasticity assignment, and the control
arm reads that draw too. In both windows it gives the control arm its best outcome. With four draws,
the chance that any given one is the extreme on one side is 1/4. A [min - 1 sd, max + 1 sd] band from
three seeds cannot carry that. So leg 1 is a tail draw of the CONTROL arm against a floor too thin to
contain it. It is not a defect in the page's bound. The 2017 floor is also discrete (two of three
seeds are identical in every figure), so 78 draws in two years have few distinct outcomes.

**Owed (one variable each):**
1. More floor seeds over the full window, at about 2 h per seed, split so that each leg ends within
   about 5 h. Until then, the published band from three seeds understates the spread of the control arm.
2. Why does the control arm take the elasticity draw at all? It is meant to be a flat arm. The draw
   sits behind `if differential:` in `roll_lifecycle_event`, so a flat offer still differs from the
   incumbent rate. Is that intended? Read the control arm's draw count in a `--partition-probe`
   before reasoning about it.

*Owed item 2 answered 2026-10-08:* yes, by design. In 2017 every arm takes the draw for all 26
renewing accounts. The floor needs nine seeds. See
`SEAT_FINDING_W2_20_THE_CONTROL_ARM_TAKES_THE_ELASTICITY_DRAW_BY_DESIGN_2026-10-08.md`.
