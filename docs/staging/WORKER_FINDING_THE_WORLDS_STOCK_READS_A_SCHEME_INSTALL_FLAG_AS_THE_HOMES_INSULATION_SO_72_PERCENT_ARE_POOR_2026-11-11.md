**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_21_the_premise_joint_is_fitted_not_drawn_independently`

# The world's stock reads a scheme-install flag as the home's insulation, so 72% of homes are POOR (2026-11-11)

**What was found.** `draw_premise_from_joint`, the world's live stock path, sets insulation from
NEED's `LI_FLAG` and `CWI_FLAG`: both is FULL, one is PARTIAL, neither is POOR. DESNZ's metadata
defines each flag as an install "under a government scheme from 2000 onwards". So a missing flag
means no scheme record, not an uninsulated home. Drawn stock: POOR 72.1%. HEE Dec 2025 has 67% of
lofts insulated to at least 125 mm and 71% of cavities filled. 98.8% of NEED's homes built from 2000
on carry neither flag. The knowledge page, with the measurement and a published bound, is
`docs/market_research/need_insulation_flags_count_scheme_installs_not_insulated_homes_2026-11-11.md`.

**Consequences.** The world's prospects have overstated fabric heat loss. The 2026-09-10 "+48%
remaining insulation ceiling" claim is inflated, and a correction now sits beside it in
`premise_population.py`. W2_21's remaining step, putting the book's founder homes on the fitted
joint, would carry this defect into the book, so that step is **held** until this is fixed. The
founders still draw insulation from the EPC letter (86% PARTIAL). That mapping is unsourced, but
it is not this defect.

**What retires it.** Loft: keep a flag as installed, and otherwise draw insulated at the rate that
reproduces HEE's 67%. That is arithmetic on published figures. Walls: this needs wall type
(cavity or solid) by age and type. That is a **GAP**, and the EHS stock tables are the next read.
The control is that the drawn stock's loft-insulated share reproduces HEE within sampling error. Its
must-fail arm is today's flag-only mapping, which gives 14%.

## End-to-end check

Explanations considered, ranked by the evidence. (1) The flag is misread. The metadata settles this.
(2) The world is right and HEE overstates coverage. Not supported: post-2000 homes at 98.8% "neither"
cannot be right under Part L. (3) The flag-to-enum rule was meant as "ceiling remaining", not
"insulation present". Possible as an intent, but `fabric_physics` reads the enum as present-state
U-values, so the demand is wrong either way.

## Reverse

Delete this file, the market_research note, and the two comment blocks in
`simulation/premise_population.py`. No code behaviour changed.
