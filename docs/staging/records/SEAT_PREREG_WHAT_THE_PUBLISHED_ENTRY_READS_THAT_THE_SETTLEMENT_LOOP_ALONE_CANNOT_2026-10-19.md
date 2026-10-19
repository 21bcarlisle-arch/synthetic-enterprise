**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** none — Lane 0 delivery
**Class:** `unanchored_world_constant` (primary)

# Pre-registration: what does the published entry read that the settlement loop alone cannot?

**Claim:** `anchor-the-446-bare-world-constants-in-impact-order`
**Written BEFORE any published-entry run below.**

## Why this exists

The reach census and the module screen
(`SEAT_PREREG_WHICH_OF_THE_446_BARE_WORLD_CONSTANTS_A_PRODUCTION_RUN_READS_2026-10-19.md`) both
ran `simulation.run_phase2b.main`. That is not what publishes. `tools/run_annual_report.py:140`
calls `simulation.run_phase4c_on_phase2b.main`, which bills, and which OVERWRITES every settlement-loop
`bad_debt_gbp` with the emergent arrears outcome (`run_phase4c_on_phase2b.py`, Phase QD). So the
first screen's bad-debt column measured a transient the published figure replaces. It showed
`simulation/bad_debt_incidence.py` passing a 10% push through to bad debt one for one, and the
arrears engine moving nothing. A constant read only at billing could not show as reached at all.
Settlement-side figures (kWh, gross margin) are unaffected: phase 4c starts from phase 2b's result.

`tools/world_constant_reach.py` now takes `--entry published` (the default) or `--entry phase2b`.

## Predictions (short window, `report_end=2017-06-30`, default book, x1.1 per module)

- **P10.** Published-entry reach is above phase 2b's 239: between 250 and 300.
- **P11.** Under the published entry, `bad_debt_incidence` moves `sum:bad_debt_gbp` by less than 1%,
  and `arrears_engine` moves it by more than 1%.
- **P12.** For every module, `sum:consumption_kwh` and `total_gross` agree between the two entries to
  the last digit.
- **P13.** At least one module that moved no figure under phase 2b moves a bill figure by more than
  0.1% under the published entry.

## What it decides

If P11 holds, the in-loop incidence table ranks low for the published figures, although it still
drives the treasury and the administration trigger inside the loop, and the arrears engine's
constants rank high. If P12 fails, phase 4c changes settled records, and the phase 2b screen's
gross ranking cannot be reused.
