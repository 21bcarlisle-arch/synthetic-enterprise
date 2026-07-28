<!-- SUPERVISOR_DRAW: fyi -->
# [PLANNER-MINT-COVERAGE] — `DIRECTOR_RULING_BLOCKED_MINT_BATCH_2026-07-28` WORK-THIS-CREATES disposition (2026-07-28)

Per the RUNG-7 mint contract (§2+§4 `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27`): one atom
minted per named deliverable in the ruling's **WORK THIS CREATES** block; a deliverable already covered by
an existing `PLANNER_MINTED_*` doc or map atom is **NOT re-minted** — stated here.

| # | Deliverable | Disposition |
|---|-------------|-------------|
| **1** | Ruling-consumption creates the ledger entry that releases a block — or a plain statement of what can. | **NEWLY MINTED** → `PLANNER_MINTED_ruling_consumption_ledger_release_2026-07-28.md`. grep-confirmed net-new; the §0 authority-plumbing fault. DISCOVER-first (resolves the R16 wall: transcription-legitimate vs director-reserved), BUILD gated on the director's seam sign-off. |
| **2** | The five §1 items drawn. | **ALREADY MINTED (5 docs) — not re-minted.** `gap1_reader_contract_failopen_fix`, `gap_registers_as_mint_sources`, `inbound_ratification_batch_path`, `generator_draw_wiring` (dated 07-24), `dd_seasonal_cashflow_physics` (dated 07-25) — all present in `docs/staging/in_progress/`. "Drawn" = their BUILD half executing, which is the release deliverable-1 plumbs; as MINTS they exist. |
| **3** | Level-ups taken at twin authority or batched with their level stated. | **ALREADY MINTED (2 docs) — not re-minted.** `director_window_delta_view` + `owned_quantity_registry_gate` (both 07-28). Disposition is of those existing atoms (twin-ratify if L1/L2, batch to director if L3), not a new atom. |
| **4a** | Reasons stated for the four §3 blocks. | **ALREADY MINTED (4 docs) — not re-minted.** `board_spec_001_wholesale_reconciliation`, `intra_year_price_cap_granularity`, `money_representation_evidence`, `payment_channel_dd_consistency_invariant` (all 07-28). Reason-stating is disposition of those existing markers. |
| **4b** | Unstated-reason blocks made impossible (the MECHANISM half). | **NEWLY MINTED** → `PLANNER_MINTED_unstated_reason_block_impossible_2026-07-28.md`. grep-confirmed net-new (distinct from the done `ruling_missing_work_block_defect_surface`, which is about a *ruling* missing a WORK-THIS-CREATES block, not an *atom/marker* with a reason-less `blocked_on`). |
| **5** | The ranked-gap-list ratification sent as one batched [ACT]. | **ALREADY MINTED — not re-minted.** `first_ranked_gap_list` (07-28) produces the list and is `blocked_on: director ratification of the proposed deliberate-and-staying set`; the batched `[ACT]` send is that atom's escalation, not a new atom. |

**Net new mints this tick: 2** (deliverables 1 and 4b). **Covered by existing mints: 4** (2, 3, 4a, 5).

**Acceptance check (ruling's own bar — "no minted item is blocked without a stated reason and a named
release condition"):** both new mints carry an explicit `blocked_on` + reason + release condition (mint-1
BUILD half: `director_authority_seam_signoff`, DISCOVER drawable now; mint-4b BUILD half:
`director_level_up`, DISCOVER drawable now). This is deliverable-4b's own standard applied to its siblings.
