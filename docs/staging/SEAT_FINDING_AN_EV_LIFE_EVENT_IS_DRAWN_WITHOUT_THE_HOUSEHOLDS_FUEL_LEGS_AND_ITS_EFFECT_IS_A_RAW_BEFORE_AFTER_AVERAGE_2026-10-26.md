**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `unminted`

# An EV life event is drawn without the household's fuel legs, and its effect is a raw before/after average

Defect 1 of the director's Explore steer (`docs/staging/advisor/done/DIRECTOR_STEER_EVERY_EXPLORE_EXAMPLE_MUST_MAKE_SENSE_TO_AN_ENERGY_READER_2026-10-26.md`).
Measured on the published 4ae8da9b0f book (752 households).

## What is wrong

- **21 EV arrivals** are on record. **1** lands on a gas-only household (SYN-2016-476, the one that was
  published), and **1** has a negative "effect" (that household's own: -65%, 1,353 -> 473 kWh/mo, which
  is its gas going from winter into summer after 16 Apr 2022).
- **5 of 21** state an effect outside the 1,750-3,300 kWh a year an EV adds at home
  (`docs/market_research/ev_charging_and_the_saving_against_petrol_and_diesel_2026-10-25.md` s.3).
  The household that would have taken the slot next, SYN-2016-050, states +17% (180 -> 211 kWh/mo),
  about 370 kWh a year.
- **16 of 21** have no full year of electricity use either side of the car, so no same-season comparison
  can be made.

## Root cause

- `simulation/life_events.py` draws the event without asking which fuels the household takes from us.
- `tools/generate_customer_reaction_chain.py:71` writes the effect as the mean of whatever leg's
  monthly kWh before and after the date, with no fuel restriction and no seasonal control.

Class: **units pass and the joins fail** (hypothesis 3 of the director's question), and **one-sided
tests**: nothing tested the sign or the size of the effect.

## What catches it now

`tools/generate_explore_cast.py` `_slot_failures("ev", ...)`: holds electricity; electricity over the
twelve months after the car minus the twelve before is in the band; the record's stated effect is in the
band. The EV slot is empty on this run with those counts named. **GAP:** the comparison is not
weather-normalised.

## What closes it

Draw the EV only for a household with an electricity leg; write its effect on electricity alone,
over a full year either side; the world-side invariant suite (the director's ruling, step 4) holds it.

## Correction and close, 27 Oct 2026

**Correction (beside the claim above):** the first remedy, "draw the EV only for a household with an
electricity leg", is **not taken**. A home that buys only its gas from us still has an electricity
supply and a driveway, and can still buy and charge a car; the world draws the car for the home
(`simulation/life_events.py`: residential and driveway), which is right. The defect is in the reader
alone. Reasoning on the knowledge page first (K8):
`docs/market_research/ev_charging_and_the_saving_against_petrol_and_diesel_2026-10-25.md` s.10.

**The fix:** `tools/generate_customer_reaction_chain.py` `_ev_effect` reads the car on our electricity
account only, over the twelve whole months either side of the arrival month, graded against the s.3
band of 1,750-3,300 kWh a year. Otherwise it says why in words: the car charges on a supply we do not
hold; the car arrived before or after we supplied the home; no full year; another electrical arrival
in the window. A stale effect is cleared on re-run. **GAP:** the read is not weather-normalised.
Test: `tests/tools/test_customer_reaction_chain.py::test_an_ev_effect_is_read_on_electricity_over_a_year_either_side_and_graded_both_ways`
(every branch asserted reachable).

**`INV_EV_ADOPTION_ELECTRICITY_ONLY`** says an EV "touches the electricity account only". That is a
rule about where the effect lands, not about who can draw a car, so it needs no correction.

**The 21 arrivals (4ae8da9b0f book, read from the published customer files), per household on its
electricity leg (or its only leg):** 1 in band, 3 out of band, 17 not observable.

| Household | Arrival | Before (3-month mean, any leg) | After (12 months either side, electricity) | Class |
|---|---|---|---|---|
| SYN-2016-050 | 2020-04-02 | +17% (180 -> 211 kWh/mo) | +2,891 kWh a year (157 -> 398 kWh/mo) | in band |
| SYN-2016-123 | 2021-02-06 | +38% (228 -> 315) | +1,043 kWh a year | out of band |
| SYN-2016-487 | 2021-07-13 | +26% (317 -> 401) | +1,495 kWh a year | out of band |
| SYN-2016-541 | 2020-01-27 | +6% (149 -> 157) | -21 kWh a year | out of band |
| SYN-2016-476 (gas only) | 2022-04-16 | -65% on gas | the car charges on a supply we do not hold | not observable |
| SYN-2016-383 | 2024-08-20 | +8% (221 -> 238) | no full year after (supply ends 2025-06) | not observable |
| PROS-2024-0111 | 2020-09-13 | - | arrived before we supplied the home | not observable |
| PROS-2016-0003, PROS-2016-0024, PROS-2016-0046, PROS-2017-0038, PROS-2017-0183, SYN-2016-091, SYN-2016-097, SYN-2016-145, SYN-2016-271, SYN-2016-371, SYN-2016-418, SYN-2016-474, SYN-2016-520, SYN-2016-603 | various | - | arrived after we stopped supplying the home | not observable |

The dual households' gas legs (SYN-2016-050g, -123g, -383g, -487g, which stated -67%, -23%, +50%, -45%)
now point to their electricity leg.

**Two things this opens, not closed here:**
1. **14 of 21 cars arrive after the household left us, yet the published customer timeline shows
   them.** A supplier cannot know of a former customer's car. The timeline is written by the customer
   generator from the world's event list without clipping it to the supply window, which is truth
   crossing onto a page labelled as the supplier's view. Next item: clip life events to the supply
   window where the timeline is built (`tools/generate_customer_data.py`), or label them as the
   world's.
2. **Three of four readable cars add less than the band, one adds nothing.** I cannot yet say whether
   the world under-draws the charging load or our record hides it. Prediction, written before the
   check: SYN-2016-541's electricity was billed on estimates through the year after the car, so the
   estimate carried the old use forward (see the finding that a third of households go more than a
   year on estimates). Refuted if its invoices in 2020-02..2021-01 are on actual reads.

**Prediction checked the same hour: not refuted.** SYN-2016-541's electricity invoices from 2020-02 to
2021-04 are all estimates (E), each repeating the year-before profile (134, 138, 123, ... kWh). The first
actual read, May 2021, jumps to 284 kWh and the use stays about double after it. The car's load is in the
world; our record shows it sixteen months late, because the meter went unread. SYN-2016-123 is the same
shape (E through 2021-10, then 390 kWh on the November actual). So the out-of-band reads are mostly the
read-duty defect (`SEAT_FINDING_A_THIRD_OF_HOUSEHOLDS_GO_MORE_THAN_A_YEAR_ON_ESTIMATES_WITHOUT_THE_READ_DUTY_FIRING_2026-10-26.md`)
showing through, not an under-drawn car. The EV root cause is closed on the reader side; this finding's
open items are the two above.
