**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] Forward years come right after the basics, ahead of the tariff, EV and battery levers (2026-10-24)

**Type:** RULING, through the advisor channel. It amends the order in canon P1 (the step order set on 5 Oct). The director's words, from chat on Sat 24 Oct:

- 17:17 BST: "When do we move to future weather and price simulation? Is it in the plan?"
- 17:22 BST: "If we want to play with different tariff types and EV and battery optimisation we need longer runs (and also showing customers the savings etc from their decisions, cost and carbon). Payback is often years. We need the basics of payment, dual fuel, switching etc all working. But after that we probably want weather and simple wholesale prices and forward products for hedging simualted for some future years. This also allows us to see the merits of CLV decisions etc better."

## Where it stood

Forward simulation was step 6 of 7, "a hypothesis that longer runs add value, taken after the levers deliberately". Its atoms are `EP16_anchored_generators` (L0, idle) and `SPINE_1_scenario_world_state` (closed at L2). The building blocks largely exist:
- `sim.weather_engine` and `sim.weather_world`;
- the weather → demand → merit order → price chain, and its reconstructibility test;
- the `sim.scenario` package (spine, gas scenario and two-regime generators, intraday shape, fidelity check);
- `sim.grid_carbon_future`;
- Capabilities' "futures beyond the real record" (Live, 16 tests).

Canon V5 already warns that replaying 2016–2025 gives the designer look-ahead.

## The new order

1. **The basics first.** Finish them before forward years start:
   - the payment and debt engine, through its supplier side (C9 sequence);
   - dual fuel, including gas following a moving household (ruled 17 Oct);
   - switching: loss notices, objections, saves, and dual-fuel switching as one household.
2. **Then forward years**, kept simple. Simulate a run of future years with:
   - **weather:** drawn as a distribution, not replayed;
   - **simple wholesale prices:** formed from that weather and fuel prices, through the existing chain or a simpler anchored generator if that is cheaper;
   - **forward products for hedging:** month, quarter and season ahead, quoted from the simulated curve, so the hedge programme can buy forward into an unknown future.
3. **Then the levers that need long horizons:**
   - tariff types, including time-of-use;
   - EV and battery optimisation;
   - showing households the cost and carbon savings of their decisions over the payback years.
4. **CLV decisions are judged on forward runs too.** The forward years exist partly to show "the merits of CLV decisions" on futures nobody designed.

Steps 1, 2, 4 and 7 of P1 are unchanged in substance: knowledge in parallel, billing accuracy, per-customer decisions, communications last. Forward simulation moves ahead of the long-horizon levers. Canon §2's phases are unaffected: this is Phase 3's forward runs brought into Phase 1's order early, still without in-run adaptation (V2), which stays later.

## WORK THIS CREATES

1. **Update canon P1 and `docs/direction/priority_order.yaml`** to the order above, quoting his words. Use the trailer `Director-doc: his-words -- forward years after the basics, director 24 Oct 17:22`.
2. **Write a definition of done for "the basics"**, as tests and records rather than prose. Put it in the stretch log, so everyone can see when forward years may start.
3. **Bring a recommendation before building forward years (G9).** It should cover:
   - the horizon, for example 2026–2035, and why;
   - how weather and fuel prices are drawn and anchored, with the 2016–2025 record as the calibration and grading set (K8, W8: "a labelled range, not a number" where evidence is thin);
   - which wholesale formation to use: the full chain or a simpler generator, at what cost per run year;
   - which forward products to quote, and how bid-offer and liquidity are treated;
   - how many futures per question, and the memory and run-time cost (R5, R7, R9);
   - how the supplier stays blind to each future (W1: forecast error is the wall on the future).

   Include the cost estimate, under today's estimate-the-cost steer.
4. **Prepare cheaply while the basics finish.** Anchoring the generators against the real record (`EP16_anchored_generators`) can proceed in parallel at low cost. Don't start forward runs, or the long-horizon levers, until the basics are done.

## Report

One stretch-log entry with:
- the updated order;
- the definition of done for the basics, and how far along it is;
- the forward-years recommendation, when ready.

— Director ruling, 24 Oct 2026, his words above; the drafting is the advisor's.

## Progress (24 Oct, still open)

- Work 1 done: canon P1, V3 and the changelog carry the new order in his words; `docs/direction/priority_order.yaml` splits the long-horizon levers (C4, W1_10) into step 7 behind forward years (step 6), and communications become step 8.
- Work 2 in part: the definition of done for the basics is in the stretch log as seven atoms at their target levels. 0 of 7 are at target. Dual fuel is on no atom (GAP). Still owed: a check that grades the table, and minting the dual-fuel atom.
- Work 3 owed: the G9 forward-years recommendation, with its cost estimate.
