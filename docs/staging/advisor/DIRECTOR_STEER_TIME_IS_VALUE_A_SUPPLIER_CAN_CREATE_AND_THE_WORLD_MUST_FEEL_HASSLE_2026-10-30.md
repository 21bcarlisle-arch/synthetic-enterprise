**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Time is value a supplier can create: the world must feel hassle, C31 gets real priority, and "value moved" is said in money terms (2026-10-30)

**Type:** STEER, through the advisor channel. These are the director's words from chat on Fri 30 Oct.

- 12:22 GMT: "Do we have a list of the all changes and investments customers can make to save money and carbon? Do we have strong knowledge and research on this to drive both SIM and supplier?"
- 12:22 GMT: "Is time/effort/hassle a factor hidden in customer typology and psychology? Is it considered or in plan somewhere? (I am reacting because it says somewhere that pricing creates no value it just moves it. Which is true in a purely financial sense, but optimises for time/hassle. But equally it's a good challenge as to how a supplier creates value for customers and then shares in it)"
- 12:25 GMT, on the advisor's proposal: "Do it."

## What the advisor found on origin

- **Canon already says it.** M3 names three currencies: money, time and carbon. Time is measured in household minutes per kind of activity and is never converted to £. M10 treats inertia and reluctance as "the operating conditions".
- **The plan already frames it.** `docs/design/C31_TIME_AS_A_CURRENCY_DISCOVER_FRAME_2026-10-04.md` splits time into four kinds: T1 shopping, T2 servicing, T3 recovery and T4 routine admin. It found that 46% of households agree "switching is a hassle I've not got time for", and that call waits averaged 391 seconds in Q1 2022. **But C31 is at level 0, idle, and has been "drawn and deprioritised about 1,900 times".**
- **The world does not feel it.** Households have an activation energy, which is status-quo bias, and an engagement archetype. No household carries a value of its own time, and none has a hassle sensitivity per activity. So a supplier that saves a household time creates nothing the world can register. A ruling that pricing only moves value then becomes true by construction, not by finding.

## The steer

1. **Wording, now (site and copy).** Wherever the site or the docs say that the price level "moves value, it does not make it", say **"in money terms"**. Add one line saying that a supplier can create value in **time**, and that the world does not measure time yet, with a link to C31. The director agrees the money-terms finding is right. It is a fair challenge, but it is not the whole of value.
2. **C31 gets real priority.** It is not to be deprioritised again by default. Its DISCOVER and FRAME passes are reading-only and cheap, so they are drawn **inside the correctness stretch**. Its build follows the exit test, beside the improvement-loop design (`DIRECTOR_STEER_OWN_THE_DESIGN_OF_THE_WORLD_SUPPLIER_IMPROVEMENT_LOOP_2026-10-30.md`). Time is one of the loop's scorecard currencies.
3. **The world must feel hassle.** You own this design, and these are prompts, not a specification.
   - Each household carries a hidden **value of its own time**. It is conditioned on traits such as work, age, children, income and health, and it is drawn from published evidence. Where evidence is thin it is given as a range.
   - Each household also carries a **hassle sensitivity per activity class**, covering T1 to T4, and per measure: arranging an installer, disruption days and paperwork.
   - These enter every decision the household makes: switching, complaining, acting on advice, adopting a measure and staying.
   - The supplier never sees them. It infers them from behaviour or asks.
   - The minutes a household spends on each activity are recorded in the world as truth, so that time saved can be graded against a counterfactual, as money is (M3).
4. **How a supplier creates value in time, as named hypotheses for the loop:**
   - auto-placing a household on the right tariff without shopping;
   - certainty through a fix;
   - smart reads that end estimates and read requests;
   - first-contact resolution;
   - proactive notices that prevent a recovery episode;
   - "done for you" grants and installs.

   Each is a candidate the supplier tests against the time scorecard. It may fairly share in that value through price; that is M2, created then shared. Grade the sharing for fairness (X1–X2), including households with a high time value and low engagement, who are often the vulnerable ones.

## The measures catalogue (knowledge, now)

`docs/market_research/household_carbon_and_the_measures_that_save_it.md` §5 maps about 20 physical measures by £, carbon and verdict. That is a good core, but it is **not complete**:
- It leaves out the money levers: tariff choice, payment method, export tariff, grants, WHD and social support.
- It leaves out several physical measures: glazing, floor insulation, zoning, hot-water timing, heat batteries, hybrids, diverters and V2G.
- No measure carries applicability, uptake, barriers, hassle, what a supplier can observe, the supplier's role, or evidence strength.

The advisor is running a research pass for a **complete catalogue with those columns**. It includes household time and hassle per measure, and a ranking of measures by value per hour of household effort. The catalogue will land beside this file today.

**Ask:** build one Knowledge page, "Every change a household can make", from the existing page and the new pack. Make it the **single list both sides read**:
- the world reads it for who *can* adopt a measure and what drives the decision;
- the supplier reads it for what to offer, to whom, and in what role.

It replaces nothing. It is the index the topic pages hang from.

## Report back

In the next reading, report:
- C31's pass written;
- the wording changed;
- the world-hassle design sketched inside `docs/design/THE_IMPROVEMENT_LOOP.md` or alongside it;
- the catalogue page drafted.

## Addendum, 12:26 GMT: the catalogue is prioritised

The director's words, 12:26 GMT: "This needs to be prioritised based on costs, ease and remaining market size (IE existing pentration, and restrictions)"

The catalogue page must carry a **priority ranking**, not only a list. For each measure:
- **remaining addressable households**: eligible homes × (1 − current penetration), after the restrictions (tenure and landlord consent, house type, roof, off-street parking, gas connection, listed or conservation status, network limits, and what is already installed);
- **cost** to the household, upfront and ongoing;
- **ease** on a 1–5 scale (hassle hours, disruption, the number of parties, installer availability);
- **value per household** in £, carbon and time.

Rank measures by value × remaining addressable households, adjusted for cost and ease. Publish the scoring formula so it can be re-weighted. The advisor's research pass is computing this.

In the world, the same applicability and penetration are **per home**, drawn and hidden: who can adopt is a property of the house and household, not a share. The supplier's version of the ranking is an *estimate* built from what it can observe or ask, graded against that truth.

## Progress (delivery seat, 30 Oct 2026). Not done until item 1 lands

- **Item 2, C31.** DISCOVER/FRAME pass 4 is written
  (`docs/design/C31_TIME_AS_A_CURRENCY_DISCOVER_FRAME_2026-10-04.md` §9). It adds:
  - T5 adoption as its own class;
  - the hidden **hassle price** and per-class sensitivity as level L0.5;
  - the one sourced gradient: DfT VTT rises with income, and commuting is £11.21/h at 2014 prices, read first-hand.

  The map row's block_reason now says BUILD follows the exit test and the atom is not deprioritised by default.
- **Item 3, the world feels hassle.** The sketch is `docs/design/THE_IMPROVEMENT_LOOP.md` §8. It gives three
  checks that can fail, one of which is a collective-switch replay against the Ofgem RCT band. Its one
  canon question, whether a hidden £/h trait is compatible with M3, is raised in `for_the_director` as
  `the-time-steer-s-hidden-value-of`, with a recommendation. The work proceeds on that reading.
- **Measures catalogue.** It is drafted and published
  (`docs/market_research/every_change_a_household_can_make.md`), and the evidence pack has moved to done/.
- **Item 1, wording.** It is being done in another lane (worktree `/tmp/wt_timeword`:
  `tools/generate_value_arms_data.py`, `tools/capabilities_page_figures.py`). This file moves to done/ when
  that lands.
