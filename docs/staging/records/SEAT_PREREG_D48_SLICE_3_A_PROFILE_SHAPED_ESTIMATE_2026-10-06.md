**Severity:** RECORDED · **Lane:** D_billing_metering · **Claim:** `d48-slice-3-a-seasonal-estimate-for-the-unread-month`

# Pre-registration: D48 slice 3, a profile-shaped estimate for the unread month

Filed 2026-10-06, before the decade world was captured, before the published profile shares
were in hand, and before any estimator was written.

## The change being tested

Today an unread month is estimated as (trailing window kWh / trailing window days) x this period's
days: flat across the year. The change is the industry's own method: derive a rate from the
window's actual kWh over the window's summed **profile weight** (the published monthly share of
annual use, spread evenly over each month's days), then bill that rate over this period's summed
profile weight. Electricity uses a published domestic profile; gas a published domestic NDM
profile. Seasonal normal only: no actual-weather correction, because that is not what the
published method asks of a bill estimate and the company holds no weather feed for it.

The ONE variable: the estimator. Same captured world (`run_phase2b()`, full decade, one capture),
same read arrivals (seeded per customer-period, untouched), bills built twice.

## Baseline (slice 2, `06cda5325`, pooled over the year ends 2016-2024)

| | Electricity | Gas |
|---|---|---|
| December net true-up / run billed kWh | +10.3% | +23.9% |
| December gross | 17.3% | 53.3% |
| June net | -1.7% | -26.3% |

The baseline is re-measured on the capture first. If it does not reproduce within 1 pp, every
row below is void and the difference is the first finding.

## Predictions

| | Prediction |
|---|---|
| P1 December net, electricity | **\|net\| < 5%** |
| P2 December net, gas | **\|net\| < 10%** |
| P3 June net, electricity | **\|net\| < 5%** |
| P4 June net, gas | **\|net\| < 10%** |
| P5 Gross share falls at both month ends, both fuels; gas December gross below 35% | yes |
| P6 What remains | December and June residuals are NOT of opposite sign at more than 5% each for either fuel. Opposite signs mean the published amplitude and the world's disagree: December still positive with June negative is the profile too flat for the world; the reverse is too steep. That is a fidelity question about the world, not the estimator |
| P7 K2 (estimated share of billed kWh) | unchanged within 0.5 pp: the estimator changes amounts, not which bills are estimated |

If P2/P4 fail with OPPOSITE signs in the two seasons, the explanation to test next is the
world's seasonal amplitude against the published one, measured from the book's actual reads by
calendar month, not a tuned profile.
