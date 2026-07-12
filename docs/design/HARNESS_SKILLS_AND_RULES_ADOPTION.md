# HARNESS_SKILLS_AND_RULES.md — adoption report

Verified against current official docs (`code.claude.com/docs/en/skills`, `.../en/memory`) via
WebFetch before building, per the staged doc's own non-negotiable — this environment is 2.1.207 and
the fetched pages confirmed the SKILL.md frontmatter fields and `.claude/rules/` path-matching syntax
match what was built below (no stale community-diagram assumptions).

## Adopted (4 of 5 candidates)

| Skill | Source | One-line reason |
|---|---|---|
| `phase-close` | CLAUDE.md's own "Phase-close checklist" section (items 0-7), moved out verbatim | Textbook case per the docs' own guidance: "a section of CLAUDE.md that has grown into a procedure rather than a fact" — freed ~4,000 chars / CLAUDE.md dropped from 134 to 120 lines |
| `staging-protocol` | CLAUDE.md's staging workflow bullets + R1/R7/R8 | Genuinely reusable, fires on every doorbell; the "check-then-put, re-fetch-and-hash ritual" the staged doc named has "been violated before" (duplicate-file re-materialization, this exact session, multiple times) |
| `cold-eyes-walk` | `docs/staging/in_progress/COLD_EYES_PROTOCOL.md`, verbatim | Real, substantial, reusable procedure already staged but never packaged; `context: fork` set so the blindfold is structural (a forked subagent literally cannot see the builder's own conversation), not just an instruction to ignore it |
| `incident-retro` | CLAUDE.md's retro-check trigger + the real format already used across `docs/retrospectives/*.md` | Reusable format that has produced this project's own R-rules; formalising it makes the R-rule-extraction step (§ "When this produces a new R-rule") explicit rather than an easily-skipped afterthought |

## Rejected (1 of 5 candidates)

| Candidate | Reason |
|---|---|
| `expert-hour-walk` | **Subsumed by `cold-eyes-walk`, not a separate skill.** `COLD_EYES_PROTOCOL.md`'s own text states it directly: "this upgrades the existing Expert-Hour simulation... same machinery, stricter blindfold." Expert Hour is cold-eyes-walk's technique applied specifically at HARDEN-stage level-promotion (`docs/design/MATURITY_MAP.md` §1-2); building a third near-identical skill would fragment one procedure across files, violating the staged doc's own "keep each small and single-purpose" instruction in the over-fragmentation direction. `cold-eyes-walk/SKILL.md` documents this relationship explicitly so a future reader doesn't independently propose the same skill again. |

## `.claude/rules/` (2 files, both path-scoped)

- `epistemic-wall-company.md` (`company/**/*.py`, `saas/**/*.py`) — fires the "could a real UK
  supplier know this?" reminder + point-in-time discipline + epistemic-verifier requirement whenever
  Claude works with company-layer code.
- `epistemic-wall-sim.md` (`sim/**/*.py`, `simulation/**/*.py`) — fires the baseline/curriculum split
  (R13) + `data_regime` field discipline + the crossing-direction warning whenever Claude works with
  world-layer code.

This is the single strongest use case the staged doc named: `sim/**` and `company/**` operate under
different laws, and a rule that fires only on path match is materially stronger than a CLAUDE.md
paragraph that must be remembered every session regardless of what's being touched.

## Demonstrated firing (real, not asserted)

- `phase-close` and `staging-protocol` invoked directly via the `Skill` tool this session — full
  content loaded into context, confirmed in the transcript.
- `cold-eyes-walk` and `incident-retro` confirmed discoverable (appeared in the harness's own
  available-skills listing immediately after creation, before this doc was even written).
- Path-scoped rules: per the fetched official docs, these inject silently into context on a matching
  `Read`/`Edit` (no visible confirmation message by design, unlike skills) — verified the trigger
  condition itself by reading `company/interfaces/sim_interface.py` in this same session; the
  mechanism's correctness rests on the documented behaviour (confirmed current via WebFetch), not on
  a directly-observable log line, since rules are designed as silent injection.

## CLAUDE.md slimmed where procedure moved out

134 lines / 34,840 chars → 120 lines / 30,773 chars. Procedure moved out (phase-close checklist);
facts and standing laws (R1-R14, architectural laws, the one-way-door list) stayed, per the docs'
own CLAUDE.md-vs-skill distinction ("facts Claude should hold every session" vs "a multi-step
procedure").

## Not built (rejected already, before this pass, no new assessment needed)

`.mcp.json` (no MCP servers), `commands/` (skills subsume commands per the current docs — "custom
commands have been merged into skills"), `output-styles/`, `CLAUDE.local.md` — all previously
assessed low-value in HARNESS_BEST_PRACTICE_ADOPTION.md (2026-07-10) and unchanged by this pass.
