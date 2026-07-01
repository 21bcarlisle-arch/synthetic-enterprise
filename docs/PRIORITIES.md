# Current Priorities

Last updated: 2026-07-01 -- reset after coverage sprint loop diagnosis (Phase IC to MR)

## Now (active this session)
STOPPED: Coverage Depth Sprint loop -- 118 sprints ran since Phase ID. Stopping.
Next real work: Real forward curve (see below). Proceeding in 4h unless redirected.

## The three real gaps (unbuilt capability, not test coverage)

### Gap 1 -- Real Forward Curve [HIGH PRIORITY]
What: NBP/EPEX term structure using real published forward prices instead of the
current synthetic curve. Without this, every hedging and pricing decision the company
makes is calibrated against made-up prices -- the key risk model input is fabricated.
Not done: sim/forward_curve.py uses a synthetic generator. No real published data.
Suggested phase: Phase MS -- Real NBP Forward Curve: ingest published seasonal
forward strips (2016-2025), fit a term structure model, replace synthetic curve.

### Gap 2 -- I&C Triad Demand Curtailment [MEDIUM PRIORITY]
What: When Triad notifications go out, the I&C customers should actually reduce
load in the sim. Currently triad_notification_book records alerts but demand model
ignores them -- load never drops in Triad windows.
Not done: sim/demand_model.py and settlement run have no Triad response logic.
Suggested phase: Phase MT -- Triad Response in Settlement: wire triad alerts to
a demand-reduction event in hh_consumption/run_segments for I&C customers.

### Gap 3 -- Human Simulation Layer [LARGE / MULTI-PHASE]
What: docs/vision/HUMAN_SIMULATION_LAYER.md calls for 4-dimension customer modelling:
physical (property/EPC/appliances), economic (income/credit), behavioural
(payment/switching propensity), emotional (satisfaction/trust). Currently 295 customers
in 5 segments -- no physical property model, no income dimension, no EPC/EV/heat pump
interaction with demand. Segment-archetype not person-level.
Not done: All four dimensions.
First phase: property/EPC foundation (EPC rating -> insulation -> seasonal demand).

## Backlog (lower priority)
- Dashboard: Flexibility revenue tab -- Phase AG built the data, needs wiring to site/
- ToU tariff depth: time-of-use pricing for HH smart meter customers
- Bad debt stress test: does bad_debt_provision feed back into capital model?

## Recently completed real capability (pre-sprint-loop)
- Phase IC area: NL query, invoicing, 4-section live site, full regulatory stack
- 303+ company modules, 12,960 tests, net margin GBP 1.24M on live 2016-2025 data
