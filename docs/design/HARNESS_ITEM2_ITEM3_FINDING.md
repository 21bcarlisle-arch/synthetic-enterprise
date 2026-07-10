# HARNESS_BEST_PRACTICE_ADOPTION.md items 2 & 3 — status

## Item 2: fresh-context evaluator subagent

Sequenced after item 1 per the staged instruction's own ordering — item 1 (all three hooks,
a/b/c) landed this session, so item 2 was picked up.

**Studied the reference first, per the instruction's own requirement** (`gh repo view
anthropics/cwc-long-running-agents`, real fetch not guessed): the repo ships three primitives
(default-FAIL contract, fresh-context evaluator, agent-maintained handoff) as example hooks +
a subagent, and explicitly recommends comparing against the built-in `/goal` command before
building bespoke. Confirmed real via the repo's own README: `/goal` runs a generic fast-model
completion-condition check; the repo's `agents/evaluator.md` pattern is a project-tailored,
skeptical, no-Write/Edit reviewer with its own rubric. Decision: **adopt the bespoke pattern, not
`/goal`**, matching "prefer built-ins over bespoke where they fit" but recognising this project's
own phase-close bar (CLAUDE.md's checklist, R1-R13, the default-FAIL maturity-map contract) is
specific and judgement-heavy enough that a generic completion-condition checker doesn't fit —
the same reasoning this project already applied when it built `epistemic-verifier` as a
purpose-built subagent rather than relying on a generic check.

**Built:** `.claude/agents/phase-close-evaluator.md`, adapted from the repo's real
`agents/evaluator.md` (no Write/Edit tools; reads the diff + claimed evidence; returns bare
`PASS`/`NEEDS_WORK`; explicitly told not to trust the builder's own assessment), with this
project's own phase-close checklist and R1-R13 substituted for the generic "spec or acceptance
criteria" the reference repo assumes.

**Initial limitation found, then corrected (both stages honestly recorded, not just the final
answer):** attempted to invoke it (`Agent` tool, `subagent_type: "phase-close-evaluator"`)
immediately after creating the file — it was NOT available. Confirmed via a second, independent
check (a fresh `general-purpose` subagent asked to list its own visible agent types) that this
wasn't a fluke of my own session's cache. Concluded at the time: agent-type registration happens
once, at the top-level Claude Code process's own start, requiring a full process restart.
**That conclusion was wrong** — a later system notification confirmed the new agent type became
available in the SAME session, with no restart, after some interval had passed (the registry
evidently refreshes periodically, not only at process start). Corrected here rather than left
standing.

**Demonstrated working for real, same session:** invoked `phase-close-evaluator` against the
actual commit `7b02343c` once it became available. It returned a genuine `NEEDS_WORK` verdict
with real, independently-verified findings (not false positives) — see PRIORITIES.md's own entry
logging exactly what it found (PROJECT_OVERVIEW.md Section 4/10 not updated; the new bill-shock
YoY fields shipped with zero test coverage; a real semantic edge-case bug in the seasonal
heuristic, found via the evaluator's own manual smoke-test; no business surface consumed the new
fields) and how each was fixed. R1 (consumer-verified completion) is now actually satisfied: the
evaluator is confirmed invokable and its output was acted on, not just claimed as built.

## Item 3: resilience settings review

`fallbackModel` chaining: already added earlier this session (`.claude/settings.json`).

**Session-cap / auto-compaction vs `/clear` habits:** no explicit session-length/turn cap is
configured in `.claude/settings.json` or `settings.local.json` (checked, not assumed — grepped
for `session-cap`/`autoCompact`/`maxTurns`/`contextWindow`, no hits). This project's own existing
pattern already matches the cwc repo's "Going further" **Unattended loop** pattern
("Cap session length and have an outer script start the next one") without an explicit setting:
`background/session_watchdog.py` auto-restarts a fresh Claude Code session after a usage-limit
reset, and CLAUDE.md's own "Key learnings" section already notes "Session usage window is ~5
hours." No new setting is being added here — the existing watchdog-restart cycle already serves
this role, and this review found no gap worth building around it.

**Native parallel subagents as input to the pending parallel-lanes proposal:** already in active
use this session, not just proposed -- three parallel research forks were dispatched this session
(B2 category 4/5/6 anchor research) via the `Agent` tool with `subagent_type: "fork"`, each
running independently and reporting back without polluting the main session's context. This is
real, first-party evidence the native mechanism already fits this project's single-writer
discipline (forks/subagents don't write to the shared working tree directly; only the
orchestrating session commits) -- worth citing as a concrete precedent if/when the parallel-lanes
proposal itself is picked up, not a reason to build a bespoke lane mechanism.
