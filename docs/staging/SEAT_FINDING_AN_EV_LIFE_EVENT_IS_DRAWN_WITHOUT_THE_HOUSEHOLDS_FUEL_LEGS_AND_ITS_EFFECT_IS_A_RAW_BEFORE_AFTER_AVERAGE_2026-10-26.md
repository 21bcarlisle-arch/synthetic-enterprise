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
