# [ADVISOR-STAGED] DISCOVER: Premise Fabric Physics — the demand engine under every home and business

**Date:** 2026-08-03 · **Origin:** Director-approved in live conversation (advisor drafted, director said stage it)
**Proportionality:** Large DISCOVER/FRAME. No BUILD authorised by this doc.
**Scope:** DISCOVER + FRAME only. Deliverables are a discovery document, framed atom proposals for the maturity map, and a two-level-test harness spec. Any build waits for its own draw under normal governance.

---

## 1. Context anchor (self-contained)

A director house-usage review (2026-08-03, rendered from origin) ran the published premise-level demand against Spec 003's two-level test (spiky homes, smooth crowds). Verdict, with evidence:

- Per-house half-hourly exists for only 3 residential homes (C7/C8/C9) + 4 I&C, electricity only. **Gas has no premise-level trace at any resolution** — monthly totals from one national seasonal shape.
- **Level 1 FAIL (homes too smooth):** median period-to-period change 0.008–0.012 kWh against a ~0.7 kWh mean (~1.5%); day-vs-next-day shape correlation 0.97; no half-hour below 0.05 kWh in ten years (no empty house, no holidays); repeating rescaled-fraction values betray a deterministic base shape, not appliance stochasticity.
- **Level 2 FAIL (crowd doesn't smooth):** C8–C9 correlation 0.95 (near-clones); identical block timing across homes; 3-home aggregate peak/mean 5.9 vs 5.7 for one home — aggregation smooths nothing. Annual totals within 8% of each other (11.8–12.8k kWh) — no between-home scale variation.
- Monthly gas/elec shape and scale for dual-fuel homes is genuinely good (gas 13,029 kWh/yr, 4.6× winter ratio) — the defect is premise-level timing and diversity, not annual levels.

Director's framing for the fix (verbatim intent): *"a robust model that can take a simple number of available variables to create accurate elec and gas usage based on local weather inputs and structural features of the property available via EPC or other data."* Fabric drives the level and the when; segments/occupants/tariffs/behaviours layer on top to give actual demand.

## 2. The objective

Design (not build) a **two-layer premise demand engine**:

**Layer 1 — fabric physics (per premise, weather-driven).** A small set of structural variables — the kind derivable from an EPC or equivalent — determines a heat loss coefficient and a thermal mass, which with local weather (temperature, sun, wind from the existing weather nodes) produce half-hourly gas and electricity demand at standard occupancy. Fabric fixes both the annual level AND the intra-day character: heavy solid-wall homes run long and smooth; light modern homes cycle and spike. LCTs (heat pump with temperature-dependent COP, EV, PV by orientation, battery) rewire the electricity side.

**Layer 2 — behaviour (separable, on top).** Segments, occupancy patterns, setpoints, heating hours, tariff-driven scheduling, income constraints (including the real prebound effect: fuel-poor homes under-heat, consuming LESS than physics predicts). This layer must be cleanly separable so the existing segment/engagement/psychology work plugs in without entangling the physics.

**The wall mechanism (strategically central):** SIM ground truth = actual fabric + actual behaviour. The company observes only EPC-class data — which is itself an imperfect estimate of real fabric — plus meter reads and weather. The EPC-vs-actual gap becomes a genuine, real-world belief-vs-truth mechanism on the wall, same class as the payment triad. The company may then *infer* per-premise thermal parameters from telemetry through the wall (see appendix item B), and the inference gap is measurable.

## 3. Hard requirements on any framed design

1. **Passes the two-level test the current traces failed.** Individual homes: stochastic half-hour texture, near-zero troughs, away-days, weekday/weekend life, day-to-day correlation well below 0.97. Crowds: diversified timing so aggregation genuinely smooths (aggregate peak/mean falls materially as N grows). Realistic-but-imperfect is the bar; too clean fails.
2. **Between-home variation in both scale and timing** — annuals spanning the real UK range, driven by fabric + occupancy, not one shape rescaled.
3. **Gas gets premise-level treatment**, at whatever resolution the design justifies (daily may be defensible for gas; say so and anchor it).
4. **Anchored and independently validated (independence rule):** RdSAP/SAP methodology parameterises the fabric physics from EPC fields; NEED (EPC-linked actual metered consumption) calibrates levels; SERL (half-hourly smart data linked to EPC/survey) calibrates timing and texture. Validation must use anchors the generator did not, or the check is theatre.
5. **Calibrated blind to P&L** (R12/R13). Baseline fidelity change, decided on fidelity grounds only.
6. **Coheres with existing work, doesn't fork it:** the weather engine (WEATHER_PHYSICS_HIERARCHY), the population coverage design (DIRECTOR_STEER_POPULATION_COVERAGE_DESIGN), the segmentation/engagement calibration, and the ratified model-on-a-page. Frame where fabric archetypes sit relative to the existing household archetype dimensions.
7. **Mission link stated:** this fabric model is the personalisation engine of the carbon mission — which homes gain from insulation, heat pump, PV, or time-shifting is HLC × weather × occupant arithmetic, and £/tCO₂e falls out of it. Savings still count only from reduced or time-shifted usage, never discounting.

## 4. Inspiration appendix — external maths, adopt/adapt/reject freely

The director reviewed an external specification sketch and approved passing these techniques through as discovery inspiration. **They are candidates, not decisions.** Evaluate each on merit; record adopt/adapt/reject with reasons. Where we already built the equivalent (epistemic wall, typed adapters), record convergence as evidence, not as new input.

A. **2R2C grey-box thermal model** — second-order lumped RC: indoor-air node (fast, gives cycling/spikes) + building-mass node (slow, gives fabric character). Parameters: R_ia, R_im, C_i, C_m; inputs: heating Φ_h, solar Φ_s, occupant gains Φ_p, ambient T_a. The standard building-physics form; the leading candidate for Layer 1's core.

B. **Unscented Kalman Filter parameter inference behind the wall** — the company recursively estimates each premise's R/C parameters from noisy meter telemetry + weather, never seeing ground truth. Turns fabric discovery into a measurable coupled belief-vs-truth gap.

C. **GARCH(1,1) conditional variance on price forecast errors** — volatility clustering: calm stays calm, crisis weeks cluster. A mechanism-level candidate for the named spike-tail defect (max £574 vs real £4,038; negatives 0.013% vs 2.241%) — evaluate against the worst-cell VaR verdict standard, not averages.

D. **Non-linear price S-curve on net load AND ramp rate** — endogenous spikes when the grid tightens fast; refinement candidate for the recalibrated price engine.

E. **Aggregation weightings** — population-weighted temperature, capacity-weighted wind, cumulative HDD windows for gas storage/linepack drawdown. Check against what the weather hierarchy already does; adopt where it improves the national roll-up.

F. **Premise-level cost stack** — DUoS bands, TNUoS, line-loss factors per half-hour for true per-home margin. Register for the value-cycle epoch; note where it would land.

G. **MILP flexibility optimisation** (pre-heating thermal mass, EV/battery scheduling against tariff over a rolling 48-period horizon) — **register, sequence later.** This is the personalisation/carbon engine itself and requires Layer 1 to exist first. Do not build it in this pass.

Explicitly NOT passed through (director: "it has branded a little... don't go off track"): real-DCC data acquisition, beta trials, VLP/SaaS commercialisation phases, and any cost-arbitrage-first framing. Non-commercial mission framing stands.

## 5. Deliverables

1. A discovery document: the two-layer model design, parameter set (the "simple number of available variables"), anchor mapping (which RdSAP/NEED/SERL facts pin which parameters), the wall/observability design, gas treatment, and the adopt/adapt/reject verdicts on appendix items A–G with reasons.
2. Framed atom proposals for the maturity map (fabric physics core; premise trace generator; company-side thermal inference; the belief-vs-truth gap metric), with dependencies on existing weather/population/segment atoms stated.
3. A two-level-test harness spec: the falsifiable statistics (per-home texture, day-to-day correlation, trough behaviour, aggregate-smoothing curve vs N, between-home spread) that any future build must pass — so an Expert Hour can fail it.

## 6. Decided vs open

**Decided (director):** two-layer separation; fabric-first; EPC-class variables as the company-visible parameter set; appendix passed as inspiration only; commercial framings excluded; DISCOVER/FRAME only.
**Open (for the discovery to answer):** 2R2C vs simpler/richer forms; gas resolution; how fabric archetypes intersect the existing archetype dimensions; whether SERL access is practical or whether published SERL statistics suffice as anchors; where the UKF inference atom sits in epoch sequencing.

## 7. Risk & blast radius

Doc-only this pass: no code, no map cell moves, blast radius zero until framed atoms are proposed through normal governance. Main risks at frame time: (a) entangling Layer 1 and Layer 2 (mitigate: separability is a hard requirement); (b) anchor circularity (mitigate: independence rule stated above); (c) scope bloom into the MILP engine (mitigate: item G explicitly sequenced later). This supersedes nothing; it extends the household-archetype and weather programmes and should be reconciled with, not layered over, the population coverage design.
