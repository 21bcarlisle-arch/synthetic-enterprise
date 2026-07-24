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
