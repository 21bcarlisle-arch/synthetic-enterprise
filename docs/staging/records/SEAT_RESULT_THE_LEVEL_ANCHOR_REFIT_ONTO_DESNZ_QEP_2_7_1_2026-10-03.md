**Severity:** RECORDED · **Lane:** W2_customer_generator · **Claim:** `refit-the-level-anchor-onto-desnz-qep-2-7-1` (Lane 0 delivery)

# The corrected switching record drains the pre-2022 book, and two passes put every fitted year on QEP 2.7.1

This grades `SEAT_PREREGISTRATION_THE_LEVEL_ANCHOR_REFIT_ONTO_DESNZ_QEP_2_7_1_2026-10-03.md`, which
sits beside this file and has not been edited since capture E started.

Every capture is `tools/capture_departure_factors.py`, default seed, from a worktree at origin plus
the commons re-site (E at `38f430f57`; F and G at the same base). About 24 minutes each. Levels are
whole book: SVT floor plus the renewal route's expected departures at the block's own anchor, over
accounts, through `fit_year_level_anchor.fit_whole_book` and `_sum_probability`.

| year | QEP % | D (old record, 4th block) | E (new record, 4th block) | F (QEP pass 1) | G (QEP pass 2) | G block |
|---|---|---|---|---|---|---|
| 2017 | 18.20 | 14.00 | 19.31 | 18.20 | 18.20 | 6.202429 |
| 2018 | 19.07 | 20.00 | 20.36 | 19.07 | 19.07 | 4.295421 |
| 2019 | 20.82 | 21.30 | 21.18 | 20.82 | 20.82 | 8.081564 |
| 2020 | 20.21 | 23.00 | 28.08 | 20.21 | 20.21 | 8.402043 |
| 2021 | 15.57 | 18.40 | 16.57 | 20.49 | 15.81 | 7.733780 |
| 2022 | 3.06 | 2.59 | 1.99 | 2.05 | 2.07 | (1.0, unfitted) |
| 2023 | 6.33 | 8.73 | 4.35 | 4.43 | 4.52 | 2.033232 kept, multiplies nothing |
| 2024 | 9.03 | 16.28 | 7.62 | 10.15 | 8.75 | 20.817509 |
| accounts 2024 / renewal decisions 2024 | | 65 / 12 | 44 / 3 | 47 / 4 | 49 / 4 | |

## Grades

- **P1 WRONG, and by the most.** 2024 moved 16.28 → 7.62, not within ±1pp. Its multiplier is 1.0
  under both records, as stated, but I said "only the book's composition can move it" as if that
  were small. The pre-2022 multipliers double, the book drains (2024 holds 44 accounts and 3
  renewal decisions against 65 and 12), and a smaller, more SVT-heavy book departs less.
- **P2 2 of 5.** 2017 (+5.3) and 2020 (+5.1) rose ≥3pp and ended above target. 2018 (+0.4) and
  2019 (−0.1) barely moved, and 2021 FELL (−1.8). The rise goes to the years whose renewal route is
  big enough to carry it; 2021's book was already thinned by 2020.
- **P3 WRONG on both.** 2023 fell much further than predicted (4.35, not 7.5-8.7), and 2022 FELL
  (1.99) where I predicted a rise. Same cause as P1: the book after 2020 is not D's book.
- **P4 6 of 7 directions.** 2017-2021 anchors all fell. 2024's ROSE (17.1 → 28.3 on E, settling at
  20.8 on G), opposite to the prediction, because E put 2024 below its new target.
- **P5 half right.** 2024 fits. 2023 stays refused, but as **no renewal decisions in this year**,
  not as unreachable: its floor fell under its target (4.52 < 6.33), so the anchor would have to
  push it UP, and there is nothing for it to push.
- **P6 HELD.** F put 4 of 6 within 0.5pp (2017-2020, to 0.01pp). G puts all 6: 2021 +0.24pp and
  2024 −0.28pp, each under 0.15 of one expected departure on a 48-49 account book. Accepted on the
  rule the fourth pass used; a third pass would chase the book's own movement.

## What it means

1. **Every fitted year is now on the publisher's record, not on a refuted one.** 2024's world level
   falls from 16.28% to 8.75%, against QEP's 9.03%. The leak the finding sized as about half of the
   console seat's 2024-25 churn-belief error is gone from the target. Whether the belief error
   itself shrinks is a separate reading and is not claimed here.
2. **The world is LOW in 2022 and 2023 and nothing can lift it.** 2022 at 2.07% against 3.06% and
   2023 at 4.52% against 6.33%, both with zero renewal decisions. Before this, 2023 was HIGH against
   its refuted band. Rung-1 debt, recorded, not clamped.
3. **The clamp carries more than ever.** 2024's 20.8 stands on 4 renewal decisions. The rung-1
   verdict (`departure_level_rung1_verdict.json`, regenerated on G) reads 0 of 6 fitted years in
   band unclamped, all LOW by 4.6-8.5pp. The band is now ~0.004pp wide, so "in band" means "on the
   record", and an unclamped world cannot reach that by luck.
4. **The company sees it too.** `market_switching_multiplier` crosses the wall as the renewal desk's
   `pressure`, which roughly doubles in 2017-2021. Measured so far: the acquisition campaign's
   in-play pool moves 2709 → 2707 quotes. The value arms are what measure the rest.

## What else the corrected record moved (found while re-keying the controls)

- **A 2016 renewal now saturates.** 2016 is outside the fit window and borrows 2024's anchor,
  which is now 20.8, at 2016's multiplier of 1.75. A household renewing at the SVT itself departs
  with probability 0.77, and at +20% both an elastic and a disengaged household sit on the churn
  ceiling (0.9831). `test_the_CHURN_DECISION_actually_feels_the_households_drawn_sensitivity` went
  red for that reason, not because the wiring broke: at +10% they read 0.894 and 0.860. Its fixture
  moved to +10%. This is the clamp-carries-the-level debt made sharper. A 4-decision 2024 anchor
  is now the calibration for every year outside the record.
- **§13 and §14 of the route split moved.** On version 1's bands the mix-free envelope admitted a
  constant phi over the fitted years. On the QEP record it refuses too, so "the refusal is a
  statement about one 2018 survey" is no longer true: the record refuses a constant phi however
  the tenure mix is read. Six reachability controls had been proving their pass branches on live
  data with a band that had width. They now prove them on version 1's bands kept as a fixture
  (`_A_BAND_WITH_WIDTH`), and every value check stays on the live record. Mutation: stop the
  fixture patching and five of them go red; the sixth patches directly.
- **2022's declared SVT floor** is 1.94% against a published 3.06% (was 2.54% against 4.30%). It is
  still below, so the cause stands.
- **The company's own readings moved with the record.** `market_conditions` reads the commons
  midpoint at three places, because a 2dp midpoint falls outside a 0.004pp band, and
  `market_report._UK_SWITCHING_RATE_PCT` is re-read onto QEP. The refutation control
  (`test_a_refuted_commons_artefact_cannot_quietly_become_current.py`) is retired with its subject,
  as its own message asks.
- **Settlement evidence re-filed for world `cdba75ebb9197b33`** (`settlement_per_axis_gain`, seed
  42 filed, 43-45 read): settled cull / chosen 62/57, 61/53, 57/46, 57/48; worst-axis ratio
  0.937, 0.891, 0.855, 1.225; P1b HOLDS on all four. As on world D, the chooser is at or below
  parity with the cull on its worst axis on three seeds of four.
- **Gap noticed, not repaired:** `world_level_identity` digests the anchors only. A commons change
  alone moves `market_switching_multiplier` on every hazard and the renewal desk's `pressure`,
  and leaves the digest unchanged. Here the anchors moved too, so the digest did move.

## Landing

The measurements (pre-registration, E, F) landed as `24ece7adb`. The world change — commons
version 2, the G block, `DEFAULT_TABLE` → G, the six regenerated verdicts — moves
`world_level_identity` and cannot land until the value arms are re-taken in it. The patch and the
running re-take are in `docs/design/UNLANDED_QEP_LEVEL_ANCHOR_REFIT_2026-10-04.md`.
