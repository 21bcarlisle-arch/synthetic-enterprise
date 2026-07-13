# THREE LANES — spend width where width is free

**Source:** `docs/staging/done/THREE_LANES_STANDING.md` (2026-07-13, advisor, director-decided).
**Status:** standing structure. The lane *structure* below is effective immediately (it changes
how the agent draws, not what it drops); the lane *work* items are QUEUE (registered as atoms,
drawn in dial-weighted order). CLAUDE.md carries a one-line pointer here.

## Diagnosis
BUILD work in a single repo is inherently narrow: one working tree, one test suite, one
integration gate. Even with map write-contention fixed, two agents touching sim/company files
still share a tree and a green-suite gate. Real BUILD parallelism comes from worktrees/PRs, not
more agents in one directory. So stop trying to make BUILD wide — spend width where it is FREE.

## The three lanes (run CONCURRENTLY; Lane 1 being narrow is never a reason for 2–3 to idle)

**LANE 1 — BUILD (narrow, serial, careful).** Company/sim atoms. 1–3 concurrent AT MOST, and only
where `file_scope`s genuinely do not intersect. Integration + full suite serialise at the end.
This is physics, not failure. Interim contention rule until `H9_map_write_serialisation` lands:
**the orchestrator is the sole `maturity_map.yaml` writer** — build forks touch only their code
`file_scope` and report their honest level back; the orchestrator records levels serially. Raises
safe concurrency from 1 toward 2–3 once H9 lands (per-atom evidence files merged into the map view).

**LANE 2 — SITE (parallel, free, high visible value).** `site/**` is DISJOINT BY CONSTRUCTION from
`sim/**` and `company/**` — zero contention with any build; run it alongside builds permanently.
The work = doors 3–8 of the ratified SITE CONSTITUTION (`docs/design/SITE_CONSTITUTION.md`), never
built: The Company (board pack), The Proof (predictions ledger + verification stack + open
defects + incident→rule timeline), The World (two-sided wall page), The Method + Simplified
(casebook), Director door (twin approval log, decision log, dials, action queue); cross-cutting
persona Expert-Hour tours, glossary, mobile pass. Number passports + evidence links throughout
(already law). **Pixel-verify each** (R11). Registered as atom `SITE1_expert_doors`.

**LANE 3 — DISCOVERY / THINKING (wide, 5–10 concurrent, zero risk).** Document output only, NO
working-tree writes. Never gated (EPOCH_GATING). Epoch-3 discovery (typed interface contracts,
go-live seam spec, adapter/async-latency contracts C-S3, what the wall must carry to be a real SLA
boundary); Epoch-4/5 framing (fitness-function OPTIONS only — director's choice; mortality rules;
NFR register — PRODUCTION_READINESS Parts B/C); red-teams on the invariants library; plausibility-
anchor seeding; charter deepening; cold-eyes C-suite walks on new site doors. Lane-3 outputs are
QUEUE items, never self-interrupts.

## Rules
- Lanes run concurrently. Lane 1 being narrow is never a reason for Lanes 2–3 to idle.
- Report per-lane activity in every digest: BUILD atoms in flight, SITE doors progressed,
  DISCOVERY forks dispatched.
- The twin approves within lanes; only one-way doors reach the director.

## DoD
Lane structure recorded in CLAUDE.md (pointer) + here; all three lanes demonstrably active in the
same digest window; site doors progressing while builds proceed; discovery forks producing docs.
