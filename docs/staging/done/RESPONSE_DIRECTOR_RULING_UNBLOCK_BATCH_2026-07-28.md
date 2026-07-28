# Response — DIRECTOR_RULING_UNBLOCK_BATCH_2026-07-28 (MINT source, coverage check)

Ruling actioned as a **MINT source** (§2+§4 DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE). One atom per WORK-THIS-CREATES deliverable; deliverables already covered by an existing map atom / PLANNER_MINTED doc are NOT re-minted, per the ruling and the draw rule. Bounded worker tick: mint + record; the mints carry execution to their next draw.

## Coverage check (grep of `maturity_map.yaml` + `docs/staging/**/PLANNER_MINTED_*` before minting)

| # | Deliverable | Verdict | Carrier |
|---|---|---|---|
| 1 | Merit-order window requirement stated; curriculum proposal if needed | **NEW MINT** | `PLANNER_MINTED_merit_order_window_requirement_2026-07-28.md` (in_progress, self-drawable). The reconstruction BUILD atom `W1_6b_merit_order_reconstruction` + `PLANNER_MINTED_merit_order_reconstruction_discover_2026-07-25` already exist — but neither is the *requirement-statement* deliverable. The statement is written in the mint body: **no curriculum proposal needed** (baseline-fidelity change, not curriculum, R13-disciplined); the window is a scheduling artifact that **elapses today (2026-07-28)**; the one residual action is flipping `W1_6b.blocked_on` off the elapsed-window text so the BUILD draws (level move stays `director_level_up`, R16). |
| 2 | Cohort promotion taken at twin authority, or batched L3 with the reason | **NEW MINT** | `PLANNER_MINTED_cohort_promotion_disposition_2026-07-28.md` (in_progress, self-drawable). Cohort BUILD atoms `CA1/CA2/CA3/CA4` exist, BUILT L3-quality, `blocked_on: director_level_up` — but the *promotion-routing decision* is not an atom. Disposition stated: **CA4 (L1) → twin standing authority, ledger-backed**; **CA1/CA2/CA3 (L3) → batch for director** with the latent-flip + untestable-at-current-book caveats carried. |
| 3 | Exit-criterion counter built, computing from primary state, in the daily note, R15 paired | **ALREADY COVERED — no re-mint** | Map atoms `HX1_exit_criterion_counter_mechanise`, `HX2_stall_set_coverage_verdict`, `HX3_counter_published_and_derivable` (maturity_map.yaml, minted 2026-07-27 from `DIRECTOR_RULING_HARNESS_EXIT_CRITERION_RATIFIED_2026-07-27`). All three `blocked_on` a director **BUILD_OPEN / H-lane FRONT_OPEN** in `gate_authorizations.jsonl` — the bootstrapping exception the ruling's own decision 2a demotes general harness BUILD behind, R16 director-console-only. That gate is the same "breakage stays drawable" the current ruling §3 re-affirms; it needs one console line to draw. Recorded, not re-minted. |

## Acceptance status (ruling: "none of the three remains blocked-and-silent")
- D1, D2 are **registered as self-drawable mints** (no longer silent); their drawable work (register-publish + the `W1_6b` blocked_on flip + the twin/L3 routing) executes at next draw.
- D3's `HX1–3` are visible in the map with an explicit `blocked_on` naming the director BUILD_OPEN — **blocked with the requirement stated**, not silent. Per ruling §3 this is the ratified control that "outranks further gap mints"; the one open dependency is the director console act.

— autonomous worker, mint tick, 2026-07-28
