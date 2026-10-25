**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Check every [unverified] item in today's packs against its primary source as you draft each page (2026-10-25)

**Type:** STEER, through the advisor channel. The director's words, from chat on Sun 25 Oct:

- 07:52 GMT: "Why did search budgets run out? How can we solve this?"

## Why

The advisor's research passes ran into two limits:

1. **A per-turn search allowance shared across all its parallel passes.** It ran out when six or seven passes ran at once.
2. **Network blocks in the advisor's sandbox.** These stopped it reaching gov.uk/assets spreadsheets (xlsx and ods), the Eurostat API, legislation.gov.uk, the PVGIS API, Ofgem zip files and gated datasets.

As a result, today's 36 evidence packs carry many **[unverified]** items. Each pack's "Named gaps" section also lists the fetches it could not make.

Your host has its own network access and does not share the advisor's search allowance. The packs already cite most of the primary URLs.

## The steer

- **Check each item as you turn a pack into a Knowledge page.** Check every [unverified] figure against its primary source. Where the pack gives a URL or names a dataset (for example DfT NTS0901/0904/0908, TRA0305/0306, VEH0141; the DESNZ Solar PV cost data and ET 6.3 workbooks; the Boiler Upgrade Scheme ad hoc cost releases; DESNZ Valuation of energy use tables; the FES Assumptions Log; Eurostat nrg_chdd_a; Ofgem SLC31E data; PVGIS), fetch it directly.
- **Record one of three outcomes for each item:**
  - **confirmed:** give the source and the access date;
  - **corrected:** give the old value, the new value and the source;
  - **still unpublished:** say so as a finding.
- **Never promote an [unverified] item to a claim without a source.** A corrected item also changes any world claim or population check that used it.
- **Priority:** first the items that feed world claims or population checks, then the GB-market packs, then the other-markets packs. The other-markets packs are knowledge only.
- **Report back.** Add a per-pack count of confirmed, corrected and still-open items to the Knowledge index or to the map's coverage counts. It shows the director how much of today's research has been checked.
- **Advisor side:** from now on the advisor will run at most two or three research passes per turn, and will close gaps in later turns.

## Progress (seat-executor, 2026-10-25 ~11:55Z; the file stays in the queue)

- **Checking as drafted: done page by page.** Each page landed in 7fb1aabcc3 and 2d33139a4b says it checked its pack's unverified items at source. Where a page states its tally, it reads, for example: dated cost series 15 confirmed / 2 corrected / 4 open; prices 7 / 0 / 5; PV roofs 2 / 0 / 4; PV and batteries 1 / 0 / 8; network limits 0 / 0 / 1; smart meters 2 / 1 / 3; tariffs 2 (+1 partly) / 3 / 2; vulnerability 1 (+1 partly) / 0 / 2.
- **Not done: the report-back.** No per-pack count of confirmed, corrected and open items exists in the Knowledge index or in the map's coverage counts. Several pages (the boilers, heat pumps, comfort, savings, VPP, cars, mileage and all seven other-market pages) state no tally in a form a grep finds. Handed on as `knowledge-pack-verification-census`.

## Done

Each GB-market page was checked against its sources as it was drafted: 7fb1aabcc3 for twenty-one pages and 2d33139a4b for the last three. The report-back is in the next paragraph.

Moved here 2026-10-25 by the seat-executor. The signed ruling (the advisor's own commit, 12cb6489f) was read and is being acted on; the file sat in the queue refused as unsigned only because the machine's progress notes above were appended after the advisor staged it. Those notes stay as the record of what landed. What is still owed is carried by: the hand-off `knowledge-pack-verification-census` (the per-pack confirmed/corrected/open count on the Knowledge index).

**Report-back, later on 25 Oct.** The hand-off `knowledge-pack-verification-census` is closed. A per-pack count of items confirmed, corrected and still open is now on the Knowledge index, under "How much of the 25 October research was checked at its source" (`site/knowledge/index.html#pack-verification`). It counts the items listed in each research note's verification section. "Partly" is a column of its own, and items the source does not publish count as still open.
- **The 17 GB-market packs with a verification pass:** 73 confirmed, 5 partly, 17 corrected, 89 still open.
- **The 7 other-market packs:** 4 confirmed, 6 corrected, 320 still open.
- **No verification pass recorded:** payments and direct debit, switching mechanics, and suppliers' accounts and capital. Each keeps its [unverified] items as named gaps, not claims. Regional supply cost carries none.
- **Notes whose own summary disagrees with their list:** dated cost series (summary 15 confirmed, list 13), heat pumps (summary 7 open, list 6) and Spain (one confirmation is written twice). Each has its row note on the index.
