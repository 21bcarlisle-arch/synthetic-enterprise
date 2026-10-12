**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# Pre-registration: the consumption forecasts behind purchasing, the DD, unbilled estimation and customer value, graded against held-back actuals

Written 2026-10-11T06:09Z, before I computed any held-back error. Claim
`one-consumption-forecast-per-property-or-several`, which answers question 2 of the director's console
message of 2026-10-11T04:20Z. The tracing of which consumer calls which forecast was done
first, by reading code, and is reported in the result finding. This file is not edited after the run.

## What is graded

**The saved run:** `docs/reports/run_output_latest.json` (producing commit `7379375f6`, generated
2026-10-10T13:50Z), 980 billed customers, 2016–2025.

**Held-back actual consumption:** `meter_read_log[*].true_consumption_kwh`, the world's monthly
consumption for each property. It is used **only to grade**. No forecast sees it, apart from the
one forecast whose production code reads the settled (true) volume (F4 below), and that is graded
the same way the run computes it.

**The anchor:** every 1 January from 2017 to 2024 at which a property has 12 complete months
behind it and 12 complete months ahead of it. A forecast predicts the next twelve months' kWh. The
opening forecast is graded separately at each account's first month.

**The forecasts:** each is rebuilt from what the run output carries, using only what the company
holds at the anchor:

| id | forecast | consumer(s) |
|---|---|---|
| F1 | registry EAC/AQ at opening (`estimate_annual_consumption`), never updated | opening DD; estimated bills before the first read |
| F2 | last 3 actual reads ÷ published profile weight × next 12 months' weight (`estimate_unread_kwh`) | estimated bills, so the estimated-billing-outstanding figure |
| F3 | last 12 months' **billed** kWh (estimates and catch-ups included) | annual DD review (`dd_balance_book`, at rates) |
| F4 | last 12 months' **settled** (true) kWh (`_company_eac_estimate`) | electricity hedge volume |
| F5 | registry AQ (× a household multiplier I cannot rebuild from the output) | gas hedge volume |
| F7 | 2-year billed kWh annualised, 30/22/18/30 quarterly shape (`calibrate_eac` + `forecast_annual_cost`) | customer portal only |

Forward CLV (`company/analytics/forward_clv.py`) is predicted to carry **no** consumption forecast,
because it projects margin history. If that is right it is reported as "no forecast", not graded.

**Error metrics:** signed and absolute percentage error of the 12-month total, per fuel, with the
median, the mean and a bootstrap 95% interval. Season error is winter (Oct–Mar) against summer
(Apr–Sep) kWh, for forecasts that carry a shape (F2, F7, and F1 shaped by the published profile).
F3 and F4 are annual figures, and their flat twelfths are graded as well to show what an
unshaped figure misses.

## Predictions

1. **There is more than one forecast.** At least four distinct functions answer "how much will this
   property use in the next year": F1, F2, F3 and F4/F5. *Already known from the trace, so this is
   not a test.*
2. **Annual accuracy, best to worst, by median absolute error:** F4 ≈ F3 < F7 < F2 < F1 ≈ F5.
   - F4 has a median absolute error of 5–10%, which is weather and life change from one year to the next.
   - F3 is about 1–3 points worse than F4, because estimated months and catch-ups add noise to the billed year.
   - F2 has a median absolute error of 12–20%, because three months is a short window and the
     profile is not this household's shape.
   - F1/F5 have a median absolute error of 20–30% after the first year, because occupancy, EPC and
     assets move households away from the registry declaration.
3. **Bias:** F1 over-forecasts on the median, because TDCV bands and declared EACs run above what
   the world's households use. F2 is unbiased on the annual figure.
4. **Season:** flat twelfths of F3/F4 under-forecast gas winter kWh by more than 30% and
   over-forecast gas summer kWh by more than 50%. F2's profile cuts the gas winter error to
   under 15%.
5. **Gas against electricity:** gas errors are larger than electricity errors for every forecast,
   because of weather sensitivity.
6. **Recommendation, predicted:** the best single forecast is a trailing-12-month **actual** kWh,
   weather-normalised and shaped by the published profile (in effect F4's level with F2's shape).
   They should be one.

Refutation: if F2 beats F3/F4 on the annual figure, or F1 is within 5 points of F4 after year
one, prediction 2 is wrong and the result says so beside it.
