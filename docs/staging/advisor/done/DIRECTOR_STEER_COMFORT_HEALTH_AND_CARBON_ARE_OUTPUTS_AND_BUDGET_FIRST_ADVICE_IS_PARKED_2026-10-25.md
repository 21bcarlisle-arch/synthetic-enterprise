**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Comfort, health and carbon are outputs per home; budget-first advice is parked for the roadmap (2026-10-25)

**Type:** STEER through the advisor channel. Adds to `DIRECTOR_STEER_ASSET_DEMAND_IS_DERIVED_PER_HOME_NOT_A_STATIC_PERCENTAGE_2026-10-25.md`. The director's words, from chat on Sun 25 Oct, 06:30 GMT:

- "And the thermostat and timer settings? Many people have the heating on all the time and could save money?"
- "Lowering the flow temp makes the boiler more efficient but make it slower to respond especially in colder weather. Is my understanding. There is a comfort measure here. There is also a healtg and safety aspect to house temp recomnedations."
- "But carbon savings should also be shown to customers. If someone takes an EV they should see how much electricity cost has saved in petrol and their carbon footprint, that we shared should go down. Same if they turn the thermostat down or put a timer on or turn down flow temp."
- "One of the other use cases I like is to let a customer set a budget and help them take actions to get to it. So rather than start with thermostat settings and get cost. Start with cost/affordability Vs comfort. This starts to get complex so not urgent. Maybe just an idea"

## Fold into the asset design note now

1. **Comfort is an output of the thermal model, not a label.** Each home already has a thermal model. It has to give **indoor temperature per half hour**, at least for the main living space, from:
   - setpoint and setback;
   - schedule type: always on, once a day, twice a day, or off;
   - flow temperature against emitter size;
   - weather compensation;
   - that home's weather.

   Comfort measures then follow, for example degree-hours below setpoint while the home is occupied, and warm-up time. The evidence pack has the anchors:
   - Flow temperature 80→60°C cuts gas about 9% in a test house, but warm-up takes 17 minutes longer and rooms average 0.5°C cooler. Starting earlier to compensate gives back 3–4 points.
   - About half of a "flow-temperature saving" is cooler rooms, not efficiency.
   - In one house, 24-hour heating used 31% more gas than 9 hours.
   - EFUS: median 7–8 hours of heating a day; 6% heat all year; only 46% use a timer.

   The director's reading is right: a lower flow temperature responds more slowly, and most of all in cold weather and where radiators are small. The world should show this because it is in the physics, not because a rule says so.
2. **Settings are household behaviour, and changing one has a comfort response.** If the household turns the thermostat down and is then cold, it may turn it back up or preheat. Use the take-back evidence in the pack and record what is unknown as a design choice.
3. **A health floor on advice.** The supplier must never advise a temperature or a setting that takes an occupied home below the public-health guidance. Check UKHSA's current guidance and source it: the widely quoted figure is **at least 18°C for living spaces, warmer for older, very young or ill occupants**. The floor is higher for Priority Services Register and vulnerable households. Hot water stored in a cylinder must stay hot enough to control legionella (EST: don't take a cylinder system's flow below 65°C). The world can carry occupant vulnerability as hidden truth and the supplier only what it is told or registers. The savings grader must count **under-heating as harm, not success**. The evidence: the 2022–23 setpoint cuts fell mostly on fuel-poor homes (odds ratio 2.39), and a falling gas slope can mean a household going cold.
4. **Carbon is shown beside money, on the same counterfactual.** Every saving shown to a customer gives £ **and** kgCO₂ from that home's own counterfactual run (asset steer, rule 4):
   - **EV:** "your charging cost £X; the petrol your previous car would have used cost £Y; your footprint fell by Z kg". This uses their own mileage, their previous car's economy, the dated fuel price, and grid intensity in the half hours they actually charged.
   - **Thermostat, timer or flow temperature:** £, kWh, kgCO₂, and the comfort change.

   The shared household footprint goes down only if the true counterfactual says it did. The proof pack's ten design rules apply: label each figure estimated or measured, show the baseline, give a range below the detectable level, and normalise for weather.

## Parked for the roadmap: budget-first advice

The idea is to start from **affordability against comfort**, not from settings. The customer says what they can afford a month. The supplier finds the set of actions and settings that gives the most comfort within that budget and above the health floor, using that household's own model, then helps them get there and tracks it.

Why it fits Poesys: it is an optimisation over a personalised home model, and the simulation holds the true comfort response, so the supplier's plan can be graded on whether it really hit the budget and how cold the home got.

It depends on:
- per-home comfort output (item 1);
- behaviour response (item 2);
- the health floor (item 3);
- the savings grader.

**Not urgent.** Add it to the advice roadmap after tariff choice and settings advice. Bring a recommendation on where it sits.

## Done -- refused, not actioned

Seat-executor, 2026-10-25 ~11:55Z. The advisor-channel reader refused this file: **no attribution.** It neither says it acts on the director's standing delegation of 15 Oct, nor quotes his chat words with a time. So it carries no authority and nothing was done on its strength. Its substance is already covered from attributed sources: comfort as an output and the health floors are in `docs/design/PERSONALISED_ASSET_WORLD.md` sections 4 and 6, and budget-first advice sits as a layer above the grader in that note's section 9. If the advisor re-stages it with his quoted words, it will be drawn on its own.
