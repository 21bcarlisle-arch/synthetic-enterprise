**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: the annual net-export level carries all of 2022's bias but only half the crisis gain, and outside the crisis it beats the real shape (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in `docs/staging/records/WORKER_PREREG_HOW_MUCH_OF_NET_EXPORTS_GAIN_ON_THE_PRICE_LEG_IS_THE_ANNUAL_LEVEL_2026-11-24.md`
(`1545ed8b0`) and promoted to origin before the `am` arm ran. Probe `/var/tmp/wpc_am/measure_am.py`, sha256
`f29e1f55…`, unchanged. Worktree at origin `1545ed8b0`. **Nothing in `sim/` changes.***

## Outcomes (monthly, demand-weighted, £/MWh; MAE, bias)

| Row | Pre-crisis | Crisis | Post-crisis | Post ex-2025 | 2022 bias | 2025 bias | Half-hourly MAE |
|---|---|---|---|---|---|---|---|
| R base (no net export) | 4.65, +1.33 | 18.46, −8.20 | 5.82, +4.08 | 6.23, +5.85 | −17.85 | −1.24 | 30.990 |
| R ne (real half-hourly) | 4.62, +0.83 | 13.29, −5.69 | 5.99, −0.30 | 4.91, +2.11 | −8.50 | −7.52 | 31.126 |
| **R am (annual level)** | **4.45, +0.29** | **16.16, −6.01** | **5.58, −0.91** | **4.64, +1.33** | **−8.43** | **−7.64** | **30.854** |
| W base | 4.99, +2.27 | 17.80, −10.08 | 5.83, +4.83 | 5.40, +4.55 | −18.48 | +5.66 | 31.334 |
| W ne | 4.90, +1.95 | 12.79, −7.41 | 5.15, −0.01 | 4.86, +0.25 | −8.40 | −0.80 | 31.398 |
| **W am** | **4.58, +1.16** | **15.32, −7.76** | **4.16, −0.30** | **3.97, −0.08** | **−8.68** | **−0.96** | **31.182** |

R am's coefficients are 0.5492 / 0.9365 / 2.1667, against ne's 0.524 / 0.998 / 1.7427. `synthetic_price` on the
fitted coefficients agrees with the probe to within 5.7e-14. The year-total assertion passed.

## Predictions, beside the outcomes

| # | Prediction | Outcome |
|---|---|---|
| AM-P0 | `ne` reproduces `c89b0910f` exactly | **held** (run before filing) |
| AM-P1 | Crisis MAE ≤ 14.99 (level share ≥ ⅔) | **wrong**: 16.16, a level share of 44% ((18.46 − 16.16) / (18.46 − 13.29)) |
| AM-P2 | 2022 bias within ±3 of −8.50 | **held**: −8.43 |
| AM-P3 | Post bias inside ±2 | **held**: −0.91 |
| AM-P4 | Pre MAE within ±0.30 of 4.62 | **held**: 4.45 |
| AM-P5 | Half-hourly MAE below 31.126 | **held**: 30.854, also below base's 30.990 |
| AM-P6 | 2025 bias within ±2 of −7.52 | **held**: −7.64 |
| AM-P7 | W crisis MAE ≤ 14.46 | **wrong**: 15.32, a level share of 50% |

Six of eight held, and both misses are the same miss. My reasoning said the day-to-day shape would be small in
money. In the crisis it is not: it carries half of the MAE gain.

## What it means

- **Rule (b) fires.** R's crisis MAE is 16.16, inside (14.99, 16.46]. The shape carries a material part of the
  crisis gain, so a level-only forward build would leave about £2.9/MWh of crisis monthly MAE on the table.
- **The level carries the bias.** 2022's bias, the post-crisis bias and 2025's bias are each within £0.7 of ne's,
  and every regime's bias is within £0.6. The exception is 2021, where am is −5.56 against ne's −4.21. The
  shape barely moves the leg's level. It moves the spread of the crisis's monthly errors around that level.
- **Outside the crisis, the level does better than the real shape.** Pre-crisis MAE is 4.45 against 4.62
  (W: 4.58 against 4.90). Post-crisis MAE is 5.58 against 5.99 (W: 4.16 against 5.15). The half-hourly fit also
  improves. So in calm years the real shape adds noise the one-leg form cannot use. This was not predicted. It
  is stated here, not attributed.
- **What that means for a forward build.** An annual level drawn from FES is the right term for calm years. A
  crisis-year shape is needed only where the spread between GB and its neighbours is itself the shock, as in
  2022. **I cannot yet say** whether the crisis shape that matters is month-level (exports in summer 2022 and
  imports that winter) or day-level. A month-mean arm would separate the two, and its answer decides whether
  the forward shape can be seasonal.

## Next, still item 4

1. **The month-mean arm.** Each month's mean net export replaces the half-hourly series. One variable against
   this record's am and ne rows, with its prediction filed first. If the month level recovers most of the crisis
   gain, the forward shape is a seasonal profile around the FES annual level, not a residual-demand conditioning.
2. Unchanged from the forward net-flow note: rerun build-terms B1-B3 on SAP plus net export (on the am form,
   given its calm-year advantage), and R's 2025 residual against the AGWS windows finding.

Reverse: delete this record.
