**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# The 12% is the company pricing its lower margin back into renewal unit rates

Claim `attribute-the-renewal-feedback-on-the-ex-vat-standing-charge`. Results are against two
pre-registrations, each written before its arms returned:
- `docs/staging/records/SEAT_PREREGISTRATION_WHERE_THE_UNATTRIBUTED_12_PERCENT_OF_THE_EX_VAT_STANDING_CHARGE_RUN_COMES_FROM_2026-10-01.md`
  (landed `ed7b4666f`, before its answer)
- `docs/staging/records/SEAT_PREREGISTRATION_WHICH_LEARNED_WRITER_RECOVERS_THE_STANDING_CHARGE_2026-10-01.md`

**Disposition of the draw's duplicate-work note.** "Already held under this very id" was this
draw's own write. The only seat process on the id was this session (pid 2218269), and no rival
`surgical_land` was running.

## The answer

In P3 of `SEAT_FINDING_THE_WORLDS_STANDING_CHARGE_IS_NOW_EX_VAT...`, revenue fell by £1,356 less
than the standing charge did. That £1,356 is **renewal unit rates rising** because the
supplier's learned writers read its own lower realised margin. It is not a defect: a real supplier
whose fixed recovery fell would see the same thing in its P&L.

| writer | £ of the +£1,356.19 unit revenue | renewals moved |
|---|---|---|
| `portfolio_premium` (book-wide margin rate → premium) | **+£1,040.51** | 876 |
| `margin_surcharge` (a loss-making prior term is recovered from the next one) | **+£320.63** | 222 |
| `price_cap` clamp (takes back part of the rise where the cap binds) | −£9.20 | 10 |
| `profitability_uplift` | £0.00 | 0 |
| residual: rate×kWh against settled unit revenue | £4.25 | — |

The median last-observed portfolio margin rate went from 0.2669 to 0.2496.

## How it was established

Two pairs of default worlds were run, one process per arm, in series, on the same base. Every
arm reproduced `n` = 319,176 records.

- **Q0 holds. The directed freeze is EQUIVALENT, not untested.** The default world runs
  `renewal_margin_arm = "flat_rules"`. `renewal_margin_uplift` returns zero for that arm before
  it calls `observed_account_state`, and the call count was **0 in all four arms**. So freezing
  `value_based_renewal._observed_standing_charge_gbp` cannot move anything in this world. The
  candidate named in the earlier finding was never reachable.
- **Q1 holds.** Unit revenue (revenue − both standing charges) rose by **+£1,356.19**. kWh was
  identical on every (account, fuel, term, year) key. Both settlement writers add the standing
  charge to revenue 1:1, and no later writer reassigns record revenue.
- **Q2: a feedback.** By term index, **first terms move by exactly £0.00**, and every later term
  moves. The rise is spread from 2016 to 2025 and is zero in 2023 electricity, the year the cap
  binds.
- **R1 holds.** The rate entering the chain (`struck_unit_rate_gbp_per_mwh`) is identical on all
  3,250 renewals in both arms. The strike does not read the standing charge; only the learned
  writers do. A placebo of old against old gave zeros on every row.
- **R2 MISSED, correction beside the claim.** I predicted that only the three learned writers
  would differ. The cap clamp also moved, on 10 renewals, and took back £9.20 of the rise. The
  miss is small, but the prediction was wrong.
- **R3 holds.** Portfolio premium carried 77%, against a predicted "more than half".

The VAT-rate merge in this claim was edited in the worktree while the first pair's old arm was
running. It is value-neutral (0.05 is still 0.05), so both arms of each pair read the same numbers.

## What it means

- **On value created versus value transferred:** about 12% of the VAT and level the world removed
  from supplier revenue comes back from the same customers as higher renewal unit rates.
  That is a transfer, and the learned writers make it automatically. Any measured "value created"
  that is downstream of a standing-charge change should therefore be read net of it.
- **On the pricing chain:** the portfolio premium learns from an all-in margin rate. That
  includes the standing charge, which the customer pays per day and not per kWh. So a fall in
  fixed recovery is repriced per kWh. That is defensible as supplier behaviour, but it is a
  basis crossing. If it ever matters, the premium could learn from a commodity-only margin.
  This is not filed as a defect.

## The VAT rate: one home (landed `ed7b4666f`)

The three literal 0.05s are gone:
- The figure lives only in `docs/domain_artefact_library/regulatory/uk_vat_rates.json`.
- The world reads it in `price_cap_enforcement` (`DOMESTIC_VAT_RATE`).
- The company reads it through `dual_fuel_bill.VAT_RATES` → `domain_invariants.vat_rate_for_segment`.
- `tariff_comparison.VAT_RATE_DOMESTIC` and `VAT_RATE_BUSINESS` are deleted.

Two readers remain, because the wall requires two. The control's agreement leg is now
`test_the_rate_is_declared_only_in_the_commons`. Three mutations were applied and reverted, and
each turned it red.

## Still open (carried from the earlier finding)

- 2025 standing-charge row: still clamps to 2024. It needs adding from the cap level model, as a
  coverage change with its own run.
