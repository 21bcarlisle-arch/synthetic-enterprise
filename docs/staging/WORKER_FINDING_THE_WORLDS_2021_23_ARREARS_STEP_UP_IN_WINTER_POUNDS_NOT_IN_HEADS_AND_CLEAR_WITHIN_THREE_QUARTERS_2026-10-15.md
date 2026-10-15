**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `the-provision-moves-in-the-quarter-arrears-build`
**Knowledge:** debt-and-collections -- `docs/market_research/debt_and_collections.md` (Ofgem quarterly arrears and debt series, 2016-2026) and `docs/market_research/gb_domestic_bill_payment_failure_and_arrears_prevalence.md` (FCA Financial Lives 2020/2022/2024; Ofgem's "sharp rise in accounts in arrears during Q2 2022")

# The world's 2021-23 arrears rise in winter pounds, not in heads, and clear within three quarters

**Fate (2026-10-15):** ATOM -- folds into `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series`. Its grader reads the 2019 level only, and this is the crisis shape the same series publishes. It couples with `W2_42_debt_reaches_prepayment_only_by_the_legal_route`, because the PPM route closed in Feb 2023.

This is why E6's level gap is the world's and not the supplier's. The supplier's published provision moves in the quarter the run's arrears build (lag 0, E6's control). No provision basis can show a 2022 step-up the run's non-payment never takes. World fidelity: decided blind to company results, and **recorded, not retuned.**

## Measured

Run: seed 61109, all_wins, at 751184c75, read from the company's own ledger. This is not the world's payment truth that W2_38's grader reads, so it is a different instrument.

- Denominator: accounts billed in the 92 days to each quarter end. That is 92-203 accounts in 2021-23, so one account moves a share by 0.5-1 point.

| Quarter end | Accounts | > 30 days | > 90 days | GBP per account > 30 days |
|---|---|---|---|---|
| 2021-12-31 | 101 | 12.9% | 1.0% | 56 |
| 2022-06-30 | 111 | 9.0% | 1.8% | 62 |
| 2022-09-30 | 121 | 7.4% | 0.8% | 62 |
| 2022-12-31 | 139 | 7.2% | 0.7% | **146** |
| 2023-03-31 | 156 | 6.4% | 0.0% | **183** |
| 2023-09-30 | 173 | 5.8% | 0.6% | 56 |
| 2023-12-31 | 203 | 5.4% | 0.5% | 144 |

## Against the published record

- **Heads.** Ofgem counts a "sharp rise in accounts in arrears during Q2 2022", to 894,732 electricity. It dips in Q4 2022-Q1 2023, which is policy (EBSS and EPG), then jumps to 1,019,640 in Q3 2023. FCA's adults behind on electricity: 2.2% (2020) -> 3.0% (2022) -> 3.4% (2024). **The world's share behind falls through 2022, on both clocks.**
- **Pounds.** Ofgem: average arrears x3.1 from 2016 to 2025, and they persist ("intensity, not incidence"). **The world's intensity is seasonal.** It rises 2.4-3x each winter (2022-23 and 2023-24) and is back to GBP 56 by 2023Q3. Crisis debt in the world clears; in the published record it accumulates.

## Explanations to rank (blind to company results)

1. **Driver.** Payment failure runs off `income_stress` (`simulation/arrears_engine.py` `_DD_FAILURE_PROB`), which moves only on life events and not on the price shock. This is the 2026-10-08 finding's driver question, now seen in the crisis years.
2. **Cure.** World debt is settled within months. There is no route for unpaid crisis debt to stay unpaid, or to move to a plan or a PPM (W2_42).
3. **Sample.** 100-200 accounts on one seed. A 2-point rise in the share behind is within one seed's noise. The pound pattern repeats over two winters and is less likely to be noise.

Next bounded step: extend `tools/grade_world_debt_against_ofgem.py` from the 2019 level to the 2021-23 quarterly shape (heads and GBP per account), on the world's truth and pooled dice seeds, before any driver changes.
