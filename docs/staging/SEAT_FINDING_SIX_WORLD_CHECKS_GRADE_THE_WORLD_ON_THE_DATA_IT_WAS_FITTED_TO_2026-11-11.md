**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# Six world checks grade the world on the data it was fitted to; one is clearly held out (2026-11-11)

**What prompted it.** The director's 11 Nov steer (gap-driven literature search, its last bullet, prompted by GLM's
blank-infilling idea) asked: "do our world checks test against data held back from fitting, or against the data the world
was fitted on? If the latter, say where." Another lane's landing of that steer carries a first pass. This is the
census behind it. Each row was read from code by a census helper (Sonnet), and the seat spot-checked three of them
(rows 3, 5 and 6 below, by grep of the quoted text). Nothing was run.

**What the categories mean, stated before counting.** *Held out*: the check's data was not used to fit the quantity it
grades. *Same as fit*: the check grades on the data, or the published band, that the quantity was fitted or calibrated
to. A pass then shows only that the fit reproduced its own input. *No check*: nothing compares the quantity with an
observed series. These are three different statements. Only the first is evidence that the world generalises.

| # | World quantity | Fitted where | Checked by | Category |
|---|---|---|---|---|
| 1 | Grid carbon intensity, generated futures | `sim/grid_carbon_future.py` `HELD_OUT_TRAIN` 2023–24 | `validation_table`, graded on 2025 | **Held out** |
| 2 | SSP residual-demand axis | `sim/price_engine.py` ~l.206 | "held out by year", per a cited pre-registration | Held out as stated, not verified |
| 3 | Wholesale SSP level (A0, A1, A2, X_TIGHT, exponent) | `simulation/run_phase3b_recalibration.py`, full window 2016-03 to 2025-06 | the same script's per-year table; `docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md` | **Same as fit** |
| 4 | SSP tail (max, negative-price share) | the same fit | `sim/ssp_tail_model.py` against `sim/ssp_tail_target.py` ("the SAME span as the model it grades") | **Same as fit**. It misses anyway |
| 5 | Annual departure level | `simulation/departure_level_anchor.py`, bisection onto the published rate, `FIT_COMPARISON_WINDOW = range(2017, 2025)` | `tests/architecture/test_switching_rate_commons.py`, in band against the same published band | **Same as fit**. The test's own text: "each sitting exactly on its high endpoint -- the anchor's own fit" |
| 6 | Direct-debit share 0.72 / 0.75 | `simulation/household_segments.py` (DESNZ 69–72%) | `tools/world_claims.py`, band [0.665, 0.755] from the same DESNZ figure | **Same as fit** |
| 7 | Weather engine constants | `simulation/run_phase3c_calibration.py` | `docs/calibration/weather-engine.md`: "the same sample used to fit … the reported errors are a best case" | **Same as fit**, stated by the doc itself |
| 8 | Other world-claims figures (fuel split, dual fuel) | `household_segments.py` draw constants | `tools/world_claims.py` | Probably same as fit; not audited claim by claim |
| 9 | Bad-debt incidence by year | `simulation/bad_debt_incidence.py` ("calibrated to the shape of the 2021-22 … surge") | none found | **No check** |
| 10 | Occupancy and consumption volume shape | `simulation/demand_model.py` anchors 1–2 | none found | **No check** |
| 11 | Savings-to-switching curve | `simulation/market_switching_propensity.py`, explicitly not calibrated to DESNZ | `tools/measure_departure_level.py` reports it against the record | An honest comparison: not fitted, measured 2.04× below the record |
| 12 | Arrears and 91-day debt stock | payment-outcome rates, cited | `tools/grade_world_debt_against_ofgem.py` (Ofgem Q4 2019) | Unclear. It looks external, but no fit to the 2019 figure was found |

**Counts.** Held out: 1 clear, 1 as stated. Same as fit: 5 clear (rows 3–7), 1 probable. No check: 2. Honest
unfitted comparison: 1. Unclear: 1.

**Where it matters most.** Rows 3–5 are the world's price and churn levels. They are what the company's margin
and retention are tested against. "The world matches the record" is true there in the sense that the fit converged.
It is not evidence that the world would match a year it was not shown. The fidelity page's "beats best-of-naive in
4/10 years" sits on row 3's fit window.

**What would answer it, smallest first (R5).** These are not built here. Each is one run that can refute the world:
(a) row 3, refit the SSP constants on 2016–2022 and grade 2023–25; (b) row 5, bisect the anchor on 2017–2021 and
grade 2022–24, with 2022 handled as the anchor already handles it; (c) row 7, fit the weather constants on one year
and grade another, as the doc itself asks. Row 1's method (`validation_table`) is the template.

**The prediction, filed before any of (a)–(c) runs.** At least one of rows 3 and 5 moves outside its published band
on its held-back years. p ≈ 0.6 for row 5, because slice 13 of B11 showed pre- and post-crisis switching differ in
sign on the supplier side. p ≈ 0.4 for row 3.

**Reverse.** Delete this file.
