**Knowledge:** the-customer-needs-framework

# Who actually switched supplier, by age and by arrears; and whether the Wave 3 worry, affordability and willingness-to-pay results survive to 2025 (2026-11-02)

The third D-graded piece of the customer-needs domain. The needs-framework page
(`the_customer_needs_framework_cost_worry_switching_cim_waves_3_6_2026-11-02.md`) ended with two gaps: cost, worry and
willingness to pay were read in Wave 3 only, and there was no revealed-behaviour source for switching by group. Its
section 7.5 said "anti-correlated with need" should not be drawn without one, because the *stated* direction was the
opposite. This page reads both gaps from Ofgem's *Consumer Impacts of Market Conditions* (CIM) data tables, Waves 3-6.

**Data.** Wave 3 (Nov-Dec 2022, unweighted 3,457), Wave 4 (Jul 2023, 3,434), Wave 5 (Jan-Feb 2024, 3,439), Wave 6
(Jan-Feb 2025, 3,458). Workbooks re-fetched 2 Nov 2026 and their SHA-256 matched the hashes in
`data/lake/ofgem_cim_waves4_6_2023_2025/PROVENANCE.md`. The extract used here is
`cost_worry_wtp_and_revealed_switching_by_column.csv` in that directory (weighted column %, unweighted and effective
base as printed). Intervals are 95% normal on the **effective** base, as on the sister pages; a contrast is starred
only when larger than its own interval. **Grades:** D derived here; P reported by the body holding the data.

## 0. What the revealed measure is, and is not (D)

CIM question C4 asks every respondent which of these they or their household have done **in the past 6 months**
(**12 months in Wave 3 — levels do not compare across Waves 3 and 4**): compared tariffs without switching; switched
tariff with the same supplier; switched to a new supplier. It is still a *report* by a survey respondent, not a
supplier's record; but it is something the household did, not something it said it would do. "Switched to a new
supplier" is the revealed counterpart of the forward intent D3_3 ("likely to switch to a new supplier in the next three
months"); the two cannot be divided into a conversion rate, because they count different windows and different
directions of time. The only comparison made below is of contrasts between groups.

The three arrears readings are not one measure. Waves 3-4 ask about "keeping up with bills" generally; Wave 5 adds a
separate energy-bills column; Wave 6 reads *other household bills (not energy)* and also has an energy-bills column.
Primary column here is the one that keeps Wave 3's meaning (household bills; in Wave 6 the non-energy one); the
energy-bills column is shown as a sensitivity where it exists. "Behind" is the group behind on some or many bills.

## 1. Predictions, written before any C4 percentage was read

Only the C4 row labels and column headers had been seen. The stated-intent contrasts (D3_3) were already on the sister
page: age 16-24 minus 65-74 of +31.6, +31.8, +18.9, +26.8, and behind-minus-none of +14.3, +7.6, +9.8, +8.3 in Waves 3-6.

| # | Prediction | Counts as refuted if |
|---|---|---|
| R1 | Revealed new-supplier switching is higher at 16-24 than 65-74 and starred in at least 3 of 4 waves, but smaller than the stated-intent age gap in every wave | fewer than 3 starred, or any wave's gap exceeds its intent gap |
| R2 | Behind-on-bills households switch supplier **less** than those with no difficulties in at least 3 of 4 waves (arrears friction; the stated sign does not reach behaviour) | the contrast is positive in 2 or more waves |
| R3 | Income under £16k minus £80k+ is negative on revealed supplier switching in at least 3 waves, starred in at least 2 | fewer than 2 starred |
| R4 | "Compared but not switched" has the same sign as intent: the young and the behind-on-bills both higher | either group not higher in 3 of 4 waves |
| R5 | Overall "switched to a new supplier" is 10% or less in every wave | any wave above 10% |

### 1.1 How they fared

| # | Result | Verdict |
|---|---|---|
| R1 | 16-24 minus 65-74: **+4.9 ± 4.2, +7.2 ± 3.8, +6.4 ± 5.1, +2.7 ± 3.1\*** (the last is not starred). Smaller than the intent gap in all four waves (31.6, 31.8, 18.9, 26.8). | **Held**: 3 starred of 4; Wave 6 is "cannot tell" |
| R2 | Behind minus none: **+3.1 ± 3.5, +4.9 ± 3.1, +5.2 ± 3.7, +4.1 ± 3.5**; positive in all four, starred in the last three. | **Refuted**: arrears households switched supplier *more*, not less |
| R3 | <£16k minus £80k+: -0.8 ± 4.7, -3.3 ± 4.7, -1.5 ± 4.4, +0.8 ± 3.7. None starred. | **Refuted**: no income gradient in actual supplier switching |
| R4 | Compared-not-switched: age **+7.8, +15.9, +9.4, +19.7**, all starred; behind-on-bills **+0.4, -2.1, -4.2, -3.0**, none starred. | **Refuted** for arrears (held for age) |
| R5 | 7.3% (12 months), 4.6%, 5.6%, 5.3%. | **Held** |

The anti-correlation of need with switching is therefore absent in behaviour as well as in intent. What the survey does
*not* show is the other half of the stated picture: the intent gap by age (about +30) shrinks to +3 to +7 in behaviour.

## 2. Revealed switching, by group and wave (D)

Share of all respondents in the group who report **switching to a new supplier** in the window (Wave 3: 12 months;
Waves 4-6: 6 months). Effective bases of the smaller groups: behind on bills 292-367 (Waves 3-4), 259 (Wave 5),
271 (Wave 6); 16-24 in the low hundreds.

| Group | W3 (12m) | W4 | W5 | W6 |
|---|---|---|---|---|
| All | 7.3 | 4.6 | 5.6 | 5.3 |
| 16-24 | 10.8 | 9.8 | 11.8 | 6.2 |
| 25-34 / 35-44 | 8.4 / 8.6 | 5.2 / 6.4 | 3.7 / 4.7 | 5.6 / 6.5 |
| 45-54 / 55-64 | 4.9 / 7.4 | 2.9 / 2.8 | 4.7 / 4.8 | 6.6 / 4.9 |
| 65-74 / 75+ | 5.9 / 4.7 | 2.5 / 2.4 | 5.4 / 4.8 | 3.5 / 3.6 |
| No difficulties paying bills | 5.3 | 3.5 | 4.1 | 4.1 |
| Sometimes struggling | 8.1 (struggling) | 4.5 | 5.5 | 5.6 |
| Constantly struggling | (merged above) | 3.8 | 6.9 | 6.1 |
| Behind on bills | 8.4 | 8.4 | 9.3 | 8.2 |
| Behind on **energy** bills (sensitivity) | n/a | n/a | 8.2 vs 4.4 | 5.9 vs 3.9 |

Reading the table:

- **The age effect is the youngest band, and it is fading.** In Waves 4-5 the 16-24 group switches at 2-4 times the
  rate of everyone over 45 (9.8 and 11.8 against 2.4-2.9 and 3.7-5.4); in Wave 4 the 25-44s sit between (5-6%),
  in Wave 5 they do not. By Wave 6 the 16-24 figure
  (6.2) is inside the interval of the over-65s (3.5). The Wave 3 and 4 shape (a slope from 16-24 to 75+) is not the
  Wave 5-6 shape.
- **Arrears is a step, not a slope, in Waves 3-4, and a slope from Wave 5.** In Waves 5 and 6 the gradient is
  monotone with difficulty (4.1, 5.5, 6.9, 9.3 and 4.1, 5.6, 6.1, 8.2). "Behind" is about twice "no difficulties" in
  Waves 4, 5 and 6.
- **The definition of arrears matters.** On *energy* bills specifically, the behind-minus-none contrast is +3.8 ± 4.0
  (Wave 5) and +2.0 ± 3.3 (Wave 6): positive but not starred. The starred result needs the general household-bills
  reading, which is a different population in Wave 6 (non-energy bills).
- **Income does not separate supplier switchers; it separates lookers.** Compared-but-not-switched, <£16k minus £80k+:
  **-11.5 ± 8.7, -14.7 ± 8.6, -11.0 ± 8.1, -19.1 ± 7.1**, all starred. "None of these": **+18.2, +14.8, +12.5, +22.3**
  more among the poorest, all starred. The better-off compare; the actual change of supplier is flat across income.
- **Any switch, including tariff with the same supplier.** The age gap on "switched at all" is +19.9 ± 6.1 (Wave 4),
  +5.1 ± 6.9 (Wave 5), -0.5 ± 6.0 (Wave 6), and the share switching tariff with the same supplier rises from 11% to
  17% (Wave 4 to Wave 6). Some other mechanism is moving everyone onto new tariffs with their own supplier by 2025.
  That is a **hypothesis** (fixed deals ending and rolling over); the tables do not say why.

## 3. Stated against revealed, by contrast (D, with the caveat in section 0)

| Wave | Intent level (3m ahead) | Revealed level (new supplier) | Age gap: intent / revealed | Arrears gap: intent / revealed |
|---|---|---|---|---|
| 3 | 25.0% | 7.3% (12m) | +31.6 / +4.9 | +14.3 / +3.1 (not starred) |
| 4 | 27.6% | 4.6% (6m) | +31.8 / +7.2 | +7.6 / +4.9 |
| 5 | 19.2% | 5.6% (6m) | +18.9 / +6.4 | +9.8 / +5.2 |
| 6 | 24.6% | 5.3% (6m) | +26.8 / +2.7 (not starred) | +8.3 / +4.1 |

Indicatively — the windows differ, so this is a pattern and not a rate — the arrears gap keeps roughly half its size
in behaviour from Wave 4 (revealed over intent: 0.2, 0.6, 0.5, 0.5) and the age gap roughly a fifth (0.2, 0.2, 0.3, 0.1).
Stated intent therefore overstates the age difference more than it overstates the arrears difference.

## 4. Do the Wave 3 worry, affordability and willingness-to-pay results survive? (D)

**Worry about falling behind (the sister page's T160, Wave 3).** The Wave 3 wording ("falling behind on my energy
bills because of the cost of my energy", asked of direct-debit, standard-credit and bill-receipt payers) is asked again
in **Wave 4 only** (Table 175). The Wave 5 and Wave 6 indexes carry no table with that wording. Level 46.5% (Wave 3:
55.2%). Contrasts, Wave 3 → Wave 4: behind-minus-none **+51.8 → +61.7 ± 5.8**; 16-24 minus 65-74 **+29.9 → +33.0 ± 7.4**;
<£16k minus £80k+ **+10.1 ± 10.1 → +24.8 ± 9.5** (now clearly starred); not-trust minus trust **+7.5 → +11.3 ± 5.1**. Every
sign and rank holds; the income gradient is larger in Wave 4 than the sister page's "income is the weakest" had it.
That page's P1 refutation of the income gradient is therefore **one winter's reading**: restate it as "weak in
Nov 2022, +24.8 in Jul 2023".

**Affordability (E3), direct-debit payers, last three months.** (The prepayment and standard-credit tables are separate
and small.) "Any recent energy-affordability issue": **61.1% (W4), 49.3% (W5), 47.8% (W6)**. Contrast behind-on-bills
minus none: **+42.0 ± 6.6, +49.4 ± 7.6, +51.5 ± 7.0**; age: +30.8, +27.5, +31.7 (all starred); trust: +10.0, +12.4,
+10.2 (starred); income: +12.9 ± 10.3, **+33.0 ± 9.5**, +9.3 ± 8.9 (not starred in Wave 6). **The arrears and age
gradients are stable; the level falls 13 points.** This is a different question from Wave 3's Table 136 (impacts of the
price rise), so the level is not comparable to the sister page's 80.7%.

**The floor result does not survive.** The sister page found older households cut energy use because they could not
afford it **more** than the young (-14.3 ± 6.7 in Wave 3). On the E3 direct-debit table the age contrast is **-15.6 ± 8.2
(W4), +3.9 ± 9.9 (W5), -1.4 ± 7.8 (W6)**: gone by 2024. The share who reduced energy use falls 42.8% → 35.3% → 28.6%.
The warning that "worry is a poor proxy for harm" rests on one winter and one summer.

**Willingness to pay slightly more (D8_5 service, D8_6 green).** Asked in Waves 3-5, not found in Wave 6. Agree-share:
service 25.1% → 23.3% → 21.2%; green 28.5% → 28.1% → 26.0%. Contrasts (Wave 3 / 4 / 5):

| | Age 16-24 minus 65-74 | Behind minus none | Income <£16k minus £80k+ | Not trust minus trust |
|---|---|---|---|---|
| Service | +26.7 / +35.0 / +21.2 | +3.2 / -2.1 / -2.8 (none starred) | -11.9 / -12.3 / -2.2 | -10.1 / -10.3 / -12.2 |
| Green | +21.3 / +23.2 / +27.1 | -1.7 / -4.5 / +1.0 (none starred) | -15.3 / -13.8 / -6.9 | -15.9 / -13.4 / -14.4 |

Age and trust are stable in all three waves; **arrears never separates willingness to pay**; the income gradient
shrinks to within its interval by Wave 5. The sister page's reading ("a statement of attitude, not of capacity") stands.

**Cost judgement (fairness of the rise, T141 etc.).** Not found as the same tables in Waves 4-6. **GAP.**

## 5. What this changes for the framework (D, with what it does not establish)

1. **"Arrears households switch less" is not available from this source, in any form.** Stated intent, looking and
   acting each give a non-negative arrears contrast. The sister page said stated intent should not be read as
   anti-correlated with need; behaviour agrees.
2. **But do not read this as "arrears households shop".** They do not compare more (R4); they change supplier more.
   Candidate causes the tables cannot separate: (a) **age**, because arrears is concentrated in the young (the sister
   page: behind on bills 14.5% at 16-24, 0.6% at 75+) and the young switch most in Waves 3-5; (b) **imposed moves**,
   such as a supplier failing or a prepayment move, which a household may report under "switched to a new supplier";
   (c) **price-driven search by those hit hardest**; (d) **churn from poor service**. Nothing here ranks them. Ofgem
   publishes no age-by-arrears table and W11 forbids the microdata. **GAP, and an honest "we cannot tell".**
3. **Whether a supplier can *block* an arrears household's switch is not checked on this page.** A debt-based
   objection rule is believed to exist in the switching process, but it, its threshold and its wording were not read here, so no
   claim is made about it. Self-reported switching by arrears households says the barrier is not complete. **GAP: read
   Ofgem's switching licence conditions before relying on this.**
4. **For the world:** a switching propensity drawn *lower* for financially stressed households has no support in
   this source, stated or revealed. Age should carry the first-order effect, concentrated in the youngest band. The
   plausible alternative is that income acts on *comparison* (looking), and only weakly on the change itself. None of
   this changes a world value.
5. **For the supplier (observables):** a supplier sees who leaves. If the leavers over-represent arrears households,
   that is the signature of this table; it does not say they left *because* of the arrears.

## 6. What this page does not establish

- **Cause**: one-way tables. Age, arrears and income cannot be separated.
- **A supplier's record.** Self-report from a panel of about 3,400 respondents. The new-supplier share has an interval
  of 1-2 points on the total and 3-5 on the small groups; every "not starred" cell is "cannot tell".
- **The windows.** 12 months in Wave 3, 6 months afterwards, for the same question. No level crosses Waves 3-4.
- **Waves 5-6 for cost and worry.** The Wave 3 and Wave 4 worry tables have no successors in the indexes of Waves 5
  and 6; this is read from the index and not from any statement by Ofgem. Wave 7 had not been published when searched.
- **Reasons.** Why a household switched (C5) was not read.

## Sources

- Ofgem, *Consumer Impacts of Market Conditions survey*, Waves 3-6, data tables (XLSX), Open Government Licence v3.0:
  C4 (Wave 3 Table 87; Wave 4 Table 94; Wave 5 Table 70; Wave 6 Table 56); D3_3; E4_3, E4_4, E4_6 (Wave 4 Tables
  175-177); D8_5, D8_6 (Wave 4 Tables 155-156; Wave 5 Tables 139-140); E3 for direct-debit payers (Wave 4 Table 164;
  Wave 5 Table 148; Wave 6 Table 102). URLs and hashes: `data/lake/ofgem_cim_waves4_6_2023_2025/PROVENANCE.md`.
- The sister pages named at the top.
