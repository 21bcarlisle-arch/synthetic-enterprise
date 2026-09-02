<!-- PARKED IN in_progress/ 2026-07-29 — audit STARTED at docs/design/MOTHBALL_2026-07-29.md
     (verdicts recorded per component). OPEN: execute the MOTHBALL-verdict rows (disable + record),
     do not re-scan as unprocessed. Reversible throughout. -->
# [DIRECTOR-RULING] — Mothball the apparatus unless it earns its place (2026-07-29)

**Type:** [DIRECTOR-RULING] via advisor bridge. Companion to `THE_STANDARD`. Do this yourself; do not wait.

## The ruling

Much of the machinery built over the past fortnight exists to manage **waiting, approving and blocking** — things `THE_STANDARD` has now removed. It is still in the code even though the canon overrides it, and code beats canon unless someone acts.

**Default: mothball it. The burden of proof is on KEEPING, not on removing.**

For every gate, queue, window, approval path, blocked-state tracker, draw-ordering rule and reporting ritual, answer one question:

> **Under the new standard — no one-way doors, silence is agreement, never wait, show the working — what is this actually for?**

- **If it serves the new model as-is:** keep it, and say in one line what it does.
- **If it could serve the new model adapted:** adapt it, and say what changed.
- **If you cannot say plainly what it is for:** **mothball it.**

## Mothball, not delete

Disable it, keep the code, record what was mothballed and why. Nothing here is irreversible and reinstating something is cheap. **Do not agonise** — a wrong removal costs a few minutes; leaving dead machinery in place costs a working day every time it fires.

## Prime candidates — your judgement, not a list to obey

Anything that makes the **director wait**, or makes **you wait**, is the obvious place to start: approval plumbing, propose-then-proceed windows used as blockers, blocked-item tracking, reserved-category checks outside real money and real people, elaborate work-source ordering now that you set your own agenda.

Likely worth keeping, but decide for yourself: the rules forged from real incidents, the gap and simplification registers (**they are the backlog's raw material**), the coherence checks that stop the published story drifting from the truth, and the red-teaming that keeps finding genuine defects.

## Do not ask

**Do not send a proposal and wait.** Do it, then tell the director in plain language: what you mothballed, what you kept, what you adapted, and why. If he disagrees he will say so and it comes back — that is cheap and that is the design.

**Test:** after this, the machine should be unable to be blocked by anything other than real money, real people, or a safety control.

— Advisor bridge, carrying the director's instruction. The advisor built most of what is being mothballed. 2026-07-29.

---

## Addendum — the test is now measurable (director, 2026-08-12)

The test above asks whether you can say plainly what a control is for.
That is a judgement, and judgement is why this audit stalled: nobody
wants to be the one who says a thing built in good faith was theatre.

There is now a better test. The OPS10 class work holds fifty-one recorded
instances across five named classes, each with evidence. Use it:

**For each control, which of the recorded instances would it have
caught?**

- Catches instances on the list → it earns its place, and you can now say
  so with evidence rather than argument.
- Catches nothing on the list → the burden of proof is on keeping it, and
  "what it is for" is no longer an adequate defence.

The board of six stances gets an explicit recorded verdict this pass —
mothballed, or kept with a one-line reason. Neither has been recorded,
and neither-is the worst state.

**Guardrail, and it is not optional.** This coverage count is a
measurement, never a target. Nothing is to be built, tuned, or reshaped
to raise it. The moment a control is written to score rather than to
catch, the number stops meaning anything and the audit has manufactured
the goal-seeking this project exists to refuse.

Fifty-one is today's count, not a fixed set. If the classes have grown by
the time you run this, use what exists then and say which count you used.

— Advisor, carrying the director's instruction. 2026-08-12.

---

## Second addendum — three imports from a peer harness (director, 2026-08-12)

Source: the agent-instruction file of DeepSeek Harness (`AGENTS.md`, MIT,
public repo, read directly by the advisor — not a summary of it). It is
the closest published equivalent to our own governance file. Three of its
rules bear directly on work already open here. Take the ideas; we are not
adopting their harness.

### 1. Assert relationships, not presence

Their rule for runtime invariants: check authoritative event streams or
mutable data — **not** service presence, method presence, metadata, or
fixed pure examples.

That is the general form of the no-caller class. A test that asserts a
mechanism *exists* is satisfied by an orphan. Only a test that asserts
the *relationship the mechanism participates in* is not. The orphan
ratchet applies this to callers. The question for this audit is whether
our other controls assert presence or relationship — a presence-asserting
control is a strong mothball candidate even if it is green every day,
because green is what it would be either way.

### 2. Removability by construction

In their design every contribution is registered as an effect, and the
act of registering returns the thing that removes it. Nothing can be
added that cannot be cleanly removed.

This is why our mothball audit stalls: disabling a component here is a
judgement about what else breaks. Not a proposal to re-architect. But
when a component is genuinely hard to mothball, record that as a finding
in its own right — difficulty of removal is information about how the
thing was built, and it belongs in the audit's output.

### 3. State the invariant in both directions

They require that anything reaching a model request be reconstructable
from the session log, **and** that any new model-visible input add a log
event. Both directions, so an unlogged new input fails the build.

Our reconstruct-from-repo-alone principle is stated in one direction
only, and the direction that failed was the reverse one: thirteen running
services that no repo analysis could see. Where a principle here is
stated one way, ask what its reverse would catch.

### Two smaller notes, not rulings

- They gate documentation size, with an explicit protocol for raising the
  ceiling when the content genuinely needs it. That is the CLAUDE.md
  decay problem mechanised.
- Their pre-release section carries its own retirement condition tied to
  an event, not a date. Rules that know when they expire.
- `knip` is off-the-shelf unused-export detection. Worth knowing it
  exists before hand-rolling more of the ratchet.

— Advisor, carrying the director's instruction. 2026-08-12.

---

## Third addendum — a second test for each control (director, 2026-08-12)

The coverage test in the first addendum asks whether a control catches
any of the recorded instances. Add a second question, asked of the same
control at the same time:

**Does this control need judgement to run, or does it decide
deterministically?**

Try deterministic first. Reach for judgement only when identifying the
error genuinely requires it. A control that needs judgement is more
expensive, slower, and can itself be wrong — so where a control currently
requires judgement, ask whether the same error has a deterministic
expression that would decide it.

This is not a rule that judgement-based controls are wrong. Some errors
cannot be expressed any other way — a page that reads as stale, a chart
whose shape is off, a claim that overstates its evidence. It is a rule
about order: deterministic where possible, judgement where necessary,
and a recorded reason when judgement is chosen.

Two consequences worth recording in the audit's output:

- A control that could be deterministic but is not is a candidate for
  conversion, not mothballing.
- An error the project keeps finding by eye, which no control catches
  because no deterministic expression exists, is a gap this audit should
  name rather than pass over. The nav-route and stamp-vintage findings
  staged today are both of that kind.

Source: an eval methodology guide by Teresa Torres (producttalk.org),
read directly. Her rule is to find a deterministic measurement for every
error first and use a model's judgement only where the error truly
requires it. She also uses a cheap deterministic check across everything
with only the failures escalated to the expensive judge — a pattern worth
remembering when visual telemetry is unparked, but not authorised here.

— Advisor, carrying the director's instruction. 2026-08-12.
