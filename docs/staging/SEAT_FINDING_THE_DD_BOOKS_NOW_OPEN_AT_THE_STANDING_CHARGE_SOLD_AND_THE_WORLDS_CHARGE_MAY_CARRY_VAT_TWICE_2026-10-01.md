**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# The DD books now open at the standing charge sold, and the world's charge may carry VAT twice

Claim `open-the-dd-books-at-the-standing-charge-sold`. Results are recorded against
`docs/staging/records/SEAT_PREREGISTRATION_THE_DD_BOOKS_OPEN_AT_THE_STANDING_CHARGE_SOLD_2026-10-01.md`,
which was filed before the run.

## What changed

`simulation/run_phase4c_on_phase2b._opening_dd_by_customer` now passes `sold_standing_charge` as
`contracted_standing_charge_per_day_ex_vat`, beside `sold_unit_rate`. The DD books and the
experienced bill shock now quote each leg the same first bill. A new control, in
`tests/simulation/test_the_dd_books_open_at_the_rate_sold.py`, checks three things: the charge sold
moves the opening, an account with no charge keeps the fallback, and the books' opening equals
`opening_monthly_for_household` for the same leg. Mutating the pass-through to `None` makes it red.

## Results (one default world, both arms in one process, `/var/tmp/se-dd-books-sc-sold/out.json`)

| | Predicted | Measured | Verdict |
|---|---|---|---|
| P0 placebo | `n_opened` equal | 247 / 247 | **holds** |
| P1 | ≥ 80% open lower | 216 / 247 = 87.4% lower; 28 higher; 3 equal (no charge in first month) | **holds** |
| P2 | pre-2019 gas median fall £6–£11/month | −£9.09 (pre-2019 elec −£8.46) | **holds** |
| P3 | ≥ 1 opens higher, 2022+ elec | 28, all 2023–2025 electricity (+£0.81 for 2023, +£3.36 for 2024–25) | **holds** |
| P4 | review increases do not fall; held credit does not rise | increases 439 → 490, large 329 → 378; final held credit £2,310 → £1,443; mean held £1,882 → £784 | **holds** |

The median fall by cohort shrinks steadily over time: 2016 elec −£8.46 … 2021 −£6.86, 2022 −£1.43,
then 2023 +£0.81. Gas runs from −£9.09 to −£6.22.

## The odd reading: the world's charge is probably inc-VAT, carried as ex-VAT

`simulation/policy_costs._ELEC_SC_PENCE_PER_DAY_BY_YEAR` cites Ofgem cap publications for 2022+
(46p, 53p, 61p), and Ofgem publishes cap standing charges INCLUDING VAT. The table states no basis.
Settlement writes the figure into `standing_charge_gbp`, which every reader treats as ex-VAT. The
door then grosses it by 5%, so a 2023 account is quoted 55.65p where its bill printed 53p. That is
why 2023 electricity opens HIGHER than the 53p fallback, although the two figures are the same.

The pre-2022 rows are "typical market averages" with no named source. Before anything is built on
the level, the world's standing-charge basis needs establishing against the published cap
breakdowns (a world-side fidelity question, decided blind to company results). It does not split
the two callers: the bill shock has grossed this same field since 7c872f2d0, so books and shock now
agree, including on this.
