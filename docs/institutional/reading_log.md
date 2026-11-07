# Reading log: external sources on building it

One entry per source the director shares or the reading rota reads. Each entry gives the source's
claim, how strong its evidence is, our verdict and what was done. Rejections stay in the log so
they are never argued again. Market and household sources do not go here; they belong in
`docs/market_research/` and `knowledge_map.md`. This log covers software, product and AI practice,
which sits under the "How it's built" spine (`docs/design/the_map/concepts.yaml`, `build`).

Set up on the director's 5 Nov steer
(`docs/staging/advisor/DIRECTOR_STEER_A_STANDING_EXTERNAL_READING_HABIT_AND_THE_KNOWLEDGE_TAB_TAKES_THE_MAPS_SHAPE_2026-11-05.md`, item 3).
The first block is the advisor's backfill for early October to 5 Nov. Sources whose verdict the
advisor could not reconstruct were left out rather than guessed.

**Evidence grades, weakest first:** vendor post · single author · book · peer-reviewed ·
multi-organisation data. Most of what reaches us is one of the first two.

**Verdicts:** adopt · adopt partly · already have · deferred · reject · not relevant · gap found.

**Appending:** add a row at the bottom with the date read. A recommendation from a source goes
through normal ranking and names the failure class or measured problem it addresses. Reading
alone never proposes a new gate.

| Read | Source | Claim, in short | Evidence | Verdict | What was done | Concept |
|---|---|---|---|---|---|---|
| Oct (backfill) | loki-mode (autonomous build harness repo) | A per-commit evidence record that keeps facts apart from judgement, with a headline computed from the facts | Single project | Deferred | Tested against our history: it would not have caught no-caller or stale figures. It led to the no-caller class count | Commit gate |
| Oct (backfill) | DeepSeek harness `AGENTS.md` | Agent rules for a large codebase | Vendor repo | Adopt three | Assert relationships, not presence; removability by construction; invariants in both directions; deterministic checks before judgement (addenda on the 29 Jul mothball ruling) | Checks that can fail |
| Oct (backfill) | WikiSkill (Google, arXiv 2608.27454) | Agents need raw experience, accumulated knowledge and executable code kept apart. The middle layer drives the gain | One paper, benchmarks, unreplicated | Adopt the idea | Class documents moved to `docs/staging/reference/` so the drain does not consume them | Learning |
| Oct (backfill) | GEPA (prompt evolution against an eval) | Tune instructions as trainable parameters | Paper and posts | **Reject** | It goal-seeks against our own score (R12, C1) | Outputs are diagnostics |
| Oct (backfill) | Product Talk on evals | Binary yes/no checks beat graded scores | Practitioner blog | Already have / adopt partly | Deterministic before judgement. Judge validation measures the model graders | Checks that can fail |
| Oct (backfill) | *Observability Engineering*, 2nd ed. (Majors, Fong-Jones, Miranda) | Wide structured events, the core analysis loop, SLOs | Book | Gap found | Our run ledger exists and nothing calls it, so we fail the arbitrary-question test (`ADVISOR_FINDINGS_THE_HARNESS_HAS_NO_WIDE_EVENT..._2026-10-11`) | Observability |
| Oct (backfill) | Merge-queue post (LinkedIn) | Batch changes and bisect on failure | Single author | Question staged | `ADVISOR_QUESTION_WOULD_BATCH_THEN_BISECT_LANDING_CUT_GATE_TIME_2026-10-15` | Commit gate |
| Oct (backfill) | Anthropic, "Solving code review at Anthropic" | Parallel bug hunters, verifier votes, risk tiers, incidents as evals | Vendor, internal data | Adopt as a trial | Two-reader trial: one reader caught 1 of 5 known-bad commits; two agreeing readers flagged 4 of 5 bad and 0 of 5 clean. Now runs on qualifying commits | Independent review |
| Oct (backfill) | Google Harness² (recursive harness tuning) | Rewrite the harness files per task, from behavioural contrast | Paper, benchmarks | **Reject** | Self-tuning again, and its gains go to weak models | Outputs are diagnostics |
| Oct (backfill) | MIT Technology Review / Snowflake, data engineering | Data engineers move to AI; synthetic-data quality is a top worry | Sponsored survey | Nothing to adopt | Positioning only: our validation ladder answers the synthetic-data worry | — |
| Oct (backfill) | AWS Lambda Web Functions | Lambda runs normal web servers | Vendor | Not relevant | Poesys has no cloud functions | — |
| Oct (backfill) | Anthropic, "When to fold subagents into your main agent loop" | A single loop with skills beats org-chart subagents. Keep agents for checking, parallelism and permissions | Vendor, customer cases | Already have | Serial by default; context halved 23 Oct; the reader trial justifies the checking agents | Agents and models |
| Oct (backfill) | Anthropic, "The AI-Native SDLC Playbook" (Claxton) | Intent, spec and plan artefacts; hooks; continuous evals; review on every PR | Vendor guide | Mostly have | Gap: no eval re-runs when CLAUDE.md, skills or hooks change | Delivery and CI |
| Oct–Nov (backfill) | Predbat (springfall2008/batpred) | Home battery planner. Personal-use licence: ideas only, no code | Open repo, mature | Adopt two ideas, queued | A replayable run snapshot; a test-order hunt (ruled 3 Nov). Also a knowledge source for asset optimisation | Testing and controls |
| Nov (backfill) | Google Elephant-Goldfish model | Fresh-context reviewers read a design before it is built | Vendor, "thousands" of users, no metrics | Adopt | A design read before build (2 Nov). Its first read found 7 defects in the value-test design | Independent review |
| Oct (backfill) | Graph and taxonomy technologies (OGM/Neo4j, GraphQL, SKOS, semantic layer, AST) | Ways to abstract nodes and taxonomies | General | Adopt two ideas, no tooling | SKOS fields; one computable definition per measure (24 Oct) | One source of truth |
| Nov (backfill) | NVIDIA Auto Ontology | A model extracts a business ontology from databases, with certified definitions | Vendor repo | No tooling; one idea | Propose then certify, for drafting the register (ruled 3 Nov) | One source of truth |
| 5 Nov (backfill) | Mc Gowan, "Review Gates for Code You Didn't Write" | Over 336 PRs, size predicts must-fix findings and path does not; gates only grow | Single author, own data | Adopt as calibration | For 11 Nov: calibrate the reader selector on our own history, and report what each gate caught (staged 5 Nov) | Commit gate |
| 7 Nov | `agent-estimate` (kiloloop), a Claude Code plugin for effort estimates | Estimates agent task time from per-model limits | Single maintainer, alpha; its model limits are labelled by its author "Local policy (unmeasured)"; accuracy evidence anecdotal (one 4–8x over-estimate) | **Reject** | Third-party, not Anthropic's. Its limits are picked numbers presented as estimates: "a number you need is a question to research, never a value to pick". Pacing estimates come from our own session records, through the token measurement (`DIRECTOR_STEER_MEASURE_WHERE_READING_TOKENS_GO..._2026-11-07`) | Agents and models |
| 7 Nov | Anthropic official plugin marketplace (`claude-plugins-official`): `pyright-lsp`, `code-review` | Language-server navigation instead of grep-and-read; a packaged PR review | Vendor | Trial, queued | `pyright-lsp` trialled inside the token measurement; `code-review` compared with our two readers on the labelled set at the 11 Nov review (`DIRECTOR_STEER_OFFICIAL_PLUGINS_EARN_THEIR_PLACE..._2026-11-07`) | Agents and models |
