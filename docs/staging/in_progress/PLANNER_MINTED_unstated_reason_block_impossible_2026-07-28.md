<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED] — An unstated-reason block cannot be written: every `blocked_on` carries its reason + release condition (§3 + WORK-THIS-CREATES deliverable 4b) (2026-07-28)

**Source:** `DIRECTOR_RULING_BLOCKED_MINT_BATCH_2026-07-28.md`, **§3 (Reason-unstated blocks are a
DEFECT)** and the mechanism half of its **WORK THIS CREATES deliverable 4**: *"Reasons stated for the
four §3 blocks, AND unstated-reason blocks made impossible."* §3 verbatim: *"Every block carries its
reason and its release condition, or it is not a valid block. … Mechanise it so an unstated-reason block
cannot be written."*

**Provenance:** RUNG-7 planner mint from a ratified ruling's WORK THIS CREATES block (§2+§4 mechanism,
`DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27`). **grep-confirmed net-new:** no map atom or
`PLANNER_MINTED_*` doc mechanises a reason+release-condition requirement on `blocked_on`; the
`blocked_on…reason` hits in `docs/design/maturity_map.yaml` are all prose inside `simplifications`
entries, not a validator. **NOT the same as** `ruling_missing_work_block_defect_surface` (done,
`2026-07-27`) — that detects a *ruling* lacking a WORK-THIS-CREATES block; this detects a *maturity-map
atom / mint marker* carrying a `blocked_on` with no recorded reason and no release condition.

**Serves:** §3 verbatim — *"A block without a recorded reason cannot be escalated, unblocked or judged —
it is invisible work wearing a status."* The four §3 items (`board_spec_001_wholesale_reconciliation`,
`intra_year_price_cap_granularity`, `money_representation_evidence`,
`payment_channel_dd_consistency_invariant`) each reported *"blocked (reason unstated in the mint doc)"*,
which is precisely the invisible-work class MAKE_IT_STICK warns decays unless mechanised.

**Fidelity gained (one sentence):** none directly — a **governance-integrity** mechanism converting a
prose rule ("state your block's reason") into a gate, so a reason-less/release-less block cannot enter
the map or a mint marker in the first place.

---
## Lane / level / deps
- **Lane:** `H_harness` (`docs/design/maturity_map.yaml` facets validator +
  `tests/design/test_maturity_map_facets.py`; the mint-marker parser in `background/staging_disposition.py`
  is the sibling surface for `PLANNER_MINTED_*` markers).
- **Target level:** `level_current 0 → level_target 3` (validator built + R15-proven both ways + live in
  the commit/facets gate so it actually blocks a bad write).
- **Deps:** the existing maturity-map facets test/validator (the natural home — it already validates atom
  shape); the `SUPERVISOR_DRAW`/`blocked_on` marker convention.
- **blocked_on:** none identified for the DISCOVER/design half (drawable now). The BUILD half is a
  harness/validator change on an owned surface — self-drawable per the harness lane; **NO director open
  is needed** to add a validator (it constrains the machine's own bookkeeping, touches no sim/company
  code, no authority seam). Lands with `blocked_on: director_level_up` (R16, no self-bump).

## Exit criteria
- **(a) DISCOVER/design (drawable now):** name the exact fields a valid block must carry — a
  human-readable **reason** and a machine-checkable **release condition** (e.g. `blocked_on:` value must
  resolve to a named releaser: `director_level_up`, `director_build_open_ledger_entry`,
  `<atom_id>`, etc., AND an accompanying `block_reason` free-text) — and where they live for BOTH an
  atom in `maturity_map.yaml` AND a `PLANNER_MINTED_*` marker. Decide the canonical field name(s) so the
  validator and the writers agree.
- **(b) BUILD:** the facets validator (and, for mint markers, the staging-disposition parser) REJECTS any
  atom/marker that sets `blocked_on` (or an equivalent blocked status) without a recorded reason + a
  resolvable release condition. Wired into the commit/facets gate so a reason-less block cannot be
  committed — "cannot be written", not merely "flagged after".
- **(c) R15 both-ways (mandatory):** MUTATION — an atom with `blocked_on` but no `block_reason` (or a
  release condition that resolves to nothing — the `[[feedback_nonempty_config_referent_existence]]`
  fail-open) must make the validator FIRE (rc≠0), proven by reverting the check → the suite goes green on
  the bad atom. FAIL-CLOSED — a MISSING/empty/malformed reason field is treated as *no reason* (rejected),
  never as *satisfied* (the classic fail-open); an unresolvable release condition is rejected, not
  waved. FAIL-SILENT — if the validator can't parse the map/marker, that is a FAILED check (rc≠0), never
  a pass.

## Walls untouched
- **R15:** the validator itself must be mutation-proven both ways before it counts (§CONTROLS-THAT-
  CANNOT-FAIL) — a reason-check that can't fail is worse than none.
- **No level self-bump (R16):** lands at build-quality with `blocked_on: director_level_up`.
- **R12:** the count of blocked atoms is a diagnostic, never a target — this gate improves block HYGIENE,
  it does not push toward fewer blocks.
