**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — follow-on from `every-surface-that-still-says-our-advantage-is-selection-must-answer-the-nine-seed-floor`) · **Class:** `controls_that_cannot_fail`

# The six unread Knowledge entries are deleted, and the exception list that declared them went with them

**2026-09-09, scheduled tick.** The Lane 0 selection sweep is spent — its DONE condition was met
at `0a4686f5a` and corrected at `b9ff0425b`, and both findings are on origin. This is item 2 of
that correction's *"what is next"*, done rather than re-recorded.

---

## 1. The drawn item was spent, and saying so is the first result

The doorbell drew the selection sweep again. It has already run twice: `0a4686f5a` swept five
pages and sixteen feeds and fixed one defect; `b9ff0425b` re-derived the page set with
`tools/site_reachability.crawl()`, found the first pass had covered five of twenty-two live pages,
checked the missing seventeen, and **refuted its own P1 and P2** — not one of them asserts that our
advantage comes from per-customer selection. No page edit is owed. The claim is not re-swept here.

What that correction left open, in its own words, was: *"Six knowledge topics have two homes and
have drifted. Either the migration into `knowledge_topics.json` finishes and the six per-page feeds
are deleted, or the six unrendered entries are deleted and the consolidation is recorded as
abandoned. Both are cheap. Leaving it is the only expensive option."*

## 2. It was not a new finding, and that is the more interesting fact

`site/knowledge/test_the_consolidated_pages_render_their_own_record.py` has named all six by name
since **2026-08-30**, in a `SHADOW_ENTRIES` set with a docstring explaining exactly what they were
and a filed finding (`WORKER_FINDING_THE_CONSOLIDATED_KNOWLEDGE_RECORD_HOLDS_A_SECOND_STALER_COPY_
OF_SIX_PAGES_2026-08-30.md`). The sweep on 2026-09-09 rediscovered it as though new.

That is not wasted work — the sweep reached the same conclusion independently, which is worth
something — but it is the tell that a **declared** exception is not a **disarmed** one. Ten days,
two lanes, one control printing the number the whole time, and the hazard sat exactly where it was.

## 3. What was measured today, in this tree

`site/data/knowledge_topics.json` held 11 keys. Five pages fetch it, scanned from their own markup:
`acquisition-and-retention-economics`, `how-households-choose`, `how-many-synthetic-households`,
`the-price-a-household-is-shown`, `what-a-customer-is-worth`. The other six —
`gb-electricity-market`, `merit-order-residual-demand`, `gas-wholesale`, `carbon-price`,
`imbalance-cashout-settlement`, `hedging-forward-market` — each have a `knowledge_<topic>.json`
their page fetches instead, and **rendered to nobody**.

| measured | result |
|---|---|
| rungs differing between the shadow entry and the body the reader is served | **7 of 7, on all six** |
| pages where even the `meta.title` differs | 2 (`gb-electricity-market`, `gas-wholesale`) |
| fields present in the shadow copy and absent from the live per-page copy | **0, on all six** |
| research documents that would become orphans under `knowledge_layer_gate.orphan_research()` | **0** (107 orphans either way) |
| rendered value that changes for any reader | **none, by construction** |

The last two are why this was safe to do rather than escalate. The orphan measure was checked
because it globs the record's *text*, so a research doc cited only inside a shadow entry would have
counted as published while reaching no reader — a live instance of the shape the sweep's correction
named. There were none. Had there been, the finding would have been the orphan measure, not this.

## 4. What was done, and why deletion beat the alternative

The six entries are **deleted**. The consolidation is recorded as abandoned for those six, in the
record's own `_note`, where the invitation to consolidate lives — not in a test docstring a
migrator has no reason to open.

The `_note` was the actual mechanism of harm. It invited the migration; the body a migrator would
reach for was the older draft, sitting under the right key, in the right file. The warning that
taking it would silently revert six pages lived somewhere else entirely. **The invitation and the
warning had two homes** — which is the same defect one level up from the one being fixed.

Deletion over declaration, per CLAUDE.md's *"prefer doing the work to building the thing that
watches the work"*: an unread second copy of a fact has exactly one live role, which is to be the
draft somebody finishes the migration from. Nothing is lost — the live per-page copy is a strict
superset by field, and git holds the bodies.

## 5. The control got stronger, not weaker

`test_the_shadow_entries_are_exactly_the_unrendered_keys` (key set minus consumers == a six-name
list) is replaced by `test_the_record_holds_exactly_the_pages_that_render_it` (key set **equals**
consumer set). Before, six named keys could render nowhere and a seventh was caught. Now none can.
The consumer set is still scanned from the pages' markup and never listed.

**Poison round first, in a clean extract, because "survived" means two opposite things:**

| poison | result |
|---|---|
| add an unrendered key (`carbon-price` back in) | RED — names the key |
| drop a consumer's key (`what-a-customer-is-worth`) | RED — names the page |
| empty `pages` entirely | RED on all five consumers |

Both directions of the equality are proven separately, because a subset test in either direction
passes the mutation aimed at the other. Full suite: 113 passed across `site/knowledge/` and
`site/test_the_sampling_page_reaches_the_reader.py`.

## 6. A claim I made and then refuted, kept beside the right one

Raising the population floor from 3 to 5, I wrote in the docstring that the floor was now *"the
only thing standing between an emptied record and a key-set equality that both sides satisfy with
nothing."* Poison 3 refutes it: emptying `pages` reds the equality on all five consumers and the
floor still passes, because the consumer set is scanned from html and does not empty when the
record does. The equality has no vacuous case for the floor to cover. The floor is raised anyway —
five is the measured truth and three was slack — and its real job is the parametrized tests, which
genuinely do pass by having no subjects. The wrong reason is recorded next to the right one.

## What is next

1. **Nothing is owed on the selection claim.** Two sweeps, twenty-two pages, twenty-seven feeds,
   no live surface asserting selection without the band. The Lane 0 item is released.
2. **The other four separate feeds are not the same shape and were not touched.**
   `knowledge_price_cap.json`, `knowledge_wholesale.json`, `knowledge_metering_and_reads.json`,
   `knowledge_non_commodity_costs.json` and `weather_cells.json` each have exactly one home; only
   the six had two. Named here so a later pass can tell a checked file from an unchecked one.
3. **107 of 111 research documents are named by no Knowledge surface.** Unchanged by this work,
   measured in passing, and a standing backlog that belongs to the knowledge layer rather than to
   this lane. It is the largest number this turn touched and the one nobody is grading.
