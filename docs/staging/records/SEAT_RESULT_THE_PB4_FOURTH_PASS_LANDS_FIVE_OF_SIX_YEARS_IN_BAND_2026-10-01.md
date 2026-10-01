**Severity:** RECORDED · **Lane:** Lane 0 delivery · **Claim:** `land-pb4-swap-with-value-arms-retaken-in-the-new-world`

# The PB4 fourth pass lands five of six fitted years in band, and the standing-charge change did not move the fit

This grades `SEAT_PREREGISTRATION_THE_PB4_FOURTH_PASS_IN_THE_EX_VAT_STANDING_CHARGE_WORLD_2026-10-01.md`,
which sits beside this file and has not been edited.

Every capture was taken at origin `0407ce0e3` plus the PB4 swap, default seed, by
`tools/capture_departure_factors.py`. Each took about 25 minutes. The levels are whole book: the
SVT floor plus the renewal route's expected departures at the block's own anchor, over accounts.
They are computed through `tools/fit_year_level_anchor`'s own `fit_whole_book` and `_sum_probability`.

| year | band | C (third block, `e9b79073d`) | C2 (third block, now) | fourth block (refit on C2) | D (fourth block) |
|---|---|---|---|---|---|
| 2017 | 13.5-14.0 | 14.00 | 14.04 | 6.990171 | 14.00 in |
| 2018 | 19.5-20.0 | 20.00 | 20.03 | 5.269958 | 20.00 in |
| 2019 | 20.7-21.3 | 21.22 | 21.28 | 8.583067 | 21.30 in |
| 2020 | 22.5-23.0 | 21.67 | 21.67 | 19.550406 | 23.00 in |
| 2021 | 17.9-18.4 | 16.07 | 16.14 | 18.474462 | 18.40 in |
| 2023 | 8.9-12.5 | 8.81 | 8.81 | (unfittable, kept 2.033232) | 8.73 low |
| 2024 | 12.5-16.1 | 15.42 | 15.42 | 17.128306 | 16.28 **high by 0.18** |

- **P1 right.** C2 is within 0.07pp of C in every year. The ex-VAT standing charge does not
  move the departure level.
- **P2 right.** 2020 and 2021 are still low on C2.
- **P3 right.** The refit raises 2020 (16.29 to 19.55) and 2021 (12.21 to 18.47). The fixed point
  still was not reached: 2024 went over on D.
- **P4 right.** 2023 is still unfittable.

**Why D is accepted with 2024 0.18pp over.** On 65 accounts one departure is 1.54pp, so 0.18pp is
about 0.12 of one expected departure. The difference between C2 and D comes from the book moving
(2024 has 66 accounts in C2 and 65 in D), and a fifth pass would chase that move. The targets sit
at the band tops, which is why a small move shows as out of band. The cost is unchanged from the
third pass and gets larger: 2020, 2021 and 2024 now carry anchors above 17 on 8-12 renewal
decisions each, so the clamp is carrying more of the level.

D is the block the value arms are now re-taken in (world digest `cf823b185f8ca51c`). The landing
state lives in `docs/design/UNLANDED_PB4_SWAP_AND_THIRD_PASS_ANCHOR_2026-10-01.md`.
