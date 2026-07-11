# G — Data & Learning: lane charter

**Dial reached 2 2026-07-11** (SPIKE_WEEKEND DISCOVER/FRAME charter flood, item 4) — charter
seeded per the map's own equaliser rule, ahead of this lane's dial reaching the standard 3+
threshold, as part of a deliberate background-lane distillation pass.

## Mission

The project's own record of its growth must itself be trustworthy: metrics that describe
engineering progress (test counts, commit history) must never quietly plateau as the codebase
matures, and facts that cross the sim/company boundary must eventually flow through one shared,
disciplined channel rather than ad hoc per-caller data passing. This lane is the project
watching itself grow, honestly.

## Sub-capability tree

- **G1 (`G1_test_progression_metrics`)** — monotonic, non-saturating growth metrics: cumulative
  tests *executed* (not just collected), commit history, phase timeline — already real,
  already load-bearing in the phase-close checklist's own tooling.
- **G2 (`G2_event_log_shared_with_spine`)** — the generalised, shared version of
  `company/interfaces/bitemporal_event_log.py` (currently scoped to price/forward observables
  only), extended to be the one shared log any sim/company-crossing event flows through — named
  explicitly in `docs/design/charters/W1_market_weather.md`'s own sub-capability tree as riding
  the *same* reveal-over-time spine as W1 and `D2_three_clocks`.

## What L2/L3/L4 mean in this lane's terms

**G1 (already at target, level 2/2):** the real mechanism already exists and is genuinely
non-saturating — `tools/test_execution_metric.py` appends one record per real pytest
invocation (not just full-suite runs) to `docs/observability/test_execution_log.jsonl`, forward-
instrumented only (no fabricated historical backfill, per the Anchored-noise/no-fabrication
rule), and `tools/generate_phases_json.py::_monotonic_test_progression()` enforces a running-max
over the phase timeline so the project's own reported test-count history can never appear to
shrink. Further hardening (not a level change, since target is already met) would mean also
detecting *gaming* of the metric itself — e.g. a plateau in unique assertions even while
raw execution counts keep climbing — not attempted or scoped here.

- **L1 (no shared log):** sim and company each hold their own disconnected event views; any
  fact crossing the boundary is passed via a direct function call or ad hoc dict, per call site.
- **L2 (this phase's ceiling, if built):** a real, generalised event-log object exists —
  extending `BitemporalEventLog`'s dual valid_time/transaction_time design beyond price/forward
  data — proven correct in isolation, mirroring exactly how `PointInTimeView` reached L2 for W1
  before any call site migrated onto it.
- **L3:** at least one real cross-cutting event type (candidate: a customer interaction, or a
  settlement restatement) flows through this shared log and is genuinely consumed by both a
  sim-side and a company-side reader — not just written once and read by one side.
- **L4:** the shared log is the SOLE source of truth for any event crossing the sim/company
  boundary; ad hoc per-caller data passing for boundary-crossing facts is retired, not merely
  supplemented.

## Named best-practice references

- **DORA's own "Four Keys" metrics guide** (dora.dev, the official successor to the original
  DevOps Research and Assessment work by Forsgren/Humble/Kim) — https://dora.dev/guides/dora-metrics-four-keys/
  — the standard reference for engineering-velocity metrics that stay meaningful (deployment
  frequency, lead time, change failure rate, time-to-restore) rather than naive counters that
  plateau or can be gamed; G1's own "executed, not just collected" design follows the same
  instinct of measuring real activity over a static snapshot count.
- **Martin Fowler, "Event Sourcing"** — https://martinfowler.com/tags/event%20architectures.html
  — the canonical description (2005) of an event log as the rebuildable source of truth for
  application state; the vocabulary G2 borrows (a shared log multiple systems read from) traces
  directly to this pattern family.
- **Microsoft Azure Architecture Center, "Event Sourcing pattern"** —
  https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing — a concrete,
  independently-documented description of an event-sourced architecture where an event log is
  the central hub producers write to and consumers read from, eliminating custom point-to-point
  adaptors between systems — the exact shape G2 proposes for the sim/company boundary instead of
  today's per-caller data passing.

## Lane roadmap

1. **DONE, already at target:** G1's real, non-saturating execution-count metric
   (`tools/test_execution_metric.py`, `tools/generate_phases_json.py`) — no further build
   scoped this pass.
2. **Registered, NOT started this pass:** G2's generalisation of the bitemporal event log is
   Epoch-2 core, the same architectural spine as `W1_reveal_over_time`/`D2_three_clocks`/
   `B1_margin_bridge`/`E2_revenue_reconciliation` — sequencing is blocked pending the advisor's
   epoch-sequencing framing, per the director's own standing instruction. Do not start the
   actual generalisation build before that framing names its turn.
3. **Later (post-framing):** identify the first real cross-cutting event type to migrate onto
   the shared log (L3) — not yet chosen; a genuine open design question, not an oversight.

## Simplifications register

- G1's execution-count log is forward-only by design — no historical backfill exists before
  the instrumentation's own start date, and none should be fabricated (R12/no-fudge-factors
  discipline extended to this metric too).
- G2 does not exist as code yet. This charter is DISCOVER/FRAME-stage documentation only, per
  SPIKE_WEEKEND's own instruction ("output is documents") — no scaffolding, no placeholder
  class, nothing built prematurely ahead of the epoch-sequencing framing that governs when this
  lane's real build turn arrives.
