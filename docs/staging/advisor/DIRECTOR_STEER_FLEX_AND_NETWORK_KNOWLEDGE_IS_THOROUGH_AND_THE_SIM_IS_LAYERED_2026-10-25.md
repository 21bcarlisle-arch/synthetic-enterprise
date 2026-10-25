**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Flexibility and network knowledge is thorough; the simulation is layered, from a minimum viable core to richer options (2026-10-25)

**Type:** STEER, through the advisor channel. The director's words, from chat on Sun 25 Oct:

- 06:44 GMT: "This may be more complex than we want to build but knowledge should be thorough and then we decide where the minimum viable SIM is and have road map options for more complexity as the supplier matches the evolution of services to match the world."

## The rule

**Knowledge and build are separate.** Knowledge pages cover the world as thoroughly as the evidence allows, whatever we intend to build. Then the roadmap sets a **minimum viable simulation** and adds **layers** on top of it. Each layer is a named world capability, paired with the supplier service that matches it. The supplier's services grow as the world they live in grows.

Apply this rule to every advice and asset domain from today's packs, not only flexibility and networks.

## Recommended layers for flexibility and networks

These come from the two packs beside this file. They are the advisor's recommendation; rule them or improve them.

| Layer | World holds | Supplier can then offer |
|---|---|---|
| **L0 (minimum viable)** | Per-home devices with kW ratings and plug-in or availability patterns; half-hourly wholesale and imbalance prices. For network: cut-out amps (30/60/80/100 A), phase, a looped flag, and the ENA notify-or-apply rule engine, with delay and cost drawn from published distributions | Smart time-of-use shifting for EVs and heat pumps, valued against its own wholesale book. Install lead time and conversion loss when it sells an EV charger, heat pump, PV or battery |
| L1 | DFS and Capacity Market as event and annual streams; customer opt-in, incentive response and fatigue | Event participation and payments to customers |
| L2 | Region-specific DNO policies (first LCT on a loop, load limiters, three-phase charging, supplier-delegated fuse upgrades); G98, G99 and G100 export logic | Region-aware install offers; export-limited PV and battery designs |
| L3 | DNO flexibility zones by postcode and primary substation; products, prices and event calls; the performance multiplier. A feeder and secondary-substation layer built on ADMD, where street clustering drives remedial work | Local flexibility revenue, location-gated; targeting where the network needs it |
| L4 | Rival aggregators (VTP/VLP): the newest registration takes the meter, deviation compensation, the mutualisation levy, and P510/P511 switches | Retention of flexibility customers, and pricing against rival offers |
| L5 | Balancing Mechanism access; the 2027 standardisation (common dispatch, a single asset registry); load-control licensing | BM revenue and a licensed load-controller role |

Facts the packs establish that the world should reproduce, as population checks:

**Networks**
- Looped services: 3.9m GB, 11–17%, 6–25% by DNO. This supersedes "up to 1.5m". Under 1% had been unlooped by Jan 2025.
- About 45% of Octopus heat pump installs needed a fuse upgrade, with delays of up to 12 weeks. Unlooping takes 3–12 weeks, or 6–12 months when disputed.
- A home's after-diversity maximum demand (ADMD) is about 1.5–3 kVA with gas heating, about 6–7 kVA with a heat pump and an unmanaged EV, and about 5 kVA if the EV charges smartly.
- Since Apr 2023 reinforcement for domestic demand is mostly free. Three-phase upgrades still cost £3–7k.
- A combined heat pump and EV forces the slower apply process, not notify. That penalises the bundled offers suppliers prefer.

**Flexibility**
- Supplier shifting is worth about £250–610 per EV per year and about £84 per heat pump per year.
- VPP payments to households run about £6–25 a month.
- DNO flexibility at NGED averages about £369/MWh, which is only about £8 per registered home per year.
- Rival-aggregator supplier compensation was about £19m over Sep 2025–Feb 2026, at about £90/MWh. It is highly concentrated.

## Ask

- Publish both packs as Knowledge pages, alongside the serial queue.
- Add the layer table to the advice-roadmap order in `docs/direction/priority_order.yaml`, after the forward years. Treat L0 as part of the personalised asset world. L1 onward are options, each with a stated trigger: the evidence or capability that justifies building it.
- Do the same minimum-viable-plus-layers framing for the other advice domains (heating, EV, PV and battery, the savings grader, budget-first advice), and bring it back as a recommendation.
