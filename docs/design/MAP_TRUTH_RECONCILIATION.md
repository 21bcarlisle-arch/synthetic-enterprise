# Map self-report vs external truth — root-cause + fix (2026-07-15)

**Director's question:** "HOW did the sole-map-writer fall out of sync with its own
committed ARCH1 work this morning? If the map can silently diverge from origin, that's
the self-report-vs-external-truth class and the loop can't run unwatched until it's
understood."

## Answer up front
The map did **not** silently diverge. `ARCH1_internal_seams` `level_current: 0` is the
**correct, honest value** — no level was earned. BUT the investigation exposed a real
structural gap the director is right to gate on: **the map level is a judgment-written
self-report with no external-truth reconciliation and no atomic coupling to the commit.**
It didn't bite on ARCH1, but nothing would have caught it if it had. Fix below; a
fail-closed guard is now built so the class can no longer pass silently.

## Evidence (labelled observed / inferred, R9)

**1. `level_current: 0` is correct, not a lost write. [observed]**
- ARCH1's level DoDs (its own FRAME, in the atom's `simplifications`): **L1** = wall-safe
  single life at **sub-GB RSS**; **L2 (target)** = **composes with A8, workers>1 measured
  + gap measured**. Every level's acceptance test requires a *measured* RSS collapse.
- `RecordedSimInterface` / `build_sim_interface()` has **zero callers in any run path**
  (`grep` over `saas/`, `tools/tournament_runner.py`: none). The mechanism is built and
  unit-tested in isolation but **unwired**.
- The one RSS test (`tests/interfaces/test_recorded_sim_interface.py::
  test_memory_cap_admits_more_workers_with_mock_rss`) feeds **parameterized** `mock_life`
  / `full_life` byte values into `memory_safe_worker_cap` — it does **not** measure a real
  life's RSS. So no level's DoD is demonstrated.
- The build commit (`08e20d914`) body says so itself, verbatim: *"the stricter
  measured-RSS L2 DoD is NOT met … a real wiring gap OUTSIDE this atom's scope, filed for
  the next slice."* The author **deliberately** kept it at 0.

**2. The *appearance* of divergence had two sources, neither a data bug. [observed]**
- The commit **subject** — `"…RecordedSimInterface … (L0->L2 mechanism)"` — overclaims: it
  reads as a level move to 2, while the **body** correctly says the level did **not** move.
  Subject/body disagree; the map agrees with the body.
- My own earlier status report called it *"reconciliation pending,"* implying a level-2
  write was owed and lost. **That was wrong** — nothing was owed; 0 is correct. I seeded
  the "fell out of sync" framing and I'm correcting it here.

**3. The map-write path has no external-truth reconciliation — the real finding. [observed]**
- `maturity_map.yaml` is **hand-authored** (canonical, rich prose). The safe-by-
  construction path (`tools/merge_atom_status.py`: a fork writes a narrow inbox at
  `docs/design/atom_status/<id>.yaml`, an integrator folds it) **exists but is dormant** —
  it is wired into **no** daemon/flow/hook, ARCH1 **never wrote an inbox**, and
  `atom_status/` holds only its README.
- The executor's live contract (`background/build_executor.py:539`) tells a fork to
  *"report the level reached and let the orchestrator write it"* — a **free-text** report
  in the turn output, folded by a **separate judgment step** (hand-edit), never atomic with
  the code commit.
- The executor's write-landed gate checks **only the commit SHA on origin** — it never
  reads, writes, or reconciles the map level.

**Conclusion [inferred, well-supported]:** a fork can land verified work while the map
level is wrong — lost to a crash between commit and map-write, mis-judged, or simply
forgotten — and **nothing alarms**. The map drives the DRAW (what's below-target), so a
wrong level makes the loop re-draw finished work or skip earned work. That is the
self-report-vs-external-truth class, live. ARCH1 happened to be a correct 0, so it didn't
bite — but the class was uncaught.

## The fix (make the map reconcilable, fail-closed)

**F1 — Atomic level-write (kills the lost-write-on-crash window).** The executor's turn
contract writes a **structured** `docs/design/atom_status/<id>.yaml` inbox (level_current +
evidence) **in the same commit as the code**, replacing the free-text report-back. The loop
folds it via `merge_atom_status` as part of landing. There is then no window in which the
committed code and the reported level disagree.

**F2 — Fail-closed reconciliation guard (catches the class, R15).** A control the loop runs
each cycle (and the executor gate consults): **an unfolded inbox left at rest is a level
report that never reached the map** — a silent divergence signal. The guard FAILS on any
`atom_status/<id>.yaml` present at rest, and (extensible) on any map level not supported by
its evidence. An **unreconciled map is a failed check → the loop STOPS** (an unverifiable
self-report is a failed one). Built now as `tests/controls/test_map_reconciliation.py`,
mutation-proven (a planted inbox makes it fire; folding+clearing makes it pass).

**Loop-trust bar:** the unwatched loop may run for hours only once F1 + F2 hold, so a
mis-reported level is either impossible (atomic) or an immediate stop (guarded), never a
silent drift the director discovers hours later.

## Status (2026-07-15)
- **F2 guard — BUILT + mutation-tested + wired this turn.** `tools/merge_atom_status.
  unfolded_inbox_ids()` (one reused primitive) + `tests/controls/test_map_reconciliation.py`
  (5 tests: guard fires on a planted inbox, passes once folded+cleared, no false positive on
  the README, fail-closed on a missing dir). Wired into `background/executor_governor.
  run_loop` as a **per-cycle fail-closed STOP** (`map_unreconciled` → alert + halt), with a
  test proving it stops before dispatch and one proving the default resolves to a divergence
  sentinel if the check itself errors. So the divergence class is now a loop HALT, never a
  silent drift. Full suite around the change: 1231 passed.
- **F1 atomic-inbox contract — DESIGNED, not yet wired (awaiting the director's check).**
  It changes the executor's turn *governance contract* (`build_executor.py:539`: replace the
  free-text "report the level" with a structured in-commit inbox write + a loop-side
  `merge_atom_status` fold). That is close to the governance surface under review, and its two
  halves (fork-writes-inbox / loop-folds-inbox) must land together or F2 would (correctly)
  halt the loop — so it is staged for the director to confirm the approach before it touches
  the executor contract. **Loop-trust bar: F1 must land before the loop runs UNWATCHED.**
  While WATCHED (a human present, F2 live), the orchestrator writing the level directly is
  fine — F2 catches any miss.
