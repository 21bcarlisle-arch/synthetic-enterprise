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

**Reverse:** delete this file.
