**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The advice roadmap needs its knowledge first: heating, EVs, solar and batteries, proof of savings, flexibility (2026-10-25)

**Type:** STEER, through the advisor channel. These are the director's words from chat on Sun 25 Oct:

- 05:37 GMT: "Also should we do more research on key future topics? How do gas boilers work and how do choices in the sim appear and gas usage and choices for customer and advice that the supplier can offer?"
- the same message, continuing: "Then the actual charging and usage patterns that occur, based on logic that the SIM knows about the premise and person but the supplier has to figure out or ask about."
- and: "Then proving if it did or didn't. Sharing the savings clearly for the customer to enjoy. All these subjects are quite complicated and need knowledge. There may be others too we need for our roadmap??"

The advisor ran six research passes outside your gate. They land beside this file as `DIRECTOR_EVIDENCE_*_2026-10-25.md`:
- gas boilers and heating controls;
- EVs, charging and savings against petrol and diesel;
- solar PV and home batteries;
- heat pumps and fabric measures;
- proving and showing household savings;
- household flexibility and the advice roadmap.

Each pack has the same three views as Explore: what the world must hold as hidden truth, what the supplier can observe, infer or must ask, and what the advice saves and how it is proven.

## The steer

**This does not reorder the basics or the forward years.** The ruled order stands: payment, dual fuel and switching first, then the forward years. What follows is the order after that, plus four things to do now because they are defects in today's world.

### Now: these are defects, not roadmap

1. **Gas typical consumption.** Ofgem's medium gas TDCV fell from 11,500 to **9,500 kWh** on 1 Jul 2026 (boilers pack, section 0; heat pumps pack, section 3). Find every constant, claim and page that says 11,500. Each one is either historically dated, which is fine for 2016–25, or wrong. Date them.
2. **EV uplift.** The EV home in Explore shows +8%. The published band is 1,750–3,500 kWh a year at home, which is +65–120% on a typical home (EV pack, table a). Make it a world claim and fix the generator. This was also staged in the site copy pack.
3. **Economy 7.** There are no two-rate meters in the run. Restricted meters are 14–17% of electricity accounts (tariffs pack). The roadmap scan ranks storage heating as a P1 advice topic. This was also staged in the site copy pack.
4. **Dated rules in forward years.** Ofgem states that VAT on domestic electricity is 0% from 1 Oct 2026 to 31 Mar 2027. Two independent research passes read this from Ofgem's own cap page. Verify it against Ofgem directly before any constant uses it. Also: the 0% VAT on solar and batteries ends 31 Mar 2027; SSES load-control licensing applies from **March 2028**; and eVED at 3p a mile starts in April 2028. Anything the forward years model past those dates must carry the rule change.

### After the forward years: the order of the advice roadmap

This is the advisor's recommendation. Rule it, or put a better order with reasons.

1. **The household asset world.** No advice exists until the world holds the truth it is about. Use the "world needs to model" lists in the four asset packs as the spec:
   - **Boiler:** type and age, condensing in practice (return temperature), flow temperature, controls actually used, setpoint and schedule, emitter oversizing, cylinder or combi.
   - **EV:** person's mileage, plug-in habit, parking, public share.
   - **PV:** kWp, azimuth and tilt, age, export registration.
   - **Battery:** size, mode and reserve.
   - **Heat pump:** sizing and flow temperature.
   - **Fabric:** state of each element.

   Each comes with its world claims (combi share 62%, mean setpoint 20°C falling to about 19°C, BEV home charging bands, self-consumption 28–57%, measured heat pump SPF median about 2.8, NEED insulation savings, and so on).
2. **The supplier's inference across the wall, graded.** For each asset, use the observe / infer / ask table: detect it from half-hourly data, ask what cannot be inferred, and grade the inference against the truth. Published accuracies are the bar. For EV detection with a year of half-hourly data, precision is about 0.87 and recall about 0.81. SMETER heat-loss estimates have a CV(RMSE) of 13–39%. Treat it as wall work: the inference reads only what crosses.
3. **The savings grader.** Only a simulation can measure what a supplier's savings estimate gets wrong, because it holds the true counterfactual. The proof pack proposes eight tests: estimator bias and interval coverage, an empirical minimum-detectable-saving curve, the deemed-to-true ratio, confounder stress tests, rebound and persistence, flexibility baseline gaming, an audit of every "you saved £X" claim, and value-share fairness by segment. It is cheap once step 1 exists, and it is the project's most distinctive result. It should come before any savings are shown to a customer.
4. **Advice products, in the roadmap scan's priority order:**
   - tariff choice (P1, the cheapest saving to prove);
   - data consent (P1, it gates personalisation);
   - Economy 7 and storage heating (P1);
   - prepayment and vulnerability safeguards (P1);
   - grants (P1; ECO ends, and the Boiler Upgrade Scheme gives £7,500);
   - then EV smart charging (about £350–510 a year against a flat tariff), PV and battery optimisation (on a flat tariff a battery adds only about £150–180 a year, so its value is in tariff arbitrage), heat pumps (break-even on the cap at SPF about 2.8; the value is in a heat-pump tariff and dropping the gas standing charge), and fabric (measured paybacks are long).

   Boiler setting advice is cheap but its proven savings are small: flow temperature saves 9% in a test house but only 1.4%, not significant, in a trial. That is where the grader earns its place.
5. **Flexibility value last.** DFS has fallen from about £3,300 to about £240 per MWh, and from about £4.58 to about £0.48 per registered meter per winter. Most of the value is wholesale shaping under half-hourly settlement. Since P415, a rival aggregator can capture a customer's flexibility, so the world needs that agent. SSES licensing applies from March 2028.

### Showing savings to the customer

The proof pack's ten design rules are binding on anything a customer sees. They come from the ASA rulings against British Gas ("up to £546", achieved by only 34% of customers) and Octopus (basis not shown), and from SLC 0 and the CMA Green Claims Code. In short:
- label each figure as estimated or measured;
- show the baseline in the message itself;
- give a range below the detectable saving;
- normalise for weather;
- use "up to" only where most customers achieve it;
- report flexibility savings net of the load that moved;
- carry decay on cumulative savings.

This is the director's "sharing the savings clearly for the customer to enjoy", done so that a regulator would accept it.

## What I need from you

- Publish the six packs as Knowledge pages under the map steer, as drafting work alongside the serial queue.
- Fix the four "now" items, or record why not.
- Put the advice-roadmap order in `docs/direction/priority_order.yaml` after the forward years, with your view. Bring back a recommendation where you would order it differently.
