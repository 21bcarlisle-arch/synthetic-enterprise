**Severity:** BLOCKING · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The map: one concept register, four spines, generated links and gap checks, and a forward knowledge plan (2026-10-24)

**Type:** STEER, through the advisor channel. He reviewed two rounds of the advisor's mock-up in between. The director's words, from chat on Sat 24 Oct:

- 11:28 BST: "Is there a forward plan for knowledge either independently or as part of the work intended ?"
- 12:21 BST: "Also is there knowledge for the main things already built?"
- 12:30 BST: "Is it worth converting some or all of the 200 research notes too into pages? How can we tie all this together into some structure? Ontology or taxonomy? Or feature architecture? Or a bit of both? How can humans and AI understand and interrogate, with interconnections of knowledge maps above the interconnectiion of the SIM and then supplier beneath? Im not sure which comes first? Is the structure an output or an input?? Or a bit of both???"
- 12:38 BST: "It's really good. How does CLV and premise level usage, bills, payment and margin forecasting work. You've included code but what about data (for decision making etc)? What about recommendations … and then asset optimisation (EV charging and battery control)?"
- 13:04 BST: "Does it work for both SIM and supplier or is this just for supplier? Does all knowledge wr have fit somewhere? Do all main features of sim and supplier link somewhere? Should there be a kbowledge section for harness and code itself? Where we learn and apply best practice of both AI coding but also general IT/data best practice ??"
- 13:05 BST: "Like it. Do that. With some topic interconnections below potentially?"

**When:** design proposal and pilot first, after the Monday 26 Oct publish work. The pilot is payments and direct debit, the current top priority and the biggest knowledge gap, plus one slice of How it's built (testing and controls). The full build follows once the pilot holds.

**The design he approved:** the advisor's interactive mock-up, committed at `docs/design/the_map_mockup_2026-10-24/Main.dc.html`. It is a reference for shape and behaviour. Its module names, line counts and call status are real (24 Oct census). Its links were matched by hand, which is the part you replace with generated links.

---

## The structure: a small input, a large output

**Input.** A small concept register, curated and changed only deliberately: about 100–150 concepts, taken from how the industry and the field define themselves (BSC, SLCs, REC, Bacs; for How it's built, established engineering practice). Each concept has an id, a plain name, its source, a one-line definition and its relations to other concepts ("feeds", "depends on", "graded by", "causes"). This is the ontology core.

**Four spines,** the views over that register:
1. **The world:** markets and physics (weather → demand → generation and merit order → wholesale price → settlement); households (who lives where → home physics → finances and life events → choices).
2. **The supplier's value chain:** acquire, switch, meter, bill, collect, settle, hedge, renew or lose, move, **advise, optimise**.
3. **Running the company:** accounts, capital, trading risk, regulation, vulnerability, complaints.
4. **How it's built:** testing and controls, delivery and CI, agents and models, data and lineage, security, observability.

A concept may sit on more than one spine. The wall is where the world and supplier spines meet.

**Layers per concept.**
- World and supplier spines: knowledge (published page, research notes) → world rule → what crosses the wall → supplier feature.
- Supplier spine, below those layers: **beliefs and decisions**. Each forecast or model the supplier decides on is a data product, shown as what it is built from, then the code, then the decisions it feeds, then its grade against hidden truth. Examples: the consumption forecast per property, the forward cash forecast, CLV, can't-pay versus won't-pay, next best action, "does this home have an EV".
- How it's built: established practice with sources (for example DORA, the Google SRE book, Fowler, mutation-testing literature, Anthropic's Claude Code guidance) → our rule → what enforces it → what the record shows.

**Output, all generated:**
- which pages, notes, modules, tests, atoms, controls and claims attach to which concept, read from references the code and documents already carry or will carry;
- every gap: a concept missing a layer, a page or note on no concept, a module on no concept that is not declared machinery, a belief with no grade, a practice the record goes against;
- the topic interconnections, from the register's relations.

## WORK THIS CREATES

1. **Your own design proposal first.** Use the mock-up as a sketch, not a specification. Decide:
   - the register's format and home, kept light: no heavy ontology tooling;
   - how links are generated, and what declaration a module or note needs to attach;
   - which existing pieces it absorbs or joins: the knowledge map (`docs/institutional/knowledge_map.md`, hand-kept today), `tools/world_claims.py`, the world-constant anchor register, the capability index and orphan register, the module graph, the maturity map, the Explore cast, and the other advisor chat's control stack and "learned from the record" work.

   One home per thing: a piece the map absorbs stops being a second copy. Show the proposal in the stretch log before building beyond the pilot.
2. **Pilot on two slices:** supplier › Collect, with its beliefs band, and How it's built › Testing and controls. Generate their links. Show the page as the mock-up does, with the topic interconnections under the selected concept, each tappable to jump across spines. Measure what the map finds. Compare it with the hand-matched mock-up, and say where the hand matching was wrong.
3. **Coverage checks,** run in the Monday end-to-end step and mutation-proven:
   - every published page and research note attaches to at least one concept;
   - every module attaches to a concept, or is declared machinery;
   - every concept on a world or supplier spine has each layer it needs, or a recorded reason why not.

   Report counts, not just pass or fail. Start the checks as reporting only. Make them binding once the backlog they expose is planned.
4. **Research notes become pages where a domain lacks one.** Do not convert all 200. Every note attaches to a page as part of its evidence. Where a domain has notes and no page, write the page, starting with:
   - payments and direct debit (SLC 27.15, Bacs, failures, method migration);
   - switching mechanics (loss notice, objections, CSS, dual-fuel switching);
   - the supplier's accounts and capital (revenue recognition, unbilled accrual, MCR);
   - tariffs and the default tariff;
   - smart meters and half-hourly settlement;
   - vulnerability and the PSR.

   An orphan note is either a gap in the register or dead research. Rule on each one.
5. **A forward knowledge plan, generated from the map.** Rank the next knowledge from:
   - the priority order's next items;
   - the 239 unanchored constants the production run reads, in impact order;
   - the 17 Capabilities uses waiting on truth;
   - the open owed knowledge (owed item 7).

   Give each its cost estimate, under today's estimate-the-cost steer. Keep knowledge one step ahead of builds, and report a lagging measure of builds drawn before their knowledge. Add scheduled freshness sweeps of each page against new publications (Ofgem cap updates, DESNZ statistics, Energy UK switching data).
6. **Agents read the map before building.** Give each turn the generated register and its links as one cheap file, so it doesn't have to search the tree. Measure the token saving per turn.

## Report

One stretch-log entry with:
- the design proposal and what it absorbs;
- the two pilot slices, with their generated findings;
- the coverage counts;
- the knowledge pages owed, in order;
- the first forward knowledge plan with its cost;
- the token saving.

— Director steer, 24 Oct 2026, his words above; the mock-up and drafting are the advisor's.
