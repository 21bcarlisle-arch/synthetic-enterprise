**Severity:** BLOCKING · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Grade the weather-to-price chain on the record now, so forward years are not held by it

**Type:** STEER, through the advisor channel. The director's words, from chat, Tue 24 Nov:

- 05:32 GMT: "How far are we away from being stable and accurate enough to start simulating new years of weather and prices and not just history?"
- 05:33 GMT, to the advisor's recommendation to check the price chain now: "Yes"

## What the advisor told him

- Forward years are planned and approved (the 25 Oct six choices, and the 25 Oct and 11 Nov steers). They wait on the correctness exit test. Legs 1 and 3 are not met. The newest book is refused on 9 breaches against a maximum of 8. The eleventh and twelfth reads each found one serious class, converging from three or four.
- The advisor's estimate: one or two clean books and one clean read, about 1-2 weeks, then the forward-years build at up to about 15 points of a week in pieces, about 1-2 weeks inside the feature third. That puts the first forward futures around early to mid December.
- **The concern he accepted:** `sim/weather_price_chain.py` prices the daily mean with a **£24/MWh MAE against a real mean of £78** (FORWARD_YEARS_RECOMMENDATION §0, §3). That is about 30%. Forward years will form price from this chain, and hedging will be judged on it.

## What is asked

1. **Grade the chain on the 2016-2025 record now.** This is grading on the record, not a forward run, so it is allowed before the exit test (FORWARD_YEARS_RECOMMENDATION §8, "holding position"). Use his two steers as the acceptance frame:
   - **Volatility at every scale:** half-hourly, daily, weekly and seasonal distributions and the extremes, against the record.
   - **Weather and price move together, and spells last:** the cold-and-still premium, spell length and autocorrelation, and the joint distribution of weather and price.
   - Report the error **by regime**: pre-crisis, 2021-23, post-crisis. A single MAE across a gas-price shock hides where it fails.
2. **Pre-register the acceptance bands first.** What error is good enough for the questions forward years will answer? For hedging and pricing, that means a forward's value and a supplier's cost of supply. Answer that question before the run, under R5. A per-day MAE may matter less than whether the monthly and seasonal costs a hedge book sees are right.
3. **If it fails, find out why (the 22 Nov curiosity steer).** Candidates:
   - the gas floor;
   - the residual-demand-to-price mapping;
   - missing interconnector or outage terms;
   - the fleet changing over 2016-2025.

   Fix the largest cause, or state plainly the error that forward figures will carry, beside every figure (§3, "known error").
4. **Place it first in the feature third** in Sunday's weekly review, or earlier if the third has room this week. It must be done before the exit test is met, so that the price model is not the next hold.

## Addendum, Tue 24 Nov 05:39 GMT: carbon price and CfDs

The director's words: "Carbon price? Cfds?"

What the advisor found on origin:

- **Carbon.** `sim/weather_price_chain.py` leaves the carbon term at 0.0. Its docstring says "adding a real UK-ETS series is future work". `sim/price_engine.py` has the term but defaults it to 0.0 in every call. Only the flat Carbon Price Support (about £18/t) is priced, in `sim/merit_order_reconstruction.py`.
  - A real series has been sourced since 3 Aug: `docs/market_research/eu_uk_ets_carbon_price_series_2026-08-03.md`. The EU ETS series and the FX are high confidence. The UK ETS series is medium, with a caveat: the civil-penalty price is not the market price.
  - **At a gas plant's roughly 0.37 tCO2 per MWh, a carbon price of £50-80/t adds about £20-30/MWh.** That is the size of the chain's whole £24 MAE. And it moved from about €5 in 2017 to over €80 in 2022. **Missing carbon is a leading suspect for the error**, and it will bias forward prices low wherever carbon stays high.
- **CfDs.** The CfD levy is in the supplier's policy costs (`simulation/policy_costs.py`) as a **fixed historical table by year**, including the negative 2022 rate. That is right for the record.
  - **It is wrong for forward years.** The CfD levy is the gap between strike and market reference price. It goes negative when wholesale prices are high, as in 2022. It must be **computed from the simulated wholesale price** and the CfD fleet's strikes and volumes, not read from a table.
  - The same applies to any policy cost whose size depends on price.
  - CfD and other renewable output also bids near zero in the merit order. It shapes price formation through residual demand, which the chain already uses.

What is asked, added to the steer above:

1. **Put carbon into the record grading as a named candidate fix:** the Carbon Price Support plus the traded allowance price (UK ETS from 2021, EU ETS before). Grade the chain with and without it, with the predicted improvement filed first. Resolve the UK ETS caveat by finding a market price series for the UK allowance (UKA), not the civil-penalty price, or state the gap.
2. **For forward years, carbon is a drawn input like gas**, in a sourced band: DESNZ carbon value or traded-price projections. Draw it jointly with gas where the evidence supports that. Set the band by curriculum, which is the director's.
3. **The CfD levy (and any price-dependent policy cost) becomes endogenous for forward years:** strike against the simulated reference price, times the CfD fleet's volumes. Check it on the record against LCCC's published Interim Levy Rate, including the 2022 negative. The supplier still sees only the levy as a real supplier would, not the mechanism's inside.
4. **K8 first:** a short page on carbon pricing and CfD levy mechanics with sources, GAPs labelled.

## Addendum, Tue 24 Nov 05:40 GMT: gas first, interconnection, and why there is no deep page

The director's words: "Interconnection? Nb. Start with gas, getting gas right first is key as it drives elec often. Why isn't the model drawing on a deep knowledge page? Cfds etc are obvious"

**What the advisor found on origin, 05:40:**

- **There is no deep knowledge page on GB wholesale price formation.**
  - The five published Knowledge topics are short (about 75-115 rendered words each, the body in `site/data/knowledge_wholesale.json`): electricity-wholesale, gas-wholesale, carbon-price, how-gb-gas-and-power-prices-move, gb-electricity-market.
  - Across the wholesale knowledge data they mention interconnectors **0** times, CfDs **0** times and the merit order **0** times.
  - `sim/weather_price_chain.py` was built and taken to L4 without one.
  - Interconnectors appear only in the grid-carbon modules, not in price formation.
- He is right that these are obvious. Any GB power trader would name these drivers first:
  - gas, and the gas-plant cost with carbon;
  - interconnectors;
  - the renewable support schemes (CfD, RO);
  - nuclear availability;
  - scarcity and the balancing mechanism.

  **This is a K8 breach on the world side, and a clean case for the 22 Nov curiosity measure:** "nonsense found by the director before the machine". File it in the learning loop as a world model built to L4 with no knowledge page beneath it. Find any other world model in the same state.

**What is asked. This supersedes the order of work above, not its content.**

1. **Gas first.** Get the GB gas price right before electricity, because gas sets the marginal power price most of the time.
   - Write the deep **K8 gas page**: how the NBP and SAP price forms.
   - Its drivers: UK Continental Shelf supply, Norwegian pipeline flows, LNG and the global LNG market, storage (and the loss of Rough in 2017), interconnection to the continent through IUK and BBL and coupling to TTF, seasonal and weather-driven demand, and the 2021-23 shock.
   - Then grade the world's gas price record and any gas drawing for forward years against it. The world's daily SAP splice landed on 18 Nov; start from it.
2. **Then the deep electricity page:** price formation from the merit order.
   - Gas-plant short-run marginal cost (gas plus carbon: Carbon Price Support plus UK or EU ETS) and efficiency.
   - Renewables and their support schemes (CfD, RO), and negative-price behaviour.
   - Nuclear.
   - **Interconnectors:** France, Belgium, the Netherlands, Norway, Denmark and Ireland. Their capacity by year, flow direction, price coupling, and the exports of 2022.
   - Capacity Market, scarcity and the balancing mechanism.
   - Demand and its weather dependence.
   - Use published sources: Ofgem, NESO, Elexon, the CMA's 2016 energy market investigation, Cornwall Insight and Aurora summaries where public, and the academic literature on GB price formation.
3. **Then grade and rebuild the chain against both pages,** in order of the largest gap. Add the carbon term from the 05:39 addendum. Add interconnector flows as a price-coupling term, or state why not. Keep the regime-split grading and the pre-registered bands from the steer above.
4. **Mechanism, not only numbers (22 Nov steer):** each page says what moves each driver and how it passes into price. That is what lets forward years respond to a cold, still, low-LNG winter as reality would.
