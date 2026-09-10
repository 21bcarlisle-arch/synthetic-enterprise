**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `land-the-ledger-guard-ratchet-repair-from-isolated-bytes-and-discharge-its-finding`) · **Class:** controls_that_cannot_fail

# PRE-REGISTRATION — what the unguarded-writer census reads under the item's stated path list, and under the real one

Written **before** any census is run in this worktree. Nothing below has been measured yet.

## Why there is anything to pre-register

The drawn Lane 0 item names three paths and says the repair "is finished in the working tree":

> `background/live_ledger_guard.py`, `background/process_run_complete.py` and
> `tests/background/test_live_ledger_guard.py`

and it says the docstring already records the clean-HEAD figures — **86 → 56, delta 30 across 17
modules**. Those two statements cannot both be about the same three files. `process_run_complete.py`
is one module. A delta of 30 across **17** modules has to be carried by sixteen other files, and the
shared tree confirms sixteen `background/*.py` modules that call `guard_live_ledger_write` in the
working tree and do not call it at HEAD:

```
autonomous_runner  background_worker  boot_announce   daily_self_note
deploy_restart     long_job           notify          ntfy_utils
publish_freshness  reconcile_watch    retro_cadence_check  sanity_daemon
supervisor         trust_ledger       worker_seat     worker_tick
```

Sixteen, plus `process_run_complete.py` itself, is the seventeen the docstring names.

So the item's path list is a **subset of the change it describes**, and a landing obeying it
literally would move the bound from 74 to 56 while landing only one module's worth of the guarding
that earns it. That is the specific thing this pre-registration exists to make falsifiable before it
is done rather than after.

## The predictions

Measured by the census inside
`tests/background/test_live_ledger_guard.py::test_the_narrowing_to_measurement_ledgers_is_measured_not_assumed`,
run in a **clean HEAD extract** carrying the named hunks and nothing else — never in the shared tree,
which holds four other lanes' uncommitted modules and reads one higher for that reason.

| # | Question | Prediction |
|---|---|---|
| P1 | Census over `background/` at HEAD, unmodified | **86** |
| P2 | Census with the item's stated THREE paths only | **78** — 86 less the eight writers `process_run_complete.py` newly routes through the guard. Band: 78–80 if some of those eight resolve outside `docs/observability/`; it will NOT be ≤ 56. |
| P3 | The test under P2 | **RED.** `assert 78 <= 56`. Landing the stated three paths alone leaves the ratchet red at HEAD in a *new* way — bound lowered, writers unguarded — which is strictly worse than the red it was sent to clear. |
| P4 | Census with the full 22-path set below | **56**, and the test GREEN. |
| P5 | The newly-guarded set under P4 is a strict subset of the HEAD population | **Yes** — no writer appears that HEAD did not already have. |

P3 is the load-bearing one. If P3 comes back GREEN, my reading of the path list is wrong and the
sixteen modules are not needed — in which case this document is the record that I predicted
otherwise.

## The path set this turn will actually land

Nineteen under `background/` — the sixteen above, plus `live_ledger_guard.py` (the guard's new twin
`guard_site_publish_pipeline`, moved home), `process_run_complete.py` (eight guard calls, and the
twin moved out), and `head_red_register.py` (a docstring only: the note recording that
`save_observed` is deliberately unguarded because `conftest.py`'s `production_surface_guard` already
covers it, so the next reader does not re-add a second implementation of a live rule).

Three under `tests/` — `test_live_ledger_guard.py` (the bound, 74 → 56),
`test_the_site_publish_pipeline_is_contained.py` and `tests/tools/test_website_integrity_fix.py`,
both of which import from `process_run_complete` at HEAD and must follow the twin to
`live_ledger_guard`. **Those two are not optional**: landing the move without them leaves two
`ImportError`s at HEAD.

## What is deliberately NOT in it

`tests/simulation/test_phase40a_pass_through.py` and `tools/ops_repo_contract_battery.py` both
mention `live_ledger_guard` in working-tree hunks and both belong to other lanes — the first is a
`gap_ledger_path` route through a sim test, the second a mutation battery for `ops_repo`. Neither
changes this census. They are named here so that leaving them behind is a decision on the record and
not an omission.

## Method

Every file is reconstructed as HEAD-plus-this-lane's-hunks. `supervisor.py` (four foreign hunks, a
pass-ceiling fix) and `head_red_register.py` (five foreign hunks) go through
`tools/isolate_hunks.py`; the rest have no foreign hunks and their working-tree bytes already equal
HEAD-plus-mine. The landing is `surgical_land --content` so no in-place edit by another lane rides
along. The census is then run in a clean extract **of the commit that was made**, not of this
worktree.
