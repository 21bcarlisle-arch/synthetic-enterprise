# [PLANNER-MINTED] Make a waived in-progress mint's next SELF-DRAWABLE step visible to the rung-1–6 draw (2026-07-24)

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7; rungs 1–6 empty this tick). **Propose-then-proceed. FRAME-first (confirm the gap before any mechanism).**

## What ratified law this serves
- **R17 — THE TICK NEVER RESTS while authorized work exists at ANY priority** (2026-07-22 director P0). *"Rest is legitimate ONLY with PROOF the authorized set is empty at EVERY level … 'Consumed' ≠ 'absorbed'."*
- **`DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24.md`** waived five mints to **proceed to BUILD/FRAME immediately** — that is standing authorization for their next steps.

## The suspected gap (observed this tick, to be confirmed in FRAME)
- **6 `PLANNER_MINTED_*` docs sit in `docs/staging/in_progress/`** — a directory CLAUDE.md **excludes from the supervisor's unprocessed-staging scan** (same as `done/`/`fyi/`/`drafts/`).
- Several carry an **authorized, self-unblocked next step** that no wall gates. Read directly this tick:
  - `ssp_negative_lift_cells`: *"UNBLOCKS: self — no wall; next drawable step is the scope-2 BUILD"* (drift-aware recalibration + R10 class registration).
  - `moap_node_evidence_anchors`: *"BUILT + GATED + PUSHED — only live-pixel verify pending."*
  - `premise_demand_publish`: *"BUILD DONE + pushed … site-lane gate green"* — pending publish/live-pixel.
- **The tension:** these steps are authorized-and-drawable, yet they live only as `.md` docs in an unscanned directory, and their map atoms are parked at a pre-BUILD `loop_stage`. So rungs 1–6 draw nothing → **rung-7 fires and mints MORE** while authorized-and-drawable work is parked out of the draw's sight. That is the treadmill (consumed-not-absorbed) and a candidate R17 breach-of-class.

## Real-world / goal value
Closes a self-refill blind spot: the planner should not mint fresh work while a waived mint's own next step is drawable-but-invisible. Fixing it makes "rest only with proof the authorized set is empty at EVERY level" *actually* true, not just true of the scanned root.

## Scope (propose-then-proceed)
1. **FRAME (drawable now, doc-only) — CONFIRM OR REFUTE the gap first.** Read `background/supervisor.py` (`_self_refill_draw`, `_maturity_map_draw*`, `_open_campaign_draw`, `_is_drained_and_gated`) and establish: when a waived in-progress mint has a self-drawable next step, *is* there already a rung that surfaces it (e.g. via the map atom's `loop_stage`, or an open-campaign row)? If yes → this mint closes NO-BUILD with the evidence (honest close, not a re-draw). If no → proceed to 2.
2. **BUILD (reversible, only if the gap is confirmed):** the minimal mechanism that re-admits a waived in-progress mint's next self-drawable step to the rung-1–6 drawable set (e.g. a `next_step: drawable` marker the draw parses, mirroring how `_open_campaign_draw` reads `CAMPAIGN_REGISTER.yaml`). **R15 both-ways** test: fires (a marked next-step is drawn ahead of a rung-7 mint) and fails-closed (a parked/walled step is NOT drawn).

## Walls this mint does NOT cross
- Director-reserved next steps stay parked: `generator_draw_wiring` (R13 activation), `payment_truth_detection_gap` (Billing+CRM roadmap gate), any MC-2 curriculum-difficulty value — the mechanism must draw ONLY genuinely self-unblocked steps, never a walled one (that is the fail-closed half of the R15 test).
- No change to the one-way-door list, epoch ceilings, or level gates.

## Propose-then-proceed window
Standard planner window; FRAME is doc-only and fully reversible. Per SELF_INTERRUPT_DISCIPLINE this is queued as a mint (not fixed on sight). If FRAME refutes the gap, close it NO-BUILD with the supervisor-code evidence rather than building a redundant mechanism.


---

## DISPOSITION — FRAME confirmed → BUILT + ABSORBED (2026-07-24 worker tick)

**FRAME verdict: gap CONFIRMED and material.** The two existing `in_progress/` nets (`misparked_actionable_in_progress`, `misparked_open_campaign_in_progress`) surfaced **0 of the 6** open `PLANNER_MINTED_*` docs: the actionable-net needs a `[in-progress disposition` banner these mints don't use, and the campaign-net keys on the word "campaign" (a mint is not one). So a genuinely self-drawable next step (`ssp_negative_lift_cells` scope-2 BUILD *"UNBLOCKS: self — no wall"*; `value_chain_observation_window_cap` next BUILD step *"reversible under standing PRODUCT-FIRST authority"*) was invisible to EVERY draw rung → rungs 1–6 drew nothing → rung-7 fired and minted a fresh batch (the 3 docs committed `d39a0ac54` this very tick) while authorised, self-drawable work sat parked. Corroborated independently by the vcap doc's own repeated "Tick note"s (*"doorbell fired the stale 'rungs 1–6 empty → MINT' read AGAIN; disk contradicts it"*). This is the treadmill (consumed-not-absorbed) and the R17 breach-of-class the mint predicted.

**BUILD (absorbed, R15 both-ways):**
- `background/staging_disposition.py::selfdrawable_mint_in_progress` — a THIRD net on a **structured, machine-legible marker** (`<!-- SUPERVISOR_DRAW: self-drawable -->`), not fragile prose (R3). **Fail-closed:** surfaces a doc ONLY if it carries the self-drawable marker AND not the blocked marker; unmarked or blocked-marked docs stay parked. De-dups vs open-campaign-tracked docs.
- Wired into `background/supervisor.py::_real_staged_instructions` (the live draw path used by `find_work`) alongside the other two nets.
- `tests/background/test_staging_disposition.py` — R15 both-ways: fires on a self-drawable mint; fails-closed four ways (blocked-marked, both-markers→blocked-wins, unmarked, open-campaign-tracked). 5 pass; full supervisor draw suite 205 pass (no map-empty→rest regression).
- **Park-honesty retrofit** onto all 6 open mints: SELF-DRAWABLE on `ssp_negative_lift_cells` + `value_chain_observation_window_cap`; BLOCKED on the 4 genuinely-walled (`moap`/`premise` CDN-or-deploy wait, `generator` R13 director-reserved, `payment` roadmap-gated). Verified: the net now surfaces exactly the self-drawable set, and Mint 3 (`twin_axis_prescore`, FRAME-parked this tick) dogfoods it end-to-end.

Consumed → **absorbed** (mechanism LIVE + R15-proven both ways). Archived to `done/`.
