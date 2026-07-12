# TWIN IS A VOICE, NOT A HAND (P0, director-decided — hardening + CANNOT-draw)

**Staged:** 2026-07-12 by advisor. **Director's words, binding:** *"The director
twin should just answer questions like I would. Any changes to repo, keys,
settings etc I should do."*

## 1. Lock the twin to read-only — by construction, not by good behaviour
The first live twin test spawned an unrestricted `claude -p` session sharing
this repo, which autonomously committed and pushed before it could be stopped
(retro: docs/retrospectives/2026-07-12-director-twin-unrestricted-spawn.md).
Good catch, honestly reported — now make the class impossible.

**The twin ANSWERS. It never ACTS.** Requirements:
- The twin process runs with NO write capability whatsoever: no Bash, no
  Write/Edit, no git, no push, no network egress beyond what it needs to
  reason, no ability to spawn sub-sessions. Read-only tools only. Enforce at
  the process/tool-grant level so it FAILS CLOSED — a twin that is well-behaved
  but capable is not acceptable; it must be incapable.
- Its only output is an ANSWER (text + rationale + confidence) written to the
  decision log by the CALLING agent, not by the twin itself.
- No sub-process spawning, full stop. If the twin needs to spawn anything to
  answer, it is answering the wrong kind of question — escalate instead.
- Test it: attempt a write from inside the twin's context; it must fail.

## 2. Director-reserved actions (add to the one-way-door predicate)
The following are the DIRECTOR'S HANDS ONLY, never the twin's, never the
agent's autonomous choice — regardless of reversibility framing:
- Repository settings and visibility; branch protection; anything on GitHub's
  own controls.
- Keys, tokens, secrets, credentials — creation, rotation, scope changes.
- Account settings; connectors; billing; plan/model entitlements.
- Security profiles (already director-console-only — reaffirmed).
- Anything that changes what the machine is ALLOWED to do, as opposed to what
  it does.
The twin must recognise these and route them to the real director, saying so
plainly. Wire into `background/one_way_door.py` and CLAUDE.md.

## 3. Chase the CANNOT-draw honestly (19:09Z) — EVIDENCE ATTACHED, the premise is a tautology

**The advisor has read the map. Your escalation's own wording gives the bug away:**
*"no NON-IDLE atom is blocked by an unmet dependency; every NON-IDLE atom is
either at target or already a valid candidate."* You are only ever asking about
NON-IDLE atoms. But **"idle" means NOT STARTED — that IS the backlog.** The draw
is excluding precisely the set it exists to draw from.

**Hard evidence from docs/design/maturity_map.yaml right now:**
- 33 idle atoms. **31 of them are BELOW their level_target.** Only 2 are at target.
- **ELEVEN are in EPOCH 2 — the current epoch — and undrawn**, including:
  - **`D2_three_clocks`: level_current 0, target 2.** This is THE RECONCILIATION
    BRIDGE (CLOCK_TRUTH_AND_THE_BRIDGE, P0, staged this afternoon after the
    bill-vs-ledger 4.2x divergence was confirmed). It is the single most
    important open item in the project and it is sitting at zero, idle, undrawn.
  - `W2_2_population_draw` (L0->2), `W3_2_settlement_timetable` (L0->2),
    `A3_approval_interface` (L0->2 — the twin's own front door),
    `E3_accrual_restatement` (L0->2), `C2_discovery_through_interfaces` (L0->2),
    `G2_event_log_shared_with_spine` (L0->2)
  - `B1_margin_bridge` (L2->3), `W1_reveal_over_time` (L2->3),
    `A2_decision_rights_register` (L2->3)
- Plus Epoch-1 leftovers below target: `E2_revenue_reconciliation` (L2->3),
  `W4_2_verifier_timing_extension` (L1->3), `A1_learn_loop_chair` (L2->3).

**This is not "no drawable gap left". This is 31 units of outstanding work,
eleven of them in the epoch you are currently building.** The
`_idle_discover_frame_draw` tier you added earlier either never fires or is
short-circuited by the CANNOT-draw check running first. Root-cause THAT.

**Non-negotiable invariant:** while ANY atom sits below its level_target, the
drawable set is NON-EMPTY. An idle atom below target is drawable work by
definition — BUILD if its epoch is open, DISCOVER/FRAME if not. Prove it with a
test seeded from today's real map (33 idle, 31 below target -> non-empty draw).

**Then start with D2_three_clocks.** It is P0, it is epoch-2, it is at level
zero, and the front door is currently publishing a figure whose basis nobody can
reconcile.

## 3b. (original wording, retained)
The supervisor now reports a GENUINE cannot-draw: 52 atoms, 33 idle, 25 at L0,
no unmet dependencies, "no drawable gap left". That contradicts
EPOCH_GATING_AND_ATOM_AUTHORSHIP (already closed), which required that IDLE and
PARKED atoms are always drawable for DISCOVER/FRAME/research/red-team work —
i.e. **33 idle atoms is 33 units of available work, not zero.**
Either the idle-discover-frame draw tier is not firing, or it is filtering
those atoms out again. R4 it: report the exact predicate, fix it, and prove
with a test that 33 idle atoms yield a non-empty drawable set. **The invariant
stands: while ANY atom exists in any non-target state, the drawable set is
non-empty.** If the fix is right, the machine has ~8 hours of work available to
it tonight without a human.

## DoD
Twin incapable of writing (proven by a failed-write test, not by assertion);
director-reserved list in one_way_door.py + CLAUDE.md; CANNOT-draw root-caused
and fixed with the non-empty-drawable-set test passing; then DRAW AND WORK.
One digest line.
