# Integration grants — completed green work must never strand off-main

**Status:** DESIGN (director-approved 2026-07-22 console; auto-integrator BUILD gated on the R15 condition in §4). Author: main session, 2026-07-22.

## The incident this fixes (evidence, not exhortation)
On 2026-07-21→22, finished, tested, green work sat in the `worktree-cwd-fix` branch for ~11h awaiting a manual director merge grant. Consequences, all observed:
1. **origin/main had ZERO work commits for ~11h** (only auto-process run-complete commits).
2. **The deadman hit 637 min.** Its liveness clock is the *meaningful git-commit clock on main alone* — so work done off-main reads as a total stall.
3. **A parallel reimplementation.** A worker on main independently rebuilt the *same* capability (the tenure→adoption / D-SEGMENT generator, under `W2_2_population_draw`) because nothing told it the worktree already owned that work. ~70% duplicated effort; the two designs then had to be reconciled by hand.

Root cause is one sentence: **there is no mechanism that carries green branch work onto main, and the stall detector cannot see work that is not yet on main.** Manual grants are a human bottleneck exactly where the project's own doctrine (MAKE_IT_STICK, PROCEED_BY_DEFAULT) says a mechanism must live.

## Design principle
Authority delegates to **proven gates, not to hope** (director, 2026-07-22). Auto-integration is safe *only* because the same gates that already protect main (the pre-commit test gate, the level-promotion gate, the fronts reconciler, the epistemic verifier) decide whether a branch merges — and because those gates are R15 mutation-proven to *refuse* the things that must not merge.

## §1 — Auto-integrator (the mechanism)
A systemd unit (sibling of `reconcile-watch.timer`, ~every 5 min) that, for each live worktree branch ahead of main:
1. **Fast-forward-or-clean-3-way check** against current main. A branch that does not merge cleanly is skipped (never force-resolved) and flagged as `needs-manual-reconcile` (a transition alert, not a stall alarm — see §3).
2. **Green gate:** the branch tip must pass the FULL pre-commit gate (test gate + level-promotion gate + site-lane gate + epistemic verifier) against the post-merge tree. A red result → NOT merged.
3. **Front/reserved gate:** every atom the branch advances must be a member of an OPEN front and must NOT cross a gate — reusing `background/fronts.yaml` + `gate_authorization.is_valid_level_up`/`is_valid_twin_level_up` verbatim. A director-reserved change (an L3 level move, a curriculum/R13 edit, a one-way door) → NOT auto-merged; it is split off and BATCHED to the director, the rest merges.
4. On success: merge to main under **`shared_tree_lock`** (the cross-worktree primitive — `background/tree_lock.py`), push, and write an **`INTEGRATE_AUTO`** ledger entry (§2).

## §2 — INTEGRATE_AUTO provenance (auditability + the daily self-note)
Every auto-merge appends one line to `docs/observability/gate_authorizations.jsonl`:
`{action: "INTEGRATE_AUTO", branch, merged_commits: [...], gates_passed: [...], ts, authorized_by: "auto-integrator", channel: "gate"}`.
- The **daily self-note counts INTEGRATE_AUTO events** as work reaching main, so an auto-integrated night reads as productive, not idle.
- The ledger is the audit trail: every autonomous merge is attributable to the exact gate-set that cleared it. No silent merges.

## §3 — Stall detector must not blind itself to off-main work
Two changes so finished work never reads as a wedge:
- The deadman's "meaningful-commit clock" additionally counts **branch work commits + INTEGRATE_AUTO events**, not main commits alone.
- A branch green+pushed for **> N minutes without integrating** raises a distinct **`stranded-green-work`** transition (its own NTFY class), NOT the deadman STALL alarm. Stranded work is visible as *work waiting to land*, never as *the machine is dead*.

## §4 — R15 CONDITION ON GO-LIVE (director-mandated, 2026-07-22, binding)
The auto-integrator does NOT go live until it is **mutation-proven in BOTH directions** (CONTROLS_THAT_CANNOT_FAIL doctrine — a control that cannot fail is worse than none):
- **A red-gate branch MUST NOT merge.** Test: plant a branch whose tip fails the pre-commit gate (a deliberately-broken test / a failing invariant) → assert the integrator REFUSES it and leaves main untouched.
- **A director-reserved change MUST NOT merge.** Test: plant a branch with (a) an unauthorized L3 `level_current` bump and (b) a curriculum/R13 edit → assert the integrator REFUSES to auto-merge either, and BATCHES them to the director instead.
- **The happy path DOES merge + writes INTEGRATE_AUTO.** Test: a clean, green, in-front branch → asserts it merges and the ledger carries the INTEGRATE_AUTO line.
- **Fail-safe:** an unreadable gate result / an unreachable main / a lock timeout → REFUSE (no merge), never fail-open.
These live in `tests/background/test_auto_integrator.py` and must be green before the systemd unit is enabled.

## §5 — Cross-tree work registry (prevents the duplicate build)
Before the on-main draw starts a BUILD, it consults a registry of `{worktree branch → atoms/file_scopes in flight}` and skips any atom a live worktree already owns — extending the existing `file_scope`-disjoint multi-atom-draw discipline across worktrees. This is the direct fix for the 2026-07-21 parallel D-SEGMENT build: had it existed, the on-main worker would have seen the worktree already owned the tenure→adoption gating and drawn something else.

## What NOT to build (SIMPLICITY GUARD)
No new merge engine — reuse git + the existing gates. No parallel authorization store — reuse `gate_authorizations.jsonl`. No new lock — reuse `shared_tree_lock`. The integrator is glue over proven parts, not new architecture.
