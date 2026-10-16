**Lane:** W2_customer_generator · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# Pre-registration: what the ratio screen flags among occupied homes that are neither stealing nor empty (2026-10-16, written before the ratios were computed)

The third source of flags, named as a GAP in
`WORKER_PREREG_W2_36_WHAT_A_RATIO_SCREEN_FINDS_AMONG_VOIDS_AND_THEFTS_2026-10-16.md`.

**What is measured.** A flag here is a month or a calendar year in which an occupied home's
registered electricity, over what the company expected for that window, falls under the cut. The
expectation is the company's own, from what it could see: `estimate_unread_kwh` over its last three
actual reads ("own reads"), or before its first read `opening_estimate_kwh` from the registry EAC it
was handed ("opening"). The two bases are counted apart.

**Population.** The published run (`run_output_latest.json.gz`, producing commit 78f77c34e): 633
electricity accounts, about 2,150 account-years. The run draws no theft, and a void is off the
account (the account ends at the move-out), so every flag is an occupied home. Registered = true
kWh, because nothing is stolen.

**Why the earlier probe could not answer this.** It held occupied use flat at the EAC. The world's
use is not flat: it carries weather, life events (EV, ASHP, solar fitted mid-run) and a registry
EAC that is the drawn TDCV band for legacy homes (+21% on average, per the legacy-EAC finding).

**Predictions**, per 10,000 premise-years so they sit beside the voids-and-thefts table:
- **O1.** Empty month (under 0.05): **zero** occupied flags on either basis. Solar is netted half-hour
  by half-hour in the run, so import never empties a month. The empty-month screen stays a theft
  screen.
- **O2.** Month under 0.4: under 50.
- **O3.** Month under 0.65: between 100 and 1,000. Most come from the opening basis.
- **O4.** Year under 0.65: under 50.
- **O5.** At the 0.65 monthly cut, the opening basis flags at a higher rate per account-month than
  the own-reads basis.

*Refutation.* If O1 fails, the world produces empty months in occupied homes and the theft screen's
precision at the empty-month cut is overstated in the earlier table. If O3 exceeds 1,000, low-use
occupied homes rival private voids as the loose cut's false positives.

## Graded (same day, after the run)

`python3 -m tools.theft_void_screen_probe --occupied-run docs/reports/run_output_latest.json`.
The run book has 633 accounts and 2,099 premise-years.

**Corrected beside the premise above: a void is NOT off the account.** B7 slice 6 opens the incoming
occupier's account on the move date, and its rows before `void_end` are the owner's, at 0 kWh. The
first pass filed 58 empty periods to occupied homes. Every one of them was an `OCC-` account's
opening stub, 2 to 21 days at 0 kWh. The probe now files an incoming account's periods, up to and
including its first period with any use, to the void.

| Flags per 10,000 premise-years | occupied, opening | occupied, own reads | void (incoming stub) |
|---|---|---|---|
| Month under 0.05 | 0 | 0 | 276 |
| Month under 0.4 | 52 | 524 | 391 |
| Month under 0.65 | 143 | 1,796 | 467 |
| Year under 0.65 | 0 | 0 | 0 |

- **O1: held** once voids are attributed. No occupied home empties a period.
- **O2: refuted.** Occupied homes flag 576 months under 0.4, not under 50.
- **O3: refuted.** They flag 1,939 under 0.65, above 1,000, and most come from the own-reads basis, not the opening one.
- **O4: held.** No occupied year falls under 0.65.
- **O5: refuted.** Per window, own reads flag 1.6% of months and the opening basis 1.2%.

**Why O2, O3 and O5 failed.** The flags come from the expectation's shape, not from low use.
55 accounts carry the 377 own-reads flags, and ten of them carry 63%. 48 of the 55 are
`fabric_physics` (weather-driven) homes, against 339 of 633 in the book. The flags fall from April
to September. Fabric homes flag 2.5% of their own-read months (293 of 11,882) and legacy homes 0.5%
(53 of 11,153). A window of three reads taken in winter or spring, shaped by the published profile,
over-expects the summer of a home whose swing is steeper than that profile. The annual window
never flags them.
