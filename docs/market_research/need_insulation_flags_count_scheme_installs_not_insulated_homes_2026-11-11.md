**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_21_the_premise_joint_is_fitted_not_drawn_independently

**Knowledge:** what-a-house-does-to-its-energy

# NEED's insulation flags count scheme installations, not insulated homes

*Worker, 2026-11-11, W2_21. Measured on `~/.cache/synthetic-enterprise/need_2026/anon2026_50k.csv`
(50,000 dwellings) and its `meta.ods`.*

## What the source says

DESNZ's NEED metadata defines the two flags as follows, verbatim:

- `LI_FLAG`: "Indication of whether the property has had loft insulation (including roof and
  room-in-roof) installed **under a government scheme from 2000 onwards**."
- `CWI_FLAG`: "Indication of whether the property has had cavity wall insulation installed **under a
  government scheme from 2000 onwards**."

The source is the scheme administrators (for example, Ofgem for ECO). A 0 means no scheme
installation is recorded. It does **not** mean the home is uninsulated. The flags miss homes built
insulated, homes insulated before 2000, and homes insulated privately.

## What NEED shows, and what the stock actually is

| | NEED flag = 1 (all 50k) | Published coverage (HEE Dec 2025, DESNZ Mar 2026) |
|---|---|---|
| Loft | 14.4% (7,180) | 67% of 26.3m lofts at ≥125 mm |
| Cavity | 14.3% (7,164) | 71% of 21.8m cavity-wall homes |

Share of homes with neither flag, by NEED age band: before 1930, 81.7%; 1930-72, 63.5%; 1973-99,
70.5%; 2000 or later, **98.8%**. The last figure is the giveaway. New-build homes are insulated to
Part L, and they carry no scheme flag because they never needed a scheme.

## How this world uses it

`premise_population.draw_premise_from_joint` (the live world stock since 2026-09-10) and
`tools/demand_vector_coverage._fabric_for` map flags to insulation: two flags is FULL, one is
PARTIAL, none is POOR. On 2,000 draws at seed 42 this gives **POOR 72.1%, PARTIAL 22.0%, FULL
5.9%**. `fabric_physics` gives POOR a U-value multiplier of 1.00, against 0.70 for PARTIAL.

A bound on the error, using only published figures: a home with "neither measure" cannot be more
common than a loft below 125 mm, which is 33% of lofted homes. The world's 72% is more than twice
that ceiling. Two consequences:

- Fabric heat loss is overstated for most of the world's prospects, so heating demand is too.
- The 2026-09-10 claim in `premise_population.py`, that the mean remaining insulation ceiling rises
  48% (41.5 to 61.4 W/K), is inflated by the same misread. The correction now sits beside it.

The book's founder homes still come from `draw_premise`, which maps insulation from the EPC letter
(86% PARTIAL). They are unaffected for now. W2_21's remaining step, drawing the founders from the
fitted joint, would carry the defect into the book. **That step is held until this is fixed.**

## What a fix needs, and what is not established

- **Loft.** Treat a flag as installed. Otherwise draw "insulated" with probability
  q = (P_pub − P_flag) / (1 − P_flag), so that the stock reproduces HEE's 67%. This is arithmetic on
  two published numbers. Lofts are only a property of homes that have one, so flats need to be
  handled.
- **Walls.** HEE gives 71% of cavity walls filled and 11% of 8.5m solid walls insulated. Applying
  either share needs the wall type of each home. **GAP:** no published table in the knowledge layer
  gives cavity versus solid by age band and property type. The RdSAP note
  (`what_rdsap_and_sap_publish_for_a_homes_fabric_by_age_band.md`) already says Table 1 age bands do
  not determine construction. The likely source is the EHS stock tables (wall type by dwelling age),
  and that has not been read yet.
- **Mapping to the three-level enum.** The world's FULL/PARTIAL/POOR is coarser than loft plus wall.
  The existing count rule can stay once each measure means "present" rather than "scheme-installed".
