**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Would linking findings to concepts have caught our repeat defects? Measure it (2026-11-14)

**Type:** STEER, through the advisor channel. The director's words, from chat:

- Fri 13 Nov, 18:50 GMT, sharing https://allegrograph.com/netflixs-ontology-driven-ai-architecture-validates-the-need-for-context-graph/ with no comment.
- Sat 14 Nov, 05:51 GMT, on the advisor's recommendation below: "Stage it"

## What the advisor found (check it)

- **The source** is a vendor blog (Franz, AllegroGraph, 28 Oct) retelling a Netflix Technology Blog post of 16 Oct. Netflix's incident agents (AutoRCA) share one ontology and knowledge graph (RDF, OWL, SHACL, SPARQL). Each investigation and human insight is written back into the graph. Netflix: "the ontology gradually stops being a schema and starts being a memory." "Context graph" is Franz's label, not Netflix's. It gives no before/after figures; the one number is an example investigation of about four hours, mostly spent reconstructing relationships. The advisor has not read the Netflix original.
- **The ontology half we have.** `docs/design/the_map/concepts.yaml` holds 76 concepts with SKOS names, definitions, `match`, one home per layer, relations, and the two-names and second-home checks. Research notes attach through `**Knowledge:**` lines or `note_rulings.yaml`.
- **The memory half we mostly don't.** Of 4,720 staging items (`docs/staging/*.md` and `docs/staging/done/*.md`), 199 carry a `**Knowledge:**` line, about 4%. Findings, steers and rulings sit as files, not as memory attached to the concept they are about.
- **Why it might matter.** CLAUDE.md names the interconnection question ("what else assumes it?") as the seat's alone, and its evidence is a repeat defect: the VAT rule, one requirement, five implementations, fixed in one in July and still live in another in August. Half-month direct debits and bill shock are the same shape.

## The question

**On the day a later defect in a family was filed, would a concept-linked list of findings have shown the earlier related one?** If yes, links are cheap memory. If no, this is ceremony and we drop it.

## The outcome wanted

1. **Tag, don't hand-file.** Using the names the register already holds (`prefLabel`, `altLabel`, the same matching the module search uses), tag past staging items to concepts automatically. Report coverage and a hand-checked precision sample of 30. Write nothing to the staging files.
2. **Replay three known families:** the VAT rule; the half-month first direct debit; bill shock (one name for two experiences). For each, find the earlier and later findings. At the later filing date, ask whether the earlier one would have been listed under the same concept. Pre-register the prediction before running it.
3. **Decide by the rule set now.** If two of three would have been caught, propose that new findings carry a concept link (generated, not hand-typed where the tagger is confident), plus one line in the seat's orientation: "findings already on this concept". If fewer, say so and drop it. No graph database, no new store, no new gate either way.
4. **Read the Netflix original** (Netflix Technology Blog, 16 Oct 2026) if reachable. Record what it says it measured, beside the vendor's claim.

## Reading-log entry to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-13 | Franz / AllegroGraph, "Netflix's ontology-driven AI architecture validates the need for context graph" (28 Oct), retelling Netflix Technology Blog (16 Oct) | Director | The ontology becomes memory when findings and decisions hang off concepts; ours has the ontology, but only ~4% of staging items link to a concept. Measure on three repeat-defect families before building anything. | MEASURE; vendor source, no outcome figures |

## Rules

- **Measure before build.** Smallest thing that can fail: a tagger and three replays.
- **Key the result to the property.** Did the earlier finding surface on the day? Not tag counts.
- **Correct the record plainly** if the 4% count above is wrong. It was a filename-and-grep count.

## Risk

Touches: read-only over staging and the concept register; one report.
Blast radius: none.
Probable failure modes:
- **Hindsight tagging:** the tagger uses names coined after the defect was understood. Tag with the register as of each filing date where git history allows, and say where it doesn't.
- **A family picked because it will pass.** These three were named by the advisor from CLAUDE.md before any run.

Proportionality: doc-and-measurement only. Implement directly.

— Director steer, 14 Nov 2026, his words above; the reading and drafting are the advisor's.
