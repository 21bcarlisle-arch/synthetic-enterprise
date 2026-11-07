**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Abstraction is one research family, and a census of our descriptions (2026-11-07)

**Type:** STEER, through the advisor channel. It adds to `DIRECTOR_STEER_A_STANDING_EXTERNAL_READING_HABIT_AND_THE_KNOWLEDGE_TAB_TAKES_THE_MAPS_SHAPE_2026-11-05.md` and links to `..._MEASURE_WHERE_READING_TOKENS_GO_BEFORE_SPLITTING_ANY_FILE_2026-11-07.md`. The director's words, from chat on Sat 7 Nov:

- 06:25 GMT: "How does this link to other topics. Knowledge, ontology, taxonomy, the code map etc. Should we have perhaps research these topics as part of our harness knowledge base, including abstraction?"
- 06:27 GMT: "Are there software or methods of code abstraction. I'm sure there was an acronym I researched previously, a meta layer. How does this link to knowledge graphs etc. also dimensional models."
- 06:28 GMT, on the advisor's recommendation below: "Add it. (AST was the acronym)"

**When:** with the reading habit, behind the correctness exit test. No build now.

## 1. One research family in the monthly rota

Each of these is a small, trustworthy description that lets an agent or reader work with something large without reading all of it. Research them as one family under "Building it", not as separate topics.

| Abstraction | Over what | Ours today |
|---|---|---|
| Ontology and taxonomy | What things mean | The map's concept register |
| Knowledge graph | How things relate | The map, partly |
| AST and code graphs (code property graphs; SCIP/LSIF symbol indexes; call and dependency graphs) | How code relates | The code galaxy, `tools/capability_index.py` |
| Interfaces and deep modules (Parnas 1972; Ousterhout, *A Philosophy of Software Design*) | What a module does | Mostly absent (see the token measurement) |
| Architecture as code (C4 and Structurizr; import-linter and ArchUnit) | Layers and allowed dependencies | The wall's checks |
| Meta levels (OMG MOF/MDA: M0 to M3) | Models of models | None |
| Dimensional models (Kimball facts and dimensions) | What happened, for analysis | **Missing:** the run ledger has no caller |
| Semantic layer | Each measure, defined once over the facts | "One definition per measure", 24 Oct |

They share one payoff: less reading, which saves tokens, and one definition, which saves errors. They share one failure: the description drifts from the thing. Our stale-copy, several-homes and canon-drift classes, and the hand-typed test count, are all that failure. They share one remedy: generate the description from the thing, or check it against the thing.

## 2. Its first deep dive: a census of our descriptions

For each description we keep, say whether it is **generated** from the thing, **checked** against it, or **neither**. That covers:
- knowledge pages;
- the concept register;
- the code galaxy;
- the capability index;
- module docstrings and interfaces;
- canon;
- CLAUDE.md;
- memory pointers;
- the site's figures;
- the maturity map;
- and any others you find.

Rank the "neither" ones by what their drift would cost. They are where the next drift failure will come from.

## 3. One trial join, after the census

Join the code graph to the concept register for one measure, bill shock being the obvious candidate. Trace concept, then measure definition, then the function or functions computing it, then the facts it reads, then the pages that publish it. Two of our worst classes become graph shapes:
- two functions behind one measure is several homes;
- a function with no path to anything published is no caller.

Report whether the join finds anything the current checks do not. If it does, say what it would take to run it for every measure. If not, say so.

The dimensional fact table of runs and decisions is the larger step. It is the observability gap from 11 Oct, and it is not asked for here. Say where it should rank once the census is in.

## Risk

Touches: the reading rota, and a read of our own descriptions. The trial join is a read-only analysis.
Blast radius: none until a recommendation is acted on.
Probable failure mode: a census that marks something "checked" because a test exists near it, when the test does not compare the description to the thing. Mark "checked" only when a control would go red on drift, and prove one.
Proportionality: reversible and narrow — just do it.

— Director steer, 7 Nov 2026, his words above; the framing and drafting are the advisor's.
