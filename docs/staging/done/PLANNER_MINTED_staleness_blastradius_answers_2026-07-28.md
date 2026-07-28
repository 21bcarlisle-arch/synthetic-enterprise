<!-- SUPERVISOR_DRAW: blocked -->
> **EXECUTED + COMPLETE 2026-07-28** (planner tick) → `docs/design/GAP_TRIAGE_STALENESS_AND_BLASTRADIUS.md`.
> Both answers landed **AUTONOMOUS** (no return-for-ratification): (a) staleness = a read-time filter in
> GAP1's reader, NOT a fifth taxonomy bucket (evidence-gated E1/E2/E3, burden-of-proof on `stale`); (b)
> blast-radius risk = deliberately FOLDED, left as-is, with a named un-fold trigger at go-live. No blocked
> residue, no director action pending → this mint is DONE (archived to docs/staging/done/).
# [PLANNER-MINTED] — GAP-Q: answer the director's two triage questions (staleness disposition; blast-radius as risk) in one report (2026-07-28)

**Source:** `DIRECTOR_RULING_GAP_TRIAGE_RATIFIED_2026-07-28.md`, **deliverable 4** ("Answers to (a)
staleness and (b) blast-radius, in one report"), from §3 (the two QUESTIONS the director poses as
*"your judgement, not prescriptions"*).

**Provenance:** RUNG-7 planner mint from a ratified ruling's WORK THIS CREATES block (§2+§4 mechanism,
`DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27`). grep-confirmed no existing
`PLANNER_MINTED_*` doc or map atom answers the staleness-disposition / blast-radius-as-risk questions —
they are net-new, posed only by this ratification ruling. **NOT re-minted** (distinct from GAP1
enumerate / GAP2 method / GAP3 ranked list).

**Serves:** `DIRECTOR_RULING_GAP_TRIAGE_RATIFIED_2026-07-28.md` §3(a)+§3(b). Closes the two open
judgement calls the director left to the agent, so the ratified taxonomy has **total coverage** with
no undisposed class (staleness) and a **stated** risk treatment (blast-radius).

**Fidelity gained (one sentence):** none directly — a **triage-method completeness** artefact that
removes the one coverage hole (a register entry that is no longer true fits none of the four buckets)
and makes the value/risk folding explicit rather than implicit.

---
## Lane / level / deps
- **Lane:** `L3 DISCOVER` — doc-only (`docs/design/GAP_TRIAGE_STALENESS_AND_BLASTRADIUS.md`, or an
  appendix to `docs/design/GAP_TRIAGE_AND_RANKING.md`). Drawable NOW (THREE_LANES L3: doc-only DISCOVER
  is always available — no BUILD_OPEN, no front).
- **Target level:** report artefact → **returns for director ratification** on the ONE part that is a
  method change: if the answer to (a) is a **fifth disposition** (not "handled by GAP1's staleness
  filter"), that extends the ratified taxonomy and is a scope call (same class as GAP2), so it is
  proposed, not self-enacted. If the answer is "already handled by GAP1's reader-time staleness filter,"
  no taxonomy change → autonomous. The blast-radius answer (b) is descriptive (state whether risk is
  separate or folded) → autonomous.
- **Deps:** none to write the report. It reasons over the ratified method (`GAP_TRIAGE_AND_RANKING.md`)
  and the GAP1 mint-source contract (`GAP_REGISTER_MINT_SOURCE_CONTRACT.md`), both of which exist.

## Exit criteria
- A single report answering, with reasoning **and evidence from the live registers**:
  - **(a) Staleness disposition.** Decide and argue: is a register entry that is *no longer true*
    (superseded / already-fixed / describing a since-removed component) handled by **GAP1's reader-time
    staleness filter** (a read-time drop, so it never reaches the taxonomy), OR does it need a **fifth
    disposition** (`stale`/`superseded`) with its own evidence test? Name the evidence test either way
    (what proves an entry stale — a passing test over the described component, a commit that removed it,
    a supersedence pointer). State how this interacts with the ratified **ambiguous-defaults-to-mint**
    rule so a dead gap does NOT become phantom work. **If a fifth disposition: RETURN FOR RATIFICATION.**
  - **(b) Blast-radius as risk.** State plainly whether risk is scored **separately** anywhere in the
    ordering, or **deliberately folded** into blast-radius on the argument that value and risk move
    together for these gaps. Per the director's steer, if the honest answer is "folded for simplicity,"
    say so and **leave it** — this is explicitly *not worth a mechanism*.
- **R12 restated:** neither answer introduces a gap-count target; the count stays a diagnostic.
- The report is a **single document** (§3 requires "in one report"), inspectable from published state.

## Walls untouched
- **No R13 / curriculum / generator move:** the report reasons about triage bookkeeping only.
- **No self-extension of the taxonomy:** a fifth disposition, if proposed, is HELD for director
  ratification (§2 direction-of-risk: adding a disposition that can *retire* honest reds is the
  scope-drift direction that returns).
