# Current Priorities

Last updated: 2026-07-01 -- Gaps 1 and 2 closed (Phases MS and MT). Coverage sprints continue.

## Now (active this session)
Phase MV proposed (Coverage Depth Sprint CXX). Opt-out window expires 14:46 UTC 2026-07-01.
Forward: assess Human Simulation Layer (Gap 3) as next big capability phase.

## Real capability gaps

### Gap 1 -- Real Forward Curve [CLOSED -- Phase MS]
NBP/EPEX term structure using real published seasonal forward strips (2016-2025).
seasonal_calibration.json now data-derived from Elexon SSP + TTF proxy. Gas Dec 1.294 (was 1.20).

### Gap 2 -- I&C Triad Demand Curtailment [CLOSED -- Phase MT]
Triad notification book wired to 25% load reduction in settlement for I&C HH customers.
build_triad_alert_set (SSP>80 + Triad season + SP 33-39) + make_triad_aware_shape_fn live.

### Gap 3 -- Human Simulation Layer [OPEN -- LARGE / MULTI-PHASE]
What: docs/vision/HUMAN_SIMULATION_LAYER.md calls for 4-dimension customer modelling:
physical (property/EPC/appliances), economic (income/credit), behavioural
(payment/switching propensity), emotional (satisfaction/trust). Currently 295 customers
in 5 segments -- no physical property model, no income dimension, no EPC/EV/heat pump
interaction with demand. Segment-archetype not person-level.
Not done: Dimensions 1 (physical) and 2 (economic) -- 3 and 4 partially addressed by
churn/satisfaction models but not wired to physical/economic state.
First phase: property/EPC foundation (EPC rating -> insulation -> seasonal demand scalar).

## Backlog (lower priority)
- Dashboard: Flexibility revenue tab -- Phase AG built the data, needs wiring to site/
- ToU tariff depth: time-of-use pricing for HH smart meter customers
- Bad debt stress test: does bad_debt_provision feed back into capital model?
- Human Simulation Layer Dim 2: income/credit score -> payment propensity (after Dim 1)

## Recently completed real capability
- Phase MS (2026-07-01): Real NBP Forward Curve -- seasonal multipliers data-derived
- Phase MT (2026-07-01): I&C Triad Demand Curtailment -- wired to settlement
- Phase IC area: NL query, invoicing, 4-section live site, full regulatory stack
- 303+ company modules, 13,033 tests, net margin GBP 6.17M on live 2016-2025 data
