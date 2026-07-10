# D — Billing & Metering: lane charter

**Dial reached 4 (hot) 2026-07-10** (docs/design/MATURITY_MAP.md Section 8) — charter earned per
the map's own rule ("a lane earns its charter when its dial reaches 3+").

## Mission

A bill must reconcile against the same real settlement timetable a real supplier's finance
function lives with: physical (what was actually consumed), financial (what was actually paid
for it, hedged + spot), and regulatory (levies/charges, network costs) clocks, each ticking on
its own real-world cadence, not one flattened assumption. This lane's own `real_world_twin`:
"settlement timetable D+1/D+... true-up cycle" (`docs/design/maturity_map.yaml`).

## Shared architecture note — one spine, two faces

D2 (this atom, `D2_three_clocks`) is the **billing-side face** of the reveal-over-time spine.
`W1_reveal_over_time` (lane W1, its own charter: `docs/design/charters/W1_market_weather.md`) is
the **company-side/pricing-decision face** of the *same* architecture — per the director's own
placement correction closing `docs/review_gates/done/POINT_IN_TIME_SNAPSHOT_TIER1.md`: *"this is
Epoch-2 core... sibling to D2_three_clocks... one architecture not two."* This lane's build must
reuse W1's `BitemporalEventLog`/`PointInTimeView` foundation, not invent a parallel one.

## Sub-capability tree

- **D2 (this atom, `D2_three_clocks`)** — reconcile physical/financial/regulatory settlement per
  bill; depends on `W1_reveal_over_time` (the underlying spine this reconciliation rides).
- **D3_catchup_rebilling** — re-billing when a settlement run restates a figure after the
  original bill was already issued (depends on W1 — this is the bitemporal log's
  `superseded_by_run` concept made concrete on the billing side).
- **E2_revenue_reconciliation** — the company-side revenue-matching consumer of D2's output
  (depends on D2).
- **B1_margin_bridge** — margin-bridge reconciliation, also a downstream consumer of D2.
- **W3_2_settlement_timetable** — the industry-systems-lane twin of this same settlement-timing
  concern (depends on D2).

## What L2/L3/L4 mean in this lane's terms

- **L1 (not yet reached):** the two real pipelines that should agree — `saas/bill_generator.py`
  (bills non-commodity cost via ONE blended £/MWh rate, `saas/non_commodity.py`) and
  `simulation/hedged_settlement.py` (computes the same real-world cost per-levy, per-settlement-
  period: RO/CfD/CCL/CM/FiT + DUoS/TNUoS individually) — are independently built and never
  reconciled, per the real finding already landed (`docs/design/
  MARGIN_REALISM_E2_TWO_PIPELINES_FINDING.md`): the resulting gap is bidirectional/non-monotonic
  across years (+27.7% to -25.3%), consistent with a genuine volume/timing mismatch, not a simple
  missing-component bug.
- **L2 (this atom's current level_target):** the three clocks (physical/financial/regulatory) are
  named, separately observable quantities for at least one real bill, reconciled against each
  other with the gap EXPLAINED (not just measured) in terms of real settlement timing — riding
  the W1 `PointInTimeView`/`BitemporalEventLog` foundation for the "what did we know when"
  dimension of the reconciliation.
- **L3:** the reconciliation runs for the FULL 2016-2025 real run, not one illustrative bill, with
  the gap's time-series behaviour matched against real Elexon settlement-run cadence (Initial/
  II/IF/SF), not just internally self-consistent.
- **L4:** `D3_catchup_rebilling` — a real re-bill fires when a bitemporal restatement changes a
  previously-issued bill's true figure, the concrete, load-bearing use of the bitemporal log's
  `superseded_by_run` field (registered as a simplification, not yet built — see below).

## Named best-practice references

Shares W1's citations (look-ahead bias / bitemporal history / point-in-time join — see
`docs/design/charters/W1_market_weather.md`) since this is the same underlying pattern applied to
billing rather than pricing decisions. Additional, billing-specific:

- **UK Elexon settlement timetable** (Initial Settlement, II, IF, SF at T+5wd/T+14mo/T+14mo) —
  the real external cadence this lane's reconciliation must eventually match, not an invented
  schedule.

## Lane roadmap

1. **DONE this phase:** the shared spine foundation (`BitemporalEventLog`/`PointInTimeView`,
   `company/interfaces/`) this lane depends on is built and tested — see W1's charter for detail.
   This atom itself (`D2_three_clocks`) remains `loop_stage: idle` per the director's own
   sequencing instruction ("sequencing left to the advisor's epoch framing... no proactive build
   before the epoch sequencing names its turn") — this charter registers the lane's own thinking
   in advance of that turn being named, per the map's charter rule, not a claim that D2 itself
   has started building.
2. **Next (advisor epoch framing names the turn):** build the actual three-clock reconciliation
   for one real bill using the E2 two-pipelines finding as the concrete first target.
3. **Later:** full-run reconciliation (L3), then `D3_catchup_rebilling` (L4).

## Simplifications register

- No reconciliation code has been built yet for this atom — the charter itself, and the shared
  W1 spine it depends on, are this phase's real deliverable. Registering this explicitly (per
  R10: silent simplification is itself a defect) rather than implying progress that hasn't
  happened.
- `D3_catchup_rebilling`'s re-billing trigger is conceptually named here but has no design beyond
  "uses the bitemporal log's `superseded_by_run` field" — real design work, not yet done.
