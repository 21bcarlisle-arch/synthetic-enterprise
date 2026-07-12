# MAKE IT STICK — mechanism, not memory (P0, standing; enforces PROCEED_BY_DEFAULT + DIRECTOR_TWIN)

**Staged:** 2026-07-12 by advisor. **Director-decided:** *"No real money today,
just a bit of wasted time and tokens — and right now we are extremely wasteful
of both. So very little to lose. And if the way we do it enhances the overall
project pitch and future states, even better. Please make it stick this time."*

## 1. The asymmetry (record as a standing bias in CLAUDE.md)
- Cost of a WRONG REVERSIBLE decision: ~1 hour of compute. Reverts with git.
  Produces a finding.
- Cost of a STALL: hours of wall-clock, plus the director's attention — the
  only genuinely scarce resource in this project.
**Bias ~100:1 toward acting.** When the cost of being wrong is a revert and the
cost of waiting is a day, ACT. Hesitation is the expensive choice, and we have
been paying it all weekend.

## 2. WHY RULES DECAY — the diagnosis, from this weekend's own evidence
Every rule that DECAYED was an exhortation: "fan out" (reverted to serial
within an hour), "don't idle" (8 recurrences), "ntfy me when blocked" (failed
4x). Every rule that HELD was a MECHANISM: the Stop hook, the multi-atom draw,
the file_scope gate, the idle-turn counter, the change-detection gate.
**Policy in memory dies at the next /clear or drifts under load. Policy
compiled into the machinery cannot.**
Therefore: **convert policy to mechanism, or accept that it will evaporate.**
This is now a standing engineering law of the harness.

## 3. Requirements — mechanise the autonomy rules
1. **The twin is a HOOK, not a habit.** When the agent enters ANY blocking or
   waiting state (a question for the director, an ambiguity, "awaiting steer"),
   the hook fires automatically, routes the question to DIRECTOR_TWIN, and the
   agent continues on the answer. The agent must not have to REMEMBER to
   consult it — remembering is what decays.
2. **The one-way-door list is CODE, not judgement.** A checkable predicate
   (real money / real-world commitment / irretractable public claim /
   irrecoverable data / security-safety / values decision / real customer).
   Fails closed to escalation on genuine uncertainty. Not re-derived each time.
3. **The decision log writes itself.** Hook-written, not discipline-written:
   what, why, confidence, how to reverse. Surfaced in digest + Director door.
4. **Rules live in TWO places or not at all:** CLAUDE.md (survives /clear) AND
   as enforced mechanism (survives drift). A rule that exists only as prose is
   a rule with an expiry date.

## 4. Anti-decay metrics (alarmed, reported every digest)
- **Turns spent waiting on a human -> target ZERO** (except at a genuine
  one-way door).
- **Escalations later judged reversible -> target ZERO.** (Audit the last 20:
  report the number. It is the measure of the old error.)
- Twin answer latency (seconds, not minutes).
- Idle turns with atoms available (already zero — keep it there).
A rising number on any of these is a DECAY ALARM: the mechanism has slipped.

## 5. The decay audit (standing, every epoch boundary)
Walk every standing rule. For each: is it enforced by mechanism, or does it
depend on the agent remembering? Prose-only rules are decay candidates —
MECHANISE OR DELETE them. A rule nobody enforces is worse than no rule: it
creates the illusion of control.

## 6. This IS the pitch (build it as a product surface, not overhead)
An autonomous company is investable only if it is GOVERNABLE. What we are
building — a full audit trail of autonomous decisions, a published fidelity
score between the AI proxy and its human principal, and the disagreements
shown rather than hidden — is the proof that autonomy and accountability can
coexist. Nobody else has that artefact. Feature it: a Governance surface on
the site (Method/Director doors), and a section in the pitch. The mechanism
that makes us fast is the same mechanism that makes us credible.

## DoD
Twin-hook firing on blocking states (test: agent asks a reversible question ->
answered and continued with NO human turn); one-way-door predicate in code with
a values-question test proving it escalates; decision log hook-written and
surfaced; both rules in CLAUDE.md; the four anti-decay metrics live and alarmed;
decay audit scheduled at epoch boundaries; governance surface on the site.
Then: work. The map has 23 atoms at L0 and nothing is waiting for a human.
