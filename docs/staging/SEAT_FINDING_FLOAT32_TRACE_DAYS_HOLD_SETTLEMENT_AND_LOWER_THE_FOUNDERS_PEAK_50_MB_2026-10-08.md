**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `founders-peak-float32-trace-day`

# Float32 trace days hold the settlement and lower the 160-founder peak by 50 MB

Follows `SEAT_FINDING_THE_FABRIC_TRACE_ALIVE_AT_THE_FOUNDERS_PEAK_2026-10-07.md` (`a0205bfbb`), which
found the trace alive at the peak and so movable only by a smaller day.

**Disposition at draw.** The duplicate-work note named `founders-slope-trace-alive-at-peak`. That
claim is the predecessor probe whose finding drew this item. It is a different question (timing) on the same
subject, so this item went ahead.

## Pre-registration (written before any leg, `/var/tmp/f32/PREREG.md`)

The legs were founders-only, 40 founders, budget 0.0, `--end 2019-12-31`, at `d58f64ced` (origin/main), with
`all_records` pickled at the return of `run_phase2b`. Arms D1 and D2 ran unpatched (`'d'`). Arm F forced
`fabric_demand_path.array` to `'f'`. D1 vs D2 is the placebo. The tolerance comes from the meter's own
resolution, a half-hourly register read to 0.001 kWh: every kWh field |F−D| < 0.0005; every GBP field
< 0.005; record count, keys and every non-numeric field identical. Prediction: kWh delta about 1e-6,
GBP < 1e-4. The 160-founder peak would be measured only if this passed.

## Result

- **Placebo:** D1 = D2 exactly (32,757 records, 0 fields differ). The run is deterministic.
- **F vs D:** 32,757 records each. 0 key-set differences and 0 non-numeric differences. 326,779 numeric fields
  moved. The largest moves: `consumption_kwh`/`daily_kwh` 0.0001, `treasury_cash_balance_gbp` 1.7e-5
  (cumulative), `net_margin_gbp` 2e-6, every other GBP field ≤ 1e-6. **Pass.** One correction to
  the prediction: the kWh delta is 0.0001, not 1e-6. The records round kWh to 4 dp, so a float32
  error of about 1e-7 flips the last rounded digit. That is still 5× inside the tolerance.
- **160-founder peak** (`ctl0_peak.py` with the typecode forced, untraced, sequential, swap 0 at both):

| | `'d'` | `'f'` |
|---|---|---|
| peak anon RSS | 1,896.9 MB | **1,847.1 MB** |
| series / day-arrays alive at the peak | 60 / 262,980 | 60 / 262,980 |
| max anon after the last free | 1,867.4 | 1,823.5 |
| largest sampler gap | 0.83 s | 0.68 s |

The saving is **49.8 MB**. Predicted: 262,980 × (464 − 256) B = 52.2 MB. The `'d'` arm read 1,893.6 MB
yesterday, about 3 MB of run-to-run spread, so one leg per arm is enough to place a 50 MB move. Per
settled customer-year this is about 0.09 MB/scy of the trace's 0.227, as the parent finding estimated.

## Landed

`simulation/fabric_demand_path.py` now builds each day as `array("f", …)`. The comment beside it says why
and what the precision check found. `tests/simulation/test_fabric_demand_path.py`: 96 pass.

**Not established:** the precision check covers founders-only 2016–2019. A full-window run with
the acquisition budget on settles more customer-years. The per-record error does not grow with
the book, but the cumulative treasury balance does, at about 1e-5 GBP per 4 years of 40 founders.
That is many orders of magnitude below the penny. The records (0.57 MB/scy, 45% in dict key tables) remain the bigger lever.
