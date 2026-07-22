# BOARD SPECIFICATION 004 — Wholesale price formation (blind practitioner spec, VERBATIM)

**Type:** [ANCHOR — verbatim + reconciliation instruction]. Blind-drafted. **Do not edit the board's text.** Reconcile line-by-line against W1_6, the decade record, and the VALUE_CHAIN frame, per the standing steer; battery joins the oracle.

**Advisor flags (verify):** (a) §1's reconstructibility test ("power must be substantially reconstructible from gas, carbon, demand and wind on ordinary days, or it was not formed, only generated") is the sharpest single test of W1_6 — our engine is weather-led; the board says most GB hours are gas-arithmetic. This aligns with Spec 001's gas-first (F1) from a second independent direction — reconcile jointly. (b) §3's architecture requirement (fast local reversion + jumps with realistic decay + a regime layer where level/vol/correlations move JOINTLY; 2021–22 must be containable-after-onset, not perpetually many-sigma) matches the director's mean-reversion-within-regime steer — record the convergence. (c) §4 is a genuine REFINEMENT of the advisor's earlier wall-split: the board argues sentiment moves REAL prices through premium dynamics and flow-mediated channels (fear-as-injection-demand), converging onto fundamentals-dominated spot at delivery — so premium dynamics belong SIM-side, not only company-side recency. Treat this as a correction to the triangulation steer's framing and record it as a finding. (d) Battery items 3 (negative-price frequency), 11 (stochastic outages), and 12 (static regime / bimodal transition) are concrete generator audits; item 9 cross-references Spec 001 item 10 by design.

---
---

# POESYS BOARD — PRACTITIONER SPECIFICATION 004
## Wholesale price formation: why GB prices are what they are

*Issued blind under Movement 2 of Sitting 001. Distinct from Specification 001, which specified the desk that trades these prices; this specifies the machinery that makes them. The Board has not examined any price engine as built and asks nothing about it. The Executive reconciles line by line to Movement 3.*

*The Chair orchestrates. The Brain leads on fundamentals and horizons; the Worrier on regimes and 2021–22; the Visionary on the structural transition already rewriting the merit order; the Child asks why the price of electricity is really the price of gas, and answering that is §1.*

---

## 1. The fundamental machinery

**Power: the merit order, and the marginal plant.** In each settlement period, price is set by the short-run cost of the most expensive unit needed to meet demand. Zero-marginal-cost generation — wind, solar, nuclear, must-run — fills first; gas plant sets the price in the large majority of GB hours. Hence the Child's answer: **GB power is, most of the time, gas price × plant heat rate + carbon cost + a margin** — the spark-spread arithmetic — and any power price series must be reconstructible from gas and carbon on ordinary days, or it was not formed, only generated.

The interesting behaviour lives at the ends of the stack. **High wind** pushes the marginal unit down the merit order; on windy, mild, low-demand periods the marginal unit is subsidised or must-run generation and prices go to zero or **negative** — no longer exotic, occurring in a low-single-digit percentage of settlement periods in recent years. **Low wind plus high demand** climbs the stack through inefficient peakers, interconnector imports and demand response into **scarcity pricing** — a convex hockey stick where the last gigawatts cost multiples, with historic spikes in the thousands of pounds per MWh. The price–load–wind surface is therefore violently non-linear: flat-to-negative at one end, near-vertical at the other, with gas arithmetic in between.

**Two channels a veteran checks for:** the **carbon price** as a genuine input to the marginal cost (it moves the spreads and the stack ordering), and **interconnectors** coupling GB to continental prices when uncongested — which is how the 2022 French nuclear availability crisis became a GB price event without a single GB plant failing.

**Gas: a stock-and-flow balance priced at the margin of a global market.** The NBP price forms from: domestic and Norwegian pipeline supply; **LNG arrivals**, which since 2021–22 are the marginal source and price GB against Asian competition for cargoes — the global channel; interconnector flows to and from the continent; **storage stocks**, the buffer whose level is the market's anxiety gauge (GB's own storage is thin since the loss of its main seasonal facility, so European stock levels and GB's flexibility sources do the work); and demand — heating (Spec 002) plus the power sector's own gas burn, which rises exactly when wind falls. Storage creates the winter–summer spread and the intertemporal logic of the curve: low stocks going into winter steepen everything; the injection season prices against the withdrawal season.

**The joint driver, once more with feeling:** the same weather draw moves demand up, wind output down, power-sector gas burn up, and both commodity prices up, *together*. Spec 001 demanded this correlation of the trading book; Spec 002 of the weather; here is where it is manufactured. Sever it anywhere and every downstream result is decorative.

## 2. Modellable versus random, by horizon

The honest map, which any credible engine must implicitly respect:

- **Within-day and day-ahead:** substantially deterministic given the weather forecast and plant availability. Fundamentals dominate; the residual randomness is forecast error and **stochastic outages** — plants fail without warning, and a model with no unplanned outage process has removed a real driver of spikes.
- **Weeks to a few months:** weather *is* the randomness — unforecastable beyond ten to fourteen days — while storage trajectories and LNG schedules are partly visible. Price here is an expectation over the weather distribution plus a risk premium, and its variance is dominated by which weather actually arrives.
- **Seasons to years:** modellable only in scenario terms (capacity mix, demand trend, policy), and *dominated* by shocks no fundamental model contains — geopolitics, fleet crises, regulatory intervention. The practitioner's creed: **a forward price is not a forecast.** It is a traded, risk-adjusted expectation; realised spot routinely lands far from it, in both directions, and a simulation in which forwards predict spot well has confused the market with an oracle.
- **The structural horizon:** the transition is rewriting the machinery itself — more zero-marginal generation means fewer gas-set hours, more zero-and-negative periods, *and* sharper scarcity when the wind stops: the distribution is becoming bimodal, with both tails growing at the expense of the middle. A price model calibrated to yesterday's unimodal world and held static is aging in real time.

## 3. Mean reversion, and when it breaks

Spot prices mean-revert — to the cost of the marginal fuel, around storage and weather cycles — with fast half-lives: spikes collapse in days, weather anomalies wash out in weeks. So far, textbook. The veteran's correction is that **reversion is to a level that can itself jump.** The long-run mean is not a constant; it is a regime variable set by the global gas balance, and regimes shift discontinuously.

**2021–22 is the permanent exhibit.** Post-pandemic demand, a squeezed then severed Russian supply, panicked storage refill, and a French nuclear fleet partly offline moved the *level* of European gas — and therefore GB power — by five to ten times, and held it there for over a year. Any mean-reverting process calibrated to the placid 2015–2019 window declared the crisis a many-sigma impossibility, continuously, for months. That is the disqualifying signature: not that the model missed the crisis (everyone did) but that its architecture *could not contain* the crisis after it had begun.

What 2021–22 changed structurally, and a model must reflect: the marginal cargo is global (LNG netbacks price GB against Asia); the resting level and volatility both stepped up; gas–power correlation went to near unity as gas set everything; collateral and credit became price-formation factors (distressed hedging and forced unwinds moved prices); and **government intervention entered the price mechanism itself** — caps, subsidies, and market interventions are now part of the state space, not outside it.

The required architecture, stated without prescribing implementation: fast local reversion, **plus** jumps and spikes with realistic decay, **plus** a regime layer in which level, volatility, and correlations move *jointly* — because regimes are precisely the states in which everything correlates at once.

## 4. Sentiment and recency: do they move prices, or only beliefs?

The Board's answer, argued: **they move actual prices, through two real channels — and fundamentals discipline them only at delivery.**

First, forwards *are* traded beliefs. The forward curve is the market's aggregated expectation plus a risk premium, and both components respond to fear and recency: risk premia demonstrably widen after crises (forwards overpricing subsequently realised spot) and compress after long calm (the complacency that makes the next shock profitable to have hedged). A simulation whose forward premium is constant through a crisis has left the humans out of the market.

Second — the channel amateurs miss — **sentiment moves physical decisions, which move fundamentals.** The 2021 storage panic was fear expressed as injection demand: buying gas *now* against the dread of winter raised the price of gas now. Precautionary hedging, cargo diversion on expectation, plant self-scheduling against feared scarcity — belief becomes flow, and flow is fundamental.

The discipline is at the short end: as delivery approaches, storage is whatever it is, the wind blows or it does not, and spot settles on physics. So the credible structure is **sentiment-inflected forwards converging onto fundamentals-dominated spot** — a term structure of belief resolving into fact. Spot driven by mood, or forwards immune to it, are opposite failures of the same test.

## 5. The battery — what makes a simulated price formation NOT credible

1. **Power unanchored from gas and carbon.** No marginal-unit arithmetic; a power series that cannot be substantially reconstructed from gas, carbon, demand and wind on ordinary days.
2. **No hockey stick.** The price–load–wind relationship linear; no scarcity convexity into the thousands; spike magnitude, frequency and duration materially inside the observed settlement record.
3. **No negative prices**, or negative prices at token frequency against the low-single-digit percentage of recent reality.
4. **Wind uncorrelated with price** at delivery horizons — the displacement mechanism absent.
5. **Reversion to a fixed mean.** A stationary process in which a 2021–22-class level shift is architecturally impossible; the crisis permanently a many-sigma event rather than a regime.
6. **Storage absent from gas formation.** No stock-level feedback, no winter–summer spread logic, no injection-season/withdrawal-season structure.
7. **Gaussian returns.** No jumps, no fat tails, no volatility clustering; a spike that decays like ordinary noise.
8. **The severed joint driver.** Weather moving demand but not price, or prices generated independently of the demand the same supplier faces — the shared disqualifier of Specs 001, 002 and 004, listed in each deliberately.
9. **Forwards that forecast.** Forward equals expected spot; no risk premium, no term structure, no premium dynamics around stress; or a simulated desk profiting reliably against such forwards (Spec 001, item 10, arriving from the other side).
10. **Flat volatility.** No winter-versus-summer vol difference; no rise in volatility as contracts approach delivery; the far curve as noisy as the prompt.
11. **No outage process.** Plant availability deterministic; interconnector and foreign-fleet shocks (the French channel) inexpressible.
12. **A static regime.** Correlations, volatility and level frozen at one era's calibration; the structural transition — growing zeros, growing spikes, shrinking middle — invisible to the machinery.

*The Chair, closing: the veteran's summary is that a credible price engine is judged at its ends, not its middle — the zeros and the spikes, the regime breaks and the risk premia — because the middle of the distribution is where every model looks the same and nothing is being tested. Reconciliation line by line: met / partially met / absent / not applicable, with reasons, to Movement 3.*

*Signed for the Board — the Chair.*
