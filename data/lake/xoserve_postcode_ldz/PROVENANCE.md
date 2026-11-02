# Xoserve: the gas charging area (LDZ) of each census output area

- **Source:** Xoserve, "Postcode Exit Zone List" (May 2017), linked from xoserve.com/a-to-z/ under
  "Postcode Exit Zone/LDZ mapping list": "a mapping of GB postcodes to gas Local Distribution Zones
  (LDZs) ... This list is created by the Network Operators."
  `https://www.xoserve.com/media/2008/postcode-exit-zone-list-may-2017.zip`, one workbook, one sheet
  per distribution network (WWU, SGN, NGN, NG), 1,382,476 postcodes with LDZ and exit zone.
  SHA-256 of the zip as fetched 2026-11-02:
  `1c488b62116fd27315c031f11851b3a450d22595136d2c3d936be84ad9865afb`.
- **Joined to:** the ONS Postcode Directory in the census cache (`onspd_gb_live_residential.csv`,
  postcode -> 2021 output area), as `tools.household_siting_frame` reads it.
- **Built:** 2026-11-02, by the delivery seat, with `python3 -m tools.xoserve_output_area_ldz`.
- **What is here:** `output_area_ldz.csv.gz`, 213,917 rows: `output_area`, `ldz` (the LDZ most of its
  matched postcodes are in), `postcodes` (how many matched), `share` (the modal LDZ's share). 366 rows
  have share < 1. Weighted by the siting frame's households, 92.4% of households are in an output
  area whose matched postcodes are all one LDZ, 0.18% in a split one, and 7.4% in an output area with
  no postcode on the list.
- **What is not here (GAP):** output areas with no postcode on Xoserve's list. The list names gas
  supply postcodes, so most are off the grid (Scotland 17.9% of households, South West 13.2%, East
  11.3%); some are postcodes created after May 2017. 73.0% of ONSPD's live residential postcodes
  match. A newer edition of the list was not found on Xoserve's site.
- **Five independent networks** carry codes outside the 13 charging areas: LC, LO, LS, LT, LW
  (Campbeltown, Oban, Stornoway, Thurso, Wick; 288 output areas). National Gas publishes no CV for
  them in the LDZ series, so their R5 is a GAP.
- **Licence:** Xoserve's published reference list; ONSPD under the Open Government Licence. Not
  personal data (W11): one code per area.
- **Read by:** `sim/ldz_calorific_value.ldz_for_output_area` only. The supplier holds its supply
  point's LDZ from the supply point register, never this file (W6).
