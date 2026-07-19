# Resource-aware scheduling — proposal (light must never queue behind heavy)

**Provenance:** director steer, `docs/staging/DIRECTOR_STEER_RESOURCE_AWARE_SCHEDULING_2026-07-19.md`.
**Status:** PROPOSAL ONLY — no code changed by this document. Sequenced per the steer: report cause →
propose model → adopt incrementally, bound proven at each step. Do NOT change the draw and the fan cap
in the same turn.

## 0. Root cause (evidence, not reconstruction)

Between ~06:28 and ~08:32 UTC on 2026-07-19 the main seat produced no commits for ~62 minutes while
`pytest tests/sim/ tests/simulation/` ran (task `bi08d760g`, backgrounded after exceeding the 120s
foreground limit, total runtime 3753s ≈ 62.5min).

**The seat was NOT hard-blocked by the tool.** The suite ran in the background exactly as designed. The
stall was a **scheduling choice**: the orchestrator held the turn open, waiting synchronously for the
validation result before gating the SSP push on it — which is correct discipline (never skip
verification) — instead of ending the turn (or dispatching parallel light work) so the Stop hook
(`.claude/hooks/pull_next_work.py::decide()`) could re-draw immediately. `decide()` is stateless per
turn: it calls `find_work()` fresh every time and has no notion of "a heavy job is in flight" today —
which means it *also* has no mechanism preventing the orchestrator from re-drawing light work in
parallel. The harness permits interleaving. The flaw is that nothing makes interleaving the **default**
— it was left to in-turn judgement, and this session's judgement chose to wait instead of draw. Two
staged advisor steers sat unconsumed in `docs/staging/` throughout the stall; DISCOVER/FRAME work sat
drawable the entire time.

**This proposal's job is to make "keep light flowing while heavy holds a slot" the mechanised default,
not a per-turn judgement call.**

## 1. Resource-class mapping — `loop_stage` as the free proxy

The draw today reads only `level`, `dial_inherited`, `loop_stage`, `depends_on`. No new metadata is
needed to start — `loop_stage` already tells us what class of work an atom is:

| `loop_stage` | resource_class | why |
|---|---|---|
| `discover` | **light** | document/research output, no code, no tests run |
| `frame` | **light** | charter/design writing, no code, no tests run |
| `idle` (drawn via the DISCOVER/FRAME tier only, per Rule 7 — never BUILD) | **light** | same as above |
| `build` | **moderate** | code + targeted tests for the atom's own scope |
| `verify` | **heavy** | full validation run |
| `harden` | **heavy** | full validation, mutation-re-test, red-team, Expert Hour re-verification |

Rule: **at most 1 concurrent heavy job, plus N concurrent light jobs** (moderate bounded separately, §2).
This is a pure classification over an existing field; it changes no behavior by itself (Adoption Step 1).

## 2. The fan bound restated as a resource budget (not a count) — with the R15 proof

### Today
`MAX_CONCURRENT_FORKS = 3` (`background/supervisor.py:202`) is a single flat ceiling shared across all
three lanes (BUILD, SITE, DISCOVERY), filled BUILD > SITE > DISCOVERY (`_self_refill_draw`,
`supervisor.py:1257-1287`). Because it is one shared pool, a saturating BUILD/heavy draw can trim
SITE/DISCOVERY to zero even though those lanes cost near-zero CPU and are file-scope-disjoint from BUILD
by construction. The count treats a design doc and a full-suite validation as equivalent units when they
differ by orders of magnitude.

### Proposed budget shape
- `HEAVY_FORK_BUDGET = 1` — gates concurrently-dispatched sessions whose atom's `resource_class == heavy`
  (loop_stage ∈ {verify, harden}), **and** any long-running validation the orchestrator itself
  backgrounds (tracked via the advisory registry, §3) counts against this same slot.
- `MODERATE_FORK_BUDGET = 3` — today's value, renamed and scoped to BUILD-class atoms only. **Unchanged
  value** — this proposal widens nothing; widening is the separate pending `FAN_WIDENING_SAFETY_CASE.md`.
- `LIGHT_FORK_BUDGET` — the existing per-lane widths (`SITE_LANE_CONCURRENT_WIDTH=3`,
  `IDLE_DISCOVER_FRAME_CONCURRENT_WIDTH=6`) kept as coded but **no longer sharing a pool** with
  heavy/moderate — light lanes are never trimmed to make room for a heavy/moderate saturation.

### Invariants (what "provably bounded" means)
- **I1:** concurrent heavy forks ≤ `HEAVY_FORK_BUDGET`.
- **I2:** concurrent moderate forks ≤ `MODERATE_FORK_BUDGET`.
- **I3:** light-class forks bounded only by their existing per-lane widths; never trimmed by I1/I2.
- **I4 (WALL, unchanged, non-negotiable):** every concurrently-dispatched fork of any class is
  file-scope-disjoint from every other in flight; every commit serializes through `tree_lock()`; every
  fork is merge-or-reaped; the locked-worktree reap guard (`classify_worktree_reap`) is untouched. This
  proposal touches only how many of each class run concurrently — never disjointness, locking, or reap.

### R15 mutation tests (mirror `test_self_refill_draw_bounds_fan_out_to_three_not_twelve`)
1. `test_heavy_fork_count_bounded_to_budget` — 4 heavy candidates → draw contains ≤1; monkeypatch budget
   to 4 → all 4 appear (proves the constant, not incidental draw, bounds it).
2. `test_light_lanes_never_trimmed_by_heavy_or_moderate_saturation` — 1 heavy at budget + full moderate +
   full light → ALL light atoms still appear; reintroduce shared-pool trimming → light atoms dropped.
3. `test_fork_lifecycle_guard_unchanged_under_new_budget` — the reap/lock guard tests pass unmodified.
4. `test_heavy_in_flight_never_empties_the_draw` — with heavy-in-flight true, `find_work()` still returns
   non-None light/moderate work (interleave, never idle — requirement 5).

## 3. The consume-path fix (requirement 4)

`find_work()` already checks unprocessed `docs/staging/*.md` **before** the self-refill draw — staged-steer
consumption already has code priority. The 06:28 failure was the orchestrator not ending the turn after
backgrounding heavy work. Two parts:
1. **Mechanism — an advisory "heavy in flight" registry** (`docs/observability/.heavy_job_in_flight.json`,
   `{task_id, started_at}`), read ONLY to decide heavy-lane eligibility. **Fail open toward drawing** — an
   unreadable/missing registry never withholds light/moderate work (Rule-0 fail-safe).
2. **Policy — the turn ends, it doesn't wait.** After backgrounding a heavy validation, the same turn
   proceeds to staged-steer consumption + `[ACT]` composition + light dispatch, then ends so the Stop hook
   redraws — rather than a synchronous wait. The validation-gates-the-push discipline is unchanged; only
   the *exclusivity of attention while waiting* is removed.

## 4. Incremental adoption (bound proven at each step; draw and fan cap never change together)

| Step | Change | Contract-touching? | Revert | Proof |
|---|---|---|---|---|
| 0 | This doc. No code. | No | — | — |
| 1 | `resource_class_of(atom)` pure helper, wired to LOGGING only. | No | delete helper | unit test vs fixture map |
| 2 | Heavy-in-flight registry as an advisory READ in `find_work()`, proven no-op. | Minor (fail-open) | delete reader | draw identical with/without the file |
| 3 | Split `MAX_CONCURRENT_FORKS` → `HEAVY=1`/`MODERATE=3`(unchanged)/decoupled `LIGHT`. | **Yes** — the draw spine | restore single constant | the 3 mutation tests §2 |
| 4 | Wire real `HEAVY_FORK_BUDGET` enforcement once a concurrent VERIFY/HARDEN lane exists (no-op today). | Deferred | — | — |
| 5 | Process policy: background heavy → end turn, never synchronous wait. | No (prose) | delete paragraph | behavioral |

Steps 1–2 are pure instrumentation (land immediately). Step 3 is the one contract-touching step, isolated
from step 5 — satisfying "do NOT change the draw and the fan cap in one turn."

## 5. One-way-door / [ACT] flags
- Step 3 is contract-touching but **not a one-way door** — a value-preserving integer/logic change,
  instantly revertible, touching none of I4. Implement with the §2 mutation tests; no [ACT] for Step 3.
- **Genuine wall:** any change letting a heavy atom skip the disjoint-scope check, letting the reap guard
  treat a locked/live worktree as reapable, or letting a commit bypass `tree_lock()` — one-way-door safety
  weakening, MUST return as an [ACT]. This proposal makes none.
- `HEAVY_FORK_BUDGET` above 1 is director-reserved (like `MAX_CONCURRENT_FORKS` widening — §6).

## 6. Note for the fan-widening [ACT] (prerequisite)
`FAN_WIDENING_SAFETY_CASE.md` proposes ≤3 → `min(cores−2, 8)`. Per requirement 3, reframe it: since this
proposal splits the pool into HEAVY/MODERATE/LIGHT, the pending widening should be understood as widening
**`MODERATE_FORK_BUDGET` only** (BUILD-class concurrency, where the safety case genuinely applies).
`HEAVY_FORK_BUDGET` stays at 1 pending its own separate safety case — heavy jobs are precisely the ones
that saturate a shared machine. Recommend the fan-widening [ACT] be amended to state this split before sign-off.
