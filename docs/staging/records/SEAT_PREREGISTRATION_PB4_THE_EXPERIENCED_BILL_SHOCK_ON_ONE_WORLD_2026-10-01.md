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

## Result (appended after the run; nothing above is edited)

Run `aed6bf966`, 1360 s, 106 decided renewals, every one carrying the shock. Scripts and output:
`/var/tmp/se-pb4-shock-out/` (`run.py`, `analyse.py`, `events.json`). Each billing account is
decided once per renewal, so the per-household table equals the per-row table.

| Population | n |
|---|---|
| A, direct debit | 83 |
| C, prepayment (None by definition) | 13 |
| B, standard credit | 10 |

| | n | None: no quote | None: prepayment | Defined | Shocked | Share |
|---|---|---|---|---|---|---|
| First renewal | 36 | 27 | 5 | **4** | 0 | 0.000 |
| Later renewal | 70 | 0 | 8 | 62 | 20 | **0.323** |

| | Verdict |
|---|---|
| P1 | **CANNOT BE GRADED.** 0 of 4 defined. n = 4 is no reading, and 0/4 is consistent with the predicted band. |
| P2 | **NOT HELD as written:** 0.000 against 0.323 is a difference of 0.32. The same n = 4 makes it ungradable in substance. |
| P3 | **CANNOT BE GRADED.** The world decided **no renewal in 2022** and two in 2023. There is no 2022 cell. |
| P4 | **HELD.** Every pre-2020 first renewal is None: 27 for no quote, 4 prepayment. The None share of first renewals is **0.89**. |
| P5 | **HELD.** The within-year correlation is +0.029 (n = 62), inside the published −0.07 to +0.05. |
| P6 | **PARTLY.** 2023 is 2/2, the highest cell but on n = 2. 2025 is 0/5. 2024 is 2/9 = 0.22, which is not near 0. 2018 is 6/16 = 0.38. |

Other readings:

- The rise fraction's quartiles are −0.082, +0.066 and +0.223.
- **16 of 66 defined rows FELL by more than 15%.** The old `abs()` count scored those as shocks; this
  definition does not.
- The old base averages 0.023 at first renewals against 0.111 at later ones. That is the old
  tenure gradient, reproduced.

**The plan-level refutation fired, but on a different leg than the one written.** The cut did not
saturate: the later share is 0.32, a usable rate. Instead, **year one is still blind, now as None
where it used to be 0**. 76 of the 106 rows are 2016 sign-ups. The opening amount is annualised
at the cap unit rate, and the repository holds no cap before January 2019. So the quantity
cannot fire at the first renewal for 87% (27/31) of in-scope first renewals. Swapping the hazard
onto it now would move the blindness, not end it. The swap waits. See
`SEAT_FINDING_THE_EXPERIENCED_BILL_SHOCK_IS_STILL_BLIND_IN_YEAR_ONE_BECAUSE_THE_QUOTE_IS_PRICED_AT_A_CAP_THAT_DID_NOT_EXIST_2026-10-01.md`.
