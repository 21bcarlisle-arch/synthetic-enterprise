**Severity:** BLOCKING · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `unminted`

# N17. Metered electricity use barely moves from one year to the next: the median month changes 1.1% against last year's, where GB homes change about 15% (2026-11-04)

**Source.** The eighth cold read's named check (b), run by the seat over all 1,292 page files of the b3ce2a4e73
book (`records/SEAT_READING_THE_EIGHTH_COLD_READ_ON_THE_B3CE2A4E73_BOOK_2026-11-04.md`). Built pages:
`/var/tmp/fresh-grade-b3ce2a4e73/tree/site/data/customers/`; script `/var/tmp/eighth-read/scripts/b_ratio.py`.

**What the record shows.** These are same-month, year-on-year pairs, with an actual or prepayment read on both
bills and an identical period:

| fuel | pairs | median \|r−1\| | p90 | share moving < 1% | within 0.1 kWh |
|---|---:|---:|---:|---:|---:|
| electricity | 5,179 | **0.011** | 0.186 | **48.6%** | 352 (6.8%) |
| gas | 4,107 | 0.129 | 0.358 | 3.5% | 14 (0.3%) |

- Every cohort carries it: OCC 50 of 821 exact repeats, PROS 109 of 1,375, SYN 193 of 2,925. Read type does not
  matter: actual 177 of 2,857, prepayment 175 of 2,322.
- 43 electricity legs repeat to 0.1 kWh three or more times. SYN-2016-120 does it 15 times in 94 pairs,
  SYN-2016-277 15 of 91, and PROS-2018-0176 13 of 67. SYN-2016-368 is the mover slot's household.
- It is not chance. Pairs within 0.1 kWh are 22% of those within 1 kWh, where a smooth spread would give about 10%.
  And 61% of all electricity pairs sit within 5 kWh of last year's month.

**Why it is wrong.** `docs/market_research/how_far_a_settled_eac_sits_from_next_years_use.md` (NEED, 330,884
dwelling-year pairs) gives a median |r−1| of 0.147 for **annual** domestic electricity, centred on 1. That is an
upper bound for one household, because it includes change of occupier. A single month varies more than a year,
because weather, holidays and occupancy do not average out. The book's electricity is about thirteen times
smoother than the annual figure. Its gas, at 0.129 a month, is credible.

**What it most resembles.** N13 (`SEAT_FINDING_THE_SIXTH_COLD_READ_FINDS_METERED_GAS_USE_REPEATING_LAST_YEARS_MONTH_TO_THE_DECIMAL_ON_A_THIRD_OF_GAS_LEGS_2026-11-03.md`).
- N13 measured electricity at "0–8% a year" of exact repeats and scoped it out: "the effect is on the gas leg".
- `records/SEAT_RESULT_N13_THE_WORLD_REPEATS_GAS_USE_BECAUSE_HALF_THE_BOOK_HAS_NO_SKY_2026-11-03.md` counted
  263 of 567 resi electricity premises with no weather cell, beside the 227 of 477 gas premises.
- The fix (7ec8b1030) brought gas from 37% exact repeats to 0.3%. It did not move electricity.
- The exact repeats are N13's shape on the other fuel. The near-flat spread is wider than N13. Even a premise
  whose sky exists has a non-heating load with almost no year-to-year draw.
- **I cannot yet say** which of these is the cause. The pages are the supplier's side, and the bill prints what
  the world metered (focus item 1: world 10, billed 10 on gas).

**Prediction, filed before the measurement.** In the world's own settlement:
- the exact repeats concentrate on premises with no weather cell;
- the near-flat spread is on every premise, because the non-heating base load has no year-to-year term.

If the repeats do not concentrate on those premises, the cause is elsewhere.

**The row this owes (ruling step 6).** It must be written blind, from the knowledge page above:
- on actual and prepayment month-pairs, per fuel, the book's median \|r−1\| sits within a two-sided band from NEED;
- and the share of pairs within 0.1 kWh does not exceed what chance gives.

`INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR` still has no evaluator in the runner (focus item 1), so this row
and that one are one build.

**Reverse.** Delete this file. Nothing outside `docs/staging/` was touched.

## Done (2026-11-07): the side is the WORLD, and the row now grades it

**The row.** `INV_ELEC_MONTHLY_USE_MOVES_YEAR_ON_YEAR_LIKE_A_HOUSEHOLD` is in
`docs/design/DOMAIN_INVARIANTS.yaml`. It was written from the NEED page and SERL
(`how_much_a_same_households_use_moves_year_on_year_and_in_2022.md` section 2A) before the book was
graded. Its evaluator is `ev_elec_monthly_use_moves`.
- **Leg A:** the book median |r−1| must fall in [0.05, 0.30].
- **Leg B:** within 1 kWh of last year's month, the share within 0.1 kWh must not exceed 3/21 (a flat
  spread at one decimal place) beyond the 99.9% binomial bound.

**On the fd91027799 book** (ledger of `run_output_fd91027799_20261105T004022Z.json`):

| leg | value | bound | verdict |
|---|---:|---|---|
| A: median \|r−1\| over 4,851 measured pairs | **0.0075** | [0.05, 0.30] | breach (below) |
| B: within 0.1 kWh, of 1,743 within 1 kWh | **510 (29.3%)** | ≤ 16.9% (chance 14.3%) | breach (above) |
| legs with 3 or more repeats | 58 | | flag |

It is worse than b3ce2a4e73's 0.011.

**The three-way split** (script `/var/tmp/n17/split.py`; world truth = the run's
`meter_read_log.true_consumption_kwh` on the same months):

1. **World truth against the billed read.** Both give a median of 0.0075. Every split below agrees to
   the fourth decimal. The bill prints what the world metered, so **the side is the world.**
2. **OCC, SYN and PROS.** The medians are 0.0134, 0.0065 and 0.0079. Every cohort carries it, as you
   found. Cohort is not the cause.
3. **Weather cell, and the demand provider it decides.** This is the cut that separates:

| premise | electricity premises | pairs | median \|r−1\| (world) | within 0.1 kWh |
|---|---:|---:|---:|---:|
| fabric refused "no weather archive", settles on `legacy_pc1_rescaled` | 519 of 712 | 3,601 | **0.0056** | 9.2% |
| fabric eligible, `fabric_physics` | 187 | 1,127 | 0.0450 | 1.6% |
| real half-hourly reads, `hh_metered_reads` | 4 | 123 | 0.1146 | 0% |

**Against the prediction filed above:**
- *"The exact repeats concentrate on premises with no weather cell."* **This half held, with a correction
  to what "no weather cell" means.** 333 of the 351 billed pairs within 0.1 kWh (95%) are on the 519
  refused premises.
  - The 3 Nov store rebuild (7ec8b1030) gave every premise a temperature sky. That is why gas moves
    now. It did **not** give them the full ERA5 archive (wind, cloud, precipitation) that the
    electricity fabric engine needs.
  - On 3 Nov 440 cells were still temperature-only (f763637d83). The refusal reads "the store holds no
    complete weather for it".
  - So the brief's "the no-weather-cell half can be refuted outright" was itself wrong. That half is
    the cause.
- *"The near-flat spread is on every premise."* **This half is refuted in its stated form.**
  - Fabric premises move: summer, where the base load dominates, 0.036; winter 0.046; 2022 0.077.
  - The flatness belongs to the fallback shape. `legacy_pc1_rescaled` moves 0.005 to 0.007 in every
    season, and **0.0042 in 2022**. Three in four of the book's electricity homes did not respond to
    the crisis at all.
  - The fabric premises still sit just under the band's lower bound (0.045). Their ordinary-year
    base load moves 2.5–3.6%, against 6–17% for the four real HH homes. That is a smaller, second
    question.
- The four real half-hourly homes land inside the band. That is an external check on the band itself.

**Filed.** The world side is filed as a slice of W2_30
(`docs/design/simplifications/W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape.yaml`,
`n17_year_on_year_slice_note`), citing NEED and SERL. There are two separable remedies:
- finish the ERA5 pull (W1_14), which moves premises onto fabric;
- give the fallback and the fabric base load a household year-to-year term.

No company estimator is at fault, so there is no company fix. The forecasting consequence stands: on 519 of
712 premises a per-customer forecast has nothing to infer.
