**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# Pre-registration: the experienced bill shock on one world, before the hazard reads it

Claim `measure-the-experienced-bill-shock-on-one-world`. Filed 2026-10-01 ~06:40 BST, BEFORE the run.
No figure below has been computed. This is step 1 and step 2 of
`SEAT_CONTINUATION_SWAP_THE_WORLDS_BILL_SHOCK_BASE_ONTO_THE_EXPERIENCED_SHOCK_2026-10-01.md`.

## The run

One `simulation.run_phase2b.main()` on the default book. The code is a clean detached worktree at
origin/main `aed6bf966`, which contains `a0ccd009b`. No redraw keys, and the default seed. The
population is every `customer_events` row carrying `sim_experienced_bill_shock`, i.e. every
renewal `roll_lifecycle_event` decided. The shock does not drive the hazard yet, so this run's
departures are the world as it already is.

"First renewal" is the module's own flag: acquisition + 365 days falls in the renewal month.
"Later" is every other decided renewal. A dual-fuel household is decided once per leg. Counting
rows overstates n for dual fuel, so each headline is given per row AND per (household, renewal
month), with the household taken as shocked if any leg is.

## Predictions

| | Prediction | Why |
|---|---|---|
| P1 | Among first renewals with a defined shock (`shocked` not None), the shocked share is **> 0**, in [0.10, 0.50]. | The old count is 0 by construction at tenure 1. The quote is a sign-up rate. The year's bills include weather and cap movements. |
| P2 | The **tenure gradient is small**: \|share(first) − share(later)\| < 0.25 over defined rows. The old count's 0 against 6.86/12 months had no common scale; this one is binary on both sides. | Both sides now measure one event a year against a reference of the same kind. |
| P3 | Of the (renewal year × first/later) cells with ≥ 5 defined rows, **the 2022 first renewals have the highest shocked share**. | Cap rises from April 2022 hit a year whose reference is a 2021 quote. |
| P4 | **Every first renewal before 2020 is None** with the "no amount was set at sign-up" reason, and **over half of all first renewals are None**. | The continuation says pre-2019 sign-ups have no quote, and the book is old. |
| P5 | **No bill-size gradient**: within renewal year, \|corr(shocked, household annual bill)\| < 0.10 over defined later renewals. | The rise is a ratio, so it is scale-free. The published band is −0.07 to +0.05 (Ofgem/BMG 2024). |
| P6 | Among later renewals, the shocked share is **highest in 2022–2023** and **at or near 0 in 2024–2025**. | Bills rose from 2021 into 2022–23 and fell after. A fall is not a shock. |

The None count is published by reason, never dropped.

## What would refute the plan, not just a prediction

If the shocked share at first renewal and at later renewals are both near 0, or both near 1, the
15% cut (inherited, unsourced) is doing the work and the swap would only move the level. The swap
then waits on a sourced noticing threshold. It does not proceed on this quantity.

## Result

(appended after the run; nothing above is edited)
