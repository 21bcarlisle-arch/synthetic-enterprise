<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED] — Surface the "no WORK THIS CREATES block" defect back to the advisor (§4) (2026-07-27)

**Provenance:** RUNG-7 mint from a ratified ruling's WORK THIS CREATES block (§2+§4, landed 6f2be1d41).
Source: `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27.md`, deliverable **4** (""WORK THIS
CREATES" parser + the missing-block defect report per §4").

**Why a distinct mint (the parser half is COVERED, the report half is OPEN):** the §4 PARSER
(`work_this_creates_deliverables`) and the missing-block DETECTOR (`ruling_steer_missing_work_block`)
both LANDED with item 2 and are R15-proven. But §4 is binding *on the advisor*: *"A ruling arriving
without one is a defect in the ruling — say so and request it; do not silently absorb it."* The
detector is currently surfaced NOWHERE — `grep` finds `ruling_steer_missing_work_block` referenced only
by its own definition and this ruling's banner. So a block-less ruling would be detected and then
silently dropped — the exact silent absorption §4 forbids. This mint wires the detector to an actual
"say so and request it" output.

**Serves:**
- **§4 verbatim** — the missing-block case must be *reported*, not absorbed; definition stays with the
  author (advisor), map mechanics with the machine.
- The broader honesty invariant that a defect the machine can detect must reach the human who can fix
  it — an un-surfaced detector is a fail-silent control ([[feedback_fail_silent_control_patterns]]).

**Robustness gained (one sentence):** whenever a staged `[DIRECTOR-RULING]`/`[STEER]` lacks a WORK THIS
CREATES block, the machine emits an explicit "§4 DEFECT — ruling <name> has no WORK THIS CREATES block;
requesting it" notice (NTFY [STEER]-class and/or the observability action-needed register) rather than
silently absorbing it — and stays silent when every staged ruling carries its block (no false page).

---

## Scope — BUILD (harness/observability lane)
- **Lane:** harness / observability. **Target level:** L2.
- **Exit criteria:**
  1. `ruling_steer_missing_work_block()` output is surfaced to a real consumer: emit a bounded,
     transition-only NTFY ([STEER]/[ACT]-class per the terse-wire convention
     [[feedback_operating_model_2026_07_18]]) AND/OR write to the observability action-needed register
     (`docs/observability/action_needed_register.json`) so the daily note / director window sees it.
     Pick the channel that fits R5 (fire on the transition into "a block-less ruling is staged", carry
     the ruling name + the ask, never repeat an unchanged status).
  2. The notice names the specific defective ruling and states the ask ("close it with a WORK THIS
     CREATES block naming deliverables, acceptance criteria and target lane").
  3. **R15 both ways (binding):** a staged ruling WITH no block → the surface fires (register entry /
     NTFY payload present); a staged ruling WITH a block → the surface stays quiet (mutation-prove the
     fail-open direction: neutralise the detector wiring → the block-less case goes undetected → test
     RED). Include a legitimate-edge test so a well-formed ruling never false-fires
     ([[feedback_control_false_positive_jams_pipeline]]).
  4. Idempotent / no-repeat: the same block-less ruling does not re-fire every tick (transition-only).
- **Deps:** item 2 (landed — parser + detector). No dep on #1/#3/#5. Disjoint file_scope (the surface
  wiring + register) → concurrent with the others.

## Walls untouched
- One-way doors: none. NTFY is agent→director alerting (allowed); no safety-control change.
- The advisor-facing content is a REQUEST, not an action on the ruling — the machine never fabricates a
  WORK THIS CREATES block on the author's behalf (that would defeat §4's "definition stays with the
  author").

## Window
Director-ruled; drawable now. Failing test FIRST.

— Planner mint, RUNG-7 refill from ruling WORK THIS CREATES §4, 2026-07-27.
