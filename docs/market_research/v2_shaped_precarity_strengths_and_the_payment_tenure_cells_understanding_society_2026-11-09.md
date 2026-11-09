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

*Pending: this section is written by the commit after the one that files the predictions above.*
