# DISCOVER — An unstated-reason block cannot be written: every `blocked_on` carries a reason + a resolvable release condition (atom `unstated_reason_block_impossible`)

**Executes the DISCOVER/design half of** `docs/staging/in_progress/PLANNER_MINTED_unstated_reason_block_impossible_2026-07-28.md`
(source: `DIRECTOR_RULING_BLOCKED_MINT_BATCH_2026-07-28.md` §3 + WORK-THIS-CREATES d4b).
**Lane:** H_harness. **This doc is doc-only (drawable now); the BUILD half is a harness validator on an
owned surface — self-drawable next (see §5).**

---
## 1. What §3 requires (verbatim)
*"Every block carries its reason and its release condition, or it is not a valid block. … A block without
a recorded reason cannot be escalated, unblocked or judged — it is invisible work wearing a status.
Mechanise it so an unstated-reason block cannot be written."* The four §3 items
(`board_spec_001_wholesale_reconciliation`, `intra_year_price_cap_granularity`,
`money_representation_evidence`, `payment_channel_dd_consistency_invariant`) each reported *"blocked
(reason unstated in the mint doc)"* — the invisible-work class MAKE_IT_STICK warns decays unless
mechanised into a gate.

## 2. Two surfaces a block can live on
1. **A maturity-map atom** (`docs/design/maturity_map.yaml`): structured YAML, has `blocked_on` today.
2. **A `PLANNER_MINTED_*` mint marker** (`docs/staging/**`): prose `.md`, carries `**blocked_on:**` in
   prose + a `<!-- SUPERVISOR_DRAW: blocked -->` marker (see `background/staging_disposition.py`).

The map atom is the **primary, machine-structured** surface and the natural validator home
(`tests/design/test_maturity_map_facets.py` already validates atom shape — value_stream + coupling). The
mint marker is the **sibling** surface (its parser is `staging_disposition.py`).

## 3. Canonical fields a valid block MUST carry
Decided field names (validator and writers agree on these):

- **`blocked_on`** — the **release condition**, a machine-checkable value that MUST resolve to a **known
  releaser**. Canonical releaser set:
  - `director_level_up` — released by a director/twin `LEVEL_UP_PROPOSED`/`LEVEL_UP_TWIN` ledger entry.
  - `director_build_open` / `director_authority_seam_signoff` — released by a director-console/phone
    `BUILD_OPEN` ledger entry (ties to `[[ruling_consumption_ledger_release]]`).
  - `build_open` / `front_open:<front>` — released by the corresponding ledger action.
  - **`<atom_id>`** — released when that named atom (which MUST exist in the map) advances; the
    referent-existence check (`[[feedback_nonempty_config_referent_existence]]`): a `blocked_on` naming a
    non-existent atom is UNRESOLVABLE → rejected, not waved.
- **`block_reason`** — a **human-readable, non-empty** free-text reason (why it is blocked). Missing /
  empty / whitespace-only is treated as *no reason* → rejected (never as *satisfied*).

An atom with `blocked_on` set but **no** `block_reason`, OR whose `blocked_on` resolves to **nothing**
(not in the releaser set and not an existing atom id), is an **invalid block** → validator FIRES (rc≠0).
An atom with **no** `blocked_on` is unconstrained (this gate governs block HYGIENE only, never block
count — R12).

## 4. Where the fields live per surface
- **Map atom:** `blocked_on: <releaser>` and `block_reason: "<why>"` as sibling YAML keys on the atom.
- **Mint marker:** the existing `<!-- SUPERVISOR_DRAW: blocked -->` marker must be accompanied by a
  machine-parseable `blocked_on:` line resolving to a known releaser **and** a non-empty reason. (The
  map-atom validator is the primary R15-proven control; the mint-marker check is the sibling extension so
  `[[feedback_audit_sibling_half_for_hardened_class]]` — harden the sibling half of the same class.)

## 5. BUILD half — scope + level
- **Home:** a new pure `check_block_hygiene(atoms) -> list[str]` in `test_maturity_map_facets.py`
  (mirrors `check_value_stream_hygiene`), wired into the `_main()` phase-close gate CLI and a
  `test_live_map_block_hygiene()` over the live map. Sibling parser check added to
  `staging_disposition.py` for mint markers.
- **Self-drawable:** a validator constraining the machine's OWN bookkeeping (touches no sim/company code,
  no authority seam) is harness-lane self-drawable — **NO director open needed** for the build itself.
  Lands `level_current 0 → level_target 3` with `blocked_on: director_level_up` (R16, no self-bump).
- **⚠ Backfill precondition (flagged so the BUILD tick does not wedge the gate):** turning this on will
  RED the live suite for **every existing** map atom / mint marker that currently carries a bare
  `blocked_on`. The BUILD step MUST first sweep the live map + open mint markers and add `block_reason` +
  a resolvable `blocked_on` to each, in the SAME increment as the validator — else the commit/facets gate
  wedges publishing (`[[feedback_control_false_positive_jams_pipeline]]`,
  `[[feedback_live_snapshot_test_wedges_on_legit_progress]]`). Do the backfill first, prove the live map
  green, then wire the check into the gate.

## 6. R15 both-ways (mandatory before it counts)
- **MUTATION:** an atom with `blocked_on` but no `block_reason` (or a release condition resolving to
  nothing) must make the validator FIRE (rc≠0); reverting the check → suite goes green on the bad atom.
- **FAIL-CLOSED:** a MISSING/empty/malformed reason is treated as *no reason* (rejected), never *satisfied*
  (the classic fail-open); an unresolvable `blocked_on` is rejected, not waved
  (`[[feedback_nonempty_config_referent_existence]]`).
- **FAIL-SILENT:** if the validator can't parse the map/marker, that is a FAILED check (rc≠0), never a
  pass.

## 7. Walls untouched
R15 — the validator itself must be mutation-proven both ways before it counts (a reason-check that can't
fail is worse than none). No level self-bump (R16) — BUILD lands `blocked_on: director_level_up`. R12 —
this gate improves block HYGIENE; the count of blocked atoms is a diagnostic, never a target.
Distinct from done `ruling_missing_work_block_defect_surface` (that = a *ruling* lacking a
WORK-THIS-CREATES block; this = a *map atom / mint marker* carrying a reason-less block).

---

## 8. SIBLING (mint-marker) surface — BUILT 2026-07-28

The map-atom half (§5–§7 above) landed 2026-07-28 (commit c8f6ef52f). The mint-marker half — the
remaining self-drawable sub-step — landed this tick.

**Canonical marker (dedicated + structured, R3):** a `PLANNER_MINTED_*.md` parked in `in_progress/`
that the draw treats as blocked carries
`<!-- BLOCK_RELEASE: <releaser> -- <reason> -->`. Chosen over parsing the prose `blocked_on:` lines
(which several docs QUOTE from *other* atoms — a free-form sniff would false-trip on the quote), it
mirrors the existing `<!-- SUPERVISOR_DRAW: ... -->` convention the same worker already writes.

**Why a marker, not a `block_reason` field like the map:** a bare YAML atom has no prose, so it needs
an explicit reason field; a mint is a whole document whose reason is structurally present (title +
Serves + FRAME). The field genuinely AT RISK on a mint is the machine-legible RESOLVABLE RELEASE
CONDITION — so the marker carries both (releaser before the dash, reason after) and the check enforces
resolvability of the releaser + non-emptiness of the reason.

**Releaser vocabulary (`MINT_RELEASER_TOKENS`):** the map's `KNOWN_RELEASER_TOKENS` (pinned as a
subset by `test_mint_releaser_tokens_superset_of_map`) PLUS two mint-specific releasers the map atoms
do not use — `propose_then_proceed` (a self-releasing window) and `director_ratification` (a director
decision beyond a level/build move, e.g. ratifying a ranked gap set or a money-type migration) — OR an
existing maturity-map atom id (an atom-landing releaser, e.g. `ssp_negative_lift_cells` →
`W1_6b_merit_order_reconstruction`).

- **Detector:** `background/staging_disposition.mint_block_hygiene_violations()` — report-only, never
  raises. FAIL-CLOSED (missing marker / unresolvable releaser / empty reason → violation); FAIL-SILENT
  (an undecodable doc is a FAILED check). A self-drawable mint is exempt (it is not a block); an
  UNMARKED mint is fail-closed to blocked (matching the draw) and must carry the release marker.
- **Backfill DONE FIRST (wedge precondition honoured):** all 25 blocked/unmarked `PLANNER_MINTED_*`
  docs live in `in_progress/` (incl. this atom's own doc, flipped self-drawable→blocked) were given a
  resolvable releaser + reason; the live scan is GREEN.
- **Wired into the commit gate:** `tools/pre_commit_test_gate.py` now runs the hygiene test whenever a
  `docs/staging/in_progress/PLANNER_MINTED_*.md` is staged — so a reason-less/release-less mint marker
  CANNOT be committed ("cannot be written", not "flagged after"), the sibling of the LEVEL_SURFACE
  mechanism. End-to-end proven: staging a marker-less mint → gate rc=1; clean tree → rc=0.
- **R15 both-ways:** `tests/background/test_staging_disposition.py` (13 mint tests) + the gate-trigger
  tests in `tests/tools/test_pre_commit_test_gate.py`. Mutation: missing marker / unresolvable releaser
  / empty reason / undecodable doc all FIRE; negative controls (well-formed block, atom-id releaser,
  propose-then-proceed, self-drawable exempt) all pass; the map cannot be read → an atom-id releaser
  resolves to nothing (fail-closed).

Only the director L0→L3 level move (R16, no self-bump) remains on the atom.
