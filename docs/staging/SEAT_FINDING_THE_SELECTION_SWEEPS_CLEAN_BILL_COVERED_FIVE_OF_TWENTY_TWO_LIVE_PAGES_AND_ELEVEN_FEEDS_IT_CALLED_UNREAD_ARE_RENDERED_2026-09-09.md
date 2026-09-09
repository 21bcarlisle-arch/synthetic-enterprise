**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `every-surface-that-still-says-our-advantage-is-selection-must-answer-the-nine-seed-floor`) · **Class:** measurements_that_mirror

# FINDING — the selection sweep's clean bill covered five of twenty-two live pages, and eleven feeds it recorded as reaching no reader are rendered

Graded against
`docs/staging/SEAT_PREREGISTRATION_WHICH_OF_THE_SIXTEEN_UNCHECKED_LIVE_PAGES_ASSERT_SELECTION_2026-09-09.md`,
filed before any selection-word scan of the unchecked pages.

**P1 REFUTED. P2 REFUTED. P3 HELD IN PART. P4 HELD. P5 NOT REACHED.** No page edit is owed on
selection grounds. The census correction and one drift discovery are what this pass produced, and
the refutation is written up as plainly as a confirmation would have been.

## What this pass was checking, and why a landed sweep needed checking at all

`SEAT_FINDING_ONE_LIVE_SURFACE_IN_SIXTEEN_STATED_THE_SELECTION_CLAIM_AND_FORTY_FIVE_FEEDS_REACH_NO_READER_AT_ALL_2026-09-09.md`
(on origin at `0a4686f5a`) swept this same Lane 0 item, fixed the front door, and issued a clean
bill over sixteen surfaces. Its method section opens: *"The five pages a reader can open fetch 16
distinct ones."*

**The site serves twenty-two pages a reader can open.** That is not my count — it is this
repository's own control's count. `tools/site_reachability.crawl()` crawls outward from
`site/index.html` and returns 22 reachable pages, 0 orphans, from a population of 26:

```
population: 26   reachable-from-front-door: 22   orphans: 0
```

The seventeen the sweep did not open are `site/privacy/index.html` — which is in `sitemap.xml` in
its own right — and the sixteen `site/knowledge/<topic>/index.html` pages, each linked by
`href="./<topic>/"` from `site/knowledge/index.html`, which is itself in the sitemap and linked
from the front door.

The sweep's census was aimed at the **sitemap's door set** and read as though it were the **live
surface set**. `sitemap.xml` says in its own comment why topic pages are excluded from it: they
carry `noindex`, and the sitemap advertises doors, not sub-pages. `noindex` is an instruction to a
crawler. It is not a statement that no reader arrives — a reader arrives by clicking, from a page
that is in the sitemap.

**This is the failure the sweep was written to catch, landing on the sweep.** Its own table
carries the sentence *"a clean surface and an unchecked one look identical from outside"*, and
seventeen pages have been carrying the first appearance on the strength of the second treatment.

## My own count was wrong too, and it is corrected here rather than quietly

The pre-registration says *"twenty-one pages, not five"* and *"the sixteen unchecked pages"*. The
true figures are **22 and 17** — I dropped `site/privacy/index.html` from the total while
separately naming it as a subject in P4. The prereg's title still says SIXTEEN and is left alone;
a pre-registration edited after its measurement is not a pre-registration. The numbers in this
finding are the derived ones, and `tools/site_reachability.crawl()` is why they can be checked
rather than believed.

## The corrected feed census, derived and not hand-listed

Deriving the fetch set from all 22 reachable pages rather than listing it:

| | landed finding | derived here |
|---|---|---|
| top-level files in `site/data/` | 61 | 61 |
| **rendered** by a reachable page | 16 | **27** |
| **unrendered** | 45 | **34** |

The sixteen the sweep named are all genuinely rendered — it produced no false positives. It missed
eleven:

`knowledge_topics` (fetched by **5** pages), `knowledge_carbon_price`, `knowledge_gas_wholesale`,
`knowledge_gb_electricity_market`, `knowledge_hedging_forward_market`,
`knowledge_imbalance_cashout_settlement`, `knowledge_merit_order_residual_demand`,
`knowledge_metering_and_reads`, `knowledge_non_commodity_costs`, `knowledge_price_cap`,
`weather_cells`.

**Why this is not bookkeeping.** The landed finding's central method claim is that unrendered
feeds must not be graded as claims, because grading them manufactures a fictitious remediation
list. That argument is right. Its mirror is the error made here: eleven feeds were *excused* from
grading by a census that was wrong about whether anyone reads them. **The UNRENDERED verdict is
only ever as good as the render census beneath it**, and nothing in the sweep tested that census.
An UNRENDERED row is a claim about a reader, and it was never measured against one.

## Every surface this pass checked, and its verdict

Seventeen pages, plus the eleven feeds behind them. The prereg committed to **reading every page
for its directional claim regardless of whether it hit the word scan**, because a grep for a name
is blind to the mechanism written without it. Both columns are recorded so the next pass can tell
which verdict came from a hit and which from a read.

| # | Surface | Word hits | What it says about where the advantage comes from | Verdict |
|---|---|---|---|---|
| 1 | `privacy/index.html` | 0 | how a supplier would handle personal data; UK GDPR lawful bases | NO CLAIM |
| 2 | `knowledge/what-a-customer-is-worth/` (`knowledge_topics`) | 4, all rendered | value = contribution × survival, drivers lexicographic. The `per customer` hits are the OVO/SSE £143 and E.ON/OVO ~£150 **transaction prices**, external anchors with citations | NO CLAIM — and see below |
| 3 | `knowledge/acquisition-and-retention-economics/` | 4, all rendered | `bespoke` is inside a verbatim Ofgem quote about retention derogations; `per-customer` appears three times naming what is **redacted** from the CMA appendix | **ALREADY HONEST** |
| 4 | `knowledge/how-households-choose/` | 3, all rendered | choosing and paying are separated by years; the SVT majority is an absence of decisions | NO CLAIM |
| 5 | `knowledge/the-price-a-household-is-shown/` | 2, all rendered | cap and comparison sites quote an annual figure at an assumed consumption | NO CLAIM |
| 6 | `knowledge/how-many-synthetic-households/` | 1, rendered | *"Weight without choosing and you are back to a scale model"* — **sampling** selection | NO CLAIM — near miss, see below |
| 7 | `knowledge/non-commodity-costs/` (`knowledge_non_commodity_costs`) | 4, all rendered | levies settled `per customer` with their own rate tables; a residual naming the standing charge as the likely error source | **ALREADY HONEST** |
| 8–13 | `carbon-price`, `gas-wholesale`, `gb-electricity-market`, `hedging-forward-market`, `imbalance-cashout-settlement`, `merit-order-residual-demand` | 0 | published GB market mechanics: carbon cost, NBP, unbundling, hedging as certainty, cash-out, marginal pricing | NO CLAIM |
| 14–17 | `electricity-wholesale`, `metering-and-reads`, `price-cap`, `weather-cells` | 0 | wholesale formation, meter reads, the cap, weather cells | NO CLAIM |

**Not one of the seventeen asserts that Poesys's advantage comes from per-customer selection.**
They are domain pages about the published record, and they were written to explain a market rather
than to claim an edge.

## P1 and P2 refuted, and the near miss that shows the scan was worth running anyway

P1 predicted at least one of them would assert selection without the band. P2 named
`what-a-customer-is-worth` specifically so that a hit elsewhere would count as a miss. Both fail,
and the reasoning behind them was wrong in an instructive way: I expected pages written weeks
before the floor to have absorbed the house thesis. They had not, because they are **knowledge**
pages and the knowledge layer's own discipline held — every page carries a `live_evidence` rung
that says what is anchored and what is a practitioner's estimate.

`what-a-customer-is-worth` is the sharpest evidence that P2 was wrong for the right reason. Its
`residuals` rung ends:

> *"this page describes what drives value for a supplier that already has a customer. It says
> almost nothing about how you FIND the households worth having in the first place, which is the
> harder problem and the one this project exists to answer."*

That is the selection question named, scoped out, and **declared unanswered on the page itself**.
It is the opposite of the defect this sweep hunts.

**The near miss is #6 and it is a definition trap, not a defect.**
`how-many-synthetic-households` says a chosen-and-weighted sample beats a random one by a large
factor. That is *choosing which synthetic households to simulate* — a sampling-design claim about
representing a country. It is not *choosing which customers to serve*, which is the nine-seed
floor's subject. Two different quantities sharing a word. Recorded explicitly because the next
sweep will hit that string, and this project's most expensive recurring shape is a concept nobody
defined being differenced and published; a scan that graded #6 as a selection claim would have
sent a later pass to rewrite a page that is correct.

## P3 held in part — and what the part that failed turned up

P3 predicted `knowledge_topics.json` carries directional selection prose and is rendered by four
pages. **Rendered by five**, not four, and all 17 of its hits are in rendered fields — so the
render half holds and is stronger than predicted. The directional half fails: none of the 17 is a
claim about where our advantage comes from.

Checking the render half is what turned up the thing worth keeping. `knowledge_topics.json` holds
entries for **eleven** slugs. Only **five** pages fetch it:

```
ENTRIES THAT RENDER NOWHERE: carbon-price, gas-wholesale, gb-electricity-market,
                             hedging-forward-market, imbalance-cashout-settlement,
                             merit-order-residual-demand
```

Those six pages each fetch their own per-page feed instead. So six topics have **two homes**, and
the reader only ever meets one of them. The file's own `_note` records the decision to stop
growing one data file per page, and `what-a-customer-is-worth` carries a comment saying the older
pages *"keep their per-page files until someone migrates them — deliberately not migrated here,
because a page whose data moves is a page that has to be re-checked."* The intent was staged
migration. What exists is a half-finished one.

**All six have already drifted.** Comparing `rungs.headline.body` between the two homes, every one
of the six differs — not by whitespace but by being independently written:

| topic | unrendered `knowledge_topics` copy | rendered per-page copy |
|---|---|---|
| merit-order-residual-demand | *"an outcome competing generators produce for themselves rather than an order anyone issues"* | *"everything cheaper earns the difference"* |
| gb-electricity-market | separation is *"a matter of LICENCE rather than of ownership"* | supplier *"does not buy electricity once"* — contracting and imbalance |
| hedging-forward-market | *"why hedging looks like a mistake roughly half the time"* | *"it accepts being worse off in falling markets"* |

These are not contradictory today — they are two different explanations of the same topic, drifting
apart with no mechanism holding them together. **This is the named VAT shape**: one fact, more than
one home, edited on different days for different reasons. The landed sweep invoked that exact rule
to keep the ±£1,811 band off the front door. It is live in the knowledge layer, six times over, and
the dangerous half is that the copy nobody reads is the one that can rot without anyone noticing.

Recorded here rather than fixed: choosing which of two homes wins for six topics is a knowledge-layer
editorial call with a re-check obligation attached, and it is not this Lane 0 item's subject.

## P4 held, P5 not reached

`/privacy/` is NO CLAIM, as predicted. Recorded because a clean result predicted in advance is
worth more than a surface quietly dropped from a table.

P5 predicted the remedy would be a rewrite rather than a deletion. **Not reached — no remedy is
owed.** No live surface among the seventeen asserts selection, so there is nothing to rewrite and
nothing to withdraw. Stating this rather than leaving P5 unmentioned: an unreached prediction is
not a met one.

## What this does and does not change about the drawn item's DONE condition

DONE was: *no live surface asserts selection as the source of the advantage without the nine-seed
band beside it, and the finding names each surface it checked.*

That condition now holds over the **derived** live-page set rather than a hand-listed subset of
it. Twenty-two pages, twenty-seven feeds; five pages and sixteen feeds checked at `0a4686f5a` with
one defect fixed, seventeen pages and eleven feeds checked here with none found. The two findings
together name every one.

**What no longer holds is the landed finding's `45 feeds reach no reader` headline**, which is on
origin and wrong by eleven. It is not edited — a finding corrected in place loses the evidence that
it was checked — and this finding is the correction beside it.

## What is next

1. **A future sweep must derive its page set, never list it.** `tools/site_reachability.crawl()`
   already returns it and is already run by the pre-commit gate on any `site/**/*.html` change. The
   sweep that missed seventeen pages was written in a tree that contained the tool that would have
   found them. No new control is proposed here: the mechanism exists, is wired, and was simply not
   consulted, and a control watching whether a sweep consulted a control is the shape CLAUDE.md
   warns costs more than it catches.
2. **Six knowledge topics have two homes and have drifted.** Either the migration into
   `knowledge_topics.json` finishes and the six per-page feeds are deleted, or the six unrendered
   entries are deleted and the consolidation is recorded as abandoned. Both are cheap. Leaving it
   is the only expensive option, and the re-check obligation the comment names is the reason it has
   been left twice.
3. **The 34 unrendered feeds remain the standing hazard the landed finding named** — with the
   correction that there are 34 and not 45, and that `knowledge_topics.json` proved a feed can move
   from one side of that line to the other without anything noticing.
