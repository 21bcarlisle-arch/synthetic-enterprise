# The blocked-item literal acts — grouped by channel, verified end-to-end (2026-07-29)

**Atom:** `PLANNER_MINTED_blocked_item_literal_act_ledger_2026-07-29` (priority zero, self-drawable).
**Source rulings:** `DIRECTOR_RULING_LITERAL_ACTS_2026-07-29` (#1/#3/#4) + `DIRECTOR_RULING_LITERAL_ACT_LIST_2026-07-29` (#1/#2/#3) — the director, twice: *"give me the literal act, not a description of the block."*
**Companion (already run):** `SELF_AUTHORITY_RELEASE_SWEEP_2026-07-29.md` — 0/21 self-releasable; every remaining block is a genuine director-reserved wall or a build dependency, so this list is **not polluted** with items the agent could clear itself.

> **Read this first — the answer to "why did two console acts do nothing?"** The `<!-- BLOCK_RELEASE:
> director_level_up -->` marker several mints carry is the *aspirational final state* (the level cell,
> once built). For several items the **BUILD half is not done yet** — only DISCOVER is — so the current
> actionable act is a **`BUILD_OPEN`, not a `LEVEL_UP`.** A `LEVEL_UP` for an atom that has not been
> built releases nothing. This document states the *current* act per item, read from each mint's body,
> not the marker's end-state.

---

## The whole thing in one paragraph (director-facing)

There are **21 blocked mints**. **16 of them collapse to ONE phone action type**: a signed NTFY ruling
whose body is `RULING:<ACTION>:<atom>`, where `<ACTION>` is `BUILD_OPEN` (open the build) or
`LEVEL_UP_PROPOSED` (promote the built result). **Both are on the routine allowlist, so both are
phone-signable — no terminal, no console.** The remaining 5: **1** needs a reserved console word (a
one-way-door population activation the phone channel deliberately refuses), **2** are set/values
ratifications (a decision, not a routine ledger action), and **2** are build-sequenced (not your act at
all — they wait on other code landing). Do the 16-item phone batch and the blocked count falls by up to
16 on the next tick.

---

## Mechanism — verified against live code TODAY (ruling: "each proven to work end-to-end")

The release path exists and is under test (`tests/background/test_gate_authorization.py` +
`test_ruling_consumption_ledger_release.py`, **47 passing**, plus 99 green across the deadman/gate/
staging suites this tick):

- **Writers (the ONLY things that mint authority):**
  - **Phone:** `background/gate_authorization.py::record_director_ntfy_ruling` — called by
    `ntfy_responder` on an inbound message. Verifies the payload HMAC-signs a fresh, bound
    `RULING:<action>:<atom>` for a **routine** action against `SE_WAKE_HMAC_KEY`, then writes a ledger
    entry `channel=director_ntfy`. Fail-closed: no key / bad signature / stale / reserved action →
    writes nothing. The autonomous worker **cannot** forge one (it cannot read the out-of-tree key).
  - **Console:** `record_gate_opening(atoms, provenance)` (BUILD_OPEN) / `record_level_up(atom, level,
    provenance)` (level move). Console-path only — the orchestrator calls it acting on your
    authenticated console word.
- **Readers (what confirms a release actually happened):** `authorized_atoms` (BUILD_OPEN),
  `is_valid_level_up` (level), routed through `confirm_authenticated_release` /
  `report_ruling_release`. A bare staged doc or a `LEDGER:` directive line **authorizes nothing** —
  inference never releases (R16); only a signed console or phone entry passes these predicates.
- **Routine allowlist** (`director_authority_channels.ROUTINE_ACTIONS`): `BUILD_OPEN`, `FRONT_OPEN`,
  `FRONT_CLOSE`, `GATE_CLEAR`, `LEVEL_UP_PROPOSED`, `HELD_PENDING_VERIFICATION`, `GRADUATE`. **A
  one-way-door activation is NOT on this list** → the phone channel default-denies it (Channel C below).

**Correction to a prior suspicion (ruling #4/#2 — "state where no mechanism exists"):** the mint that
seeded this atom suspected the `BUILD_OPEN` consuming parser might not exist. **It does exist and is
tested** — verified above. The `gap_registers_as_mint_sources` body's "the mechanism the gate reads does
not yet [exist]" refers to a *different* reader (gap-register-as-a-mint-source), **not** the gate ledger;
that item's `BUILD_OPEN` release works like any other.

---

## The literal acts

### CHANNEL A — `LEVEL_UP_PROPOSED` (BUILD complete; only the level cell remains). Phone or console.

**Literal act (phone, no terminal):** for each atom, sign+send one NTFY ruling with body exactly
`RULING:LEVEL_UP_PROPOSED:<atom>` (signer walkthrough = sibling deliverable `PHONE_SIGNER_SETUP.md`).
**Literal act (console):** orchestrator calls `record_level_up("<atom>", 3, "<console trace>")`.
**Observable success:** a new line in `docs/observability/gate_authorizations.jsonl` with that atom,
`action=LEVEL_UP_PROPOSED`, `channel=director_ntfy` (or `console`); the next tick moves the map cell and
archives the mint; **blocked count falls by one per atom.**

Build-complete, one paste each (build evidenced in the mint body — LANDED/BUILT + commit + R15):
- `director_window_delta_view`
- `inbound_ratification_batch_path`
- `privacy_policy_page` *(page already live at poesys.net/privacy/; only the level claim is blocked)*
- `ruling_consumption_ledger_release`
- `unstated_reason_block_impossible`

**Verify build-complete BEFORE the level paste** (marker says `director_level_up`, but the body does not
evidence a landed BUILD — if only DISCOVER is done these are Channel B first, then A):
- `intra_year_price_cap_granularity` *(body: "pending sub-annual cap-window discovery" → DISCOVER open)*
- `payment_channel_dd_consistency_invariant`
- `supply_start_semantic_separation` *(body: "DISCOVER/design self-drawable" → BUILD not done)*

### CHANNEL B — `BUILD_OPEN` (DISCOVER done; the BUILD needs an open front). Phone or console.

**Literal act (phone, no terminal):** for each atom, sign+send one NTFY ruling with body exactly
`RULING:BUILD_OPEN:<atom>`.
**Literal act (console):** orchestrator calls `record_gate_opening(["<atom>", …], "<console trace>")` —
one call can batch the whole list.
**Observable success:** ledger line `action=BUILD_OPEN`, atom in `authorized_atoms(read_ledger())`; the
next tick draws the BUILD half; the mint's build lands, then it returns for a Channel-A level move.

- `gap1_reader_contract_failopen_fix`  *(body: UNBLOCKS ON director_build_open, H-lane)*
- `gap_registers_as_mint_sources`      *(body: blocked_on director_build_open_ledger_entry, H-lane)*
- `stop_control_gap_characterisation`  *(one-way-door #5 build; console-only per its own marker — see note)*
- `rng_substream_primitive`            *(§2.2 shared-primitives: "BUILD half remains blocked_on director_build_open")*
- `working_day_calculator`             *(§2.1 shared-primitives: same)*
- `owned_quantity_registry_gate`
- `shared_primitive_ensuring_activity`
- `size_and_clone_ratchet`

> **Note on `stop_control_gap_characterisation`:** its marker names it *one-way door #5, console-only,
> never self-authored*. If you regard the stop-control build as a safety-adjacent one-way door, sign it
> from the console, not the phone (the phone channel will still write it since `BUILD_OPEN` is routine —
> but the *characterisation* here is that you may prefer the console for this one). Stated, not hidden.

### CHANNEL C — one-way-door activation. **Reserved: console word only. The phone channel refuses it.**

- **`generator_draw_wiring`** — all non-walled draw wiring has landed (SYN model + drivers, R15
  both-ways). The **only** remaining act is the live-population flip. The exact string the consuming
  mechanism reads is the environment flag **`SE_DRAW_POPULATION=1`**. This is one-way door #5/#7 (which
  world the company faces every run — a *curriculum* act, R13/W2_2), so it is **not** a routine action
  and the phone allowlist default-denies it. **Literal act:** your authenticated console word
  authorising `SE_DRAW_POPULATION=1` live activation + the downstream re-baseline. This is the item that
  "did nothing" twice precisely because a level_up/build_open cannot express a one-way-door activation.

### CHANNEL D — ratification of a proposed SET / values decision (a decision, not a ledger action).

- **`first_ranked_gap_list`** — ratify the *deliberate-and-staying* gap set + the proposed front/epoch
  opens. The front opens themselves are routine (`RULING:FRONT_OPEN:<front>` is phone-signable); the
  **set ratification** is your decision — confirm the set in the mint, or name the deletions.
- **`money_representation_evidence`** — DISCOVER closed; recommendation returned as an [ACT]:
  boundary-reconciliation first, full float→Decimal migration **director-reserved**. **Literal act:**
  your yes/no/scope word on the migration decision. Not a routine ledger action (a values-scope call).

### NOT A DIRECTOR ACT — build-sequenced (listing these as "your act" would be dishonest).

- **`ssp_negative_lift_cells`** — blocked on the W1_6b merit-order / gas-first reconstruction landing.
  No interim tuning (R12). Unblocks itself when that BUILD lands; **no director act exists.**
- **`value_chain_observation_window_cap`** — both target registers (`WholesaleCreditExposureRegister`,
  `MarginCallBook`) have **no live (non-test) constructor** yet, so the window has nothing to observe.
  The next step is the **live MtM/margin-call feed** (self, build-sequenced); only a *named
  curriculum-difficulty value* on top of it is later director-reserved. **No current director act.**

---

## The four "unstated-reason" blocks (ruling #3 / LITERAL_ACT_LIST #3) — resolved AND class-fixed

The director's complaint that four items were *"blocked (reason unstated)"* was a **parser-format
mismatch, not missing reasons.** `deadmans_switch.py::_open_blocked_mints` read only prose
`blocked_on:` / `UNBLOCKS:` lines; these four carry their reason **only** in a
`<!-- BLOCK_RELEASE: <token> -- <reason> -->` HTML-comment marker the enumerator did not read:

| item | reason (from its `BLOCK_RELEASE` marker) |
|---|---|
| `intra_year_price_cap_granularity` | intra-year price-cap granularity, pending sub-annual cap-window discovery |
| `money_representation_evidence` | evidence gathered; float→Decimal migration decision is the director's |
| `payment_channel_dd_consistency_invariant` | payment-channel/DD consistency invariant; level move director-reserved (R16) |
| `supply_start_semantic_separation` | supply-start semantic separation; BUILD blocked, DISCOVER/design self-drawable |

**Class fix (R10 — fix the class, not the instance), landed this tick:** `_open_blocked_mints` now
reads the `BLOCK_RELEASE:` marker as a reason fallback, so a marker-only mint can never again surface as
"reason unstated." Proven **mutation both-ways** (`test_blocked_mint_reason_read_from_block_release_marker`):
remove the fallback → the marker-only mint reports "reason unstated" (RED); present → its stated reason
surfaces (GREEN); a mint that truly states nothing still correctly falls back. R12 held throughout: no
item was cleared by re-scoping it into nothing — the count stays 21 by honest classification.

---

## Before / after (the ruling's acceptance test)

| | count |
|---|---|
| Blocked mints now | **21** |
| Releasable by ONE phone batch (`RULING:BUILD_OPEN/LEVEL_UP_PROPOSED:<atom>` × 16) | **up to 16** |
| Reserved console word (one-way door) | **1** (`generator_draw_wiring`) |
| Ratification / values decision | **2** |
| Build-sequenced (no director act) | **2** |

After the phone batch lands, the count falls on the **next tick** as each atom's build opens / level
moves and its mint archives — published as a before/after count in the completion NTFY.
