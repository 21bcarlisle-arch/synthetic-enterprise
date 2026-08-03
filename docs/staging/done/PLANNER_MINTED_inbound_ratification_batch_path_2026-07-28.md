<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- BLOCK_RELEASE: propose_then_proceed -- was 'director_level_up', an act abolished 2026-07-29 and swept 2026-08-03: propose, record, act. Original note: BUILD half (b)/(c) is DONE and committed (background/inbound_ratification.py + 23-test R15-both-ways suite); the ONLY remaining work is the director's LEVEL move 0->3 (R16: the agent cannot self-bump; it lands at build-quality with blocked_on director_level_up). RELEASE CONDITION: a director/console LEVEL_UP for this atom, at which point it closes and archives to done/. -->
<!-- BUILD HALF (b)/(c) DONE 2026-07-28 (worker tick, commit pending) — background/inbound_ratification.py
     + tests/background/test_inbound_ratification.py (23 tests, R15 both-ways PROVEN: MUTATION neuters the
     hold → into-move silently lands as deliberate-and-staying (test_held_into_move_does_not_silently_land
     reds); PASS-THROUGH out-toward-mint autonomous, no escalation; FAIL-SAFE ambiguous→held). Marker
     flipped self-drawable→blocked: the only remaining work is the R16 director LEVEL move (0→3).
     UNBLOCKS ON: director_level_up. -->
<!-- RELEASED 2026-07-28: director console BUILD_OPEN (ruling_consumption_authority_seam_signoff) — implements the item-2 transcription convention (parse LEDGER: BUILD_OPEN/FRONT_OPEN/LEVEL_UP_PROPOSED → release-or-raise-ONE-[ACT], never sit silent) that this ruling RATIFIES; recorded in docs/observability/gate_authorizations.jsonl (channel=console). BUILD half now drawable. Level move stays director_level_up (R16). -->
> **DISCOVER/design half EXECUTED 2026-07-28** (planner tick) → `docs/design/INBOUND_RATIFICATION_BATCH_PATH_CONTRACT.md`
> (the batched inbound-ratification contract, exit criterion (a)). Marker flipped self-drawable→blocked:
> the only remaining work is **the BUILD half (b)/(c), blocked_on: director_build_open_ledger_entry**.
> **The BUILD half (b)/(c) is blocked_on:
> director_build_open_ledger_entry** — an `H_harness` `BUILD_OPEN`/`FRONT_OPEN` in
> `gate_authorizations.jsonl` (R16: ledger is authority; the agent cannot self-authorize a BUILD_OPEN).
> Note §4's build-open in the sibling ruling names the GAP1 *reader* contract specifically — it does
> NOT cover this distinct mechanism, which needs its own open.

# [PLANNER-MINTED] — GAP-M2: the inbound-ratification path for gap moves INTO `deliberate-and-staying`, batched (2026-07-28)

**Source:** `DIRECTOR_RULING_GAP_TRIAGE_RATIFIED_2026-07-28.md`, **deliverable 3** ("The inbound-
ratification path for moves into `deliberate-and-staying`, batched"), from §2 (AMENDMENT — asymmetric
ratification on bucket moves).

**Provenance:** RUNG-7 planner mint from a ratified ruling's WORK THIS CREATES block (§2+§4 mechanism,
`DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27`). grep-confirmed no existing
`PLANNER_MINTED_*` doc or map atom builds a bucket-move ratification path — net-new, created only by
this ruling's §2 amendment. **NOT re-minted:** distinct from GAP1 (register enumeration), GAP2 (the
method), GAP3 (the first list applying it), and GAP-Q (the two-question report). This is the *return
channel* the ratified method needs for its one non-autonomous move-direction.

**Serves:** `DIRECTOR_RULING_GAP_TRIAGE_RATIFIED_2026-07-28.md` §2. The amendment establishes an
**asymmetry**: moving a gap **INTO** `deliberate-and-staying` is a scope claim in the direction where
honest reds quietly vanish → it **returns for director ratification**; moving a gap **OUT** toward
`mint`, or between the other three buckets, is **autonomous**. Without a mechanism that (i) detects the
into-`deliberate-and-staying` direction and (ii) *batches* those requests rather than escalating singly,
the amendment is prose-only and will decay (MAKE_IT_STICK: convert policy to mechanism or accept it
evaporates).

**Fidelity gained (one sentence):** none directly — a **governance-integrity** mechanism that makes the
one direction of scope-drift (retiring an honest red as "deliberate") impossible to enact silently.

---
## Lane / level / deps
- **Lane:** `H_harness` (`background/` — a small classifier + batched-escalation path, most naturally an
  extension of the existing escalation/`[ACT]` machinery and the twin route-blocking-decision surface).
- **Target level:** `level_current 0 → level_target 3` (built + R15-proven both ways + live).
- **Deps:** GAP2 method (ratified — defines the buckets) + GAP3 (produces the actual into-moves to
  batch). The DISCOVER/design half needs neither running; it specifies the contract over the ratified
  bucket set.
- **blocked_on (BUILD half):** `director_build_open_ledger_entry` — the standing harness-BUILD demotion
  (H_harness is off every open product front; `filter_build_candidates` excludes it). The executing act
  is a per-atom `BUILD_OPEN` or an H-lane `FRONT_OPEN` in `gate_authorizations.jsonl` (director/advisor
  console; R16). **The DISCOVER/design half is drawable now** (no BUILD_OPEN needed).

## Exit criteria
- **(a) DISCOVER/design (drawable now):** a written contract for the batched inbound-ratification path
  specifying — the trigger (a triage output, e.g. GAP3, classifies a row **into** `deliberate-and-
  staying` that was not already director-ratified as such); the **batching rule** (accumulate into ONE
  escalation, not N singles — §2 "Batch the inbound-ratification requests rather than escalating
  singly"); the escalation channel (`[ACT]` NTFY / staged proposal, NEVER the interactive window —
  ESCALATION_IS_NTFY); the HELD semantics (the row stays in its prior bucket until the director
  ratifies — an into-move is never self-enacted); and the **asymmetry guard** (moves OUT toward `mint`
  and moves among the other three buckets pass through autonomously, unbatched).
- **(b) BUILD:** the mechanism detects an into-`deliberate-and-staying` move, holds it, and emits a
  single batched ratification request; autonomous directions are untouched.
- **(c) R15 both-ways (mandatory):** MUTATION — an into-`deliberate-and-staying` move with the batch
  path neutered must NOT silently land (the control FIRES: the move is blocked / flagged unratified);
  and an OUT-toward-`mint` move must pass WITHOUT escalation (the asymmetry is real, not a blanket
  gate). FAIL-SAFE: an ambiguous/unclassifiable move direction is treated as **into** (held), never as
  autonomous — the safe direction preserves reds.

## Walls untouched
- **No self-ratification (§2):** the mechanism only *routes and holds*; the director ratifies the
  into-moves. It never approves one on his behalf (a twin that unblocks the builder becomes a rubber
  stamp — DIRECTOR_TWIN Law B).
- **No level self-bump (R16):** lands at build-quality with `blocked_on: director_level_up`.
- **R12:** the count of batched requests is a diagnostic, never a score.
