**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

*RECORDED, not LATENT: this is a pre-registration and refutes nothing on its own. It exists so the
finding filed beside it can be shown to have been designed before its answer was known.*

# Pre-registration: what the SVT route's market-invariance must show

**Filed 2026-08-31, delivery seat, Lane 0, BEFORE running any of P1–P3 below.**
Instrument: `tools/fit_year_level_anchor.py` (whole-book fit, landed `b8e6ba32d`).
Capture: `docs/reports/ladder_churn_factors.json` + its `_svt_segment_decisions.json` sidecar.

---

## What is already observed, and is therefore NOT a prediction

The whole-book fit was run before this file was written and the following is the output, not a
forecast. It is written down here so the predictions below cannot be mistaken for it.

| year | accts | nRen | nSVT | record % | SVT floor % | anchor | achieved % |
|---|---|---|---|---|---|---|---|
| 2016 | 3 | 1 | 2 | 17.60 | 0.04 | — | partial year |
| 2017 | 57 | 20 | 115 | 14.00 | 9.27 | 4.0274 | 14.000 |
| 2018 | 53 | 20 | 139 | 20.00 | 11.36 | 2.5386 | 20.000 |
| 2019 | 39 | 14 | 110 | 21.30 | 11.60 | 4.3482 | 21.300 |
| 2020 | 48 | 17 | 127 | 23.00 | 9.85 | 5.8495 | 23.000 |
| 2021 | 54 | 22 | 148 | 18.40 | 9.62 | 4.0422 | 18.400 |
| 2022 | 55 | 0 | 198 | **4.30** | **12.80** | — | **unreachable** |
| 2023 | 54 | 17 | 196 | 12.50 | 12.43 | **0.0300** | 12.500 |
| 2024 | 54 | 18 | 150 | 16.10 | 9.12 | 2.8005 | 16.100 |
| 2025 | 48 | 15 | 81 | 17.90 | 4.90 | — | partial year |

So: the record swings 4.30 → 23.00 (5.3x) and the SVT floor sits in a 9.1–12.8 band throughout.
2022 is the record's TROUGH and carries the SVT route's HIGHEST floor. 2023's renewal anchor is
driven to 0.03 — near-total extinction of the priceable route — because the SVT floor has already
consumed 12.43 of the 12.50 available.

**That much is measured.** What is NOT yet established is whether this is a calibration choice that
a different point in the published band would cure, or a property of the mechanism. That is what
P1–P3 are for.

---

## The mechanism claim under test

`simulation.departure_risks.svt_inertia_hazard(years_on_svt=, segment_days=)` takes **no market
year and no market term**. Every renewal-route hazard carries `market_switching_multiplier`, which
is the record's own level ratio inside 2016–2025. The SVT route does not. If that is what is
happening, the route carrying 61% of this world's departures is *invariant to the market the record
describes* — flat across a decade whose published switching rate moves 5.3x.

`docs/market_research/svt_rates_active_passive_2016_2025.md` §3 states the opposite of invariance
for the crisis specifically: *"Customers did not voluntarily churn: no competitive fixed
alternatives existed."* The world's own source says the 2022 drift collapsed. The world applies the
same 0.20/0.10 it applies to 2020.

---

## Predictions, filed before measurement

**P1 — the floor does not track the record.** Spearman rank correlation between the SVT floor % and
the published band midpoint, over the eight non-partial years 2017–2024, will be **near zero or
negative: |rho| < 0.4**. A route that tracked the market would run strongly positive. If rho comes
out > 0.4 positive, this whole finding is wrong and I will say so beside it.

**P2 — no point in the published SVT band rescues 2022.** §4 of the source publishes bands, not
points: 15–20% recent, 5–10% long-stayer, and the world takes the TOP of each. Re-running the
whole-book fit at the BOTTOM of both bands (0.15 / 0.05) will still leave 2022's SVT floor **above**
its 4.30% target, so 2022 remains refused as unreachable. Predicted floor at the band bottom:
roughly 0.75x of 12.80 ≈ **9–10%**, still 2x the target. If the band bottom does clear 2022, this is
a calibration finding and not a mechanism one, and the remedy is a constant, not a wiring change.

**P3 — the floor is flat where the record is not.** The coefficient of variation of the SVT floor
across 2017–2024 will be **less than half** that of the published midpoint over the same years.

---

## What each outcome means for the re-fit

- **P1 and P2 both confirmed** → the SVT route is structurally market-invariant, the whole-book
  anchor table must NOT be pasted into `simulation/departure_level_anchor.py` (a 2023 value of 0.03
  is the defect propagating, not a level), and the owed repair is to give the SVT hazard the market
  term the renewal route already carries.
- **P2 refuted** → the band top was the wrong end and the fix is the constant. The §7 anti-flattering
  tie-break that chose the top gets re-examined, because once the whole-book total is anchored to the
  record, a HIGHER SVT floor LOWERS the renewal anchor — it hands the company less churn on the only
  route it can price against. The tie-break inverts its own sign.
- **P1 refuted** → the route does track the record by some path I have not found, and the 2022
  refusal is about 2022 alone.

**Nothing is pasted into the world on this turn either way.** The re-fit's output is a diagnostic
until the mechanism question above is settled; that is the same discipline `emission_refusal`
already applies one level up.
