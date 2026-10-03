**Severity:** RECORDED · **Lane:** W2_customer_generator · **Claim:** `refit-the-level-anchor-onto-desnz-qep-2-7-1` (Lane 0 delivery)

# Pre-registration: what re-siting the switching record onto DESNZ QEP 2.7.1 must move

Written 2026-10-03 ~22:30Z, BEFORE capture E (below) was started. Grades go in a sibling result
file; this one is not edited after the capture begins.

## What changed, and the one thing that is easy to miss

The commons `gb_domestic_switching_rate.json` `rates` are re-sited onto QEP 2.7.1 (version 2; band
= the published count's rounding, ~0.004pp wide). The world reads that file in TWO places, not one:

1. `market_departure_rate(year)` — the fit's TARGET. 2017-2025 targets fall in every year except
   2017 (13.5-14.0 → 18.19); 2023-2025 fall by 42-49%.
2. `market_switching_multiplier(year)` = rate(year) / rate(2024) — a factor on every hazard AND the
   company-facing observable the renewal desk reads as `pressure`. Because 2024 falls the most, the
   ratio for every earlier year roughly doubles. Printed at real inputs:

   | year | old ratio | new ratio |
   |---|---|---|
   | 2017 | 0.87 | 2.02 |
   | 2018 | 1.24 | 2.11 |
   | 2019 | 1.32 | 2.31 |
   | 2020 | 1.43 | 2.24 |
   | 2021 | 1.14 | 1.72 |
   | 2022 | 0.27 | 0.34 |
   | 2023 | 0.78 | 0.70 |
   | 2024 | 1.00 | 1.00 |
   | 2025 | 1.11 | 1.15 |

   Synthetic futures (2026+) read the savings curve at `_curve_level_scale()`, which falls 2.04 →
   1.67, so a future year reads 15.04%, above 2025's 10.40. Noted, not repaired here.

So the corrected record changes the world's hazards BEFORE any anchor moves, and a capture under
the old anchors is a different world from D. That capture is E.

## Capture E — corrected commons, fourth-pass anchors (origin `38f430f57` + the commons edit)

Whole-book expected level, `fit_whole_book` on E, against D's 2017 14.00 · 2018 20.00 ·
2019 21.30 · 2020 23.00 · 2021 18.40 · 2022 2.59 · 2023 8.73 · 2024 16.28:

- **P1.** 2024 within ±1.0pp of D (16.28): its multiplier is 1.0 under both records, so only the
  book's composition can move it.
- **P2.** 2017-2021 all RISE above D, each by at least 3pp, and all five end ABOVE their new
  targets (18.19-20.82). The multiplier rises 1.5-2.3x on a saturating hazard, so less than
  proportionally.
- **P3.** 2023 FALLS a little (ratio 0.78 → 0.70), to 7.5-8.7. 2022 RISES (0.27 → 0.34), to 2.8-3.6.

## The fit on E, onto QEP

- **P4.** Every fitted anchor in 2017-2021 FALLS, and 2024's falls (target 16.1 → 9.03).
- **P5 — the one that decides whether this is a re-fit or a finding.** The SVT route is untouched
  by the anchor. If its floor in a year already exceeds the corrected target, `fit_whole_book`
  refuses the year as **unreachable** and no clamp can carry it down. I predict 2024 FITS (floor
  below 9.03) and 2023 stays refused, now as **unreachable** rather than "the renewal route cannot
  carry the residual", because its target fell from 12.5 to 6.33. I give 2024 about even odds; if
  2024 refuses as unreachable, that is the result, it is reported as the mechanism's, and the
  table does not get a number for it.

## Capture F — corrected commons, the re-fitted block

- **P6.** F lands within 0.5pp of target in at least 4 of the fitted years. One pass does not reach
  the fixed point (third and fourth passes both moved), so I do not predict all of them.
