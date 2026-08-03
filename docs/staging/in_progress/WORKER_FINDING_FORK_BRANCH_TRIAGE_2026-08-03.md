<!-- SUPERVISOR_DRAW: self-drawable -->
# [WORKER FINDING] — fork-branch triage: the rival pair is settled, and the population was 2x what the audit knew

**Provenance:** director console, 2026-08-03: *"work the 7 branches as ordinary serial jobs cheapest
first, picking a winner where two are rival versions of the same thing."* Doing that surfaced that
the population was never 7.

## The population is 13 branches, not 7

`WORKER_FINDING_DEAD_FORK_RESCUE_AUDIT_2026-08-03.md` triaged seven branches. It could only see
seven: the rest of the fork population was still **uncommitted inside dying worktrees** at the time,
so it had no git existence to audit. `fork_salvage.py`'s 13:26 sweep committed 38 worktrees, and
that made the real backlog visible for the first time.

Cheap discriminator, run over every branch — *does this branch contain a source file that exists
NOWHERE on main?* (`git cat-file -e main:<path>`). It separates genuinely-unlanded work from the
much larger set of branches whose diff only looks big because their merge-base is old:

| branch | source that exists nowhere on main |
|---|---|
| `a3faa0acb` | **`regulation_commons/` — a whole package**: `working_days` 246, `working_day_guard` 246, `refresh_bank_holidays` 158, + 776 lines of tests |
| `a0ce47338` | `tools/moap_evidence.py` 628 + tests 413 + `site/evidence` page test 282 |
| `a8181339` | `generate_evidence_pages` 434, `moap_evidence` 463, `moap_evidence_gate` 340, tests 503 |
| `a86610798` | **rival** moap set: `site/moap_evidence` 327, `generate_moap_evidence_data` 376, 3 test files |
| `a28e560da` | `tools/build_population_value_frontier.py` 615 |
| `a860ccd66` | 3 detectors: `origin_freeze` 129, `console_rescue` 143, `advisor_restart_ruling` 107, + test |
| `a6ad9f2b3` | site proof expert-hour fixes 327, predictions-ledger test 191 |
| `ae5594bc4` | `test_site_eh1_segment_disclosure.py` 449 |
| `a84b7d9b7` | `test_merit_order_price_wiring.py` 341 |
| `ae60f5d5b` | `test_generate_proof_conversation_gap.py` 149 |
| `a878c7c09` | `tools/test_generate_world_data.py` 169 |

`tools/moap_evidence.py` exists in **three** mutually-different versions across three branches — the
same rival-implementations pattern the audit found for SITE_EH1, at 3x. None is on main.

All 13 are HELD in `.fork_reap_held`, so the now-armed reconciler cannot reap them.

## The rival pair is settled — and main won

`OPS_run_marker_sweep_livelock`, RIVAL A (`a5555b1e`) vs RIVAL B (`ad14ac1d`). The audit said
"blind-merging either would silently pick a winner". It turns out **neither wins, because main
rebuilt the atom after both forks were orphaned** — `32616f77d` (L0→L1, terminal state for a
leftover marker) and `291768c32` (zero-progress alarm). This is the pathology stated exactly: an
orphaned fork converts finished work back into queued work, and the map re-drew an atom that had
already been built twice.

What each rival actually held, and where it ended up:

- **RIVAL B — ABSORBED.** Its two ideas are live on main: supersede older markers (their names are
  fixed-width `run_complete_YYYYMMDDTHHMMSSZ.md`, so a lexicographic sort IS chronological, and an
  unrecognised name is fail-CLOSED — never superseded) and a zero-progress alarm that declares the
  retry loop STUCK after 3 dead cycles. Nothing to land.
- **RIVAL A — SUPERSEDED as a necessity; one idea kept.** A attacked the *causal* mechanism: the
  sweep acquires `process_run_complete`'s run lock **once for the whole batch** and passes
  `LOCK_ALREADY_HELD_ENV` to each child so it skips a re-acquisition it could only ever lose while
  the lock holder was mid-pipeline. Main does not have this. But main no longer *needs* it: giving
  a marker a terminal state means the backlog drains without every marker having to win the lock.

**Verified rather than reasoned:** pending run markers **404 → 1**, with **4,298** archived to
`done/`; the single pending marker is 20 minutes old (a run that just finished), not stuck; the
sweep state file is a fresh `{}`; and the last zero-progress alarm fired at **10:45 UTC, before**
the supersession fix landed. The livelock is gone.

**The one idea worth keeping from RIVAL A** (recorded, not built — SELF_INTERRUPT_DISCIPLINE:
queue, don't fix on sight). Batch-scoped lock acquisition is still strictly better than per-marker
contention under a burst, and main's own alarm is the thing that would report it if it ever
mattered again. It is deliberately NOT force-fitted now: `background_worker.py` has moved twice
since A branched, so porting 266 lines would be a rewrite against a changed file to fix a problem
that is currently not occurring — the definition of speculative work.

Both rival branches are therefore released from the held list and are reapable; their content stays
reachable at `salvage/worktree-agent-a5555b1e8256de0e4` and `…-ad14ac1d4858a473f`, both on origin.

## Disposition

- **Settled:** RIVAL A / RIVAL B (above). `ac55b4bf` ABSORBED, `abdcad5f` LANDED, `a6ad9f2b`
  implementation SUPERSEDED — all three confirmed by the audit and now reaped, recoverable by tag.
  `ab2bd7ad` adopted at `5987001f5` and kept (director: "keep the adoption — no revert").
- **Open, ranked cheapest-first for the next ticks.** Each is a self-contained landing job: decide
  the winner among the three `moap_evidence` rivals FIRST (one atom, three implementations — the
  same reconciliation shape as above, and landing any one blind would silently pick), then
  `regulation_commons/` (largest, and a genuine capability main lacks), then the single-test
  branches (`a84b7d9b7`, `ae60f5d5b`, `a878c7c09`) which are the cheapest of all.
- **Nothing is reaped while listed** in `.fork_reap_held`; remove a line only when that branch's
  work has landed or been positively judged superseded, with the evidence recorded here.

## The class

The audit's closing line said the `reaper` was unbuilt and the audit was "the manual stand-in [that]
must be repeated before any prune". It has now been built and armed — and arming it immediately
exposed two defects in its own destructive half (a FAIL-SILENT reap that reported 26/26 while
deleting 0, and a FAIL-OPEN held-list parser), plus a deadlock that made orphan+worktree pairs
immortal. All three are fixed at `ee8bf7e75` with R15 pairs. The lesson is not "the reaper was
wrong" but that **a control's first armed run is the only thing that tells you whether it works** —
report-first proved the *detection* half for weeks and told us nothing about the *acting* half.
