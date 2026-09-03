**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `SITE2_two_sided_wall_exhibit`

# The consolidated Knowledge record holds a second, older copy of six pages, and the migration it invites would silently revert them

**Found:** 2026-08-30, incidental to writing the two choice-and-channel Knowledge pages
(`docs/staging/DIRECTOR_BRIEF_CHOICE_AND_CHANNEL_2026-08-30.md`, WORK item 1). It is not that
item's subject and it weakens the next person to touch any of six pages, so it is filed rather
than folded in.

**Not a claim that any published figure is wrong.** Every reader today gets the newer text. What
is wrong is a trap laid for the next edit.

## The mechanism

`site/data/knowledge_topics.json` was introduced as the consolidated home for Knowledge page
bodies. Its own `_note` says so, and records that the older pages *"keep their per-page files
until someone migrates them"*. `acquisition-and-retention-economics` was the first page to read
it, on 2026-08-28, and its inline comment repeats the invitation:

```
// The older pages keep their per-page files until someone migrates them --
// deliberately not migrated here, because a page whose data moves is a page that has to be
// re-checked, and that is its own piece of work.
```

That is all true and all sensible. What neither note says, and what nothing in the repository
checks, is that **the consolidated file already contains bodies for six of those pages** — and
they are not the bodies the pages render.

| slug | per-page file the html actually fetches | rungs differing |
|---|---|---|
| `gb-electricity-market` | `knowledge_gb_electricity_market.json` | 7 of 7 |
| `merit-order-residual-demand` | `knowledge_merit_order_residual_demand.json` | 7 of 7 |
| `gas-wholesale` | `knowledge_gas_wholesale.json` | 7 of 7 |
| `carbon-price` | `knowledge_carbon_price.json` | 7 of 7 |
| `imbalance-cashout-settlement` | `knowledge_imbalance_cashout_settlement.json` | 7 of 7 |
| `hedging-forward-market` | `knowledge_hedging_forward_market.json` | 7 of 7 |

Measured, not inferred: every rung body differs on every one of the six, and three of the six
differ in their title as well.

## Which copy is stale, and by how much

The consolidated copies are the **older** draft. Sampled on `carbon-price`:

```
consolidated  claim_freshness.last_verified = 2026-08-19   title "The UK carbon price"
per-page      claim_freshness.last_verified = 2026-08-24   title "The carbon price"
```

So the live pages carry work done on 24 August that the consolidated file never received. A
migration performed as the plumbing change both notes describe — repoint the `fetch`, delete the
per-page json — **reverts six pages to an eleven-day-old draft, with no diff a reviewer would
see**, because the change under review is a URL and the content change is in a file nobody
touched.

## Why nothing caught it

Two blindnesses meeting, and the second is the interesting one.

1. **No test named the consolidated file's consumer at all.** On 2026-08-30,
   `grep -rln acquisition-and-retention-economics --include=*.py site/ tests/ tools/` returned
   nothing. The first and only page reading the record had no control over it.

2. **The natural control would have been keyed to the wrong set.** The first draft of
   `site/knowledge/test_the_consolidated_pages_render_their_own_record.py` parametrised over
   *every key in `pages`* — and reported twelve failures, all six shadow entries, as if the pages
   were broken. They are not broken; they are unread. A control that treats an unread key as a
   broken page is the same defect one level up: it fires on the wrong subject and would be
   silenced by whoever met it.

The shipped control instead **scans the pages' own markup** for which ones fetch the record, and
carries `SHADOW_ENTRIES` as a declared, asserted-exact set. That turns the gap from an absence
nobody counts into a number the suite prints, and — the point — it makes withdrawing an entry
from that set the moment a migrator is looking at the sentence that tells them the consolidated
copy is older.

## What is owed

**Reconcile before migrating, per page, and never as one commit.** For each of the six: diff the
consolidated body against the per-page body, keep the newer text with its own
`claim_freshness`, re-check the claims (a page whose data moves has to be re-checked — the
existing note is right about that), then repoint the fetch and remove the shadow entry.

**Or delete the six shadow entries outright** and let each page migrate by being written into the
record fresh. That is cheaper and loses nothing, because the shadow bodies are strictly older
than what is live. It is the recommendation; it is not done here because deleting six page bodies
from a published data file on the way past is precisely the kind of tidy-up that should be its own
commit with its own diff.

Either way the control above already refuses the silent version.

## The falsifier

`site/knowledge/test_the_consolidated_pages_render_their_own_record.py::test_the_shadow_entries_are_exactly_the_unrendered_keys`
reds if a shadow entry is withdrawn without the page being migrated, or if a new page is added to
the record that nothing renders.
