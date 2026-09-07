**Severity:** RECORDED · **Lane:** A_strategy_governance (the director's own words: "product (what the world is for) + W1/W2 fidelity register" -- `product` is not one of the thirteen lanes `background/finding_severity.LANES` knows, and an unparseable lane refuses EVERY lane's merge of origin/main, so the field carries the nearest real lane and his phrasing is kept verbatim beside it) · **Priority:** P1 for registration; fidelity gaps folded into the existing phases; two small discovery pulls authorised · **Proportionality:** reversible / narrow

**Knowledge:** none -- no topic declared at filing; the seat that acts on this document names the page its understanding reaches, or says why none

# [DIRECTOR-RULING][ADVISOR-STAGED] Supplier-side use-case register, and the SIM fidelity each one needs (2026-09-06)

**Decided by the director in the advisor channel, 5–6 September 2026.** This is a **product document, not a build order**: it says what the world being built is *for*, so the machine can judge fidelity work by the use it enables, and so the site's Capabilities register has something true to say. Nothing here authorises a company-side build. The **second half** registers the SIM-side fidelity each use case depends on — the director's instruction verbatim: *"we need the SIM to have sufficient fidelity on the other side to enable these."*

Companion documents: the three phase-1 rulings and their amendment (5 September), and `ADVISOR_REFERENCE_CLV_DRIVERS_THESIS_AND_SENSE_CHECK_2026-09-05.md`.

## 0. The principle that makes these SIM-native

**The SIM gives a per-household counterfactual.** For every house it knows what would have happened without the intervention. So any product built on attribution — "we saved you this much", "this customer is worth that", "this debt will go this way" — can be scored against hidden truth before it meets a real customer. Real suppliers argue about baselines; this company can prove its baseline method first. Every use case below carries its **SIM-native test**: the hidden truth it is scored against.

Every use case must also be workable **inside the epistemic wall**: nothing below needs data a real supplier could not lawfully obtain.

## 1. The register, grouped by the merit-order gate each serves

### Gate 1 — pays

**1.1 Premise-level debt and cash-flow modelling.** Bottom-up provisioning per premise; payment-allocation rules made explicit (payments clearing current consumption while arrears persist, or oldest-first); a per-premise arrears trajectory, so "beating the forecast" is measurable management. *Value:* the largest per-customer swing in the thesis (−£800 badly managed, ~break-even well managed). *Test:* trajectory accuracy against truth; can't-pay/won't-pay diagnosis speed and accuracy; plan uptake; PAYG conversion outcomes; vulnerability handling. *Rules:* Ofgem debt and disconnection rules; vulnerability flags gate PAYG.
**1.2 Self-rationing detection.** Usage falling below what the house's physics says it needs in cold weather is a household going cold. *Value:* a regulatory duty done well; avoided harm; retention of the vulnerable. *Test:* detection rate and false-alarm rate against truth — the false alarm that matters is "empty house" versus "cold occupant".
**1.3 PAYG done right.** Smart-enabled conversion for won't-pay-but-can, with vulnerability screening and friendly-credit design. *Test:* bad-debt loss by meter type holding payment method and stress constant; the vulnerability-flag rate that gates it.

### Gate 2 — stays

**2.1 Budget billing and physics forecasting.** Premise-physics forecasts instead of profile averages; a direct debit right from month one; **budget mode** — the customer names a bill and is shown the levers that hit it (thermostat, flow temperature, off-peak, timing), with weather warnings ahead of cold snaps priced in pounds. Usage is not taken as a given. *Value:* serves every customer; the loyalty hypothesis's cleanest test. *Test:* forecast accuracy by house type against truth; bill-shock rate; arrears onset; churn response to accurate, controllable bills.
**2.2 Presence matching.** Don't heat empty houses: basic version inferred from meter signatures (base-load-only, no evening peak, weekday regularity, holiday gaps) driving automatic setback; smarter version with location, **opt-in only**. *Test:* presence detection accuracy and false alarms against truth; never set back on inference alone for anyone who may be vulnerable (links to 1.2).
**2.3 The property as the customer.** A property passport of the home's energy physics that outlives occupants; pre-populated quotes for a property before anyone applies; move-in onboarding at the meter point; deemed contracts converted well; final bills collected. *Value:* the renter economics — margin per meter point across occupier changes. *Test:* onboarding cost, first-month DD accuracy, final-bill collection, retention of the meter point.
**2.4 Honest peer benchmarking.** "Similar homes" normalised by physics rather than neighbourhood. *Test:* nudge lift by segment against the counterfactual (the machine already measures this).
**2.5 Gamification of money, carbon, load-shift and efficiency.** Streaks, targets and budgets on all four; offered to the engaged, withheld from the apathetic; not regressive — the free-and-easy rungs must score as richly as the capex ones. *Test:* behaviour change versus reporting change, by segment, against the counterfactual; rebound.

### Gate 3 — the margin bet

**3.1 Hedging by physics.** Portfolio hedge shape derived from per-premise gradients and weather cells, not industry profiles. Internal, and possibly the largest single value item. *Test:* forecast/volume risk and hedge-shape error on the cold-winter practice book; the crisis-year tail.
**3.2 Partial-risk tariffs.** Between fully fixed and fully variable: fixed for a share of expected volume; caps and floors; a weather-indexed element; a hedge ladder chosen by stated risk appetite. *Value:* stability sold to those who value it, priced honestly. *Test:* the promise's cost in a cold year against the weather distribution and the house's gradient; customer comprehension. *Rules:* cap compliance for default tariffs; fairness and clarity duties.
**3.3 Algorithmic hedging and asset arbitrage, inside an envelope.** Optimisation of hedge timing and shape, and battery/EV arbitrage with permission, **within a director-set risk envelope — never a speculative position on the book.** *Test:* value captured versus the envelope; the 2021-style tail must be survivable by construction.
**3.4 Cost to serve as the product.** Running at a fraction of the cap's overhead allowance captures near-full contribution per account (the market reconciliation: ~£110/account standalone, ~£340/account contribution). *Test:* per-account cost measured honestly in the SIM against £100–140 standalone and £150–200 market-clearing.

### Gate 4 — value-add

**4.1 Tailored business cases and advice.** PV, battery, EV, insulation, flow temperature, timing — from the property model plus actuals. *Test:* did the promised saving materialise; how much adoption was the advice versus the household's own drift.
**4.2 Shared-savings contracts.** "We take a share of what we save you, measured against your own physics baseline." The mission's value-sharing as a product; credible only once the baseline method is proven against hidden truth. *Test:* baseline error distribution; two-sided value created-then-shared.
**4.3 Fabric and system diagnostics from the meter.** A change in the house's gradient against degree-days is a boiler degrading, an insulation failure, a thermostat war. *Test:* detection against the house-change timeline.
**4.4 Flexibility with permission.** EV, battery, heat-pump control and DSR revenue sharing. *Test:* shape value captured per asset class; consent rates by attitude; PV-only remains negative unless paired.
**4.5 Bill explanation and disaggregation by asset class.** Heating, hot water, EV, appliances — fintech-style. *Test:* disaggregation accuracy against per-asset truth.
**4.6 The carbon product.** Per-household carbon with real half-hourly intensity; a carbon budget beside the money one; green-hour shifting. *Test:* carbon saved against the counterfactual; shift achieved.
**4.7 Value at the funnel and at the quote.** A value model learned from observables only (postcode → cell, stock and socio-demographics; address → dwelling type; quote inputs → payment method, meter type, consumption estimate), scored against true CLV; **bid by expected value**; and **the question ladder** — the value of information of each question, so "free advice for three answers" is a designed exchange ordered by how much each answer sharpens the estimate (first questions: paying and staying, not roofs). *Rules:* value-based *acquisition spend* and *service design*, not value-based pricing at quote.

### Priority within the register (director's ranking, from the merit order and what exists)
1.1 and 2.1 first (serve everyone; arrears engine, DD physics, bill-shock mechanics exist); 3.1 and 2.3 next (large; weather and moves now commissioned); 4.7 once the three phase-1 samples exist; 4.1–4.6 and 3.2–3.3 as the house timeline and the people phases land.

## 2. The SIM fidelity each use case needs — provided, or a gap

| Use case | SIM-side truth and responses required | Provided by | Gap? |
|---|---|---|---|
| 1.1 Debt modelling | can't/won't-pay truth; collections responses; **payment-allocation rules in the arrears engine**; vulnerability flags and disclosure | People P1 (amended); arrears engine | **Allocation rules** not yet explicit — add to People P1 |
| 1.2 Self-rationing | **going-cold behaviour**: households under-heating relative to physics under stress, by vulnerability | — | **Gap** — add to People P1 (pays gate) |
| 1.3 PAYG | smart flag per house; conversion responses; friendly-credit behaviour | Housing P1; People P1 (amended) | none beyond above |
| 2.1 Budget billing | per-house gradient and shape truth; weather persistence; **bill-shock → churn and arrears responses**; lever responses (thermostat, flow temp, timing) | Weather P1; Housing P1; existing mechanics; Housing P1 current-settings | **Lever responses** (does a household act on a budget prompt?) — People P2 |
| 2.2 Presence matching | **half-hourly presence truth** (working hours, holidays, shifts); consent to location | People P2 | Timing: needed earlier than P2 if 2.2 is pursued early |
| 2.3 Property passport | **move events, deemed contracts, final bills**; property physics independent of occupant | Amendment (moves into People P1); Housing P1 | none beyond the amendment |
| 2.4 Benchmarking | physics-normalised similar-homes truth; nudge lift by segment | Housing P1; existing nudge discovery | none |
| 2.5 Gamification | **nudge and game responses incl. rebound**, by engagement archetype | partial (framing lift) | **Gap** — People P2 |
| 3.1 Hedging by physics | cell weather with synchrony; gradient distribution; **hedge cost model and forward curves** | Weather P1; Housing P1; held batch (forward-curve backtesting) | **Forward curves / hedge cost** — small discovery pull, authorised below |
| 3.2 Partial-risk tariffs | weather distribution (generator), house gradient, **stability preference** | Epoch-4 generator; Weather/Housing P1; People P2 | preference is P2; generator is epoch 4 — 3.2 waits |
| 3.3 Algo hedging | as 3.1 + **director risk envelope** (curriculum value) | — | **Director value** — reserved |
| 3.4 Cost to serve | contact propensity and channel; per-account cost accounting | People P2; company ledger | P2 timing |
| 4.1 / 4.2 Business cases, shared savings | ceilings; **unprompted drift (house timeline)**; uptake responses | Housing P1; Housing P3; People P3 | P3 timing — 4.1/4.2 wait |
| 4.3 Diagnostics | **house-change timeline** (boiler degradation, insulation failure) | Housing P3 | P3 timing |
| 4.4 Flex with permission | assets; **consent to control** | Housing P1; People P2 | P2 timing |
| 4.5 Disaggregation | **per-asset consumption truth** (heating, hot water, EV, appliances, PV) in the usage model | — | **Gap** — Housing P1 + People P1 usage outputs must be per-asset, not totals |
| 4.6 Carbon | **half-hourly grid carbon intensity, historical** aligned to the settlement data | — | **Data pull** — authorised below |
| 4.7 Funnel and quote | **a prospect pool** (drawn houses not yet customers) with channel and quote behaviour; value-of-information machinery | — | **Gap** — People P2 (channel behaviour); the pool is a sampling instruction for the run draw |

## 3. Decisions (director-decided; transmit as decisions)

1. **Fold the gaps into the phases named** — payment-allocation rules and going-cold behaviour into People P1; per-asset consumption truth into the Housing P1 and People P1 usage outputs (a decomposition, not a new model); lever, nudge and game responses, consent to control, channel behaviour into People P2; nothing pulled from P3.
2. **Two small discovery pulls are authorised now** (reversible, cheap, wall-clean): historical half-hourly grid carbon intensity aligned to the existing settlement data (for 4.6 and the mission's carbon accounting); a published forward-curve or hedge-cost series sufficient to backtest 3.1 (the held-batch item). Register both as data assets with provenance; no product build.
3. **Reserved for the director:** the hedging risk envelope (3.3); which use cases the company is *allowed* to pursue per epoch — this register describes, it does not permit.
4. **The register is product.** Publish it to the site's Capabilities register in the external register (no atom names, no phase labels) as "what a supplier can do with this world", each item carrying its SIM-native test and its current status: *testable now / waits on [plain-English condition]*.

## 4. Risk

Touches: registers and the site; the scope lines of People P1/P2 and Housing P1; two data pulls. Blast radius: nil on published figures; usage outputs gain a per-asset decomposition that must sum to the existing totals (a control). Failure modes: (a) a use case built company-side on this document's authority — forbidden, it describes; (b) per-asset decomposition invented rather than anchored (EFUS end-use splits and published disaggregation studies exist — anchor or declare); (c) carbon intensity pulled at a resolution that does not align with the settlement periods — align or state the mismatch.

## 5. WORK THIS CREATES

- The use-case register published to Capabilities, external register, with status per item.
- Scope additions to People P1 (allocation rules; going-cold), Housing/People P1 (per-asset usage decomposition with a sum-to-total control), People P2 (lever/nudge/game responses; consent to control; channel behaviour).
- Two data assets: half-hourly carbon intensity; forward-curve/hedge-cost series.
- One plain-English report to the director: the register as published, the gaps folded, the two pulls landed, and the envelope decision awaiting him.
