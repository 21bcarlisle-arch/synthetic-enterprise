**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_21_the_premise_joint_is_fitted_not_drawn_independently

**Knowledge:** what-a-house-does-to-its-energy

# Wall insulation by dwelling age (EHS 2023), and how the world now reads NEED's scheme flags

*Worker, 2026-11-13, W2_21. This retires the wall GAP in
`need_insulation_flags_count_scheme_installs_not_insulated_homes_2026-11-11.md`.*

## The source

The source is EHS 2023-24, the Climate Resilient Homes fact sheet, Annex Table 2: "Dwelling age, by
energy efficiency characteristics, 2023" (MHCLG). It covers England. Figures are thousands of
dwellings.

- File: <https://assets.publishing.service.gov.uk/media/6868dc4f81dd8f70f5de3b76/Climate_Resilient_Homes_Annex_Tables.ods>
- Sheet: AT2
- Release page: <https://www.gov.uk/government/statistics/english-housing-survey-2023-to-2024-climate-resilient-homes-fact-sheet>

| Wall | Pre-1945 | 1945-2012 | Post-2012 | All |
|---|---|---|---|---|
| cavity, insulated | 1,509 | 9,641 | 1,499 | 12,649 |
| cavity, uninsulated | 1,266 | 3,740 | 0 | 5,007 |
| solid, insulated | 417 | 364 | 87 | 868 |
| solid, uninsulated | 5,678 | 678 | 0 | 6,356 |
| other | 27 | 299 | 191 | 517 |
| **all** | **8,896** | **14,723** | **1,778** | **25,396** |

The unweighted sample sizes are 3,951, 8,709, 628 and 13,288. EHS counts a home as cavity-walled
when cavity makes up at least 50% of its wall area. It counts a post-1995 cavity as insulated, which
is RdSAP's in-built assumption. A cell of 0 means the sample had no cases, not that the stock has
none.

The share of walls insulated (cavity and solid insulated, divided by all dwellings) is:

- pre-1945: **21.7%**
- 1945-2012: **68.0%**
- post-2012: **89.2%**

For cavities alone, 71.6% are insulated, which agrees with HEE's 71%.

## What the world does with it

`simulation/premise_population.insulation_presence_rates` treats a scheme flag as a measure that is
present. A home without a flag gets the measure with this probability:

q = (P_pub − P_flag) / (1 − P_flag)

P_flag is measured on the fitted joint itself. For lofts, P_pub is HEE's 67%. For walls, P_pub is the
EHS share for the home's age group, which is read from its drawn era. Results at seed 42:

| | P_flag | P_pub | q |
|---|---|---|---|
| loft (all homes) | 16.5% | 67% | 0.605 |
| walls, pre-1945 | 10.6% | 21.7% | 0.124 |
| walls, 1945-2012 | 22.8% | 68.0% | 0.585 |
| walls, post-2012 | 2.1% | 89.2% | 0.890 |

Drawn stock over 4,000 homes, seed 42:

| | Before | After |
|---|---|---|
| POOR | 72.1% | **15.2%** |
| PARTIAL | 22.0% | 48.0% |
| FULL | 5.9% | 36.8% |

The published bound on homes with neither measure is 33%. If loft and wall were independent, the
expected share with neither would be 0.33 × 0.468 ≈ 15.4%.

## Choices made, and which way each error runs

- **POST_2000 reads the post-2012 column.** That column is a simplification. Homes built in 2001-12
  sit in EHS's 1945-2012 column, but Part L and RdSAP's post-1995 rule make them insulated. The
  1945-2000 eras therefore inherit a column that includes some 2001-12 homes. That makes them read a
  little **more** insulated than they are. The effect is a smaller remaining ceiling, which errs
  against our own thesis, the safe side under F11.
- **Lofts are treated alike across property types.** HEE counts 26.3m lofts. **GAP:** which flats
  have a loft of their own. NEED flags 3.6% of flats, against about 20% of houses.
- **Measures are drawn independently given age.** **GAP:** EHS publishes no joint of loft and wall
  insulation by home. The independence estimate matches the draw, but no source grades it.
- **`has_loft_insulation` and `has_cavity_wall_insulation` keep the flags' own meaning**, the scheme
  record. Only the `insulation` level reads presence.

## Not yet done

`tools/demand_vector_coverage._fabric_for` still reads the flags as presence. It is a diagnostic
tool, not the world's stock path. The 2026-09-10 "+48% ceiling" claim remains overstated, as its
correction says, and has not been re-measured. W2_21's held step, putting the founder homes on the
fitted joint, is no longer blocked by this defect.
