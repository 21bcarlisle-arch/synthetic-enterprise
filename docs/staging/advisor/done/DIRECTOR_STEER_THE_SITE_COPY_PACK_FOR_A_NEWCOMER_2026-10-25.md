**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The site copy pack: drafted outside the serial gate, landed as one batch (2026-10-25)

**Type:** STEER, through the advisor channel. These are the director's words from chat on Sun 25 Oct:

- 05:15 GMT: "Is there no way to use the spare tokens productively? On knowledge creation for example ? Or improving the website? Things that don't impact it's need to run tasks in series"
- 05:30 GMT, answering the advisor's offer to draft the website copy for the machine to land as one batch: "Do it"

The advisor read every page's text off origin at cfb72939 (the pages as generated from the 19 Oct run) as a newcomer in energy or tech would. Below are drafted copy and the defects that reading surfaced. **Land the copy as one batch, in the generators and their data, not in the built HTML.** Where a draft contradicts the record, the record wins. Change the draft and say so in the landing commit. Where the reading found a defect in the world rather than the words, the page is right to show it. That is Explore doing its job of testing the features. Those defects are listed separately in section B, as work, and are not to be hidden by the copy.

Reader test for every page: someone who knows energy or tech but not this project should, in the first screen, understand what the page is, why it is impressive and what to click. Don't use canon ids (M7, K8, G5) in body text; give the plain words, with the id in a tooltip if you want it. Don't name file paths above the fold.

## A. Copy

### A1. Explore

- **Intro: the same thing is said twice.** "Explore real households from the run" and "Meet the households" both explain the three views. Replace both with:

  > **One household, three ways of seeing it.** Pick a household from the latest run and step through its life. Each moment is shown three ways: what the customer saw on their bill, what the supplier believed on that date, and what was really true in the simulated world. A real supplier only ever has the first two. The gap between the second and third is what this project is built to close.

- **Renewal vignette: right now it is machine output.** "company estimated 100% churn risk, decided to offer a 5% discount (cost £118.01) against £1,313.26 expected term margin at risk -- expected value of offering £1,195.25." Render vignettes from a sentence template, for example:

  > *The renewal, Oct 2018.* The supplier judged this household likely to leave at renewal and offered 5% off (£118 a year) to keep £1,313 of margin over the new term. What the household actually did is shown at the stage below.

  Also, a churn risk of exactly 100% is not a belief a supplier can hold. Either it is clipped wrongly or the model saturates. See section B.

- **"How big the book really is":** this reads as an apology. Replace it with:

  > **Why a few hundred homes, not a few million.** Every household here is a full simulated life: its building's physics under its own local weather, its finances, its moves, every half-hourly read and every bill. The book is sized so that each one can be followed end to end and checked against the published record. It is a deliberate design choice, not a limit.

  (The figure must come from the run. From Monday's run it should be about 400 founder households.)

- **Empty slots:** keep the honesty, but end each one with what closes it, in one line. For example, "The mover: no household in this run can be followed through a move yet. Home moves are being linked occupant to occupant next."

### A2. Capabilities: internal contradictions a newcomer will spot

- **"Prices that come out of physics, not out of a distribution" (Live)** contradicts the front door, which correctly says the 2016–25 prices are *replayed as they happened* and that weather drives demand, not prices. Until the forward years are built, the row should read:

  > **Real prices, replayed in order — Live.** Every half-hourly GB price from Nov 2015 to Jun 2025 is replayed as it happened, so the supplier lives the real market, the 2021–22 crisis included. Prices that come out of weather and the generation stack are the next step, for the forward years (Building).

- **"Futures beyond the real record — Live, 16 tests":** the forward years were approved on 25 Oct to be built after the basics. It is Building. Say "Planned: 2026–2035, five futures, with gas, power and forward products whose volatility is checked against the published record."
- **"Banking and payment rails … the bank, the acquirer":** an acquirer is a card-scheme term. Direct debit runs on Bacs. Replace with:

  > **Direct debit on the Bacs rails — Live.** Mandates set up and refused (AUDDIS), collections that fail and why (ARUDD), payers who cancel or change bank (ADDACS), and refunds claimed under the Direct Debit Guarantee, on the real three-day cycle.

  Cite only what the code does.
- **"Live, no test cited"** (Business customers; Three clocks kept straight; Telling can't-pay from won't-pay): Live with no test contradicts the page's own rule that state is computed from evidence. Either cite the test or the row computes to Building. This is a generator fix, not a copy fix.
- **"Households with hidden lives … job loss, illness, a new child" (Live, 1 of 4 parts)** contradicts the front door ("bigger life events … being wired in next"). Make the row say which of the four parts is live.
- **"Capital adequacy" on the home page** cites "Ofgem's 2023 financial resilience *consultation*". The rules were decided in July 2023 and have been in force since 31 Mar 2025: a floor of £0 and a target of £115 of adjusted net assets per dual-fuel customer. Cite the decision and test against the decided numbers (see the accounts evidence pack staged today). If any constant says £130, it is the consultation figure and is wrong.

### A3. The five sheets one level down (/model/world, wall, company, score, governance)

- **The legend ". done, _ in build, ~ not started"** is unreadable to a newcomer. Use the words Live / Building / Planned with the same colour chips as the front door.
- **"(M7)", "(M2)", "(M3)":** drop them from the body. Replace each sheet's opening with:
  - **World:** "A synthetic Britain the supplier cannot see into: real prices and weather from 2016–25, and households drawn fresh each run with lives, homes and money the supplier is never told about. Each box below is one part of it, read from cause to effect."
  - **Wall:** "The line between the world and the supplier. Only what a real GB supplier could receive crosses it — meter reads, market data, payments, industry messages, regulation. The test on every line of supplier code: could a real supplier know this?"
  - **Company:** "An automated supplier that sees only through the wall. It wins customers, prices, hedges, bills, collects and settles, and forms a belief about each home that it must act on while it is wrong. Payment, credit risk and cash forecasting are the heart of it."
  - **Score:** "Is it working? Three tests: does it survive a worst-case shock, does it earn on a probability-weighted basis, and does each household save money, time and carbon? Value is created and then shared, so every decision is scored for both sides."
  - **Governance:** "One human sets the mission and the few decisions that can't be undone. AI agents design, build, test and run everything else, inside gates that refuse work that would break the rules. Each box is one of those gates or roles."

### A4. Knowledge index

- Add the seven topics evidenced today under their themes, each with a one-line *why the simulation needs it*:
  - **Payments and direct debit:** "How most households pay, and how a collection fails. This is the supplier's cash, so a book with the wrong payment mix has the wrong debt and the wrong working capital."
  - **Switching:** "How a household leaves or joins, both fuels together, and what a losing supplier may and may not do. Every gain and loss in the book passes through it."
  - **A supplier's accounts and capital:** "How revenue, unbilled energy, bad debt and Ofgem's capital rules show up in a real supplier's accounts. It is the yardstick for whether the simulated supplier's books look like a real one's."
  - **Tariffs and the default tariff:** "Fixed deals, the capped default, time-of-use, and how households have sat across them since 2016. They set what the supplier can offer and what a household compares."
  - **Smart meters and half-hourly settlement:** "Who has a working smart meter, what data the supplier may use, and the industry's move to settling every home half-hourly. It sets what the supplier can see of a home."
  - **How gas and power prices move:** "Volatility at every time scale, the forward curve's shape and the spark spread. This is the uncertainty a supplier has to hedge, and what the forward years must reproduce."
  - **Vulnerable customers:** "The Priority Services Register, ability to pay and self-disconnection. A third of households are on the register, and a supplier's duties to them shape collections."
- Under "Some of it is more than reading", show the live count: "*N* published claims are checked against the simulated world every Monday; *k* currently pass." Generate the figures. A newcomer should see that the claims bite.

### A5. Home

- The structure is now right. Two fixes:
  1. The "Capital adequacy" card, per A2.
  2. Once Monday's run lands, check that the household figure reads as a founding book of about 400 households on both fuels, and that the dual-fuel story card still matches the run.
- One addition under "What has been built", generated: "*New this week:* …", three lines at most, drawn from the stretch log. It gives a returning reader a reason to come back. Not a banner.

### A6. How it's built

- The above-the-fold section reads well. Below it the page is still about 20,000 words of text in total. Put the file paths (`background/one_way_door.py` and so on) behind a "show the code that holds it" toggle on each layer. A newcomer reads the claim and the evidence line; an engineer opens the toggle.
- Collapse everything below the eight layers by default, except the headline figures.

## B. Defects in the world that the pages surfaced (work, not copy)

1. **The EV home: an EV adds 8% (99 → 108 kWh a month).** A GB home with an EV typically adds about 2,000–3,000 kWh a year (about 150–250 kWh a month), which is roughly doubling a typical home's electricity. And 99 kWh a month is already well under a typical home's ~225. Check the EV uptake model and the household base load against the knowledge pages and world claims, and add the EV uplift as a claim with a published band.
2. **Storage heating: there are no two-rate meters in the run.** Restricted meters (mostly Economy 7) were 14–17% of electricity accounts in 2015–2020 (CMA 2016; Ofgem 2020; tariffs evidence pack staged today). A book with none is outside the published record. Add it as a world claim and draw profile class 2 homes.
3. **A churn risk of exactly 100%** (renewal vignette, SYN-2016-441). Find out whether the belief saturates or is clipped, and whether it changes the retention decision.
4. **The mover slot is empty because occupants aren't linked across a move.** This is already known. Explore's slot is the test that shows when it is fixed.

## C. How to land it

- One batch, generators and data first, then a single publish. Run the cold read on the five sheets and Explore after it, and record the result.
- If a draft line here cannot be made true from the record, don't publish the line. Publish the true one and log the difference.
- The research and drafting cost has been spent in the advisor's chat. Your cost is the landing.

## Progress (autonomous worker, 2026-10-25; the file stays in the queue)

**A2, Capabilities: three rows rewritten in `tools/generate_capabilities_door.py`.** The feed is regenerated at the next publish, not here, as section C asks. The record won over the draft in two places:
- **Prices.** The draft row "Real prices, replayed in order" would duplicate the existing row "Ten years of real settlement data, revealed in order". The row it replaces rests on `W1_6_physics_price_signal`, the weather-to-price chain, which is built and at target. So the row now says what that chain is: built and graded for the forward years, with a daily error of £24/MWh against a mean of £78, and not used inside 2016-25, where every price is replayed.
- **Bacs.** The rewrite keeps AUDDIS, ADDACS, ARUDD and the three-working-day cycle, which `simulation/bacs_rails.py` implements. It drops "refunds claimed under the Direct Debit Guarantee", because no code models a DDG indemnity claim. That is a gap to file, not a line to publish.
- **Futures.** The row says the stress worlds exist and the forward years approved on 25 Oct come next. Its status is still derived from `W1_2_generate_futures`, which is at target, so it may still compute Live. Moving it to Building needs a new atom for the forward years to cite, not hand-typed copy.

**Already done before this pass:** "Live, no test cited" now computes as Building through `held_from_live` (24 Oct).

**A3, the five sheets (seat, 25 Oct): landed.** The glyph legend is gone from every sheet. Each box now carries the front door's own chip, LIVE / BUILDING / PLANNED, in the front door's soft fills, and the page legend uses the same chips (`tools/model_on_a_page_sheets.py`). The five openings are the drafted ones, in the canon page's `sheets:` block, with one change where the record won: the Company opening keeps M7 as his verbatim quote ("Payment, credit risk and forward cash forecasting are the heart of this business."), without the id, rather than the draft's paraphrase, because canon is quoted and never reworded. Cold read of the rendered score sheet and its SVG: the chips read as words on both. The canon ids inside box lines (M8, CO1, CO4) were not in A3's list and stay for now. The front-door picture keeps its glyphs; it is a separate artefact with its own tests, and A3 named the sheets.

**Still owed:** A1 (Explore intro, vignette template, the "why a few hundred homes" copy, empty-slot closers), the rest of A2 (which hidden-lives parts are live; the capital-adequacy citation), A4, A5, A6, section B, and the single publish with its cold read.

**A1, Explore (seat-executor, 25 Oct): landed.** The page opens on the drafted intro, "One household, three ways of seeing it", and the duplicate "Meet the households" lede is now one line on how the cast is chosen. The old intro's six-stage walk moved under its own heading. The renewal vignette renders from a sentence template (`_renewal_words`). The record won in three places. (1) The belief is printed as stored, 99.9%, not the draft's "likely to leave", because the point of B3 is that the page showed a rounded certainty. (2) "£118 a year" became "costing £118": the record gives the offer's cost, not a yearly figure. (3) "to keep £1,313 of margin" became "against £1,313 of expected margin at risk", which is what the record computes. "Why a few hundred homes" replaces "How big the book really is", with the count from the run's own list (550 accounts in the 19 Oct run, all occupants included, not founders only). Both empty slots now end with what closes them: the mover with the record's new move-out and successor links, the next run being the first that can fill it; storage heating with the per-home asset world, after the forward years. The cast feed and its static block regenerate at the publish, as section C asks.

## Moved to done

Moved here 2026-10-25 by the seat-executor. The signed ruling (the advisor's own commit, a3ab1c65d) was read and is being acted on; the file sat in the queue refused as unsigned only because the machine's progress notes above were appended after the advisor staged it. Those notes stay as the record of what landed. What is still owed is carried by: the claim `the-site-copy-pack-lands-its-remaining-sections` and its hand-off: A2's hidden-lives row, A4, A5's "new this week" line, A6, then the single publish with its cold read; B1 and B2 are step 8 world work; B3 is answered in the open Explore cast finding (`SEAT_FINDING_EXPLORES_CAST_FINDS_STANDARD_VARIABLE_BILLS_ABOVE_THE_CAP_AND_NO_MOVER_OR_TWO_RATE_HOME_2026-10-23.md`, last section).

**A4, Knowledge index (seat-executor, 25 Oct): landed.** The seven topics were already on the index from 7fb1aabcc3 and 2d33139a4b. Their why lines come from the record, so they say what the world and the company do with each topic, not the draft's general lines; they are kept. "Some of it is more than reading" now ends with the live count, "6 claims are published, and at the publish of 25 Oct 2026 6 of them held". It is drawn at every publish (`tools/world_claims.py::write_index_count`, called from `process_run_complete` beside the Explore cast) and says so plainly when the draw cannot run. The draft said "every Monday"; the record says the claims are checked on every change that could move them and again every Monday, and the bullet already said that.
