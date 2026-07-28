<!-- SUPERVISOR_DRAW: blocked -->
<!-- BLOCK_RELEASE: director_level_up -- both surfaces (map-atom facets gate + sibling mint-marker hygiene gate) BUILT + R15-proven + wired; the atom lands at build-quality, the level move is the director's (R16, no self-bump) -->
# [PLANNER-MINTED] — An unstated-reason block cannot be written: every `blocked_on` carries its reason + release condition (§3 + WORK-THIS-CREATES deliverable 4b) (2026-07-28)

> **[IN-PROGRESS DISPOSITION 2026-07-28 (UPDATED-3) — BOTH SURFACES NOW BUILT. SIBLING (mint-marker) hygiene gate BUILT this tick → marker FLIPPED self-drawable→blocked; only the director level move remains (R16).**
> **SIBLING BUILT (2026-07-28):** `background/staging_disposition.mint_block_hygiene_violations()` +
> the `<!-- BLOCK_RELEASE: <releaser> -- <reason> -->` canonical marker (dedicated + non-fragile, R3 —
> not a prose `blocked_on:` sniff a quote could false-trip). Every blocked/unmarked `PLANNER_MINTED_*`
> parked in `in_progress/` was backfilled with a resolvable releaser + reason (25 docs incl. this one);
> the live scan is GREEN. R15 both-ways in `tests/background/test_staging_disposition.py` (mutation:
> missing marker / unresolvable releaser / empty reason all FIRE; fail-closed on missing/empty;
> fail-silent on unreadable; negative controls pass; self-drawable exempt). WIRED into the commit gate
> via `tools/pre_commit_test_gate.py` (a staged `docs/staging/in_progress/PLANNER_MINTED_*.md` now runs
> the hygiene test) so a reason-less/release-less mint marker CANNOT be committed — "cannot be written",
> not "flagged after". SUPERSEDES the sub-step note below.

> **[SUPERSEDED — PRIOR DISPOSITION 2026-07-28 (UPDATED) — PRIMARY (map-atom) SURFACE BUILT + LIVE-WIRED; SIBLING (mint-marker) surface is the remaining drawable sub-step → marker stays self-drawable.**
> The DISCOVER/design half is EXECUTED → `docs/design/UNSTATED_REASON_BLOCK_IMPOSSIBLE_DISCOVER.md`.
> Canonical fields decided: **`block_reason`** (non-empty free text) + **`blocked_on`** (must resolve to a
> known releaser or an existing atom id).
>
> **BUILT THIS TICK (2026-07-28) — the load-bearing structured surface, done + proven + green:**
> - `check_block_hygiene(atoms)` + `KNOWN_RELEASER_TOKENS` live in
>   `tests/design/test_maturity_map_facets.py` (mirrors `check_value_stream_hygiene`): every atom with a
>   non-null `blocked_on` MUST carry a non-empty `block_reason` AND a `blocked_on` resolving to a canonical
>   releaser token or an existing atom id.
> - **Backfill DONE FIRST (wedge precondition honoured):** `block_reason` added to ALL 21 live blocked map
>   atoms (view-only field — the draw does not read it, so the backfill cannot alter the draw); no
>   draw-read `blocked_on` value changed.
> - **Live map GREEN then WIRED:** `test_live_map_block_hygiene()` passes over 146 atoms and
>   `check_block_hygiene` is wired into the `_main()` phase-close/facets gate (`MATURITY-MAP FACET
>   HYGIENE: PASS (146 atoms)`, rc=0) — so a reason-less/unresolvable block now CANNOT be committed.
> - **R15 both-ways proven:** MUTATION (reason-less block, unresolvable release condition, missing-referent
>   atom-id all FIRE) + FAIL-CLOSED (empty/whitespace reason rejected, never satisfied) + FAIL-SILENT
>   (non-dict atom entry is a violation) + negative controls (well-formed block, atom-id releaser,
>   unblocked atoms all pass). 19/19 in `test_maturity_map_facets.py`.
>
> **REMAINING drawable sub-step (why the marker STAYS self-drawable — park-honesty: a genuinely drawable
> step remains, so NOT flipped to blocked):** the **sibling mint-marker check** in
> `background/staging_disposition.py`, scoped to `PLANNER_MINTED_*.md` docs carrying
> `<!-- supervisor_draw: blocked -->`, requiring a machine-legible `blocked_on:` line resolving to a
> releaser (reuse `KNOWN_RELEASER_TOKENS`) + a non-empty reason — with its OWN R15 both-ways. **⚠ that
> surface needs a structured-field backfill first:** ~5 live blocked `PLANNER_MINTED_*` docs state their
> reason in PROSE but carry no machine-legible `blocked_on:` releaser line
> (`board_spec_001_wholesale_reconciliation`, `first_ranked_gap_list`, `money_representation_evidence`,
> `ssp_negative_lift_cells`, `value_chain_observation_window_cap` — two of them are §3's own four named
> items); the scope must EXCLUDE director/advisor SOURCE docs that merely quote the marker (they are
> inbound instructions, not blocks-wearing-a-status). Do the marker backfill FIRST, prove the live
> in_progress scan green, THEN wire — same discipline as the map, to avoid a staging-surface wedge
> (`[[feedback_control_false_positive_jams_pipeline]]`). Not rushed at tail-of-tick per
> `[[SELF_INTERRUPT_DISCIPLINE]]`.
>
> When the sibling lands, flip this marker to blocked with `blocked_on: director_level_up` (R16, no
> self-bump — the atom lands at build-quality; the L3 level move is the director's).

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
