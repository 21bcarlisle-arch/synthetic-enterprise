**Severity:** LATENT · **Lane:** W · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The supplier can persuade and support good candidate homes to change and to invest (2026-11-10)

**Type:** STEER, through the advisor channel. It follows tonight's two world steers: `..._A_REAL_RANGE_OF_PV_BATTERY_EV_AND_LOAD_IN_THE_WORLD_INSPIRED_BY_PREDBAT_2026-11-10.md` and `..._HOW_EACH_ASSET_IS_RUN_IS_A_SOURCED_MIX_BUILT_ON_THE_EXISTING_PHYSICS_2026-11-10.md`. The director's words, from chat on Tue 10 Nov:

- 19:56 GMT: "We also need to be able to persuade and support good candidate homes to make and invest"

The advisor reads "make" as "make changes", for example switching a battery or EV to a better operating mode, alongside investing in assets.

## The gap (the advisor's reading; check it)

`simulation/life_events.py` adopts low-carbon assets as **exogenous annual probabilities by year**: `_SOLAR_INSTALL_PROB_BY_YEAR`, `_HEAT_PUMP_INSTALL_PROB_BY_YEAR` and `_BATTERY_INSTALL_PROB_WITH_SOLAR_BY_YEAR`, gated by tenure (`adoption_eligibility_multiplier`). Nothing the supplier does changes them. `simulation/plan_offer_response.py` responds to tariff offers, but there is no world response to advice, offers or support for **changing how an asset is run or investing in one**. Knowledge pages exist (`next-best-action-and-cross-sell`, `household-flexibility-and-the-advice-roadmap`, `heat-pumps-and-fabric-measures`), but they are not reachable as a world mechanism. So today the supplier cannot create value this way in the simulation, and cannot be punished for doing it badly either.

## The outcome wanted

**World side:** a household's decision to change a setting or to invest responds to what reaches it, with real friction and real timing:
- **Friction:** upfront cost and financing, tenure (a renter needs a landlord), roof and parking suitability, trust in the messenger, and hassle in household minutes (M3).
- **Timing:** trigger moments matter, such as the boiler failing (the heat-pump moment), moving home, replacing a car, a bill shock, or a neighbour installing.
- **Responses are mixed:** most do nothing; some act; some act and regret it. Badly targeted or pushy contact can do harm. The corpus lesson applies: proactive "a better plan might suit you" messages raised churn in a telco trial.
- **Today's spontaneous adoption stays as the counterfactual,** so a household that would have invested anyway yields no created value.

**Supplier side:**
- **Find good candidates** from what a real supplier can see (the wall): half-hourly load, export, tariff, payment behaviour, what the customer tells it.
- **Advise honestly.** Show the saving with its uncertainty, in money, time and carbon, each in its own unit.
- **Support the decision.** Plausible routes include an installer partner, finance, help with grants (the Boiler Upgrade Scheme, for example) and settings help. Which routes a real supplier uses is knowledge to establish.
- **Measure the uplift causally,** against the counterfactual. Target the effect of the action, not the household's propensity.
- **Protection and fairness are a floor (M3):** no unsuitable recommendation, no pressure on the vulnerable, nothing a real supplier could not lawfully do. Ofgem's consumer standards and the installer consumer codes apply.

## Order

**Knowledge first (K8).** What moves domestic adoption and behaviour change in GB is established in published sources:
- DESNZ public attitudes tracker;
- Boiler Upgrade Scheme statistics;
- heat-pump and solar adoption studies, including peer effects;
- supplier and installer trials;
- the consumer-protection rules for advice and selling.

Grade each, and carry gaps with ranges. This comes **after** the asset range and operating modes exist, because there is nothing to change or invest in until then. Say where it lands in the 3 Nov world-additions order.

## Risk

Touches: life events, adoption, the supplier's advice and next-best-action capability, and their knowledge pages.
Blast radius: every run's adoption path, and a new way for the supplier to create or destroy value.
Probable failure modes:
- An adoption response tuned so the supplier's advice works, which is goal-seeking. The response is fitted to published evidence, decided blind to company results (the baseline/curriculum split).
- Counting adopters who would have adopted anyway as value created.

Proportionality: contract-touching — implement with the named mitigations.

— Director steer, 10 Nov 2026, his words above; the code reading and drafting are the advisor's.

## Done

(seat executor, 10 Nov ~20:50 GMT.) **Seen; moved on the executor's instruction.** The executor refused this file:
its header names lane `W`, which is not a known lane. The director's words are quoted, so it was filed rather than
shelved: third of the three asset steers in `held_behind_the_exit_test` (`docs/direction/priority_order.yaml`). It is
supplier-side, so it follows the world range it acts on: steps 9 and 11 (inference of each asset, then advice
products), held behind the correctness stretch.
