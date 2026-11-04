**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] One light taxonomy: five facets on every page and every claim, built on your existing structure (2026-11-04)

**Type:** STEER, through the advisor channel. The director's words, from chat on Wed 4 Nov:

- 08:48 GMT: "Do we need a taxonomy for all this?"
- 08:49 GMT, on the advisor's proposal of five facets that extend the seat's own structure note: "Yes."

## The design

**Extend `docs/design/THE_KNOWLEDGE_BASE_STRUCTURE.md`. Do not replace it.** The six domains and the placement of the 62 pages are kept. Use facets, not a deeper folder tree: one page can sit in several places at once, and a facet can change, for example when an insight moves from hypothesis to held, without anything moving.

| Facet | Question it answers | Values |
| --- | --- | --- |
| **Domain** | What is it about? | Your six domains |
| **Layer** | Knowledge or insight? | `knowledge` / `insight`, per today's steer `DIRECTOR_STEER_KNOWLEDGE_AND_INSIGHT_ARE_DIFFERENT_LAYERS_…` |
| **Side** | Who can know it? | `world` (hidden truth) / `supplier` (observable or must be asked) / `both` |
| **Trust** | How sure are we? | For knowledge: the D/P/S/A grade, verified or not, and the vintage date. For insight: hypothesis, tested, held, contested or refuted, what would falsify it, and the review date |
| **Use** | What depends on it? | The world parameters, supplier decisions and site pages that read it. Link this to the existing map of ideas to code and pages, so that a wrong fact shows at once what it touches |

## Ask

1. **Give every page and every claim a small machine-readable header** carrying the five facets. Every Knowledge and Insight page needs one. So does every figure-bearing claim within a page, where a page mixes trust levels.
2. **Add a check that refuses a page with a missing or invalid facet,** and that enforces the no-circularity rule automatically. A `use` link from an `insight` that is sim-derived to a world parameter or calibration target is refused.
3. **Let the site filter by any facet.** For example: "unverified insight about customer behaviour", or "everything a world parameter rests on that is graded below P".
4. **Back-fill all 62 or more pages, and report the counts by facet.** This doubles as the audit the knowledge-and-insight steer asks for.
5. **Keep it light.** Five facets, short value lists, no sub-taxonomies. Add a facet only when a real question cannot be answered without it, and record the addition as a dated design decision.

**Sequencing.** This is drafting and tooling work alongside the correctness stretch, in the same lane as the corpus. Merge it with the knowledge-and-insight steer as one piece of work.

## Done

Done 2026-11-04 with the knowledge-and-insight steer. The five facets are in `docs/design/THE_KNOWLEDGE_BASE_STRUCTURE.md` §7, which extends the existing structure rather than replacing it.
- **Asks 1 and 4.** Every one of the 63 pages has a record in `site/data/knowledge_facets.json`. The counts by facet are in the audit record.
- **Ask 2.** The check refuses a missing or invalid facet, and refuses a circular use.
- **Ask 3.** `site/knowledge/what-we-think.html` filters by every facet, and a view can be linked.
- **Inside each mixed page.** Every section is marked knowledge or insight from the record.
- **Ask 5.** No facet was added.
