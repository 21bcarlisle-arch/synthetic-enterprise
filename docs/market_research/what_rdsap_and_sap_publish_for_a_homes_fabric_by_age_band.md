# What RdSAP and SAP Publish for a Home's Fabric, by Age Band

**Knowledge:** what-a-house-does-to-its-energy

Researched against `simulation/fabric_physics.py` lines ~497-640 (fabric U-values, insulation,
infiltration, floor area, solar/frame) and ~810-870 (heat-source oversize, boiler efficiency,
ASHP COP, design external temperature). All values quoted below were fetched and read directly
from the primary PDFs on 2026-10-19 (see Sources); nothing is quoted from memory. Where a figure
could not be fetched it is marked **GAP** and the search attempted is stated.

## Sources fetched

- **RdSAP 10 Specification** (BRE, "RdSAP10 Specification", subject "June 2026", created
  2026-06-10) — `https://bregroup.com/documents/d/bre-group/rdsap-10-specification-2026-06-07`
  (114 pp, served as a raw PDF despite the `.html`-looking URL). Cited as **[RdSAP10]**.
- **RdSAP Conventions v12.1** (BRE, author I. Rowley, 2025-08-21) —
  `https://bregroup.com/documents/d/bre-group/rdsap-conventions-v12-1-21-august-2025-final`
  (56 pp). Cited as **[RdSAP-Conv]**.
- **SAP 10.3 Full Specification** (BRE, author J. Henderson, created 2026-06-11) —
  `https://bregroup.com/documents/d/bre-group/sap-10-3-full-specification-2026-06-12` (201 pp).
  Cited as **[SAP10.3]**.
- **BREDEM-2012 Specification** (BRE) —
  `https://files.bregroup.com/bre-co-uk-file-library-copy/filelibrary/bredem/BREDEM-2012-specification.pdf`
  (37 pp). Cited as **[BREDEM-2012]**.
- **Approved Document L, Volume 1: Dwellings**, 2026 edition (MHCLG) —
  `https://assets.publishing.service.gov.uk/media/69c122a6cfa346b9d4704a55/ADL1_2026.pdf`
  (107 pp). Cited as **[ADL1-2026]**.
- **Approved Document F, Volume 1: Dwellings**, 2026 edition (MHCLG) —
  `https://assets.publishing.service.gov.uk/media/69c12224d588c92c483e4b6a/ADF1_2026.pdf`.
  Cited as **[ADF1-2026]**.
- **English Housing Survey 2021-22, Section 2 (Stock Figures)** — Fig 2.4 only (floor area BY
  TENURE, in bands, not by dwelling type) —
  `https://assets.publishing.service.gov.uk/media/6399ae4ce90e072aebae583f/2021-22_EHS_Headline_Report_Section_2_Stock_Figures.xlsx`.
  Cited as **[EHS-2122]**. Did **not** yield floor area by `PropertyType` — see the floor-area
  section below.
- CIBSE Guide A / BS EN 12831 (design external temperature) and a published heat-pump field trial
  (DESNZ/BEIS Electrification of Heat, RHPP) were searched for (gov.uk search API, several query
  strings) and **not retrieved** within this session — both remain GAP, stated explicitly below
  rather than filled with a remembered number.

## Age-band mapping (read first — every verdict below depends on it)

**[RdSAP10] Table 1** gives England age bands A-M:

| Band | England years |
|---|---|
| A | before 1900 |
| B | 1900-1929 |
| C | 1930-1949 |
| D | 1950-1966 |
| E | 1967-1975 |
| F | 1976-1982 |
| G | 1983-1990 |
| H | 1991-1995 |
| I | 1996-2002 |
| J | 2003-2006 |
| K | 2007-2011 |
| L | 2012-2022 |
| M | 2023 onward |

The module's six `BuildEra` bands do not align with these thirteen. Mapping used throughout this
page:

| Module band | RdSAP bands spanned |
|---|---|
| `PRE_1919` | A (whole) + B (1900-1919 part) |
| `ERA_1919_1944` | B (1919-1929 part) + C (whole) |
| `ERA_1945_1964` | C (1945-1949 part) + D (1950-1964 part) |
| `ERA_1965_1980` | D (1965-1966 part) + E (whole) + F (1976-1980 part) |
| `ERA_1981_2000` | F (1981-1982 part) + G + H + I (1996-2000 part) |
| `POST_2000` | I (2000-2002 part) + J + K + L + M — **26 years and growing**, the single widest and most heterogeneous span, and the only one still open-ended as the simulation clock advances |

RdSAP wall U-values also depend on **construction type** (stone, solid brick, cavity, timber
frame, system build), which Table 1's age bands do not determine — a pre-1919 wall could be stone,
solid brick of several thicknesses, or (rarely) early cavity. The module carries one number per
era with no construction-type axis; the spread this collapses is given per-constant below.

---

## Wall U-values (`_WALL_U_BY_ERA`)

**[RdSAP10] Table 6 (England)**, "as built" (uninsulated), two most common construction types:

| Age band | Cavity as built | Solid brick as built (200-280mm, §5.7) |
|---|---|---|
| A-E (all five share one value) | 1.5 | 1.7 |
| F | 1.0 | 1.0 |
| G | 0.60 | 0.60 |
| H | 0.60 | 0.60 |
| I | 0.45 | 0.45 |
| J | 0.35 | 0.35 |
| K | 0.30 | 0.30 |
| L | 0.28 | 0.28 |
| M | 0.26 | 0.26 |

Solid brick is also wall-thickness-dependent (**[RdSAP10] Table 13**): <200mm → 2.5, 200-280mm →
1.7, 280-420mm → 1.4, >420mm → 1.1. Stone walls follow a continuous thickness formula
(**[RdSAP10] Table 12**: sandstone/limestone U=54.876×W⁻⁰·⁵⁶¹; granite/whinstone
U=45.315×W⁻⁰·⁵¹³, W in mm) — e.g. a 330mm sandstone wall gives U≈2.1.

| Module constant | Module value | Published range (by construction/thickness) | Verdict |
|---|---|---|---|
| `PRE_1919` | 2.10 | 1.1-2.5 (brick, thickness-dependent); ~1.5-2.7 (stone, continuous) | **CONSISTENT** — doesn't sit on either RdSAP default step (1.7 brick / 1.5 cavity) but matches a ~300-350mm stone wall or a sub-200mm thin solid wall; both exist in the pre-1919 stock |
| `ERA_1919_1944` | 1.70 | 1.7 (solid brick 200-280mm, bands B-C) | **CONSISTENT** — exact match |
| `ERA_1945_1964` | 1.50 | 1.7 (brick) / 1.5 (cavity), bands C-D — **unchanged from the pre-1919 value**, Table 6 does not move off 1.5/1.7 until band F (1976) | **CONSISTENT** with the cavity-wall reading (1.5 exact), but note this era is NOT yet in a lower-U regime per RdSAP — the table's own transition happens later than intuition suggests |
| `ERA_1965_1980` | 1.00 | 1.5 for D/E (1965-1975, 11 of the 16 years in this module band) → 1.0 only for F (1976-1980 part) | **CONTRADICTED for most of the band** — the module's flat 1.00 understates heat loss by 33% against the published 1.5 that actually applies through 1975; it is correct only for the 1976-1980 tail |
| `ERA_1981_2000` | 0.60 | F-tail (1981-82)=1.0, G/H (1983-1995, bulk of band)=0.60, I-tail (1996-2000)=0.45 | **CONSISTENT for the bulk** (G/H, ~15 of 20 years) but overstates insulation for 1981-82 and understates it for 1996-2000 |
| `POST_2000` | 0.30 | I-tail(2000-02)=0.45, J=0.35, K=0.30, L=0.28, M=0.26 — a **42% range (0.45→0.26) across the band itself** | **CONTRADICTED as a representative value** — 0.30 happens to match K (2007-2011) almost exactly, but the band spans 26 years over which Part L has tightened the default four further times; the oldest fifth of "post-2000" stock is 50% leakier than the module's value and the newest is 15% tighter. This mismatch only grows as the simulation clock advances and feeds ever-newer builds into the same bucket. |

---

## Roof U-values (`_ROOF_U_BY_ERA`)

**[RdSAP10] Table 18**, "pitched, slates or tiles, insulation at rafters" column (the as-built,
pre-loft-insulation figure — column 1, "insulation between joists or unknown," defaults to
100mm/0.40 for bands A-G per note (4) "most lofts are insulated to at least 100mm," which is a
different assumption and not the right comparator for an as-built uninsulated value):

| Age band | Roof U (rafters/flat/RR column) |
|---|---|
| A, B, C, D | 2.3 |
| E | 1.5 |
| F | 0.68 |
| G | 0.40 |
| H | 0.35 |
| I | 0.35 |
| J | 0.20 (pitched) / 0.25 (flat) |
| K | 0.20 (pitched) / 0.25 (flat) |
| L | 0.18 |
| M | 0.15 |

| Module constant | Module value | Published value for the band | Verdict |
|---|---|---|---|
| `PRE_1919` | 2.30 | 2.3 (A-D) | **CONSISTENT** — exact match |
| `ERA_1919_1944` | 2.30 | 2.3 (B-C, both inside the A-D group) | **CONSISTENT** — exact match |
| `ERA_1945_1964` | 1.50 | 2.3 — D (1950-1966) is **still inside the A-D group**, the step down to 1.5 doesn't happen until E (1967) | **CONTRADICTED** — module's 1.50 is 35% too good for this whole era; RdSAP keeps it at 2.3 through 1966 |
| `ERA_1965_1980` | 0.68 | 1.5 for D-tail/E (1965-1975, 11 of 16 years) → 0.68 only for F (1976-1980) | **CONTRADICTED for most of the band** — understates heat loss by >2x against the 1.5 that applies through 1975 |
| `ERA_1981_2000` | 0.35 | F-tail=0.68, G=0.40, H/I (1991-2000, bulk)=0.35 | **CONSISTENT for the bulk** (H/I), overstates insulation for 1981-1990 |
| `POST_2000` | 0.16 | I-tail=0.35, J=0.20, K=0.20-0.25, L=0.18, M=0.15 | **CONTRADICTED as representative** — 0.16 sits closest to L/M (the newest ~13 years of a 26-year span) and understates heat loss sharply for the 2000-2011 majority of the band |

Same shape as the wall table: the two oldest module bands match exactly (because RdSAP itself is
flat there), the middle bands are shifted roughly one RdSAP step too optimistic, and `POST_2000`
is the worst-matched because it silently picks the newest sub-cohort to represent a 26-year span.

---

## Window U-values (`_WINDOW_U_BY_ERA`)

**[RdSAP10] Table 24** ("Window characteristics"), U-value for PVC/wooden frame:

| Glazing / installation period | U-value | g-value |
|---|---|---|
| Single, any period | 4.8 | 0.85 |
| Double, pre-2002 (England/Wales), 6mm gap | 3.1 | 0.76 |
| Double, pre-2002, 12mm gap | 2.8 | 0.76 |
| Double, pre-2002, ≥16mm gap | 2.7 | 0.76 |
| Triple, pre-2002, 12mm gap | 2.1 | 0.68 |
| Double or triple, 2002-2021 | 2.0 | 0.72 |
| Double or triple, 2022 or later | 1.4 | 0.72 |

Critically, RdSAP keys the window table on **glazing installation date**, not the building's
construction era — windows are commonly replaced independently of the wall. The module pegs
window U to `BuildEra` directly, which is a structural simplification RdSAP does not make.

| Module constant | Module value | Published value (nearest matching row) | Verdict |
|---|---|---|---|
| `PRE_1919` through `ERA_1965_1980` (all four = 2.80) | 2.80 | Double glazed pre-2002, 6mm gap = 3.1; 12mm gap = 2.8 | **CONSISTENT with the "double glazed, pre-2002, 12mm gap" row (exact match)** — but this assumes universal double glazing even on the oldest stock, which silently overrides whatever single-glazing fraction actually exists (single glazed = 4.8, 71% higher); the module carries no glazing-type field to represent that |
| `ERA_1981_2000` | 2.00 | Pre-2002 default = 2.8; 2002-2021 default = 2.0 | **CONTRADICTED for the construction-era reading** — a window **installed** in 1981-2000 would be pre-2002 (2.8), not 2.0; 2.0 only applies if the window was *replaced* after 2002, which the era field cannot represent |
| `POST_2000` | 1.50 | 2002-2021 = 2.0; 2022+ = 1.4 | **CONTRADICTED as representative** — 1.50 sits near the newest 2022+ figure (1.4) but the bulk of "post-2000" stock (built 2000-2021, 21 of 26 years) should default to 2.0, 33% higher |

---

## `_SOLAR_TRANSMITTANCE` (glazing g-value) and `_FRAME_FACTOR`

**[RdSAP10] Table 24** g-values: single 0.85; double/triple pre-2002/2003/2006 = 0.76/0.68;
double/triple 2002+ and 2022+ = 0.72. **[BREDEM-2012] Table 24** ("Solar gains transmission
factors," a finer breakdown by coating): single glazed 0.85; double glazed (air/argon) 0.76;
double glazed low-E hard coat 0.72; double glazed low-E soft coat 0.63; triple glazed (air/argon)
0.68. Across both sources the published range for ordinary UK glazing is **0.63-0.85**.

| Module constant | Module value | Published range | Verdict |
|---|---|---|---|
| `_SOLAR_TRANSMITTANCE` | 0.55 | 0.63 (double, low-E soft coat — the lowest published figure found) to 0.85 (single) | **CONTRADICTED** — below the entire published range, by at least 13% against the lowest value found (low-E soft-coat double glazing) and 24% against the common 2002+ default of 0.72 |

**[RdSAP10] Table 24** note and **[BREDEM-2012] Table 2** (identical): "Frame factor is 0.7 for
wooden or PVC frame; 0.8 for metal frame (not applied if data source is BFRC)."

| Module constant | Module value | Published value | Verdict |
|---|---|---|---|
| `_FRAME_FACTOR` | 0.70 | 0.7 (wood/PVC-U), 0.8 (metal) | **CONSISTENT** — exact match to the wood/PVC-U row, the dominant UK frame material |

---

## Boiler efficiency (`_BOILER_EFFICIENCY`)

**[SAP10.3] Table 4b**, winter seasonal efficiency, selected rows (used only when PCDB data is
unavailable — PCDB-rated individual products can differ):

| Boiler type | Winter efficiency |
|---|---|
| Condensing combi, automatic ignition (1998+) | 84% |
| Regular condensing, automatic ignition (1998+) | 84% |
| Non-condensing combi, automatic ignition (1998+) | 74% |
| Regular non-condensing, automatic ignition (1998+) | 74% |
| Standard oil boiler, 1998 or later | 80% |
| Regular, floor mounted, pre-1979 | 56% |
| Condensing combi/oil, modern | 82-84% |

| Module constant | Module value | Published Table 4b range | Verdict |
|---|---|---|---|
| `BoilerAge.NEW` (0-5yr) | 0.90 | 84% is Table 4b's ceiling (no entry exceeds it) | **CONSISTENT, upper edge** — 90% exceeds the RdSAP *default-table* ceiling by ~7%, but is within the range of PCDB-rated best-in-class condensing combis (SEDBUK-A products commonly test above 84% at full load); not contradicted, but the 84% default-table ceiling should be the stated anchor if PCDB data isn't modelled |
| `BoilerAge.MID` (5-12yr) | 0.86 | 84% (condensing combi/regular, automatic ignition) | **CONSISTENT** — within 2pp |
| `BoilerAge.OLD` (12+yr) | 0.80 | 74-84% if condensing (mandatory since 2005 Building Regs, so most "12+ year old" boilers today are still condensing); 56-74% only for genuinely pre-1998 stock | **CONSISTENT** for condensing-era old boilers, but the table shows a boiler **older than ~20 years** (pre-2005, pre-condensing-mandate) would more plausibly sit at 56-74%, not 80% — `OLD` conflates "a bit old" with "pre-condensing," which the published table treats very differently |
| `BoilerAge.NA` (default/unknown) | 0.86 | matches MID | **CONSISTENT** by construction |

---

## ASHP COP curve, oversize factor, design external temperature — GAP

- `_ASHP_COP_AT_7C` = 3.5, `_ASHP_COP_AT_MINUS_2C` = 2.2, `_GSHP_COP_UPLIFT` = 1.25: **[SAP10.3]**
  does not publish a temperature-dependent COP curve for standard assessments — it uses PCDB
  product records or a default annual SCoP figure (§C2, Appendix N), not COP at specific ambient
  temperatures. The EN 14825 standard test points (A7/W35, A2/W35, A-7/W35) that manufacturers
  publish COP against are the right published anchor for this shape of constant, but I could not
  fetch a manufacturer or regulator-published EN 14825 COP table, nor the DESNZ/BEIS
  Electrification of Heat demonstration or RHPP field-trial report, within this session (gov.uk
  search API queried with several phrasings — "electrification of heat demonstration project",
  "heat pump field trial performance monitoring coefficient of performance", "renewable heat
  premium payment heat pump monitoring" — none returned the report directly; only a related
  "successful bids" publication was found, not the performance data). **GAP — unverified.**
- `_OVERSIZE_FACTOR` (combi 1.90, system 1.50, ASHP 1.15, etc.): no SAP/RdSAP table addresses
  boiler/heat-pump oversizing factors — sizing practice sits outside the SAP/RdSAP assessment
  methodology (it's an installer/BS EN 12831 sizing-calculation question, not an EPC-assessment
  one). Industry commentary on combi oversizing (Energy Saving Trust, Heat Pump Association,
  Energy Systems Catapult) is widely cited but I did not fetch a quantified primary source within
  budget. **GAP — unverified.**
- `DESIGN_EXTERNAL_TEMP_C` = -3.0: CIBSE Guide A / BS EN 12831 publish location-specific winter
  design external temperatures (commonly cited for London around -3°C to -4°C), but both
  documents are not freely fetchable and I did not find a government-hosted copy within budget.
  One partial cross-reference: **[SAP10.3] §A3.3** uses "a design temperature difference of
  24.2 K" against an assumed 21°C living-room setpoint for a *different* purpose (testing whether
  a 3kW room heater alone can heat a highly-insulated dwelling) — implying an external reference
  of 21 − 24.2 ≈ **-3.2°C**. This is suggestively close to the module's -3.0°C, but it is an SAP
  worksheet convention for a narrow test, not BS EN 12831's winter design condition, so I am not
  treating it as the same quantity. **GAP for the primary CIBSE/BS EN 12831 source; -3.2°C from
  SAP10.3 §A3.3 recorded as a weak (M-confidence, different-purpose) cross-reference only.**

---

## Infiltration (`_INFILTRATION_ACH_BY_ERA`) — methodology mismatch, not a simple GAP

**[RdSAP10] §4.1 / Table 5** does **not** publish infiltration as a single ACH-by-age-band table.
SAP10.2/RdSAP infiltration is a worksheet sum of independent terms: structural infiltration by
wall material (0.25 steel/timber frame, 0.35 masonry), floor infiltration (0.1 "sealed" / 0.2
"unsealed," itself a function of age band only for suspended-timber ground floors, A-E), draught
lobby (0 or 0.05), number of storeys, sheltered sides (0 detached / 1-3 depending on terrace
position), and chimney/flue/extract-fan counts (extract fans default 1 for A-E, 1-4 for F-M by
room count). Age band genuinely contributes (via the floor-sealing and extract-fan defaults) but
is nowhere near the dominant term RdSAP's formula uses — wall material and number of storeys
matter more.

| Module constant | Verdict |
|---|---|
| `_INFILTRATION_ACH_BY_ERA` (1.00 → 0.45 declining with age) | **GAP, methodology mismatch** — the declining-with-age *direction* is broadly consistent with RdSAP's age-linked terms (older homes get fewer sealed floors, fewer extract fans), but no RdSAP table publishes a single ACH number by age band to check the module's specific values against; the real formula is multi-term and dominated by non-age factors the module doesn't carry (wall material, storeys, sheltered sides) |

`_MINIMUM_VENTILATION_ACH` = 0.50: **[ADF1-2026] Table 1.3** sets whole-dwelling minimum
ventilation by bedroom count in l/s (1 bed=19, 2 bed=25, 3 bed=31, 4 bed=37, 5 bed=43, +6 l/s per
extra bedroom), a different unit (absolute flow, not ACH). Converting using the module's own
`_FLOOR_AREA_BASE_M2` + `_STOREY_HEIGHT_M` (2.4m) for a 2-bedroom home of each property type gives
ACH of roughly 0.43 (detached, 88m²) to 0.78 (flat, 48m²), centring near 0.5-0.6 for the
terraced/semi-detached middle of the stock.

| Module constant | Module value | Published cross-reference | Verdict |
|---|---|---|---|
| `_MINIMUM_VENTILATION_ACH` | 0.50 | ~0.43-0.78 ACH implied by ADF1-2026 Table 1.3 across the module's own floor-area table, centring near 0.5-0.6 | **CONSISTENT** — sits inside the implied range, close to its centre |

---

## Ground floor U-values (`_GROUND_U_BY_ERA`) — methodology mismatch

**[RdSAP10] Table 19** does not give ground-floor U-values directly either; it gives the *default
insulation thickness assumed* by age band (used as an input to a BS EN ISO 13370 calculation that
also needs the dwelling's perimeter/area ratio, soil type and construction):

| Age band | Assumed all-over floor insulation (England & Wales) |
|---|---|
| A-F | none |
| G | none |
| H | none |
| I | 25mm |
| J | 75mm |
| K | 100mm |
| L | 100mm |
| M | 140mm |

Because the resulting U-value is a function of the specific dwelling's exposed perimeter and area
(not just age band), there is no published single number per band to check `_GROUND_U_BY_ERA`
(0.70 → 0.22) against directly.

| Module constant | Verdict |
|---|---|
| `_GROUND_U_BY_ERA` | **GAP, methodology mismatch** — the monotonic decline with age is directionally consistent with Table 19's assumed-insulation-thickness trend (none until I-band/1996, rising to 140mm by M-band/2023+), but RdSAP computes the actual U-value per-dwelling via BS EN ISO 13370, not from a lookup table, so no like-for-like published figure exists to confirm or contradict the module's specific numbers |

---

## Part L achievable floors (`_WALL_U_FLOOR`, `_ROOF_U_FLOOR`, `_GROUND_U_FLOOR`)

**[ADL1-2026]**:
- **Table 3.1** (new dwellings, new-build limiting standard): roof 0.16, wall 0.26, floor 0.18.
- **Table 3.2** (new/replacement elements fitted into an *existing* dwelling): roof 0.15, wall
  0.18, floor 0.18.
- **Table 3.3** (renovated/retained elements in existing dwellings — the "improved" column is the
  achievable retrofit standard): roof improved 0.16 (threshold 0.35), wall-cavity improved 0.55
  (threshold 0.70), wall-internal/external-insulation improved 0.30 (threshold 0.70), floor
  improved 0.25 (threshold 0.70).

| Module constant | Module value | Nearest published figure(s) | Verdict |
|---|---|---|---|
| `_WALL_U_FLOOR` | 0.25 | Table 3.1 new-build = 0.26 (close, 4% tighter); Table 3.3 improved retrofit (internal/external insulation) = 0.30 | **CONSISTENT with the new-build limit (0.26)**, but **tighter than Part L's own stated achievable retrofit standard (0.30) by ~17%** — worth noting if the floor is meant to represent what a retrofit can achieve on an old solid wall, rather than new-build performance |
| `_ROOF_U_FLOOR` | 0.13 | Table 3.1 new-build = 0.16; Table 3.2 = 0.15; Table 3.3 improved retrofit = 0.16 | **CONTRADICTED, mildly** — 0.13 is tighter than all three published Part L figures by 13-19%; physically achievable with deep (300mm+) loft insulation but not what Part L itself sets as the ceiling |
| `_GROUND_U_FLOOR` | 0.18 | Table 3.1 = 0.18; Table 3.2 = 0.18 | **CONSISTENT** — exact match to both the new-build and new-in-existing-dwelling limiting values |

---

## `_INSULATION_U_MULTIPLIER` (FULL 0.40, PARTIAL 0.70)

Implied ratios from **[RdSAP10] Table 6**, as-built → insulated, for the measures it tabulates:

| Measure | As built | Insulated | Ratio |
|---|---|---|---|
| Cavity fill (A-E) | 1.5 | 0.7 (fill only) | 0.47 |
| Cavity fill + 100mm (A-E) | 1.5 | 0.25 | 0.17 |
| Solid brick + 50mm insulation (A-E) | 1.7 | 0.55 | 0.32 |
| Solid brick + 100mm insulation (A-E) | 1.7 | 0.32 | 0.19 |
| Cavity fill (F, post-1976) | 1.0 | 0.40 | 0.40 |

| Module constant | Module value | Published ratios | Verdict |
|---|---|---|---|
| `FULL` | 0.40 | 0.17-0.47 depending on measure/thickness | **CONSISTENT** — sits inside the published range, coincidentally matching the F-band cavity-fill ratio (0.40) exactly, but represents a blend across very different measures (simple cavity fill vs. deep external wall insulation), which RdSAP treats as distinct rows rather than one multiplier |
| `PARTIAL` | 0.70 | 0.24-0.32 for the "50mm" (lightest) insulation step found in Table 6 — the lightest measure RdSAP tabulates already beats 0.70 | **CONTRADICTED, and conceptually mismatched** — RdSAP has no "70%-of-uninsulated" row for any measure; more importantly, the module's `InsulationLevel.PARTIAL` is defined as "loft only, or partial wall" (i.e. *some elements* fully insulated, others not at all), which RdSAP represents by applying the FULL ratio to the insulated element and the as-built value to the uninsulated one — not by applying a single blended multiplier to every opaque surface. Flagging this as the more important finding: the single blanket 0.70 multiplier doesn't correspond to how RdSAP models partial insulation at all, independent of what number is chosen. |

---

## Floor area (`_FLOOR_AREA_BASE_M2`, `_FLOOR_AREA_PER_BEDROOM_M2`) — GAP

**[EHS-2122] Fig 2.4** ("Usable floor area for occupied dwellings, by tenure, 2021") was fetched
and read in full. It gives floor-area **bands** (e.g. "70 to 89m²: 25.8% owner-occupied, 27.4%
private rented, 30.6% social sector") cross-tabbed by **tenure**, not by `PropertyType`
(detached/semi/terraced/flat) and not as a mean. This is the wrong cross-tab for the module's
constants, which need mean floor area by dwelling type and a per-bedroom increment.

| Module constant | Verdict |
|---|---|
| `_FLOOR_AREA_BASE_M2` (flat 48, terraced 60, semi 68, detached 88) | **GAP** — searched EHS 2021-22 headline Section 2 stock figures (Fig 2.4, the only floor-area figure in that release) and found tenure-by-band, not type-by-mean. The EHS annex ODS tables (fetched but not parsed — no ODS reader available in this session) or the EHS "housing stock" detailed/live tables, or the EPC register's own aggregate statistics, are the next places to look |
| `_FLOOR_AREA_PER_BEDROOM_M2` = 14.0 | **GAP** — same search, same gap |

---

## Anchoring disposition

**Could be anchored by citing this page unchanged (CONSISTENT, exact or near-exact match):**
- `ERA_1919_1944` wall U (1.70 = exact RdSAP match)
- `ERA_1945_1964` wall U (1.50, cavity reading, exact match)
- `PRE_1919` and `ERA_1919_1944` roof U (2.30, exact match both)
- `_FRAME_FACTOR` (0.70, exact match)
- `BoilerAge.MID` / `NA` (0.86, within 2pp of Table 4b)
- `_MINIMUM_VENTILATION_ACH` (0.50, inside the ADF1-2026-implied range)
- `_GROUND_U_FLOOR` (0.18, exact match to ADL1-2026 Tables 3.1/3.2)
- `_INSULATION_U_MULTIPLIER.FULL` (0.40, inside the published ratio range)

**Would need a value change or an explicit documented simplification, per this page's evidence
(CONTRADICTED or structurally mismatched):**
- `ERA_1965_1980` wall U and roof U (both understate heat loss for most of the 16-year span)
- `ERA_1945_1964` roof U (0.35 too optimistic against the published 2.3 that applies through 1966)
- `POST_2000` wall U, roof U and window U (all three pick a value representative of only the
  newest fraction of a 26-year, still-growing span)
- `ERA_1981_2000` window U (2.00 assumes a post-2002 replacement window on a pre-2002-built home)
- `_SOLAR_TRANSMITTANCE` (0.55, below the entire published 0.63-0.85 range)
- `_WALL_U_FLOOR` (0.25, tighter than Part L's own stated achievable retrofit standard of 0.30)
- `_ROOF_U_FLOOR` (0.13, tighter than all three published Part L figures by 13-19%)
- `_INSULATION_U_MULTIPLIER.PARTIAL` (0.70 — no RdSAP measure is this weak, and the whole
  single-multiplier shape doesn't match how RdSAP represents partial/per-element insulation)
- `_INFILTRATION_ACH_BY_ERA` and `_GROUND_U_BY_ERA` (not contradicted, but no published
  single-number-per-age-band table exists to check them against — RdSAP's real methods are
  multi-term formulas dominated by non-age factors)
- `_ASHP_COP_AT_7C`, `_ASHP_COP_AT_MINUS_2C`, `_OVERSIZE_FACTOR`, `DESIGN_EXTERNAL_TEMP_C`,
  `_FLOOR_AREA_BASE_M2`, `_FLOOR_AREA_PER_BEDROOM_M2` (GAP — no primary source retrieved this
  session; each states what was searched)

No code value is proposed or changed on this page — only what is published, and where nothing
published was found.
