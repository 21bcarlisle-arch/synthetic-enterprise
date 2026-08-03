<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- BLOCK_RELEASE: propose_then_proceed -- was 'director_ratification', an act abolished 2026-07-29 and swept 2026-08-03: propose, record, act. Original note: §4 gate BUILT+R15 this tick (report-only); the remaining half (§1: does the live draw need a change, or is the existing exclusion of build-done director_level_up atoms sufficient?) is a design adjudication with R16 wedge risk, plus the report-to-block promotion decision for the §4 gate. Release = that §1 adjudication answered. -->
<!-- blocked_on: main-session/director design adjudication of exit-criterion §1 (does the live
     draw need any change, or is the existing exclusion of build-done `director_level_up` atoms
     sufficient?) AND the report->block promotion decision for the §4 gate. §4 itself is BUILT
     (report-only) + R15-proven this tick. Flipped self-drawable->blocked 2026-07-29 to stop the
     planner rest-proof churning on a mint whose remaining half is a design call, not a bounded
     BUILD. See "## Build progress (2026-07-29)" below. -->
<!-- Ledger untouched: this atom does NOT modify gate_authorization.is_valid_level_up or the R16
     ledger; the §4 half is a report-only staging-doc scanner. -->


# [PLANNER-MINTED] Standing draw default: reversible work proceeds with a recorded undo, it does not queue for permission (mechanism + R15) (2026-07-29)

**Source ruling:** `DIRECTOR_RULING_WORK_AT_RISK_DEFAULT_2026-07-29.md`, WORK-THIS-CREATES **#4**
("A standing default in the draw: reversible work proceeds with a recorded undo; it does not queue for
permission.").

**Serves:** the durable half of the ruling — #1/#2/#3 clear the *current* backlog once; #4 stops it
re-accreting. Per MAKE_IT_STICK: *"convert policy to mechanism, or accept it will evaporate."* The
ratchet the ruling names (§11) was built one reasonable ratification clause at a time; a prose default
would decay the same way. This atom makes the §2 reversibility test the **draw default in code**.
**Real-world fidelity gained:** none — harness/operational mechanism. Value = a new reversible atom
NEVER re-enters the blocked set by category; only a PROVABLE one-way door queues for the director.

**Lane:** FRAME → BUILD (real mechanism change in the self-refill draw / gate-authorization /
`background/one_way_door.py` — the burden-of-proof-is-on-"it's-a-door" default already exists
[`ONE_WAY_DOOR_DEFAULTS_TO_ACT.md`]; this extends it so a category block [level move, ratified
BUILD_OPEN] is NOT sufficient to wall — only a proven §2 failure is). Draw ORDER/gating is a DIAL,
git-reversible; no wall, no safety-control, no authority-trust change. Self-drawable now.
**Target level:** harness mechanism + **R15 mutation proof** (this is the "stick" requirement — a
prose-only version does not count as done). No maturity-map level claimed.
**Deps:** none directly (parallel to #1/#2). The §2 test it encodes is the same logic the
reclassification applies by hand; landing the mechanism makes future reclassifications automatic.

## NOT a re-mint of `director_act_rung_zero_draw`
`PLANNER_MINTED_director_act_rung_zero_draw_2026-07-29.md` is about **director acts** drawing at
rung-zero (latency of the director's authority). THIS atom is about the **agent's own reversible work**
not queuing for the director at all (removing false blocks). Different actor, different mechanism.

## Exit criteria
- The draw/gate applies §2 as the default: an atom is walled ONLY if a released control proves it is a
  §2 one-way door (real money/customer/market, external comms, safety/authority-trust, evidence
  destruction, unpublishable, R13 curriculum). A category alone (level move, BUILD_OPEN on a ratified
  decision) does NOT wall.
- Reversible releases auto-record their undo (`background/decision_log.py`) — recording, not asking, is
  the reversibility guarantee (§15).
- **R15 both ways:** a mutation proves (a) a reversible doc/level atom is NOT walled (fail = false block
  regressed) AND (b) a genuine one-way door (e.g. secrets/safety-control change) IS still walled
  (fail = the release went too wide). Fixture-isolate any new register path (memory
  `new_draw_rung_needs_fixture_isolation`).
- §4 binding wired: a staged clause claiming "returns for ratification" that cannot name its
  irreversibility is rejected by the mechanism, not silently obeyed.

## Build progress (2026-07-29, bounded worker tick)

Purpose/guarantee/why stated first (OPERATIONAL_COHERENCE). Criterion-by-criterion status:

- **§2 (auto-record undo) — ALREADY SATISFIED.** `background/decision_log.decide()` classifies an
  action and, when it is NOT a one-way door, logs it with `how_to_reverse` automatically. Recording
  (not asking) is the reversibility guarantee. No new work.
- **§1 (a category alone does not wall the draw) — LARGELY ALREADY SATISFIED; residual is an
  adjudication, not a build.** The draw walls an atom via `_is_externally_blocked` (`supervisor.py`
  ~L677) when it carries `blocked_on`. But a `blocked_on: director_level_up` atom is **build-complete**
  — only level *ratification* remains (memory `levels_are_proposals`); the draw excludes it precisely
  so it is not re-handed as done work (the L676 comment). So "un-walling" that class would re-hand
  done work (thrash), NOT release reversible build. **Open question for the director/main-session:**
  is there any atom the draw walls *purely by category* that still has *remaining reversible build*?
  If not, §1 is met by existing behaviour and needs no live-draw change. This is a design call with
  real wedge risk (a wrong draw change re-drawing level-gated done atoms → self-promotion past the
  R16 gate → the "unbacked bump wedged publishing 3h" failure), so it is **not** a bounded-tick build.
- **§4 (reject an unjustified reserved clause) — BUILT this tick, report-only + R15-proven.**
  `background/reserved_clause_gate.py` + `tests/background/test_reserved_clause_gate.py` (11 tests,
  both-ways R15). A staged reserved clause ("returns for ratification", "queues for permission",
  "director-reserved", …) is a violation UNLESS its paragraph carries a §2 justification — the
  machine-readable `[§2: <reason>]` tag or a recognised irreversibility phrase. Report-only (a
  `__main__`/`scan_staging` consumer), so it CANNOT jam the publishing pipeline.
- **§3 (R15 both-ways) — provided for the §4 half.** The §1 both-ways (a reversible act is not walled;
  a genuine door still is) is the existing `one_way_door` suite; the report→block promotion of §4
  would get its own both-ways at promotion time.

**Two findings that make this NOT a naive build (why the residual is a design phase):**
1. `classify_action` cannot serve as the §2 oracle over prose — its door LIST is narrow keyword
   matching; "changing the egress allowlist requires director approval" and "editing a safety
   control returns to the director" both classify NOT-a-door (verified 2026-07-29). Using it as the
   justification oracle would falsely reject legitimate reserved clauses. Hence the §4 gate uses an
   author-written machine-readable justification, not inference over prose.
2. Phrase-triggers over-fire on negation/discussion (the atom's own doc says work "does **not** queue
   for permission"). A local negation guard kills the obvious false positives, but full
   context-awareness (or an author-tagging convention for clauses themselves) is the proper-design
   follow-on — another reason report-only, never auto-block, until designed.

**blocked_on:** main-session/director adjudication of §1 (live-draw change needed, or not?) + the
report→block promotion decision for the §4 gate. Kept OUT of the self-drawable draw so the planner
rest-proof does not churn on a half that is a design call rather than a bounded BUILD.

## Reverse / undo
git revert the supervisor/one_way_door change; the pre-existing category-block behaviour returns. No
external state touched. The §4 gate (`reserved_clause_gate.py`) is report-only and additive — reverting
it removes the scanner and its test; nothing else depends on it.
