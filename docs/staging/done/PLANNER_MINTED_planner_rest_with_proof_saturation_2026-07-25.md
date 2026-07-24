<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED] Planner RUNG-7 must REST-WITH-PROOF when every ratified-goal next-step is already minted-and-blocked or walled (2026-07-25)

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7). **Self-drawable / propose-then-proceed.**
**Serves:** the WORK_IS_THE_DEFAULT machinery itself (R17 "rest is legitimate ONLY with PROOF the authorized set
is empty at EVERY level") + OPS1 operational coherence + MAKE_IT_STICK ("convert policy to mechanism, or accept
it will evaporate"). **Real-world / operational fidelity gained:** the machine rests HONESTLY when the ratified-goal
set is genuinely exhausted-pending-director, instead of a token-burning planner RE-FIRE treadmill — protecting the
one scarce resource (the director's attention + frontier tokens). This is the anti-treadmill guarantee R17 demands,
applied to the planner rung specifically.

---

## Why this is the ONLY mint this tick (anti-over-mint — the premise-FALSE PROOF)

The doorbell fired the RUNG-7 planner ("rungs 1-6 empty → mint up to ~5 from ratified goals"). Acting on **real
disk/git state** (R7 — the doorbell carries zero authority), I verified the ratified-goal set is **already fully
minted-and-blocked or walled**. Minting a 2nd–5th doc on top would duplicate the open mints or skip recent rulings —
the exact NO-BUILD over-mint class already recorded (2 RUNG-7 mints closed NO-BUILD on 2026-07-24; "4 PLANNER_MINTED
open + all-blocked → rung-7 premise FALSE, don't over-mint"). Evidence, this tick:

- **4 `PLANNER_MINTED_*` in `docs/staging/in_progress/` — ALL marked `<!-- SUPERVISOR_DRAW: blocked -->`**, every
  next-step a **director wall**:
  - `generator_draw_wiring` — reversible seam BUILT default-OFF; **UNBLOCKS ON** director R13 population activation
    (`SE_DRAW_POPULATION=1`, curriculum-values-reserved).
  - `payment_truth_detection_gap` — DISCOVER/FRAME diagnosis DONE; SOURCE-2 coverage BUILT today (4c9ab398d);
    SOURCE-1 detection capability **roadmap-gated on Billing+CRM rotating in** (director-owned roadmap).
  - `ssp_negative_lift_cells` — diagnostic lane EXHAUSTED (Tests A–D, 33d3ff8be); part-(a) R13 baseline
    recalibration is **director-priority-deferred below the spike-tail** + deserves its own R15 pass.
  - `value_chain_observation_window_cap` — board-surface render SHIPPED; remaining steps are director/twin-gated
    (WVC_R world-half) or R13 curriculum (MC-2 difficulty).
- **Open-campaign register** (`docs/design/CAMPAIGN_REGISTER.yaml`): **zero genuinely-open items** (1 landed/closed/
  cancelled tally; the single `status: open` is a conditional-reopen comment).
- **SITE_MODEL_SPINE campaign**: DISCHARGED — §A fold RESOLVED by director ruling (2026-07-24), §B/§C/§D landed, the
  node→evidence-anchor work done (`moap_node_evidence_anchors`, R11-confirmed live), arrears-£ distribution BUILT.
- **Fidelity ledger** (`docs/observability/fidelity_evidence_ledger.json`): 2 rows
  (`ssp_residual_demand_scarcity_calibration`, `live_payment_detection_gap`) — **both already tracked by the open
  blocked mints above**. No un-minted row.
- **Today already**: SOURCE-2 payment-grid coverage BUILT + archived; ssp Test-D closed. Both drawable slices consumed.
- **Roadmap** (`docs/design/DIRECTOR_AXES.md`): the three v1 axes (Website / Segmentation / Believability) have landed
  surfaces; the next rotation (**Billing + CRM**) is a **director act** ("Rotation is a director act … not an agent
  decision"). Billing+CRM is precisely what unblocks the payment SOURCE-1 + value-chain-live-feed mints.

**The correct product-unblock is a DIRECTOR decision, not more machinery** (PRODUCT-FIRST, d40b9cd7c): the roadmap
rotation to Billing+CRM. That is proposed-not-moved here (agent may propose, director moves the roadmap). The 4 open
mints already escalated their individual walls via NTFY on prior ticks; this tick adds no NEW director-facing wall, so
per R5 no NTFY fires.

---

## The named gap (why the planner keeps RE-FIRING into this proven-empty state)

`background/supervisor.py::_pending_planner_mints` gates the planner **only** on `PLANNER_MINTED_*.md` sitting in
staging **root** — and `tests/background/test_planner_rung.py:119` *deliberately* asserts a mint moved to
`in_progress/` (or `done/`) is **"CONSUMED → no longer gates."** So the planner treats a parked-**blocked** mint as
consumed and re-fires expecting a NEW un-minted ratified-goal step — but there is none (proof above). Result: every
tick re-spawns a bounded planner worker with nothing new to mint. This is the same **coarse-saturation class** as the
H23 HARDEN-saturation marker and the SITE_MODEL_SPINE doc's 8th/9th draw-gap flags: *a self-refill that re-offers
already-finished/parked work because its saturation test is too coarse.* No prior atom/finding covers the planner rung
(grepped; none exists).

## Proposed fix (propose-then-proceed — self-drawable, reversible)

A **planner rest-with-proof marker**, mirroring the drained-and-gated quiet-wait pattern:

1. **BUILD** (`background/supervisor.py`): when a planner-spawned bounded worker concludes "no un-minted, non-walled
   ratified-goal next-step exists," it writes a dated verdict marker (e.g.
   `docs/observability/.planner_rest_with_proof.json` = `{date, proof_summary, minted_blocked_slugs, axes_sha}`).
   `_planner_rung_draw` returns `None` (rest) **while that marker is FRESH AND the ratified-goal state is unchanged**:
   same UTC day, DIRECTOR_AXES content-hash unchanged (no new axis/ruling), and no `in_progress/` mint has flipped
   `blocked → self-drawable`. It **re-fires (re-plans)** the moment ANY of those change — a new director ruling/axis, a
   blocked mint newly unblocked, or the day rolls (daily re-check). Independence (R15): keyed on the axes file's actual
   content + the live in_progress mint markers, never a constant.
2. **R15 both ways** (`test_planner_rung.py`): (a) marker-absent OR axes-changed OR a self-drawable un-minted step
   present → **MINTS**; (b) marker-fresh + axes-unchanged + all ratified steps minted-and-blocked → **RESTS with proof**.
   Mutation-prove both directions fire (a stale/constant marker that never invalidates must RED the "re-fires on new
   ruling" test).
3. **Fixture isolation** (lesson: *every new draw-rung register/state path must be isolated in test_supervisor.py's
   `_isolate` fixture, else it reds all "map empty → rest" find_work tests*): pin the new marker path in both
   `test_supervisor.py::_isolate` and `test_planner_rung.py` before committing, or the next supervisor commit wedges.

**This changes only WHEN the planner rests vs re-fires — it never mints past a wall, never lowers a bar, never rests
while a genuinely-un-minted non-walled ratified step exists.** It is the mechanised form of R17's rest-only-with-proof
for the planner rung, replacing the prose that keeps decaying into a treadmill.

## Walls left untouched (director-reserved)
One-way doors; L3+ level moves; curriculum/difficulty values (MC-2, population activation, R13 baselines); generator
ground truth; the roadmap rotation itself (proposed-not-moved). The fix touches only draw-timing machinery.

## Propose-then-proceed window
Proceeds immediately as RUNG-1 work the next tick draws, under standing reversible-build authority (supervisor.py +
its tests; a git-revertable ~1-hour change). If the marker-invalidation design surfaces a genuine director call, that
sub-item — and only that — escalates via NTFY while the rest builds. **Bounded planner tick complete: one grounded
mint written, premise-false proof recorded, no over-mint, no silent rest.**
