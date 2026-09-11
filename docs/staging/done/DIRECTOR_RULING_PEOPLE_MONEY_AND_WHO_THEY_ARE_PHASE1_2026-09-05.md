**Severity:** RECORDED · **Lane:** W2_customer_generator (household side) + knowledge layer · **Priority:** P1, director-decided · **Proportionality:** reversible / narrow — just do it

# [DIRECTOR-RULING][ADVISOR-STAGED] People modelling and segmentation — phase 1 of 3: money and who they are (2026-09-05)

**Decided by the director in the advisor channel, 2026-09-05. Transmitted as decisions. The mechanism is yours.** Third axis of the portfolio-draw approach; siblings staged today: `DIRECTOR_RULING_WEATHER_CELLS_HEAT_LOAD_SEGMENTATION_PHASE1_2026-09-05.md` and `DIRECTOR_RULING_HOUSING_VALUE_CEILING_AND_SAMPLE_PHASE1_2026-09-05.md`. The frame in the housing ruling's §1 applies verbatim here.

## 0. Zero-context orientation

The machine already carries most of the household traits this axis needs, as **independent per-axis draws**: household size (ONS Census TS017), tenure (EHS), fuel poverty conditional on payment method (DESNZ LILEE), direct-debit share (DESNZ QEP), engagement archetypes at 45/35/20 (Ofgem RMI, director-ratified 2026-07-22), daytime-at-home rates by composition (EFUS), consumption by number of adults (NEED), tone/framing susceptibility, satisfaction heterogeneity, a life-event stream. Its own D-SEGMENT discovery pass (`docs/market_research/segmentation_joint_structure.md`, 2026-07-21) found the defect this ruling addresses: twenty-one trait axes, overwhelmingly drawn independently, with only two couplings built (tenure-gated adoption; the organisation↔budget↔DD link). A wiring plan exists (`docs/design/SEGMENTATION_WIRING_PLAN.md`, families Need / Attitudes / Engagement). **Build on both; do not mint a parallel trait vector.**

The director's diagnosis, in his words: *"I guess thinking in terms of CLV credit risk, rental vs owner, number of people versus typical for house matters a lot. Next come apathy and price elasticity. Then cost to serve (likelihood to call etc). Plus then shape, and finally value add, willingness to buy services and kit or just appreciate the efforts to save money and carbon."*

## 1. The two-layer structure (director-decided)

Every household is drawn as **prior plus residual**, and the epistemic wall falls between the two:

- **Layer one — the household you would expect, given the postcode and the house.** Tenure, composition, income band, car ownership, payment method, typical presence. All published at small-area level (Census 2021/22 cross-tabs of tenure × accommodation type × composition × car × age; fuel poverty, income and deprivation at the same geography). This layer is drawn from public data and is therefore *guessable by the company from an address*.
- **Layer two — how this household deviates from that.** The single pensioner in the four-bed; the five people in the two-bed flat; the shift worker; the family away three weeks each summer; the couple working from home. Private, hard to observe, and what the company must **discover** — from the meter shape, the payment record, contacts, and by asking. Random but **anchored in distribution**: the census occupancy rating (people versus bedrooms) gives over- and under-occupancy real published shares by area; the within-cell spread of consumption in the national household sample sizes the residual.

**Geography is the coherence key across all three axes.** Draw the house from the area's stock, the household from the area's population, the weather from its cell. The correlations that matter — the pensioner couple in the off-gas bungalow, the young renters in the city flat, the social tenant on prepayment in the low-rise block — come from the small-area data, not from an invented correlation matrix.

## 2. Decisions already made — transmit as decisions, do not relitigate

1. **Three people phases, ordered by the director's CLV ranking.** Phase 1 (this ruling): money and who they are. Phase 2: how they behave toward a supplier — apathy and price elasticity; cost to serve (likelihood to call, channel, complaint propensity); the stability-versus-time-of-use preference; conditional on phase 1. Phase 3: the residual and the change — working hours, holidays, shift patterns, working from home; children arriving and leaving; unprompted device purchases (extending the existing life-event stream); and the value-add term — willingness to buy kit or services, kept **distinct** from willingness merely to appreciate being saved money and carbon. Phases 2 and 3 are **decided and registered, not authorised**.
2. **Phase 1 scope:** tenure (owner / private renter / social renter); composition (size, ages, children, pensioners); occupancy versus typical for the house; income band and fuel poverty; payment method (DD / standard credit / prepayment — the three-way split, using the anchor the repo already holds in `docs/market_research/dd_attribution_confound_w2_10.md` rather than the two-member collapse the worker finding of 2026-09-01 flagged); credit risk as a drawn propensity; **typical presence** (daytime-at-home by composition, already anchored), because it comes free with composition and usage needs it. People-driven usage: base load, hot water, presence shape, appliance devices.
3. **Coverage target: 99% of variance in the outputs, including tails.** Outputs, not traits: people-driven usage, bad-debt and payment behaviour, the credit-risk term. Draw for difference; reject near-duplicates on outputs.
4. **Un-anchorable quantities are curriculum values, not machine choices.** The can't-pay/won't-pay split (checked three times, unpublished) and the household-level switching amplitude (`docs/market_research/household_switching_response_amplitude.md`) are R13 director values. Present each as a named slot with the evidence that exists, the range it bounds, and the recommended default, for the director to ratify. Do not fill them.
5. **Fresh draw per life; the visited-corner ledger across lives.** As for houses.
6. **GB only.**

## 3. Deliverables

1. **The coherent joint for layer one**, keyed on small-area geography and conditioned on the drawn house: the published cross-tabs, the raking, and the tests that prove the marginals still recover — extending the existing trait vector and the wiring plan, replacing independent draws with conditional ones where a published joint exists, and **registering as independent, with the reason, where none does**.
2. **Layer two as anchored residuals**: occupancy-versus-typical from the census occupancy rating; residual usage spread from the within-cell distribution of the national household sample; a register of which residuals are anchored and which are curriculum slots.
3. **Per-household hidden truth** for every drawn household: the phase-1 traits, people-driven usage (base load, hot water, presence shape, devices), credit-risk and payment propensity, the CLV basics that are people-driven (bad debt, payment method cost-to-serve).
4. **The coverage curves and N** for the people axis, and the **crossed** curve — house × weather × people — showing what the three axes together cover and where the corners lie.
5. **The knowledge page** — topic: who lives where, and what that does to energy use, payment and risk. Six rungs per the knowledge canon; Fact/Choice/Wiring; the expected-shape block states the findings falsifiably (e.g. "occupancy explains X% of within-house usage variance; prepayment households carry Y× the fuel-poverty rate of direct-debit households"); external register. Stubs for phase 2 (how households behave toward a supplier) and phase 3 (the residual and the change).
6. **Registers updated:** `docs/market_research/ASSUMPTIONS.md`, `docs/institutional/knowledge_map.md`, working docs under `docs/market_research/`; the joint and the sample as machine-readable artefacts the run draw consumes.
7. **Report to the director, plain English:** N, the curves, which traits carry the variance, the corners the sample found, and the curriculum slots awaiting his values.

## 4. Non-negotiables

- **Generation and validation from separate sources.** Generate from Census 2021/22, EHS, DESNZ fuel-poverty and income statistics. Validate people-driven usage against the national household sample, payment behaviour against the Bacs/DESNZ anchors already in the machine, and never against the SIM's own outputs.
- **Where a joint is published, it is used; where it is not, the independence is declared** — the July finding's rule, made a control: no trait pair may be drawn independently without a register entry saying so.
- **No fabricated coefficients; no filled curriculum slots.** The two named un-anchorable quantities stay empty until ratified.
- **Wall placement:** everything in §3.3 is SIM truth. Layer one is *guessable* by the company from public data but not *given* to it; the company's inference belongs to a later programme. Nothing here builds company-side inference.
- **Do not reach into phase 2 or 3.** Apathy, elasticity, contact propensity, uptake, life events and holidays are out. Where phase-1 usage needs a phase-3 input (a holiday dip), leave a named empty slot.
- **Keep the existing tests green.** The engagement mix, the DD share band, the population-share convergence tests are controls; a change to any published marginal is a fidelity finding decided blind to P&L, never a side effect.

## 5. Priority and sequencing

Product, P1, drawable now. Depends on the housing ruling only for the cross in §3.4 — start the joint and the residuals immediately; run the cross when the house sample exists. File scope overlaps the housing ruling on the premise-draw modules; sequence the two so they do not fork the same file, and say which went first. The weather pull's 72-hour clock outranks both.

## 6. Risk

**What it touches:** the household-trait and premise-draw modules (SIM side), new research and knowledge files, the run-draw artefact. Not billing, not the wall, not company code.
**Blast radius:** any run that draws households — marginals must recover to existing tolerances; the engagement mix and DD share are director-ratified and must not move as a side effect.
**Probable failure modes:** (a) a correlation matrix invented where a small-area cross-tab exists — §1 and §4; (b) the residual layer drawn without an anchor, or the prior layer given to the company — §4; (c) a curriculum slot silently filled with a plausible number — §4; (d) phase-2/3 mechanics creeping in — §4; (e) the page thinning to machinery — the knowledge canon's DoD 0: the page must genuinely explain.

## 7. WORK THIS CREATES

- The layer-one joint on small-area geography, conditioned on house; independence register for un-joined pairs.
- Layer-two anchored residuals; the curriculum-slot register with recommended defaults for ratification.
- Per-household hidden truth, people-driven usage, credit and payment propensities.
- Coverage curves and N for the axis; the crossed curve.
- One knowledge page (full depth) + two stubs.
- Register rows and research docs.
- Registration of phases 2 and 3 as decided-not-authorised, with their scope from §2.1.
- One plain-English report to the director, including the slots awaiting his values.
