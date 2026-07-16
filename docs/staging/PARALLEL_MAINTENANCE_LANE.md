# A STANDING MAINTENANCE LANE — run self-repair in PARALLEL with product, not stolen from it (P1, director-decided)

**Staged:** 2026-07-16 by advisor, **director-decided**. Disposition: QUEUE-high
(structural velocity change). Director's question: "why can't it do bug-fixes /
housekeeping in parallel too?" Answer: no good reason — it's a gap in how the draw
is structured, not a machine limit.

## The gap
The daemon runs one main loop; within a turn it forks up to 2 concurrent BUILD
atoms. But bug-fixes, housekeeping, and notification-hygiene are NOT in the draw
as a parallel work-type — they get done INLINE between build turns, single-
threaded, only when the machine happens to notice or the director flags them. So
cruft survives for DAYS (the archive-on-consumption defect is the standing
example) because it never out-competes a build atom for the single loop's
attention. Self-repair is currently SUBTRACTED from product velocity — serial.

## The fix: lanes by WORK-TYPE, running in parallel
Add a standing **MAINTENANCE / HYGIENE lane** alongside the existing lanes, each
with its own worker drawing its own work-type:
- **BUILD** — finishing atoms to target (product/output)
- **DISCOVERY** — FRAME/DISCOVER (investment)
- **MAINTENANCE** — bug-fixes, notification hygiene, stale-marker cleanup, the
  archive-on-consumption defect, retro-cadence noise, `.bak`-artifact cleanup,
  and the standing pile of small class-defects (self-repair)
- **SITE** — visible surfaces (now cold-eyes-gated per DELEGATE)

The maintenance lane chews through accumulated cruft CONTINUOUSLY in the
background WHILE the build lane does product — instead of self-repair competing
with product for one loop.

## Why this is more than convenience (it's the utilisation answer)
When the machine spends a turn on self-repair today, that turn is STOLEN from
product — serial. With a parallel maintenance lane, self-repair and product run
SIMULTANEOUSLY: the self-repair cost stops being subtracted from product velocity.
The ACTIVITY_COST_AND_UTILISATION dashboard will show this directly — the
waste/self-repair bucket no longer eats the productive/product bucket, because
they are not competing for the same worker. This is the structural complement to
that dashboard: don't just MEASURE the self-repair cost, stop it stealing product
time.

## First workload for the maintenance lane (the standing pile)
1. **Archive-on-consumption defect (top priority)** — CLOSE it for good: consumed
   staged docs move cleanly to done/ with NO `.bak`/`.local-uncommitted-*`
   artifacts and NO re-emitting "new staged instruction — pending review" for
   already-processed docs. (This has been half-fixed repeatedly for a week; the
   maintenance lane owns it end-to-end.)
2. **Notification noise** — make repeating/periodic notifications TRANSITION-ONLY
   (fire on change, not every cycle); the retro-cadence message is the example.
   A channel that cries wolf erodes trust in the escalation design.
3. Then the standing backlog of small class-defects as they arise.

## GUARDRAILS (same laws — do not over-rotate)
- **Bounded by verification and independence** (per PER_ATOM_INTEGRATION): the
  maintenance lane's changes go through the SAME external-truth gate; genuinely-
  coupled changes still coordinate with build work; parallelism is bounded by
  verification throughput and file-scope-disjointness, never by lane count.
  Most hygiene (archive routine, notification formatting, marker cleanup) is
  cleanly DISJOINT from product atoms, so it parallelises safely — but respect
  the real couplings.
- **Maintenance is a lane, not a priority inversion**: it runs IN PARALLEL, it
  does not preempt product. The point is concurrency, not making self-repair
  more important than building.
- File-scope disjointness + tree-lock discipline as with the existing forks.

## Relationship to the map
Completes the "always lots of work concurrently" picture: BUILD + DISCOVERY +
MAINTENANCE + SITE as parallel work-type lanes, per-atom streamed, each gated.
Folds with per-atom integration (no batch boundary), F1 (safe concurrent map-
writes), and the utilisation dashboard (measures the parallelism dividend).

## DoD
A maintenance/hygiene lane runs concurrently with build and discovery, its own
worker drawing bug-fix/housekeeping work-type; the archive-on-consumption defect
CLOSED end-to-end (no artifacts, no duplicate "pending review" notifications) as
its first delivered fix; periodic notifications made transition-only; changes
integrate per-atom through the external-truth gate with file-scope-disjointness
respected; the utilisation dashboard shows self-repair running parallel to (not
subtracted from) product. A check: a hygiene fix and a product build land in the
same window without either waiting on the other.
