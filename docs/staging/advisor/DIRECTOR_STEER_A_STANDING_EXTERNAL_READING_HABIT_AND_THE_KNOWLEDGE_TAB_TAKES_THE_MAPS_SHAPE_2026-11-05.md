**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] A standing external reading habit, and the Knowledge tab takes the map's shape (2026-11-05)

**Type:** STEER, through the advisor channel. The director's words, from chat on Thu 5 Nov:

- 07:22 GMT: "we create primary knowledge categories about how the market works, but we don't capture insight about software engineering and agentic/AI best practice. I don't want to divert too much resource and effort to this but it seems logical to capture it and gather it more formally than the a hoc articles I keep posting."
- 07:32 GMT: "What about a periodic external exploration? Especially anything new from anthropic. Plus perhaps research related to the issue and failure categories we have? And generally building knowledge around software building and AI. Martyn cagan etc. Ontology, taxonomy, APIs, architecture etc."
- 07:35 GMT: "So knowledge is divided into simulation, supplier and code/harness? Does the website tab structrue still make sense? How will the knowledge tab be structured?"
- 07:36 GMT, on the advisor's recommendation covering all of the below: "Do it"

**When:** item 3, the reading log, starts now. The advisor has written the backfill below. Items 1 and 2 queue behind the correctness exit test. Rank them yourself.

## 1. A standing external reading habit, with a hard budget

- **Weekly, small: what's new from Anthropic.** Read the news and engineering blog, the Claude Code release notes and documentation changes, and claude.com/resources. One line in the Monday note: what changed, and whether it changes anything we do. "Nothing that changes what we do" is a full answer.
- **Monthly, about one session, alternating between two rotas:**
  - **(a) Our failure classes.** The nine `docs/staging/reference/CLASS_*` documents, one class a month. Cover what the published field knows (dead-code detection, mutation testing, single source of truth, flaky and order-dependent tests, semantic layers, validating model judges, and so on) and how we compare. Give at most three recommendations, each naming the class and the measured problem it addresses.
  - **(b) The wider craft.** Product (Cagan: the four risks of value, usability, feasibility and viability, set against M2), domain-driven design (Evans: ubiquitous language against the several-homes class, and bounded contexts against the wall), ontology and taxonomy, APIs and architecture, testing, observability, and agents and evaluation.
- **Guardrails:**
  - No hunting beyond this rota.
  - A recommendation goes through your normal ranking. Only what needs him reaches `for_the_director`.
  - Proposing a new gate from reading alone is out. Report what each pass spent, under P12.
  - Grade evidence honestly: vendor post, single author, book, peer-reviewed, or multi-organisation data. Most of what reaches us is the first two.

## 2. The Knowledge tab takes the map's shape

Today two classifications cover the same pages: the Knowledge tab's six domains and the map's four spines (`docs/design/the_map/concepts.yaml`). That is the several-homes class in our own filing. Engineering and AI practice has no home on the site at all.

The advisor's proposal, which he agreed; the shape is yours to refine:
- **The world:** markets, prices and households. Today's "Markets and prices" and "Households and their homes" sit under it as second-level groups, with "Other markets" as reference.
- **Running a supplier:** "Winning and serving customers" and "Metering, billing, debt and regulation" sit under it, with accounts and capital. This joins the map's supplier and company spines.
- **Building it:** software, product and AI practice, and the reading log's published side. This is the map's "How it's built" spine (today four concepts: checks that can fail, the commit gate, dead code, one source of truth).

Rules for the reshape:
- **Carbon** becomes a cross-cutting filter, not a section.
- **Knowledge and insight** stay labels (the 4 Nov facets), with a "What we've learned" filter across all three sections. **Method insight** belongs there too: the improvement loop's results, published as insight with status and trust. That includes the "we cannot tell" results and the experiments that failed. M4 says the method is the asset, and this is its evidence.
- **One classification, not two.** The map's register drives the tab, and the six domains become the second level. Nothing is deleted; it moves.
- **Each control-stack box on How it's built links to its practice page in "Building it",** and back.
- The other tabs keep their jobs: How it's built (the machine, live), The code (the galaxy), Capabilities, Explore.

## 3. The reading log

One entry per source: what it claims, the evidence grade, our verdict (adopt / already have / reject, with the reason), what was done, and the map concept it belongs to. Rejections are kept so they are never relitigated. Choose its home: one file in the knowledge layer, with the published side under "Building it". The advisor appends an entry for each source the director shares. The backfill below covers sources reviewed in the advisor chat from early October to 5 Nov, as best the advisor's record holds. Sources whose verdict the advisor could not reconstruct are left out rather than guessed.

| Source | Claim, in short | Evidence | Verdict | What was done / concept |
|---|---|---|---|---|
| loki-mode (autonomous build harness repo) | Per-commit evidence record: facts apart from judgement, a headline computed from the facts | Single project | Deferred | Tested against our history: it would not have caught no-caller or stale figures. Led to the no-caller class count. Concept: commit gate |
| DeepSeek harness `AGENTS.md` | Agent rules for a large codebase | Vendor repo | Adopt three | Assert relationships, not presence; removability by construction; invariants both directions; deterministic before judgement (addenda on the 29 Jul mothball ruling). Concept: checks that can fail |
| WikiSkill (Google, arXiv 2608.27454) | Agents need raw experience, accumulated knowledge and the executable kept apart; the middle layer drives the gain | One paper, benchmarks, unreplicated | Adopt idea | Class documents moved to `docs/staging/reference/` so the drain does not consume them. Concept: learning |
| GEPA (prompt evolution against an eval) | Tune instructions as trainable parameters | Paper and posts | **Reject** | Goal-seeking against our own score (R12, C1). Concept: outputs are diagnostics |
| Product Talk on evals | Binary yes/no checks beat graded scores | Practitioner blog | Already have / adopt partly | Deterministic before judgement. Judge validation measures the model graders |
| Observability Engineering, 2nd ed. (Majors, Fong-Jones, Miranda) | Wide structured events, the core analysis loop, SLOs | Book | Gap found | Our run ledger exists and nothing calls it. We fail the arbitrary-question test (`ADVISOR_FINDINGS_THE_HARNESS_HAS_NO_WIDE_EVENT..._2026-10-11`). Concept: observability |
| Merge-queue post (LinkedIn) | Batch changes and bisect on failure | Single author | Question staged | `ADVISOR_QUESTION_WOULD_BATCH_THEN_BISECT_LANDING_CUT_GATE_TIME_2026-10-15`. Concept: commit gate |
| Anthropic, "Solving code review at Anthropic" | Parallel bug hunters, verifier votes, risk tiers, incidents as evals | Vendor, internal data | Adopt as a trial | Two-reader trial: one reader caught 1 of 5 known-bad commits; two agreeing readers flagged 4 of 5 bad and 0 of 5 clean. Now running on qualifying commits. Concept: independent review |
| Google Harness² (recursive harness tuning) | Rewrite the harness files per task from behavioural contrast | Paper, benchmarks | **Reject** | Self-tuning again. Its gains go to weak models. Concept: outputs are diagnostics |
| MIT Technology Review / Snowflake, data engineering | Data engineers move to AI; synthetic data quality is a top worry | Sponsored survey | Nothing to adopt | Positioning only: our validation ladder answers the synthetic-data worry |
| AWS Lambda Web Functions | Lambda runs normal web servers | Vendor | Not relevant | No cloud functions in Poesys |
| Anthropic, "When to fold subagents into your main agent loop" | A single loop with skills beats org-chart subagents; keep agents for checking, parallelism and permissions | Vendor, customer cases | Already have | Serial by default; context halved 23 Oct; checking agents justified by the reader trial. Concept: agents and models |
| Anthropic, "The AI-Native SDLC Playbook" (Claxton) | Intent, spec, plan artefacts; hooks; continuous evals; review on every PR | Vendor guide | Mostly have | Gap: no eval re-run when CLAUDE.md, skills or hooks change. Concept: delivery and CI |
| Predbat (springfall2008/batpred) | Home battery planner. Personal-use licence: ideas only, no code | Open repo, mature | Adopt two ideas, queued | Replayable run snapshot; test-order hunt (ruled 3 Nov). Also a knowledge source for asset optimisation |
| Google Elephant-Goldfish model | Fresh-context reviewers read a design before build | Vendor, "thousands" of users, no metrics | Adopt | A design read before build (2 Nov). Its first read found 7 defects in the value-test design. Concept: independent review |
| Graph and taxonomy technologies (OGM/Neo4j, GraphQL, SKOS, semantic layer, AST) | Ways to abstract nodes and taxonomies | General | Adopt two ideas, no tooling | SKOS fields; one computable definition per measure (24 Oct). Concept: one source of truth |
| NVIDIA Auto Ontology | A model extracts a business ontology from databases; certified definitions | Vendor repo | No tooling; one idea | Propose then certify, for drafting the register (ruled 3 Nov). Concept: one source of truth |
| Mc Gowan, "Review Gates for Code You Didn't Write" (5 Nov) | 336 PRs: size predicts must-fix findings, path does not; gates only grow | Single author, own data | Adopt as calibration | For 11 Nov: calibrate the reader selector on our history, and report what each gate caught (staged 5 Nov). Concept: commit gate |

## Risk

Touches: a reading habit within the weekly rhythm, the Knowledge tab's structure and index, and one new log.
Blast radius: one public tab reorganised (nothing deleted), plus a bounded reading spend.
Probable failure modes:
- **Reading becoming a feature queue.** Mitigation: each recommendation names a class or measured problem; there is a hard budget; it goes through normal ranking.
- **Two classifications surviving the reshape.** Mitigation: the register drives the tab, and the domains become a level, not a parallel scheme.

Proportionality: reversible and narrow — just do it.

— Director steer, 5 Nov 2026, his words above; the design, the backfill and the drafting are the advisor's.
