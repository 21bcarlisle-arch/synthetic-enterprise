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

The flag sample is the G7 page's rebuild: V's prepayment OR is 3.48 among the under-65s and 6.01 among the 65+.
Intervals are 95% from 200 bootstrap replicates resampling PSUs within strata.

**A coding note first.** The G7 rebuild's arrears flag (`arr`) counts `xphsdba` codes 1 and 2 as arrears. The wave 14
dictionary has 1 = up to date with all bills, 2 = behind with some, 3 = behind with all. On the G7 page that flag
was only a validity filter over the same codes 1-3, so the sample and every printed figure stand. The earlier pages'
arrears outcome (`fit_v2.py`, `fit_proxy.py`: codes 2 and 3) was coded correctly. B2 below uses 2 or 3.

| # | Result | Verdict |
|---|---|---|
| P1 | Prepayment's OR on `hheat` = 2 (cannot keep warm): under-65 **3.06 [2.77, 3.44]**, 65+ **2.25 [1.67, 2.93]** | **Refuted.** On a question both groups answer, pensioner prepayers stand out *less* than younger prepayers |
| P2 | Household share on B1, s = **−0.56 [−1.56, −0.05]**; 98.5% of replicates below 0, 0.5% above 1 | **Refuted**: below the range, and below zero |
| P3 | s's interval is 1.5 wide | **Held** |
| P4 | B2, arrears (behind with some or all bills): OR under-65 **4.36 [3.76, 4.92]**, 65+ **4.42 [2.52, 6.87]**; s = **0.03 [−1.18, 0.94]**, against B1's −0.56 | **Refuted** (they differ by 0.59). Both say the same thing, though: no stronger household relation among the 65+ |
| P5 | Matched content inside the 65+ pensioner-module households: prepayment's OR on the module's warmth item ("no money for this") **2.03 [1.23, 3.02]**, against `hheat`'s **2.06 [1.56, 2.72]** in the same households (log ratio −0.01 [−0.38, 0.26]). Adult module, under-65: 3.01 against 3.16 | **Refuted.** The "no money" route does not concentrate on prepayers when the content is held fixed |
| P6 | Central arm **3.87 [3.49, 4.37]** (s clipped to 0). On the arrears anchor it would be 3.88 | **Refuted** (below 3.95) |

**The decision, as filed.** s's interval excludes both 0 and 1, so the arm is taken at the point estimate, clipped
to 0. **The wiring build's central arm is 3.87**, the all-question arm, whose 65+ cells are the under-65 structure at
A1's level. The floor (the under-65 cells, 3.48) and the upper arm (4.22) stand as the G7 page set them. Read either
way, the file would have picked 3.87 here: F11 picks it too when the two cannot be separated.

**A post-hoc descriptive, not pre-registered.** It asks whether a rarer item steepens the relation by itself. Among
under-65 adult-module households, prepayment's OR rises as the liquidity item narrows:
- 3.54 on V (37% prevalence);
- 3.35 on savings alone (26%);
- 3.78 on replacing goods alone (32%);
- 4.02 when both are reported (19%).

A threshold effect, then, but not one that reaches 6.0 at the £200 item's 7.6% unless it steepens sharply in the tail.

## 4. What this means

1. **The pensioners' 6.0 is the question, not a household difference that the world would need.** On the two
   things every household is asked, warmth and bill arrears, the prepayment gradient among the 65+ is no stronger
   than among the under-65s. On warmth it is weaker. So nothing about prepaying pensioners as households makes
   prepayment a sharper flag for them.
2. **The question effect is the item's content and narrowness, not its "no money" wording.** On matched warmth
   content the pensioner route has the same prepayment gradient as `hheat`. What steepens it is the £200
   unexpected-expense item itself: a narrow liquidity question near the tail. Part of that is the threshold, as the
   under-65 rows show.
3. **For the build:** the central arm is 3.87 (floor 3.48, upper 4.22), each renormalised to the toggle as the
   wiring page says. The G7 page's sentence that the household relation lies "between 3.87 and 4.2" is now read at its
   lower end.

**Not established here.** A liquidity-specific hardship among pensioner prepayers that shows up on neither warmth nor
arrears would look like the question on this file. Separating it needs a pensioner sample asked the adult liquidity
items, which wave 14 routes away (the 513 crossover households are too few prepayers to read). The two anchors also
carry their own caveats: `hheat`'s threshold sits differently by age (§1), and arrears is partly mechanical for
prepayment. They agree in direction, and that agreement is what the decision rests on.
