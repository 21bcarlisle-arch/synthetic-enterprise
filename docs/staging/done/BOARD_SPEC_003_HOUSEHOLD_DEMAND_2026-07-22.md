# BOARD SPECIFICATION 003 — Household demand (blind practitioner spec, VERBATIM)

**Type:** [ANCHOR — verbatim + reconciliation instruction]. Blind-drafted. **Do not edit the board's text.** Reconcile line-by-line against W1_5 premise demand (+idiosyncratic noise), the meter unhappy-path machinery, and the generator structure, per the standing steer; battery joins the oracle.

**Advisor flags (verify):** (a) §3's two-level test (spiky individual traces + smooth aggregates, right at BOTH levels simultaneously) is the likely headline honest gap — W1_5 was built aggregate-first with mean-1 lognormal noise; whether individual half-hourly traces are kettle-spike/zero-visiting realistic or smoothed scalings is exactly what to audit and report without flattery. (b) The meter-estate imperfection ("demand as the supplier experiences it") converges with the built unhappy-path physics — cite it. (c) Heating-season as a behavioural SWITCH with distributed start dates, zeros/voids/tenancy absences, and the gas 3–4× scale with several-fold winter/summer ratio are concrete checkable claims. (d) Battery item 11 (clean elasticity) cross-references Spec 006's disengaged majority — reconcile jointly.

---
---

# POESYS BOARD — PRACTITIONER SPECIFICATION 003
## Household demand: what drives a home's energy use, and what realistic demand looks like

*Issued blind under Movement 2 of Sitting 001. The Board has not examined any demand model as built and asks nothing about it. The Executive reconciles line by line to Movement 3.*

*The Chair orchestrates. The Brain leads on the driver decomposition; the Visionary on the variation between and within homes — because that variation is where any personalisation thesis lives or dies; the Worrier on the tails; the Doer on the two-level test; the Child asks why two identical houses have different bills, and the answer is most of this document.*

---

## 1. The drivers, decomposed honestly

Annual demand separates by fuel, because the physics differ.

**Gas (or whatever fuel heats the home) is mostly building physics filtered through behaviour.** The physics — floor area, age and construction, insulation and glazing, heating system type and efficiency — set the *envelope*: the heat the building loses per degree of inside–outside difference. Behaviour picks the position within it: thermostat setpoint (a single degree is worth roughly ten percent of heating energy), heating hours and setback patterns, which rooms are heated, whether windows leak deliberately. Then occupancy scales hot water and cooking. The veteran's decomposition for a heating fuel: physics explains the most variance *across* the housing stock; behaviour explains the most variance *between similar homes*; weather explains the most variance *within one home across time*.

**Electricity (non-heating) inverts the ranking.** Occupancy and appliance stock dominate — how many people, how many hours at home, what they own (tumble dryer, electric shower, old freezer, EV) — with the building itself a minor character. The exceptions that matter: electrically heated homes, whose electricity behaves like gas (§4), and low-carbon-tech homes, where an EV or heat pump can double a household's electricity overnight.

**And a residual that must stay random.** After physics, occupancy, appliances, behaviour and weather, real homes retain genuine day-to-day noise — variable occupancy, guests, illness, whim. A model that explains everything has overfitted reality.

## 2. Variation: between similar homes, and within one home over time

**Between physical twins: the famous factor of two to three.** The most replicated finding in domestic energy research is that physically identical homes — same street, same construction, same heating system — routinely differ in heating consumption by a factor of two, sometimes three. The occupants are the variable. Any simulated population in which similar homes cluster tightly around their physics-predicted demand has deleted the single best-documented fact in the field — and with it, the entire premise that knowing a household beats knowing its house.

**Across the whole book: a heavy right tail.** Consumption is not symmetric around the typical value. The distribution is right-skewed: a long tail of large, old, hard-to-heat, fully occupied homes consuming several multiples of the median, and a fat mass of small flats and single occupants below it. Means sit above medians. A book of near-typical consumers with thin tails is not a GB book (the Worrier notes the commercial edge of this: the tail is where margin, debt risk, and abatement opportunity all concentrate).

**Within one home over time.** Even weather-corrected, the same household's annual consumption moves ten to twenty percent year on year — occupancy shifts, habits drift, kit degrades. And it moves *discontinuously* at life events: a baby, retirement, a shift to home working, a new EV, a boiler replacement, a lodger. These are steps, not trends. Plus the scheduled absences: holidays, and the void weeks between tenancies, when gas falls to pilot-light levels or zero. A per-home demand series with no steps, no dips, and no zeros has never met a household.

## 3. The half-hourly truth: spiky homes, smooth crowds

This is the section most simulations fail, so the Board states it bluntly.

**An individual home's half-hourly electricity trace is jagged, spiky, and frequently near zero.** A base load of perhaps 50–150 watts (fridge, standby), punctured by short violent spikes — a 3 kW kettle for two minutes, a 9 kW shower for eight, an oven cycling. Gas at the half-hour is nearly binary: a boiler firing hard in bursts, then off. **Smoothness is a property of aggregation, not of homes.** Sum a few thousand diverse households and the familiar profile emerges — morning ramp, daytime trough in working households, the 17:00–20:00 evening peak, the overnight floor — because diversity averages the spikes away.

The Doer's two-level test follows: **a credible model must be right at both levels simultaneously.** Individual traces must look like real smart-meter data (spiky, gappy, zero-visiting); the aggregate must reproduce the known class profiles, the weekday/weekend split (later, flatter mornings at weekends), the seasonal shape migration (winter evening peak taller and earlier as darkness falls), and the calendar oddities a veteran checks by reflex — the Christmas pattern, bank-holiday mornings. A model that produces the right aggregate by giving every home a scaled copy of the average curve has faked the crowd by falsifying every individual in it; the reverse failure — plausible individuals summing to an implausible system — is equally disqualifying.

**Realistic versus too-perfect, summarised:** too-perfect is smooth, symmetric, always-on, gap-free, and continuously responsive to temperature. Realistic is spiky at the half-hour, skewed across the book, stepped across years, zero-visiting, seasonally switched (heating comes on for the season as a decision, not a gradient — the "heating season" starts on different dates in different homes, itself a behavioural distribution), and observed through an imperfect meter estate — missing intervals, failed communications, estimated reads on the legacy stock. The measurement imperfection is part of demand as the supplier experiences it, and Spec 006's information wall begins here.

## 4. Gas versus electricity shape, side by side

- **Scale:** a typical dual-fuel home burns roughly three to four times more gas than electricity annually.
- **Seasonality:** gas is extreme — winter months run several-fold summer months, since summer gas is hot water and cooking only. Electricity is mild — winter perhaps half as much again as summer, driven by lighting and darkness, not heating.
- **Intraday:** gas peaks hardest in the **winter morning** — the recovery burn after overnight setback — with a broad evening plateau. Electricity peaks in the **early evening year-round**, cooking and lighting stacked on returning occupants.
- **Temperature sensitivity:** gas is steeply weather-driven (Spec 002's hockey stick lives here); non-heating electricity is only weakly so.
- **The crossover cases:** electrically heated homes (storage heaters on legacy off-peak metering, resistive panels, heat pumps) make electricity behave like gas — night-charging shapes, deep winter sensitivity — and their absence from a simulated book removes a small but distinctive and often financially stressed population. EV homes add a new overnight mountain to the electricity shape.

## 5. The battery — what makes a simulated demand model NOT credible

1. **Physical twins that consume alike.** No behavioural factor-of-two-to-three between similar homes; physics predicting demand too well.
2. **Smooth per-home curves.** Individual half-hourly traces resembling scaled average profiles — diversity's smoothness stolen by the individual.
3. **No zeros, voids, or absences.** No holidays, no empty tenancies, no summer gas floor; every home always on.
4. **Continuous temperature response per home.** No heating-season switch, no setback behaviour, no distribution of season start dates.
5. **Seasonality ratios wrong.** Gas winter/summer materially below the several-fold reality, or electricity seasonality gas-like without electric heating to explain it.
6. **A symmetric book.** Consumption distributed thinly and evenly around the typical value; no heavy right tail; mean and median coincident.
7. **Frozen households.** Annual consumption static per home year over year; no life-event steps; no kit replacement.
8. **Mistimed or missing peaks.** No 17:00–20:00 electricity peak, no winter-morning gas spike, no weekend distinction, no seasonal migration of the evening peak.
9. **Perfect observation.** Every home metered half-hourly, no estimated reads, no gaps — the legacy meter estate and its estimation error absent (the seam into Spec 006, item 6).
10. **One level right, the other faked.** Aggregate profiles correct atop implausible individuals, or plausible individuals summing wrongly — the two-level test failed in either direction.
11. **Clean elasticity.** Households responding to price signals or messages with textbook responsiveness and no inattention, no non-response mass, no decline-and-never-act (the population Spec 006 calls the disengaged majority).

*The Chair, closing: the veteran's one-line summary — the average household does not exist, and a model is credible in proportion to how uncomfortable its individual homes would make a statistician who only ever saw the aggregate. Reconciliation line by line: met / partially met / absent / not applicable, with reasons, to Movement 3.*

*Signed for the Board — the Chair.*
