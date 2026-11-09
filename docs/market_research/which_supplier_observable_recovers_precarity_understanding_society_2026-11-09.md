**Knowledge:** the-customer-needs-framework

# Which supplier observable recovers precarity: Understanding Society wave 14 (2026-11-09)

The third step of the registration pack's order (`docs/director/UKDS_REGISTRATION_PACK.md`). The sister pages found
one precarity factor, indicated by bill difficulty, a cold home, prepayment and renting, and only moderately by income
(`precarity_affluence_and_life_stage_on_one_record_understanding_society_2026-11-09.md`), and a separate cash buffer
led by income (`the_cash_buffer_by_age_and_income_wealth_and_assets_survey_2026-11-09.md`). A real supplier holds
none of the factor's survey indicators. The question here is: **which observable that a supplier actually holds best
picks out the precarious household, and how much does it miss?**

## 0. Why this runs on SN 6614, not SN 9315 (a correction to the pack)

The pack's row for the English Housing Survey 2022-23 (SN 9315) says it holds "tenure, household type and payment
method on one record". **The End User Licence file does not hold payment method.** The questionnaire asks it
("Which of these methods do you use to pay for your electricity?"), but that is a primary "raw" item, and the
household user guide says raw items are released under the Special Licence only. The EUL release is two derived files
(`interviewfs22_eul`, 73 variables; `generalfs22_eul`, 9). Neither carries a payment method, an arrears item, a
difficulty item or a cold-home item. So SN 9315 as licensed cannot answer the proxy question: it has the candidate
observable tenure, but no precarity outcome to recover. SN 9593 adds only the dwelling's market value on its linked
households, which has the same gap.

Understanding Society wave 14 holds every candidate and the outcome on one household record, so the fit runs there.
SN 9315 is left for what it can do (the joint of tenure, household type and means-tested benefit in England), which
this page does not need.

**Data.** As the sister page: SN 6614 wave 14 household file, joined to the reference person's age, financial
situation and benefit receipt, weighted by `hhdeng2_xw`. Read in `~/ukds/` only (W11 as amended 3 Nov); this page
holds only aggregates. **Disclosure:** no cell under 30 unweighted households; shares to one decimal; AUC to two.
Citation: University of Essex, ISER (2025). *Understanding Society: Waves 1-15, 2009-2024 and Harmonised BHPS: Waves
1-18, 1991-2009.* UK Data Service. SN: 6614.

## 1. Definitions, fixed before any outcome was read

**What I already knew when writing this.** The sister page's one-factor loadings (arrears +0.83, finding it difficult
+0.69, cold +0.67, prepayment +0.63, owner -0.81, income -0.37). I had not read any share of the target below, nor any
relation of benefit receipt or age 65+ to it.

- **The target: precarious (T)** = the reference person finds it quite or very difficult to get by (`finnow` 4-5),
  **or** the household cannot keep the home adequately warm (`hheat` = No). Both are invisible to a supplier. Arrears
  and prepayment are left out of the target because they are candidate observables; putting them in would make the
  test circular.
- **The candidate observables, and how a supplier would hold each:**
  - **O1 Prepayment**: electricity, or dual-fuel, paid by prepayment meter (as the sister page). The supplier's own
    record.
  - **O2 Behind on bills**: `xphsdba` behind with some or all bills. A supplier holds only its own energy arrears;
    this item covers all household bills, so it is a stand-in, and wider than what a supplier sees.
  - **O3 Renting**: `tenure_dv` social or private rent. Held only if the customer gives it, or inferred from
    change-of-tenancy patterns.
  - **O4 Means-tested benefit**: anyone in the household receives Universal Credit, Income Support, JSA, ESA or
    Pension Credit (`benbase1/2/4`, `bendis2`, `benpen4` in the individual file). Partly visible through the Warm Home
    Discount's data matching (Core Groups 1 and 2: `vulnerability_psr_and_ability_to_pay_2026-10-25.md`), which tells
    a supplier which of its customers matched. It does not tell them which benefit, and Core Group 2 also requires a
    high cost to heat.
  - **O5 Aged 65+**: the reference person. Held where the customer gave a date of birth, for example on the Priority
    Services Register.
- **The reference the supplier lacks: income quintile** (equivalised, as the sister page). Not held by a supplier.
- **The measure of recovery:** for each flag, the share of flagged households that are precarious (precision) and the
  share of precarious households flagged (recall). For combinations, the weighted AUC of a weighted logistic model of
  T, fitted and scored on the same households (in-sample; with at most six binary inputs, overfitting is negligible
  at this n).

## 2. Predictions, filed before any outcome was read

| # | Prediction | Counts as refuted if |
|---|---|---|
| P1 | 10-20% of households are precarious (T) | outside 10-20% |
| P2 | Of the single supplier-held flags (O1, O2), behind on bills has the higher precision for T | prepayment's precision ≥ arrears' |
| P3 | **Prepayment alone misses most precarious households**: it flags under 35% of them | recall ≥ 35% |
| P4 | **The supplier's own records nearly match income**: the AUC of prepayment + arrears is within 0.05 of the AUC of income quintile alone | income quintile's AUC exceeds the pair's by more than 0.05 |
| P5 | Adding renting to the pair adds at least 0.03 AUC; then adding means-tested benefit adds under 0.02 more | renting adds under 0.03, or benefit adds 0.02 or more |
| P6 | **Age points the wrong way**: the precarious share among households whose reference person is 65+ is under half that among the under-65s | at least half |

Each verdict will sit beside its prediction. A refuted prediction stays as written.

## 3. Results (D)

21,385 households carry a positive weight. The flag-by-flag and AUC results use the 17,389 households with every
item answered (precarious share 20.6% there). Intervals on the contrasts are 95% from 200 bootstrap replicates that
resample PSUs within strata. The smallest published cell has 1,348 households.

| # | Result | Verdict |
|---|---|---|
| P1 | **20.7%** are precarious (n = 18,649): 11.9% find it difficult, 14.7% cannot keep warm | **Refuted**, narrowly: just over 20% |
| P2 | Precision: behind on bills **68.2%**, prepayment **40.6%** | **Held** |
| P3 | Prepayment flags **25.5%** of precarious households | **Held**: three in four precarious households do not prepay |
| P4 | AUC: prepayment + arrears **0.680**, income quintile alone **0.647**; income minus the pair -0.033 [-0.047, -0.021] | **Held, and stronger than predicted**: the supplier's own two records beat income |
| P5 | Renting adds **+0.058 [+0.050, +0.065]**; then means-tested benefit adds **+0.015 [+0.013, +0.021]** | **Held**, though the benefit interval just reaches 0.02 |
| P6 | Precarious: **10.8%** of households whose reference person is 65+ (n = 6,189), **25.1%** of the rest (n = 11,200), a ratio of 0.43 | **Held** |

**Each flag against the target (weighted).**

| Flag | Households flagged | Precarious among flagged | Precarious households flagged | Precarious among the unflagged | AUC alone |
|---|---|---|---|---|---|
| Prepayment | 12.9% | 40.6% | 25.5% | 17.6% | 0.58 |
| Behind on bills | 10.1% | 68.2% | 33.4% | 15.2% | 0.65 |
| Renting (any) | 37.2% | 35.7% | 64.5% | 11.6% | 0.67 |
| Social renting | 19.3% | 36.6% | 34.3% | 16.7% | — |
| Means-tested benefit | 19.4% | 44.0% | 41.5% | 14.9% | 0.64 |
| Reference person 65+ | 31.8% | 10.8% | 16.7% | 25.1% | 0.60 (inverse) |

**Combinations (AUC, in-sample).** Prepayment + arrears 0.68; + renting 0.74; + means-tested benefit 0.75; + age 65+
**0.77**. Without arrears (prepayment, renting, benefit, age) 0.74. Income quintile + renting 0.72. Everything,
income included, 0.78. **Income adds 0.018 to what a supplier could hold.**

## 4. What this means

1. **A supplier can recover precarity about as well without income as with it.** Its own two records (prepayment and
   arrears) beat income quintile alone. With renting, Warm Home Discount matching and age, it reaches 0.77, and
   income adds under 0.02 to that. This is what the sister page's loadings implied, now measured as recovery: the
   precarity factor is visible to a supplier through what it holds (W1), and income is not the missing key.
2. **Recovery is partial, and that is the honest size of it.** An AUC of 0.77 is a useful ranking, not a diagnosis.
   The sharpest single flag, arrears, is right two times in three but finds only a third of precarious households.
   Prepayment finds a quarter. **A supplier that reads precarity from prepayment alone misses three in four
   precarious customers.** The world should draw the precarity state correlated with these flags at these strengths,
   so that a supplier which over-trusts one flag is wrong in the world as it would be in life.
3. **Tenure is the strongest single observable, and the one a supplier is least likely to hold.** Renting recalls
   two thirds of precarious households. A supplier typically learns tenure only if the customer says, or from
   change-of-tenancy patterns. That is a finding about where to look, not a licence to infer it.
4. **Age points away from precarity.** The 65+ are under half as often precarious. A supplier that uses age (for
   example, from the Priority Services Register) as a stand-in for hardship would target the wrong households.
   Age belongs to the separate cash-buffer axis and to the PSR's own needs, not to precarity.
5. **Caution on arrears.** Wave 14 asks about all household bills. A supplier sees only its own energy arrears,
   which is narrower, so its arrears flag would recall fewer precarious households than shown here. Its precision is
   not established either way. Means-tested benefit is visible to a supplier only through WHD matching, which also
   applies a cost-to-heat test in Core Group 2, so the benefit row is an upper bound on what matching shows.

**Not established here.** Energy-specific arrears. Consumption-based signals (a supplier holds the meter reads), which
this survey does not carry. Area deprivation (IMD), which a supplier can read from the postcode, is not in the end-user
file. No world or supplier value changes on this page.
