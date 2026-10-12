# Theme: fairness-and-pricing (14 entries)

### [R-A-82] "I really want pricing to be right in the end, not just look right now." SSP coefficient recalibration HELD; the fix is merit-order reconstruction
- date: 2026-07-25
- source: docs/staging/done/DIRECTOR_RULING_SSP_BASELINE_HELD_MERIT_ORDER_FIRST_2026-07-25.md
- kind: ruling
- theme: fairness-and-pricing
- ruling: Part (a) is "a rejection of the proposed fix's shape", the director overriding the advisor. Evidence: a local per-year refit still leaves 2020, 2021-crisis and 2025 negative — "a form limit — evidence the structural story is wrong in calm regimes, not merely mis-parameterised. A regime-aware A0/A1 recalibration would lower MAE while leaving the wrongness intact ... Under R12 that is the shape of a goal-sought improvement even when each step is defensible." The real fix: Board Spec 004's reconstructibility test — "power must be substantially reconstructible from gas, carbon, demand and wind on ordinary days — or it was not formed, only generated"; the scarcity term "should earn its structure in tight hours; it should not be carrying ordinary ones."
- scope: standing
- superseded_by: none seen (UNBLOCK_BATCH 07-28 restates merit-order as "the item the director has twice named as most important")
- reflected_in_CLAUDE_md: partly (R12 as "Outputs are diagnostics, never targets"; "Prefer measuring to arguing")
- reflected_in_DIRECTOR_CANON_md: partly (R12)
- note: Whether the merit-order reconstruction ever landed is not determinable from this batch; it was still "not drawing" on 07-28 behind a scheduling window the machine said "elapses today".

### [R-A-98] Protection is a floor outside the ranking: no metric can demote a regulatorily-significant group below full-fidelity modelling
- date: 2026-07-20
- source: docs/staging/done/DIRECTOR_STEER_SEGMENTATION_LEARNING_VALUE_REFRAME_2026-07-20.md
- kind: ruling
- theme: fairness-and-pricing
- ruling: "The 'critical/protected groups' list stays and should if anything widen: regulatory protection matters a great deal to the director. State plainly that no metric — learning-value included — can ever demote a regulatorily-significant group (vulnerability, fuel poverty, prepayment, priority-services, debt) below full-fidelity modelling. Protection is a floor outside the ranking, not a term inside it."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: A fairness wall with no canon home. Nothing in CLAUDE.md names vulnerability, PSR or fuel poverty.

---

## docs/staging/done/DIRECTOR_STEER_TRIANGULATION_WEATHER_DEMAND_PRICE_2026-07-22.md

### [R-B-61] Tariffs derive from the stack; the 120-day naive estimator is the company's STARTING belief that trading experience must improve
- date: 2026-07-22
- source: docs/staging/in_progress/DIRECTOR_STEER_WHOLESALE_VALUE_CHAIN_2026-07-22.md
- kind: canon
- theme: fairness-and-pricing
- ruling: Fixed tariffs lock the shaped forward cost at acquisition (plus network/policy/operating/margin); variable reprices cap-methodology-like. "The retail prices we expect must be driven by this data, not asserted beside it." SIM owns true curves and outturn; the company forecasts, trades, and is scored on belief-vs-truth.
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: The one open contract-touching question at park — whether the constructed stack REPLACES or SITS BEHIND the published Ofgem cap (WVC_5) — has no recorded answer in this batch. Cannot tell.

### [R-B-126] Registered design principle: what genuinely serves the customer is not always what the market has normalised — a seasonal DD would serve better but customers do not expect it; a supplier that ignores expectations loses the customer before the benefit lands
- date: 2026-07-25
- source: docs/staging/in_progress/DIRECTOR_STEER_DD_SEASONAL_CASHFLOW_2026-07-25.md
- kind: guidance
- theme: fairness-and-pricing
- ruling: "the gap between true need and market norm is itself a modellable phenomenon and arguably where the product opportunity sits." Register as a candidate personalisation product for the growth/product session; do not build a variable-DD product ahead of it. The growth-timing analysis (acquisition seasonality × solvency × the MC-2 collateral loop) is reserved to the same session.
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: A director insight that goes to the heart of the personalisation thesis (now "saving them money, time and carbon") and is parked behind a session that was never recorded as held. Likely forgotten; worth resurfacing.

### [R-B-131] D6 — Ability-to-pay is a HARD regulatory constraint on the dunning ladder (SLC 27.5–27.8): a repayment-rate mechanism without an affordability assessment is non-compliant by construction; failable invariant
- date: 2026-07-25
- source: docs/staging/in_progress/DIRECTOR_STEER_DUNNING_DEBT_PROVISIONING_2026-07-25.md
- kind: ruling
- theme: fairness-and-pricing
- ruling: `ability_to_pay` had zero hits in the repository; the built ladder is the easy timing half. Coupling gap, not build-from-scratch: C6_affordability_inference already produces an affordability band from observables.
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: partly (§1 regulation-commons doctrine)
- note: Ladder sequenced step 3 with ability-to-pay "from the first commit rather than a later compliance retrofit". Cannot tell.

### [R-B-167] RESERVED to the director: money representation — every sampled module computes money in float, zero Decimal; against the Tier-1 rule "bills accurate above all" the position is UNDECLARED, the worst of the three; bring a recommendation with evidence; do not migrate money types on your own initiative
- date: 2026-07-28
- source: docs/staging/in_progress/DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28.md
- kind: ruling
- theme: fairness-and-pricing
- ruling: Evidence wanted: worst observed rounding drift across a full billing run; blast radius of a boundary conversion. "Either answer can be right. The ruling is his."
- scope: standing (until ruled)
- superseded_by: none seen (WORK_AT_RISK would classify a type migration as reversible-with-undo, but nothing records that)
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: money_representation_evidence was one of the four "reason unstated" blocks on 07-28/29. No ruling appears anywhere in this batch. Given Tier-1 bill accuracy, the most consequential unanswered reserved question in the batch. Likely forgotten.

### [R-C1-49] Margin stays off the front door; checks a reader cannot grade are reported, not blocking
- date: 2026-08-20
- source: docs/staging/done/DIRECTOR_CONSOLE_2026-08-20.md
- kind: ruling
- theme: fairness-and-pricing
- ruling: "margin stays off the front door — leave it as you've set it, and keep those five checks reported-not-blocking until a reader can open the page they grade."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: Reaffirms RC7 (2026-07-24, not in batch: "no cohort-derived pound aggregate may lead a public surface"). The 08-28 mission rewrite gives RC7 its reason ("Charging someone the cap transfers value, it doesn't create it") but neither CLAUDE.md nor the canon names RC7.

### [R-C1-84] Pricing follows expected cost, including default risk, collections and bad debt; establish what is allowed from the sources, not recollection
- date: 2026-08-25
- source: docs/staging/done/DIRECTOR_CONSOLE_2026-08-25.md
- kind: ruling
- theme: fairness-and-pricing
- ruling: "change how you're treating price and risk, and don't take my word for the rules — read them. Real suppliers already differentiate on payment risk. Direct debit discounts exist and are permitted; the cap itself sets separate levels for direct debit, standard credit and prepayment … So the shape isn't 'never price up a vulnerable household'. It's that pricing follows expected cost — and default risk, collections cost and bad debt are part of that cost. Put them inside the EV arithmetic and let the answer emerge rather than imposing a floor. Establish what's actually allowed rather than assuming, and use the sources: the regulation commons in the repo, the licence obligations register, and your read access to Ofgem and legislation. SLC 0 and SLC 27, the ability-to-pay and self-disconnection duties, the microbusiness and deemed-contract rules, and the commercial debt interest legislation. Record what is explicitly permitted, what is prohibited, and what is tolerated-but-unwritten, with citations. That register is what the pricing arm should be constrained by — not my recollection and not yours. Keep the floor as a backstop only until that's done."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: The pricing-permissions register (permitted / prohibited / required / tolerated-but-unwritten) was built 08-25 in the commons; the vulnerability floor was removed as "a stronger rule than the licence supports — SLC 27.8 governs INSTALMENTS, not the unit rate." Neither the principle (price follows expected cost; fairness constraints come from the licence register, not a floor) nor the register's existence is in CLAUDE.md. The 08-25 summary also notes the cap artefact "has one level per fuel, the real cap has DD/standard-credit/prepayment levels" — a fidelity gap the director's own words exposed, still open.

### [R-C2-35] The household side is measured and NOT scored — the two-sided objective is the director's to release
- date: 2026-08-28
- source: docs/staging/done/SEAT_TO_DIRECTOR_THE_MISSION_REWRITE_2026-08-28.md
- kind: other (pending director decision under silence-is-validation)
- theme: fairness-and-pricing
- ruling: `household_value_share.py` computes what a household paid vs the published default tariff at its metered volumes; at the cap the household keeps exactly £0 ("Your sentence is the bottom two rows"). "Wiring a household term into a decision surface changes what the company does, which is a difficulty change and therefore R13's and yours." Barred from every organ by `test_household_share_is_not_yet_a_target.py`, release named as the director's decision. Seat's recommendation, to be taken on silence: "score the two sides jointly and let the maximiser see both."
- scope: unclear
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly (consequence 1; nothing says whether the two-sided score was released)
- reflected_in_DIRECTOR_CANON_md: no
- note: A proceed-on-silence default on a decision the same letter calls R13's and the director's — structurally the EP6 problem (R-C2-40) from the other direction. Whether he answered is not in this batch. Also the headline reversed mid-letter (per-customer arm now loses £4,724) with two candidate causes, one of them another lane's uncommitted clock repair — "not reproducible from any commit".

### [R-D-71] Guard-rails inside the register: algorithmic hedging only within a director-set risk envelope, never a speculative position; location opt-in only and never set back on inference alone for the possibly vulnerable; gamification must not be regressive; value-based acquisition spend and service design, not value-based pricing at quote
- date: 2026-09-06
- source: docs/staging/done/DIRECTOR_RULING_SUPPLIER_USE_CASE_REGISTER_AND_SIM_FIDELITY_2026-09-06.md
- kind: standing
- theme: fairness-and-pricing
- ruling: 3.3 "within a director-set risk envelope — never a speculative position on the book... the 2021-style tail must be survivable by construction." 2.2 "smarter version with location, opt-in only... never set back on inference alone for anyone who may be vulnerable." 2.5 "not regressive — the free-and-easy rungs must score as richly as the capex ones." 4.7 "Rules: value-based acquisition spend and service design, not value-based pricing at quote."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: Four fairness rules with real teeth, each buried as a clause inside a use-case row. "Not value-based pricing at quote" is a pricing-fairness ruling that belongs beside "Charging someone the cap moves value without making any" in the mission block. The risk envelope is "Reserved for the director" and has never been set (A51 L0).

### [R-E-35] Harm-cost ratio R = 8:1 signed (band 5:1–10:1): harm-averse but bounded so both corporate deaths stay possible; 8:1 prices the tail
- date: 2026-07-13
- source: docs/staging/done/DIRECTOR_ANSWER_HARM_WEIGHTS.md
- kind: ruling
- theme: fairness-and-pricing
- ruling: "**R = 8:1 SIGNED. Band 5:1–10:1.** ...the shape is right — heavily harm-averse but **BOUNDED**, so BOTH real deaths stay possible (regulatory/licence death from harm; insolvency death from bad debt). Direct costs are roughly comparable... so **8:1 is pricing the TAIL** — enforcement, mass remediation, licence risk... Never tune this toward a gap number (Law B / R13). It changes only by the director's explicit re-signature."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly
- reflected_in_DIRECTOR_CANON_md: no
- note: Recorded in HARM_COST_WEIGHTS_DECISION.md ("at the SIGNED R = 8:1") and A7's simplification yaml. CLAUDE.md keeps only the parent wall (baseline/curriculum split). The same document carries the advisor's finding that the flip-point formula was inverted (`R* = p/(1-p)`, not `(1-p)/p`) and the lesson "mutation-test it at p=0.9 and p=0.1, not at p=0.5" — both evaluate to 1 at the coin flip — which is a generalisable testing rule not recorded anywhere current.

### [R-E-36] Register two simplifications (heavy-tailed harm; harm scales with vulnerability); anchor H1 on the £90m British Gas aggregate and treat licence loss as a scenario, not a probability
- date: 2026-07-13
- source: docs/staging/done/DIRECTOR_ANSWER_HARM_WEIGHTS.md
- kind: guidance
- theme: fairness-and-pricing
- ruling: "**Harm is HEAVY-TAILED, not a point estimate**... Register as a named simplification." "**Harm must SCALE WITH VULNERABILITY**... Real regulation makes that distinction; our scalar does not yet. Register it — it couples naturally to W2_8 (self-rationing) and the PSR." "Use the **£90m British Gas aggregate as the DIRECT anchor** (~£700/case). **Treat licence-loss as a SCENARIO, not a probability** — you cannot estimate the tail of an event that has almost never occurred, and a fabricated probability would be worse than an honest scenario."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly
- reflected_in_DIRECTOR_CANON_md: no
- note: "A fabricated probability would be worse than an honest scenario" is the knowledge-first rule in CLAUDE.md ("An honest `None` with a named reason is worth more than a plausible number") six weeks early. Whether the vulnerability-scaling simplification was ever modelled is not visible in this batch.

### [R-E-37] The finding to publish: at even odds any harm-aversion means forbear — pursuit must be earned by confidence
- date: 2026-07-13
- source: docs/staging/done/DIRECTOR_ANSWER_HARM_WEIGHTS.md
- kind: guidance
- theme: fairness-and-pricing
- ruling: "**At even odds, ANY harm-aversion at all means forbear. Pursuit must be EARNED by confidence.** That is what regulation implicitly demands, no supplier can articulate it, and we can put a number on it. Feature it."
- scope: one-off
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: Only the A6/A7 simplification yamls mention "earned by confidence"; no Proof-door publication is evidenced in this batch. A genuinely good, publishable thesis sentence that may have been lost.

---

## docs/staging/done/DIRECTOR_COMMENTS_BOX.md (2026-07-09)

### [R-F-113] Don't price comfort — floor it: an 18°C WHO/NICE health floor; below it the finding is the fabric, not the thermostat; every route to a bill currently runs through the customer's capital
- date: 2026-09-08
- source: docs/staging/console/DIRECTOR_CONSOLE_2026-09-08.md
- kind: ruling
- theme: fairness-and-pricing
- ruling: "Hot water: correct and re-baseline. A 1.4-1.6x overstatement on every fabric-eligible customer is the kind of error that invalidates the intervention ranking, which is the mission. Weather: agreed, don't synthesise 194,861 cells. Inventing weather we haven't measured is a fabricated observable underneath every demand figure. Say plainly on the page what the four archives cover and what that bounds. Advice: build it, and you were right to stop. But don't price comfort — floor it. A comfort cost makes warmth a willingness-to-pay question, and the households that would accept the trade are the ones who can least afford to refuse it, so the model would find the fuel-poor and recommend they be cold. That's advising self-rationing in a cold home, which the use-case register says we detect rather than cause. Use a health floor instead: 18°C, from WHO and NICE guidance — published and citable. Below it, turn-down is never recommended at any price, and the finding for that household is that the fabric needs work, not the thermostat. Above it, turn-down is a genuine zero-capital offer and the physics needs no invented constant. That also fixes the offer book's real problem: every route to a customer's bill currently runs through their capital, which is no use to the households that need it most."
- scope: standing
- superseded_by: parked (not revoked) 2026-09-08 12:39: "park the flow-temperature source, the temperature floor and the awkward-cases portfolio. They're real and they're second order" (R-F-114)
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: A fairness ruling with teeth — the only one in the batch — and it is parked two hours later and recorded nowhere standing. "We detect self-rationing rather than cause it" and "every route to a customer's bill runs through their capital" are mission-level statements about who the product must serve. High risk of being forgotten when advice is built.

# Theme: carbon (9 entries)

### [R-A-4] Customer money-saving is the engine of abatement; usage-side savings only, never discounting
- date: 2026-07-28
- source: docs/staging/done/DIRECTOR_CANON_PITCH_V7_2026-07-28.md
- kind: canon
- theme: carbon
- ruling: "By the Director's decision (28 July 2026), customer money-saving is declared the engine of abatement: bills cut by reducing or time-shifting usage, never by discounting, so the customer's motive and the carbon mission are served by the same action. The customer-savings ledger counts usage-side savings only — price transfers never count." "Discounting ... moves margin between supplier and customer and saves nothing"; "a discount can be gamed and a kilowatt-hour cannot."
- scope: standing
- superseded_by: none seen (the 2026-08-28 mission adds money and time as currencies but keeps "value created THEN shared; transfer is not creation")
- reflected_in_CLAUDE_md: partly ("Transfer is not creation. Charging someone the cap moves value without making any." — the usage-side-only ledger rule and the no-discount rule are not stated)
- reflected_in_DIRECTOR_CANON_md: no
- note: Strong, specific and largely invisible now: nothing in CLAUDE.md says the customer-savings ledger excludes price transfers. Oct-2026 staging findings are about retention offers, price-match saves and renewal pricing — i.e. price transfers — so the rule is exactly the one that would bite today.

### [R-A-10] The score and its discipline: £/tCO2e vs £273; a diagnostic not a target; three ledgers
- date: 2026-07-28
- source: docs/staging/done/DIRECTOR_CANON_PITCH_V7_2026-07-28.md
- kind: canon
- theme: carbon
- ruling: "£ per tonne of CO₂e saved = (cost to serve + cost to persuade, including compute) ÷ (carbon abated)"; yardstick the UK government appraisal value £273/tCO2e (2025). "it is a diagnostic, not a target — the moment a number becomes something to optimise, it stops measuring anything"; "three ledgers, all reported: carbon saved for customers; carbon spent serving them — people, compute, tokens; and the net position. A carbon claim that counts only one side is not a claim."
- scope: standing
- superseded_by: partly — 2026-08-28 mission makes carbon one of three currencies; PITCH_V7 header says "the £/tCO₂e formula ... survive[s]"
- reflected_in_CLAUDE_md: partly ("Outputs are diagnostics, never targets" → test_carbon_not_a_target; "Carbon is designed and unwired")
- reflected_in_DIRECTOR_CANON_md: partly (R12 / LAW A)
- note: Three-ledger reporting (incl. the machine's own carbon spend) has no visible mechanism; CLAUDE.md says carbon is unwired as of 2026-08-28.

### [R-C1-81] The carbon score is the entire point: wire it to live reads and grid intensity, publish with provenance and stated gaps
- date: 2026-08-25
- source: docs/staging/done/DIRECTOR_CONSOLE_2026-08-25.md
- kind: ruling
- theme: carbon
- ruling: "257 residential on half-hourly data means the carbon score is finally measurable, and the site still says NOT YET MEASURED. That number is the entire point of this project. Wire the carbon ledger to live meter reads and grid intensity, publish it with its provenance, and say plainly what it does and does not yet include."
- scope: standing
- superseded_by: DIRECTOR_GUIDANCE_THE_WORLD_MUST_PRESS_2026-08-28.md ("Deliberately out of scope for now, by director decision: the carbon score … They return once the basics hold.")
- reflected_in_CLAUDE_md: partly
- reflected_in_DIRECTOR_CANON_md: no
- note: Direct contradiction inside three days: 08-25 "that number is the entire point of this project"; 08-28 the carbon score is "deliberately out of scope for now … measuring an unbuilt capability is premature". The carbon instrument was built and R11-verified on 08-25 (252 residential, 108% timing effect) before being descoped. CLAUDE.md now says "Carbon is designed and unwired." The mission sentence (08-28) keeps carbon as one of three currencies. The reconciled position is: measured, published, but not a target until the world can press — and that reconciliation is written nowhere.

### [R-C1-120] Deliberately out of scope for now: the carbon score and products beyond price
- date: 2026-08-28
- source: docs/staging/done/DIRECTOR_GUIDANCE_THE_WORLD_MUST_PRESS_2026-08-28.md
- kind: ruling
- theme: carbon
- ruling: "Deliberately out of scope for now, by director decision: the carbon score, and products beyond price (efficiency advice, tariff fit, solar, heat pumps, time-shifting). Both are real and both are downstream — measuring an unbuilt capability is premature, and the products need a world that can reward them. They return once the basics hold."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly
- reflected_in_DIRECTOR_CANON_md: no
- note: See R-C1-81: contradicts the 08-25 "That number is the entire point of this project" within three days, and sits oddly beside the same-day mission sentence that makes carbon one of three currencies and "modelling, tariffs and advice" the channels (the products listed here are the advice channel). CLAUDE.md records "Carbon is designed and unwired" and the channels gap, but not that carbon is descoped by decision, nor the return condition ("once the basics hold"). The descoping is the kind of decision that is easy to forget and then re-argue.

### [R-C2-34] Carbon's monopoly on the purpose is demoted, not carbon
- date: 2026-08-28
- source: docs/staging/done/SEAT_TO_DIRECTOR_THE_MISSION_REWRITE_2026-08-28.md
- kind: other (seat's reading of director intent)
- theme: carbon
- ruling: "Rejected: rewriting the carbon commitments down. Carbon is now one of three currencies, not the mission — but E5, the SAVED/SPENT/NET ledger and the £273/tCO₂e yardstick all survive at their levels... Your sentence demoted carbon's monopoly on the purpose, not carbon."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly (carbon as one currency; no yardstick, no ledger named)
- reflected_in_DIRECTOR_CANON_md: no
- note: Tension to resolve: 08-25 console "257 residential on half-hourly data means the carbon score is finally measurable... That number is the entire point of this project. Wire the carbon ledger to live meter reads and grid intensity, publish it with its provenance" vs 08-28 carbon as one of three. The 08-17 brief also says "the fitness function is the cheapest tonne of carbon abated". Which statement the carbon score's priority now rests on is unclear.

### [R-D-73] Two discovery pulls authorised now — historical half-hourly grid carbon intensity aligned to settlement, and a published forward-curve or hedge-cost series — registered as data assets, no product build; the register is product and goes to Capabilities in the external register with a status per item
- date: 2026-09-06
- source: docs/staging/done/DIRECTOR_RULING_SUPPLIER_USE_CASE_REGISTER_AND_SIM_FIDELITY_2026-09-06.md
- kind: ruling
- theme: carbon
- ruling: "Two small discovery pulls are authorised now (reversible, cheap, wall-clean): historical half-hourly grid carbon intensity aligned to the existing settlement data (for 4.6 and the mission's carbon accounting); a published forward-curve or hedge-cost series sufficient to backtest 3.1... Register both as data assets with provenance; no product build." "Publish it to the site's Capabilities register in the external register (no atom names, no phase labels) as 'what a supplier can do with this world', each item carrying its SIM-native test and its current status."
- scope: one-off
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: G14 carbon intensity L2 (harden) — done; G15 forward curve L0 — not started; A50 publication L0 — not done. The carbon pull is the only carbon work in the period that progressed, and CLAUDE.md still says "Carbon is designed and unwired."

### [R-S-100] Carbon is not demoted — one of three; every carbon commitment survives but loses the claim to be the whole purpose
- date: 2026-08-28
- source: docs/design/THE_MODEL_ON_A_PAGE.md
- kind: standing
- theme: carbon
- ruling: "Carbon is not demoted — it is one of three. The old sentence made carbon the mission and £/tCO₂e the score. The new one makes carbon one of three currencies the household is saved in … Every carbon commitment on this page (E5, the SAVED/SPENT/NET ledger, the £/tCO₂e front-page target) survives intact and keeps its level; what it loses is the claim to be the whole purpose."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly ("Carbon is designed and unwired" — the not-demoted sentence is absent)
- reflected_in_DIRECTOR_CANON_md: no
- note: This is the only statement of carbon's purpose in the seven files. INTERNAL TENSION: TF2 still says "Carbon becomes the headline: … £/tCO₂e on the front page" — the pre-mission framing left standing in the evolution section. The open row a-household-s-electricity-carbon-is-shown (2026-10-05) awaits a definition ruling (T&D losses).

### [R-S-113] Carbon: designed ledger, not yet instrumented; emissions now measured (2026-10-09); abatement unmeasured for want of a counterfactual
- date: 2026-10-09
- source: docs/design/THE_MODEL_ON_A_PAGE.md
- kind: standing
- theme: carbon
- ruling: "Carbon: designed ledger (SAVED/SPENT/NET), honestly not yet instrumented — the site says so plainly. (Corrected 2026-10-09 … a household's emissions are now measured. `half_hourly_footprint.py` multiplies NESO's half-hourly intensity by the half-hourly reads … The ledger is still called by nothing, and abatement is still unmeasured, because nothing supplies the counterfactual it needs.)"
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no ("designed and unwired" is now behind this)
- reflected_in_DIRECTOR_CANON_md: no
- note: CLAUDE.md's "Carbon is designed and unwired" is the stale side. The T&D-losses definition row (2026-10-05) is open.

### [R-S-157] OPEN — a household's electricity carbon is shown per kWh generated; whether to add T&D losses (strategy)
- date: 2026-10-05
- source: docs/direction/DIRECTION.yaml
- kind: standing
- theme: carbon
- ruling: Proposal: "Add losses as its own named line beside the electricity figure, at DESNZ's published T&D factor (0.01853 kgCO2e/kWh, 2025 set …), never folded into the grid series, so the published NESO number stays NESO's and the household sees both. Until you rule, the page states that losses are not included."
- scope: standing (open)
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: "it was described as raised on 2026-10-05 but never reached this list" — a known escalation leak. The only carbon-definition question in the seven files; carbon's purpose (why measure it) is not what is asked.

# Theme: other (4 entries)

### [R-E-26] Copyright entity: "© 2026 Poesys Platforms. All rights reserved." — no "Ltd" until incorporation
- date: 2026-07-12
- source: docs/staging/done/DIRECTOR_ANSWERS_ENTITY_CRAWLERS.md
- kind: ruling
- theme: other
- ruling: "Footer site-wide: **'© 2026 Poesys Platforms. All rights reserved.'** Trading-style name — director intends to incorporate... Do NOT suffix 'Ltd' until incorporation; add a one-line register note to swap to the full registered name on incorporation."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: `site/` is not in the snapshot so the footer could not be checked; no other `docs/` file mentions "Poesys Platforms" or the incorporation register note. The intent to incorporate is a real-world fact worth carrying in canon; it appears nowhere else.

### [R-E-27] AI-crawler policy: block training harvesters, allow user-directed fetch and normal search
- date: 2026-07-12
- source: docs/staging/done/DIRECTOR_ANSWERS_ENTITY_CRAWLERS.md
- kind: ruling
- theme: other
- ruling: robots.txt on poesys.net: "**Disallow (training harvesters):** GPTBot, ClaudeBot, Google-Extended, CCBot, Applebot-Extended, PerplexityBot, Bytespider, and peers... **Explicitly ALLOW:** Claude-User and Claude-SearchBot (user-directed fetch — this is how the advisor reads the live site), plus normal search (Googlebot, Bingbot) untouched. Rationale on record: consistent with the private-repo IP posture — humans and search indexing unaffected; the site declines to be training data."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: No later `docs/` reference to robots.txt or the crawler list (REPO_PRIVATE_AND_IP findings do not mention it). A standing policy with no visible owner or check — possibly lapsed; cannot verify without `site/`.

### [R-S-130] Geography and culture are parameterised variables; the core physics stay constant
- date: unknown (June 2026)
- source: docs/vision/pitch.md
- kind: standing
- theme: other
- ruling: "Regulatory frameworks, tax structures, currencies, market mechanisms, and cultural behaviours are parameterised variables, not architectural dependencies. What stays constant is the core physics … The operational blueprint from UK energy … is the starting point" for German energy.
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: Vision claim with no TF1/TF2 registration in MOAP. Not contradicted; not pursued.

### [R-S-132] What we are looking for — not raising capital; domain stress-testing first; translation partners; capital only when the blueprint is proven
- date: unknown (June 2026)
- source: docs/vision/pitch.md
- kind: standing
- theme: other
- ruling: "We are not raising capital at this stage. … The most valuable thing a domain expert can do is try to break the simulation. If the physics are wrong, the discoveries are wrong." Capital "at the point when the simulation has already run the full discovery process and the blueprint is proven. We are not there yet. We will be."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: "Try to break the simulation" by domain experts is the Expert Hour / blind review idea; the open row no-atom-can-reach-l3 (2026-10-04) shows reviewer independence is unobtainable from inside and external review is "at your choosing" — the pitch's external stress-testers never materialised in the mechanism.


