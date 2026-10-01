**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# Pre-registration: the year-one quote and the amount it is met by, on one basis

Claim `put-the-year-one-bill-shock-quote-and-review-on-one-basis`. Filed 2026-10-01 BEFORE the code
is run on a world. No figure below has been computed from a run. Acts on
`SEAT_FINDING_THE_YEAR_ONE_QUOTE_AND_THE_REVIEW_IT_IS_MET_BY_ARE_ON_DIFFERENT_BASES_2026-10-01.md`;
the previous run is `records/SEAT_PREREGISTRATION_PB4_THE_OPENING_DD_AT_THE_RATE_SOLD_2026-10-01.md`
(31 of 31 defined, 9 shocked, 0.290; first-renewal rise quartiles −0.270 / −0.084 / +0.333).

## The two gaps, as found in the code

1. **VAT.** The quote is inc-VAT (`opening_monthly_amount` grosses the sold rate by 5%). The year it
   is met by is summed from settlement `revenue_gbp`, which `simulation/hedged_settlement.py` and
   `simulation/gas_settlement.py` settle ex-VAT. The company's own DD book reviews bill
   `total_amount_gbp`, which is inc-VAT, so the world's shock was the one place reviewing ex-VAT.
2. **Standing charge.** The quote charges every leg `STANDING_CHARGE_RESI_P_PER_DAY` = 53p/day, a
   2024 figure, for both fuels and every year. The bills carry the world's dated charge
   (`simulation.policy_costs`): electricity 24p (2016) to 61p (2024), gas 22p to 31p, ex-VAT.

## The change (one variable: the basis)

- **No new VAT rule.** The world grosses its settled year with the VAT rule it already has,
  `simulation.price_cap_enforcement.DOMESTIC_VAT_RATE` (VATA 1994 Sch 7A). The door keeps the rule it
  already uses. Both are 5%.
- `opening_monthly_amount` gains an optional `contracted_standing_charge_per_day_ex_vat`, the
  standing charge printed on the account's first bill. It crosses the door for the same reason the
  sold rate does: both parties hold it. When absent the 53p fallback is unchanged, so the DD-book
  caller in `run_phase4c_on_phase2b` does not move.
- `simulation.experienced_bill_shock` passes each leg's first-month daily standing charge, and puts
  every amount it compares on the inc-VAT basis: the year's bills, the prior year's bills, and the
  spend each review is computed from. That covers later renewals as well. The ratio there is
  VAT-invariant except for the review's round-up to the pound.

Nothing the world decides reads this quantity yet, so the books and the departures do not move.

## Arithmetic printed before the run (one leg, MEDIUM TDCV, rates as the 2016 world settles them)

Electricity 2016, 3,100 kWh at ~£140/MWh ex-VAT plus 24p/day: the old quote is £54.0/month. On one
basis it is £45.7, so the quote moves by a factor of 0.85, and the met amount gains 5%. A rise
therefore moves as (1 + r) × ~1.24. Gas 2016, 12,000 kWh at ~£30/MWh plus 22p/day: the factor is
~1.30. Electricity sign-ups in 2023–2024 (53p–61p ex-VAT, so 56p–64p inc-VAT, above 53p): the
factor is ~1.00–1.05.

## Predictions

| | Prediction | Why |
|---|---|---|
| R0 | **Placebo: later renewals.** Still 70 rows with 62 defined. The shocked set is identical except for any row whose old rise was within 0.02 of the 0.15 cut. Every later `rise_fraction` moves by less than 0.02. | Both sides of a later comparison are scaled by the same 5%; only the review's round-up to the pound can move them. A larger move means something other than the basis changed. |
| R1 | First renewals: still **31 of 31** in scope defined. | Every leg that had a sold rate has a first month of standing-charge rows too. |
| R2 | **Every** first-renewal `rise_fraction` is at least as high as it was, except possibly a 2023–2024 electricity-only sign-up (factor ≈ 1). | The world's inc-VAT standing charge is below 53p for every gas year and every electricity year up to 2022, and the met amount gains the 5% that the quote already had. |
| R3 | First-renewal median rise moves from −0.084 into **[+0.05, +0.25]**. The shocked share moves from 0.290 into **[0.35, 0.65]**. | Most first renewals are 2016 sign-ups, which have a factor of ~1.24–1.30: (1 − 0.084) × 1.25 ≈ +0.14. |
| R4 | **share(first) > share(later)**: year one shocks more than later years once the basis is one. | The opening DD is set from a TDCV band and not from the household's own use, so its error is the year-one shock, which is the page's "DD set wrong, then reset". This is a direction, not a size. |

## What would refute the plan

- If R0 fails, the run is not one-variable and is discarded.
- If the first-renewal share is ≥ 0.75 or the median is above +0.35, something beyond price basis
  separates the quote from the year. The most likely cause is the consumption estimate (TDCV MEDIUM
  against the household's own use). That would not be a defect: it is the shock this quantity
  exists to see. But then the hazard swap would carry a TDCV-band gradient, and that has to be
  named before the swap.
- If R2 fails on a 2016–2022 row, the standing charge read from the first bill is not the charge
  that was settled, and the reader is wrong.

## The run

`/var/tmp/se-pb4-shock-out/run_sold_rate.py` with only its worktree path changed, pointed at this
claim's worktree. The previous `events.json` is kept as `events_rate_sold_7a119f52c.json`.
`analyse.py` is re-run byte-unchanged and its sha256 is checked against `analyse.sha256`.

## Result (appended after the run; nothing above is edited)

The run used a worktree at `d3009f5a9` plus this claim's code, and took 1,396 s. The previous output
is kept as `events_rate_sold_7a119f52c.json`. `analyse.py` was re-run byte-unchanged, and its sha256
was checked.

| First renewals (36) | rate sold, mixed basis | one basis |
|---|---|---|
| Defined | 31 | **31** |
| Shocked | 9 (0.290) | **17 (0.548)**: direct debit 14/26, standard credit 3/5 |
| Rise quartiles | −0.270 / −0.084 / +0.333 | **−0.056 / +0.222 / +0.788** |

Later renewals: 62 defined, 20 shocked (0.323), median rise +0.074.

| | Verdict |
|---|---|
| R0 | **FAILED AS WRITTEN; the mechanism holds exactly.** The shocked set moved by 2 rows, both inside the allowance (0.138→0.167 and 0.153→0.145). But the largest later move is 0.061, not under 0.02. All 62 later rows recompute EXACTLY (to 1e-6) from the run's own household bills, as `ceil(1.05·this)/ceil(1.05·prior) − 1` for direct debit and an unchanged ratio for standard credit. So nothing but the review's round-up to the pound moved them. The 0.02 bound assumed ~£50 payments; a £1 round-up on a £16–£33 payment is 3–6%. The size was mispriced, not the attribution, so the run is NOT discarded. That is a call made after the answer, and it is recorded as one. |
| R1 | **HELD.** 31 of 31. |
| R2 | **HELD.** All 31 first-renewal rises went up. The factor (1+new)/(1+old) runs from 1.07 (a 2024 electricity sign-up) to 1.51 (2016 gas). That is wider than the 1.24–1.30 printed above, because a low-use leg carries the standing charge as a larger share of its quote. |
| R3 | **HELD.** Median +0.222 is inside [+0.05, +0.25]; share 0.548 is inside [0.35, 0.65]. |
| R4 | **HELD.** 0.548 > 0.323. |

**The plan-level refutation did not fire** (share < 0.75, median < +0.35). But the consumption leg
it names is visible in the tail: **7 of 31 first renewals rise by more than 100%** (+1.04 to +7.15).
These are winter-peaked, electrically heated homes whose registry EAC (1,600–2,500 kWh) is a fraction
of what they use. PROS-2016-0098 is quoted on 2,470 kWh and billed £300–600 a month all winter.
Without those 7, year one reads 10/24 shocked (0.417) with a median of +0.107, against later
renewals' 0.323 and +0.074. That tail is the subject of
`SEAT_FINDING_THE_YEAR_ONE_SHOCK_TAIL_IS_AN_EAC_A_FRACTION_OF_THE_HOMES_USE_2026-10-01.md`.
