**Severity:** LATENT · **Lane:** A_strategy_governance · **Item:** `grade-the-pros-2024-0082-first-bill-capture-on-seed-88888` · **Class:** `measurements_that_mirror`

# Result: PROS-2024-0082's 16 v 5 bills do not reproduce. The artefact's last arm ran on a weather store that was swapped on disk mid-run

**Prereg:** `SEAT_PREREG_PROS_2024_0082_FIRST_BILL_PER_ARM_ON_SEED_88888_2026-09-29.md`, on origin at `767bd9c03`. It was written before launch.

**Run:** `/var/tmp/se-leak-88888-out/drive.py`, in a worktree pinned at `5f05e0068`. Seed 88888 only, elasticity redraw `mode=all`, `--level-arm`. The patch was called 298 times over 69 accounts, which matches the artefact's seed-88888 row. The capture is `/var/tmp/se-leak-88888-out/capture.json`.

## Grades

| Line | Predicted | Measured | Grade |
|---|---|---|---|
| **P0: reproduction** | value 16 bills, £374.12; level 5 bills, £1,566.54 | value **16, £374.116868**; level **16, £374.119488** | **FAILS. This run is not a reproduction, so nothing below is graded.** |
| P1: acquisition timing, level arm ≥ 6 months later (55%) | — | not graded | not graded (P0) |
| P1-alt: same first bill, ≥ 10 held (35%) | — | not graded | not graded (P0) |
| P2: 0 elasticity calls for `PROS-2024-0082*` (85%) | — | not graded | not graded (P0) |
| P3: control arm = value arm = 16 bills (60%) | — | not graded | not graded (P0) |
| Refutation (P2 fails, so the call-site is direct) | — | not graded | not graded (P0) |

**What was observed, recorded ungraded.** These are observations only. They are not P1–P3 outcomes, because the run did not reproduce the premise.
- All three arms give this account the same schedule: 16 issued bills, 2024-03-17 to 2025-06-07. No bill is held.
- The patched symbol is called for `PROS-2024-0082*` **0 times** in every arm.
- The account's only decisions are two `svt_segment` stays, on 2025-03-17 and 2025-04-01, with the same rolls in every arm.

## Why P0 failed, and the mechanism behind the 16 v 5

**The one-seed level arm matches the artefact's seed-11111 level arm, not its seed-88888 one.**
- In the artefact, seed 11111's level arm gives the account 16 bills and **£374.119488**.
- This run's seed-88888 level arm gives the identical figure, to the micro-pound.
- Only the artefact's **seed-88888 level arm** has 5 bills. That was the sixth and last arm of the two-seed process.

**That arm ran on a different weather store.**
- The two-seed artefact ran in the executor worktree `/var/tmp/se-seat-executor`. Log: `/var/tmp/longjob-arrears-lines-head-two-seed-20260929.log`. It ran from 00:34 to 03:01 BST, and seed 11111 finished at 01:44.
- The worktree's own reflog shows it moved mid-run:
  - reset to `3b22ed3e9` at 02:16
  - `surgical_land` of `f0ba399a4` at 02:25
- `f0ba399a4` replaces `sim/weather_world/{cells,daily.csv.gz,regimes}`. It also says that 42 premises "now read" a complete cell.
- Counting the log's `legacy provider` lines per arm:
  - arms 1–5: **53** each
  - arm 6, the seed-88888 level arm, starting about 02:36: **11**
- The difference is 42 premises. PROS-2024-0082 is one of them.
- In arm 6 the account settles on the fabric path:
  - term-0 `actual_net` goes from £270.43 to £1,013.41
  - `naked_net` goes from £612.09 to £5,757.61
  - gross goes from £886.35 to £7,943.31 on the same 2,602 kWh EAC
- The run still assembled 16 bills (`PROS-2024-0082 16 0.744` in the arm's table), and only 5 were issued.
- I infer that the pre-bill gate held the other 11 against a roughly 9× consumption scale. I did not measure it: the artefact keeps only the issued count.

**It is none of the three categories the item offered.**
- It is not an acquisition draw.
- It is not an unlogged renewal decision.
- It reaches the pre-bill hold gate only downstream.
- The cause is a **data file changing on disk between arms**. The elasticity redraw does not reach this account (0 calls).

**The call chain, read from the source at `5f05e0068`:**
1. `tools/run_value_cycle_ab.py:5251` `run_value_cycle_ab` → `run_phase4c` (once per arm)
2. → `simulation/run_phase2b.py:1194` `main`
3. → `:1386` `_weather_source = WeatherWorldSource.load()`
4. → `simulation/fabric_demand_path.py` `WeatherWorldSource.load`
5. → `sim/weather_world.py:223` `WeatherWorld.load`
6. → `load_cells` / `load_daily` / `load_regimes` on `STORE_DIR = PROJECT / "sim" / "weather_world"` (`:86`)

`PROJECT` is the working tree the process was started in. The store is read **once per arm, not once per process**. So any checkout that moves under a multi-hour run changes the world between arms. Nothing reports it: `producing_commit` is resolved at process start and says so, `book_identity` does not include the weather store, and the cross-arm same-book control passes.

## What this does to the +£880 result (`5cbbad968`)

The seed-88888 P4c refutation in that result came from this mechanism, not from the noise floor.
- Its +£2,464.22 on 94 never-priced accounts splits as follows:
  - **+£2,484.27** on the 42 swapped premises
  - **−£20.05** on the other 52
- The artefact's whole seed-88888 level arm, and with it seed 88888's selection figure of +£3,618.80, was measured in a different world from its control and value arms. **Seed 88888 in that artefact is not a noise-floor draw, and its row should not be read as one.**
- Seed 11111 ran entirely before 02:16 and is unaffected.

**One more observation, ungraded and not chased here.** In the artefact, the value arm's per-account net is **identical to the penny on all 164 accounts** across seeds 11111 and 88888, while the control arm's total moves (£173,432.66 v £171,802.05). Before any "noise floor" reading is written, check whether the elasticity redraw reaches the value arm at all.

The mid-run swap is filed as `docs/staging/SEAT_FINDING_A_MULTI_ARM_RUN_REREADS_THE_WEATHER_STORE_FROM_A_TREE_THAT_MOVES_UNDER_IT_2026-09-29.md`.
