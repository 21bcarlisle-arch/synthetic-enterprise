# HARNESS: skills/ and path-scoped rules/ — the two gaps left (P2, non-interrupting)

**Staged:** 2026-07-12 by advisor, director-raised (published Claude Code
project-structure guidance). **Do NOT interrupt the self-refill draw** — take
at the next natural boundary; D2/epoch-2 atoms outrank this.

## Context (already checked — do not re-derive)
HARNESS_BEST_PRACTICE_ADOPTION (2026-07-10) is CLOSED: hooks, fresh-context
evaluator, fallbackModel, routines pilot, pruning ritual all done. Current
structure has: CLAUDE.md (134 lines, within the <200 guidance), .claude/hooks/,
.claude/agents/ (with per-agent model assignment — ahead of published practice),
settings.json, settings.local.json, .gitignore. Not needed: .mcp.json (no MCP
servers). Low value here: commands/, output-styles/, CLAUDE.local.md.

**Two genuine gaps remain.** Verify against CURRENT official docs
(code.claude.com) before building — published community diagrams may be stale,
and this environment moves fast (we are on 2.1.207).

## 1. `.claude/skills/` — model-invoked, loaded on demand (higher value)
We carry substantial PROCEDURE as prose in CLAUDE.md or as tribal memory. Skills
are the right home: loaded on demand, self-contained, decay-resistant — and they
directly serve the MAKE_IT_STICK law (mechanism, not memory) and the
just-in-time-constraints recommendation from the June harness review that was
never implemented.

Candidate skills (assess, adopt what fits, reject with reasons):
- **cold-eyes walk** — the blindfolded persona review (COLD_EYES_PROTOCOL):
  priors-before-pixels, artefact-only, "what would you doubt first".
- **phase-close / level-promotion** — the evidence bar for moving an atom up a
  level, incl. the honest-hold discipline.
- **staging protocol + R1 verification** — the check-then-put, re-fetch-and-hash
  ritual (currently prose; it has been violated before).
- **expert-hour walk** — the persona tour with the plausibility anchors.
- **incident retro** — the retro format that has produced the R-rules.
Keep each small and single-purpose. Report which you adopted and which you
rejected, with one-line reasons.

## 2. `.claude/rules/` — path-scoped context (loads only on path match)
The strongest use in this project is the epistemic wall itself: `sim/**` and
`company/**` operate under DIFFERENT LAWS. A rule that fires only when the agent
touches `company/**` (reminding it what it may not read, and that customer truth
is discovered through interfaces) is materially stronger than a paragraph in
CLAUDE.md that must be remembered. Same for `saas/**` and the settlement paths.
This complements — does not replace — the hook-level enforcement and the
lane-profile work.

## Non-negotiables
- Verify the mechanisms against current official docs before building (the
  2026-07-10 assessment did exactly this with a claude-code-guide agent — same
  standard).
- Do not bloat CLAUDE.md: moving procedure OUT of it into skills is the point.
- Anything adopted must be individually testable and removable (the pruning
  ritual applies).

## DoD
Skills and rules created (or explicitly rejected with reasons); CLAUDE.md
slimmed where procedure moved out; each new piece demonstrated firing once in
the logs; one digest line. Registered as a Lane-H atom, not a fire-drill.
