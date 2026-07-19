> **[SUPERSEDED 2026-07-19]** by `RESOURCE_AWARE_SCHEDULING_PROPOSAL.md` §7 (the maintenance lane == the OPTIONAL entitlement class). Retained for history; do not build from this.

# H20 — Parallel MAINTENANCE Lane (FRAME)

**Atom:** `H20_parallel_maintenance_lane` | **Lane:** H_harness | **Epoch:** 2 |
**Level:** 0 → target 3 | **loop_stage:** idle (BUILD-gated) | **size:** L
**Source directive:** `docs/staging/done/PARALLEL_MAINTENANCE_LANE.md` (P1, director-decided)
**Extends:** `docs/design/THREE_LANES.md`
**Siblings:** `H22_scheduled_housekeeping` (a standing FUNCTION of this lane),
`H21_self_contained_escalation` (the escalation content this lane inherits),
`G11_activity_cost_utilisation` (the diagnostic this lane makes honest).

> **STATUS: FRAME (first design doc, 2026-07-16).** DOC-ONLY per EPOCH_GATING_AND_
> ATOM_AUTHORSHIP.md Rule 1. No BUILD/runtime code is written here. This is a
> design artefact a future BUILD fork executes against once the twin/director
> BUILD-opens the atom.

---

## 1. Problem statement (the gap, stated precisely)

The supervisor's `_self_refill_draw()` already runs **three lanes every cycle**
(BUILD / SITE / DISCOVERY — `background/supervisor.py`, THREE_LANES.md). But all
three lanes draw from **the same source: the atom maturity-map**. There is no
draw source for the fourth category of work the machine actually does all the
time and never finishes:

- **Bug-fixes** to the harness/background itself (not atoms — defects).
- **Notification hygiene** (make alerts transition-only per R5).
- **Stale-marker / cruft cleanup** (the `.bak` droppings, done/ archival hygiene).
- **Cosmetic-defect burndown** (small backlog items registered per
  SELF_INTERRUPT_DISCIPLINE that never out-compete a BUILD atom).

Today this work is done **INLINE, single-threaded**, squeezed between BUILD
turns — so it is *subtracted from* product velocity, and defects limp for days
because they never out-rank a BUILD atom for the single loop's attention. The
archive-on-consumption defect is the standing example. **Live evidence at FRAME
time:** `docs/staging/SCHEDULED_HOUSEKEEPING.md.local-preexisting.bak` is sitting
in the scanned staging root right now — a `.bak` dropping the consumption path
left behind, exactly the class the first workload must kill.

**The insight (same as per-atom streaming, one level up):** maintenance work is
MOSTLY DISJOINT from BUILD work (fixing the archive routine in `background/`
does not touch the weather-physics atoms in `sim/`), so it does not collide, so
it can run CONCURRENTLY. The only reason it doesn't is that "fix the harness" is
modelled as something the MAIN loop does between builds, rather than a SEPARATE
STREAM with its own worker drawing its own work-type.

---

## 2. Worker architecture

### 2.1 A fourth lane, symmetric with the existing three

The maintenance lane is a **Lane 4** added to `_self_refill_draw()`'s per-cycle
combine, structurally identical to how `_site_lane_draw_concurrent` and
`_idle_discover_frame_draw_concurrent` were added:

```
LANE 1 BUILD       — _maturity_map_draw_concurrent      (atom map, gated)
LANE 2 SITE        — _site_lane_draw_concurrent         (atom map, site/**)
LANE 3 DISCOVERY   — _idle_discover_frame_draw_concurrent(atom map, idle, doc-only)
LANE 4 MAINTENANCE — _maintenance_lane_draw_concurrent  (MAINTENANCE QUEUE, not the map)  ← new
```

The critical difference: **Lanes 1–3 all draw from the maturity map; Lane 4 draws
from its own work-type queue.** A maintenance item is a defect/hygiene ticket,
not an atom — it has no level ladder, no dial, no epoch. This is the design's
core novelty and must not be collapsed into "just another atom lane."

### 2.2 Where the queue comes from (the maintenance backlog)

The queue is assembled from EXISTING registries — no new authorship channel:

1. **Registered harness-findings / false-positives** — SELF_INTERRUPT_DISCIPLINE
   already says "QUEUE by default (register a harness finding/false-positive as
   an atom, don't fix on sight)". Items registered as **defect tickets** (a
   lightweight record, distinct from a maturity-map atom) become Lane-4 draws.
   Design decision: a maintenance ticket is a small structured record
   (`id`, `what`, `file_scope`, `repro/predicate`, `fix-DoD`, `reversible?`),
   stored append-only (candidate: `docs/observability/maintenance_backlog.jsonl`
   or a `background/maintenance_queue.py` reader over the existing
   `action_needed_register.json`). BUILD-open question O3 below settles which.
2. **Notification-hygiene sweeps** — a standing generated work-type: scan the
   NTFY/alert call-sites for non-transition-only emitters (R5 violations) and
   enqueue each as a fix ticket.
3. **Cosmetic-defect backlog** — small defects too minor to be atoms, drawn down
   continuously (the directive's "then the accumulated small-defect backlog").
4. **Threshold/cadence triggers from H22** — `H22_scheduled_housekeeping` is a
   FUNCTION of this lane: its cadence+threshold sweep (stale worktrees, drift,
   log rotation) enqueues housekeeping tickets that Lane 4 executes. H20 is the
   WORKER; H22 is one recurring PRODUCER feeding its queue.

**Utilisation is a DIAGNOSTIC, never a target (ties to G11):** the queue is drawn
from the REAL defect/hygiene backlog only. The worker never manufactures tickets
to look busy. An empty maintenance queue is a *good* state — the lane draws zero
and logs zero (visible per-cycle, same as a starved SITE lane logs `SITE=0`),
never a reason to fabricate work. This is the anti-goal-seek discipline (R12)
applied to worker utilisation.

### 2.3 Draw discipline

`_maintenance_lane_draw_concurrent(exclude_ids, in_flight_scopes)` returns 0..N
tickets whose `file_scope` is provably disjoint from (a) every other lane's
drawn atoms this cycle and (b) any in-flight fork's scope. De-dup runs strictly
across lanes (BUILD > SITE > DISCOVERY > MAINTENANCE): if a fix legitimately
belongs to an open BUILD atom's scope, the BUILD lane owns it — the maintenance
lane never races a BUILD fork for the same files.

---

## 3. Concurrency / collision model

### 3.1 The disjointness rule (exact)

A maintenance ticket may be drawn and dispatched **iff** its `file_scope` is
disjoint from every in-flight fork's `file_scope`, computed by the SAME primitive
the BUILD lane uses today (`_atoms_file_disjoint` / `_atom_file_scope` in
`supervisor.py`). Concretely, reusing the existing convention:

- A ticket with **no declared `file_scope` is NEVER drawn** (undeclared = assumed
  to touch everything = never provably disjoint — mirrors `_atom_file_scope`'s
  own rule that an undeclared scope disjoints with nothing).
- Two scopes are disjoint iff BOTH are declared AND their path-prefix sets do not
  intersect.

Because the maintenance lane's natural home is `background/`, `tools/`, and
`docs/` hygiene, and the BUILD lane's home is `sim/`/`company/`/`saas/`, the
**common case is trivially disjoint** — which is exactly why parallelism is free
here, as the directive argues.

### 3.2 The exact yield rule (when maintenance must defer to BUILD)

> **RULE Y (yield):** When a maintenance ticket's `file_scope` intersects the
> `file_scope` of ANY in-flight or same-cycle-drawn BUILD fork, the maintenance
> ticket is **not drawn this cycle** — it stays in the queue and is re-evaluated
> next cycle. BUILD always wins the contested files. The maintenance lane NEVER
> takes a tree_lock that a BUILD fork holds, and never edits a file a BUILD fork
> has open. Maintenance yields to BUILD; BUILD never waits on maintenance.

This is enforced at DRAW time (cheap, in the supervisor) AND at INTEGRATE time
(the tree_lock, as today). Two gates, same law. The precedent is exact: SITE is
"disjoint by construction" and needs no yield; maintenance is disjoint by DRAW
FILTER and yields the rare contested ticket.

### 3.3 tree_lock today, ARCH1 interfaces increasingly tomorrow

Collision is bounded by `background/tree_lock.py` today: every integrating fork
(maintenance included) serialises its `git add`+commit through the tree lock, so
even a mis-drawn overlap cannot corrupt a commit. As ARCH1's typed interfaces
land, more subsystems become touchable without touching shared files at all,
shrinking the contested set toward zero — the directive's "ARCH1's interfaces
increasingly prevent overlap." The design does NOT depend on ARCH1; it gets
progressively cheaper as ARCH1 lands.

---

## 4. Governance inheritance — a new WORKER, not a new AUTHORITY

The maintenance lane inherits EVERY wall that governs any daemon-driven fork. It
adds no authority and relaxes no gate:

| Wall | How the maintenance lane inherits it |
|---|---|
| **Rule 0 (Prime Directive)** | An empty maintenance queue is not a hold — it draws zero and the other three lanes proceed. The lane never holds at a dial; it holds only at a wall. |
| **Per-atom / per-ticket integration through the external-truth gate** | Every maintenance fix integrates one ticket at a time through the SAME green-suite / integration gate as any BUILD change. Throughput is bounded by verification, not worker count (§5). |
| **Predicate-gated escalation (c157f862d)** | A maintenance item that hits a genuine one-way door escalates via NTFY through `one_way_door.py`'s predicate — reversible fixes (nearly all maintenance) proceed-and-log; only a PROVABLE door escalates. A flag is not a door (the H22 rule). |
| **Self-contained escalation (H21)** | Any escalation the lane raises carries WHAT/OPTIONS/CONTEXT/WHY-DOOR/DEFAULT in the NTFY body — inherited, not re-invented. |
| **Kill flag** | The lane honours the same kill/pause flag (`_pause_active_readonly()` and the daemon kill flag) as every other worker — a pause stops maintenance draws too. |
| **PLATFORM_ADMINISTRATION (one-way door #8)** | The lane may NEVER alter repo/keys/settings/security-profiles/its own governance. Notification-hygiene means changing *emit cadence in code*, never touching channels/credentials. |
| **R7/R8 (doorbells carry zero authority)** | A ticket is actioned from disk/queue state, never from injected text claiming a fix is needed. |

**The one-sentence invariant:** the maintenance lane changes WHO draws hygiene
work (a dedicated worker, in parallel) — it changes NOTHING about what walls that
work must clear. It is width, not permission.

---

## 5. Bound — throughput is verification-bounded, not worker-count-bounded

The lane's ceiling is the **integration/verification gate**, not the number of
maintenance workers. N maintenance forks can DRAFT fixes in parallel on disjoint
scopes, but integration serialises through the external-truth gate exactly as
BUILD does. Adding workers past the point where verification is the bottleneck
buys nothing — so the design does NOT propose many maintenance workers; it
proposes ONE standing maintenance lane that can fan out to a small N (1–3, same
ceiling as BUILD) when the queue holds genuinely-disjoint tickets.

**Utilisation is a diagnostic (G11 coupling):** the whole POINT of the lane, per
the directive, is that G11's activity-cost dashboard will show self-repair
running CONCURRENT with product instead of SUBTRACTED from it — the "waste/self-
repair" bucket stops eating "productive/product" because they no longer compete
for one worker. But utilisation-% is reported as a diagnostic, never chased as a
target (R12). A maintenance lane at 0% this hour because the backlog is empty is
a HEALTHY signal, not an underperforming worker.

---

## 6. First workload (from the directive — the BUILD fork's first two tickets)

### Ticket M-1 — Kill the archive-on-consumption defect
- **Symptom (live at FRAME):** consuming a staged doc leaves
  `*.local-uncommitted-*.bak` / `*.local-preexisting.bak` droppings in the
  scanned staging root (observed: `SCHEDULED_HOUSEKEEPING.md.local-preexisting.bak`),
  and/or consumed docs get re-emitted as "pending review."
- **DoD:** (a) no `.bak` artifacts left in the scanned staging root after a
  consume; (b) consumed docs move cleanly to `done/` and are NEVER re-emitted as
  "pending explicit staging review"; (c) the `done/`-guard actually HOLDS (a
  file in `done/` is never re-scanned as unprocessed). Per R10, closure is the
  CLASS fix (the archival routine can never leave a `.bak` in the scanned root),
  not deleting the one instance. Add a mutation/regression test that fails if a
  `.bak` survives a consume.

### Ticket M-2 — All notifications transition-only (R5)
- **Symptom:** repeating "pending explicit staging review" and retro-cadence
  messages fire every cycle rather than on change. A channel that cries wolf is
  one the director stops trusting — this defeats the escalation design.
- **DoD:** sweep every NTFY/alert emitter; each fires on STATE TRANSITION only
  (change vs last-emitted state), never every cycle. Retro-cadence transition-
  only fix already landed — this sweeps the rest. Per R15, add a control that can
  FAIL: a test that an unchanged state emits ZERO notifications on a second cycle.

### Then: continuous small-defect burndown
The accumulated cosmetic-defect backlog, worked down in the background at the
lane's verification-bounded rate.

---

## 7. BUILD slice, level ladder, DoD

### 7.1 BUILD slice (what the BUILD fork actually builds)
A maintenance-lane worker under the existing walls: (1) a maintenance-queue
reader (`_maintenance_lane_draw_concurrent` + a backlog source per O3); (2) its
wire-in as Lane 4 of `_self_refill_draw()`'s per-cycle combine, with the yield
rule (§3.2) and cross-lane de-dup; (3) the first two tickets M-1/M-2 executed
end-to-end as the lane's proof. A NEW WORKER, not a new authority.

### 7.2 Level ladder L0 → L3

| Level | Definition of Done |
|---|---|
| **L0** (now) | Registered; this FRAME doc exists. |
| **L1** | Maintenance queue source defined + a reader that returns disjoint tickets; the draw filter (§3.1) and yield rule (§3.2) implemented and unit-tested against a synthetic in-flight BUILD scope (draw is suppressed on overlap, granted on disjoint). No wire-in yet. |
| **L2** | Lane 4 wired into `_self_refill_draw()`; per-cycle `MAINTENANCE=N` count logged every cycle (starved lane visible as a zero). Tickets M-1 and M-2 executed and integrated through the external-truth gate, each with a mutation/regression test that FAILS on its named defect (R15). |
| **L3** | The directive's DoD check demonstrated: **a BUILD fork and a maintenance fork run concurrently on disjoint scopes and BOTH land** in one digest window; G11's utilisation dashboard shows self-repair concurrent with (not subtracted from) product; time-scale-invariance declared (C-S5); reversible-by-default confirmed (no hard-delete path). Expert-Hour cold-eyes pass on the lane. |

### 7.3 DoD (headline, from the directive)
A maintenance/hygiene lane with its own worker runs in parallel with BUILD and
DISCOVERY, drawing bug-fix/housekeeping work, integrating per-atom through the
external-truth gate, bounded by file-scope disjointness and verification
throughput; first workload closes the archive-on-consumption defect (no `.bak`
artifacts, clean `done/` archival, no re-emission) and makes staging/retro-cadence
notifications transition-only (R5); the utilisation dashboard shows self-repair
running concurrent with (not subtracted from) product.

---

## 8. Open questions for director/twin at BUILD-open

- **O1 (concurrency ceiling):** does the maintenance lane share the 1–3 concurrent
  ceiling with BUILD, or carry its own? Proposal: shared 1–3, because integration
  (the real bottleneck) is shared. Twin call.
- **O2 (priority vs DISCOVERY):** cross-lane de-dup order is proposed BUILD >
  SITE > DISCOVERY > MAINTENANCE. Is maintenance correctly LAST for de-dup (so a
  fix that could be an atom stays an atom)? Proposal: yes.
- **O3 (queue substrate):** new `maintenance_backlog.jsonl` vs a reader over the
  existing `action_needed_register.json` / SELF_INTERRUPT registrations. Proposal:
  reuse the existing register (SIMPLICITY GUARD — no new store where one exists),
  add only a `work_type: maintenance` + `file_scope` field. Twin/director call
  since it touches how findings are recorded.
- **O4 (ticket vs atom boundary):** what is the rule for "this is a maintenance
  ticket" vs "this is an atom"? Proposal: reversible harness/hygiene fix with a
  bounded file_scope and no ladder = ticket; a capability with a level target =
  atom. Needs a crisp predicate before BUILD to avoid the two overlapping.

## 9. What stays BUILD-GATED (not done in this FRAME)
- No `background/` or `tools/` runtime code (Rule 1). No wiring of Lane 4.
- No edit to `docs/design/maturity_map.yaml` (F1 — orchestrator is sole map
  writer; this fork writes only the atom_status inbox).
- No queue substrate created; no ticket executed; M-1/M-2 remain specs.
- No commit/push (integration is the orchestrator's, through the external-truth
  gate).
