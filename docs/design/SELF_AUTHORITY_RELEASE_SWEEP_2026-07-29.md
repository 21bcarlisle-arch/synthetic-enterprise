# Self-authority release sweep — 2026-07-29

**Atom:** `PLANNER_MINTED_self_authority_release_sweep_2026-07-29.md` (RUNG-1, self-drawable).
**Source rulings:** `DIRECTOR_RULING_LITERAL_ACTS_2026-07-29` (#2) + `DIRECTOR_RULING_LITERAL_ACT_LIST_2026-07-29` (#4) — *"everything releasable under existing authority, released and reported, before the list is sent."*
**Runs before** the sibling ledger atom `PLANNER_MINTED_blocked_item_literal_act_ledger_2026-07-29.md`.

## Method
Authoritative source of the blocked set is the deadman's own enumerator
`background/deadmans_switch.py::_open_blocked_mints()` (reads live disk, independent of the
supervisor's rest logic) — the same list that surfaces to the director. Every mint it returns was
classified against the three self-releasable classes named in the atom. R12 held: **no item was
cleared by re-scoping it into nothing.** The count is a diagnostic, not a target.

## Before / after
| | count |
|---|---|
| Blocked mints BEFORE sweep | **21** |
| Self-releasable found | **0** |
| Released this pass | **0** |
| Blocked mints AFTER sweep | **21** |

The count does **not** fall on this sweep — and that is the correct, honest result. Nothing in the
current blocked set is within the agent's own authority. The 5 stale-window mints that *were*
self-releasable were already released at 02:16Z on 2026-07-29; no new propose-then-proceed window
has elapsed since. Every remaining blocked item is a director-reserved wall (R16 level-up /
build-open / one-way-door activation / set-ratification) or a BUILD dependency. This confirms the
director's act-list (sibling atom) is **not polluted** with items the agent could have cleared.

## Self-releasable classes — all checked, all empty
- **Elapsed propose-then-proceed windows** — NONE. All 21 carry a hard `director_*` release marker,
  not a reversible proceed-by-default window. (The 02:16Z release of 5 stale mints already swept
  this class; nothing new has elapsed.)
- **Twin standing L1/L2 authorization** — NONE. `DIRECTOR_TWIN` is the standing approver for
  **routine** L1/L2 and BUILD-within-the-open-epoch, *not* for **map-atom** `director_level_up`
  moves — those are R16 director-reserved (no self-bump), so the ~13 Channel-A items are not
  twin-routable.
- **Consumed-ruling self-drawable-but-sitting** — the 3 self-drawable K-pilot mints
  (`one_node_to_depth_with_charts`, `scope_independence_evidence`, `stubs_and_content_rehome`) are
  **drawable, not blocked** (`SUPERVISOR_DRAW: self-drawable`, excluded by the enumerator). They are
  BUILD work surfaced by the tick's normal draw — not "releases" and not on the director's list.

## Classification of all 21 blocked mints (none self-releasable)

**Channel A — batched map-atom LEVEL-UP (R16 director-reserved), 13 items.** One director act
(a batched `gate_authorizations.jsonl` / `is_valid_level_up` ledger move) releases all:
`director_window_delta_view`, `inbound_ratification_batch_path`, `owned_quantity_registry_gate`,
`privacy_policy_page`, `rng_substream_primitive`, `ruling_consumption_ledger_release`,
`shared_primitive_ensuring_activity`, `size_and_clone_ratchet`, `working_day_calculator`,
`unstated_reason_block_impossible`, `intra_year_price_cap_granularity`,
`payment_channel_dd_consistency_invariant`, `supply_start_semantic_separation`.

**Channel B — BUILD_OPEN ledger, 3 items.** `gap1_reader_contract_failopen_fix`,
`gap_registers_as_mint_sources`, `stop_control_gap_characterisation`. (The sibling ledger atom must
verify whether the `BUILD_OPEN` consuming parser exists in code today — `gap_registers_as_mint_sources`
states in its own body the reading mechanism does not yet exist; that verification is deliberately
left to the ledger atom, not resolved here.)

**Channel C — director activation word, one-way door, 2 items.** `generator_draw_wiring`
(`SE_DRAW_POPULATION` live activation, one-way door #5/#7 — never self-authorised) and
`value_chain_observation_window_cap` (blocked on a live MtM/margin-call feed; the mechanism half is
self, the named curriculum-difficulty value is the director's).

**Channel D — director ratification of a proposed SET, 2 items.** `first_ranked_gap_list` (ratify
the deliberate-and-staying set + front/epoch opens) and `money_representation_evidence`
(float→Decimal migration decision — DISCOVER closed, recommendation returned as an [ACT]).

**Dependency-blocked — NOT a director act, 1 item.** `ssp_negative_lift_cells` — blocked on the
W1_6b merit-order / gas-first reconstruction landing (a BUILD dep, no interim tuning per R12).
Listing this as a director act would be dishonest; it is build-sequenced.

## Exit-criteria check
- Every mint classified (self-releasable vs genuinely director-blocked): **done** (table above).
- Everything self-releasable actually released this pass: **done** — the set is empty; nothing to release.
- Committed before/after report naming each item + its authority: **this document.**
- R12 (no item cleared by re-scoping into nothing): **held** — count unchanged at 21 precisely
  because nothing was within own authority.
