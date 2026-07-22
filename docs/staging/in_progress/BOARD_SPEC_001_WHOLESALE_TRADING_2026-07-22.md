# BOARD SPECIFICATION 001 — Wholesale & trading function (blind practitioner spec, VERBATIM)

**Type:** [ANCHOR — verbatim board output + reconciliation instruction]. The board drafted this **blind** — it has not seen the build and asked nothing about it. **Do not edit, condense, or "correct" the board's text below.** It is the third anchor in the triangulation the WHOLESALE_VALUE_CHAIN steer set up:

1. **Board expectation** (this document — practitioner, blind)
2. **Advisor documentary evidence** (`ADVISOR_DISCOVERY_WHOLESALE_ANCHORS_2026-07-22.md` — sourced)
3. **Your primary-source DISCOVER** (in flight)

**Instruction:** reconcile line by line, marking each board expectation **met / partially met / absent / not applicable, with reasons**, exactly as the Chair asks — against the current build AND against the VALUE_CHAIN steer's planned scope. Where the three anchors disagree with each other, that is a finding, not a nuisance: record it. The reconciliation is a document the director will carry to the board's Movement 3 — write it to be read by practitioners, not by the harness.

**Advisor's flags for your reconciliation (candidates, verify):**
- **§1 gas-first** is the headline catch: the sim's cascade is power-led; gas exists only as a thin daily series and dual-fuel customer flags. Assess honestly what "gas as the primary energy book" changes in Epoch-2 scope and sequencing — this may be the largest single re-prioritisation in the document.
- **§3 item 6 collateral/credit and §7 item 4 collateral physics** map to the cash/working-capital layer already on the Epoch-2 horizon — this spec turns it from "layer to add" into "cause of death to model," raising its priority.
- **§7 item 3 (look-ahead) and item 5 (demand–price joint tail)** map to existing machinery (epistemic wall + R15 adversarial tests; the coupled triad proved the joint tail via the 2018 cold snap) — claim them as met only with the proof cited.
- **§7 item 10 (a profitable desk is an alarm)** is our degenerate-emergent-behaviour law arriving independently from the practitioner side — record the convergence in the reconciliation; it strengthens both.
- **§7 item 6 (churn–market correlation)** — customer records carry churn probabilities and renewal events; whether churn is *coupled to market moves* is unknown to the advisor. Determine and report honestly.
- The 12-point battery in §7 should be registered as a **standing practitioner fidelity oracle** alongside the regulatory-rules oracle — same principle: every test exists because the failure it names actually kills suppliers.

**Risk & proportionality:** the reconciliation is doc-and-analysis (reversible). Any build re-prioritisation it implies (gas, collateral) comes back through the VALUE_CHAIN steer's propose-then-proceed, not as silent scope change. Tag: **narrow/reversible for the reconciliation; findings drive proposals, not immediate builds.**

---
---

# POESYS BOARD — PRACTITIONER SPECIFICATION 001
## The wholesale and trading function of a competent mid-size GB domestic supplier

*Issued under Movement 2 of Sitting 001, at the Executive's request. Drafted blind: the Board has not examined the company's trading or pricing build and asks nothing about it. This is the specification a veteran would hand a new entrant. The Executive reconciles; the Board will read the reconciliation, not perform it.*

*The Chair orchestrates. The Brain leads on conventions and measurement; the Worrier on risk, collateral and failure; the Doer supplies the desk cadence; the Visionary marks where value genuinely lives; the Child's questions are answered where they fall. Seat attributions are inline.*

---

## 1. The products actually traded, and their conventions

**Two commodities, and gas comes first.** A GB *domestic* supplier is predominantly a gas business by energy delivered: a typical dual-fuel home burns roughly four times as many kilowatt-hours of gas as of electricity. A trading function specified power-first has misread the book.

**Gas (NBP).** Priced in pence per therm; the gas day runs 05:00–05:00. Traded granularity, near to far: within-day, day-ahead, balance-of-month, individual months, quarters, and **seasons** — Summer (April–September) and Winter (October–March). A mid-size domestic book trades OTC through brokers and on exchange (ICE), with usable liquidity out to roughly two or three seasons; beyond that, quotes exist but depth does not.

**Power (GB).** Priced in £/MWh, delivered half-hourly. The building blocks are **baseload** (all hours) and **peak** (weekday 07:00–19:00). Forward granularity mirrors gas: seasons, quarters, months, weeks/weekends, then the **day-ahead auctions** (N2EX/EPEX) and continuous within-day, and finally imbalance settlement at the single cash-out price for whatever was left uncovered. GB power liquidity is thin by continental standards; standard clips are 5–10 MW, and the far curve is a negotiation, not a screen.

**The shape residual.** A residential demand profile is not baseload plus peak; it is a half-hourly shape with a morning and a heavy evening ramp, seasonally skewed (gas overwhelmingly to winter). The convention is: build the bulk position from seasons/quarters/months in baseload and peak blocks, then buy the **residual shape** progressively closer to delivery — months, then day-ahead auction, then within-day — accepting imbalance on the last few percent. The *shape and imbalance premium* over pure baseload is a real, quantifiable cost line (the Brain: if the model prices a domestic shape at the baseload price, everything downstream is flattered).

**Adjacent obligations** that sit with or beside the desk: renewable certificates (REGOs) for green tariffs, the RO and CfD supplier obligations, capacity market charges, and transmission/distribution **loss factors** grossing up purchased volume above metered demand. These are procurement and compliance rather than trading, but the cost stack in §5 is wrong without them.

---

## 2. Hedge policy by tariff type

The two books are hedged on entirely different logic, and conflating them is a classic new-entrant error.

**The fixed-tariff book: back-to-back at acquisition.** The moment a customer signs a 12-month fix, the margin is locked only if the expected volume is bought along the curve **immediately** — weather-normalised, profiled to the customer's shape, netted for expected attrition. In practice acquisition flow is hedged in daily or weekly sweeps rather than per-customer. Thereafter the desk manages *residuals*: churn (customers leaving early when the market falls below their fix, leaving the book long into a falling market), volume forecast error, and weather. The Worrier's standing note: the fixed book's poison is **correlation** — a cold snap raises demand exactly when prices spike, so the book goes short precisely when covering is most expensive. Policy must hold a tolerance band (commonly ±5% of forecast volume per month per fuel) and a documented rule for restoring it.

**The variable/default (SVT) book: replicate the cap.** Since the default tariff cap, the wholesale allowance in the SVT price is a defined average of forward prices over Ofgem's **observation window** for each (quarterly) cap period. The rational hedge is therefore mechanical: buy the expected SVT volume in tranches that mirror the cap's own indexation, so that achieved cost tracks the allowance by construction. Any deviation from that ladder is a *speculative position against the regulator's index* and must be sized, authorised and stop-lossed as such. The Child asks: *why buy before we know how cold it will be?* Answer: because the price we are allowed to charge was set by the same window; matching it converts price risk into the far smaller volume risk.

**The ladder, generically.** Written policy should state, per book: target hedge ratio by horizon (e.g. fixed book 100% at acquisition; SVT book ratably across the observation window, reaching ~100% of forecast as the window closes), tolerance bands, delegated dealing authority by tenor and size, stop-loss and escalation triggers, and a prohibition on naked short positions in delivery months. The Doer: the ladder is only real if the desk can show, any given morning, actual hedge ratio versus the policy line per month, and explain every excursion.

---

## 3. The weekly desk pack

The head of trading's Monday pack, in order (the Doer's specification — every item is a chart or a table, not a paragraph):

1. **Position versus policy**: hedge ratio by delivery month and fuel, plotted against the policy ladder and tolerance band; net open volume in GWh and therms per period.
2. **Cost versus market and versus allowance**: weighted-average cost of energy per period versus the current curve (mark-to-market of the book) and, for the SVT book, versus the accruing cap wholesale allowance for the live and next cap periods. This last line *is* the gross margin of the default book.
3. **Demand**: latest weather-normalised forecast versus prior week; actuals versus forecast with error statistics; customer numbers, churn and acquisition versus plan; movements in estimated annual consumptions.
4. **Risk**: VaR or equivalent on the open position; named stress scenarios re-run weekly (a 2021-style sustained rally; a 1-in-20 cold winter; a demand-price joint stress) with the cash and P&L consequence of each.
5. **Imbalance and shape**: imbalance volume as a percentage of demand and imbalance cost per MWh versus the day-ahead reference; shape cost achieved versus assumption.
6. **Collateral and credit** (the Worrier insists this sits *in* the trading pack, not in a finance annex): margin posted with exchanges and counterparties, Elexon credit cover, headroom against facilities, and the projected collateral call under ±30% price moves. Suppliers in 2021–22 died of collateral before they died of P&L.
7. **Market backdrop**: week-on-week curve moves, gas storage and LNG, volatility — one page, context not commentary.

---

## 4. Where trading creates or destroys value, and how to measure it

The Visionary's discipline, endorsed by the whole table: **a domestic supplier's desk is a risk-management cost centre, not a profit centre.** A retail desk that reliably "beats the market" is either taking unauthorised risk or benefiting from an information leak; either finding should alarm, not please.

Value is genuinely created in four places, each measurable against a mechanical benchmark:

- **Execution versus the ladder**: achieved price versus the price the pure mechanical policy would have achieved. Discretion must prove itself against the robot, in pence per therm and £/MWh, cumulatively.
- **Forecast accuracy**: demand forecast error × price at the time of correction = a real cost. Track MAPE by horizon; attribute the cash cost of misforecast.
- **Shape and imbalance management**: cost of the residual versus a naive buy-everything-day-ahead counterfactual.
- **Avoiding distressed trades**: never forced to buy in a spike because tolerance was breached or collateral ran out. Measured in the negative — count of forced trades, ideally zero.

Value is destroyed by the mirror images: under-hedging into a rally, churn misestimated on the fixed book, shape bought late, imbalance drift, collateral crunches forcing unwinds. A proper **P&L attribution** splits the wholesale result into price, volume, shape, timing and imbalance components each month; if the attribution cannot be produced, the desk does not know where its result came from.

---

## 5. Benchmarks, ratios, and constructing the annual cost of a residential shape

The core artefact is the **annual cost stack for one typical dual-fuel customer** (around 2,700 kWh electricity and 11,500 kWh gas on current typical-consumption values), built as:

1. Take the half-hourly demand shape for the customer class, weather-normalised.
2. Weight the forward curve by that shape: baseload cost plus the **peak/shape premium** (power) and the winter-weighted seasonal cost (gas).
3. Gross up for **losses** (transmission and distribution loss factors; unidentified gas on the gas side).
4. Add a **shaping/imbalance allowance** for the residual bought near delivery.
5. Add the supplier obligations that ride on wholesale volume — RO, CfD, capacity market.
6. The result, per customer per year, is the wholesale line that sits above networks, policy, operating cost and margin in the retail stack.

This construction is essentially the cap methodology's own, which is why the ratios watched are: achieved cost versus cap allowance (the margin driver); shape premium as a percentage of baseload (single digits when sane; if the model's is near zero, it is broken); winter/summer spreads; forward premium over realised spot across a cycle (the practitioner range is mid-single-digit to low-double-digit percent); imbalance cost per MWh versus day-ahead; and forecast error by horizon. External sanity checks against published cap allowances and independent benchmarkers should be routine.

---

## 6. How the wholesale stack should drive retail prices

**Fixed tariffs** are priced cost-plus at the point of quote: the shaped, lossed forward cost for the tenor, plus non-commodity costs, plus operating cost, plus **explicit risk premia** — volume risk, weather, shape, the customer's free option to churn (they leave if the market falls; they stay if it rises — that asymmetry has a price), and credit — plus margin. The pricing engine must consume a **live curve**: a quoted fix left standing while the market moves is a free option written to the public, and stale quote books have sunk entrants. Re-price at least daily in volatile markets.

**SVT** is cap-constrained; the commercial question is not the retail price (the cap sets its ceiling and competition sets little else) but whether the hedge tracks the allowance (§2).

**Governance**: trading supplies the cost stack; a pricing committee sets margin and approves tariffs; and the cost stack is never adjusted to reach a desired retail price. The Brain, flatly: cost flows forward into price; price never flows backward into cost. A model in which margin is a target rather than an output has already failed.

---

## 7. What would make a veteran say the simulated function is NOT credible

The Worrier and the Brain jointly, as a test battery. Any one of these is disqualifying until explained:

1. **Gas missing or subordinate.** A GB domestic supplier model that is essentially a power model is not a GB domestic supplier model.
2. **No shape residual.** "Electricity" bought as a single undifferentiated product — no baseload/peak distinction, no near-delivery shaping, no imbalance leftover — flatters every cost downstream.
3. **Any look-ahead in hedging inputs.** Hedge ratios, volatility estimates or demand forecasts that respond to information from after the decision time. The single most common and most fatal simulation defect; test for it adversarially, not by inspection.
4. **No collateral physics.** If wholesale prices can triple without margin calls, credit-cover top-ups and a cash consequence, the model cannot reproduce how suppliers actually die. 2021–22 was a liquidity event wearing a price event's clothes.
5. **Demand and price independent.** Cold weather must raise consumption and market price *together*. If the joint tail is missing, every survival result is unearned.
6. **Churn uncorrelated with market moves.** Fixed customers must leave when the market falls below their deal; the SVT book must swell when the market spikes and rivals withdraw. A book whose size ignores prices is not a book.
7. **Benign imbalance, always.** Cash-out that never spikes, settlement that never hurts, is a fiction.
8. **Cap mechanics absent or hand-waved.** No observation windows, no quarterly resets, no achieved-cost-versus-allowance tension: then the SVT book's economics — most of a mid-size supplier's margin volatility — are unmodelled.
9. **Infinite liquidity.** Any volume, any tenor, executed at mid with no bid-offer, no clip size, no depth limit. Real desks pay to trade and cannot always trade.
10. **A profitable desk.** Consistent trading profit on a domestic book is the smell of leakage or unpriced risk, not skill (§4).
11. **No losses, no unidentified gas, no consumption-estimate error.** The gap between metered, settled and billed volume is where real suppliers bleed quietly; a model without it is too clean.
12. **Everything at exactly 100% hedged, always.** Real books breathe inside tolerance bands. Perfection is a tell.

The Chair, closing: the honest headline of this specification is that competence here looks *boring* — mechanical ladders, cap replication, attribution tables, collateral headroom — and the excitement a simulation should exhibit lives entirely in its risk correlations, not its trading brilliance. The Executive is asked to reconcile against this document line by line, marking each expectation **met / partially met / absent / not applicable, with reasons**, and to bring the reconciliation to Movement 3.

*Signed for the Board — the Chair.*
