# [CC PROCESSING STATUS -- 2026-07-23 NIGHT] IN PROGRESS (rungs 2 + 4 ABSORBED + seeds MINTED; rungs 5/7 OPEN)
#
# The class-of-classes fix = a 7-rung WORK-SOURCE HIERARCHY the draw walks. Rungs 1/2/3/6 LIVE.
#   RUNG 2 (open campaigns) LIVE + R15-proven (supervisor.py::_open_campaign_draw).
#   RUNG 4 (declared-defect backlog) LIVE + R15-proven THIS TICK (night-enforcement §1):
#     supervisor.py::_declared_defect_backlog_draw reads docs/design/DECLARED_DEFECTS_REGISTER.yaml,
#     wired into _self_refill_draw + authorized_set_enumeration + _is_drained_and_gated. PROVEN both
#     ways (tests/background/test_defect_backlog_draw.py, 7 tests). LIVE FLIP DEMONSTRATED: before,
#     authorized_set_enumeration read all-empty -> REST-LEGITIMATE / drained=True with the spike-tail
#     defect sitting open; after, defect_backlog=Y -> MUST-DRAW / drained=False. The contradiction
#     (a declared defect not in the drawable set) is now impossible by construction.
#   SEEDS MINTED THIS TICK (night-enforcement §2, propose-then-proceed): docs/design/proposals/
#     PROPOSE_SPIKE_TAIL_ATTACK_PLAN.md (register plan_doc); PROPOSE_PREMISE_DEMAND_PUBLISH_SPEC003.md;
#     PROPOSE_SCENARIO_FOLLOWONS_RANKED.md (the rung-5 data source).
#
# STILL OPEN (honest red, credited -- night-enforcement: silent misses are the breach, honest reds are not):
#   RUNG 5 -- wire registered follow-ons as a drawable draw rung. DATA SOURCE now exists
#     (PROPOSE_SCENARIO_FOLLOWONS_RANKED.md); the draw fn + wiring + R15 pair remain.
#   RUNG 7 -- the PLANNER rung. NOT landed tonight, deliberately: a real coupling was found first ->
#     maybe_emit_graduation_proposal fires ONLY in run_cycle's quiet-rest branch (supervisor.py:2651);
#     a planner that makes rest structurally unreachable would silence the forward-discovery graduation
#     [ACT] to the director. The rung-7 build MUST decouple that [ACT] from the rest branch first, or
#     it introduces a director-facing regression. Landing it blind in an unsupervised night tick is the
#     exact "tired mega-turn on the release rung" the OPS1 standard forbids. Named here, drawn next tick.
#   R15 (b) "rest with 1-7 exhausted" lands with rung 7.
# UNBLOCKS: rungs 5/7 are independent contract-touching builds (tests first); drawn on subsequent ticks.
# -----------------------------------------------------------------------------------------------------

# [DIRECTOR-RULING] — WORK IS THE DEFAULT: the class-of-classes fix. The drawable set is never empty by construction. (2026-07-23)

**Type:** [DIRECTOR-RULING] via advisor bridge. This absorbs and supersedes the pattern behind all seven stall classes. Consume together with the seventh-class ruling in this queue.

## The diagnosis, on the record

Seven stall classes share one generator: **rest is the default and work must prove itself drawable against a hand-enumerated list of work shapes.** Reality mints shapes faster than the list grows. Meanwhile the system is full of *goals* the draw cannot see — the spike-tail defect (declared top priority, untouched five days), ABSENT rubric rows, registered follow-ons, worst cells — because the goal→task compilation has been done exclusively by the advisor staging documents. The director's question, verbatim: *"Why does it not always have something to do?"* Answer: it does; it cannot see it; nothing inside it is authorized to mint it. Both halves get fixed now.

## The standing WORK-SOURCE HIERARCHY (the draw walks this, in order; rest only below the bottom)

1. Staged director/advisor docs.
2. Open campaigns (per the seventh-class rule — items roll).
3. Below-target map atoms incl. propose-halves.
4. **The defect & findings backlog** — declared fidelity defects (spike tail first), FAIL/ABSENT battery and rubric rows, standing sanity findings: each is auto-mintable into an atom or a propose-doc. A declared defect that is not in the drawable set is a contradiction; enforce that as an invariant.
5. **Registered follow-ons** — every steer's "registered, not built" list is a queue, not a memorial (the scenario steer alone registered five).
6. Forward-discovery register (existing rules).
7. **The PLANNER rung**: if 1–6 are genuinely empty, run a bounded planning turn — read DIRECTOR_AXES, the epoch arc, and the fidelity ledger, and MINT the next batch as propose-then-proceed docs. Planning is work; resting instead of planning is the breach.

**Rest is legitimate only below rung 7** — i.e., when even planning can propose nothing within ratified scope. Until go-live that state should be structurally unreachable, and the daily note must say which rung fed each hour.

## The authorization sentence (explicit, so caution cannot masquerade as compliance)

**Minting tasks from ratified goals is authorized and expected.** The gates protect against bad builds, not against initiative: anything minted under rungs 4, 5 and 7 routes propose-then-proceed with its normal window, and the director's reserved walls (levels L3, one-way doors, curriculum values, generator ground truth) are untouched by this ruling. Being wrong in a proposal is cheap; being idle beside a declared defect is the failure.

## R15, both directions, before deploy

(a) Reproduce today's state — axes populated, spike-tail declared, no staged docs — and prove the draw MINTS rather than rests (the failing test first). (b) Prove a genuinely exhausted rung-1–7 state still rests with the full enumeration published. (c) The seventh-class campaign test and the existing kill-the-rung mutation still pass.

## Seed the backlog NOW (rung 4/5, no waiting for the mechanism)

Mint immediately as propose-docs: the **spike-tail defect** attack plan; the **premise-demand publish** (Spec 003 two-level bar); the cap observation-window and MC-2 collateral test if not already in flight; the scenario steer's five registered follow-ons as one ranked doc. These proceed under their windows while the hierarchy is being mechanised — product does not wait for the machinery that guarantees product.

**Risk & proportionality:** touches the draw's core — failing tests first, own commits, R15 proven; minted work is proposal-gated so scope stays governed. Tag: **class-of-classes fix — contract-touching with named tests; the seeded proposals proceed.**

— Advisor bridge, carrying the director's question as the design correction it is, 2026-07-23.
