<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- draw-visibility marker (2026-07-25, RUNG-7 planner tick): this doc carves the ONE self-drawable slice
     (SOURCE 2 — harness grid COVERAGE, "drawable now, NOT roadmap-gated" per its parent) out of
     PLANNER_MINTED_payment_truth_detection_gap_2026-07-24, which was coarse-marked non-drawable for the
     whole doc because its HEADLINE next step (SOURCE 1 detection capability) is roadmap-gated on
     Billing+CRM. That coarse marker hid a genuinely non-walled harness half from the draw — the
     consumed-not-absorbed / buried-drawable-work class. This atom makes that slice visible as RUNG-1
     work. Fail-closed structured token parsed by background/staging_disposition.selfdrawable_mint_in_progress. -->

# [PLANNER-MINTED] Light the dark payment-gap grid cells (W2_11 SOURCE 2 — harness coverage) (2026-07-25)

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7). **Self-drawable / propose-then-proceed.** Carves SOURCE 2 out of the parent mint (`PLANNER_MINTED_payment_truth_detection_gap_2026-07-24`, DISCOVER/FRAME diagnosis §"Consequence for the BUILD", step 2). Attaches to atom `W2_11_payment_behaviour_source` + the G1/G2/G3 fidelity-grid machinery.

## Why this is a distinct, NON-walled atom (and the parent's other half is not)
The parent mint diagnosed the `live_payment_detection_gap` ledger row as **two sources under one number**:
- **SOURCE 1 — the detection CAPABILITY** (non-DD push channels emit no bank-feed failure event, so the company is structurally blind to ~63% of live failures). Closing it needs a *company* build (expected-collection reconciliation) that is **roadmap-gated on Billing+CRM rotating in** (DIRECTOR_AXES roadmap, director-owned). **Stays walled — not this atom.**
- **SOURCE 2 — the measurement COVERAGE** (this atom). The parent labels it verbatim *"harness coverage, drawable now, NOT roadmap-gated ... closed by measuring more of the 5×3 grid, NOT by any detector change."* It was invisible only because the parent doc carried one coarse non-drawable flag for both halves.

## Fidelity-ledger row served
`docs/observability/fidelity_evidence_ledger.json` → `live_payment_detection_gap` — the **grid-attribution** half. Grounded in code (`background/live_fidelity_evidence.py`): `LIVE_CELL_ID = "A1_G2"`, `_REGIME_MIXED_SIMP_ID = "live_payment_gap_regime_mixed_attributed_to_G2"`; a regime-MIXED 2016–2025 live run is attributed to the **single** `A1_G2` cell while **the other 14 of 15 grid cells stay UNMEASURED**, floored by G1's fail-open rule ("one corner lit, the rest honestly dark — the grid can never report `clean` while any cell is untested").

## Ratified goal served
- **COUPLED_TRIAD doctrine** (CLAUDE.md): *the gap is reported per coupled pair each digest.* A per-cell (segment × regime) gap map is the doctrine's own scoring substrate — currently 1/15 cells carries a real measurement.
- **DIRECTOR_AXES Axis 3 (Believability):** an honest per-segment/per-regime coverage map of where the company is blind is more faithful than a single mixed number floored across 14 dark cells.

## Real-world fidelity gained
Turns "one corner lit, 14 dark, fail-open floored" into an **honest per-cell coverage map**: which affordability segment (A0/A1/A2) × which price regime (G1 calm / G2 crisis-spike / G3 …) the belief-vs-truth payment gap has actually been measured in, and where it remains unmeasured. This is **load-bearing for any future G1 `clean` report** (the grid cannot go clean while cells are dark) and makes the coupled-triad's per-cell gap real rather than a single collapsed cell.

## Honesty guard (what this atom is NOT)
This improves **measurement COVERAGE, not the detection CAPABILITY**. The company's structural blindness to non-DD channels (SOURCE 1) is unchanged and stays roadmap-gated — lighting more cells will (correctly, per R12/R13) show the SAME structural blind spot recurring across segments/regimes, not a smaller gap. A cell that suddenly reads a near-zero gap would be a **leak, not a win** (the parent's `n_flagged_non_dd == 0` witness must hold). The value is coverage-honesty, not a capability claim.

## Scope (propose — bounded harness work, reversible)
1. **FRAME the attribution seam:** read where the single-cell collapse happens (`background/live_fidelity_evidence.py` `emit_*`/`cell_id=LIVE_CELL_ID`, `regime_label`) and the harness (`tools/couple_w2_11_d5.py` `build_scenario`/`measure`/`score_triad`). Name which cells a live 2016–2025 run can *honestly* light by partitioning its own periods by observed price regime and its own book by affordability segment — using only WORLD-side truth on the harness/director side of the wall (never leaked into the company belief).
2. **Light the honestly-measurable cells:** attribute the crisis periods (2021–22) to their G2/G3 cells and the calm periods to G1 cells, per affordability segment, rather than collapsing all to `A1_G2`. Each newly-lit cell carries its own measured `true/believed/gap`.
3. **Register the irreducible residual as a named R10 simplification** for any cell that genuinely cannot be isolated from a single mixed run (the collapse that survives), with its measured bound — replacing/refining `_REGIME_MIXED_SIMP_ID` so it names *exactly which* cells remain mixed rather than blanket-attributing all to G2.
4. **R15 both ways:** a test that a newly-lit cell reports its own distinct measured gap (fires on the coverage fix); a mutation proving an unmeasured cell still shows as dark/floored, never silently `clean` (must not fail-open). Update the ledger; the coupled-triad per-cell map widens visibly.

## Walls untouched
Generator ground truth (the true failures are sim truth — the company still discovers, never reads them; regime/segment partition is WORLD/harness-side only). No curriculum change (no scenario difficulty knob). No L3 self-promote. No SOURCE-1 detection build (roadmap-gated). Reversible harness/measurement work under standing PRODUCT-FIRST authority.

## Propose-then-proceed window
Proceeds immediately as a bounded harness slice under reversible-build authority. If a cell's honest disposition is "register a residual simplification," that lands without a wall. SOURCE 1 remains the parent mint's roadmap-gated half.

---
## RESOLUTION (2026-07-25, SOURCE 2 BUILT + LIVE-WIRED)
**Status: DONE — the drawable SOURCE 2 slice is built, tested, and wired into the live run.** Archived to `done/`.

**What shipped:**
- `tools/couple_w2_11_d5.py`: `score_detection_by_partition` (per-partition DETECTION scoring via the SAME `detection_gap` scorer — no bespoke metric, R15 independence), `detection_cell_measurements` (per-cell `CellMeasurement` map ready for emission), and `uk_price_regime` (world-side date→G1/G2 classifier grounded in the REAL 2021-09..2023-03 UK gas-crisis window per Ofgem's cap trajectory — historical fact, not an R13 curriculum knob; G3 acute-tail NOT asserted from a calendar).
- `background/live_fidelity_evidence.py`: `emit_live_fidelity_cells` lights each honestly-measured `A1_Gx` cell (one ledger row per cell, keyed by `cell_rel_id` so cells never overwrite), each carrying `_DETECTION_REGIME_PARTITIONED_SIMP_ID` — the honest residual that **DETECTION is regime-resolved while BELIEF/AGEING stay regime-mixed** (they read the account-level running belief, which double-counts a customer spanning regimes; named, never silently split). Single-cell `emit_live_fidelity_evidence` kept as the conservative single-regime fallback.
- `simulation/run_phase2b.py`: the live emit now partitions by observed regime — a run spanning calm+crisis lights ≥2 cells; a single-regime run collapses to one (unchanged behaviour). Non-fatal wrapper preserved.

**R15 both ways (33 tests, all green):** per-cell lighting reports distinct measured gaps + widening never makes the grid cleaner (extra cell only raises the worst-cell floor) + empty map raises (fail-closed) + each per-cell chain holds no belief leak + partition conserves the whole run's failures with no double-count + the classifier reads only harness truth. The grid can still never report `clean` while any of the 15 cells is dark.

**Honesty guard held (mint §"what this atom is NOT"):** this widens measurement COVERAGE, not detection CAPABILITY. Lighting more cells shows the SAME structural non-DD blind spot recurring per regime (a near-zero cell would be a leak, not a win). SOURCE 1 (the detection capability) remains the parent mint's roadmap-gated half — untouched.
