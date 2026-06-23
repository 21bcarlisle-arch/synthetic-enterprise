# Claude Code Architecture Upgrade — Phased Execution

## Governing Principle

The goal is not to look like a professional AI setup. The goal is to be one,
and make that legible. Every change must be motivated by a genuine architectural
benefit. Cosmetic changes — renaming, restructuring without functional
improvement, documentation that duplicates what the code already shows — are
explicitly out of scope.

If a best-practice pattern does not fit this project's actual architecture,
say so in the audit and explain why. Cargo-culting patterns that don't fit is
worse than not having them.

Honouring STOP gates in this document is a hard constraint, not a preference.
Do not proceed past a STOP under any circumstances without receiving an explicit
"proceed stage N" message from Rich via NTFY or staging.

Every agent operating in the company layer is bound by the Epistemic Honesty
Principle — it can only access information a real UK energy supplier could
know. No company-layer agent may read simulation internals, SIM state, or
ground-truth parameters directly. This applies to all existing and future
agents without exception. The Epistemic Verifier (Stage 3) enforces this
automatically at phase close.

The discovery agent is the company's market research function. It discovers
what the real world looks like by reading real-world sources (Ofgem, Elexon,
NESO, published market data) — not from simulation outputs or ground truth.
Its findings inform the company's own models. It must never be seeded from
SIM internals.

---

## Observability Requirement (applies to all stages)

As the agent architecture grows, visibility into what each agent is doing
becomes critical. Silent failures are worse than loud ones.

**Hard requirement:** every agent — existing and new — must emit structured
status updates. No agent is considered complete or correctly implemented
until its observability output is visible on the poesys.net system health
panel.

Each agent must report:
- Last action taken and timestamp
- Current status: idle / working / waiting / error
- What it produced (file written, message sent, run triggered, finding logged)
- Any anomaly or unexpected condition

These are written to a central observability log (suggest
`docs/observability/agent_status.json`, updated by each agent after
every meaningful action) and surfaced on the poesys.net dashboard as a
system health panel alongside the business metrics.

The system health panel must show, for each agent:
- Name and role (one line)
- Last heartbeat timestamp
- Current status
- Last action summary
- Any active anomaly or error

This panel is the operational view of the system. Rich should be able to
open poesys.net and immediately see both the business running and the
machinery running it.

**Before Stage 0 begins:** add the observability log schema and the
poesys.net system health panel as a prerequisite task. This is the
foundation everything else reports into.

---

## Stage 0 — Best Practice Audit

Analysis only. No code changes. No file changes except the audit output
itself and the observability prerequisite above.

Audit the current codebase against Claude Code best practices across these
dimensions:

**Architecture visibility**
- Are all agent roles (discovery, risk committee, dispatcher, autonomous
  runner, staging watcher, session watchdog, background worker,
  sim runner) documented as first-class definitions or only implicit in code?
- Is the SIM/company separation legible to someone reading the repo cold?
- Does the README accurately convey the multi-agent architecture?
- What would an AI expert miss or misread on a cold read?

**CLAUDE.md hygiene**
- Current line count
- What proportion is session-invariant rules vs reference material that
  could load on demand?
- Which rules carry the highest risk of being ignored due to context
  dilution?

**Verification discipline**
- Is every phase-close structurally gated by a test run?
- Are failure modes documented as discovered artifacts, not just fixed
  silently?
- Is there a structured record of what each phase discovered vs what was
  specified in advance?

**Inter-agent communication**
- What formats are currently used between agents?
- Are they consistent, typed, and versioned?
- Where are implicit dependencies that would break silently?

**Subagent architecture**
- Which existing background processes are natural candidates for
  formalisation as .claude/agents/ definitions?
- First verify: does the current Claude Code version actually support
  .claude/agents/ as a functional pattern, or is it documentation only?
  If not supported, document this and propose an alternative before
  proceeding to Stage 2.
- Which processes are not candidates — and why?
- What would be gained and what would be risked by each formalisation?

**Observability gaps**
- Which agents currently emit no status output?
- Which agents could be silently failing without anyone noticing?
- What is the current mean time to detection for a daemon failure?

**What already exists but is not visible**
- Which best-practice patterns are already implemented but not surfaced
  in documentation or structure?
- What genuine strengths does the project have that a cold reader would
  not immediately see?

Produce the audit as docs/claude/best-practice-audit.md. Be specific —
name files, line numbers, concrete gaps. Do not soften findings. Do not
inflate strengths.

**Gate:** docs/claude/best-practice-audit.md committed. Observability
prerequisite (log schema + poesys.net system health panel) implemented
and visible. NTFY Rich with: top 3 genuine gaps, top 3 existing strengths
not currently visible, whether .claude/agents/ is functionally supported,
and your assessment of whether the stage order below is correct or should
be reordered based on findings. STOP.

---

## Stage 1 — CLAUDE.md Restructure

Reduce CLAUDE.md to under 200 lines containing only session-invariant
rules.

**Move out:**
- Phase build history → docs/claude/phase-history.md
- Module inventory and file descriptions → docs/claude/module-index.md
- Calibration findings → docs/claude/calibration-notes.md
- Any content that only applies in specific contexts

**Keep in CLAUDE.md:**
- All four architectural laws
- Observability requirement (reference to this document)
- Phase-close checklist (including epistemic verifier and CLAUDE.md
  size check)
- NTFY protocol reference
- Verification discipline (never ignore failures, never tolerate anomalies)
- Current phase and test count (one line each)
- Reference to this upgrade document while it is in progress

Wire all moved content back using @path/to/file references so it remains
accessible on demand without loading every session.

Add to phase-close checklist: check CLAUDE.md line count after every
phase. If over 35k chars, trim before committing. Completed phase details
go to docs/claude/phase-history.md, not CLAUDE.md.

**Gate:** CLAUDE.md under 200 lines. All referenced files exist and are
complete. Full test suite passes. Commit "refactor: CLAUDE.md restructure
for context efficiency". NTFY Rich with line count before and after. STOP.

---

## Stage 2 — Discovery Agent Formalisation

**Prerequisite:** confirm from Stage 0 audit whether .claude/agents/ is
functionally supported. If not, adapt this stage to whatever the correct
pattern is for this Claude Code version.

Create .claude/agents/discovery-agent.md (or equivalent) as a first-class
subagent definition.

The definition must specify:
- Role: validates simulation assumptions against real UK market benchmarks,
  updates ASSUMPTIONS.md with structured findings
- Tools: Read, Bash (read-only queries only), Write (ASSUMPTIONS.md and
  docs/market_research/ only)
- Scope: docs/market_research/ and docs/institutional/ only — no access
  to simulation code or company layer
- Output schema: each finding must include domain, assumption tested,
  benchmark value, confidence (H/M/L), source, date
- Observability: emits structured status to docs/observability/agent_status.json
  after every finding — visible on poesys.net system health panel

Do not modify background/discovery_agent.py. Both execution paths must
continue to work. The definition is additive.

Verify the orchestrator can delegate a discovery task to this subagent
and receive a correctly structured finding in return.

**Gate:** agent definition exists and is valid. A delegated discovery task
completes and returns a structured finding. Discovery agent status visible
on poesys.net system health panel. Full test suite passes. Commit. NTFY
Rich. STOP.

---

## Stage 3 — Epistemic Verifier Subagent

Create .claude/agents/epistemic-verifier.md (or equivalent).

This agent is read-only. Its sole function is to scan code changes for
SIM/company barrier violations after each phase closes.

The agent must:
- Accept a git diff or list of changed files as input
- Check for direct reads of simulation internals from the company layer
  (imports from sim/ or simulation/ into company/, access to SIM state
  not via company/interfaces/sim_interface.py)
- Apply the test to every flagged access: "Could a real UK energy supplier
  know this without reading simulation internals?"
- Produce a structured report: PASS with summary, or FAIL with violation
  list (file, line, description, why it violates the epistemic law)
- Tools: Read, Bash (git diff only). No Write access.
- Observability: emits verifier result to docs/observability/agent_status.json
  after every scan — PASS/FAIL visible on poesys.net system health panel

Wire into the phase-close checklist in CLAUDE.md: run epistemic verifier
on the diff before committing any phase-close commit.

Validation test: introduce one deliberate minor violation (a comment or
import that reads a SIM internal from the company layer), run the verifier,
confirm it flags it correctly, then remove the violation. Document the
test input and output in the commit message.

**Gate:** Verifier correctly identifies the planted violation. Checklist
updated. Violation removed. Verifier status visible on poesys.net. Full
test suite passes. Commit with validation test documented. NTFY Rich with
verifier test result (what was planted, what was flagged). STOP.

---

## Stage 4 — Inter-Agent Message Schema

Create background/agent_protocol.py defining an AgentMessage dataclass
with these fields:

    sender: str
    receiver: str
    intent: str        # e.g. "run_complete", "discovery_finding",
                       #      "health_check", "observability_update"
    payload: dict
    timestamp: str     # ISO 8601
    session_id: str | None = None

Include serialisation (to_dict, from_dict), an IntentType enum of known
values, and validation that rejects unknown intents.

This is additive only. Do not refactor existing NTFY message formats or
staging file structures — those are stable and working. AgentMessage is
for new inter-agent communication going forward.

Add `observability_update` as a first-class intent type. All agent status
updates to docs/observability/agent_status.json should use AgentMessage
with this intent going forward.

Add 8-10 tests in tests/background/test_agent_protocol.py covering:
serialisation round-trip, deserialisation, required field validation,
unknown intent rejection, None session_id handling, observability_update
intent handling.

Adopt AgentMessage for at least one new message in the background stack
to prove the pattern works end to end.

**Gate:** agent_protocol.py exists with dataclass, serialisation, and
validation. Tests pass. At least one live usage in background stack.
Observability updates using AgentMessage visible on poesys.net. Full
suite passes. Commit. NTFY Rich. STOP.

---

## Stage 5 — Deferred

Parallel settlement execution (split-and-merge pattern for risk committee
calls) is deliberately excluded from this document. It requires a design
conversation with Rich before any implementation because the risk committee
call ordering relative to settlement state is not trivially parallelisable.

Do not attempt Stage 5. Do not propose an implementation. Flag it as
deferred in the NTFY after Stage 4 completes.

---

## On Completion of All Stages

After Stage 4 gate is confirmed:

1. Update docs/claude/best-practice-audit.md with a completion section:
   what was implemented, what was found during implementation that differed
   from the audit findings, what remains genuinely deferred and why.

2. Update PROJECT_OVERVIEW.md with a new section describing the agent
   architecture as it now exists — including the observability layer.

3. Verify poesys.net system health panel shows all agents with current
   status, last action, and any anomalies.

4. NTFY Rich with a summary: stages completed, test count before and
   after, any findings that should inform future phases.

Do not mark this document as done until Rich confirms completion.
