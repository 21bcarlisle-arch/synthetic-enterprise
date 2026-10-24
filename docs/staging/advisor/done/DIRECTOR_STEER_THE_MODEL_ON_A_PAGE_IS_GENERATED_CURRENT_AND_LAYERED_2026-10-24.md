**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The front-door diagram: bring it to current, generate it at publish, and ship the layered drill-down he ruled on 9 Oct (2026-10-24)

**Type:** STEER, through the advisor channel. The director's words, from chat on Sat 24 Oct. He sent a screenshot of the diagram on poesys.net:

- 09:42 BST: "Also I really like the diagram on home page, but i thought we already review this to create a multi layer live artefact? In any case this diagram looks to be a bit out of date in places even if it is still very good"

**When:** bring the content up to date for the Monday 26 Oct publish. The generated, layered version follows that publish. Do your own review of every box against canon v4 and the current record. The list below is the advisor's illustration, not the full answer.

---

## What he ruled before, and what shipped

- **27 Jul.** Model, diagram, site and map are never kept in sync by hand. What shipped: the band stage words in the list *under* the diagram are computed from the maturity map. The picture itself is still a static file, `site/assets/model-on-a-page.svg`, so its words never update.
- **9 Oct.** The diagram stays a simple visual with no stats, counters or finding tallies. Going deeper means L2 drill-down sheets, one per band, in the same visual grammar. Any claim of state on an L2 sheet derives from the maturity map. The July drafts (the weather→price cascade) never shipped.
- **12 Oct canon alignment.** This required "THE_MODEL_ON_A_PAGE.md … Timeframe 2, 'Carbon becomes the headline … £/tCO₂e on the front page': replace with CO1 and CO3", and changed "EV is fitness" to "open". The picture still carries both.

## The advisor's illustration: what reads out of date in the picture (24 Oct)

- **The mission line.** "Mission: cut carbon through personalisation — measured in £ per tonne of CO₂e saved" is the retired mission. Use M1 verbatim, or point to it. Carbon's public face is the household's saved and could-save CO₂ (CO1, CO3). £/tCO₂e is an internal diagnostic.
- **Governance.** "Board AI · six stances in tension": is there still a board? If it is retired, take it out. If not, say what it does now.
- **The world.**
  - "competitors — not yet": a published competitor signal now holds renewal prices (`competitor_reference.py`).
  - "three hidden traits, one expresses": households now carry hidden finances, life events, a thermal home under local weather, and dual-fuel supply.
  - "~200 homes, ~12 segments": the book is 400 founder households, and seed families exist (R6).
- **The company.** The loop has no payment and debt engine. Canon says it is "the heart of this business" (M7, C9): a forward cash forecast per customer driving provision, drift limits and plans. Next best action (C7) and the retention save are also absent.
- **The score.** "ABATE: grid intensity × HH use → £/tCO₂e" should read as CO1/CO3. The three currencies, money, time and carbon (M3), are not on the page.
- **"Now" and "Evolves into".**
  - "Carbon ledger designed, not yet instrumented": household half-hourly emissions are now measured.
  - "£/tCO₂e on the front page — the headline": withdrawn by canon decision 4.
  - "EV is fitness, mortality is selection": the fitness function is open until Phase 3.
  - "Customer state layer: moves, births, shocks": partly built (B7: moves, income shocks, deaths).
  - "Holdout-measured uplift": the company's own holdout is now readable (decision 7).
  - "Conversations v1" and "Naive forward belief": check whether these are still true.
- **The phases.** Canon §2 (Build, Adapt, Forward) could anchor the Now and Evolves columns.

## WORK THIS CREATES

1. **Make the content current for Monday.** Correct every box that disagrees with canon v4 or the record. A canon line on the picture is quoted verbatim or cites its id. Use the his-words trailer: this is a director document.
2. **Generate the picture at publish.** Render `model-on-a-page.svg` at publish from `docs/design/THE_MODEL_ON_A_PAGE.md` (the words) and the maturity map (the states), so the 27 Jul ruling covers the picture as well as the list under it. No figure, stat or count goes on the diagram (9 Oct). Extend the canon check to the diagram's words, so a superseded line on the picture reds the build.
3. **Ship the L2 layer after Monday.** One drill-down sheet per band (world, wall, company, score, governance), in the same visual grammar, opened from its band. The weather→price cascade draft is the first. Claims of state on L2 derive from the maturity map. Each sheet links on to the live evidence: Capabilities, How it's built, Explore and The code. The front door stays simple, and depth sits one tap down. The 9 Oct ruling stands: deeper, not denser.
4. **A cold read** of the updated door, one energy reader and one tech reader, as for the other pages.

## Report

One stretch-log entry with:
- each box changed, before and after;
- what your own review found beyond the illustration;
- the generator and the canon check on the picture;
- the L2 sheets shipped, or what they wait on.

— Director steer, 24 Oct 2026, his words above; the illustration and drafting are the advisor's.

## Done

*Seat executor, 24 Oct 2026, lane 0 item `front-door-diagram-generated-and-layered`.*

1. **Content current for Monday.** Landed in 9451cb34e: every box was read against canon v4, with the before and after of each box in that commit. One more correction came later, from the cold read. "9-year record replayed" sat beside "2016–25" on the same picture, a span of ten calendar years, so the line now says "2016–25 record replayed". That was the picture's last statistic, and the no-stats allow-list is now empty.
2. **Generated at publish.** The picture's words are now a yaml block under "## The picture" in `docs/design/THE_MODEL_ON_A_PAGE.md`. `tools/model_on_a_page_picture.py` renders `site/assets/model-on-a-page.svg` from that block. Each Now line's state, and the payment engine's, comes from the maturity map through `moap_stage.compute_stage`, the derivation the list under the picture already used. It runs in `generate_dashboard_data` beside the other front-door writers, and it fails closed. Five markers moved to what the map says: four lines from done to in build (W1_5, EP4, D48/C4, EP13), and the naive forward belief to not started (G15). The canon check over the picture landed in 9451cb34e. `tests/tools/test_model_on_a_page_picture.py` now holds that the served words are the canon page's words.
3. **The L2 layer.** `tools/model_on_a_page_sheets.py` renders five sheets from `sheets:` in the same block: world, wall, company, score and governance, at `/model/<band>/`, in the picture's grammar. Every box on them carries its state from the map, and every sheet links on to Capabilities, How it's built, Explore and The code. The world sheet is the weather cascade, from real weather to each home's demand to settlement, beside the record and household chains. Each band in the picture links to its sheet, and each entry in the list under the picture opens its sheet. The door's `<img>` stays single, because `site/test_home_door.py` holds that it is hosted once. `tests/tools/test_model_on_a_page_sheets.py` covers the sheets.
4. **Cold read.** One fresh Sonnet instance read the picture and the world sheet, as an energy reader and then as a tech reader. It found that the price cap chained into settlement and that demand restated use, and both were fixed. The points that touch canon wording are in the stretch log for the director:
   - "learn from true-up": the trade term is reconciliation;
   - "serve & converse — always on" sits beside conversations marked in build;
   - "three currencies" sits beside time not yet instrumented;
   - "Tier-1 bill accuracy · assets on anchored S-curves" is opaque to a billing reader;
   - the canon ids on the picture are unexplained.

The report is the stretch-log entry of 24 Oct, "The front-door diagram is generated at publish…".
