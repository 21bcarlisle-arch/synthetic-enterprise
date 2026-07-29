# Blocked-set reclassification against the reversibility test (2026-07-29)

**Atom:** `PLANNER_MINTED_reversibility_reclassify_blocked_set_2026-07-29` (WORK-THIS-CREATES #1 of
`DIRECTOR_RULING_WORK_AT_RISK_DEFAULT_2026-07-29`).
**Method:** read-only enumeration + judgement. No production state changed. Consumed by the action
atom (#2, `PLANNER_MINTED_reversibility_action_and_act`) and the batched [ACT] (#3).

## The test applied (ruling §2, verbatim)
> "Can this be undone by a **single act**, with **no external consequence in the meantime**?"
> YES = **PROCEED-AT-RISK** (default, no permission — recommend, proceed, record the one-line undo, flag it).
> NO = **RESERVED** (one-way doors, safety/authority-trust, unpublishable, R13 curriculum-as-science).

**§4 binding also applied:** any RESERVED verdict that cannot *name its specific irreversibility* is
invalid → flipped to PROCEED-AT-RISK. The regression the ruling owns (§0/§9): the set was drawn **by
category** (all `director_level_up`, all `director_ratification`, all BUILD_OPENs) not **by risk**.

## Enumeration — every currently-blocked minted item (real disk state, `docs/staging/in_progress/`)
21 blocked mints (3 further mints there are `SUPERVISOR_DRAW: self` and are NOT blocked:
`one_node_to_depth_with_charts`, `scope_independence_evidence`, `stubs_and_content_rehome`).

### CLASS 1 — `director_level_up` × 15 → **PROCEED-AT-RISK** (verdict), MECHANISM-WALLED (action)
`director_window_delta_view`, `gap1_reader_contract_failopen_fix`, `gap_registers_as_mint_sources`,
`inbound_ratification_batch_path`, `intra_year_price_cap_granularity`, `owned_quantity_registry_gate`,
`payment_channel_dd_consistency_invariant`, `privacy_policy_page`, `rng_substream_primitive`,
`ruling_consumption_ledger_release`, `shared_primitive_ensuring_activity`, `size_and_clone_ratchet`,
`supply_start_semantic_separation`, `unstated_reason_block_impossible`, `working_day_calculator`.

- **Verdict: PROCEED-AT-RISK.** The ruling is explicit — *"Level moves are reversible."* Each is a
  worker-built L2/L3-quality atom whose `level_current` is HELD per R16 (confirmed in
  `docs/design/maturity_map.yaml`: e.g. cohort atoms carry `level_current HELD ... per R16`). A level
  is internal maturity bookkeeping: it publishes nothing, touches no customer/market, and the website
  build-stamp reads a test-count from CLAUDE.md, **not** per-atom levels
  ([[feedback_claudemd_build_stamp_coupling]]). No external consequence in the meantime.
- **The single reversing act:** re-set `level_current` to its prior value (git revert of the bump
  commit). One act, no external effect.
- **HONEST BLOCKER (not a wall — a DIAL defect, ruling §9):** the *verdict* is proceed-at-risk, but the
  *action* currently hits the R16 pre-commit level gate (`is_valid_level_up`), which enforces
  category-blocking regardless of risk. This is exactly the mechanism the ruling reclassifies away from.
  **Do NOT `--no-verify` these** ([[feedback_no_verify_and_shared_surface_writes]], R16 memory: "Never
  --no-verify a `level_current` change"). The clean release path is atom #4
  (`reversible_draws_dont_queue_for_permission`): update the gate so a reversible level move is not
  category-walled, then #2 bumps them through the updated mechanism with recorded undos. Until #4 lands,
  these are verdict-reversible but mechanism-held — an empty-feasible-set DIAL defect, not a director act.

### CLASS 2 — `director_build_open` × 1 → **PROCEED-AT-RISK**
`stop_control_gap_characterisation`.
- **Verdict: PROCEED-AT-RISK.** Ruling: *"BUILD_OPEN on an already-ratified decision is plumbing not a
  decision."* The characterisation itself is DISCOVER/doc work — drawable now with no BUILD_OPEN needed
  to *characterise* the gap. **Reversing act:** delete the characterisation doc / git revert.
- Caveat carried forward from the ledger-atom's Channel-B finding: if characterisation concludes a
  *build* is needed, the BUILD_OPEN consuming mechanism may not exist in code
  (`gap_registers_as_mint_sources` states "authorization exists; the mechanism the gate reads does
  not yet") — that is a **build gap to state**, not a director act. Verify at build-draw.

### CLASS 3 — `director_ratification` × 2 → **SPLIT** (reversible half proceeds; canon-half reserved)
- **`first_ranked_gap_list`** — producing/using a ranked gap backlog is a diagnostic and **reversible**
  (LAW A: the plan is a diagnostic, never a target; re-ranking is expected). → **PROCEED-AT-RISK** to
  produce and act on the ranked list. The only genuinely reserved sliver is the director *blessing a
  "deliberate-and-staying" simplification set as published canon* — that is a scope/values statement
  (§6-adjacent). Named irreversibility: a published "this is deliberate and staying" stance. Keep that
  sliver as a one-line director note; it does **not** block ranking or drawing the gaps.
- **`money_representation_evidence`** — DISCOVER already CLOSED with the recommendation returned:
  boundary-reconciliation first, full float→Decimal migration director-reserved. → **PROCEED-AT-RISK**
  on the boundary-reconciliation work (git-reversible code). **RESERVED sliver:** committing to a
  pervasive money-type migration is a large architecture decision — named irreversibility: a repo-wide
  type change that is technically git-reversible but expensive to cleanly unwind and defines a monetary
  treatment (portability constraint: no hardcoded monetary treatment). Keep as a director note, not a
  work-block.

### CLASS 4 — GENUINELY RESERVED (one-way door / curriculum) × 1
- **`generator_draw_wiring`** (`director_live_run`, activation of `SE_DRAW_POPULATION`). → **RESERVED.**
  **Named irreversibility:** live activation of the real-population draw is a one-way-door-class
  curriculum/activation act (director-reserved across GENERATOR_ACTIVATION / POPULATION_ACTIVATION
  rulings and [[project_population_activation_infra]]); R13 keeps curriculum activation the director's.
  A signed director word is the literal act — this stays on the director's list.

### CLASS 5 — NOT DIRECTOR ACTS AT ALL — build-sequenced × 2 (listing these as director acts is dishonest)
- **`ssp_negative_lift_cells`** — `BLOCK_RELEASE: W1_6b_merit_order_reconstruction`. Blocked on a BUILD
  dep (the merit-order reconstruction landing), **no interim tuning** (R12). Not releasable by any
  director act. → build-sequenced.
- **`value_chain_observation_window_cap`** — nominally `director_live_run`, but actually blocked on a
  live MtM/margin-call feed being built first (ledger-atom finding). → build-sequenced, not a director act.

## Reclassification summary (the count the ruling asks for)
| Class | Items | Verdict |
|---|---|---|
| `director_level_up` | 15 | **PROCEED-AT-RISK** (verdict) — action gated on atom #4, not on the director |
| `director_build_open` | 1 | **PROCEED-AT-RISK** (characterisation is DISCOVER; verify build-open at build-draw) |
| `director_ratification` | 2 | **PROCEED-AT-RISK** on the reversible half; a values/canon sliver each stays a director note |
| `director_live_run` (population activation) | 1 | **RESERVED** — one-way-door / curriculum activation |
| build-dep (mislabelled or genuine) | 2 | **NOT director acts** — build-sequenced |

**Bottom line:** of 21 "director-blocked" mints, exactly **1 is a genuine one-way-door director act**
(`generator_draw_wiring`) plus **two small values/canon slivers** the director may bless at leisure
(`first_ranked_gap_list` staying-set, `money_representation` full-migration). The other **18 were walled
by category, not by risk** — 16 are reversible work the agent should action (15 gated only on the
mechanism fix #4, 1 DISCOVER-drawable now), and 2 are build-sequenced dependencies that were never
director acts. This register is the input to #2 (action) and #3 (batched [ACT]).

## Reverse / undo
Delete this file; no production state changed (read-only analysis). git revert of the commit.
