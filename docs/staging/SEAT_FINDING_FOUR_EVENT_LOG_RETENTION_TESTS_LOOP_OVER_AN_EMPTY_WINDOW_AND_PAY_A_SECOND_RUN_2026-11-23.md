**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Four event-log retention tests loop over an empty window, and their file pays a second whole run for it (2026-11-23)

*Delivery seat, claim `the-largest-gate-selection-is-measured-per-file`. This is the part of that
claim that was not landed in 1c9cd8195.*

## What was measured

Run in isolation with `--durations`, reg 6C's gate selection spends 534 s in the setup of
`tests/simulation/test_run_phase2b_event_log.py`. That is its own module fixture,
`run_phase2b(report_end="2017-12-31")`. Every commit that touches `simulation/run_phase2b.py` selects
the file by `tests_for`, together with `tests/simulation/test_run_phase2b.py`, whose module fixture
already runs 2016-2018 (1,017 s). So the gate builds two overlapping simulations.
Evidence: `docs/staging/SEAT_FINDING_THE_COMMIT_GATE_LOSES_ITS_HOUR_2026-11-22.md`, section
"Per-file measurement".

## The defect

`test_run_phase2b.py`'s fixture records why it left the 2017 window (2026-08-31): "the world's
earliest retention offer now lands on 2018-02-09, so the 2016-2017 window contains NONE". The
event-log file stayed on that window. These four of its tests are a bare `for` over the list and
assert nothing when it is empty:

- `test_retention_log_entries_have_required_fields`
- `test_retention_cost_events_are_negative_amounts`
- `test_retention_log_entries_above_threshold`
- `test_retention_log_entries_have_expected_margin`

Not re-measured here: it needs a 9-minute run. The premise is the sibling fixture's own
measurement, and that should be the first reading taken.

## Done means

- The event-log tests read the 2016-2018 run that `test_run_phase2b.py` already builds: one fixture,
  shared through `tests/simulation/conftest.py`, and no second simulation. The comment in that file
  ("two runs ... proven by the sibling file") moves with it.
- Each of the four asserts its list is non-empty before it loops, so a window with no offers goes
  red instead of passing.
- `test_every_churned_account_appears_in_a_departure_record` still holds on the longer window.
- `--durations` before and after are printed. Expected: about 534 s less for every run_phase2b gate.

`test_run_phase2b.py` carries reg 6C's uncommitted work in the shared tree. Land through
`tools/isolate_hunks.py` + `surgical_land --content`, never a pathspec of the working copy.
`tools/profile_test_suite.py`, `tools/head_green_census.py` and
`background/process_run_complete.py` name the event-log file. Keep the file, or update all three.
