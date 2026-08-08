# [ADVISOR-SCOPE-BRIEF] — CfDs and asset-level generation: where the fleet must be modelled individually (2026-08-04)

**Type:** [SCOPE BRIEF]. Addendum to `ADVISOR_SCOPE_BRIEF_ELECTRICITY_2026-08-04.md`, which named CfDs but understated them. The director's question — *"aren't these going to transform how energy pricing works in certain periods?"* — is correct, and the mechanisms are specific.

---

## PART 1 — What CfDs actually do to prices

**The instrument.** A generator contracts with the Low Carbon Contracts Company at a fixed **strike price** for 15 years. If the market **reference price** is below strike, LCCC pays the difference, funded by a levy on electricity suppliers. If reference is above strike, **the generator pays back**, and the money returns to suppliers. Two-way.

**Reference price is not one thing.** Intermittent generators (most of the portfolio — offshore wind) settle against an **hourly day-ahead-based reference**. Baseload generators settle against a **six-month reference from traded forward contracts**. Same scheme, entirely different exposure.

### Mechanism A — the negative-price floor, and where negatives migrate

For rounds 1–3, support is lost only when the reference price is negative for **six or more consecutive hours**. **From round 4 onward, support is lost in any single negative hour.**

Consequence: round-4-and-later plant will not sell below zero in the day-ahead market, because doing so costs them their subsidy. When such plant is generating, this **effectively floors the day-ahead price at zero.**

**But the rule bites on the day-ahead reference only.** Intraday and balancing markets have no such constraint, and prices there can still go negative once day-ahead has cleared at or above zero. **Negative prices do not disappear; they migrate to a different market.**

**Implication:** a model with a single price series cannot represent this. It needs at least day-ahead distinct from within-day/balancing, and the negative-price behaviour differs between them — increasingly so as the round-4+ share of the fleet grows.

### Mechanism B — the levy is bidirectional, and 2022 proves it

Suppliers fund top-ups through the Supplier Obligation Levy. In high-price periods that flow **reverses**: between September 2022 and March 2023, CfD generators paid back approximately **£660 million**, reducing what suppliers were charged.

**Implication, and it matters commercially:** a supplier modelling only wholesale exposure **overstates its 2022 pain.** Part of the spike was rebated through a policy cost that went *negative*. Any model treating policy costs as a monotonic per-kWh adder is wrong in exactly the year that matters most, and will make the crisis look worse — and the company's survival less impressive — than reality.

### Mechanism C — the contract can stop generation

In 2022 the **baseload** reference price rose so far that biomass generators would have paid back more than they earned at the prices they actually received. **Biomass generation fell by roughly 97%.** A contract designed to support generation caused it to cease.

**Implication:** CfDs are not a passive settlement layer. They change dispatch behaviour, and a model where contracted plant always generates regardless of contract economics is missing a real and demonstrated effect.

### The structural drift

612 contracts are in the portfolio and roughly 30GW will be contracted by 2030. As the contracted share grows, **more of the fleet becomes price-insensitive while gas still sets the marginal price** — so what consumers pay drifts steadily away from what the market clears at. "Gas sets the price" remains true of the marginal unit and becomes progressively less true of the bill.

---

## PART 2 — Which assets need to be modelled individually

**The test, and it should govern every case:** *does location or contract change what the supplier experiences?* If not, aggregate.

### Wind and solar — YES, asset level. Three separate reasons:

1. **Output depends on weather where the asset is.** National output cannot be derived from average national wind; it needs capacity at locations. This is the capacity-weighting already identified as an open gap.
2. **Correlation between sites creates the tail.** A still day across the whole country is a materially different event from a still day in Scotland alone. Spatial structure is what makes cold-and-still a compound risk rather than two independent draws.
3. **CfD vintage determines negative-price behaviour.** The floor effect depends on *which* contracts are generating — round 1–3 versus round 4+ behave differently in the same hour.

**Minimum per asset:** capacity, location, technology, commissioning date, and CfD status with round and strike price.

### Thermal plant — NO. Banded is sufficient.

A gas station runs when dispatched, and where it sits is not a domestic supplier's concern. **Bands by technology and efficiency** reproduce the marginal cost correctly. Knowing which individual unit is marginal adds nothing a supplier experiences.

### Interconnectors — individually, but there are few.

Each has a distinct counterpart market and its own drivers — French nuclear availability, Norwegian hydro. Small enough to enumerate.

### Storage and demand-side response — later, aggregate for now.

Growing, and they change the shape of the tails, but not yet the dominant term.

**Data exists publicly and joins:** the renewable energy planning database gives capacity, location, technology and status per project; the CfD register gives strike price, allocation round, technology and capacity per contract.

## Disqualification battery

1. One price series, so the day-ahead floor and migrated negatives cannot both exist.
2. CfD treated as a flat per-kWh levy that cannot go negative.
3. No distinction between round 1–3 and round 4+ negative-price rules.
4. Intermittent and baseload reference prices treated identically.
5. Contracted plant always generating regardless of contract economics.
6. Wind as national average rather than assets at locations.
7. No spatial correlation between wind sites.
8. Consumer price assumed to track wholesale as the contracted share grows.
9. Thermal modelled per unit — over-modelling, the mirror error.

**Sources:** LCCC briefing on the CfD scheme (reference price definitions, IMRP, baseload six-month reference, levy mechanics); Frontier Economics and LCP analysis of the negative-price rule and its bidding consequences (AR2/AR3 six-hour rule, AR4+ single-hour rule, day-ahead floor, intraday still negative); Commons Library research briefing (biomass 97% fall linked to baseload reference prices); industry guides on the £660m clawback September 2022–March 2023; CfD portfolio scale and allocation round history.

— Advisor scope brief, written before consulting the repository, 2026-08-04.
