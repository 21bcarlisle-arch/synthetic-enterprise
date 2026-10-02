**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none · **Claim:** `opt-other-run-phase2b-test-modules-into-shared-fabric-traces` (Lane 0 delivery)

# Of the eight other modules that run `run_phase2b.main`, one runs it twice over one window

## Premise, re-measured at draw time

`09555ee17` is origin/main's tip and this worktree's HEAD, so the pattern it lands
(`test_home_move_undeliverable_win.py::shared_fabric_traces`) is the base, not a rival copy. The
duplicate-work note named this very id; that entry was this draw's own write and `ps` showed no
other `surgical_land` on it.

## Census (static, every `tests/**/test_*.py` importing `simulation.run_phase2b`)

| module | runs per module | window | touches physics |
|---|---|---|---|
| `simulation/test_net_new_acquisition.py` | **2** (`test_c_…REACHES_THE_RUN…`, `test_MUTATION_c_…PRE_BUILD…`) | 2016-01-01..2016-06-30 | no |
| `simulation/test_run_phase2b.py` | 1 (module fixture) | ..2018-12-31 | no |
| `simulation/test_run_phase2b_event_log.py` | 1 (module fixture) | ..2017-12-31 | no |
| `simulation/test_value_chain_credit_feed_wiring.py` | 1 (module fixture) | ..2016-12-31 | no |
| `simulation/test_phase40a_pass_through.py` | 1 | fast-mode default | no |
| `simulation/test_phase40c_deemed_rate.py` | 1 | fast-mode default | no |
| `simulation/test_phase41a_flex.py` | 1 | fast-mode default | no |
| `company/test_competitive_pressure.py` | 0 (names `run_phase4c_on_phase2b.main` in a docstring only) | — | — |

A module-scoped scope only pays inside a module, so only the first row can gain. The three
fast-mode modules each run the same default window once; sharing ACROSS modules would need a
session scope, which the 2026-08-24 cache leak (traces built under one test's monkeypatched
physics served to another) rules out while four modules patch the physics.

In the mutation leg the patched name is `campaign_acquisition_spend_events`, which feeds the
acquisition spend, not households or weather; the trace key carries customer id, household and
weather, so any premise the mutation changes builds its own trace.

## Pre-registration (written before timing)

Per-run wall time for the module's two runs, measured as `--durations` without and with the scope.
Prediction: without the scope each run is 10-40 s; with it the second run falls by roughly the
trace share of a six-month window, 5-20 s. If the second run falls by under 2 s the trace build is
not the cost at this window and the change is not worth landing.

## Result

`--durations`, the two run tests alone, same worktree, one variable (the fixture):

| | REACHES_THE_RUN | PRE_BUILD mutation |
|---|---|---|
| without the scope | 31.8 s | 31.9 s |
| with it | 33.2 s | **13.6 s** |

The second run falls 18.3 s, inside the predicted 5-20 s; the first is unchanged within noise.
Whole module: 61 passed. The fixture is module-scoped and requested only by those two tests, so
nothing else in the module enters the scope.

**Done means:** every module that runs `run_phase2b.main` 2+ times over one window without patching
the physics is inside a scope. After this landing there are none left outside one; the remaining
cross-module repetition (three fast-mode default-window modules) needs a session scope and stays
out by design until the physics-patching modules can be fenced off from it.
