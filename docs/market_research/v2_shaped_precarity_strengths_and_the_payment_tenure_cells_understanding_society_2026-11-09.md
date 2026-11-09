**Knowledge:** vulnerability-and-the-psr

# The world's precarity construct measured on its own terms: V2-shaped strengths and the payment × tenure cells, Understanding Society wave 14 (2026-11-09)

This page closes G1 and G2 of `wiring_the_precarity_state_to_what_a_supplier_can_see_2026-11-09.md`. The strengths
measured so far are for T (finds it difficult to get by, or cannot keep the home warm: 20.7%,
`which_supplier_observable_recovers_precarity_understanding_society_2026-11-09.md`). The world's state V2 is drawn
at 30% on CIM's construct: **cannot save, or cannot absorb an unexpected expense.** Carrying T's odds ratios onto a
30% V2 raises prepayment's precision from 40% to 53% at the same recall, which flatters a flag-reading supplier
(F11). This page measures the strengths on a V2-shaped target, and publishes the six cells
P(target | prepayment or not × owner / private rent / social rent) that the build would draw from.

**No world or supplier value changes on this page.** The build waits for the correctness stretch to exit.

**Data.** SN 6614 wave 14 household file, joined to the reference person's age (as the sister pages), weighted by
`hhdeng2_xw`. Read in `~/ukds/` only (W11); this page holds aggregates only. **Disclosure:** no published cell under
30 unweighted households; shares to one decimal. Citation: University of Essex, ISER (2025). *Understanding Society:
Waves 1-15, 2009-2024 and Harmonised BHPS: Waves 1-18, 1991-2009.* UK Data Service. SN: 6614.

## 1. Definitions, fixed before any outcome was read

**What I knew when writing this.** Everything on the T page and the wiring page. I had read the item labels and
their coverage by the reference person's age (valid answers, not values), and nothing else about these items.

**Which items exist.** Wave 14 has no individual saving item (`save`, `saved` are not on the wave 14 file). It holds
two material-deprivation modules, routed by age:

| Module | Households with a valid answer | Items used |
|---|---|---|
| Adult material deprivation (`matdep*`) | 13,762 with a reference person under 65; 520 aged 65+ | `matdepf` "savings": regular savings for rainy days; `matdeph` "electrical goods": replace broken electrical goods. Code 2 = would like it but cannot afford it |
| Pensioner material deprivation (`pdep*`) | 6,712 with a reference person 65+; 197 under 65 | `pdepo2` "pay unexpected expense: no, no money for this" (the pensioner module's unexpected-expense item) |

- **The target: V2-shaped (V).** A household is V if **either** module says it cannot afford it: `matdepf` = 2 **or**
  `matdeph` = 2, **or** `pdepo2` = 1. It is not-V if it answered at least one module and is V on none. A household
  with no valid answer in either module is left out. Replacing broken electrical goods is the adult module's
  unexpected-expense item (the standard reading in the EU-SILC and FRS deprivation literature); regular savings is
  its "cannot save" item. This is CIM's construct in the survey's words, as near as wave 14 allows.
- **What is not the same.** The two modules are not one question asked of everyone. A pensioner is V only through
  the £200 unexpected-expense item; a working-age household through savings or replacing goods. So the age
  relation of V is partly a relation of the instrument, and this page will not publish an age contrast on V as a
  finding. The flags below are graded on the pooled V, and separately within the under-65s (one module) as a check.
- **The flags (as the T page):** prepayment (electricity or dual-fuel paid by prepayment meter); behind on bills
  (`xphsdba`, all household bills); tenure from `tenure_dv`: owner (1-2), social rent (3-4), private rent (5-7);
  other tenures (8) are left out of the cells.
- **The six cells:** weighted P(V | payment × tenure) with unweighted n, and 95% intervals from 200 bootstrap
  replicates resampling PSUs within strata.
- **The interaction check:** the odds ratio of prepayment on V within each tenure, and the ratio of the observed
  cell odds to the odds a no-interaction (main-effects) logistic model predicts.

## 2. Predictions, filed before any outcome was read

| # | Prediction | Counts as refuted if |
|---|---|---|
| Q1 | V is between 20% and 30% of households: broader than T (20.7%), at or below the world's 30% | outside 20-30% |
| Q2 | **Prepayment is weaker on V than on T**: its odds ratio on V is below T's 3.20 | OR ≥ 3.20 |
| Q3 | Renting's odds ratio on V is between 3 and 6 (T: 4.23) | outside 3-6 |
| Q4 | **Prepayment's precision on V, at V's own prevalence, is under 53%**, the figure the transfer of T's odds ratios to a 30% V2 produces | precision ≥ 53% |
| Q5 | **The flags are sub-multiplicative**: prepayment's odds ratio among social renters is smaller than among owners | OR among social renters ≥ OR among owners |
| Q6 | Every one of the six cells holds at least 30 unweighted households | any cell under 30 |
| Q7 | AUC of prepayment + arrears on V is between 0.62 and 0.74 (T: 0.68) | outside 0.62-0.74 |

Each verdict will sit beside its prediction. A refuted prediction stays as written.

## 3. Results

21,385 households carry a positive weight; 21,215 answered one of the two modules (14,306 the adult module, 6,909
the pensioner module, none both). The flag and cell results use the 19,829 with V, payment method, arrears and one of
the three tenures (V = 27.7% there). Intervals are 95% from 200 bootstrap replicates resampling PSUs within strata.
The smallest published cell holds 482 households (pooled) and 43 (by age, below).

| # | Result | Verdict |
|---|---|---|
| Q1 | **27.8%** are V (n = 21,215). The adult module 36.2%, the pensioner module 7.6% | **Held** |
| Q2 | Prepayment's odds ratio on V **4.00 [3.68, 4.37]**, against 3.20 on T | **Refuted**: stronger on V, not weaker. Within the under-65s (one module) it is 3.24, the same as T |
| Q3 | Renting's odds ratio on V **4.80 [4.46, 5.25]** (under-65s 3.92) | **Held** |
| Q4 | Prepayment's precision on V **55.2% [53.3%, 57.4%]**, recall 25.8% | **Refuted**: at or above the 53% the transfer produced |
| Q5 | Prepayment's odds ratio within owners **3.07**, within social renters **2.00**, within private renters 1.61. Owners minus social +1.07 [+0.46, +1.74] | **Held** |
| Q6 | Smallest cell 482 unweighted households | **Held** |
| Q7 | AUC of prepayment + arrears on V **0.677 [0.671, 0.686]** (T: 0.680) | **Held** |

**The six cells, P(V | payment × tenure), weighted, all ages.**

| | Owner | Private rent | Social rent |
|---|---|---|---|
| **Prepayment** | 35.5% [31.4, 40.0], n = 498, 2.0% of households | 53.3% [48.3, 57.7], n = 482, 3.6% | 61.6% [59.2, 64.3], n = 1,093, 7.3% |
| **Not prepayment** | 15.2% [14.6, 15.8], n = 14,030, 60.6% | 41.4% [38.9, 44.5], n = 1,966, 14.7% | 44.5% [42.4, 46.6], n = 1,760, 11.8% |

A main-effects model (prepayment, private, social: odds ratios 2.02, 3.69, 4.37) fits four cells to within 5% on the odds
and private prepayers at 0.84 of them, and misses one: **prepaying owners are 35.5% V, where the main effects predict 27.0%.**
Multiplying single-flag odds ratios would understate exactly the cell where prepayment tells a supplier the most.

**The same cells by the reference person's age** (each age band answers one module, so the bands are not on one
instrument and their levels are not comparable with each other):

| | Owner | Private rent | Social rent |
|---|---|---|---|
| Under 65, prepayment | 40.7% (n = 378) | 56.8% (n = 439) | 67.2% (n = 870) |
| Under 65, not | 22.2% (n = 8,473) | 44.6% (n = 1,705) | 57.8% (n = 1,153) |
| 65+, prepayment | 18.5% (n = 120) | 19.4% (n = 43) | 37.0% (n = 223) |
| 65+, not | 3.7% (n = 5,553) | 14.7% (n = 261) | 20.1% (n = 607) |

Other flags on V, pooled: behind on bills flags 10.0%, precision 80.1%, recall 29.0%. Renting precision 47.5%,
recall 64.1%. AUC: renting alone 0.685; prepayment + arrears + tenure 0.742 (T: 0.74). V and T overlap but are not
one state: half of V is T (P(T | V) = 50.9%), and two thirds of T is V (P(V | T) = 68.0%).

## 4. What this means for the wiring

1. **G1 is closed, and the worry it named is not borne out.** Measured on a V2-shaped construct, prepayment's
   precision is 55%, not below the 53% that carrying T's odds ratios to a 30% V2 produced. The transfer did not
   flatter a flag-reading supplier. If anything it understated prepayment. Recall is the same on both constructs
   (about a quarter), and so is the supplier's two-record AUC (0.68). **A supplier reading prepayment still misses
   three in four V households.**
2. **Part of the pooled strength is the instrument, not the household.** Pensioners answer a narrower item (£200
   unexpected expense), on which 7.6% are V, against 36.2% of working-age households on savings or replacing goods.
   Pensioners rarely prepay, so pooling inflates prepayment's odds ratio from 3.24 (one instrument) to 4.00. Some of
   that age gradient is real (T, one instrument for all ages, puts the 65+ at 0.43 of the rest's rate). How much is
   not separable on this file. **This is the new GAP (G7 on the wiring page).**
   **Corrected by measurement, 9 Nov:** it is separable (`hheat` is asked of every age), and the explanation above is
   wrong. The instrument sets the pensioners' level, but lifting it to the household gap leaves the pooled odds ratio
   where it was. The pooled excess over the under-65s is age composition (about 55%) plus the pensioners' own
   stronger within-age relation (about 45%), not instrument inflation:
   `separating_the_age_routed_deprivation_instrument_from_the_household_understanding_society_2026-11-09.md`.
3. **The world draws no age (G3), so it can only take the pooled cells or a single-instrument version of them.**
   Under F11 the build's default should be the weaker one: the under-65 cells' odds-ratio structure (prepayment
   within tenure 2.4 / 1.6 / 1.5, tenure 2.8 to 4.8 without prepayment), renormalised so the population share equals
   the toggle. The pooled cells are the upper arm. Both are on this page, so the choice is the build's and can be
   reversed in one line.
4. **The cells must be drawn as cells, not as multiplied odds ratios (G2 closed).** The flags are sub-multiplicative
   within renting and super-multiplicative for prepaying owners. Six cells cost nothing more to carry than two odds
   ratios.
5. **The world's 30% is consistent with this construct.** V is 27.8% here, inside the toggle's 26-32% range. The
   fallback the wiring page held in reserve (redefine V2 as T at 20.7%) is not needed.
6. **The build's acceptance band moves very little.** The two-record AUC on V (0.677) is the same as on T (0.680),
   and with tenure 0.742 (T: 0.74). The wiring page's §6 band stands.

**Not established here.** Whether the pensioner module's item and the adult module's items pick out the same
households at the same ages (G7). Energy-specific arrears (G5). The cells for Scotland, Wales and Northern Ireland
separately (the cells are UK-weighted).
