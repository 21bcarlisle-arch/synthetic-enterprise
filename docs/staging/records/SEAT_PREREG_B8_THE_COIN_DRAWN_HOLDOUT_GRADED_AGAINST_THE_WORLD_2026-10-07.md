# Pre-registration: what the coin-drawn holdout must return

**Written before the graded runs**, after a smoke run at seed 7 with about 280 decisions per arm.
**Atom:** `B8_discovered_price_sensitivity_holdout`.

## The set

Each seed builds three arms with `tools.grade_coin_drawn_holdout`.

- **Real.** The treated arm is offered £7.5/MWh below the world's default.
- **Null.** There is no cut, so the true effect is exactly 0.
- **Planted.** The treated arm gets the world's holdout P(stay) plus 0.05.

Each arm is graded at two sizes:

| size | households per year | decisions per arm |
|---|---|---|
| S | 850 | about 6,000, the top of the reply's 3,000–6,000 |
| L | 4,700 | about 33,000 |

## Predictions

The smoke run gave a true effect of +0.011 at a stay share of 0.60. From that:

1. **Real arm, size S.** The true effect is between +0.008 and +0.020. The 95% half-width is about 0.018, so the verdict is "undecided" on most seeds. The interval covers the truth on all three seeds.
2. **Real arm, size L.** The half-width is about 0.0075, so the verdict is "raises staying" on this one seed, with about 80% power. The interval covers the truth.
3. **Null arm, both sizes.** The verdict is "undecided" and the interval covers 0. A "raises staying" here counts against the method.
4. **Planted arm, size S.** The truth is just under 0.05, because the cap at 1 binds on a few rows. The verdict is "raises staying" and the interval covers the truth.
5. **Cost.** It stays under 10 ms and under 400 day-records per decision. Memory does not grow with the set beyond its rows. Against the 2.7 MB of a settled customer-year, that is at least 100 times cheaper per decision.

If prediction 1 holds, the reply's 3,000–6,000 per arm is too few for this offer in this world. The deciding size is then roughly 30,000 per arm, and the result will say so.
