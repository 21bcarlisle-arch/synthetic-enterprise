# [PLANNER-MINTED / DEP-BLOCKED] — GAP3: the first ranked gap list, marking which are deliberate-and-staying (2026-07-28)

<!-- SUPERVISOR_DRAW: blocked -->

**Source:** DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG_2026-07-28.md, deliverable 3.

**UNBLOCKS ON:** GAP2's triage-and-ranking method is director-**ratified** (the method must exist and
be approved before a list can honestly apply it) AND GAP1's register enumeration is available (the
residue to rank over). Both are minted this same tick; GAP3 is the third-in-sequence product and is
parked BLOCKED until they land — surfaced here so the enumeration counts it, never drawn prematurely.

**Provenance:** RUNG-7 planner mint from the ruling's WORK THIS CREATES block. No existing atom/mint
produces a ranked gap list. Distinct from GAP1 (enumerate) and GAP2 (method): GAP3 *applies* the
ratified method to the live enumeration to produce the first ranked list.

**Serves:** `DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG_2026-07-28` §2–§3 (*"the first ranked gap
list, marking which are deliberate-and-staying"*, with reasoning; deliberate simplifications stay
deliberate; honest reds credited).

**Fidelity gained (one sentence):** none directly — the **first prioritised backlog** the machine
ranks its own published gaps into, the artefact §5 says the registers were always implicitly holding.

---
## Lane / level / deps
- **Lane:** `L3 DISCOVER` (doc-only — `docs/design/FIRST_RANKED_GAP_LIST.md`, or a derived surface if
  the ratified method calls for one).
- **Target level:** ranked-list artefact → **returns for ratification** (it embodies the same scope
  judgement as GAP2 — which rows are deliberate-and-staying).
- **Deps:** `GAP2_gap_triage_ranking_method` (director-ratified) + `GAP1_gap_registers_as_mint_sources`
  (enumeration available). blocked_on: **GAP2 ratification**.

## Exit criteria
- A ranked list applying the ratified GAP2 method to the GAP1 enumeration. **Every** enumerated gap
  appears with exactly one class tag: `mint` · `deliberate-and-staying` (with its argument) ·
  `blocked-on-director` (with the reserved-wall decision it needs) · `not-worth-the-complexity` (with a
  better-measured bound).
- The `mint` rows are **ordered** by the ratified ranking dimensions; the top rows become planner mint
  sources ranked alongside everything else (§1).
- The `deliberate-and-staying` rows carry an **explicit argument** for staying — not a silent omission
  (§3: closing/reclassifying one silently is a claim-status defect).
- **R12 non-negotiable, restated in the artefact:** the count of `mint` vs `deliberate` rows is a
  diagnostic; it is never presented as a score, a target, or a headline, and no gap is reclassified to
  move a count.
- **Returns for ratification** (scope judgement); the list is proposed to the director, not
  self-enacted into closures.

## Walls untouched
- **R13 / reserved walls (§3):** any gap whose closure needs a director decision is tagged
  `blocked-on-director` and escalated as one, never worked around.
- **Honest reds credited (§3):** a gap examined and left open with a better-measured bound is a
  legitimate `not-worth-the-complexity` / bounded outcome, recorded as such — not a failure.
