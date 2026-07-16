# A STANDING MAINTENANCE LANE — self-repair runs PARALLEL to product, not stolen from it (P1, director-decided)

**Staged:** 2026-07-16 by advisor, **director-decided**. Disposition: QUEUE-high
(structural velocity multiplier). Director: "Why can't it do stuff like that
[bug-fixes/hygiene] in parallel too?" No good reason — it's a gap in how the draw
is structured, not a machine limit.

## The gap
The daemon runs one main loop; within a turn it forks ~2 concurrent BUILD atoms.
But bug-fixes, housekeeping, and notification-hygiene are NOT in the draw as
parallel work — they get done INLINE when the machine happens to notice them, or
when the director flags them, single-threaded, squeezed between build turns. So
defects limp along for days (the archive-on-consumption bug is the standing
example) because they never out-compete a build atom for the single loop's
attention.

## The insight (same as per-atom streaming, one level up)
Maintenance/hygiene/bug-fix work is MOSTLY DISJOINT from build work (fixing the
archive routine doesn't touch the weather-physics atoms), so it does not collide,
so it can run CONCURRENTLY. The only reason it doesn't is that "fix the harness"
is treated as something the MAIN loop does between builds, rather than a SEPARATE
STREAM with its own worker.

## The model: LANES BY WORK-TYPE, running in parallel
- **BUILD lane** — finishing atoms to target (product / value output)
- **DISCOVERY lane** — FRAME/DISCOVER (investment)
- **MAINTENANCE lane** — bug-fixes, notification hygiene, stale-marker cleanup,
  cosmetic-defect burndown, retro-cadence noise (self-repair) — its OWN worker,
  drawing its OWN work-type, running alongside the others
- **SITE lane** — visible surfaces

Each with its own worker, drawing its own work-type, integrating PER-ATOM through
the same external-truth gate, colliding only where file_scopes genuinely overlap
(which ARCH1's interfaces increasingly prevent).

## Why this is more than convenience (the utilisation connection)
Right now, when the machine spends a turn on self-repair, that turn is STOLEN from
product — serial. With a maintenance lane, self-repair and product happen
SIMULTANEOUSLY — the self-repair cost stops being subtracted from product
velocity. The ACTIVITY_COST_AND_UTILISATION dashboard will show it directly: the
"waste/self-repair" bucket no longer eats "productive/product," because they no
longer compete for the same worker. This is the structural answer to "is
self-repair too expensive" — parallelise it so it isn't paid for in product time.

## First workload for the maintenance lane (the standing cruft)
- **Archive-on-consumption defect** — kill it properly: no `.local-uncommitted-*.bak`
  artifacts; consumed docs move cleanly to done/ and are NEVER re-emitted as
  "pending review"; the done/-guard actually holds.
- **Notification noise** — the repeating "pending explicit staging review" and
  retro-cadence messages: make ALL such notifications TRANSITION-ONLY (fire on
  change, never every cycle) per the existing transition-only alerting rule (R5).
  A channel that cries wolf is one the director stops trusting — this defeats the
  escalation design.
- Then the accumulated small-defect backlog, worked down continuously in the
  background.

## Guardrails (unchanged laws)
- **Bounded by verification, not worker count** — maintenance changes go through
  the same external-truth gate; genuinely-coupled changes still coordinate; a
  maintenance fix touching shared code lands coherently with build work.
- **File-scope disjointness** — the maintenance worker draws work whose
  file_scopes don't collide with in-flight build forks (tree-lock as today).
- **Same daemon governance** — one-way doors escalate (via self-contained NTFY),
  Rule 0, per-atom integration, kill flag. The maintenance lane is a new WORKER
  under the existing walls, not a new authority.
- Utilisation is a diagnostic not a target (don't spawn maintenance work to look
  busy; draw it from the real defect/hygiene backlog).

## DoD
A maintenance/hygiene lane with its own worker runs in parallel with build and
discovery, drawing bug-fix/housekeeping work, integrating per-atom through the
external-truth gate, bounded by file-scope disjointness and verification
throughput; first workload closes the archive-on-consumption defect (no .bak
artifacts, clean done/ archival, no re-emission) and makes staging/retro-cadence
notifications transition-only (R5); the utilisation dashboard shows self-repair
running concurrent with (not subtracted from) product. A check: a build fork and
a maintenance fork run concurrently on disjoint scopes and both land.
