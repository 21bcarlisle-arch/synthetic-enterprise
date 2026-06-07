# Profile Class 1 (domestic unrestricted) — load shape provenance

Decision record for where `sim/data/profile_class_1_gad.csv` came from and
why, so the choice doesn't need re-deriving each time the shape is used.
Researched 2026-06-07 while building the Phase 0b settlement increment.

## Why not pull this from the Elexon API like SSP/SBP?

Checked first, because the Historical Ground Truth law prefers a live,
programmatically-retrievable source. There isn't one:

- `data.elexon.co.uk`'s BMRS Insights Solution API (the same one
  `sim/system_prices.py` uses) covers balancing-mechanism, generation,
  system-price and demand-forecast datasets only — nothing for profile
  classes, profile coefficients, GSP Group Take, or non-half-hourly
  settlement.
- The real data is produced by the **Profile Administrator** under
  **BSCP508** and published as **SAA-I014 / D0018 "Daily Profile Data
  Report"** — a legacy BSC-portal flat-file dataflow, not a REST/JSON API.
  Elexon ran a 2023-24 consultation (**DR498617**) on whether to expose
  D0018 via API at all, which implies it currently isn't. Pulling a real
  multi-year historical PC1 coefficient series programmatically is not
  practical for this project.

## What we used instead

`sim/data/profile_class_1_gad.csv` is a verbatim copy of `ProfileClass1.csv`
from the **UKERC Energy Data Centre** archive entry "Electricity user load
profiles by profile class" (supplied by the Electricity Association via
Elexon Ltd; Open Access — "may be freely used for any purpose"):

- Discovery page: https://ukerc.rl.ac.uk/cgi-bin/dataDiscover.pl?Action=detail&dataid=5af8ae29-86a7-4e8c-9fe4-1e2d99d9fb96
- Archive file: https://dap.ceda.ac.uk/edc/d1/5af8ae29-86a7-4e8c-9fe4-1e2d99d9fb96/data/version_0/data/ProfileClass1.csv

This is real, citable, published data — not invented — but it is a single
**1997 reference year** (384 records: 48 half-hourly periods x 5 seasons x
3 day types), not a multi-year series matching the 2016-2025 sim window.
It is the standard shape structure documented in Elexon's BSC Guidance Note
**"Load Profiles and their use in Electricity Settlement"**
(https://bscdocs.elexon.co.uk/guidance-notes/load-profiles-and-their-use-in-electricity-settlement)
— the same 5 seasons × 3 day-types (15 "GAD" columns) the BSC still uses.

## Shape

- 48 rows in chronological settlement-period order: row 0 = settlement
  period 1 (00:00-00:30, the CSV's "Time" column shows the period's *end*
  time, "00:30"), row 47 = settlement period 48 (23:30-00:00, "Time"
  shows "00:00"). Settlement period = row index + 1 — don't parse "Time".
- 15 value columns named `{Season} {DayType}`, e.g. `Wtr Wd` = Winter
  Weekday. Season prefixes: `Aut`/`Hsr`/`Smr`/`Spr`/`Wtr` = Autumn/High
  Summer/Summer/Spring/Winter. Day-type suffixes: `Wd`/`Sat`/`Sun`.
- Values are **Group Average Demand in kW** for an average PC1 customer.
  Energy per half-hour period = GAD × 0.5h — used directly as kWh, with no
  invented per-customer scaling, since these are themselves real published
  representative-customer figures.

## Season calendar definitions (used by `sim/profile_class_1.py`)

From the Elexon guidance note (UK clock changes: last Sunday of March
GMT→BST and last Sunday of October BST→GMT; August Bank Holiday: last
Monday of August):

- **Winter** — from the October clock change to the day before the
  following March clock change.
- **Spring** — from the March clock change to the Friday before summer
  starts.
- **Summer** — 10 weeks, starting on the 16th Saturday before August Bank
  Holiday.
- **High Summer** — 6 weeks 2 days (44 days), starting on the 6th Saturday
  before August Bank Holiday, ending the Sunday following it.
- **Autumn** — from the Monday following August Bank Holiday to the day
  before the October clock change.

Because August Bank Holiday is always a Monday, "the Nth Saturday before
it" is a fixed offset of `2 + 7*(N-1)` days earlier, and "the Sunday
following it" is `+6` days — `sim/profile_class_1.py` computes both this
way rather than via a generic weekday search.

## Implementation

See [`sim/profile_class_1.py`](../../sim/profile_class_1.py) for
`season_for_date`, `day_type_for_date`, and `load_pc1_shape`.
