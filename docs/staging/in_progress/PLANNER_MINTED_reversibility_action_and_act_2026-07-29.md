<!-- BLOCK DISSOLVED 2026-08-03 (worker tick) -- KEPT IN in_progress/ ON PURPOSE, AS DRAWABLE WORK,
  NOT ARCHIVED. The stated blocker above is now FALSE. It reads "the agent cannot self-cross the R16 wall",
  but R16 was RESCOPED 2026-08-03: "a level move must leave an auditable trace in gate_authorizations.jsonl
  ... What R16 never required, and no longer implies, is that anyone AUTHORISE the move: self-certify with
  the evidence and go." There is no wall left to cross, and no phone-signed LEVEL_UP batch to wait for.
  RESIDUAL, NAMED SO THE NEXT TICK CAN DRAW IT DIRECTLY: item #2's 15 reversible level moves are now
  self-certifiable via background.gate_authorization.record_level_up_self_certified.
  They are deliberately NOT bulk-stamped here. Each needs its level RE-VERIFIED against real artifacts
  first -- clearing a blocked_on has never moved a level_current, and a control that passes for the wrong
  reason is not evidence (the abolished-block stale-cells class). Precedent from THIS SAME TICK: five items
  filed as "build done, only the abolished level move remained" were checked against real disk, and one of
  them -- director_window_delta_view -- turned out to have no code and no test anywhere, only design-doc
  mentions. A bulk stamp would have recorded it as done. Fifteen individual re-verifications is the work;
  that is not bookkeeping, and it is why this file stays in the BUILD queue rather than the archive. -->

<!-- PARTIALLY ACTIONED 2026-07-29 (planner tick):
  #3 (batched [ACT]) DELIVERED -> docs/observability/work_at_risk_batched_act_2026-07-29.md (committed).
  #2 (release the proceed-at-risk set) is BLOCKED, not self-actionable: the reclassification's 15
  reversible level moves are mechanism-held on atom #4 (reversible_draws_dont_queue_for_permission),
  whose CORE relaxes the R16 pre-commit level gate = an authority/safety-control change the agent may
  NEVER self-authorize on an advisor-bridge ruling (authentication convention; one-way-door cat 5/8).
  Per this atom's own decompose-and-escalate note: reversible parts done, irreducible core ESCALATED
  via NTFY. Left in in_progress/ (open sub-item = the director act ACT-1/ACT-2 in the batched [ACT]).
  Self-authority release sweep already found 0/21 self-releasable; nothing crossed the R16 wall; no
  --no-verify (R16). R12 held: count stays 21 by honest classification, not re-scoped to zero. -->
<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- BLOCK_RELEASE: propose_then_proceed -- was 'director_level_up', an act abolished 2026-07-29 and swept 2026-08-03: propose, record, act. Original note: #3 delivered; #2 releases the 15 director_level_up items via the director act ACT-1 in docs/observability/work_at_risk_batched_act_2026-07-29.md (phone-sign the LEVEL_UP batch, OR console-authorize atom #4's R16 gate relaxation). Agent cannot self-cross the R16 wall. -->

# [PLANNER-MINTED] Action the proceed-at-risk class with recorded undos, and send ONE batched [ACT] (2026-07-29)

**Source ruling:** `DIRECTOR_RULING_WORK_AT_RISK_DEFAULT_2026-07-29.md`, WORK-THIS-CREATES **#2**
("Everything in the proceed-at-risk class actioned, with recorded undos.") **and #3** ("One batched
[ACT]: what was done, how to reverse each, what remains genuinely reserved and why.") — #3 is the
OUTPUT artifact of #2, so both are minted ONCE here.

**Serves:** the ruling's core move (§1) — reversibility is achieved by RECORDING, not by ASKING: make
the recommendation, proceed, record the one-line undo, flag it in the batch. The director reverses if
he disagrees. This is the ACTION half; the reclassification (#1) is the input.
**Real-world fidelity gained:** none directly — operational authority. Value = the blocked count falls
on the AGENT's action (not the director's), satisfying the ruling's acceptance test, and the director
receives ONE batch containing only genuine one-way doors.

**Lane:** FRAME + self-release action (self-authority level/window/mint/BUILD_OPEN releases per the
widened §2 class; **no production behaviour change, no walls crossed** — every release is git-reversible
and recorded). Self-drawable now.
**Target level:** operational action + committed before/after ledger + one batched NTFY [ACT]. No
maturity-map level claimed.
**Deps:** **[PLANNER_MINTED_reversibility_reclassify_blocked_set_2026-07-29]** — must have the
per-item verdicts before acting. Do NOT release blind.

## Relationship to `self_authority_release_sweep` (extends, does not duplicate)
`PLANNER_MINTED_self_authority_release_sweep_2026-07-29.md` released under the narrow pre-ruling scope.
This atom releases the ADDITIONAL items that §2 reclassifies to proceed-at-risk (reversible level moves,
BUILD_OPENs on already-ratified decisions). If the sweep has already run, start from its after-state and
release only the delta the reversibility test newly permits — do not re-release what it cleared.

## Exit criteria (#2 + #3 both satisfied)
- For every item the reclassification marks PROCEED-AT-RISK: make the recommendation, **proceed**
  (release the level/window/mint/BUILD_OPEN via existing self-authority paths — memory
  `blocked_on: clear ≠ director_level_up`, `levels are proposals`), and **record a one-line undo** in
  `background/decision_log.py`.
- Produce **one** committed batched [ACT] stating, per item: what was done, the exact single reversing
  act, and — for every item left RESERVED — the named irreversibility. NTFY it as one message (R5/R8
  batch, terse).
- Acceptance (ruling §52): items awaiting a director act fall to those that are genuinely one-way, each
  stating its irreversibility.

## Reverse / undo
Each released item carries its own recorded one-line undo (re-set the level/blocked_on/window). The
batch is a report — retract by follow-up NTFY. git revert of the release commits.
