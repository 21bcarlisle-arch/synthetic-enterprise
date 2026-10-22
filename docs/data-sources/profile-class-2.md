# Profile Class 2 (domestic Economy 7): load shape provenance

Where `sim/data/profile_class_2_gad.csv` came from, and what decided that a home was registered on
it. Added 2026-10-22 so that a storage-heated home can be settled on the profile it was settled on
in 2016–2025. The measurement that showed it matters:
`docs/staging/records/SEAT_RESULT_SETTLING_EACH_HOMES_OWN_SHAPE_AGAINST_THE_PROFILE_IS_NEAR_ZERO_FOR_THE_BOOK_AND_TENS_OF_POUNDS_FOR_AN_ELECTRICALLY_HEATED_HOME_2026-10-22.md`.

## The file

A verbatim copy of `ProfileClass2.csv` from the UKERC Energy Data Centre archive "Electricity user
load profiles by profile class" (Electricity Association via Elexon Ltd; Open Access). It is the
same archive, reference year (1997) and layout as PC1's. See `profile-class-1.md` for why the
Elexon API is not the source, for the column layout and for the season calendar.

- Archive file: https://dap.ceda.ac.uk/edc/d1/5af8ae29-86a7-4e8c-9fe4-1e2d99d9fb96/data/version_0/data/ProfileClass2.csv
- Fetched 2026-10-22, no transformation. SHA-256 `08457653933eee376c619489358e837c71f8301abcdd36555eba8c4c1359e60b`.
  The tree's `profile_class_1_gad.csv` was re-fetched the same day and is still byte-identical to
  the archive's `ProfileClass1.csv`.
- 48 rows × 15 `{Season} {DayType}` columns of Group Average Demand in kW; kWh per period = GAD × 0.5.

Read by `sim/profile_class_2.py` (`load_pc2_shape`), which reuses PC1's calendar.

## What it looks like, printed at real inputs

| Calendar 2019 | PC1 | PC2 |
|---|---:|---:|
| Annual kWh of the average customer | 3,922 | 6,976 |
| Share of the year's volume 00:00–07:00 | 15.2% | 44.5% |
| 4 Jan 2016 (winter weekday), share 00:00–07:00 | | 52.0% |

## Who was registered on it

Elexon's profiling page (https://www.elexon.co.uk/bsc/settlement/profiling/, read 2026-10-22):

- PC1 is "Domestic Unrestricted Customers", PC2 "Domestic Economy 7 Customers", PC3 "Non-Domestic
  Unrestricted Customers", PC4 "Non-Domestic Economy 7 Customers".
- The class depends on whether the metering system is import or export, on domestic or
  non-domestic use, on whether the meter has "switched load", and on maximum-demand recording.
- "Suppliers are responsible for allocating their customers in the appropriate Profile Class",
  under BSCP516.

So the class followed the **meter**, not the heating. A domestic home with an off-peak (switched)
register was PC2. A storage-heated home was PC2 because storage heaters charge on that register. A
gas-heated home that kept an Economy 7 meter was PC2 as well.

The class is printed as the first two digits of the MPAN's supplementary (top) line, "02" for a
domestic meter of two or more rates. *Secondary source*: Wikipedia, "Meter Point Administration
Number". Elexon's own MSID/MPAN guidance renders client-side and was not read.

## GAPs

- **G1. Other domestic multi-rate configurations.** Elexon's page names only "Economy 7". Whether
  Economy 10, heating-only circuits and the like were PC2 is not established here. The MPAN source
  above says "two or more rates", which suggests PC2, but that is secondary.
- **G2. E7 meters in gas-heated homes.** No share has been established. The world places a two-rate
  meter only where the heating needs one (`ELECTRIC_STORAGE`), so any such homes are absent.
- **G3. Direct-electric and heat-pump homes on E7.** Not established. The world keeps them on PC1.
- **G4. The table is not the period's coefficients.** The Profile Administrator regressed each
  class on noon temperature, sunset and day of week, and split PC2 into switched and base load.
  The 1997 GAD table has five seasons and three day types and none of that.
