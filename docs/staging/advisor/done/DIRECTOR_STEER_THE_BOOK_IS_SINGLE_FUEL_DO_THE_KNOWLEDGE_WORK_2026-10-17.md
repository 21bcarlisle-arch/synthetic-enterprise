**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The opening book is 1% dual fuel: do the knowledge work, find why we missed it, and correct the world (2026-10-17)

**Type:** STEER, through the advisor channel. The director's words, from chat on Sat 17 Oct:

- 10:09 BST: "How many customers does the supplier start with? How many of the book are elec only, gas only, duel fuel. Is this representative and typical of the mix for a supplier?"
- 10:23 BST: "Almost all the switching market is dual fuel. The vast majority of customers keep their fuels together. Legacy suppliers may have some single fuel from failed switches. Some properties don't have gas. But this tiny focus on dual fuel, is so fantastically wrong I can't believe it. If have thought even basic knowledge work would have resolved this. And id switching is fuel by fuel rather than household, something is badly wrong"
- 10:24 BST: "Research and understand the problem and get it to do knowledge work and self correct"

**What he asks of you:** the knowledge work, the diagnosis and the correction are yours. This document gives the measurement that started it and where to look. It does not give the answer. Where your knowledge work disagrees with anything below, the knowledge wins, and you say so.

**When:** next, at rung zero, ahead of feature work. This is breakage in the world (P7), and every per-customer number rests on it. It is not a new feature.

---

## The measurement that started it (advisor, 17 Oct, on origin/main, default seed)

I ran `founder_book(seed)` with `SE_DRAW_POPULATION=1`:

| Opening book, 400 accounts in 395 homes | Homes | Share |
|---|---|---|
| Electricity only | 283 | 72% |
| Gas only | 107 | 27% |
| Dual fuel | 5 | 1% |

- **The cause.** All five dual-fuel homes are among the 13 hand-written accounts. Each of the 387 drawn founders is one single-fuel account. A coin picks its fuel: `population_draw.DEFAULT_COMMODITY_WEIGHTS = {"electricity": 0.72, "gas": 0.28}`. The module calls this a "documented placeholder… Not claimed as anchored" (13 July).
- **What the homes are.** Crossing the account's fuel against the home's own drawn heating fuel (`premise.commodity`):
  - 250 are electricity-only accounts on gas-heated homes;
  - 107 are gas-only accounts on gas-heated homes;
  - 25 are electricity-only accounts on electrically heated homes.

  So 357 of the 382 drawn homes are gas homes, and every one of them is split-supply by construction, with the other fuel at an unseen rival.
- **The same coin feeds other paths.** It also feeds the trickle (`_drawn_trickle`, through `iter_acquisition_events`) and the default of `net_new_acquisition.iter_prospects`.
- **Only campaign wins are drawn as households:** electricity always, plus a gas leg where the home has gas (`_gas_leg_for`).
- **What I could not measure:** the whole book with the trickle and the campaign. That part of the draw needs the NEED file, which is only on Skynet. Measure it there.

## What he said before, and where it landed

He said it once already. On 26 Aug: *"The funnel only ever wins electricity, never dual fuel. Real suppliers win both together far more often than not, and dual fuel changes cost-to-serve, churn and lifetime value -- so a single-fuel-only book quietly distorts every per-customer number we've been arguing about."*

That ruling was applied to campaign wins and nowhere else. Then the founder count was raised, from 13 to 80 on 28 Aug and to 400 on 8 Oct, on the unanchored coin. So the book that runs the whole decade is almost all single fuel.

On 16 Sept, `SEAT_RESULT_THE_LAST_158_REFUSED_RENEWALS_ARE_EIGHTEEN_GAS_ONLY_ACCOUNTS_THAT_CANNOT_LEAVE` found gas-only households. The fix gave them a way out. Nobody asked whether a supplier holding that many gas-only households is plausible at all. Canon says "a ruling lands everywhere or it has not landed" (How this canon works, item 2), and K4 says to treat a reading that is odd against the industry as a finding. Both failed here.

## WORK THIS CREATES

1. **The knowledge work comes first, from published sources (K8: knowledge before build).** Write a knowledge page answering these with cited sources, and with labelled ranges where there is no published number (W7 principle 1, W8):
   - **How GB domestic books split by fuel.** Dual fuel with one supplier, electricity-only, gas-only, and split supply where the home has both fuels but buys them from two suppliers. How that differs between legacy incumbents and challengers, and why: for example, failed or partial switches, historic regional incumbency, and gas-only legacy books.
   - **How GB switching works for a home with both fuels.** One decision or two? What share of switches move both fuels together? How does a dual-fuel home's departure, save and win-back work in practice?
   - **What share of GB homes have no gas.**
   - **Places to start, not answers:**
     - DESNZ subnational statistics: 29.3m domestic electricity meters in 2024, and about 16% of domestic properties off the gas grid.
     - Ofgem's retail market indicators, and Ofgem's *Retail Energy Markets in 2016* (about 28m electricity and 21m gas domestic customers, with discounts for buying both).
     - The CMA Energy Market Investigation customer survey. Its questionnaire asks exactly this: A6 "Mains electricity only", A7 "One company for both" against "Separate companies".
     - DESNZ QEP 2.7.1 counts transfer events, and a dual-fuel switch counts as two (`population_draw.py`). Read it with that in mind.

2. **Check the world against that page, path by path.** Run a census of every route by which an account enters the book (founders, trickle, campaign wins, successor occupants after a home move, anything else), and of every route by which one leaves (renewal departure, loss notice and save, home move, debt). For each route, ask: does a home with gas buy both fuels from us as one household, and does it leave or stay as one? Measure on the 400-founder production shape on Skynet, with N.
   - Also check the housing stock. 357 of the 382 drawn founder homes (93%) are gas-heated, against about 84% of GB homes on the gas grid. Is the premise draw itself off? A gas meter and gas heating are not the same thing, so say which one the knowledge supports.

3. **Find why we missed it, and fix the cause (P13).** Answer three questions:
   - Why did a "documented placeholder" from 13 July stay load-bearing for three months while the book it shaped grew thirtyfold?
   - Why did the 26 Aug ruling reach one path and not the others?
   - Why did the 16 Sept gas-only finding treat an implausible composition as a fact about the world?

   Then find the smallest mechanism that would have caught it. Candidates:
   - a book-composition reality check against published aggregates, run in the Monday end-to-end check (W8: "a reality check on the world rather than an input");
   - a register of unanchored draw constants, each one blocking a founder-count or book-size change until it is anchored or labelled as a range.

   Make whatever you choose mutation-proven.

4. **Sweep for the same class.** Treat every other "documented placeholder" in the draw the same way: `DEFAULT_SEGMENT_WEIGHTS`, `DEFAULT_BAND_WEIGHTS`, the default for `iter_prospects`, and any constant that shapes who is in the book without an anchor. Anchor each one, label it as a range, or name it as a known gap.

5. **Correct the world, under the four principles.**
   - File your predictions first: what the corrected mix moves in volume, cost-to-serve, churn, arrears netting and CLV.
   - Then correct the draw from the knowledge, measured before and after on the same seed.
   - A correction of the world's draw comes before any supplier result, so it is a freeze-then-solve step, not a change made after seeing results (W7 principle 2). Say so in the commit.
   - EP17 ("keep one variable constant") is about holding a fixed draw while bugs are cleared, and this is a bug in the draw. Correct it once, record the new draw as the one held, and report which published figures it moves.
   - The founder count and the prospect cap stay as he set them (P11).

6. **Report.** One stretch-log entry with:
   - the knowledge page;
   - the census of every path, before and after;
   - the root cause and the mechanism that now catches it;
   - the sweep;
   - the published figures that moved.

   Raise anything that would change a ruling as a proposal, with the evidence.

— Director steer, 17 Oct 2026, from his chat words above. The advisor drafted it and measured the founder book.

## Done

*Worker tick, 17 Oct. Full report:
`docs/staging/WORKER_FINDING_THE_OPENING_BOOK_WAS_ONE_PERCENT_DUAL_FUEL_AND_NOW_BEARS_THE_PUBLISHED_SPLIT_2026-10-17.md`.*

- **1. Knowledge.** `docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md`:
  - CMA PF ¶9: 19m of 23m gas customers are dual.
  - CMA/GfK ¶41: 72% of homes one supplier, 9% split, 15–17% no gas.
  - Ofgem CES 2017: switching homes with gas move both fuels together, ~90%.
  - EHS/DESNZ: 14–16% no gas.
  - The steer's reading holds on every point. The repo already had a 21 June page saying ~75%.
- **2. Census, founders at the production shape, default seed.** Before: 382 homes, 0 dual. After: 220 homes, 73.6% dual, 83.6% gas homes; eight seeds pooled read 76.4% dual. Founders and the trickle take the challenger/switching shape, 0.90 of gas homes dual. They were first built at the market-wide 0.83; the advisor's supplier-accounts evidence (10:03 UTC) moved them, and both are reported.
  - **Campaign wins:** 100% dual on gas homes, against a published ~90%. Unchanged; this is the one remaining departure, in the dual-heavy direction.
  - **Exits:** departures are household-level already.
  - **Not re-measured:** home moves, debt and save, for a dual home.
  - **Housing stock:** the founders' homes were 93% gas because `draw_premise` drew heating from `published_heating_weights()`, which drops oil, communal and solid fuel. They now draw the gas meter first (EHS 86.0%). The harness's 60-home panel has the same defect, and is handed on with its pinned values.
- **3. Cause.**
  - The placeholder named no anchor page.
  - The 26 Aug ruling was fixed only in the funnel where it was seen.
  - The 16 Sept finding took 28% gas-only as a fact about the world.
  - No control compared the book with the published record while it grew 13 → 400.

  **Mechanism:** `tests/simulation/test_the_opening_book_bears_the_published_fuel_split.py`, run at the production founder count over eight seeds, against published bands. Mutation-proven (P(dual)=0, meter-first off and the old coin each red it).
- **4. Sweep.**
  - Commodity coin: retired.
  - Founder heating weights: replaced.
  - `DEFAULT_BAND_WEIGHTS`: named a GAP, with NEED as the anchor to measure next.
  - Segment and lambda: not fidelity shares.
  - Combi/storage splits: labelled GAPs.
- **5. Correction.**
  - Freeze-then-solve, decided before any supplier result. It is now the held EP17 draw.
  - Predictions were filed first in `docs/staging/records/WORKER_PREREG_WHAT_DRAWING_THE_FUEL_FROM_THE_HOME_DOES_TO_THE_OPENING_BOOK_2026-10-17.md`, and all landed inside their ranges.
  - The 400 is held as supply points, so the founders now hold ~233 households.
  - Whether he meant 400 households is raised as `the-founder-number-has-two-readings-now`, with the recommendation to keep supply points.
- **6. Not yet:** the published run figures move at the next run on this code.
