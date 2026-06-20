# Next: Phase 7e Full Run

Phase 7e implementation is complete (2026-06-16). All tests pass (379).

## What was built

- `SUCCESSOR_CUSTOMERS` (C1_2..C6_2) in `saas/customers.py`
- `home_move_won` field on every lifecycle event (second deterministic roll, seed `win_{account}_{date}`)
- Gating logic in `run_phase2b.py` main loop — successor terms skip until activation date
- Win activation: when `home_move_won==True` on a churn event, `won_successor_activations[successor_id] = term_start_str`
- `_ALL_KNOWN_CUSTOMERS` passed to churn model (avoids KeyError for successor records)
- `won_successor_activations` passed through the full pipeline to `annual_report.py`
- Successor acquisitions appear in the correct year's report section
- `per_customer_lifetime` covers successors

## Next step: Phase 7e full run

Run `make run` (or `python3 -m simulation.run_phase4c_on_phase2b --save-json`) to produce:
- The first run where successor customers actually settle energy terms
- `won_successor_activations` showing which accounts won home-movers and when
- Successor accounts appearing in CLV trajectory, pricing flags, churn risk tables
- Updated `docs/reports/ANNUAL_REPORT.md` and `run_output_latest.json`

Then:
1. Commit run outputs
2. Update `LATEST.md` with which successors were won and their financials
3. Push to GitHub (Pages will serve updated report)
4. Send NTFY digest

## After the run: report improvements to consider

- `_customer_book_section`: distinguish won home-movers from 2016 originals in the acquisitions line
  (e.g. "New acquisitions: C1_2 [home-move win]")
- CLV trajectory: show successor accounts in their own rows
- If all successors have 0 activations (all churn events had `home_move_won=False`), the win
  probabilities in `home_move_win_rate.py` may be too low — check and calibrate
