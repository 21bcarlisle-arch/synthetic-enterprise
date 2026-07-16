# SCHEDULED HOUSEKEEPING — sweep the cruft on a cadence, before it causes incidents (P1, director-decided)

**Staged:** 2026-07-16 by advisor, **director-decided**. Disposition: QUEUE-high.
A standing function of the MAINTENANCE LANE (PARALLEL_MAINTENANCE_LANE, 600f0687).
Director: "have we got stale trees and other no-longer-needed things? should we
schedule regular housekeeping?" Yes to both — and there is currently NO scheduled
sweep; cleanup happens REACTIVELY (when something breaks), which is the worst model.

## The evidence it's needed (cruft already accumulating)
- **~64 stale worktrees** (agent flagged, deliberately not bulk-removed mid-session)
  — disused git worktrees eating disk and confusing tooling (a plausible source of
  the grep-guard false-positive earlier).
- **~30-32 commit local/origin divergence** — reconciled once today, but the drift
  RECURS (cross-machine, advisor-bridge duplicate commits) and SILENTLY BLOCKED
  PUSHES today until fixed.
- **Staging artifacts** — `.local-uncommitted-*.bak` droppings + un-archived docs
  (the archive-on-consumption bug).
- **run_complete markers** — batches accumulated in staging all weekend.
- **Stale tests** — the frozen `test_health_check` assertion WEDGED THE PIPELINE
  FOR 2 HOURS. There are likely others.
- Probable-but-unlooked: dead branches, orphaned tmux sessions from crashes,
  unbounded logs, superseded design docs, abandoned map atoms, old site snapshots.

**Two incidents this weekend (the stale-test wedge; divergence-blocked pushes) were
BOTH "old cruft nobody swept until it broke something."** Reactive cleanup pays for
mess in INCIDENTS. Scheduled cleanup pays for it in cheap routine sweeps. This is
the SRE toil-reduction discipline.

## The recurring housekeeping pass (inventory-and-sweep, on the maintenance lane)
- **Worktrees** — prune worktrees with NO active work (only fully-merged/abandoned;
  NEVER in-flight).
- **Branches** — delete merged/dead branches.
- **Staging** — clear archived docs, remove `.bak` droppings, sweep old
  run_complete markers (clean once the archive-on-consumption fix lands).
- **Tests** — surface assertions referencing stale facts (the frozen-test class) as
  CANDIDATES for review (harder to auto-judge — flag, don't auto-edit).
- **Logs** — rotate/truncate unbounded logs.
- **Map** — flag atoms idle/abandoned > N days as cleanup CANDIDATES for the
  director (dropping an atom is a judgment call — surface, never auto-remove).
- **Tmux/processes** — reap orphaned sessions from crashes (not live daemons).
- **Local/origin drift** — DETECT and flag divergence before it blocks pushes (the
  thing that silently broke pushes today) — ideally auto-reconcile when it's pure
  duplicate/already-applied commits, flag when it's real.

## GUARDRAILS (housekeeping that deletes the wrong thing is worse than cruft)
- **Reversible by default** — archive/move to history/, NEVER hard-delete, wherever
  possible (the director's own marker-cleanup instinct: move, don't rm).
- **Never touch in-flight work** — sweep ONLY what is PROVABLY abandoned (merged,
  idle past threshold, orphaned). Tree-lock / active-work checks before any removal.
- **Ambiguous -> FLAG, don't remove** — dropping a map atom, a branch someone might
  want, a test: surface for review, never auto-vanish. (Same class as one-way-door
  caution, applied to deletion.)
- **Schedule AND threshold** — runs on a cadence (e.g. daily) AND fires when
  accumulation crosses a threshold (e.g. > N worktrees, > M staging artifacts).
- **Transition-only reporting (R5)** — the sweep reports what it CHANGED, not a
  heartbeat every cycle. A clean sweep with nothing to do is silent.
- **Same daemon governance** — the housekeeping worker is a WORKER under existing
  walls (one-way doors escalate, kill flag applies), not a new authority. Bulk
  deletion of anything director-reserved still escalates.

## Why high-value
Converts a recurring INCIDENT SOURCE into cheap routine BACKGROUND work, running
PARALLEL to product (maintenance lane) so it costs no product velocity. It is the
thing that keeps an autonomous system running UNATTENDED from slowly choking on its
own exhaust — worktrees, drift, stale tests, log growth all silently accumulate
between the director's visits, and a scheduled sweep is what stops accumulation
reaching incident threshold while no one is watching.

## DoD
A scheduled housekeeping pass runs on the maintenance lane, on a cadence +
threshold-triggered; inventories and sweeps worktrees/branches/staging/logs/
orphaned-processes reversibly (archive not delete; never in-flight; provably-
abandoned only); flags ambiguous items (stale tests, idle atoms, real drift) for
review rather than removing; detects local/origin divergence before it blocks
pushes; reports transition-only (R5); runs under existing daemon governance. First
run: the ~64 worktrees, the .bak/run_complete staging cruft, and a drift check. A
check: an in-flight worktree is NEVER pruned; an abandoned one IS; nothing is
hard-deleted that could be archived.
