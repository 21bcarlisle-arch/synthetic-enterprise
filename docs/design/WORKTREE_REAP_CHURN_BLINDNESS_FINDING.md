# FINDING — the worktree reaper can't tell background-churn from fork work (H10 red-team)

**Stage:** FINDING → FRAME (off-front harness item; DISCOVER/FRAME only until a harness front / director BUILD_OPEN). **Lane:** H_harness. **Provenance:** a grounded H10 (worktree isolation) red-team from repeated first-hand incident THIS session (2026-07-18).

## The defect (confirmed in code + observed repeatedly)
`background/fork_reconciler.py`:
- `_worktree_dirty(path)` (line ~314) = `git status --porcelain --untracked-files=all` → **any** uncommitted/untracked entry ⇒ dirty.
- `classify_worktree_reap(...)` (line ~361): `if dirty: eligible=False, "uncommitted/untracked changes -- never reaped"`.

But **background daemons write into every worktree**: `docs/observability/*log*.md`, `docs/observability/*.jsonl` (deadmans-switch-log, test_execution_log, …), `site/data/*.json`, `site/state/*`, market-data/state caches — none of it fork work, all of it regeneratable churn that main owns. So a **MERGED, work-complete** fork worktree whose ONLY dirt is this churn is classified `not eligible` and is **never auto-reaped**.

## Evidence (first-hand, this session)
- **Every one** of the fork reaps this session (regulatory-tab, debt-B/C/D) refused the no-force `git worktree remove` on churn (`M docs/observability/deadmans-switch-log.md`, `M site/data/wip_flow.json`, …) and needed a manual `git -C <wt> checkout -- .` + `clean -fd` before the reap succeeded.
- The stale `a857b050` worktree (pre-session) **still cannot** be no-force reaped for exactly this reason (dirty with observability logs), so it lingers.
- Connects to the known **worktree-scan hazard** (memory `reference_worktree_scan_hazard`): stale worktrees accumulate (64 seen historically), tree-scanning tests/controls false-positive on their stale copies, and that **jams the publish pipeline**. Churn-blindness in the reaper is an upstream cause of that accumulation.

## Why it matters / fit
The reaper's job is "every fork comes home: merged→reaped." A reaper that can't reap a merged worktree because a daemon touched a log in it does not do that job — the merge-or-reap invariant silently degrades into merge-then-linger, and the lingering worktrees are a real publish-pipeline hazard, not cosmetic. The no-force safety net is correct and must stay; the fix is to make the *eligibility classifier* churn-aware, not to weaken the remove.

## Fix direction (FRAME)
Split "dirty" into **fork-dirty** vs **churn-only**:
- Define a tight, explicit CHURN_ALLOWLIST of daemon-written, main-owned, regeneratable path globs (`docs/observability/**` logs+jsonl, `site/data/*.json`, `site/state/**`, the market-data/state caches — the exact set already excluded from `git add` discipline elsewhere).
- `classify_worktree_reap`: a MERGED/salvaged worktree whose dirt is **entirely** within CHURN_ALLOWLIST → eligible; the reaper first restores/cleans only those churn paths (`git checkout -- <churn>` + scoped `clean`), then does the **unchanged no-force** `git worktree remove` (git's refusal stays the second net for anything the allowlist missed).
- Dirt containing **any** path outside the allowlist (a real `.py`/source edit = fork work) → stays `not eligible`, never reaped. Unchanged fail-safe: an unreadable tree is still dirty.

## R15 — must be able to FAIL (mutation test, required before any L2+ claim)
- **Fires (never over-reaps):** a worktree with a genuine fork edit outside the allowlist (e.g. `company/foo.py` modified) MUST classify `not eligible` even if churn is also present. Neuter the allowlist bound (treat all dirt as churn) → the real edit gets reaped → the mutation test must catch it.
- **Reaps churn-only:** a worktree dirty ONLY with allowlisted churn → eligible; verify the churn paths are restored (not committed, not lost) before remove.
- **Fail-closed:** allowlist match is by exact glob on the porcelain paths; an unreadable status is still dirty; git's no-force remove remains the independent second net.

## Open questions for BUILD-open
1. The exact CHURN_ALLOWLIST — reuse the same exclusion set already encoded for `git add` discipline (single source of truth) rather than a second hand-maintained list.
2. Whether to also add a periodic sweep that reaps churn-only-dirty MERGED worktrees left by earlier runs (would clear `a857b050` and any siblings) — or leave that to the next reconcile pass once the classifier is churn-aware.

**No BUILD here.** Mitigation until built (already the current practice, now recorded): reap manually with `git -C <wt> checkout -- .` to drop churn, then no-force `git worktree remove`. Relates `reference_worktree_scan_hazard`, `feedback_check_fronts_before_twin_open` (don't reap a live fork), and the Campaign-A debt-E coverage-seam FRAME (same "a control that can't do its job silently degrades an invariant" shape).
