**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

*LATENT and not BLOCKING: no published surface today states a whole-book departure rate, so no live
figure and no control's verdict rests on this. It becomes BLOCKING the moment one does — the world's
2022 departs ~12.8% of the book by a route the record caps at 4.3% for every route combined. The
control landed beside this refuses the constant rather than merely warning, which is what keeps the
gap from reaching a page while it is open.*

# The route carrying most of this world's departures is invariant to the record it is fitted against

**Filed 2026-08-31, delivery seat, Lane 0.** Instrument: `tools/fit_year_level_anchor.py`
(whole-book fit). Capture: `docs/reports/ladder_churn_factors.json` + its
`_svt_segment_decisions.json` sidecar. Control:
`tests/architecture/test_a_departure_reading_declares_its_population.py::test_the_fit_refuses_while_the_svt_route_cannot_see_the_market`
and its lift leg (3 mutations proven, each firing on the leg it targets).
Pre-registered before measurement in
`docs/staging/WORKER_PREREGISTRATION_WHAT_THE_SVT_ROUTES_MARKET_INVARIANCE_MUST_SHOW_2026-08-31.md`.

---

## What was being done, and what fell out of it

`b8e6ba32d` unioned the two departure routes onto the record's own denominator — accounts — and left
one item owed: re-fit `YEAR_LEVEL_ANCHOR` on the two-route capture. Running that fit is what surfaced
this. **The re-fit is not landable, and the reason is not the fit.**

| year | accts | nRen | nSVT | record % | SVT floor % | fitted anchor |
|---|---|---|---|---|---|---|
| 2017 | 57 | 20 | 115 | 14.00 | 9.27 | 4.0274 |
| 2018 | 53 | 20 | 139 | 20.00 | 11.36 | 2.5386 |
| 2019 | 39 | 14 | 110 | 21.30 | 11.60 | 4.3482 |
| 2020 | 48 | 17 | 127 | 23.00 | 9.85 | 5.8495 |
| 2021 | 54 | 22 | 148 | 18.40 | 9.62 | 4.0422 |
| 2022 | 55 | 0 | 198 | **4.30** | **12.80** | **refused — unreachable** |
| 2023 | 54 | 17 | 196 | 12.50 | 12.43 | **0.0300** |
| 2024 | 54 | 18 | 150 | 16.10 | 9.12 | 2.8005 |

The record swings 4.30 → 23.00, a 5.3x move. The SVT floor sits in a 9.1–12.8 band throughout, and
**2022 — the record's trough — carries the route's highest floor.**

## The mechanism

`simulation.departure_risks.svt_inertia_hazard` takes `years_on_svt` and `segment_days`. That is
all. Every renewal-route hazard carries `market_switching_multiplier`, the record's own level ratio
inside 2016–2025. The SVT route has no parameter through which the market could arrive, so it runs
the same 0.20/0.10 through the crisis, the 2020 peak and the 2022 collapse alike.

The world's own source says the opposite. `docs/market_research/svt_rates_active_passive_2016_2025.md`
§3: *"Customers did not voluntarily churn: no competitive fixed alternatives existed."*

## Three predictions, filed before the measurement, all confirmed

- **P1 — the floor does not track the record.** Predicted |rho| < 0.4. **Measured Spearman rho =
  −0.26** over 2017–2024. Near zero and the wrong sign.
- **P2 — no point in the published band rescues 2022.** §4 publishes bands (15–20% recent, 5–10%
  long-stayer) and the world takes the top of each. At the **bottom** of both, 2022's floor is still
  **8.99% against a 4.30% target — 2.09x**. Clearing it needs the pair scaled to **0.354x**; the band
  bottom is only **0.750x** of the top. This is a mechanism result, not a constant at the wrong end.
- **P3 — flat where the record is not.** Predicted CV ratio < 0.5. **Measured 0.336.**

## Why this blocks the constant instead of warning beside it

With the whole-book total pinned to the record, the two routes are **zero-sum**. The SVT route's
market error does not stay on the SVT route — it lands in the renewal anchor, which is the only free
parameter left. 2023's floor consumes 12.43 of the 12.50 available and the fit returns **0.03**:
near-total extinction of the one route the company can price against. Pasting that table into
`simulation/departure_level_anchor.py` would not be a level. It would be this defect wearing a
calibration's clothes, and every downstream reason-mix reading would inherit it silently — every row
well-formed, the table still printing.

## The part worth keeping: an anti-flattering tie-break that inverted its own sign

`0.20` was taken at the **top** of its band under the director's §7 rule — where the evidence is
ambiguous, choose what makes the company's advantage harder to demonstrate. The stated argument:
the company "loses accounts it has NO renewal lever on… pure loss with no instrument against it".

That argument was sound **when the SVT route was sized on its own**. Once both routes share one
denominator and one anchored total, a *higher* SVT floor *lowers* the renewal anchor — it hands the
company **less** churn on the route it can actually price against, and shifts loss onto a route no
A/B can measure. **The anti-flattering choice became a flattering one at the moment the denominator
was unioned, and nothing in the tree would have reported it.** The tie-break was not wrong; its sign
is a function of a structure that changed underneath it.

*Generalising: a tie-break argued on a quantity's own direction inverts when that quantity becomes a
component of an anchored total. Re-examine every §7 choice whose subject later joined a fitted sum.*

## What is owed, and it is not a widened band

Wire the market term the renewal route already carries into the SVT hazard. **Checked, and it is
sufficient:** `floor × market_switching_multiplier(year)` puts all eight years under their target
with headroom for the renewal route —

| year | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|
| floor × mult % | 8.06 | 14.12 | 15.35 | 14.08 | 11.00 | **3.42** | 9.65 | 9.12 |
| target % | 14.00 | 20.00 | 21.30 | 23.00 | 18.40 | **4.30** | 12.50 | 16.10 |

That is a world change against the published record, decided blind to company results, so it is
**baseline, not curriculum** — and it moves hard against the company in the years that matter, by
restoring departures to the priceable route. It needs its own capture → fit → capture cycle and is
larger than the turn that found it, so it is filed here rather than half-done.

**Not yet established and deliberately not guessed:** whether drift off SVT is an *external* change
of supplier at all. §4's own bottom row — "All customers (industry avg) ~20–22%" — is the same
quantity as the published band, which suggests the SVT rows are a **component** of that rate rather
than a route on top of it. If so the union is double-counting, and that is a second, larger question
than the market term. Filed as open, with no number attached.
