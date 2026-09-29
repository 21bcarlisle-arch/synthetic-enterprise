# Prereg: where PROS-2024-0082's 16 v 5 bills come from on seed 88888

**Item:** `locate-the-never-renewed-leak-on-seed-88888` · **Lane:** A_strategy_governance · **Class:** `measurements_that_mirror`

Written before launch. No output of this run existed when it was written.

## What is already read, without a run

- **From the artefact.** `/var/tmp/se-arrears-lines-head/value_cycle_ab.json`, seed 88888, PROS-2024-0082:
  - value arm: 16 bills issued, net £374.12 (pre-4c £327.84, placeholder released £46.28)
  - level arm: 5 bills issued, net £1,566.54 (pre-4c £1,120.89, placeholder released £445.65)
  - no renewal decision in either arm, and `left_at` is null in both
- **The artefact carries no bill dates.** `_decisions_by_billing_account` keeps only a count. So the first-bill date the item asks for cannot be read from it, and a re-run is needed.
- **The call-site, read from the source at `5f05e0068`.** The patched symbol is `simulation.population_draw.price_elasticity_for_customer`. It has one production caller: `simulation/customer_events.py:650`, inside `roll_lifecycle_event`, which runs only on a renewal term that has an offered-rate differential. Everything else that names the symbol is in `tools/` and never runs inside an arm.

## The run

- **Code:** a worktree at exactly `5f05e0068` (`/var/tmp/se-leak-88888`). That is the commit the artefact was drawn at. It is not origin, because `f0ba399a4` (the weather store) landed after it and would be a second variable.
- **Seed:** 88888 only. The `elasticity` redraw is `mode=all`, through the tool's own `resolve_redraw_target` / patch factory, with `--level-arm`.
- **Extra capture, and nothing else changed.** A pass-through wrapper on `run_phase4c` records each arm's rows for `PROS-2024-0082*`:
  - bills, each with its held or issued status
  - `all_records` rows
  - customer events
  - any `phase2b` list entry naming it

  A counter records elasticity calls by customer id.

## Predictions

- **P0, reproduction.** Value arm: 16 bills and £374.12. Level arm: 5 bills and £1,566.54, each to the penny. **If this fails, the run is not a reproduction and nothing below is graded.**
- **P1, acquisition timing (55%).** The level arm's first issued bill comes at least 6 months after the value arm's. The two arms' last bills fall in the same month.
- **P1-alt, held bills (35%).** The first bill has the same date in both arms, and the level arm's pre-bill gate holds at least 10 bills. The remaining 10% is neither.
- **P2 (85%).** The patched elasticity symbol is called 0 times with an id starting `PROS-2024-0082`, in every arm. If so, the re-draw reaches this account indirectly, through other households' renewal departures. The run must then name the path, which is the account's acquisition or billing record.
- **P3 (60%).** The control arm issues the same number of bills to this account as the value arm, 16.

**Refutation.** If P2 fails, the call-site is direct. In that case the account had a renewal decision that the renewal log does not record, and that is a separate defect in the log.
