**Knowledge:** vulnerability-and-the-psr

# Separating the age-routed deprivation instrument from the household: how much of V's age gap is real, Understanding Society wave 14 (2026-11-09)

This page works G7 of `wiring_the_precarity_state_to_what_a_supplier_can_see_2026-11-09.md`. The V2-shaped target on
`v2_shaped_precarity_strengths_and_the_payment_tenure_cells_understanding_society_2026-11-09.md` pools two
material-deprivation modules that wave 14 routes by age: working-age households answer "savings" and "replace broken
electrical goods" (36.2% V); pensioner households answer "pay a £200 unexpected expense" (7.6% V). Pensioners rarely
prepay, so pooling inflates prepayment's odds ratio from 3.24 (under-65s, one module) to 4.00. The world draws no age
(G3), so the build must draw pooled cells, and its default constants depend on **how much of the 36.2% / 7.6% gap is
the household and how much is the question**. That page called it not separable on the file. This page separates it
with an instrument every household answers.

**No world or supplier value changes on this page.** The wiring build waits for the correctness stretch to exit.

**Data.** SN 6614 wave 14 household file (`n_hhresp`), the reference person's age from `n_indall` (`age_dv` via
`hrpid`), weighted by `hhdeng2_xw`. Read in `~/ukds/` only (W11); this page holds aggregates only. **Disclosure:** no
published cell under 30 unweighted households; shares to one decimal. Citation: University of Essex, ISER (2025).
*Understanding Society: Waves 1-15, 2009-2024 and Harmonised BHPS: Waves 1-18, 1991-2009.* UK Data Service. SN: 6614.

## 1. Definitions, fixed before any outcome was read

**What I knew when writing this.** Everything on the V2 and T pages: V 27.8% (adult module 36.2%, pensioner 7.6%),
prepayment OR 4.00 pooled and 3.24 within the under-65s, T's age ratio 0.43 (OR 0.36). I had read the item labels and
codes of the modules and of `hheat`, and no value of any of them.

- **V, the age OR of V, and the six cells** exactly as the V2 page.
- **The common instrument (A1).** `hheat` = 2: the household cannot keep the home adequately warm. It sits outside
  both modules and is asked of every household whatever its age, so its age gradient is a household gradient on one
  question. Code 3 ("doesn't apply") and negatives are left out.
- **The matched-content check (A2).** Both modules carry a warmth item, worded for their module: the adult module's
  `matdepd` = 2 ("would like but cannot afford", keep the house warm) and the pensioner module's `pdepi2` = 1 ("home
  kept warm: no, no money for this"). Each module's warmth rate divided by `hheat`'s rate in the same households is the
  module's **reporting ratio on matched content**. If the pensioner module's ratio is lower, its "no money" route
  under-reports deprivation relative to the adult module on the same content: an instrument effect measured, not
  inferred. The holiday pair (`matdepa` = 2 / `pdepd2` = 1) is printed beside it as a second matched pair.
- **The decomposition.** V's log age odds ratio (65+ against under-65) = the household part + the instrument part. The
  household part is taken as A1's log age odds ratio; the instrument part is the remainder. **This assumes the
  household age gradient on "cannot save or absorb a shock" equals that on "cannot keep warm".** It is an assumption,
  so the page carries a second anchor: T's age OR (0.36, one instrument, already published).
- **The correction.** Shift every 65+ cell's log-odds of V by one constant Δ, chosen so that the 65+ share of V, against
  the under-65 share, has the anchor's age odds ratio. This keeps the 65+ cells' own payment × tenure structure and
  replaces only their level. Pool by weight to give the **corrected six cells**, the corrected pooled prepayment odds
  ratio and the corrected V share. Done once on A1 and once on T's OR.
- **The crossover households, descriptive only.** Households whose reference person is 65+ yet answered the adult
  module (520 on the V2 page). Their V rate is the adult instrument read on older households, but the routing that
  sent them there is not documented here, so it is printed and not used.
- Intervals: 95% from 200 bootstrap replicates resampling PSUs within strata, as the sister pages.

## 2. Predictions, filed before any outcome was read

| # | Prediction | Counts as refuted if |
|---|---|---|
| R1 | A1's age OR (65+ against under-65 on `hheat`) is between 0.25 and 0.60: pensioners are less deprived on one question, but by far less than V's raw gap (about 0.15) | outside 0.25-0.60 |
| R2 | The instrument is between 30% and 70% of V's log age gap, on A1 | outside 30-70% |
| R3 | **On matched content the pensioner module under-reports**: its warmth reporting ratio (`pdepi2` / `hheat`, 65+) is below the adult module's (`matdepd` / `hheat`, under-65) | pensioner ratio ≥ adult ratio |
| R4 | The corrected pooled prepayment OR (A1) is between 3.24 and 4.00, and below 3.70 | outside 3.24-3.70 |
| R5 | The corrected V share (A1) is between 30% and 35% | outside 30-35% |
| R6 | Each of the six corrected cells lies between its under-65 cell and its pooled cell | any cell outside |
| R7 | The crossover households' V rate lies between 7.6% and 36.2% | outside |

**The decision, filed with the predictions.** The build's default cells become the corrected cells of whichever anchor
(A1 or T) gives the **lower** pooled prepayment OR, if that OR lies between 3.24 and 4.00 (F11: the weaker flag is the
safe direction). The under-65 cells stay as the floor arm and the pooled cells as the upper arm. If the corrected OR
falls outside 3.24-4.00, the correction is not trusted, the under-65 default stands, and the page says why.

Each verdict will sit beside its prediction. A refuted prediction stays as written.

## 3. Results

*Not yet measured.*
