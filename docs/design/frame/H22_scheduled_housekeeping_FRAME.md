# H22 FRAME: Scheduled housekeeping — a standing cadence+threshold cruft sweep

**Status:** DISCOVER/FRAME (this doc, first design doc, 2026-07-16). BUILD NOT
started — deliberately, EPOCH_GATING R1 (H22 is `loop_stage: idle`, epoch 2).
Level HELD at 0. This is a design artefact for a later BUILD fork; it contains
NO runtime code.

**Atom:** `H22_scheduled_housekeeping` (lane H_harness, `depends_on:
[H20_parallel_maintenance_lane]`). H22 is a standing **function OF** the H20
maintenance lane — it does not introduce a new worker or a new authority. It is
one scheduled work-type the H20 maintenance worker draws and runs under the
existing walls. Where this doc and the H20 registration text disagree, H20 wins;
H20 has no FRAME doc yet (2026-07-16), so this frames against the H20 registration
in `docs/design/maturity_map.yaml`.

**Source directive:** `docs/staging/done/SCHEDULED_HOUSEKEEPING.md`
(director-decided, P1).

---

## 1. The problem, restated from evidence (not narrative)

Cleanup today is **REACTIVE** — it happens only when accumulated cruft breaks
something. That is the worst possible model for an unattended autonomous system:
it pays for the mess in *incidents* (downtime + the director's attention, the one
scarce resource), not in cheap routine sweeps. Two incidents this weekend were
both "old cruft nobody swept until it broke something":

1. A frozen `test_health_check` (stale assertion) wedged the publish pipeline for
   ~2 hours.
2. A ~32-commit local/origin divergence silently **blocked pushes** — invisible
   until a push failed.

Cruft measured directly at FRAME time (2026-07-16, this working tree), so the
design is grounded in real magnitudes rather than the directive's estimates:

| Category | Measured now | Directive estimate |
|---|---|---|
| Worktrees (`git worktree list`) | **78** | ~64 |
| Local branches total (`git branch`) | **113** | — |
| Local branches merged into `main` | **80** | — |
| `run_complete_*` markers in `docs/staging/` | **7** | "batches" |
| `.local-uncommitted-*.bak` / `*.bak` droppings | **1** | present |
| Local/origin drift | recurs cross-machine | ~32 commits, blocked pushes |

The magnitudes matter for the trigger design (§2): 80 provably-merged branches and
78 worktrees is already well past any sane threshold — the first run has real work.

---

## 2. Trigger model — CADENCE **and** THRESHOLD (both, not one)

A single trigger is insufficient, and the two triggers guard different failure
modes:

- **CADENCE (time-based).** A recurring sweep on a fixed schedule (design default:
  **daily**, one pass). Guards *slow* accumulation and catches the class of cruft
  that never crosses a dramatic threshold but still rots (a stale test assertion,
  a slowly-growing log). Cadence is the SRE toil-discipline baseline: the sweep
  happens whether or not anything looks alarming.

- **THRESHOLD (accumulation-based).** Fire an *extra* sweep the moment a category
  crosses a bound, so a burst between cadence ticks can't reach incident scale.
  Design defaults (DIALS, tunable, never targets — R12):
  - worktrees `> 40`
  - merged-but-undeleted local branches `> 40`
  - `run_complete_*` markers `> 10`
  - any single unbounded log `> 50 MB`
  - local/origin drift `≥ 5` commits either direction (DETECT early — see §3.6)

Both triggers converge on the **same idempotent sweep pass** (§4). Running the
sweep when there is nothing to clear must be a cheap no-op (C-S2 idempotency:
processing the same clean state twice is harmless). The threshold values live in
config, not code constants, so tuning them is not a BUILD change.

The sweep is **invoked by the H20 maintenance lane**, not a new daemon: H20 draws
"scheduled housekeeping" as a work-type on its cadence, or on a threshold event,
and runs one pass under the existing daemon governance (predicate-gated
escalation, Rule 0, per-atom integration, kill flag). No new scheduler process is
introduced by H22 — that would duplicate H20's reason to exist.

---

## 3. Inventory categories + the per-category "provably abandoned" PREDICATE

The predicate is the crux of the whole atom: *what exactly makes an item
safe-to-clear vs. in-flight vs. ambiguous?* Every category classifies each item
into one of three buckets:

- **CLEAR** — provably abandoned by the predicate → reversible sweep (§4/§5).
- **IN-FLIGHT** — provably live → **never touched**, not even flagged.
- **AMBIGUOUS** — cannot be proven either way → **FLAG for director review**
  (§5), never auto-cleared, never escalated as a one-way door (it's reversible).

The default on any predicate failure or missing signal is **AMBIGUOUS, not
CLEAR** — fail-closed (R15: a control that fails open is worse than none; an
unavailable signal is a failed check, so it degrades to "flag", never to
"delete").

### 3.1 Stale worktrees (`.claude/worktrees/`)

A worktree is **CLEAR** iff ALL hold:
- its branch is fully merged into `main` (`git branch --merged main` contains it),
  **OR** its HEAD commit is an ancestor of `main` (`git merge-base --is-ancestor`),
  **OR** it is orphaned (its backing branch no longer exists / `git worktree list`
  shows it `prunable`); AND
- it is **idle past threshold** — no file mtime under the worktree newer than N
  hours (design default N=24h); AND
- it holds **no tree-lock** (not the shared `.tree.lock`/`.tree-shared.lock`
  holder) — an active `flock` holder is by definition live; AND
- it is not in any **active fork's declared `file_scope`** — cross-check against
  the live-fork registry the supervisor already maintains (the multi-atom draw
  tracks in-flight file_scopes; the sweep consults it, it does not invent one).

**IN-FLIGHT** iff it holds a tree-lock, OR has a file mtime within N hours, OR is
the working dir of a registered live fork.
**AMBIGUOUS** iff merged-status cannot be determined (detached HEAD with no
merge-base resolvable), OR the fork registry is unavailable (fail-closed).

Clearing = `git worktree remove` (git's own reversible removal; the branch is
retained until §3.2 reaps it separately, so no commit is lost). 78 worktrees →
the large majority are expected CLEAR on first run; the DoD test (§6) proves an
IN-FLIGHT one survives.

### 3.2 Dead / merged branches

A local branch is **CLEAR** iff: fully merged into `main` AND not currently
checked out by any worktree AND not the current branch AND not on a protected
name list (`main` and any director-named long-lived branch). 80 merged branches
measured now.
**AMBIGUOUS** iff it is unmerged but idle-past-a-longer-threshold (design default
14 days) — an unmerged branch may hold un-landed work; that is a judgment call →
FLAG, never delete.
Clearing = the branch ref is **archived** first (write the ref/SHA to a
`housekeeping/archived_branches.log` or a `refs/archive/…` namespace) THEN
`git branch -d` (safe delete, which itself refuses unmerged branches — a second
belt-and-braces guard). Reversible: the SHA is recorded, so the branch is
recreatable.

### 3.3 Staging droppings

- `.local-uncommitted-*.bak` and stray `*.bak` under `docs/staging/`: **CLEAR** iff
  older than N hours AND not referenced by any open staged doc. These are pure
  droppings from the archive-on-consumption defect (H20's first workload kills the
  *source*; H22 sweeps the *residue*).
- Orphaned `run_complete_*` markers: **CLEAR** iff the run they mark is confirmed
  processed (its output published / archived) — the predicate checks the
  processed-state, not just the file's age. 7 present now.
- Un-archived actioned docs sitting in scanned staging root: **AMBIGUOUS** by
  default (a doc in the scanned root may be genuinely open) → FLAG, do not move.
Clearing = move to `docs/staging/done/` or a `history/` archive, never `rm`.

### 3.4 Unbounded logs

A log is **CLEAR-to-rotate** iff it exceeds a size bound (default 50 MB) OR an age
bound. Clearing = **rotate/truncate-with-archive** (move tail to `*.N.gz` or an
archived copy), NEVER delete the live log. The observability logs are consumed by
other controls, so rotation must preserve the most-recent window intact.

### 3.5 Orphaned tmux panes / processes

A tmux session/pane is **CLEAR** iff it is provably orphaned — its owning process
is dead (PID gone) OR it is a known daemon name whose supervisor shows it should
not be running AND it holds no tree-lock. **IN-FLIGHT** iff it maps to a live
registered daemon (supervisor, autonomous_runner, sim_runner) — never reaped.
**AMBIGUOUS** iff ownership can't be resolved → FLAG. Reaping a live pane could
kill in-flight work, so this category is the most conservative: default
AMBIGUOUS on any doubt.

### 3.6 Local/origin drift — **DETECT before it blocks**

This category is **detect-and-flag, not auto-clear** — reconciling divergent
history is a judgment call (rebase vs. merge vs. reset) and can lose commits, so
the sweep NEVER auto-resolves it. Its job is to fire the alarm *early*:
- Compute ahead/behind counts vs. `origin/<branch>` (`git rev-list --left-right
  --count`). This does not require a push; a `git fetch` (read-only) suffices.
- **FLAG** (transition-only, §5) the moment drift `≥ threshold` — well before the
  ~32-commit level that silently blocked pushes this weekend.
- The flag names the exact remediation options; it does not act. This directly
  pre-empts the second weekend incident.

---

## 4. The sweep pass — properties (design, not implementation)

- **Idempotent (C-S2).** Running twice = running once; a clean tree is a cheap
  no-op. No sweep result depends on how many times it has run.
- **Reversible by construction (§5).** Every CLEAR action is archive/move/rotate,
  never hard-delete. `git worktree remove` and `git branch -d` are git-reversible
  (refs recorded first).
- **Order-independent.** Categories are swept independently; one category's
  failure (e.g. the fork registry is unavailable, forcing §3.1 to AMBIGUOUS) does
  not block the others. A category that cannot evaluate its predicate degrades to
  "flag/skip", never to "clear" (fail-closed).
- **Tree-lock aware.** Any git-state mutation (worktree/branch removal) runs
  inside `with tree_lock():` per the concurrent-writers rule — the sweep is one
  more writer on the shared tree.
- **Never writes the map.** `docs/design/maturity_map.yaml` is orchestrator/
  integrator-written only (H9/H10 doctrine, a `PROTECTED_PATH`); the sweep only
  ever *flags* an idle map atom for review, never edits the map.

---

## 5. Guardrails (deleting the wrong thing is worse than the cruft)

1. **Reversible by default.** Archive / move to `history/` / rotate — **NEVER
   hard-delete.** Git-native removals (`worktree remove`, `branch -d`) are used
   because they are recoverable (ref/SHA recorded first). No `rm -rf`, no
   `branch -D` (force-delete), no `git gc --prune=now`.
2. **Never touch in-flight work.** Sweep only PROVABLY-abandoned items (§3
   predicates). File-scope-aware and tree-lock-aware. When in doubt, do not act.
3. **Ambiguous ⇒ FLAG, never auto-vanish AND never escalate as a one-way door.**
   A map atom, a maybe-wanted unmerged branch, an unresolvable process — surface
   it for director review (a flag doc / register entry), and let it sit. Because
   every sweep action is reversible, an ambiguous item is **not a one-way door**
   (per `background/one_way_door.py` + the predicate fix `c157f862d`: reversible
   ⇒ a flag is not a door ⇒ do NOT fire a one-way-door escalation for it). The
   flag is a low-noise review queue, not an NTFY interrupt.
4. **Transition-only reporting (R5).** The sweep reports only on STATE CHANGES —
   "cleared N worktrees / M branches, flagged K ambiguous, drift now D commits" —
   and only when those numbers change vs. the last pass. A pass that clears
   nothing and finds nothing new is SILENT (idle isn't progress worth reporting).
   The sweep must not itself become notification noise — that would replace one
   toil with another. A DRIFT flag crossing threshold IS a transition → it
   notifies once; a still-clean tree stays silent.
5. **Bounded by verification, governed by H20.** Runs under the maintenance lane's
   existing walls; utilisation/sweep-frequency is a diagnostic, never a target
   (R12). The kill flag stops it like any daemon work-type.

---

## 6. DoD acceptance test (from the directive)

The load-bearing acceptance test, restated as the BUILD fork's exit gate:

> **Run the sweep with an in-flight worktree present. It prunes the abandoned
> worktrees and leaves the active one untouched.**

Concretely, the BUILD test must:
1. Construct a fixture with (a) ≥1 provably-abandoned worktree (branch merged into
   `main`, mtimes older than threshold, no lock), and (b) ≥1 in-flight worktree
   (holds the tree-lock OR has a fresh mtime OR is a registered live fork).
2. Run one sweep pass.
3. Assert: the abandoned worktree(s) are removed (and their branch refs archived),
   AND the in-flight worktree is **still present and untouched** (no file mtime
   changed, lock intact).
4. **Mutation test (R15):** flip the in-flight worktree's classification signal
   (e.g. drop its lock / age its mtimes) and assert the sweep now WOULD clear it —
   proving the predicate actually gates on that signal and is not a tautology /
   fail-open. A predicate that clears the in-flight worktree in step 3, or that
   passes step 4 without the signal mattering, is a FAILED control.

Additional exit checks: idempotency (run twice, second pass is a no-op), the
ambiguous-⇒-flag path fires on a fixture unmerged-idle branch without deleting it,
and the drift detector flags a fixture with ≥threshold ahead/behind commits
without attempting to reconcile.

---

## 7. L0 → L3 ladder + what stays BUILD-GATED

- **L0 (now).** Registered + this FRAME. Design only. No sweep exists.
- **L1 (BUILD, gated).** The sweep implemented as an H20 maintenance-lane
  work-type: cadence+threshold trigger wired to the H20 worker, the six category
  predicates, reversible-by-default clearing, the flag queue, transition-only
  reporting. Exit: the DoD test (§6) incl. the mutation test passes; a first real
  pass clears the merged-branch/abandoned-worktree backlog and detects drift.
- **L2 (harden).** Expert-Hour cold-eyes pass on the predicates (the real risk is
  a false CLEAR on a live item); run against the real 78-worktree / 80-merged-
  branch state; confirm each predicate's fail-closed behaviour with the signal
  removed; confirm the sweep is genuinely silent on a clean tree.
- **L3 (settled).** Standing function running under H20 on cadence+threshold, with
  a demonstrated history of clearing cruft without ever touching in-flight work,
  and time-scale-invariance declared (C-S5) or its exception registered (R10).

**BUILD-GATED (this fork must NOT do):** any code under `background/`, `tools/`;
any `git worktree remove` / `git branch -d`; any file move/rotate/delete; any edit
to `docs/design/maturity_map.yaml`; any commit/add/push. All of that is L1+ BUILD
work for a later fork, only after this atom is BUILD-opened per EPOCH_GATING
(DIRECTOR_TWIN's call for BUILD-within-the-open-epoch).

---

## 8. Relationship to H20 (the maintenance lane)

H20 is the **lane** (a standing worker drawing bug-fix/housekeeping work parallel
to BUILD/DISCOVER/SITE, integrating per-atom through the external-truth gate,
bounded by file-scope disjointness). H22 is **one scheduled work-type that lane
draws**. The split matters:

- H20 owns *the worker and its governance* (kill flag, predicate-gated escalation,
  per-atom integration, file-scope disjointness). H22 adds **no new authority** —
  it is a task on H20's backlog, invoked on H22's cadence/threshold.
- H20's *first* workload (registration) is REACTIVE-defect burndown (kill the
  archive-on-consumption defect; make notifications transition-only). H22 is the
  *proactive, scheduled* complement: sweep before cruft becomes an incident.
- Sequencing: H22's BUILD depends on H20 existing (its `depends_on`). Until the
  H20 lane BUILDs, H22 stays FRAME. A useful thin-start: H22's sweep could be a
  standalone idempotent pass first, then be *drawn by* the H20 worker once that
  lands — but that sequencing is a BUILD decision for the later fork, not settled
  here.

---

## 9. Open questions for the BUILD fork (not blocking FRAME)

- **Fork registry source of truth for §3.1.** Confirm the exact in-flight
  file_scope / live-fork registry the supervisor maintains and read from it; do
  NOT invent a parallel registry. If none is queryable, §3.1 degrades to
  merged+idle+lock signals only and worktrees whose status can't be proven stay
  AMBIGUOUS (fail-closed) — acceptable but weaker.
- **Idle thresholds (N hours / days) as config DIALS.** Defaults proposed (24h
  worktree idle, 14d unmerged-branch, 50 MB log) are starting points, not
  targets; tune from the first real run's distribution.
- **Where flags live.** Reuse an existing register (e.g. the action-needed
  register / a `housekeeping_flags.json`) rather than a new NTFY channel — R5 /
  low-noise. To be decided at BUILD against what already exists.
- **Time-scale invariance (C-S5).** The sweep's logic keys on wall-clock idle
  thresholds, so it is NOT time-scale invariant by construction — register that as
  a named simplification (R10) at L3, or express thresholds in a scale-relative
  unit.
