# THREE LANES — spend width where width is free (P1, standing structure)

**Staged:** 2026-07-13 by advisor, director-decided. Disposition: **QUEUE** for
the lane work itself; the LANE STRUCTURE below takes effect immediately as
standing policy (it changes how you draw, not what you drop).

## The diagnosis (why parallelism keeps failing)
Every fix revealed the next bottleneck: empty draw -> capped at 1 -> livelock ->
BUILD-gated -> and now write-contention on maturity_map.yaml. But underneath all
of it is a truth we should stop fighting: **BUILD work in a single repo is
inherently narrow.** One working tree, one test suite, one integration gate. Even
with map contention fixed, two agents touching hedged_settlement.py and
bill_generator.py still share a tree and a green-suite gate. Real build
parallelism comes from worktrees/PRs, not from more agents in one directory.

**So stop trying to make BUILD wide. Spend the width where it is FREE.**

## The standing lane structure (apply from now)
**LANE 1 — BUILD (narrow, serial, careful).** Company/sim atoms. 1-3 concurrent
at most, and only where file_scopes genuinely do not intersect. Integration and
the full suite serialise at the end. This is physics, not failure. Fix the map
write-contention (already queued) to raise this from 1 to 2-3 safely.

**LANE 2 — SITE (parallel, free, high visible value).** `site/**` is DISJOINT BY
CONSTRUCTION from sim/** and company/** — zero contention with any build. Run it
alongside builds permanently. The work: doors 3-8 of the ratified SITE
CONSTITUTION, which were never built —
- The Company (board pack: trading/risk, three-clock finance, the household
  drill-down absorbed, compliance organs)
- The Proof (predictions ledger centrepiece, verification stack incl. NEEDS_WORK
  history, open defects, the incident->rule timeline)
- The World (two-sided wall page; sim depth re-homed; anchors register)
- The Method + Simplified (casebook shop-window; consolidated simplifications)
- Director door (twin approval log, decision log, dials, action queue)
- Cross-cutting: persona Expert-Hour tours, glossary layer, mobile pass
Number passports and evidence links throughout (already law). Pixel-verify each.
**This is what an expert actually sees. The front door is honest now; everything
behind it is still the old codebase-shaped tabs.**

**LANE 3 — DISCOVERY / THINKING (wide, 5-10 concurrent, zero risk).** Document
output only, no working-tree writes:
- **Epoch-3 discovery** (thinking is never gated — EPOCH_GATING): typed interface
  contracts, the go-live seam spec, adapter patterns, async/latency contracts
  (C-S3), what the wall must carry to become a real SLA boundary.
- Epoch-4/5 framing: fitness-function OPTIONS (never the choice — director's),
  mortality rules, the NFR register (PRODUCTION_READINESS Parts B/C still open).
- Red-teams on the invariants library; plausibility-anchor seeding; charter
  deepening; cold-eyes C-suite walks on the new site doors as they land.

## Rules
- Lanes run CONCURRENTLY. Lane 1 being narrow is never a reason for Lanes 2-3 to
  be idle — that is the mistake we have been making all weekend.
- Report per-lane activity in every digest: BUILD atoms in flight, SITE doors
  progressed, DISCOVERY forks dispatched.
- Lane 3 outputs are QUEUE items (register as atoms), never self-interrupts.
- The twin approves within lanes; only one-way doors reach the director.

## DoD
Lane structure recorded in CLAUDE.md; all three lanes demonstrably active in the
same digest window; site doors progressing while builds proceed; discovery forks
running 5+ wide. Metric: atoms-below-target AND level-transitions-banked AND
site doors closed.
