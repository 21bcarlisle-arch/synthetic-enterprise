**Severity:** BLOCKING · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Knowledge that checks the world, not knowledge that is read once (2026-10-19)

**Type:** STEER, through the advisor channel. The director's words, from chat on Mon 19 Oct:

- 06:15 BST: "In terms of root cause, do we need to make sure knowledge is created, referenced and crosschecked better? Or not?"
- 06:15 BST, on the advisor's answer below: "Yes, well done."

**When:** next, beside the week's feature work, and ahead of any change to the draw or the book size. It is a named dependency of every product item that reads the world (P6). The design is yours. What follows is the class to close and the shape the director agreed. It is not a specification.

---

## The class

The single-fuel book (`WORKER_FINDING_THE_OPENING_BOOK_WAS_ONE_PERCENT_DUAL_FUEL_AND_NOW_BEARS_THE_PUBLISHED_SPLIT_2026-10-17`) was not a gap in knowledge. The knowledge existed and nothing tested the world against it.

- `docs/market_research/rd_synthesis_june_2026.md` said "~75% … dual fuel" and "correct by design". No code or check pointed at it, so the founder draw changed underneath it twice.
- The 13 July "documented placeholder" named no source to anchor it from, so it read as owned debt and was never retired.
- The director's 26 Aug ruling reached one of three paths. Nothing listed the others.
- The same class is already visible on a published page. The annual report carries two "Low Carbon %" tables, from `company/billing/fuel_mix.py` and `company/regulatory/carbon_emissions.py`, which differ by up to 3.4 points. The report says "neither table carries a publication vintage".

Your 17 Oct mechanism, a book-composition test for the fuel split, closes one fact. This steer asks you to close the class, with the smallest mechanism that can fail (P13; canon "How this canon works", item 4).

## The shape he agreed

1. **Anchor or range.** Every constant the world draws from must either cite its knowledge page or source, or be marked as a labelled evidence range (W7 principle 1, W8). A check refuses a bare number, and refuses "placeholder" with no anchor named. Name the existing unanchored ones and register them; don't fix them all at once. `DEFAULT_BAND_WEIGHTS` is the first entry.
2. **Knowledge pages carry checks.** A page's headline figures are stated as testable claims about the world or the book, with their range and source. Examples from the fuel page: the dual-fuel share of homes, the off-grid share, and gas-only accounts arising only from split homes. The Monday end-to-end step compares the world with each claim and goes red on a gap (W8: "a reality check on the world rather than an input"). Start with the pages that describe the population and its behaviour, not all 180.
3. **A change to who is in the world re-runs them.** A change to founder count, prospect cap, a draw path or a new arrival route triggers the population checks automatically. That is what was missing when the book went 13 → 80 → 400.
4. **One home per fact.** Where two tables hold the same fact, retire one or reconcile them, starting with the two fuel-mix tables. A ruling or fact that lands carries its "where this lands" list into the code paths as well as the pages (canon "How this canon works", item 2).

**Not wanted:** a new review layer, a new document type, or a process that relies on someone remembering to read a page. A number that is checked is the mechanism.

## Report

One stretch-log entry with:
- the mechanism, mutation-proven (R15);
- the register of unanchored constants, with counts;
- which knowledge pages now carry checks, and which checks went red on first run, with what you did about each;
- the fuel-mix tables reconciled.

Raise anything that would change a ruling as a proposal.

— Director steer, 19 Oct 2026, from his chat words above. The drafting is the advisor's.

## Done

*Delivery seat, 2026-10-19.* Items 1 to 3 landed earlier today: `tools/world_constant_anchors.py`
(anchor or range, 446 bare constants registered, `DEFAULT_BAND_WEIGHTS` first) and
`tools/world_claims.py` (the population pages carry `world-claims` blocks, which are re-run when
who is in the world changes).

**Item 4, one home per fact: the two fuel-mix tables.** Both DESNZ sources were fetched. They are
**two facts**: DESNZ's own disclosure table says its supply-basis mix "differs from the UK
generation mix published in UK Energy Trends and [DUKES]". Neither old table was what it claimed.
The "FMD" table was a generation mix, and the Observatory table was undated whole numbers with an
imports bucket. Each now has one source:
- `UK_GRID_FUEL_MIX`: DUKES 5.6.C generation shares, published 30 July 2026.
- `_FUEL_MIX_BY_YEAR`: the FMD UK mix, 2019/20 to 2025/26. 2016/17 to 2018/19 are a stated GAP.

The report's note now names each basis instead of "at most one is right".
`tests/company/regulatory/test_the_two_fuel_mixes_are_their_published_sources.py` holds both tables
to the page's fetched block (three mutations, each red). Knowledge page:
`docs/market_research/two_uk_electricity_fuel_mixes_generation_and_disclosure.md`.

These published figures move:
- Observatory `Low Carbon %`: up to 3.7 points (2025: 68 → 64.3).
- FMD section: up to 7.2 points (2024: 65.5 → 58.3).
- "Renewable majority" no longer fires: 48.0% at peak on the supply basis.

**Also:** `world_claims` now measures the trickle and campaign routes too. On first run the campaign
went red: 100% of won gas homes are dual against a published 81–96%. It is registered in
`KNOWN_ROUTE_GAPS` and filed as
`docs/staging/SEAT_FINDING_THE_FUEL_CLAIMS_ARE_MEASURED_ON_THE_FOUNDERS_ONLY_AND_THE_CAMPAIGN_ROUTE_WINS_EVERY_GAS_HOME_DUAL_2026-10-19.md`.
The world fix is handed on.
