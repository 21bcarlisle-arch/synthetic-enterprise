<!-- SUPERVISOR_DRAW: self-drawable -->

# [PLANNER-MINTED] The blocked-item literal-act document, grouped by channel, each act verified end-to-end (2026-07-29)

**Source rulings (BOTH — same deliverable, deduped into this one atom):**
`DIRECTOR_RULING_LITERAL_ACTS_2026-07-29.md` (WORK-THIS-CREATES #1, #3, #4) **and**
`DIRECTOR_RULING_LITERAL_ACT_LIST_2026-07-29.md` (WORK-THIS-CREATES #1, #2, #3). The two rulings are
the director repeating one ask ("give me the literal act, not a description of the block"); their
deliverables are the same and are minted ONCE here. See the sibling atom
`PLANNER_MINTED_self_authority_release_sweep_2026-07-29.md` for the release half (LITERAL_ACTS #2 /
LITERAL_ACT_LIST #4).
**Serves:** DIRECTOR_AXES Axis 1 (the director must be able to act in a small number of pastes) +
the top system defect named in the ruling: "22 blocked items with a working detector and no working
release." Fidelity/ops, not a product surface.
**Real-world fidelity gained:** none directly — this is an operational-authority artifact. Its value
is that ONE director action makes the blocked count fall measurably (the ruling's acceptance test).

**Lane:** DISCOVER + FRAME (doc-only enumeration and code verification; no production behaviour
changes). Self-drawable now.
**Target level:** doc-only operational artifact (no maturity-map level claimed). Output is a committed
document + a batched NTFY [ACT] pointing at it.

## Priority
The rulings tag this **priority zero**, above further gap minting, the K-pilot decomposition, and all
HARDEN work. It is the top drawable item after any live gate wedge.

## Seed analysis (already done this tick — the next draw starts HERE, not cold)
Real disk state 2026-07-29: `docs/staging/in_progress/` holds **24** `PLANNER_MINTED_*` mints — **3
self-drawable** (K-pilot: one_node_to_depth, scope_independence, stubs_and_content_rehome; NOT
blocked) and **21 blocked**. The 21 collapse to a **small number of director CHANNELS**, which is the
answer to "group by channel so he performs one act per channel, not 22":

- **CHANNEL A — batched map-atom LEVEL-UP (R16), ~14 items.** `director_window_delta_view`,
  `owned_quantity_registry_gate`, `privacy_policy_page`, `rng_substream_primitive`,
  `ruling_consumption_ledger_release`, `shared_primitive_ensuring_activity`, `size_and_clone_ratchet`,
  `inbound_ratification_batch_path`, `working_day_calculator`, `intra_year_price_cap_granularity`,
  `payment_channel_dd_consistency_invariant`, `supply_start_semantic_separation`,
  `unstated_reason_block_impossible` — all carry `BLOCK_RELEASE: director_level_up` and are built to
  L2-quality awaiting the director's level move. **These are ONE act:** a batched level-up. The atom
  must confirm the LITERAL act (a `gate_authorizations.jsonl` ledger entry / `is_valid_level_up`
  console form — R16) and PROVE it releases at least one, before emitting.
- **CHANNEL B — BUILD_OPEN ledger, 3 items.** `gap1_reader_contract_failopen_fix`,
  `gap_registers_as_mint_sources`, `stop_control_gap_characterisation`. **CRITICAL FINDING to verify:**
  `gap_registers_as_mint_sources` states in its own body *"The authorization exists; the mechanism that
  the gate reads does not yet."* This is very likely the ruling's deliverable #4/#2 — **the BUILD_OPEN
  release mechanism does not exist in code.** The 19:40 BST console act failed for exactly this reason
  (the `LEDGER: BUILD_OPEN` parser was part of the work being authorised). The atom must VERIFY whether
  a consuming parser exists/is tested TODAY; if not, emit NO act for this class and instead state
  "no mechanism — here is what would need building" (ruling non-negotiable).
- **CHANNEL C — director activation word, one-way door, 1 item.** `generator_draw_wiring` —
  live activation of `SE_DRAW_POPULATION` (one-way-door #5/#7, real-population activation). The literal
  act is a director console word; the atom must state the EXACT string the consuming mechanism reads
  and prove that path fires (this is the item that "did nothing" twice — verify before emitting).
- **CHANNEL D — director ratification of a proposed SET, 2 items.** `money_representation_evidence`
  (float→Decimal migration decision — DISCOVER already CLOSED, recommendation returned as an [ACT]:
  boundary-reconciliation first, full migration director-reserved) and `first_ranked_gap_list`
  (ratify the `deliberate-and-staying` set + front/epoch opens).
- **DEPENDENCY-BLOCKED — NOT director acts, 2 items.** `ssp_negative_lift_cells` (blocked on the
  merit-order/gas-first reconstruction landing — a BUILD dep, no interim tuning per R12) and
  `value_chain_observation_window_cap` (blocked on a live MtM/margin-call feed being built first).
  State these as build-sequenced, NOT as things the director can release — listing them as director
  acts would be dishonest.

**Second critical finding for deliverable #3 (the "four unstated-reason blocks"):** the director's
complaint that four items are "blocked (reason unstated)" is a **parser-format mismatch**, not missing
reasons. `deadmans_switch.py::_open_blocked_mints` parses prose `blocked_on:` / `UNBLOCKS:` lines; the
four named items (`intra_year_price_cap_granularity`, `money_representation_evidence`,
`payment_channel_dd_consistency_invariant`, `supply_start_semantic_separation`) carry their reason in a
`<!-- BLOCK_RELEASE: ... -->` HTML-comment marker the enumerator does not read. The reasons ARE stated;
the register that surfaces them to the director does not render that marker. The atom resolves this by
(a) stating each reason from its BLOCK_RELEASE marker and (b) proposing the enumerator read the marker,
so this class of false "unstated" report cannot recur (R10 — fix the class, not the instance).

## Exit criteria
- ONE committed document (e.g. `docs/design/BLOCKED_ITEM_LITERAL_ACTS.md`) listing every currently-
  blocked minted item with, for each: id; one-line block; **the verbatim literal act** (exact console
  command / signed-NTFY body / file path+contents — the STRING, not a description); execution channel;
  observable success criterion (commit / ledger row / status change to look for). **Grouped by
  channel** per the seed above.
- **Verified before emitting (ruling non-negotiable):** each channel's act is proven to work end-to-end
  — a real release performed against at least one item, OR a test proving the consuming path fires.
  Two console acts have now done nothing; a third that does nothing is worse than delay.
- **Where no release mechanism exists (Channel B, likely), say so explicitly** and emit no act for that
  class — instead state what would need building (ruling #4 / #2). Confirm by reading the code whether a
  `LEDGER: BUILD_OPEN` / build-open consuming parser exists and is tested TODAY.
- The four "unstated-reason" blocks are each resolved: reason stated (from its BLOCK_RELEASE marker) +
  literal act, OR the item is drawn. A block with no reason is not a block (ruling #3).
- R12: the blocked count is a diagnostic, never a target — no item cleared by re-scoping it into nothing.
- One batched NTFY [ACT] points at the document, grouped so the director performs one act per channel.
- Acceptance (ruling): after the director executes the small set of acts, the blocked count falls
  measurably — published as a before/after count.

## Coverage mapping (doorbell requires stating what each ruling deliverable maps to)
- LITERAL_ACTS #1 (batched verbatim artifact) = LITERAL_ACT_LIST #1 (literal-act list by channel) → **this atom.**
- LITERAL_ACTS #3 (reasons + release conditions for unstated-reason blocks) = LITERAL_ACT_LIST #3 → **this atom** (second finding above).
- LITERAL_ACTS #4 (statement where a release mechanism does not exist) = LITERAL_ACT_LIST #2 → **this atom** (Channel B).
- LITERAL_ACTS #2 (release everything under existing authority + report) = LITERAL_ACT_LIST #4 → **sibling atom** `PLANNER_MINTED_self_authority_release_sweep_2026-07-29.md`.

**Propose-then-proceed window:** proceed by default (both rulings tagged **priority; proceed** /
**priority zero**; doc + code-verification only, reversible via git; releases only under authority
already held, handled by the sibling atom). Director-reserved walls untouched: this atom describes the
director acts, it does not perform them.

## Deliverable (verbatim, both rulings)
> One batched artifact: every remaining director-required act, verbatim and executable, each proven to work.
> The literal-act list, grouped by channel, with observable success criteria.
> Explicit statements where no release mechanism exists.
> Reasons and release conditions for the unstated-reason blocks.
