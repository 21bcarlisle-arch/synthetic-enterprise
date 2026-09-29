# Result: seed 88888 run on its own gives PROS-2024-0082 16 bills in the level arm, not 5, so the leak is not in the world that seed draws

**Severity:** LATENT · **Lane:** A_strategy_governance · **Item:** `locate-the-never-renewed-leak-on-seed-88888` · **Class:** `measurements_that_mirror`

**Prereg:** `SEAT_PREREG_PROS_2024_0082_FIRST_BILL_PER_ARM_ON_SEED_88888_2026-09-29.md`, on origin at `767bd9c03`, landed before the run produced any output.

## The run

- **Code:** worktree `/var/tmp/se-leak-88888` at exactly `5f05e0068`.
- **Seed and redraw:** seed 88888, `elasticity` redraw `mode=all`, built through the tool's own `resolve_redraw_target` and patch factory.
- **Call:** `run_value_cycle_ab(report_end=None, level_arm=True)`, called directly, in a fresh process.
- **Driver and capture:** `/var/tmp/se-leak-88888-out/drive.py` and `capture.json`.
- **Timing:** three arms, 1,486 s, 1,579 s and 1,662 s.

## PROS-2024-0082 per arm, seed 88888

| Arm | Bills (issued) | First bill | Last bill | Net | Elasticity calls for this id |
|---|---|---|---|---|---|
| control | 16 (16) | 2024-03-17 (stub to 03-31) | 2025-06-07 | — | 0 |
| value | 16 (16) | 2024-03-17 | 2025-06-07 | £374.12 | 0 |
| level | **16 (16)** | **2024-03-17** | 2025-06-07 | **£374.12** | 0 |
| *artefact's level arm* | *5* | *not recorded* | — | *£1,566.54* | — |

The account's path is the same in all three arms:
- It starts a fixed term on 2024-03-17 at £224.80/MWh.
- It rolls to SVT on 2025-03-17.
- The SVT route rolls it twice, at 0.675 and 0.304. It stays both times.
- There is no `customer_events` renewal row, which is why the artefact counts 0 decisions.

## Grades

| Line | Predicted | Measured | Grade |
|---|---|---|---|
| **P0: reproduction** | value 16 bills / £374.12; level 5 bills / £1,566.54 | value **16 / £374.12** (reproduces); level **16 / £374.12** | **REFUTED on the level arm.** By the prereg, P1, P1-alt and P3 are not graded. |
| P2: 0 elasticity calls for the account, all arms | 0 | 0 in every arm. The patch fired 298 times over 69 ids, all re-drawn. | holds, and recorded because the call count is its own control |

- **The call stream matches the artefact's.** The artefact's seed-88888 row records `draw_calls` 298, `draws_redrawn` 298 and `accounts_redrawn` 69. This run recorded 298, 298 and 69.
- So the elasticity re-draw reached the same calls. A world drawn at seed 88888 does not, on its own, produce the artefact's 5 bills.

## What that means, stated narrowly

**The item asked which call-site of the re-drawn elasticity symbol sets PROS-2024-0082's first bill. The answer is none.**
- The symbol has one production caller, `simulation/customer_events.py:650` in `roll_lifecycle_event`, the renewal churn decision.
- That caller never runs for this account, in any arm.
- With the same 298 calls re-drawn at seed 88888, the level arm bills this account exactly as the value arm does.

**The artefact's 5 bills came from something that separates its run from this one.** Two things do:
1. **Order.** In the artefact, seed 88888 ran second in one process, after a full three-arm pass at seed 11111.
2. **Entry route.** The artefact came through the CLI `--noise-floor-seeds` → `noise_floor`. This run called `run_value_cycle_ab` directly.

I cannot yet say which. Both fit the 5cbbad968 observation that the level arm agrees with the value arm on seed 11111, the first pass, and not on 88888, the second.

**This bears on more than one account.**
- If it is order, the elasticity noise floor's second and later seeds are not draws of the quantity the floor names. They carry state from the pass before.
- That would apply to every multi-seed floor artefact, not only this one.
- Nothing here yet shows that it is order.
- The +£2,464 book-wide figure was not re-measured: this driver kept only the one account's rows.

## Next, one variable: running now, prediction filed here before any output

- **Command:** `python3 -m tools.run_value_cycle_ab --level-arm --noise-floor-seeds 88888,88888 --ignore-headroom --out /var/tmp/se-leak-88888-out/floor_88888x2.json`
- **Where:** the same `5f05e0068` worktree.
- **Why this command:** it is the artefact's own entry route with the same seed twice, so the two passes in one process separate the two candidates.
  - **Pass 1** equals this run except for the entry route.
  - **Pass 2** differs from pass 1 only by having a pass before it.

**Prediction, on the PROS-2024-0082 level arm `bills_issued`:**
- **(60%, order):** pass 1 = 16 and pass 2 ≠ 16.
- **(25%, entry route):** pass 1 = pass 2 ≠ 16.
- **(15%):** both 16. Then the artefact's 5 needs seed 11111 specifically in front of it, or is not reproducible at this commit. Next is the exact `11111,88888` command.

**Secondary prediction.** Under "order", pass 2's never-priced accounts move by more than £500 against pass 1, summed as value minus level.

**Output:** `/var/tmp/se-leak-88888-out/floor_88888x2.json` (about 2.7 h). Whoever draws this next grades it against the lines above.
