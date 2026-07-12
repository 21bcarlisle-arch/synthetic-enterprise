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

## 3. Chase the CANNOT-draw honestly (19:09Z)
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
