**Knowledge:** vulnerability-and-the-psr

# Is the pensioners' stronger prepayment relation the household or the question? Understanding Society wave 14 (2026-11-10)

This page takes the one item that
`separating_the_age_routed_deprivation_instrument_from_the_household_understanding_society_2026-11-09.md` (the G7
page) left open. Among households whose reference person is 65+, prepayment's odds ratio on V is **6.01** [4.72, 7.80].
Among the under-65s it is **3.48** [3.10, 3.92]. The pooled ratio is 4.20. The G7 page split that excess, in log terms,
into about 55% age composition and about 45% the pensioners' own within-age relation. It could not say whether that
45% is the household or the question. The question is the pensioner module's "pay a £200 unexpected expense, no money
for this", asked only of pensioners. The answer decides the wiring build's central arm:
- **3.87** if the stronger relation is all question: the 65+ cells keep the under-65 structure at A1's level.
- **4.22** if it is all household: the A1-corrected cells.

**No world or supplier value changes on this page.** The wiring build waits for the correctness stretch to exit.

**Data.** As on the G7 page: SN 6614 wave 14 `n_hhresp`, the reference person's age from `n_indall`, weighted by
`hhdeng2_xw`, and the G7 page's rebuilt flag sample. Read in `~/ukds/` only (W11), with aggregates only here. **Disclosure:** no
published cell under 30 unweighted households, and shares to one decimal. Citation: University of Essex, ISER (2025).
*Understanding Society: Waves 1-15, 2009-2024 and Harmonised BHPS: Waves 1-18, 1991-2009.* UK Data Service. SN: 6614.

## 1. Definitions, fixed before any outcome was read

**What I knew when writing this.** Everything on the G7 page:
- the six cells by age;
- V's prepayment ORs 6.01 / 3.48 / 4.20;
- `hheat`'s age OR 0.45;
- the matched-content warmth reporting ratios 0.47 (pensioner module) and 1.43 (adult module).

I had read **no** prepayment odds ratio on `hheat`, on arrears or on either module's warmth item, in either age group.

The idea is a difference in differences. The pensioner module is one instrument, and the under-65s answer another.
Prepayment's relation to *any* question differs by age partly because the households differ. Measure that household
difference on a question both groups answer, and the remainder of V's difference is the question.

- **The within-age excess on V.** E_V = log(OR_V,65+ / OR_V,<65) = log(6.01 / 3.48) on the rebuild.
- **B1, the common instrument.** On `hheat` = 2 (cannot keep the home adequately warm, asked of every household), the
  prepayment odds ratio in each age group, on the flag sample's households with `hheat` valid. The household excess is
  E_A1 = log(OR_A1,65+ / OR_A1,<65). **The household share s = E_A1 / E_V.** It is clipped to [0, 1] for the arm and
  printed unclipped.
- **B2, a second common anchor.** The same quantity on household bill arrears (`xphsdba`, the flag sample's arrears
  variable). Arrears is partly mechanical for prepayment, because debt is a route onto a prepayment meter. So B2 is printed
  as a cross-check and does not enter the decision.
- **B3, the question measured directly, on matched content.** Within the 65+ pensioner-module households, compare the
  prepayment OR on the module's own warmth item (`pdepi2` = 1, "no money for this") with the prepayment OR on `hheat` in
  **the same households**. Their log ratio is the pensioner route's effect on the gradient for that content. The adult
  module's counterpart is the same comparison among under-65 adult-module households (`matdepd` = 2 against `hheat`).
  If the pensioner route concentrates on prepayers more than the adult route does on the same content, that is a
  question effect measured directly.
- **The arm.** The 65+ cells take logits interpolated between the under-65 cells (weight 1 − s) and their own observed
  cells (weight s), then shift by one constant to A1's age level, exactly as the G7 page's correction. At s = 0 this is
  the 3.87 arm and at s = 1 the 4.22 arm. **The central arm is the pooled prepayment OR at the point estimate of s.**
- **Intervals.** 95% from 200 bootstrap replicates resampling PSUs within strata, as on the G7 page.
- **Caveat stated now.** An odds ratio depends on where a question's threshold sits on the underlying hardship, and
  `hheat` (65+ 8.6%, under-65 17.3%) does not sit where V does (7.6%, 36.2%). The 65+ prevalences are close, but the
  under-65 ones are not. That is why B3 compares within one age group, at matched content.

## 2. Predictions, filed before any outcome was read

| # | Prediction | Counts as refuted if |
|---|---|---|
| P1 | Prepayment's OR on `hheat` is higher among the 65+ than among the under-65s (the households differ: prepaying pensioners are a selected, poorer group) | OR_A1,65+ ≤ OR_A1,<65 |
| P2 | The household share s on B1 lies between 0.2 and 0.8 | outside 0.2-0.8 |
| P3 | s's 95% interval is wider than 0.6: this file separates the two only loosely | width ≤ 0.6 |
| P4 | B2 (arrears) gives a household share within 0.3 of B1's | differs by more than 0.3 |
| P5 | On matched content, among 65+ pensioner-module households, the warmth item's prepayment OR exceeds `hheat`'s in the same households (the "no money" route concentrates on prepayers) | module OR ≤ `hheat` OR |
| P6 | The central arm lies between 3.95 and 4.15 | outside 3.95-4.15 |

**The decision, filed with the predictions.** The build's central arm is the interpolated arm at B1's point estimate
of s, if s's 95% interval excludes at least one of 0 and 1. If the interval covers both 0 and 1, the file cannot
separate household from question. Then the central arm is **3.87**, the all-question arm, because F11 prefers the
weaker flag, the safe direction for a flag-reading supplier. In both cases the floor (3.48, the under-65 cells) and
the upper arm (4.22) stand as the G7 page set them.

Each verdict will sit beside its prediction. A refuted prediction stays as written.

## 3. Results

*Filled after the measurement, in a later commit.*
