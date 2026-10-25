**Severity:** BLOCKING · **Lane:** W1_market_weather · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Forward years must reproduce the volatility, and the calm, of weather and prices at every time scale (2026-10-25)

**Type:** STEER, through the advisor channel. It adds requirements to `docs/design/FORWARD_YEARS_RECOMMENDATION_2026-10-24.md` (choices 2–5) before his yes on the six choices, which the advisor has asked him for separately. The director's words, from chat on Sun 25 Oct:

- 05:12 GMT: "Will the gas price have appropriate volatility too? And mix and depth of backwardation and contango? And the range of the spark spread. Overall keen that weather and price create the daily, weekly,.monthly, yearly volatility and lack of volaity that can be seen, as this uncertainty in forecasting what's ahead is a key challenge of running an energy supply business, advising customers and optimising their assets."

## Why it matters

Forecasting under uncertainty is the job. Hedging, pricing, cash forecasting, advice and asset optimisation all live in the gap between what was expected and what happened. A forward world that is too smooth, or too wild, or has the wrong shape over time, would flatter or punish every supplier decision for the wrong reason. Uncertainty is treated as part of the world being built (W1: "forecast error is the natural wall on the future").

## What the forward world must reproduce

Each item is a measured property of the 2016–2025 record, filed as a **world claim** with a band (W8, `tools/world_claims.py`). Grade the forward generators against them before any forward run is used for a supplier result: freeze, then solve (W7 principle 2).

1. **Volatility at each scale.** Report realised volatility of gas, power, temperature and wind at daily, weekly, monthly and yearly horizons, by season. Cover both quiet and turbulent periods, so the forward world shows **calm stretches as well as stormy ones**: volatility clustering and regime persistence, not uniform noise. The 2022 crisis is in the record and in the fit as a possible tail, not a certainty.
2. **The gas path itself.** Report the distribution of daily log-returns (fat tails included), mean reversion, and how a shock decays. The recommendation's §2b already proposes "log-returns with the record's volatility and mean reversion, fitted on 2016-2025 NBP". Grade it against the record at every scale in item 1.
3. **The shape of the forward curve: how often backwardation and contango occur, and how deep.** From the record, measure:
   - the share of days the curve was in backwardation or contango;
   - the distribution of slope (front month against season-ahead, and season-ahead against year-ahead);
   - how slope relates to the spot level (high spot usually means backwardation);
   - seasonal shape (winter over summer).

   A forward quote "at the conditional expectation plus the sourced term premium" (§4) must reproduce that mix and depth. `docs/market_research/uk_power_forward_curves_2016_2025.md` is the starting point. Gas curves need the same treatment, and they are not in the knowledge layer yet (K8 first).
4. **The spark spread's range.** Clean and dark spark spreads (power minus gas at plant efficiency, minus carbon) have a distribution by season and time of day in the record. That includes near-zero and negative periods, and crisis peaks. The weather chain prices power on a gas floor, so check it reproduces the spread's range and how often it sits there, not only the power level. The chain's known daily error (£24/MWh against a mean of £78) is published beside every figure. Show whether that error flattens the spread's tails.
5. **The links between them.** Gas against power, temperature against demand against price, and wind against price (still, cold days). Measure their correlation by scale and in the tails, so a cold, still, gas-tight week can happen together, as it does in reality.
6. **Forecast error growing with horizon.** The supplier's own forecasts (consumption, price, cash) should show error that grows with lead time at roughly the record's rate. That is the uncertainty the director names. It is measured on the supplier's side, through the wall, never fed from the truth (W7 principle 4).

## WORK THIS CREATES

1. **A K8 page first:** "how GB gas and power prices move: volatility by time scale, curve shape, spark spreads, 2016–2025", with sources: NBP, N2EX/APX, ICE Endex, Ofgem wholesale indicators, Elexon. Its headline figures become the world claims for items 1–5.
2. **Grade every candidate generator** (block-drawn weather, the gas path, the weather→price chain, the forward quote) against those claims as part of the EP16 anchoring the ruling already allows in parallel. Where a generator fails a claim, say which one and by how much. Fix it, or name it as a limit, erring against our own thesis (F11). Don't tune a generator to a supplier outcome.
3. **Publish the grading** on the map's world spine ("Wholesale price", "Weather") and in the forward-years page, so a reader sees that the future is as uncertain as the past was, in the same ways.
4. **Fold the result into the recommendation.** If meeting these claims changes any of the six choices, for example the bimodal or regime component being needed after all, or the full merit-order rebuild being worth its cost for the spread's tails, bring the changed choice back to him with a recommendation (G9).

## Report

One stretch-log entry with:
- the K8 page;
- the claims table, record against each generator at each scale;
- what passed, what failed and by how much;
- any change to the six choices.

— Director steer, 25 Oct 2026, his words above; the drafting is the advisor's.

## Progress (seat-executor, 2026-10-25 ~11:55Z; the file stays in the queue)

- **Work item 1, the K8 page: done.** "How GB gas and power prices move" is published (7fb1aabcc3, `docs/market_research/how_gb_gas_and_power_prices_move_2026-10-25.md`). Its own check: 7 confirmed (covering 24 figures), 0 corrected, 5 still open.
- **Routed:** the ruling made these claims the forward years' pass mark. EP16 is unblocked against them (`docs/design/maturity_map.yaml` EP16 `block_reason`), and `docs/design/curriculum/forward_years.json` says no forward run is used for a supplier result until they pass.
- **Not done: work items 2-4.** No volatility, curve-shape, spark-spread or correlation claim exists yet in `tools/world_claims.py` (a grep for "volatil" finds none). No generator has been graded, and nothing is published on the world spine. That is EP16's work and it waits on the page's headline figures becoming claims. The file stays here until the claims table and its grading are reported.

## Done

Work item 1, the knowledge page, landed in 7fb1aabcc3 as `site/knowledge/how-gb-gas-and-power-prices-move/` (note `docs/market_research/how_gb_gas_and_power_prices_move_2026-10-25.md`). Its count on the Knowledge index is 7 confirmed, 0 corrected, 5 still open. Work items 2-4 are EP16's, as below.

Moved here 2026-10-25 by the seat-executor. The signed ruling (the advisor's own commit, ccf49bf88) was read and is being acted on; the file sat in the queue refused as unsigned only because the machine's progress notes above were appended after the advisor staged it. Those notes stay as the record of what landed. What is still owed is carried by: work items 2-4 are EP16's on the maturity map (the volatility, curve-shape, spark-spread and correlation claims in `tools/world_claims.py`, then grading the generators against them).
