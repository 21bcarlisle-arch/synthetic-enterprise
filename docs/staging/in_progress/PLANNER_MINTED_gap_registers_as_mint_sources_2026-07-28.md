<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED] — GAP1: wire the published gap registers as planner mint sources, with the whole-set enumeration reporting them (2026-07-28)

**Source:** DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG_2026-07-28.md, deliverable 1.

**Provenance:** RUNG-7 planner mint from a ratified ruling's WORK THIS CREATES block (§2+§4 mechanism,
`DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27`). Minted this tick because the ruling
explicitly commands it (tag **proceed**) and grep-confirmed no existing PLANNER_MINTED_* doc or map
atom names the *gap-register-as-mint-source* wiring: the closest prior mint,
`PLANNER_MINTED_named_and_not_done_backlog_surface_2026-07-27` (`primary_state_scan.py::named_but_unminted`),
reads the **rulings'/steers' WORK THIS CREATES blocks** — NOT the published gap registers this ruling
names (simplifications register, fidelity ledger, board-spec reconciliations, disqualification battery,
claim-status placeholders, sanity findings, MODEL_ON_A_PAGE Timeframe 2, registered follow-ons). This
is the distinct, un-minted next step.

**Serves:** `DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG_2026-07-28` §1 (the published gap registers
are first-class mint sources) + §5 (coherence: the registers exist; nothing read them as work). The
acceptance the whole ruling turns on: *"a saturation claim is impossible while any published register
holds an open, un-triaged item."*

**Fidelity gained (one sentence):** none directly — this is a **draw-completeness / work-accounting**
fix that makes the machine's own published backlog *drawable*, closing the "saturation was a bookkeeping
artifact" hole the director named.

---
## Lane / level / deps
- **Lane:** `H_harness` (`background/` — an independent register reader + a new enumeration level in
  `background/supervisor.py::authorized_set_enumeration()`).
- **Target level:** `level_current 0 → level_target 3`.
- **Deps:** none — reads the *already-published* registers. Extends (does not import from) the LAW-C
  independent-reader pattern established by `primary_state_scan.py` (drift-guarded, imports nothing
  from `supervisor`, so it cannot restate the tick's own belief).
- **blocked_on (BUILD half):** the standing **harness-BUILD demotion** — `H_harness/close_to_learn` is
  off every open product front and fronts enforcement is ON, so `filter_build_candidates` excludes
  H-lane atoms from the BUILD draw (same wall HX1/HX2/HX3 sit behind). The executing act — a per-atom
  `BUILD_OPEN` in `gate_authorizations.jsonl` or an H-lane `FRONT_OPEN` — is **director-console-only**
  (R16: the ledger is authority; the agent cannot self-authorize a BUILD_OPEN). This is the same
  bootstrapping exception the HX* atoms name. **The DISCOVER/design half is drawable NOW** (no
  BUILD_OPEN needed): enumerate each register's on-disk path + parse schema, and specify the
  mint-source contract — see exit criterion (a).

## Exit criteria
- **(a) DISCOVER/design (drawable now):** a written contract naming, per register, its primary-state
  path and the field that marks a row OPEN: simplifications register (each entry + measured bound);
  fidelity ledger (cells at/below a naive baseline); board-spec reconciliations 001–006 (every PARTIAL
  and ABSENT row); disqualification-battery items not met; claim-status placeholders (designed-but-not-
  working — **starting with the carbon ledger, already map atom `E5_carbon_three_ledger`, idle 0→3**);
  standing sanity findings adjudicated real; MODEL_ON_A_PAGE Timeframe 2; registered follow-ons.
- **(b) BUILD:** an independent reader emits the OPEN-item residue from those registers, from PRIMARY
  state (no import from `supervisor`); a new `gap_register` level appears in
  `authorized_set_enumeration()` reading that residue (Y = drawable ⇒ rest illegitimate).
- **(c) R15 both-ways (mandatory):** neuter the register read (residue → `[]`) ⇒ the `gap_register`
  level reads empty **when open items demonstrably exist** (the control FIRES); restore ⇒ green. A
  second mutation: a register with one open row must flip the level to Y.
- **(d) FAIL-SAFE toward work:** a parse/read error on any register reads **drawable** (Rule-0
  direction — ambiguity forbids rest), matching `_safe()`'s existing contract.
- **Acceptance (ruling §): a rest/saturation claim is impossible while any published register holds an
  open, un-triaged item.** R12 non-negotiable: the *count* of open/closed gaps is a diagnostic on this
  line, never a score or headline.

## Walls untouched
- **No curriculum / R13:** this reads existing published state; it changes what is *drawable*, never a
  baseline or difficulty parameter.
- **No level self-bump (R16):** the atom lands at build-quality with `blocked_on: director_level_up`;
  this mint restores draw eligibility only.
- **Deliberate simplifications stay deliberate (§3):** GAP1 only *enumerates* open items; it never
  closes or reclassifies one — that is GAP2 (method) + GAP3 (ranked list), which return for
  ratification.
