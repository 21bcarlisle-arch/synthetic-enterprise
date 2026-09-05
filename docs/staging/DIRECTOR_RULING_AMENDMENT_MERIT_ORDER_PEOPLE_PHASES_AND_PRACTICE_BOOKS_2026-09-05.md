**Severity:** RECORDED · **Lane:** W2_customer_generator + W1 weather + run-mix curriculum · **Priority:** P1 — amends rulings staged today, before they are drawn · **Proportionality:** reversible / narrow

# [DIRECTOR-RULING][ADVISOR-STAGED] Amendment: the merit order re-cuts the people phases, and four practice books (2026-09-05)

**Amends** `DIRECTOR_RULING_PEOPLE_MONEY_AND_WHO_THEY_ARE_PHASE1_2026-09-05.md` (§2.1–2.2, §3, §4), `DIRECTOR_RULING_HOUSING_VALUE_CEILING_AND_SAMPLE_PHASE1_2026-09-05.md` (§5) and the run-mix item those rulings reserve for the director. **Where this conflicts with those files, this governs.** Recorded as a separate document so the staged files stay byte-stable for the bridge.

Decided by the director in the advisor channel this afternoon, after the CLV reference work (`ADVISOR_REFERENCE_CLV_DRIVERS_THESIS_AND_SENSE_CHECK_2026-09-05.md`). Director, verbatim: *"Good management of renters and won't pay (but can) can create as much value for a given starting portfolio as other value add."* And: *"I'm not sure we've modelled the phases of this well enough."*

## 1. The finding that drives the amendment

The CLV reference model makes value lexicographic — pays → stays → size and sign of the margin bet → value-add. Read against the three phase-1 rulings, the fidelity that matters most for **managing a given book well** sits mostly on the people axis and mostly in the parts phase 1 deferred:

- **Collections responses** — how a household answers a payment plan, a right-sized direct debit, a tone, a PAYG proposal — were people phase 2. Without them the company can observe debt but cannot practise managing it, and the stressed standard-credit household (−£800 badly managed, break-even well managed) is the largest per-customer swing in the book.
- **Moves and change of tenancy** were people phase 3 — and today's SIM emits no move event at all (`simulation/life_events.py`; the change-of-tenancy register has no caller). Renters churn by moving, not switching; for them the unit of value is the meter point, kept on a deemed contract across occupiers. A third of the book's real dynamics is absent.
- **Geography carries socio-demographics and asset potential together** (rural = detached, drive, roof, off-gas, older, owner, higher income), so the people joint keyed on small-area geography — already in the people ruling — is also how EV and battery potential gets its people-side correlation. Nothing changes there; it is restated so the housing sample's asset outputs are not read as house-only.
- **Better-than-average shape is money to play with.** A customer whose load is flatter or off-peak is cheaper to supply and easier to keep happy; shape stays a coverage output on the housing side, not a recorded attribute. The earlier suggestion to demote solar to an attribute is **withdrawn**; instead §4 orders the fidelity *effort*.

## 2. The people phases, re-cut along the merit order (supersedes people ruling §2.1)

**Phase 1 — pays and stays.** Everything already in phase 1 (tenure, composition, occupancy versus typical, income and fuel poverty, three-way payment method, credit risk, typical presence, people-driven usage) **plus**:
- **collections responses** — the household's response to a payment plan, a DD re-size, a tone, a PAYG proposal, a final-bill demand; anchored where anchors exist (the Bacs/DESNZ payment anchors and the tone/framing susceptibility already in the machine; Ofgem's debt-and-collections statistics), curriculum-slotted where they do not (the can't/won't split stays a director value);
- **vulnerability and disclosure** — who carries a flag, who tells the supplier, and when; the flag gates PAYG conversion and disconnection by rule;
- **moves and change of tenancy** — move-out and move-in as events with real rates by tenure and age; the property stays; deemed contract on the incoming occupier; the outgoing occupier's final bill as a collectable; the existing change-of-tenancy register wired to a real emitter;
- **engagement archetype** (forward from phase 2) and **expected length of stay** (add) — both merit-order gates.

**Phase 2 — shape and attitudes.** Price elasticity and the stability-versus-time-of-use preference; contact propensity and channel; presence residuals (working hours, holidays, shift patterns, working from home) and the shape they make; **consent to control** — the attitudes that grant or withhold permission over an EV or a battery, which is where geography's asset potential becomes value or does not; green stance and trust.

**Phase 3 — change.** Life events and income shocks (extending the existing stream), children arriving and leaving, unprompted device purchases, and the value-add term: willingness to buy kit or services, kept distinct from willingness to appreciate being saved money and carbon.

Phases 2 and 3 remain decided and registered, not authorised.

## 3. Four practice books (adds to the run-mix item reserved for the director)

The run-mix set the machine proposes for ratification must include, alongside the population-proportional re-weighting for the market reconciliation, four books each designed so a life can be scored on **one** management skill:

1. **The stressed book** — heavy standard-credit and prepayment, income stress, mixed smart/dumb metering, a realistic vulnerability rate. Scored on bad debt and cost to serve against the reference's badly-managed / well-managed bounds.
2. **The renter book** — private-rented flats, high move rates, short stays, deemed contracts. Scored on onboarding cost, first-month DD accuracy, final-bill collection, and margin per meter point across occupier changes.
3. **The cold-winter big-house book** — large, old, weather-sensitive fabric on fixed deals through a cold, still, expensive winter. Scored on forecast/volume risk and hedge-shape error.
4. **The asset-rich book** — owners with roofs, drives, EVs and batteries, engaged enough to grant permission. Scored on shape value captured and on the loyalty effect measured, not assumed.

Each book is a curriculum instrument: the mix and its true probability are the director's, decided blind to P&L; the company never knows which book it is in; fitness weights every life by true probability so no practice book dominates expected value.

## 4. Fidelity effort in merit order (applies to all three phase-1 rulings)

Where effort must be rationed, spend it in this order, and say which rung a piece of work serves:

1. Payment, collections and vulnerability dynamics (people).
2. Moves and change of tenancy (people; the register exists, the emitter does not).
3. Bill accuracy and the shape of the year — persistence and cold-still synchrony (weather), fabric gradient and heating fuel including the electric-heat tail (housing), engagement (people).
4. Forecast and hedge fidelity at portfolio level — cells, gradients, the estimated-read population.
5. Assets and permission — roof, parking, tenure gate, consent — for phase two's bias of the mix.

Solar irradiance stays in weather phase 1 (it is one data pull, and PV-plus-battery shape is rung 5's input); PV ceilings stay in the housing sample's outputs; the *effort* on them is rung 5.

## 5. Risk

Touches: the people and housing rulings' scope, not their mechanism; the run-mix proposal; the life-event emitter and the change-of-tenancy register (SIM side, new events). Blast radius: any run that draws households gains move events — marginals must still recover; published figures move only through a declared fidelity change. Failure modes: (a) collections *responses* built as company-side policy rather than SIM-side household truth — they are truth, the policy is the company's and separate; (b) moves built without the deemed-contract mechanic, which is what makes renters valuable at all; (c) a practice book leaking into the company's knowledge of which book it is in.

## 6. WORK THIS CREATES

- People phase 1 scope extended per §2 (collections responses, vulnerability and disclosure, moves and change of tenancy, engagement, length of stay); phases 2–3 re-scoped.
- The move emitter wired to the existing change-of-tenancy register, deemed contracts on move-in.
- Four practice books added to the run-mix proposal for ratification.
- The fidelity-effort ordering recorded and cited by each phase-1 report.
