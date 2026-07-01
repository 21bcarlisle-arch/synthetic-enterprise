# Current Priorities

Last updated: 2026-07-01 -- Sprints STOPPED. Direction: Human Simulation Layer (Gap 3).

## CRITICAL: NO MORE COVERAGE SPRINTS
Coverage sprints (phases LQ through MU, 95+ sprints) are complete. Test count: 14,460.
All future phases must close a real capability gap from the list below.
Do NOT propose another coverage sprint. Do NOT read the old sprint pattern and repeat it.

## Now (active this session)
Phase MW proposed (Income Stress -> Observed Payment Behaviour). Opt-out ~2026-07-01T23:10Z.
If MW proceeds: income_stress (SIM ground truth) cascades into observable payment records.
After MW: Dim 1 physical model (property/EPC -> seasonal demand scalar).

## Real capability gaps

### Gap 1 -- Real Forward Curve [CLOSED -- Phase MS]
NBP/EPEX term structure using real published seasonal forward strips (2016-2025).
seasonal_calibration.json now data-derived from Elexon SSP + TTF proxy. Gas Dec 1.294 (was 1.20).

### Gap 2 -- I&C Triad Demand Curtailment [CLOSED -- Phase MT]
Triad notification book wired to 25% load reduction in settlement for I&C HH customers.
build_triad_alert_set (SSP>80 + Triad season + SP 33-39) + make_triad_aware_shape_fn live.

### Gap 3 -- Human Simulation Layer [OPEN -- LARGE / MULTI-PHASE]
4-dimension customer modelling: physical (property/EPC/appliances), economic (income/credit),
behavioural (payment/switching propensity), emotional (satisfaction/trust).
Phase MV closed part of Dim 2 (income_stress enum + economic life events).
Phase MW closes Dim 2 further (income_stress -> observable payment behaviour).
Next after MW: Dim 1 physical (property/EPC foundation -> seasonal demand scalar).

### Gap 4 -- Churn Blind Miss Rate [OPEN]
Board risk shows 4/6 departures (67%) not forecast. Company churn model needs calibration
against observed payment behaviour and contract near-expiry signals.
Addressable after Gap 3 Dim 2 (payment behaviour) is closed.

### Gap 5 -- Gas Segment ROC [OPEN]
Gas legs show -0.7x ROC (net GBP -134,790 on GBP 187,116 capital).
Options: exit gas, gas-specific tariff uplift, gas hedging model improvement.

## Backlog (lower priority)
- Dashboard: Flexibility revenue tab -- Phase AG built the data, needs wiring to site/
- ToU tariff depth: time-of-use pricing for HH smart meter customers
- Bad debt stress test: does bad_debt_provision feed back into capital model?

## Recently completed real capability
- Phase MV (2026-07-01): Economic Life Events -- income_stress enum, job_loss/income_recovery/new_baby/retirement
- Phase MT (2026-07-01): I&C Triad Demand Curtailment -- wired to settlement
- Phase MS (2026-07-01): Real NBP Forward Curve -- seasonal multipliers data-derived
- 14,460 tests, net margin GBP 6.17M on live 2016-2025 data
