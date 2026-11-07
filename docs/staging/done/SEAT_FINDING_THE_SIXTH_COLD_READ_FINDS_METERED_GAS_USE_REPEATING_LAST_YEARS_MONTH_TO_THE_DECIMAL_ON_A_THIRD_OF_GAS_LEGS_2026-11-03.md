**Severity:** BLOCKING · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `unminted`

# The sixth cold read finds metered gas use repeating last year's same month to the decimal on about a third of gas legs, so the weather does not reach them (2026-11-03)

**Source.** This is class N13 of the sixth cold read, on the 85b044be54 book
(`docs/staging/records/SEAT_READING_THE_SIXTH_COLD_READ_ON_THE_85B044BE54_BOOK_2026-11-03.md`, reader's O23).
It is BLOCKING because it is a new class, and the correctness stretch cannot exit while it stands.

**What the page prints.** OCC-924f5fe3f622, Section B account 1, stage 3:
- "2021 5,979 kWh / 2022 5,979 kWh / 2023 5,979 kWh" for gas;
- "62 bill(s), 0 on an estimated read";
- beside them, the page's own words: "the year-to-year swing is winter temperature".

**What the record holds** (the published pages, `site/data/customers/*.json`, whole calendar months only):
- **OCC-924f5fe3f622g.** This is a prepayment meter. It prints 879.0 kWh every January and 860.2 kWh every December
  from 2020 to 2024, and 161.7 kWh every July.
- **OCC-098fe5fa8b46g.** These are actual reads on a volume register. October to January read
  724.3 / 1,060.0 / 1,408.6 / 1,439.2 kWh in winter 2020-21, and again to the 0.1 kWh in winter 2021-22. The
  volume register advances to match each month.
- **Book-wide, gas, actual or prepayment-meter read on both sides.** 1,635 of 4,413 same-month year-on-year
  pairs (37%) repeat to 0.1 kWh. The rate is 26–43% in every year from 2017 to 2025, and 20–44% in every
  calendar month, winter included.
- **Electricity.** 0–8% a year, so the effect is on the gas leg.
- **By leg.** 114 of 383 gas legs with six or more pairs repeat on 10% or more of their pairs. The legs span
  `SYN`, `PROS` and `OCC`.

**Why it is wrong.** Domestic gas is mostly space heating, and heating follows outdoor temperature. Two
winters as different as 2020-21 and 2021-22, or a crisis winter (2022-23), cannot meter the same kWh to
the decimal month after month. The page claims weather drives the swing, but on these legs nothing does.

**What it most resembles.** W1_14
(`docs/staging/records/WORKER_RESULT_THE_HDD_LEG_READ_THE_NORMAL_FOR_91_OF_95_GAS_PREMISES_THE_RUN_SETTLES_2026-09-30.md`):
- drawn gas premises that no roster entry held read the 1991–2020 monthly normal;
- that record measured "premises with 2018 == 2022: 15/15 -> 0/15" after `weather_inputs.adopt_book`;
- that run settled 95 gas premises, and this book has 514 gas legs.

**I cannot yet say** which of two explanations holds. (1) The world's demand reads the normal: W1_14's fix
regressed, or never reached these legs. (2) The company bills a profiled estimate (an annual quantity spread by a
fixed seasonal shape, which repeats by construction) and labels it actual. The blind row-writer named (2), and the
meter's volume register advancing to match does not rule it out. If (1), the fault is world-side; if (2), it is
company-side. Occupier accounts and later
cohorts are both candidates. That is the first measurement for whoever draws this: for each repeating leg, which
sky its demand read, at the run that built 85b044be54. Under (1) the work is world-side
(`sim/`, `simulation/`); under (2) it is in the company's read path.

**Why no row caught it.**
- The suite bounds annual use per account and the book median.
- No row asks whether metered use moves with the weather year on year.
- The blind row written with this finding (`INV_…` in `docs/design/DOMAIN_INVARIANTS.yaml`, written from the
  knowledge layer only) grades that.

## The side, decided (2026-11-03)

**The world repeats, not the bill.** On 43 of the 46 repeating legs I could join, the run's own
`true_consumption_kwh` repeats. Every repeating leg except two reads the 1991–2020 monthly normal,
for one of two reasons:
1. **The OCC leg was never adopted** (15 legs). This is **fixed**: `weather_inputs.adopt_record` is
   now called on admission.
2. **The premise is more than 5 km from any cell the store holds** (29 legs). On today's starting
   book that is 490 of 1,046 records, including 227 of 477 gas premises, because the store was
   built on 11 Oct and the book has been redrawn since. **This one stands.** The remedy is a store
   rebuild over today's book. It is a baseline fidelity change that moves every gas figure, so it is
   pre-registered and run on its own.

Full record: `docs/staging/records/SEAT_RESULT_N13_THE_WORLD_REPEATS_GAS_USE_BECAUSE_HALF_THE_BOOK_HAS_NO_SKY_2026-11-03.md`.

## Cause 2 closed at the store (2026-11-03, later the same day)

The store was rebuilt over today's book with HadUK temperature for every book cell: 836 cells, and
**0 of 1,052 settled records** (0 of 477 gas) now lack a sky, down from 490 (227). The 227
former-normal gas premises read a 2022 HDD 13.1% below the normal on the mean, and none reads
the same January in 2018 and 2022. A control now asks the settled book rather than the roster and
goes red at the old store. Record:
`docs/staging/records/SEAT_RESULT_THE_WEATHER_STORE_NOW_COVERS_THE_DRAWN_BOOK_2026-11-03.md`.

**This finding stays BLOCKING until the next published run shows it.** That means the blind
year-on-year row grades no world-side repeats on the full book. A fixed cause is a prediction about
that run, not the run. One residual is still open: PROS-2019-0208g meters a flat 4.5 kWh a day from
April 2021 with a sky. That is a separate question, and it is in the N13 result.

**Reverse:** delete this file.

## Graded on the fd91027799 book (2026-11-07)

`INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR` now has an evaluator (`ev_gas_monthly_use_repeat`
in `tools/domain_invariant_runner.py`). On the ledger of `run_output_fd91027799_20261105T004022Z.json`,
the first published-class run after the store rebuild:

| | count |
|---|---:|
| gas legs with a measured month-pair | 140 |
| month-pairs (whole calendar month, A/C/M read at both ends, above the leg's zero-use floor) | 3,743 |
| pairs repeating to 0.1 kWh | **10 (0.27%)**, under the row's 1% book bound |
| legs breached (3 or more repeats) | 1 (SYN-2016-206g) |
| legs flagged (exactly 2) | 2 (PROS-2017-0183g, SYN-2016-258g) |
| legs with winter dispersion under 1% | 0 |

On the 85b044be54 pages it was 1,635 of 4,413 (37%). The world-side repeat this finding named is
gone from the heating months. PROS-2019-0208g, the flat 4.5 kWh a day residual, has 54 pairs and 0 repeats here.

**The residual, named.** All seven repeats on the three legs are **July** months
(SYN-2016-206g: July 2019, 2022 and 2023 at 421.4 kWh). The summer gas, hot water and cooking,
has no year-to-year term. This is the same mechanism as N17 on electricity: a base load with no
household draw from one year to the next. It is filed as the W2_30 slice in
`docs/design/simplifications/W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape.yaml`
(`n17_year_on_year_slice_note`), and the gas row grades it from now on. It does not breach the
book bound. This finding moves to done/; the residual is N17's.
