# [PLANNER-MINTED] — GAP3: the first ranked gap list, marking which are deliberate-and-staying (2026-07-28)

<!-- SUPERVISOR_DRAW: self-drawable -->

**Source:** DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG_2026-07-28.md, deliverable 3 — **and now
`DIRECTOR_RULING_GAP_TRIAGE_RATIFIED_2026-07-28.md` deliverable 1** ("Apply the ratified taxonomy;
GAP3's first ranked list, with buckets and rationale"), which UNBLOCKS this atom.

**UNBLOCKED 2026-07-28 (ratification tick):** GAP2's triage-and-ranking method was **director-ratified**
(`DIRECTOR_RULING_GAP_TRIAGE_RATIFIED_2026-07-28.md` §1) and GAP1's register enumeration is available
as the written mint-source contract (`docs/design/GAP_REGISTER_MINT_SOURCE_CONTRACT.md`, GAP1 DISCOVER
half). Both preconditions now hold → **GAP3 is drawable NOW** (doc-only DISCOVER: apply the ratified
method to the registers per the GAP1 contract; the reader-BUILD residue is not required — the method
ranks over the enumerated registers directly).

**APPLY THE §1 RATIFICATION AS-RATIFIED (not the raw proposal):** the ranked list must honour the
ratified specifics — (i) the **asymmetric bound default**: below threshold *with* a measured bound →
`not-worth-the-complexity`; below threshold *without* one → `mint` at low rank (measure the gap); (ii)
the **faced-or-scheduled condition** on `deliberate-and-staying` (a simplification the harness has never
been exposed to is an untested assumption, not a proven scope choice — route it to `mint`, not
`deliberate-and-staying`); (iii) **board-battery weight = 3 mints regardless of composite**; (iv) both
**argue-back filters as filters-within-sources** — held SSP-baseline cells route to `blocked-on-director`
and are NEVER `mint` residue (reading them as mint re-opens a settled R12 goal-seek trap), standing
sanity findings are filtered on adjudication verdict so only adjudicated-real rows are residue.
**AMENDMENT §2 (binding on this list):** any row this list moves **INTO** `deliberate-and-staying`
**returns for director ratification** (batched, via the deliverable-3 inbound path); moves toward `mint`
are autonomous. So GAP3 PROPOSES the `deliberate-and-staying` set — it does not self-enact it.

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
