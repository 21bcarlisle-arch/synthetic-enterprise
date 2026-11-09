**Severity:** RECORDED · **Lane:** W3_industry_systems · **Atom:** `W3_3_the_network_charge_splits_per_unit_and_per_day`

# Pre-registration: what splitting the domestic network charge into per-kWh and per-day moves (2026-11-09)

Written by the worker tick on 9 Nov 2026, in the commit that lands the change and before any run
of it. Source finding: `docs/staging/done/SEAT_FINDING_RENEWALS_SIT_AT_THEIR_COST_FLOOR_BECAUSE_THE_FLOOR_CARRIES_THE_STANDING_CHARGES_NETWORK_AND_THE_PREMIUM_READS_THE_STANDING_CHARGE_AS_MARGIN_2026-10-14.md`,
fix 2. K8: `docs/market_research/network_charges_uk_2016_2024.md` §7d, the Knowledge page
`non-commodity-costs` (residuals), and the knowledge map's "Network charges (electricity)" row.
This is a world fidelity change, decided from Ofgem's model and blind to company results.

## The change

- `simulation/policy_costs.get_electricity_network_cost_per_mwh(date, "resi")` returns the cap's
  **per-kWh** NC allowance for the cap period in force (v1.31, 15-row median), not the whole
  allowance / 3.1 MWh. SME and I&C are unchanged.
- New `get_electricity_network_fixed_per_day(date, "resi")`: the cap's NC **nil** allowance / 365.
  Zero for SME and I&C.
- All three settlement writers (`run_hedged_term`, `run_deemed_term`, `run_flex_term`) charge
  `network_cost_gbp` = per-kWh x volume + fixed / 48 per half-hour. Pass-through and flex revenue
  pass through the per-kWh part only, because the standing charge recovers the fixed part.
- Every price-floor reader of the per-MWh figure follows by construction: the renewal lock
  (`renewals.py`), the rival cost floor (`competitor_reference.cost_floor_gbp_per_mwh`), and so
  the company's `pre_margin_unit_rate` and `term_contribution_per_year`.

## What each number counts

- **Network cost per household-year:** the supplier's network charge for one domestic electricity
  supply point over a year, ex-VAT. It is charged on every settled half-hour of the term.
- **Renewal floor:** the per-MWh unit-rate floor the desk reads, in GBP/MWh ex-VAT.

## The table at real inputs (printed before the code was written)

Old charge = whole table x kWh. New charge = nil + per-kWh x kWh. GBP per year, ex-VAT.

| date | 1,500 kWh | 2,700 | 3,100 | 4,500 | 8,000 |
|---|---|---|---|---|---|
| 2019-06 | 68 → 74 | 122 → 121 | 140 → 136 | 202 → 190 | 360 → 325 |
| 2022-06 | 99 → 148 | 178 → 193 | 205 → 208 | 297 → 261 | 528 → 392 |
| 2024-06 | 104 → 176 | 186 → 213 | 214 → 226 | 310 → 269 | 552 → 378 |
| 2025-06 | 104 → 150 | 186 → 197 | 214 → 212 | 310 → 266 | 552 → 400 |

## Predictions, filed before the run

1. **The renewal floor and the rival floor drop.** The domestic per-MWh network falls from about
   £49 to £42/MWh in 2021/22, from £66 to £37.5 in 2022/23, and from £69 to £31 in 2024/25.
   Prediction: on the next run's held electricity renewals, **fewer than half sit on the floor to
   the penny** (it was 21 of 21 at d55598dd6). If most still sit on it, then writer 1's
   standing-charge-as-margin (B12, fix 1) is carrying the whole effect.
2. **Settled domestic network cost per household is redistributed, not just scaled.** Low users
   cost more and high users less. Post-2022, the book's domestic network line moves by
   Σ(nil x days) + Σ(per-kWh x kWh) − Σ(old x kWh). It rises if the book's mean domestic EAC is
   below about 3,100 kWh and falls if above. I have not read the book's mean EAC, so **I predict
   the sign only conditionally**. The next run's reading should state the mean EAC first and then
   check the sign against this.
3. **Pre-2022 moves are small:** under £10 a year per household at typical use, and under 5% of
   the network line.
4. **Churn: I cannot say.** Lower renewal floors make our prices keener, and a lower rival floor
   makes theirs keener too. The two act in opposite directions, so the net retention move is not
   predicted. Attributing it needs the one-variable run (rival floor held on the old figure),
   which is not done here.

## Not changed, named

- **Void meters** (`sim/customer_state_layer.as_void_row`) zero `network_cost_gbp` with the volume
  fields. A vacated domestic meter still bears the fixed DUoS share in reality, so void rows now
  under-state network by about £0.25–0.35 a day after April 2022. This is outside this atom's
  file scope and is filed with the finding below.
- **The deemed and flex writers book no standing-charge revenue.** They now bear the fixed network
  cost with nothing recovering it, which makes them more conservative. Filed:
  `WORKER_FINDING_THE_DEEMED_AND_FLEX_WRITERS_BOOK_NO_STANDING_CHARGE_SO_THE_FIXED_NETWORK_SHARE_HAS_NO_RECOVERY_2026-11-09.md`.
- **SME** stays on the whole allowance per MWh, with a 1.5x domestic standing charge (GAP: no
  non-domestic residual band table).
