**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The map's register borrows SKOS's fields, and each measure carries one computable definition (2026-10-24)

**Type:** STEER, through the advisor channel. It adds to `DIRECTOR_STEER_THE_MAP_ONE_CONCEPT_REGISTER_FOUR_SPINES_AND_A_KNOWLEDGE_PLAN_2026-10-24.md` and is an input to your design proposal (its item 1). It is not a separate build. The director's words, from chat on Sat 24 Oct:

- 15:39 BST, sharing a list of graph and taxonomy technologies (OGM and Neo4j, GraphQL and Apollo, SKOS, semantic layers, AST): "We've staged an improvement to knowledge and ontology. But are any of these of use too?"
- 15:44 BST, on the advisor's recommendation to borrow two ideas and adopt no tooling: "Yes"

## The advisor's reading, which he agreed

The map steer already says "no heavy ontology tooling", and with roughly 100–150 concepts that holds. A graph database or object-graph mapper would add a service and a second copy of the truth. GraphQL solves a problem this project does not have: there is no live API and the site is generated at publish. Code structure (AST) is already in use through the module graph and the reuse index. Two ideas are worth borrowing, and only as ideas.

## 1. SKOS's field vocabulary for the register

SKOS is the W3C standard model for taxonomies and thesauri. Consider giving each register concept its well-known fields:
- one preferred name, and its alternative names;
- a definition;
- broader, narrower and related links;
- a match to an outside scheme, such as a BSC defined term, a licence condition or a Bacs definition.

Why this matters here:
- **Alternative names** address the most expensive recurring defect: one word quietly meaning two things (bill shock, average unit rate, net margin). A concept that has two names, or two concepts sharing one name, becomes something a check can find.
- **External matches** make "taken from how the industry defines itself" checkable.
- Humans and agents already know these field names, so nothing new has to be learned.

SKOS covers hierarchy and association only. The map's causal relations ("feeds", "depends on", "graded by", "causes") stay ours. No RDF, triple store or SKOS tooling is implied: borrow the field names, keep the register in whatever light format you choose.

## 2. One computable definition per measure (the semantic-layer pattern)

BI semantic layers (Looker's LookML, Cube) define a business measure once, and every chart and report computes from that single definition. That is the shape of the failure CLAUDE.md calls this project's most expensive: "a concept nobody defined, then differenced, published and treated as a driver."

Consider: every register concept that is a **measure**, such as net margin, average unit rate, bill shock or the switching rate, carries its one definition. That means what it counts, over which population, and the code that computes it. Every published figure that uses the measure is then traceable to it. A coverage check can then find a measure computed in two places, or a published figure attached to no definition. This joins rather than replaces what already holds part of it: the one-home rule, `tools/world_claims.py`, and the basis gate on financial figures.

## Yours to decide

Whether either idea fits your design, and in what form. If the pilot on Collect shows one of them earns nothing, say so in the stretch log and drop it.

## Risk

Touches: the map's design proposal only. No code is implied by this file.
Blast radius: none until the design is built.
Probable failure mode: the register growing heavy, with every field filled for its own sake. Fill a field when a check or a reader uses it.
Proportionality: reversible and narrow — just do it.

— Director steer, 24 Oct 2026, his words above; the reading and drafting are the advisor's.
