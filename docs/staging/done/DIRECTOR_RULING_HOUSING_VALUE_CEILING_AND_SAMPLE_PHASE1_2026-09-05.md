**Severity:** RECORDED · **Lane:** W2_customer_generator (premise side) + knowledge layer · **Priority:** P1, director-decided · **Proportionality:** reversible / narrow — just do it

# [DIRECTOR-RULING][ADVISOR-STAGED] Housing modelling and segmentation — phase 1 of 3: the houses, the sample, the ceiling (2026-09-05)

**Decided by the director in the advisor channel, 2026-09-05. Transmitted as decisions. The mechanism is yours.** Sibling of `DIRECTOR_RULING_WEATHER_CELLS_HEAT_LOAD_SEGMENTATION_PHASE1_2026-09-05.md` (staged this morning); the two are the first two axes of one portfolio-draw approach described in §1.

## 0. Zero-context orientation

The SIM already draws a premise population from a joint of EPC band × property type × build era × heating system, raked onto English Housing Survey marginals, and computes a fabric heat-loss coefficient per premise (`docs/market_research/ASSUMPTIONS.md`, "Household Physical Property Attributes" and "Stock-Representative Premise Population"). That work stands. Its own register names the gaps this ruling closes: floor area rests on an unpublished bedrooms table; solar PV, EV, loft and cavity insulation are not drawn at premise level; bungalows are folded into detached; the EPC's model-versus-metered gap is not represented.

This ruling is **housing only**. People — tenure gating, engagement, price sensitivity, apathy, income stress, bad-debt propensity, uptake of any offer — are a separate programme the director will commission. Do not build any of them here; where a house-side quantity needs a people-side input to become money (an EV's mileage, a household's willingness), state the ceiling in physical units and leave the people term as a named, empty slot.

## 1. The portfolio-draw approach (director's frame, transmitted)

The director's aim, in his words: *"Creating enterprise value by automating ways to find individual customers we can create value for, and sharing in that value."* To find them, the world must contain them, and the company must have to look. Hence:

- **The SIM holds hidden variables; the company holds beliefs.** Every sample house has a full physical truth the company never sees. The company sees a postcode, an address (possibly fictional, but always on a real postcode sector), an EPC where one exists, and a meter.
- **Draw for difference, not for proportion.** The sample is not a representative slice of the stock. Two London terraces on one street teach the world nothing the first didn't; the south-facing detached house in Bournemouth, the Edinburgh tenement flat, the off-gas bungalow on a Welsh hillside each occupy a corner no other house covers. Houses are drawn so that the set spans the variation, and a candidate is rejected if a house already drawn would behave the same.
- **"Behave the same" is judged on outputs, not inputs:** usage level, shape and weather gradient, and the technical ceiling on each value lever. Not on type/age/size labels.
- **Coverage is a property of the ensemble of runs**, tracked across lives, with the corners not yet exercised steered toward. The director explicitly does **not** want every house in every geography in one run.
- **CLV variance is the cross of three axes** — house × weather × people — each covering its own variation. Portfolio economics (gross margin, opex, bad debt, value-add share) is the umbrella this feeds; the house axis supplies the house-driven terms only.
- **No averages, no archetypes as segments.** Segmentation is a *finding* (which physical quantities explain the variance) and, later, the company's belief structure — never the way the SIM represents a house.

## 2. Decisions already made — transmit as decisions, do not relitigate

1. **Three housing phases.** Phase 1 (this ruling): the houses, the sample, the ceiling. Phase 2: what the company can see of a house — the observation layer (EPC as a dated, modelled, ~60%-coverage snapshot; postcode and address as free signals; what the meter reveals). Phase 3: houses change — the unprompted timeline (boiler replaced at end of life and returning condensing; PV and EV arriving on their own adoption curves; extensions; the physics and ceiling updating, the EPC falling behind). Phases 2 and 3 are **decided and registered, not authorised**.
2. **Coverage target: 99% of variance, including tails.** The tail is where the money and the risk are, and marginal houses are cheap.
3. **Levers in phase 1** (technical ceiling per house, hidden truth): PV; battery (a function of PV, shape and tariff spread — state it as conditional); EV charging (parking → shiftable kWh; mileage is a people slot); insulation (loft, cavity, solid wall, draught-proofing); flow-temperature turn-down and heating/hot-water timing; a ladder of energy-efficiency behavioural actions from free-and-easy to effort-and-expense; tariff fit (shiftable share of load, seasonal bill swing, hence the value of stability versus time-of-use). **Heat pump is out of all three phases until the director says otherwise.**
4. **Ceilings are stated in physical units first** — kWh generated, saved or shifted; tonnes of carbon; customer effort — and monetised on top, because prices and policy move and belong to the value cycle. Effort is the "time" currency of the mission and is a real property of each rung.
5. **Current settings are hidden state.** Flow temperature, heating and hot-water schedules, thermostat set-point: the free-and-easy rungs' potential depends entirely on where the house is now, so each house carries a current-settings draw from published distributions.
6. **House-driven CLV basics come out of phase 1:** consumption (for gross margin) and the meter and fuel facts that drive cost to serve (smart or not, dual fuel, off-gas). Bad debt is people; leave it out.
7. **Weather cross:** phase 1 crosses houses with weather at the 1 km grid via the house's postcode, using the HadUK-Grid pull the weather ruling commissions. When the weather cells land, re-run the coverage curve on cells. Do not wait for the cells to start.
8. **Fresh draw per life, never a fixed library.** The fitted joint is the asset; the houses are not. Addresses are regenerated per run. The visited-corner ledger across runs is what guarantees the corners get exercised.
9. **GB only.**

## 3. Deliverables

1. **The fitted joint** of the physical quantities that carry the variance — floor area (anchored from the EPC register, closing the bedrooms-table hole), fabric heat loss, thermal mass, solar aperture by orientation, roof (area, orientation, pitch, flat-vs-house), off-street parking, heating system and fuel including **no mains gas**, current settings — with their published correlations (flats are newer and smaller; pre-1919 is solid-wall; rural is detached, off-gas and has a drive). Bungalow becomes a real type.
2. **The space-filling sample** across quantities × weather, with output-similarity rejection, and **the two coverage curves**: distinct houses versus variance covered (level, gradient, shape, ceilings), and tail coverage (share of the population's top 1% on each output represented). These set N. Report N.
3. **Per-house hidden truth** for every drawn house: physics, current settings, usage (level, half-hourly shape, degree-day gradient), and the ceiling on each phase-1 lever in physical units and money, plus the house-driven CLV basics.
4. **The knowledge page** — topic: what a house's physical properties do to its energy use and its potential, and where the value sits across Britain. Six rungs per the knowledge canon (`docs/staging/done/ADVISOR_PILOT_KNOWLEDGE_PAGE_WHOLESALE_2026-07-28.md`); Fact/Choice/Wiring claim classes; the expected-shape block states the phase-1 findings falsifiably (e.g. "floor area and fabric loss explain X% of household-weighted gas variance; the technical PV ceiling exceeds Y kWh/yr for Z% of houses"); the sample design and N are Choice-class, versioned. Stubs minted now for phase 2 (what a supplier can see of a house) and phase 3 (how houses change). External register.
5. **Registers updated:** sourced figures as rows in `docs/market_research/ASSUMPTIONS.md` and `docs/institutional/knowledge_map.md`; the working research docs under `docs/market_research/`; the sample and joint as machine-readable artefacts the run draw consumes.
6. **Report to the director, plain English:** N, the curve, which quantities carry the variance, the three or four corners the sample found that the old four-node/thirteen-customer world could never have contained, and where the data forced a choice.

Charts diagnose and communicate; numbers prove.

## 4. Non-negotiables

- **Generation and validation from separate sources.** Generate from the English Housing Survey, the EPC register (open data, MHCLG) and Census 2021/22 (accommodation type, central-heating fuel including none). Validate usage against the DESNZ household-level consumption sample the machine already holds, stating honestly that its property attributes are partly EPC-lineage so the separation is imperfect. Validate ceilings against published trial and installation data (MCS installation statistics for PV; the published flow-temperature trial results; installation-programme evaluations for insulation), never against the SIM's own physics.
- **No fabricated coefficients.** Every saving, yield and distribution traces to a published source; where none exists — roof geometry beyond flat-vs-house and orientation is the expected gap — register it as a gap with its consequence, not a number.
- **The rated-versus-in-use gap is modelled, not ignored.** Published savings for insulation and the EPC's modelled consumption both overstate what meters show; the ceiling carries the in-use figure with the rated figure beside it, cited.
- **Wall placement:** everything in §3.3 is SIM truth. Nothing here builds company-side inference; phase 2 defines the observables and a later programme builds the inference. Run the epistemic verifier as normal.
- **No people-side mechanics.** Where a ceiling needs a people input, leave a named empty slot.
- **This ruling registers phases 2 and 3; it does not authorise them.**

## 5. Priority and sequencing

Product (a knowledge page and a run-draw artefact), P1, drawable now. File scope is disjoint from everything in flight except the existing premise-population and fabric-physics modules it extends — extend them, do not fork a parallel generator ("concept has one home"). It does **not** depend on the weather ruling landing; it depends only on the HadUK pull, which that ruling puts first. If the fan-out bound allows, run alongside the weather work; if not, the weather pull outranks this because of its 72-hour token clock.

## 6. Risk

**What it touches:** the premise-population and fabric-physics modules (SIM side), new research and knowledge files, a new run-draw artefact. Not billing, not the wall, not company code.
**Blast radius:** any current run that draws premises — the extended joint must reproduce the existing marginals to the same tolerance the existing tests enforce (they already exist; keep them green), so nothing published moves unless a fidelity finding says it should, decided blind to P&L.
**Probable failure modes:** (a) the similarity test run on inputs instead of outputs, producing a sample that matches every marginal and misses the joint corners — forbidden in §1; (b) a segmentation smuggled back in as archetypes — forbidden in §1; (c) people-side mechanics creeping in through uptake or mileage — §4; (d) ceilings quoted at rated rather than in-use — §4; (e) the page thinning to machinery — the knowledge canon's DoD 0 applies: the page must genuinely explain, and if the mechanics threaten the content, the content wins.

## 7. WORK THIS CREATES

- Extension of the premise joint with the §3.1 quantities, anchored, marginals-preserving.
- The space-filling sample, the output-similarity test, the two coverage curves, and N.
- Per-house ceilings on the seven phase-1 levers, current-settings draw, house-driven CLV basics.
- One knowledge page (full depth) + two stubs.
- Register rows and research docs.
- Registration of phases 2 and 3 as decided-not-authorised, with their scope from §2.1.
- One plain-English report to the director.
