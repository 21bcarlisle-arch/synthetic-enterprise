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

**The rebuild, first.** The V2 page's code was not kept, so V and its cells were rebuilt from §1 of that page. The
flag sample is 19,779 households (V2 page: 19,829), and the six pooled cells agree within 1.5 points. The rebuild
reads prepayment's pooled OR as **4.20** [3.79, 4.62] and the under-65 OR as **3.48** [3.10, 3.92], where the V2 page
printed 4.00 and 3.24. Each pair lies inside the other's interval. The likeliest source is the payment and arrears
validity filters (a household with no valid payment answer is dropped here). **Every comparison below is made inside
the rebuild, like with like.** The predictions were filed on the V2 page's scale. The verdicts read the rebuild,
and where the scale matters it is said.

Intervals are 95% from 200 bootstrap replicates resampling PSUs within strata.

| # | Result | Verdict |
|---|---|---|
| R1 | `hheat` cannot keep warm: under-65 **17.3%**, 65+ **8.6%**; age OR **0.45 [0.40, 0.49]**. V's age OR in the rebuild 0.16 [0.14, 0.17] | **Held** |
| R2 | The instrument is **56% [51, 61]** of V's log age gap on A1, and 44% on T's anchor (OR 0.36) | **Held** |
| R3 | Warmth reporting ratio on matched content: pensioner module **0.47 [0.43, 0.51]** (3.9% against `hheat`'s 8.4%, n = 6,683), adult module **1.43 [1.36, 1.51]** (23.2% against 16.3%, n = 12,629). Holiday: 0.75 against 1.82 | **Held, strongly**: on the same content, the pensioner module's "no money for this" route reports about a third as much as the adult module's "would like but can't afford" |
| R4 | Corrected pooled prepayment OR: **4.22 [3.84, 4.70]** on A1, 4.26 [3.86, 4.72] on T. The uncorrected pooled OR is 4.20 | **Refuted.** Correcting the pensioners' level does not move the pooled OR at all: it stays where it was, and above the 3.70 ceiling |
| R5 | Corrected V share **31.8% [30.8, 32.9]** on A1, 30.8% on T (flag sample) | **Held** |
| R6 | Five of the six corrected cells lie between their under-65 and pooled cells. Prepaying owners sit at 41.4% [37.5, 46.2], above the under-65s' 40.9% | **Refuted on one cell**, by half a point and well inside its interval |
| R7 | The 513 households whose reference person is 65+ but who answered the adult module are **23.6%** V | **Held** (descriptive; the routing that sent them there is not documented here) |

**The cells, P(V | payment × tenure), flag sample, weighted.**

| Cell | Pooled (rebuild) | Under 65 | 65+ (pensioner module mostly) | Corrected, A1 | Corrected, T | Post hoc: under-65 structure, A1 level | n pooled / n 65+ |
|---|---|---|---|---|---|---|---|
| Prepayment, owner | 35.6% | 40.9% | 18.5% | 41.4% [37.5, 46.2] | 39.9% | 37.6% [33.3, 43.1] | 495 / 120 |
| Prepayment, private rent | 54.0% | 57.7% | 19.4% | 56.4% [51.0, 61.3] | 55.8% | 56.2% [50.6, 61.4] | 471 / 43 |
| Prepayment, social rent | 64.3% | 70.8% | 37.2% | 70.0% [66.7, 73.1] | 68.8% | 68.0% [64.8, 71.5] | 1,056 / 222 |
| Not prepayment, owner | 15.2% | 22.3% | 3.7% | 18.2% [17.4, 19.0] | 17.3% | 18.8% [18.0, 19.8] | 13,988 / 5,550 |
| Not prepayment, private rent | 41.6% | 45.0% | 14.0% | 43.9% [41.1, 46.1] | 43.3% | 43.4% [40.5, 46.0] | 2,023 / 273 |
| Not prepayment, social rent | 45.2% | 59.3% | 20.3% | 54.5% [51.8, 57.2] | 52.2% | 53.6% [51.0, 56.0] | 1,746 / 616 |
| **Prepayment OR** | **4.20** | **3.48** | **6.01** [4.72, 7.80] | **4.22** | **4.26** | **3.87** [3.44, 4.33] | |

The last arm was **not pre-registered**. I added it after reading R4, to ask what R4's refutation is made of. It gives
the 65+ households the under-65 structure at A1's level.

## 4. What this means

1. **The age gap in V is about half question and half household.** On a question every household answers, pensioners
   are 0.45 times as likely to say they cannot keep warm (odds). On V's two questions they are 0.16 times. On matched
   content the pensioner module's route reports about a third of what the adult module's does. So the 7.6% is mostly
   the question.
2. **But the question sets the pensioners' level, not prepayment's odds ratio, and the V2 page's explanation of the
   pooled 4.00 is wrong.** That page said pooling the two instruments inflates the odds ratio from 3.24 to 4.00.
   Lifting the 65+ cells to the household gap (R4) leaves the pooled odds ratio at 4.22 against 4.20. The excess of
   the pooled ratio over the under-65s' (4.20 against 3.48 in the rebuild, log gap 0.19) has two parts, read from
   the post-hoc arm:
   - **About 55% is age composition** (3.48 to 3.87). Older households prepay less and are less deprived *on one
     question*. That is a real confounder, and a world that draws no age should carry it in its marginal cells.
   - **About 45% is the pensioners' own within-age relation** (OR 6.0 on the £200 item, against 3.5 among the
     under-65s). Whether that is household or question this file cannot say. A narrow item that picks out the most
     deprived pensioners would concentrate them among prepayers, and so would real hardship.
3. **The decision, as filed.** The lower corrected OR (4.22, A1) is outside 3.24-4.00, and outside the rebuild's
   equivalent band (3.48-4.20) too, so under the filed rule the correction is not used as the default. **The
   under-65 default stands**, for a different reason than the wiring page gave. The reason is no longer "the pooled
   strength is instrument inflation", which is refuted here. It is F11: the household-level ratio for an age-less
   world lies between 3.87 (if the pensioners' stronger relation is all question) and 4.2 (if it is all household).
   Both are above the under-65s' 3.48, so the under-65 default **understates** prepayment's strength as a flag. That
   is the safe direction for a flag-reading supplier, and the size of the understatement is now known.
   - **The arms for the build, as constants it can cite:** floor = under-65 cells (OR 3.48 in the rebuild, 3.24 on
     the V2 page); central = the post-hoc arm (3.87); upper = the A1-corrected cells (4.22). Each is renormalised to
     the 30% toggle, as the wiring page says.
   - The corrected V share (31.8%) sits inside the toggle's 26-32% range, so the toggle needs no change.
4. **For the wiring page's acceptance band**, a supplier's prepayment precision at the corrected level is 60-62%
   (flag sample), against 57% on the pooled cells.

**Not established here.** Whether the pensioners' within-age prepayment relation (6.0) is household or question
(it would need a pensioner sample asked the adult items, which wave 14 routes away). Why the 513 crossover households
were routed to the adult module. The rebuild's 0.2 gap from the V2 page's odds ratios, whose code was not kept.
