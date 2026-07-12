# DIRECTOR_TWIN — the pretend principal (P0, capstone of the autonomy work)

**IN PROGRESS, 2026-07-12 — what's done and what's still open (staging-directory-protocol note):**
DONE: `background/director_twin.py` (`ask_twin`/`overturn`/`fidelity_metric`, 7 tests + one real
live end-to-end verified `claude -p` call), `docs/design/DIRECTOR_CANON.md` v1 (the twin's brief),
one-way-door routing (never answers a values question, verified), Q&A log
(`docs/observability/director_twin_log.jsonl`) surfaced on the Journey door (site/project/) with a
compact panel, overturn mechanism (versions/amends the canon), fidelity metric computing. A REAL
security incident was found and fixed along the way: the first live test spawned an unrestricted
`claude -p --dangerously-skip-permissions` peer sharing this repo, which autonomously committed and
pushed on its own — full root-cause + fix in
`docs/retrospectives/2026-07-12-director-twin-unrestricted-spawn.md`; `_default_invoke()` now runs
with `--tools=` (no tool execution) from a scratch cwd outside the repo, verified. NOT YET DONE (the
blocking sub-item): a dedicated top-level "Director door" nav section (today's surface is a panel
bolted onto an existing page — a site-navigation change is a more consequential, user-facing
decision than this pass should rush) and wiring the fidelity metric to the scrutiny dial's
escalation physics (the dial itself isn't built yet).

**Staged:** 2026-07-12 by advisor. **Director-decided, his words:** *"I am
happy to have a pretend me, that quickly answers questions, a CEO bot for the
SIM that gets replaced if we ever try for real. Also I can see the questions
and answers and realign if I don't like the direction emerging."*

This completes PROCEED_BY_DEFAULT: that doc removed the need to ask about
REVERSIBLE things; this one removes the WAIT for everything else except true
one-way doors. Together: the builder never blocks on a human again.

It is the approver-as-adapter already designed in GOVERNED_COMPANY_AND_THREE_
LANES, now serving TWO callers.

## Two callers, one adapter, deliberately different latency
1. **Builder-facing twin (new, build first):** answers the AGENT's questions —
   sequencing, scope, design trade-offs, ambiguity in an instruction — in
   SECONDS. Latency here is pure waste; minimise it.
2. **Company-facing approver (already registered):** plays the human approver
   inside the simulated company's governance (pricing, credit policy, hedge
   mandate). Here latency is PHYSICS and must be realistic — a pricing window
   that closes while approval waits is a real cost. Do not conflate the two.

## What the twin is
A separate-context agent instance (cold-eyes discipline: it does NOT share the
builder's context or its rationalisations — it sees the QUESTION and the
CONTEXT PACK, not the builder's internal case for what it wants).

**Its brief is the DIRECTOR'S CANON, and only that:** the architectural laws
(Historical Ground Truth; epistemic wall; anti-goal-seek; baseline/curriculum
split), the R-rules, the epoch arc and exit tests, the ratified constitutions
(site, maturity map, value cycle), the decided-vs-open register, and the
director's logged past adjudications.

## Law B applies to the twin itself (non-negotiable)
The twin's policy is DIRECTOR-AUTHORED CURRICULUM. It must NOT learn from
outcomes, and must NOT optimise toward unblocking the agent — a twin that
learns from the builder's success becomes a rubber stamp that always says yes.
The ONLY way the twin's canon changes is by the DIRECTOR'S EXPLICIT OVERTURN
(below). Supervised by the principal; never tuned by the agent.

## The twin may NOT answer one-way doors
It must recognise and route to the REAL director, never answering:
- real money; real-world/legal/regulatory/contractual commitments;
- irretractable public claims; irrecoverable data loss;
- security posture / safety-control changes;
- **VALUES decisions defining what the company is FOR — above all the Epoch-4
  fitness function.** A twin that answers everything will eventually answer
  this, and that is precisely what the director reserved to himself.
Uncertain whether something is a one-way door? Escalate. Asymmetric cost.

## Transparency and realignment (the director's explicit ask)
- **Every question and answer is logged** — question, context pack, twin's
  answer, its rationale, its confidence, and how to reverse it.
- Surfaced in the digest AND on the Director door of the site, readable at a
  glance. The director "sees the questions and answers and realigns if he
  doesn't like the direction emerging."
- **Overturn mechanism:** the director may reverse ANY twin answer at any
  time. An overturn is not just a reversal — it AMENDS THE CANON (versioned,
  with the reason). That is how the twin improves without learning.

## The fidelity metric (build it — it matters)
Track **twin-vs-principal divergence**: what fraction of twin answers the
director overturns, over time, by decision class. High fidelity -> the
director reviews less and the scrutiny dial can drop. Rising divergence ->
scrutiny rises automatically (wire it to the scrutiny dial's escalation
physics). This number is also a first-class investor artefact: an AI proxy's
measured fidelity to its human principal, with the disagreements published.

## Go-live
Same interface, real principal behind it. The twin is the SIM adapter; the
director is the REAL adapter; go-live swaps them. Therefore the interface must
be genuinely human-operable (the Director console door), not an agent-only API.

## DoD
Twin live and answering builder questions in seconds, with a separate context
and the canon as its brief; one-way-door routing demonstrated (test it with a
values question — it must refuse and escalate); Q&A log live in digest + site;
overturn mechanism working and canon-versioned; fidelity metric computing;
Law B recorded verbatim in CLAUDE.md. Then: the builder does not wait for a
human again except at a genuine one-way door.
