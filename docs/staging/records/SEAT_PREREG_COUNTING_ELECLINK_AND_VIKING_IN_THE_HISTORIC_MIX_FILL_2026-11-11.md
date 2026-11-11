**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** unassigned · **Atom:** `unminted`

# Prediction, filed before the fill was re-run: what counting ElecLink and Viking does to the historic-mix fill's bias (2026-11-11)

**The question.** `household_carbon` §1b showed NESO's historic-mix IMPORTS counts ElecLink and Viking, and
`sim/grid_carbon_history.fuelmix_intensity` leaves them out (`OUTSIDE_NESO_MIX`). The fill now counts them:
ElecLink at France's Table 1 factor (53), and Viking at Table 1 applied to Denmark's published electricity
output by energy type (Energistatistik, Tabel 6). Arithmetic done before this note, so it is not a
prediction: Denmark is 115 g (2023), 93 g (2024) and 68 g (2025).

**What the thing is.** `meta["arithmetic_versus_historic_mix"]`, mean_bias of the arithmetic estimate minus
NESO's historic-mix intensity, over half hours where both exist, as a percentage of the historic mean.

**Predictions (no re-run made):**
- Q1. 2016–2020 are unchanged to 0.01 g. Neither cable flowed then.
- Q2. 2021 moves by less than 0.3 percentage points (ElecLink metered from 2021-09-18, small).
- Q3. 2024 falls from +7.1% to between +4.5% and +6.5%. The basis is §1b's attribution of 1–3 g of the 8.8 g
  bias to the import share. Adding about 3 points of import share at about 70 g into a figure near 130 g moves
  it about 2 g.
- Q4. 2023 falls from +5.0% to +3.5–4.8%, and 2025 from +3.9% to +1.5–3.2%. Every post-2021 year stays
  POSITIVE: the per-market factor term (§1b point 1) is untouched and is the larger one.
- Q5. Filled half hours stay 0 in every year: the change is latent for the published series.

**What would refute.** A 2024 move above 3 points would mean the share term is larger than §1b attributed.
Any post-2021 year going negative would mean the factor term is smaller than attributed. Any year 2016–2020
moving at all would mean the change touches more than the two cables.

## Result, filed after the run (same day). The predictions above are unedited.

`sim.grid_carbon_history.build()`, run before the change (HEAD's two source files) and after, over the same caches.
Each cell is fill minus historic mix: mean bias in g, then as a % of the historic mean.

| Year | Before | After |
|---|---|---|
| 2016–2020 | identical | identical (−9.64 / −8.19 / +0.29 / +2.69 / +3.28 g) |
| 2021 | +4.45 g, +2.43% | +4.44 g, +2.42% |
| 2022 | +3.19 g, +1.76% | +3.05 g, +1.68% |
| 2023 | +7.43 g, +4.98% | +5.77 g, +3.87% |
| 2024 | +8.83 g, +7.12% | +6.67 g, +5.37% |
| 2025 | +4.92 g, +3.87% | +2.32 g, +1.83% |

Q1 held. Q2 held (−0.01 points). Q3 held (−1.75 points, inside 4.5–6.5%). Q4 held (2023 at 3.87%, 2025 at 1.83%,
all positive). Q5 held: `fuelmix_fill` is 0 in every year. In 2024, about 2.2 g of the 8.8 g bias was the two
cables, so §1b's "1–3 g" for the share term stands. The remaining 4–6 g is the per-market factor term.
