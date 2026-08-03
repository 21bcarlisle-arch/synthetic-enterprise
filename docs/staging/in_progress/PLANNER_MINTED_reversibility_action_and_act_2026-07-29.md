<!-- BLOCK DISSOLVED 2026-08-03 (worker tick) -- KEPT IN in_progress/ ON PURPOSE, AS DRAWABLE WORK,
  NOT ARCHIVED. The stated blocker above is now FALSE. It reads "the agent cannot self-cross the R16 wall",
  but R16 was RESCOPED 2026-08-03: "a level move must leave an auditable trace in gate_authorizations.jsonl
  ... What R16 never required, and no longer implies, is that anyone AUTHORISE the move: self-certify with
  the evidence and go." There is no wall left to cross, and no phone-signed LEVEL_UP batch to wait for.
  RESIDUAL, NAMED SO THE NEXT TICK CAN DRAW IT DIRECTLY: item #2's 15 reversible level moves are now
  self-certifiable via background.gate_authorization.record_level_up_self_certified.
  They are deliberately NOT bulk-stamped here. Each needs its level RE-VERIFIED against real artifacts
  first -- clearing a blocked_on has never moved a level_current, and a control that passes for the wrong
  reason is not evidence (the abolished-block stale-cells class). Precedent from THIS SAME TICK: five items
  filed as "build done, only the abolished level move remained" were checked against real disk, and one of
  them -- director_window_delta_view -- turned out to have no code and no test anywhere, only design-doc
  mentions. A bulk stamp would have recorded it as done. Fifteen individual re-verifications is the work;
  that is not bookkeeping, and it is why this file stays in the BUILD queue rather than the archive. -->

<!-- PARTIALLY ACTIONED 2026-07-29 (planner tick):
  #3 (batched [ACT]) DELIVERED -> docs/observability/work_at_risk_batched_act_2026-07-29.md (committed).
  #2 (release the proceed-at-risk set) is BLOCKED, not self-actionable: the reclassification's 15
  reversible level moves are mechanism-held on atom #4 (reversible_draws_dont_queue_for_permission),
  whose CORE relaxes the R16 pre-commit level gate = an authority/safety-control change the agent may
  NEVER self-authorize on an advisor-bridge ruling (authentication convention; one-way-door cat 5/8).
  Per this atom's own decompose-and-escalate note: reversible parts done, irreducible core ESCALATED
  via NTFY. Left in in_progress/ (open sub-item = the director act ACT-1/ACT-2 in the batched [ACT]).
  Self-authority release sweep already found 0/21 self-releasable; nothing crossed the R16 wall; no
  --no-verify (R16). R12 held: count stays 21 by honest classification, not re-scoped to zero. -->
<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- BLOCK_RELEASE: propose_then_proceed -- was 'director_level_up', an act abolished 2026-07-29 and swept 2026-08-03: propose, record, act. Original note: #3 delivered; #2 releases the 15 director_level_up items via the director act ACT-1 in docs/observability/work_at_risk_batched_act_2026-07-29.md (phone-sign the LEVEL_UP batch, OR console-authorize atom #4's R16 gate relaxation). Agent cannot self-cross the R16 wall. -->

# [PLANNER-MINTED] Action the proceed-at-risk class with recorded undos, and send ONE batched [ACT] (2026-07-29)

**Source ruling:** `DIRECTOR_RULING_WORK_AT_RISK_DEFAULT_2026-07-29.md`, WORK-THIS-CREATES **#2**
("Everything in the proceed-at-risk class actioned, with recorded undos.") **and #3** ("One batched
[ACT]: what was done, how to reverse each, what remains genuinely reserved and why.") — #3 is the
OUTPUT artifact of #2, so both are minted ONCE here.

**Serves:** the ruling's core move (§1) — reversibility is achieved by RECORDING, not by ASKING: make
the recommendation, proceed, record the one-line undo, flag it in the batch. The director reverses if
he disagrees. This is the ACTION half; the reclassification (#1) is the input.
**Real-world fidelity gained:** none directly — operational authority. Value = the blocked count falls
on the AGENT's action (not the director's), satisfying the ruling's acceptance test, and the director
receives ONE batch containing only genuine one-way doors.

**Lane:** FRAME + self-release action (self-authority level/window/mint/BUILD_OPEN releases per the
widened §2 class; **no production behaviour change, no walls crossed** — every release is git-reversible
and recorded). Self-drawable now.
**Target level:** operational action + committed before/after ledger + one batched NTFY [ACT]. No
maturity-map level claimed.
**Deps:** **[PLANNER_MINTED_reversibility_reclassify_blocked_set_2026-07-29]** — must have the
per-item verdicts before acting. Do NOT release blind.

## Relationship to `self_authority_release_sweep` (extends, does not duplicate)
`PLANNER_MINTED_self_authority_release_sweep_2026-07-29.md` released under the narrow pre-ruling scope.
This atom releases the ADDITIONAL items that §2 reclassifies to proceed-at-risk (reversible level moves,
BUILD_OPENs on already-ratified decisions). If the sweep has already run, start from its after-state and
release only the delta the reversibility test newly permits — do not re-release what it cleared.

## Exit criteria (#2 + #3 both satisfied)
- For every item the reclassification marks PROCEED-AT-RISK: make the recommendation, **proceed**
  (release the level/window/mint/BUILD_OPEN via existing self-authority paths — memory
  `blocked_on: clear ≠ director_level_up`, `levels are proposals`), and **record a one-line undo** in
  `background/decision_log.py`.
- Produce **one** committed batched [ACT] stating, per item: what was done, the exact single reversing
  act, and — for every item left RESERVED — the named irreversibility. NTFY it as one message (R5/R8
  batch, terse).
- Acceptance (ruling §52): items awaiting a director act fall to those that are genuinely one-way, each
  stating its irreversibility.

## Reverse / undo
Each released item carries its own recorded one-line undo (re-set the level/blocked_on/window). The
batch is a report — retract by follow-up NTFY. git revert of the release commits.

---
## PROGRESS 2026-08-03 (worker tick) — the residual MEASURED, and the act-list is largely obsolete

The block note above said the residual is "15 reversible level moves, deliberately NOT bulk-stamped,
each needing re-verification against real artifacts first." That is still the right disposition. What
this tick adds is the thing that was missing: **the actual list, measured off real map state**, so the
next tick draws named atoms instead of re-deriving the triage a fourth time.

### Finding 1 — the `director_level_up` blocks are already gone from the map
`docs/design/maturity_map.yaml` now carries **4 blocked atoms out of 179**, and not one is
`director_level_up`:
`W1_8_zonal_locational_pricing` (closed/watching-brief), `OPS1_operational_layer_rebuild`
(director_systemd_deploy), `OPS1_governance_refusal_mutation_test` (director_live_run),
`H27_payment_belief_gap` (coupled_triad_measured). The 2026-08-03 sweep did its job. So there is no
blocked *set* left to release — only level *cells* that the sweep never touched, which is precisely the
abolished-block stale-cells class (clearing `blocked_on` has never moved `level_current`).

### Finding 2 — 29 atoms carry a "level HELD per R16 / director_level_up" note, and 18 of them are AT TARGET
Measured this tick by scanning every atom's `simplifications` for a HELD-per-R16 note and comparing
`level_current` to `level_target`:

**Already at target — the note is STALE PROSE, not a held level (18):**
`C13_weather_normalisation`, `CA1_cohort_assignment_live`, `CA2_coverage_report_realised_cohort`,
`CA3_segmentation_untestable_ledger_marking`, `F1a_sim_customer_response`, `F1b_company_comms`,
`F1c_harness_conversation_gap`, `G11_activity_cost_utilisation`, `H23_publish_gate_scope_marker`,
`H24_precommit_gate_git_env_isolation`, `H24_worktree_dir_autoreap`, `W1_2_generate_futures`,
`W1_3_national_weather_signal`, `W1_4_regional_weather_field`, `W1_6_physics_price_signal`,
`W1_9_dsr_flex_markets`, `W2_13_occupancy_consumption_volume_shape`, `W2_2_population_draw`.
These need **no level move at all**. Their notes assert a wait on an act that no longer exists, which
misleads anything scanning for "HELD" — the correction is to the note, not to the cell.

**Genuinely below target — the real re-verification queue (11):**
`B10_competitor_switching_response` (L0→3), `B6_collateral_cash_death_loop` (L0→3),
`B7_customer_state_layer_moves_and_shocks` (L0→3), `DD_seasonal_cashflow_physics` (L0→3),
`E5_carbon_three_ledger` (L0→3), `SITE1_expert_doors` (L2→3), `SPINE_1_scenario_world_state` (L0→3),
`SPINE_3_gas_storage_crisis_regime` (L0→3), `W1_10_ev_heatpump_geography` (L2→3),
`W1_5_premise_demand_shape` (L1→3), `W1_7_renewable_capacity_trends` (L2→3).

### Finding 3 — the batched [ACT]'s own act-list is obsolete, and saying so is the point
`docs/observability/work_at_risk_batched_act_2026-07-29.md` ACT 1 offers the director "Path A: phone-sign
the LEVEL_UP batch OR Path B: console-authorize the R16 gate relaxation." **Neither is needed.** R16 was
rescoped 2026-08-03 to *record*, not *authorise*; `record_level_up_self_certified` is the path, and a
level move is not among the four reserved classes in `background/one_way_door.py`. ACT 3's two "values
slivers" are likewise not bare asks the director owes an answer to — under NEVER_ASK_WITHOUT_RECOMMENDING
they proceed with a recommendation. **ACT 2 (`generator_draw_wiring`, `SE_DRAW_POPULATION=1`) is the one
item that genuinely stays reserved** — population activation is curriculum, and curriculum is the
director's under R13.

### Why nothing was stamped this tick, and the evidence for that being right
`SITE1_expert_doors` is one of the 11, and this same tick did real build work on it: closed its L2→L3
residual (b) by driving the LIVE doors (`site/live_pixel_verify.py`, commit `80055c4ff`), which found and
fixed a genuine live defect. It was still **held at L2**, because residuals (a) and (c) are unbuilt. One
atom, verified properly, moved zero levels. A bulk stamp of all 11 would have recorded it as L3.

**NEXT TICK'S DRAW, named:** the 11 above, one at a time, each re-verified against artifacts before any
`record_level_up_self_certified`. Plus the cheap, separable cleanup: correct the 18 stale HELD notes.
