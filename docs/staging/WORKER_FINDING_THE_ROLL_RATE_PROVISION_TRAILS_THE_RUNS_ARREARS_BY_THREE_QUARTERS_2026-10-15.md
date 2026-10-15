**Severity:** LATENT · **Lane:** E_finance_treasury · **Epoch:** 4 · **Atom:** `E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build` · **Claim:** `the-provision-moves-in-the-quarter-arrears-build`
**Knowledge:** bad-debt-provisioning -- `docs/market_research/bad_debt_provisioning.md`, "A provision matrix whose loss rates come from the company's own roll rates" (IFRS 9 B5.5.35, B5.5.52)

# The roll-rate provision trails the run's arrears by three quarters, and the run's published provision does not

**Fate (2026-10-15):** ATOM -- the open half of E6's first slice; graded by `tests/company/finance/test_the_provision_charges_expected_loss_as_arrears_build.py` (strict xfail, flips when fixed).

## Pre-registered, then measured

The prediction was written before the run's quarterly series existed (`/var/tmp/writeoff/r4/PREREG.md`). Run: seed 61109, all_wins, 12 founders (r3's recipe), at 751184c75. That is 6442d41af plus an auto-salvage of six generated observability files, so the code is the same. The switch was off for the run, and both stocks were read afterwards on its ledger at each quarter end.

- **Clock:** the run's own arrears stock, meaning money on bills unpaid more than 30 days.
- **Build quarter:** the largest rise in 2021Q1-2023Q4 is 2023Q4 (GBP 888 -> 1,895). 2022Q4 is close behind (GBP 769 -> 1,668).

| Stock | `lag_peak` | `lag_xcorr` | Prediction |
|---|---|---|---|
| Roll-rate matrix (`roll_rate_provision_stock`, overlay none) | **3** | **3** | 0, **wrong** |
| Centrica-rate matrix (`default_belief.provision_stock`, what the run publishes) | 0 | 0 | not predicted |

## Why it lags

- The learned loss rates for money aged 0-2 months are low: live direct debit 0.02-0.15%, live other 0.14-1.2% (2022-09-30). They were learned from 24 months of young arrears that cured.
- So 2022Q4's arrears doubling moves the roll-rate stock by GBP 1.45 (210.75 -> 212.20). The Centrica-rate stock moves GBP 168 in the same quarter.
- The roll-rate stock catches up only once that money is four months old or more, where the learned rates are 30-50%. Its largest rise is 2023Q3, while arrears fell.

The overlay, at either of its published ends, is a fixed share of the matrix. It scales the lag and does not remove it. IFRS 9's remedy is a forward-looking adjustment (B5.5.52) that responds to current conditions. Nothing here has one.

**What I cannot yet say:** six synthetic book shapes did not reproduce the lag. In each one the crisis cohort's own uncured rolls dominated the young-age rates at once. The dilution explanation above comes from the run's loss-rate table, and no controlled book has tested it yet.

## Decisions

- **`ROLL_RATE_PROVISION` stays off.** Turned on, it would publish beside the Centrica stock, which stays the run's provision. So it moves no published margin either way. F11 points the same way. A provision that charges the crisis three quarters late flatters 2022 margins, and that error runs in favour of our own thesis.
- **E6 moves L0 -> L1.** The provision is built and its named control exists and grades it. L2 is not claimed. The first slice's property, the charge moving in the quarter arrears build, holds for the published stock and fails for the learned one.
- **EP17's switch condition** now names the remaining lag (3 quarters, learned rates) in place of "lags a year".

## Next bounded step

A forward-looking term keyed to the book's own arrears inflow. Example: the young-age rate floored at the cohort's observed roll rate over the last quarter, not the 24-month pool. Write it knowledge-first (K8): what B5.5.52 practice publishes, and GAP where it does not. It must pass the strict xfail above on a re-run of this recipe.
