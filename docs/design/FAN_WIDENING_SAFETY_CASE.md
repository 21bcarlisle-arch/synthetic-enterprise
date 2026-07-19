# Fan-widening beyond ≤3 — safety case (proposal for director sign-off)

**Provenance:** director console 2026-07-19, gate-after model item 7 — *"Parallel: propose the fan-widening
beyond ≤3 with your safety case — stability has earned the proposal."*

**Ask:** replace the fixed `≤3 concurrent forks/draw` DIAL with a **disjointness-and-verification-bounded width**,
ceilinged at `min(cpu_cores − 2, 8)` (≈8 on Skynet's i5-13400F). This is a **DIAL**, not a wall — it orders work,
never zeroes it (Rule 0). Below is why the number 3 was never the real safety boundary, what actually bounds
safe width, and the one genuine gap that must stay respected.

## 1. Why "3" is not the safety boundary
`≤3` was a caution-era default, not a measured ceiling (the naive-organ is right to press this: no width-4
failure was ever observed — see LATEST asks T3_inherence). Safety at width N has never depended on N; it depends
on four **structural** properties that are already mechanised and hold at any N:

| Property | Mechanism (already live) | Fails loud if violated? |
|---|---|---|
| **Disjoint file_scope** — no two forks touch the same path | `supervisor.py::_maturity_map_draw_concurrent` grants concurrent atoms only on provably disjoint `file_scope` | Yes — non-disjoint atoms simply aren't co-drawn |
| **Serialized git writers** — no interleaved commits on the shared tree | `background/tree_lock.py` (`with tree_lock()`) around every add+commit+push | Yes — the lock blocks; a bypass is a code review catch |
| **Merge-or-reap** — every fork comes home | fork-lifecycle reconciler (report-first): merged on success, salvage-tagged + reaped on failure | Yes — a stranded fork is reconciled + loud |
| **Red-test commit impossible** | pre-commit test gate on every commit (+ `site_lane_gate` for site/) | Yes — the commit is refused |

None of these four weakens as N grows from 3 to 8. A disjoint-scope, tree-locked, merge-or-reaped, gate-passing
fork is exactly as safe the 8th time as the 3rd. **The bound that matters is disjointness, not count.**

## 2. What actually bounds safe width (the real ceiling)
Three real limiters, in priority order:

1. **The single-map-writer serialization (the one genuine gap).** Until `H9_map_write_serialisation` is built, the
   ORCHESTRATOR is the SOLE writer of `maturity_map.yaml`; forks report levels back, they do not write the map.
   This is a real serialization point — but it bounds *map writes*, not *fork count*: 8 forks can build in parallel
   and report back to one serialized writer. So H9-absence does **not** block widening; it means the widen must
   keep the report-back discipline (forks never write the map). **Respected, not violated, by this proposal.**
2. **Machine resources.** The workflow/agent concurrency is already capped at `min(16, cores−2)`; Skynet's
   i5-13400F (10 cores) → ~8. Proposing `min(cores−2, 8)` aligns the fork bound with the resource reality — going
   past cores−2 thrashes, which is why 8 (not 16) is the proposed ceiling.
3. **The single reviewer's attention** (per BUDGET_UNCONSTRAINED: the real limiter is coordination + your
   attention, not tokens). Width multiplies *what you must correct-after*. This is why observability (gate-after
   item 6) is the precondition: 8 parallel decisions are only safe to run if the decision-ledger + results views
   make all 8 visible for your correction. **Widening and observability ship together or not at all.**

## 3. The failure mode to guard (honest)
The naive-organ's `T5_sustained_work_flat_goal` concern is the real risk of width: **width without value-diversity**
(12/20 commits into `site` while the north-star stayed flat). Widening the *count* must not become a licence to
fan out low-value near-duplicate work. Guard: the draw already ranks by PRIORITIES + exposure (atom F); a wide
draw must pull from **distinct** priority items, not N slices of one. Proposed acceptance test: a width-N draw
whose N atoms are not on N distinct PRIORITIES items (or N disjoint value-bearing scopes) is refused — width
serves coverage, never busywork.

## 4. Proposal (concrete)
- **Change:** `MAX_CONCURRENT_FORKS` DIAL from `3` → `min(cpu_cores − 2, 8)`, gated on **all four §1 properties
  holding** (already enforced) **and** the §3 distinct-value test.
- **Precondition (hard):** the observability views (gate-after item 6) are live first — width is only safe if you
  can see + correct all N in flight. This proposal is therefore **sequenced AFTER** the decision-ledger +
  results-of-actions site views land this campaign.
- **Reversibility:** it's one integer + a draw predicate; revert instantly if coordination cost bites.
- **Unchanged walls:** disjoint-scope, tree-lock, merge-or-reap, pre-commit gate, orchestrator-sole-map-writer
  (until H9), epoch ceilings.

**Status:** proposal only — batched for the daily [ACT]. I am NOT widening until (a) you sign off the ceiling and
(b) the observability views are live. Building at ≤3 in the meantime.
