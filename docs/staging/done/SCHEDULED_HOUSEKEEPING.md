# SCHEDULED HOUSEKEEPING — sweep the cruft on a cadence, before it causes incidents (P1, director-decided)

**Staged:** 2026-07-16 by advisor, **director-decided**. Disposition: QUEUE-high.
A standing function of the MAINTENANCE LANE (PARALLEL_MAINTENANCE_LANE, 600f0687).
Director: "Have we got stale trees and other no-longer-needed things? Should we
schedule regular housekeeping?" — yes, and there is none today: cleanup is
REACTIVE (happens when something breaks), which is the worst model.

## The problem: cruft accumulates, and we pay for it in INCIDENTS not sweeps
Provably accumulating this weekend:
- **~64 stale worktrees** (deliberately not cleaned mid-session; a plausible
  source of the grep-guard false-positive).
- **~30 commit local/origin divergence** (cross-machine, advisor-bridge duplicate
  commits; reconciled once today, RECURS — and it silently BLOCKED PUSHES today).
- **Staging artifacts** — `.local-uncommitted-*.bak` files, un-archived docs
  (archive-on-consumption bug droppings).
- **run_complete markers** — batches accumulating in staging all weekend.
- **Stale test assertions** — the frozen test_health_check wedged the whole
  pipeline for 2 HOURS; that class exists elsewhere.
Likely also: dead branches, orphaned tmux sessions from crashes, unbounded logs,
superseded design docs, abandoned/idle map atoms, old Pages snapshots.

**Two incidents this weekend (the stale-test wedge; divergence-blocked pushes)
were BOTH "old cruft nobody swept until it broke something."** Reactive cleanup
pays for the mess in downtime. Scheduled cleanup pays cheaply, in advance.

## The fix: housekeeping as a STANDING, SCHEDULED maintenance-lane function
A recurring sweep (SRE toil-reduction discipline) that inventories and clears
what is no longer needed, on a cadence, so cruft never reaches incident scale:
- **Worktrees** — prune worktrees with no active work (only fully merged/abandoned
  ones; NEVER in-flight).
- **Branches** — delete merged/dead branches.
- **Staging** — clear archived docs, remove `.bak` droppings, sweep old
  run_complete markers (clean once the archive-on-consumption fix lands).
- **Tests** — surface assertions referencing stale facts (the frozen-test class)
  as candidates for review.
- **Logs** — rotate/truncate unbounded logs.
- **Map** — flag atoms idle/abandoned past N days as cleanup candidates (for the
  director — dropping an atom is a judgment call).
- **Processes** — reap orphaned tmux sessions from crashes.
- **Local/origin drift** — DETECT and flag divergence before it blocks pushes
  (the exact thing that silently broke pushes today).

## GUARDRAILS (housekeeping that deletes the wrong thing is WORSE than cruft)
- **Reversible by default** — archive/move to history/, NEVER hard-delete, wherever
  possible (the director's own marker-cleanup principle: move, don't rm).
- **Never touch in-flight work** — sweep only what is PROVABLY abandoned (merged,
  idle past threshold, orphaned). File-scope/tree-lock aware.
- **Ambiguous -> FLAG, don't remove** — dropping a map atom or a maybe-wanted
  branch is a judgment call; surface it for review, never auto-vanish it. (And
  never escalate these as one-way doors — they're reversible; per the predicate
  fix, a flag is not a door.)
- **Cadence AND threshold-triggered** — run on a regular schedule (e.g. daily)
  PLUS fire when accumulation crosses a threshold (e.g. > N worktrees).
- **Same daemon governance** — reversible sweeps proceed autonomously; the
  maintenance worker runs it under the existing walls; transition-only reporting
  (R5) so the sweep itself doesn't become notification noise.

## Why high-value
Converts a RECURRING INCIDENT SOURCE into cheap routine background work, running
PARALLEL to product (maintenance lane) so it costs no product velocity. It is the
thing that keeps an unattended autonomous system from slowly choking on its own
exhaust — and it directly prevents the two incident classes already hit this
weekend (stale-test wedge, divergence-blocked pushes).

## DoD
A scheduled housekeeping pass runs as a standing maintenance-lane function on a
cadence + threshold trigger; inventories and sweeps worktrees/branches/staging/
logs/orphaned-processes/local-origin-drift; reversible-by-default (archive not
delete); never touches in-flight work; ambiguous items (map atoms, maybe-wanted
branches) flagged for director review not auto-removed; reports transition-only;
first run clears the ~64 stale worktrees (safely) and detects local/origin drift.
A check: run the sweep with an in-flight worktree present — it prunes the
abandoned ones and leaves the active one untouched.
