**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — director steer 17 Oct

# Pre-registration: what drawing the fuel from the home does to the opening book

**Written 2026-10-17, before the correction was built and before any after-measurement.** The steer
is `docs/staging/advisor/DIRECTOR_STEER_THE_BOOK_IS_SINGLE_FUEL_DO_THE_KNOWLEDGE_WORK_2026-10-17.md`.
The knowledge page is
`docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md`.

## Before, measured on origin/main a33168b1f at seed 20260724, `SE_DRAW_POPULATION=1`

| Drawn founders (382 records) | account fuel | home has gas | n |
|---|---|---|---|
| | electricity | yes | 250 |
| | gas | yes | 107 |
| | electricity | no | 25 |

That is 382 homes, 0 dual, and 357 of 382 gas homes (93%). The roster adds 18 records in 13
homes, 5 of them dual. Trickle: 2 arrivals, both electricity accounts on gas homes. The census
script is `/tmp/fuel_census.py`, quoted in the result.

## The change, two steps, measured one at a time

1. **Arrangement.** The account-level coin is replaced by the home's arrangement. Founders take
   the held-book shape: P(dual | gas meter) = 0.83, otherwise half electricity and half gas. The
   trickle takes the switching shape: P(both | gas meter) = 0.90. A home with no gas meter is
   electricity only. The founder count is held at **382 drawn records** (the director's 400 less
   the roster's 18), so the settlement budget the founders consume does not move.
2. **Gas meter on the founders' homes.** `draw_premise` draws the meter first from EHS AT3.5
   (86.0%), then heating given the meter. This is the stock path's own mechanism since W2_20.

## Predictions

- **After step 1:** of the 382 records, about 357 / 382 of homes have gas, so expected records per
  home = 1 + 0.93 × 0.83 ≈ 1.77, giving **≈ 216 homes (range 205–228)**. **≈ 167 dual** (334
  records), **≈ 37 electricity only**, **≈ 14 gas only**.
- **After step 2:** P(gas) ≈ 0.86, so records per home ≈ 1.71, giving **≈ 223 homes (210–236)**.
  **≈ 159 dual, ≈ 48 electricity only, ≈ 16 gas only**. Gas supply points go from 107 to
  **≈ 175**; electricity from 275 to **≈ 207**.
- **Dual share of founder homes: ≈ 71% (64–78%).** The published household figure is 72%
  (CMA/GfK) and the supplier-count share is 70% (CMA PF ¶9).
- **Downstream directions, not magnitudes:**
  - Founder **gas volume up ~60%** and electricity volume down ~25%.
  - **Households down by ~40%** for the same customer-year budget, so per-household figures (CLV,
    cost-to-serve per household, arrears per household) rise and household counts fall.
  - **Gas-only accounts that "cannot leave"** (the 16 Sept finding) **fall from 107 to ≈ 16**.
  - **The published book's account count** is unchanged, because records are held.
- **What would refute this:** a dual share outside 64–78% after step 2, or a book whose record
  count moves.

## Held, and why

Records, not homes, because `FOUNDER_BOOK.yaml` defines its number as "accounts the supplier
launches holding". Each line of the book is a supply-point record, and the customer-year budget is
counted over those lines. Holding homes instead would add ~280 gas records and squeeze the
campaign, which is two variables. Which reading he meant is his, and it is raised as a proposal.

## Result, and a change of constant made after the prediction (kept beside it)

**As pre-registered, at P(dual | gas) = 0.83:**

| | Predicted | Measured |
|---|---|---|
| Step 1 homes | 216 (205–228) | 221 |
| Step 1 dual | ≈ 167 | 161 |
| Step 1 electricity only / gas only | ≈ 37 / ≈ 14 | 46 / 14 |
| Step 2 homes | 223 (210–236) | 228 |
| Step 2 dual share | 71% (64–78%) | 67.5% |
| Step 2 gas homes | 86% | 86.8% |
| Step 2 gas / electricity points | 175 / 207 | 175 / 207 |
| Step 2 gas only | ≈ 16 | 21 |

Every prediction held inside its range. Gas-only came out a little high.

**Then the constant moved, on evidence rather than on that result.** The advisor's supplier-accounts
research landed at 10:03 UTC:
`docs/staging/advisor/DIRECTOR_EVIDENCE_HOW_GB_HOUSEHOLDS_BUY_BOTH_FUELS_2026-10-17.md`. It shows
challenger books at 80–90%+ dual (Utility Warehouse, First Utility), against a market-wide figure
pulled down by incumbent legacy tails. Poesys is a challenger, so the founders now take the
switching/challenger shape, 0.90, and 0.83 is the floor of its range. **This is a second variable,
so it is reported separately:**

- **At 0.90, default seed:** 220 homes; **162 dual (73.6%)**; 48 electricity only (36 with no gas,
  12 split); 10 gas only; 83.6% gas homes.
- **Pooled over eight seeds (1,732 homes):** 76.4% dual, 84.9% gas homes, 3.9% gas only.
- **Predicted from the constants:** 0.86 × 0.90 = 77.4% dual. **Measured 76.4%.**
