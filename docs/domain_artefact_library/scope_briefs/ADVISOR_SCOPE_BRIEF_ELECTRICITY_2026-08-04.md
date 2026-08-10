# [ADVISOR-SCOPE-BRIEF] — GB wholesale ELECTRICITY: what a complete treatment must contain (2026-08-04)

**Type:** [SCOPE BRIEF]. Written **from the domain, before looking at what we hold** — per the scope-first ruling, which exists because assembling from existing material can only reproduce existing material.

**How to use it:** this is the specification, not the page. Assemble against it; **the delta between this brief and what we can fill is the primary finding** and is worth more than the page. Where the brief is wrong or incomplete, say so with evidence — it was written from outside the code by someone who cannot see it.

**Separate from gas** per the director's ruling: different products, different mechanisms, different drivers. Gas *drives* power; that is an edge, not a merger.

---

## A. What the market is for

Electricity cannot be stored at scale, so supply and demand must match continuously. Everything downstream is a consequence: why trading happens at many horizons, why a price exists for every half hour, why being wrong costs money at the moment of delivery rather than at the end of the month.

A complete treatment answers: **why does a market exist here at all, and what would happen without one?**

## B. Products and structure — the traded ladder

The single most-missed area, and the director's stated priority: *possibly the most important thing we use.*

**Time-of-day shapes.** Baseload covers every period, 23:00–23:00. Peak covers 07:00–19:00 on weekdays. The **EFA day** divides into six four-hour blocks starting at 23:00; baseload is blocks 1–6, peak is blocks 3–5 on weekdays, off-peak is blocks 1, 2 and 6 on weekdays plus all weekend, overnight is blocks 1–2. Blocks can be halved (1a, 1b…).

**Horizons, longest to shortest.** Futures and forwards years ahead — standardised futures on ICE (UK baseload and UK peak), bilateral forwards negotiated directly, often brokered. Then **seasons** (Winter = October–March, Summer = April–September), **quarters**, **months**, **weeks**, **days**. Then **day-ahead**: two exchanges, N2EX and EPEX, running morning auctions that clear pay-as-clear — one price for all accepted participants — which is the market usually treated as the reference price. Then **within-day**: continuous trading, 48 half-hourly contracts (most liquid), 24 hourly, and six EFA blocks. Finally **imbalance/cash-out**, settled by Elexon at a single imbalance price per half hour, **not known until after the period has ended.**

**Liquidity is not uniform, and this matters commercially.** Most trading sits in the front three or four seasons; availability thins along the curve. Seasonal baseload trades furthest out; monthly baseload concentrates within about three months of delivery; peak products and individual blocks are materially less available. **A model that assumes any product is tradeable at any horizon is wrong**, and a hedging strategy that ignores it is untestable.

A complete treatment answers: **what can actually be bought, when, in what size, and at what cost of crossing the spread?**

## C. Mechanism — how the price is formed

**Merit order.** Plant is dispatched cheapest first; the price is set by the most expensive unit needed to meet demand. That unit's short-run marginal cost is roughly **fuel divided by efficiency, plus carbon cost** — which is why gas and carbon prices propagate into power.

**Zero-marginal-cost renewables displace, they do not price.** Wind and solar enter at the bottom of the stack and push the marginal unit *down* it. High wind therefore lowers price by changing *which* plant is marginal, not by bidding low.

**Gas is usually marginal in GB**, so for most hours the power price is close to gas-over-efficiency plus carbon. **This is the reconstructibility test:** on ordinary days, power should be substantially reconstructible from gas, carbon, demand and wind — if it is not, the price was generated rather than formed.

**Scarcity and the tail.** When the stack is tight the price departs from marginal cost entirely and reflects scarcity — a different regime, not an extreme draw from the same one.

**Negative prices.** When inflexible must-run output plus renewables exceeds demand, price goes below zero and generators pay to run. Frequency and depth have grown with renewable penetration. **A model that cannot produce negative prices is missing a real and increasingly common state.**

A complete treatment answers: **what sets the price in an ordinary hour, a tight hour, and a glutted hour — and are they the same mechanism?**

## D. Drivers, and where they come from

- **Gas price** — NBP, closely tracking the Dutch TTF benchmark; a European position, not a domestic one.
- **Carbon** — UK ETS, adding directly to fossil marginal cost.
- **Demand** — temperature, time of day, day of week, holidays, economic activity.
- **Wind** — output at turbine locations, not average national wind. **Capacity-weighted.**
- **Solar** — output at solar sites; note aggregate solar is estimated rather than metered centrally.
- **Interconnectors** — France, Norway, Netherlands, Belgium, Ireland. **French nuclear availability and Norwegian hydro are first-order GB price drivers.**
- **Plant availability and outages** — largely unforecastable timing.

A complete treatment answers: **which of these are observable in advance, which only after the fact, and which are irreducibly random?**

## E. Structure over time

Seasonality (winter above summer, driven by heat demand and short days). Intra-day shape with morning and evening peaks. Weekday against weekend. And **regimes** — the market before 2021, the crisis, and after — where the *level, the volatility and the correlations between drivers all move together.* Mean reversion holds within a regime and breaks across regimes.

A complete treatment answers: **what is the characteristic shape of a year, a week and a day — and what changed in 2021 that was not simply a bigger version of before?**

## F. The layers around the wholesale market

Not the wholesale market, but they change what is bought and what consumers pay:

- **Capacity Market** — pays for *availability*, not energy; T-4 and T-1 auctions; a revenue floor that underwrites new build.
- **CfDs** — renewables paid a strike price against a market reference; the difference flows through consumer bills, and the reference itself is a volume-weighted day-ahead average.
- **REGOs** and **PPAs** — long-term bilateral contracts, pay-as-produced or baseload-shaped.

A complete treatment answers: **what does a consumer actually pay for, beyond the commodity?**

## G. Modellable versus random

Explicitly per horizon: fundamentals that should be *caused* by the model (weather-to-demand, merit order, seasonality, capacity evolution) versus residual that should be *drawn* with honest tails and regime structure (outage timing, geopolitics, sentiment). **Never pretend to forecast the unforecastable, and never generate as noise what should have been caused.**

## H. Disqualification battery — what makes a treatment incomplete

1. No product ladder: shapes, horizons and liquidity absent.
2. Prices treated as a single series with no distinction between forward, day-ahead, within-day and imbalance.
3. Renewables modelled as lowering the price directly rather than by displacing the marginal unit.
4. No negative prices.
5. Scarcity treated as a large draw from the ordinary distribution rather than a different regime.
6. Wind modelled as national average rather than weighted to turbine locations.
7. Interconnectors and French nuclear absent.
8. Carbon missing from marginal cost.
9. No account of liquidity — everything tradeable at any horizon, no spread cost.
10. One regime for the whole decade.
11. Imbalance price treated as knowable before delivery.
12. Gas treated as a correlated series rather than the thing that sets the marginal cost.

**Sources:** GB market structure and EFA block definitions (Modo, Gridcog, Aneesh Mistry); Platts European Electricity specifications for contract definitions and season boundaries; CMA energy market investigation appendix on liquidity along the curve; Elexon/HEFTcom on single imbalance pricing and day-ahead reference; industry commentary on NBP–TTF linkage and interconnector drivers.

— Advisor scope brief, written before consulting the repository, 2026-08-04.
