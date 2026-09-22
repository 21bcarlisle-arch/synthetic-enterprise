**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `every-surface-that-still-says-our-advantage-is-selection-must-answer-the-nine-seed-floor`) · **Class:** measurements_that_mirror

# PRE-REGISTRATION — which of the sixteen unchecked live pages assert selection, and what the corrected rendered/unrendered split is

Filed **before** any selection-word scan of `site/knowledge/*/index.html`,
`site/privacy/index.html`, or the eleven feeds they fetch. Written after establishing the page
census and the feed census only — both of which are facts about routes, not about claims.

## Why this exists when the sweep already landed

`docs/staging/SEAT_FINDING_ONE_LIVE_SURFACE_IN_SIXTEEN_STATED_THE_SELECTION_CLAIM_AND_FORTY_FIVE_FEEDS_REACH_NO_READER_AT_ALL_2026-09-09.md`
(landed on origin at `0a4686f5a`) swept the same Lane 0 item and issued a clean bill. Its own
method section opens: *"The five pages a reader can open fetch 16 distinct ones."*

**The site serves twenty-one pages, not five.** `site/knowledge/index.html` links sixteen topic
directories with `href="./<topic>/"`; every one resolves to a served `index.html`, and
`/knowledge/` is itself in `site/sitemap.xml` and linked from the front door. `/privacy/` is in
the sitemap in its own right, named there as *"a footer route on every page"*.

The sweep's census was aimed at the **sitemap's door set** and read as if it were the **live
surface set**. The sitemap says in its own comment why topic pages are excluded from it — they
carry `noindex` and the sitemap advertises doors — and `noindex` is an instruction to a crawler,
not a statement that no reader arrives. A reader arrives by clicking, from a page in the sitemap.

That is the failure this repository names most often and it has landed on the sweep that was
written to catch it: **a clean surface and an unchecked one look identical from outside**, and
sixteen pages are currently carrying the first appearance while having had the second treatment.

## The arithmetic, which is not a prediction

Stated here so it cannot be reported as a discovery afterwards. The sixteen unchecked pages fetch
eleven feeds the sweep did not count as rendered:

`knowledge_topics`, `knowledge_carbon_price`, `knowledge_gas_wholesale`,
`knowledge_gb_electricity_market`, `knowledge_hedging_forward_market`,
`knowledge_imbalance_cashout_settlement`, `knowledge_merit_order_residual_demand`,
`knowledge_metering_and_reads`, `knowledge_non_commodity_costs`, `knowledge_price_cap`,
`weather_cells`.

So the corrected split over the 61 top-level files in `site/data/` is **27 rendered / 34
unrendered**, against the landed finding's **16 / 45**. Eleven feeds are currently recorded as
reaching no reader while a reader can open a page that fetches them.

This matters beyond bookkeeping: the landed finding's central method claim is that unrendered
feeds must **not** be graded as claims, because grading them produces a fictitious remediation
list. The mirror error is the one made here — eleven feeds were excused from grading by a census
that was wrong about whether anyone reads them. **The UNRENDERED verdict is only as good as the
render census under it**, and nothing in the sweep tested that census.

## Predictions

**P1 — at least one of the sixteen pages asserts, in hand-authored prose, that the advantage
comes from per-customer selection, without the nine-seed verdict beside it.** I expect this to
hold. These pages were written to explain the domain, they predate the floor by weeks, and the
front door needed exactly this fix.

**P2 — `what-a-customer-is-worth` is the page that does it.** Named specifically so a hit
somewhere else counts as a miss. CLV is the concept where "knowing each household well pays" is
the natural sentence, and it is the topic closest to the selection leg. Runner-up, named second
so the order is on the record before the scan: `acquisition-and-retention-economics`, then
`how-households-choose`.

**P3 — `knowledge_topics.json` carries directional selection prose and is rendered by four
pages.** If a claim lives there, one edit reaches four surfaces, and the "one fact, one home"
rule the landed finding invoked for the front door applies here in reverse: the fix belongs in
the feed, not in four copies of the prose.

**P4 — `/privacy/` is NO CLAIM.** Predicted clean. Recorded so that a clean result is a
prediction met rather than a surface quietly dropped from the table.

**P5 — the remedy that ends up being needed is a rewrite, not a deletion.** The drawn item is
explicit that where a surface has no floor behind it, the page must say so rather than lose the
claim quietly.

## What would refute the whole frame

If every one of the sixteen pages is genuinely NO CLAIM, then P1 fails and the landed sweep's
verdict was right by luck rather than by method — the census was still wrong, and the
27/34 correction still stands, but the clean bill it issued turns out to have covered the truth.
**That outcome gets written up exactly as plainly as the other one.** A census error that
happened not to hide a defect is a smaller finding, not a non-finding, because the next pass
inherits the census and not the luck.

## The stated risk in this prereg's own method

A selection-word scan finds the word, not the claim. A page can assert the direction without any
of the words (`selection`, `personalis`, `per-customer`, `tailor`, `individual`, `each
household`, `bespoke`) — the mechanism written without the name is a shape this project has
filed before. So the scan is the census and **every one of the sixteen pages gets read for its
directional claim regardless of whether it hits**, and the table records which verdict came from
a hit and which from a read.
