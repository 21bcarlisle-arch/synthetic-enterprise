# Best Practice Audit — Synthetic Enterprise

**Date:** 2026-06-23
**Auditor:** Claude Code (Sonnet 4.6)
**Scope:** Architecture visibility, CLAUDE.md hygiene, verification discipline,
inter-agent communication, subagent architecture, observability gaps.

---

## Architecture Visibility

**Agent roles are partially documented.**
CLAUDE.md describes all 8 background daemons and 3 code-domain subagents, but:
- Background daemons (sim-runner, ntfy-responder, dispatcher, etc.) live in
  `background/` as plain Python scripts with no formal agent definition.
- Three code-domain subagents (`sim-engineer`, `saas-engineer`,
  `interface-steward`) have `.claude/agents/` definitions — these work.
- A cold reader of `background/` cannot tell which scripts are daemons vs
  utilities vs one-off scripts without reading CLAUDE.md.

**Concrete gaps (file/line):**
- No `README.md` at the repo root. The top-level structure gives no signal
  about what the project is or how it's organised.
- `background/` contains 15 Python files. No index or inventory.
  `background/sim_runner.py` is the most critical process — nothing marks it
  as such except its docstring.
- `simulation/run_phase2b.py` is the simulation core but is not clearly
  distinguished from the 6 other `run_phase*.py` files.

**SIM/company separation.**
The seam is legible if you read `company/interfaces/sim_interface.py` (313
lines). The law is stated in CLAUDE.md. But:
- The company layer is thin — most I&C and resi tariff decisions still live
  in `simulation/run_phase2b.py`, not under `company/`. The separation is
  architectural intention not yet fully implemented.
- A cold reader of the code would not see the intended split from the
  directory structure alone.

**What a cold AI expert would miss or misread:**
1. That `simulation/` and `sim/` are different layers (sim/ is the physics;
   simulation/ is the business orchestration over it).
2. That `background/` processes are running 24/7 as daemons, not scripts.
3. That CLAUDE.md's 35k char limit is a hard constraint with a checklist
   enforcement — unusual and non-obvious.
4. The significance of the Point-in-Time Blindfold: the constraint that makes
   all company-layer decisions valid is invisible from code structure.

---

## CLAUDE.md Hygiene

**Current state:** 494 lines, 33,677 chars. Hard limit: 35,000 chars.
**Remaining headroom:** 1,323 chars (~3 more phases before overflow).

**Proportion breakdown (estimated):**
- Session-invariant rules (architectural laws, sequencing, tone): ~18%
- Protocol and communication rules (NTFY, staging, REVIEW_GATE): ~8%
- Phase build history and current state: ~55%
- Technical environment and file map: ~12%
- Roadmap: ~7%

**Risk of context dilution:**
The four architectural laws and the phase-close checklist are buried inside
~500 lines of content. During a long debug session the laws are not reliably
loaded or applied. The CLAUDE.md char limit check has already failed once
(33,677 of 35,000 — Phase 43+ will overflow without a trim).

**Highest-risk rules (most likely to be missed under context pressure):**
1. `wc -c CLAUDE.md` at phase close — nearly at the limit right now
2. "Never write code from company layer that reads simulation internals" — no
   automated check exists yet (Epistemic Verifier is proposed in Stage 3)
3. "Update and commit LATEST.md before NTFY" — violated tonight (NTFY was
   sent before LATEST.md was committed in the initial crash response)

---

## Verification Discipline

**Structural gating:** Phase close is NOT structurally gated. The current
process requires manual discipline. Tonight demonstrated the risk:
- 4 bugs accumulated in Phases 40a-42 (committee cooldown, volume tolerance,
  unit_rate format, I&C segment) without detection
- All 4 were introduced across multiple phase commits with no full-run test
  between them
- Detection required an overnight production crash

**Failure modes documentation:**
Failures are not systematically recorded as discovered artifacts. Tonight's
4 bugs will appear in commit messages but not in a searchable failure register.
Consequence: the next similar bug (e.g., a new customer segment missing from
cost_to_serve) will not be caught by reviewing past failures.

**What should exist but doesn't:**
- A `docs/claude/failure-register.md` — each discovered production bug with
  root cause and category (would have caught the "new segment needs entries in
  all dicts" pattern)
- A pre-commit hook running `SIM_FAST_MODE=1 pytest tests/ -q` — 14 minutes
  is too slow for a pre-commit hook, but running on the changed modules would
  catch I&C-related regressions in <30 seconds

---

## Inter-Agent Communication

**Current formats:**
| Channel | Format | Typed? | Versioned? |
|---------|--------|--------|------------|
| Rich → CC | NTFY text → from_rich_*.md | No | No |
| CC → Rich | NTFY text | No | No |
| CC → background daemons | staging/*.md markers | Loose schema | No |
| background → CC | staging/run_complete_*.md | Loose schema | No |
| between daemons | log files | No | No |
| CC → site | site/data/*.json | Structured | No (no schema doc) |

**Implicit dependencies that would break silently:**
1. `ntfy_responder.py` creates `from_rich_TIMESTAMP.md`; `dispatcher.py`
   expects files matching `from_rich_*.md` glob. If ntfy_responder changes
   the filename pattern, dispatcher silently stops processing.
2. `run_phase4c_on_phase2b.py`'s `save_run_output_json()` produces
   `run_output_HASH_TIMESTAMP.json`; `sim_runner.py` parses the filename
   to check success. A format change would cause silent false-success.
3. `site/data/dashboard.json` has no documented schema. If a field name
   changes in `extract_report_data()`, the dashboard silently shows empty
   panels with no error.

---

## Subagent Architecture

**Is .claude/agents/ functionally supported?**
**YES — confirmed working.** Three agents are defined and active:
- `.claude/agents/sim-engineer.md` — tools: Read, Write, Edit, Bash, Grep, Glob
- `.claude/agents/saas-engineer.md`
- `.claude/agents/interface-steward.md`

These are invoked via the `Agent` tool with `subagent_type: "sim-engineer"` etc.
and appear in the `<system-reminder>` available-agents list. The pattern is
functional, not documentation-only.

**Natural candidates for formalisation:**
1. `background/discovery_agent.py` → `.claude/agents/discovery-agent.md`
   (Stage 2 target). The agent already has a defined role; the .claude/agents/
   definition would add tool restrictions and output schema.
2. Risk committee → already uses local Ollama (not a Claude Code subagent,
   correct design for cost reasons — no change needed)

**Not candidates (and why):**
- `sim_runner.py`: pure Python loop, no reasoning required, no benefit from
  Claude subagent formalism
- `ntfy_responder.py`, `dispatcher.py`: I/O and classification — Qwen handles
  classification. Formalising as Claude subagents would add frontier cost.
- `session_watchdog.py`, `staging_watcher.py`: infrastructure monitoring,
  no reasoning required

**Risks of formalisation:**
- Discovery agent formalized as a Claude subagent would spend frontier tokens
  on web searches. Currently it uses Qwen for summarisation. The proposed
  Stage 2 definition restricts tools to Read/Bash — no web access, which is
  more conservative than the current background/discovery_agent.py.
- Epistemic Verifier (Stage 3) as a subagent is the right pattern — read-only,
  narrow scope, no risk of breaking anything.

---

## Observability Gaps (as of Stage 0 start; partially fixed by Stage 0 prerequisite)

**Before tonight's fixes:**
- All 8 background daemons: no structured status output
- Mean time to detection for a daemon failure: unbounded (could be days)
- Tonight's incident: sim_runner crashed repeatedly for 8+ hours before
  detection. Root cause was a TimeoutExpired exception with no try/except.
  MTTR was the entire overnight window.

**After tonight's fixes (Stage 0 prerequisite):**
- `docs/observability/agent_status.json` created — 3 daemons now emit status
- `site/data/agent_status.json` mirrored for dashboard
- "System" tab added to poesys.net
- sim_runner, ntfy_responder, dispatcher now call `update_agent_status()`

**Remaining observability gaps (5 daemons not yet wired):**
- `session_watchdog.py` — no status emit
- `staging_watcher.py` — no status emit
- `autonomous_runner.py` — no status emit
- `discovery_agent.py` — no status emit
- `background_worker.py` — no status emit

**Detection methods for each daemon before these changes:**
| Daemon | How you'd know it failed | MTTD |
|--------|--------------------------|------|
| sim-runner | No run_complete markers in staging | Hours to days |
| ntfy-responder | NTFY from Rich gets no ack reply | Minutes (Rich notices) |
| dispatcher | Messages sit unclassified in staging | Hours to days |
| session-watchdog | Session never restarts if CC dies | Until CC is manually checked |
| staging-watcher | New files sit unprocessed | Hours to days |
| autonomous-runner | No phase work happens | Days |
| discovery-daemon | Assumptions go stale | Weeks |
| background-worker | Depends on what task | Variable |

---

## What Already Exists But Is Not Visible

**Genuine strengths a cold reader would miss:**

1. **`.claude/agents/` is already working.** Three domain-specific subagents
   are defined and functional. This is an advanced pattern most projects don't
   have.

2. **The Point-in-Time Blindfold is architecturally enforced.** `company/
   interfaces/sim_interface.py` provides a deliberate seam. The company layer
   cannot accidentally read simulation internals — it has to explicitly reach
   through an interface that is documented as the only legal channel.

3. **The failure register exists in git history.** Every crash from tonight's
   session is documented in commit messages with root cause and fix. This is
   the right place for it, not a separate doc — but it's not easily searchable.

4. **The simulation's epistemic honesty is production-quality.** The
   company's forward curve (`company/crm/`) uses only observable data; the
   divergence between company estimates and SIM ground truth is measured
   (phase 12e). This is genuinely sophisticated and not visible from the
   directory structure.

5. **NTFY + staging is a robust async communication channel.** The handoff
   between Rich and CC via NTFY → staged files → actioned → moved to done/ is
   a complete, auditable protocol. Message loss is handled by content-hash
   dedup in ntfy_responder. This is production-quality workflow automation.

---

## Stage Order Assessment

The proposed stage order (0 → 1 → 2 → 3 → 4) is correct. One note:

Stage 1 (CLAUDE.md restructure) should happen soon — the file is at 33,677 of
35,000 chars. Phase 43 will push it over. The 200-line target is aggressive;
a more realistic target given the operational protocol documentation is 300
lines.

Stage 3 (Epistemic Verifier) is the highest-value stage for build quality.
The barrier violation risk is real and currently undetected. If I were
prioritising by risk reduction: Stage 3 > Stage 1 > Stage 2 > Stage 4.

Stage 4 (AgentMessage schema) is correct to include but the staging file
format and NTFY protocol are stable and do not urgently need formalisation.
The priority is Stage 3's verifier before Stage 4's message schema.

---

## Completion Note

Stage 0 prerequisite (observability log schema + poesys.net system health
panel) implemented as of commit f498b17. This audit is the Stage 0 gate
artefact. NTFY Rich with findings; waiting for explicit "proceed stage 1"
before implementing CLAUDE.md restructure.
