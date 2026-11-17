**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The CLAUDE.md trial uses a golden set run twice, and each handoff earns its place (2026-11-17)

**Type:** STEER, through the advisor channel. It amends `DIRECTOR_STEER_TEST_CLAUDE_MD_BY_DELETING_AND_ADDING_BACK_AND_AUDIT_WHAT_EACH_SEAT_LOADS_2026-11-15.md` before its trial starts (pre-registered for 21 Nov). The director's words, from chat on Tue 17 Nov:

- 15:12 GMT, sharing https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop with no comment.
- 17:57 GMT, on the advisor's recommendation below: "Yes"

## What the advisor found (check it)

- **The source.** Anthropic, "Building agents: when to fold subagents into your main agent loop" (Diane Sarkis, 22 Oct 2026). Many multi-agent systems do better as one loop with progressively disclosed skills and tools.
  - Warning signs: "the agent architecture becoming a copy of their org chart", and "Each call still hands back a lossy summary".
  - One customer saw "roughly 2x faster runtime" with a single loop.
  - Method: build a small end-to-end eval (about 10 golden examples), fold one subagent at a time, and "keep it as a subagent only if the folded version scores worse".
  - Run each eval task more than once: in their sample, a folding failure appeared in only one of two runs.
  - Tool choice degrades past 30–50 tool definitions.
- **Against us:**
  - Nested subagents are already rare: 0.1% of context tokens in the 7–14 Nov week, at a ~36k fixed cost per call.
  - Our separation is in seats and written handoffs: advisor steer, seat draw, executor build, reviewer check.
  - Six specialist agent types are defined in `.claude/agents/`: `discovery-agent`, `epistemic-verifier`, `interface-steward`, `phase-close-evaluator`, `saas-engineer`, `sim-engineer`.
  - Lanes (A–W5) are classification labels, not agents.
  - **One reason for separation the article does not name holds here: an information barrier.** The company side must not see world internals (the epistemic wall), and blind reviewers must not see the work being produced. Separation that is a barrier stays, whatever a fold would save.

## The amendment

1. **A golden set for the CLAUDE.md trial.** Before 21 Nov, choose about 10 representative seat tasks. Cover at least:
   - a staging draw;
   - a fidelity change near the wall;
   - a commit through the gates;
   - a knowledge-first build;
   - an escalation that must reach `for_the_director` with a recommendation;
   - a G5 refusal;
   - an interconnection review after a landing.

   Fix each task's inputs and its pass criteria in advance. **Run each task twice** on the full file and twice on the minimal file. A line is added back if its absence fails a task in either run. Real-turn comparisons stay as a secondary check, not the decider. Report each run, not only the totals.
2. **A one-off inventory of every handoff and specialist agent:** the six agent types, each seat and daemon kind, and each written handoff between them. Mark each one:
   - **keep: information barrier** (name the barrier); or
   - **keep: measured benefit** (parallelism, context isolation, a different model), with the measurement; or
   - **candidate to fold.**

   Candidates are folded one at a time, through the same golden set run twice, and kept separate only if the folded version scores worse. No fold that weakens the epistemic wall or a blind review, whatever it scores.
3. **The tool count.** Report the tool definitions each seat kind carries after the 16 Nov switch-offs, against the article's 30–50 degradation band.

## Reading-log entry to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-17 | Anthropic, "Building agents: when to fold subagents into your main agent loop" (Sarkis, 22 Oct) | Director | Nested subagents are already rare here. The useful parts are the method (golden set, fold one at a time, keep only if folding scores worse, run each task twice) and the org-chart warning. Information barriers (the wall, blind review) are a reason to stay separate that the article does not name. | ADAPT (amends the CLAUDE.md trial) |

## Risk

Touches: the CLAUDE.md trial's design, a read-only inventory, and later one-at-a-time fold trials.
Blast radius: none until a fold is tried.
Probable failure modes:
- **A golden set chosen to be easy.** Include the escalation and G5 cases, where a dropped line would show.
- **A fold that quietly leaks across a barrier.** Barrier-marked handoffs are never fold candidates.

Proportionality: harness, reversible. Implement directly.

— Director steer, 17 Nov 2026, his words above; the reading and drafting are the advisor's.
