**Knowledge:** the-customer-needs-framework

# What households need from a supplier, and who feels each need: the needs framework tested on cost, worry and switching (2026-11-02)

The second D-graded piece of the customer-needs domain the 30 Oct corpus steer asks for
(`docs/staging/advisor/DIRECTOR_STEER_BUILD_THE_CUSTOMER_KNOWLEDGE_CORPUS_AND_PROPOSE_THE_NEXT_SIM_ADDITIONS_2026-10-30.md`,
Ask 1, steps 1-4, and the 16:51 data addendum). The first, on payment method, is
`why_households_pay_the_way_they_do_cim_wave3_2026-11-02.md`; it ended by saying one question in one wave cannot fix
the factor structure of the drawn world, and that the cross-tabs on **cost, worry and switching** were needed. This
page does that. It asks, of the needs in `docs/design/CUSTOMER_NEEDS_BEYOND_THREE_CURRENCIES.md` (the framing note,
written under canon M3 as amended 31 Oct): **which of a household's attributes (age, income, difficulty paying bills,
trust in its supplier) separates how much it feels each need, and does the answer survive to 2025?**

**Data.** Ofgem, *Consumer Impacts of Market Conditions*, Wave 3 (fieldwork 21 Nov - 11 Dec 2022; unweighted base 3,457;
BMG for Ofgem), Tables 108-110, 123-125, 129-136, 138, 140-141, 149 and 160-162, stored raw at
`data/lake/ofgem_cim_wave3_2022/`; the extract is `needs_crosstabs_by_column.csv`. Stability uses question A15 and
D3_3 in Waves 4-6 (July 2023, Jan-Feb 2024, Jan-Feb 2025); the extract and the hashes of the raw files are in
`data/lake/ofgem_cim_waves4_6_2023_2025/` (the 80 MB of raw workbooks are not stored). Every percentage is the table's
weighted column percentage. Every interval is a 95% normal interval on the table's own **effective** sample size, and a
contrast is bold only when it is larger than its own interval.

**Grades.** **D** = derived here from the table. **P** = reported by the body that holds the data. **S** = a secondary
summary. **A** = an assumption, with a range.

---

## 0. Predictions, written before any cross-tab value was read

Written 2026-11-02 after reading only the table titles, row labels and column headers of Tables 123-162, and before any
percentage in them. Source of the priors: the advisor's 30 Oct synthesis (precarity and affluence axes; life stage
over income; switching propensity anti-correlated with need) and the A15 results of the sister page. "Range" means the
highest minus the lowest band of a crossbreak.

| # | Prediction | Counts as refuted if |
|---|---|---|
| P1 | **Worry** about falling behind because energy cost rises (T160): bill difficulty is the steepest gradient (behind on bills ≥ 70% worried, no difficulties ≤ 25%); income <£16k against £80k+ differs by 25-40pp; age peaks at 35-54 but its range is under 15pp; trust in fair treatment moves it by under 5pp. | any one of the four numeric bounds is missed |
| P2 | **Switching intent** (T110, will switch supplier in 3 months): lower among those behind on bills than those with no difficulty by at least 5pp (need and propensity anti-correlated); the age range is at least 15pp, young highest; the income range is under 10pp; those who do not trust their supplier are at least 5pp higher. | any bound missed, or behind-on-bills is not lower |
| P3 | **Pay more for green** (T134, agree): rises with income (£80k+ minus <£16k at least 15pp), falls with bill difficulty (behind minus none, at most -15pp), and the age range is under the income range. | any bound missed |
| P4 | **Pay more for service** (T133, agree) is flatter than green: income range under 10pp. | income range 10pp or more |
| P5 | **Life stage against income.** Age has the larger range on switching intent (P2); bill difficulty or income has the larger range on worry (P1). | either ordering reversed |

No prediction is made about the nine or so other rows read below; they are reported as found, and said to be so.


### 0.1 How the predictions fared (written after the tables were read)

| # | Result | Verdict |
|---|---|---|
| P1 worry | Behind on bills **81.7%** worried, no difficulties **29.9%** (bound was 25%). Income under £16k against £80k+ differs by **10.1 ± 10.1**, not 25-40. Worry does not peak at 35-54: it is highest at **16-24 (69.1%)** and falls to 33.5% at 75+, a range of **36pp**. Not trusting the supplier to treat you fairly adds 7.5 ± 5.1. | **Refuted**: one of five bounds held. |
| P2 switching | Behind on bills are **14.3 ± 6.0 more** likely to say they will switch supplier, not 5pp fewer. Age range 33pp, young highest, as predicted. Income range 12pp, and it runs the other way to a precarity story (£80k+ higher). Trust: **-0.3 ± 4.1**, not +5. | **Refuted**: the anti-correlation of need with switching is not in this table. |
| P3 pay more for green | £80k+ over under-£16k: +15.3 ± 9.3 (held, barely, with an interval that reaches 6). Behind on bills against none: **-1.7 ± 6.0**, not -15. Age range 24pp, larger than the income range 15pp. | **Refuted**: two of three bounds missed. |
| P4 pay more for service | Income range **12.0pp**, not under 10 (the step is at £60k, not a gradient). | **Refuted**, narrowly. |
| P5 life stage against income | On switching intent the age range (33pp) is far larger than the income range (12pp), as predicted. On worry the bill-difficulty range (52pp) exceeds age (36pp), as predicted, but the income range (11pp) is the smallest of the three. | **Held**, and it hides a split: "precarity" read as bill difficulty works, read as income does not. |

The prior was the advisor's synthesis plus the sister page. It was wrong about the shape of worry by age, the direction
of switching against need, and the size of the income gradient; the sections below say what the tables show instead.
One caution on P1: the bill-difficulty column is the household's own report of keeping up with all its bills, and worry
about falling behind on energy bills is close to the same thing said another way. The 52pp gap is real, but it is not
two independent measurements.

---

## 1. What each need can be measured with, and what this survey cannot see (D, GAP)

The framing note splits what a household wants from a supplier into cost (N1), cash flow (N2), certainty (N3), control
(N4), time (N5), carbon (N6) and a comfort floor. CIM Wave 3 is a stated-attitude survey of bill payers. It measures
five of the seven, each by a stated answer and none by what the household then did:

| Need (M3) | CIM Wave 3 measure used here | What it is | What it is not |
|---|---|---|---|
| Cost | price noticed up (T135); DD raised (T138); "supplier charges me more than needed" (T140); "the rise is fair" (T141); expected rise (T149) | what the household noticed, was told, and believes | the bill; the cap is not a column |
| Cash flow | any affordability impact, stopped saving, cut necessities, took on debt (T136) | stated consequences of the rise | timing within the month. **GAP-3/4/5 stand**: the survey has no payday or intra-month question |
| Certainty | worry about falling behind (T160-162); worry a new supplier fails (T131); worry costs rise after switching (T132) | worry, a stated fear | willingness to pay to avoid it (**GAP-6 stands**) |
| Control | A15 "gives me more control" (sister page); DD changed by supplier (T138) | a stated reason for a payment method | control over devices |
| Time | nothing | | **GAP: no time measure in the survey.** C31 must be sourced elsewhere |
| Carbon | "prepared to pay slightly more for green energy investment" (T134) | stated willingness | carbon saved or saveable. It is the only carbon-adjacent item |
| Floor | "cut energy because we cannot afford it" (T136) | a stated cut | a measured temperature or a breach; a cut can be sensible |

A stated answer overstates what is later paid (corpus page 5, `stated_against_revealed_preference_and_defaults_2026-11-02.md`: the "3-5x" first cited here divides two populations and is corrected there to an offset of 28-36 points, and a contrast between households shrinks by a factor that differs by contrast). Every figure below
is therefore an upper bound on behaviour and a direct measure of belief.

## 2. How big each group is (D)

Weighted shares of all respondents in the column (Table 135): **age** 16-24 13.1%, 25-34 16.7%, 35-44 15.5%, 45-54 16.7%,
55-64 15.1%, 65-74 12.4%, 75+ 10.5%. **Keeping up with bills** (Table 179; the question is Ofgem's F5): no difficulties
**27.8%**, struggling (from time to time, or constantly) **56.3%**, behind on some or many bills **10.0%**. **Income**
under £16k 18.6%, £16-25k 19.3%, £25-45k 30.5%, £45-60k 12.1%, £60-80k 7.8%, £80k+ 4.1%. **Trust the supplier to treat
you fairly** 54.1%, do not 18.9% (the rest are neutral or do not know). In November 2022 "struggling" was a majority.

The £80k+ column is small (effective base 86 to 126 in the tables used), which is why income contrasts have wide
intervals throughout. That is a property of the survey, not evidence of no effect.

**Difficulty with bills falls with age more than with income** (Table 179, columns): behind on bills is **14.5%** at 16-24
and 0.6% at 75+; by income it is 16.7% under £16k and 2.6% at £80k+. Yet the share with household income under £16k is
28.5% at 16-24 and 23.0% at 75+ (Table 176, with 12.9% of the 75+ group not saying). So a 75-year-old and a 20-year-old
can sit in the same income band and be a long way apart in difficulty.

## 3. The cross-tabs (D)

Each cell is the difference in percentage points, with its 95% interval. Bold means larger than its interval.
The column to read is the sign: a plus means the first-named group says "yes" more.

| Table | Need | Measure | All | Age: 16-24 less 65-74 | Bills: behind less none | Income: under £16k less £80k+ | Trust (fair treatment): not less trust |
|---|---|---|---|---|---|---|---|
| 135 | Cost | Noticed the price of home energy has gone up | 80.5% | **-9.0 ± 6.0** | **+7.3 ± 4.9** | -1.3 ± 7.7 | +3.0 ± 3.5 |
| 138 | Cost | Supplier raised the direct debit (DD payers) | 65.3% | +0.6 ± 8.4 | **+17.2 ± 8.1** | -3.7 ± 10.4 | **+10.7 ± 5.1** |
| 140 | Cost | Agree supplier charges more DD than needed (those paying more) | 50.7% | **+25.4 ± 9.7** | **+23.3 ± 9.7** | -6.5 ± 12.1 | **+21.1 ± 5.9** |
| 141 | Cost | Agree the rise is fair (those paying more) | 34.2% | **+19.2 ± 8.1** | **-17.8 ± 6.5** | **-14.1 ± 10.7** | **-30.3 ± 4.1** |
| 149 | Cost | Expects own energy costs to go up before April 2023 | 75.3% | -5.8 ± 6.4 | **+10.9 ± 5.3** | -3.6 ± 8.2 | -0.6 ± 4.0 |
| 136 | Cash flow | Any affordability impact of the rise | 80.7% | **+15.6 ± 5.6** | **+36.8 ± 4.0** | +7.7 ± 8.1 | **+9.3 ± 3.3** |
| 136 | Cash flow | Stopped or cut regular saving | 28.8% | -5.8 ± 6.1 | **+18.7 ± 6.0** | -2.5 ± 8.7 | **+7.4 ± 4.4** |
| 136 | Cash flow | Cut spending on necessities | 30.7% | **+7.8 ± 6.4** | **+37.8 ± 6.2** | **+13.3 ± 8.4** | **+9.8 ± 4.5** |
| 136 | Cash flow | Took on more household debt | 10.3% | **+14.3 ± 4.7** | **+25.9 ± 5.4** | +1.6 ± 5.6 | **+4.0 ± 3.1** |
| 136 | Floor | Cut energy use because cannot afford it | 42.8% | **-14.3 ± 6.7** | **+33.1 ± 6.3** | **+14.0 ± 9.2** | **+13.8 ± 4.7** |
| 160 | Worry | Worried about falling behind because energy cost rises | 55.2% | **+29.9 ± 7.4** | **+51.8 ± 6.6** | **+10.1 ± 10.1** | **+7.5 ± 5.1** |
| 161 | Worry | Worried about falling behind because general costs rise | 56.4% | **+23.9 ± 7.6** | **+50.7 ± 6.7** | **+13.2 ± 10.1** | **+9.8 ± 5.1** |
| 162 | Worry | Worried about falling behind when the EPG ends | 59.8% | **+26.6 ± 8.9** | **+55.3 ± 6.1** | **+19.0 ± 11.7** | +4.9 ± 5.7 |
| 110 | Switching | Will switch to a new supplier in 3 months | 25.0% | **+31.6 ± 6.4** | **+14.3 ± 6.0** | **-10.4 ± 9.1** | -0.3 ± 4.1 |
| 109 | Switching | Will switch tariff with current supplier in 3 months | 27.7% | **+24.6 ± 6.5** | **+6.0 ± 5.9** | **-17.7 ± 9.4** | **-4.8 ± 4.2** |
| 108 | Switching | Will compare tariffs in 3 months | 51.5% | **+22.0 ± 6.9** | **+11.3 ± 6.6** | **-15.4 ± 9.5** | -2.7 ± 4.7 |
| 123 | Switching | Would switch to a variable tariff to save money | 26.3% | **+28.3 ± 6.5** | **+6.5 ± 6.0** | -8.4 ± 8.9 | **-12.0 ± 3.9** |
| 124 | Switching | Would switch to a 1-year fix to save money | 41.7% | **+14.1 ± 7.1** | **-6.5 ± 6.5** | **-16.5 ± 9.6** | **-5.2 ± 4.7** |
| 125 | Switching | Would switch to a 2-year fix to save money | 41.2% | **+7.4 ± 7.0** | -3.4 ± 6.5 | -9.2 ± 9.6 | **-7.1 ± 4.6** |
| 129 | Switching | Would only consider a large or well-known supplier | 51.3% | **-15.1 ± 7.1** | **-7.4 ± 6.6** | -7.0 ± 9.6 | **-11.5 ± 4.7** |
| 131 | Switching | Worried a new supplier would go out of business | 59.3% | **-10.2 ± 7.1** | -5.5 ± 6.5 | -4.0 ± 9.5 | **-17.8 ± 4.6** |
| 132 | Switching | Worried costs would go up once switched | 63.3% | -5.6 ± 7.0 | +6.0 ± 6.4 | -3.9 ± 9.1 | **-6.6 ± 4.5** |
| 133 | Willingness to pay | Happy to pay slightly more for better customer service | 25.1% | **+26.7 ± 6.5** | +3.2 ± 5.8 | **-11.9 ± 9.0** | **-10.1 ± 3.9** |
| 134 | Willingness to pay | Prepared to pay slightly more for green energy investment | 28.5% | **+21.3 ± 6.7** | -1.7 ± 6.0 | **-15.3 ± 9.3** | **-15.9 ± 4.0** |

The same data as ranges across all bands of a crossbreak (highest band minus lowest, in points). A range is inflated
by the noisiest small band, so read it against the contrasts above, not instead of them.

| Table | Measure | Age (7 bands) | Bill difficulty (3) | Income (6 bands) |
|---|---|---|---|---|
| 135 | Noticed the price of home energy has gone up | 11 | 7 | 4 |
| 138 | Supplier raised the direct debit (DD payers) | 16 | 17 | 8 |
| 140 | Agree supplier charges more DD than needed (those paying more) | 32 | 23 | 9 |
| 141 | Agree the rise is fair (those paying more) | 28 | 18 | 15 |
| 149 | Expects own energy costs to go up before April 2023 | 8 | 11 | 6 |
| 136 | Any affordability impact of the rise | 22 | 37 | 8 |
| 136 | Stopped or cut regular saving | 13 | 21 | 6 |
| 136 | Cut spending on necessities | 22 | 38 | 13 |
| 136 | Took on more household debt | 15 | 26 | 4 |
| 136 | Cut energy use because cannot afford it | 26 | 33 | 14 |
| 160 | Worried about falling behind because energy cost rises | 36 | 52 | 11 |
| 161 | Worried about falling behind because general costs rise | 37 | 51 | 13 |
| 162 | Worried about falling behind when the EPG ends | 32 | 55 | 19 |
| 110 | Will switch to a new supplier in 3 months | 33 | 14 | 12 |
| 109 | Will switch tariff with current supplier in 3 months | 28 | 6 | 18 |
| 108 | Will compare tariffs in 3 months | 31 | 11 | 17 |
| 123 | Would switch to a variable tariff to save money | 29 | 7 | 8 |
| 124 | Would switch to a 1-year fix to save money | 18 | 7 | 17 |
| 125 | Would switch to a 2-year fix to save money | 19 | 4 | 10 |
| 129 | Would only consider a large or well-known supplier | 17 | 7 | 9 |
| 131 | Worried a new supplier would go out of business | 19 | 5 | 6 |
| 132 | Worried costs would go up once switched | 8 | 7 | 7 |
| 133 | Happy to pay slightly more for better customer service | 27 | 3 | 12 |
| 134 | Prepared to pay slightly more for green energy investment | 24 | 2 | 15 |

## 4. What the tables say, need by need (D)

**Cost: noticed everywhere, judged fair by trust.** 80.5% say the price has gone up, and 75.3% expect it to rise
further before April 2023. Income moves neither; age moves "noticed" by 9 points (the older notice more). What moves most is the judgement. Among those paying more,
only **34.2%** agree the rise is fair, and the gap between those who do not trust their supplier to treat them fairly
and those who do is **-30.3 ± 4.1** points. Trust is the largest single separator of that judgement, larger than any
demographic. Belief that the supplier charges more direct debit than it needs to is higher among the young (+25.4 ±
9.7) and the behind-on-bills (+23.3 ± 9.7) and the distrusting (+21.1 ± 5.9). Of those paying by direct debit, 65.3%
say the supplier raised the amount, **76.1% of those behind on bills against 58.9% of those with no difficulties**:
the supplier's own action fell hardest on the households least able to take it.

**Cash flow: this is bill difficulty and almost nothing else.** Cut spending on necessities: +37.8 ± 6.2 for behind on
bills, +13.3 ± 8.4 for the lowest income band, +7.8 ± 6.4 for the youngest. Stopped saving: +18.7 ± 6.0 by difficulty,
nothing measurable by age or income. More household debt: +25.9 ± 5.4 by difficulty and +14.3 ± 4.7 for the young.
Income alone does not show a cash-flow gradient except on cutting necessities.

**Certainty (worry): bill difficulty first, then life stage, and income last.** Worry about falling behind because
energy costs rise: 55.2% overall; 81.7% behind on bills, 66.3% struggling, 29.9% with no difficulties; 69.1% at 16-24
down to 33.5% at 75+. The income gradient is 60.9% under £16k to 50.8% at £80k+, a gap of 10 that its interval does
not exclude from zero. The same holds for worry about the end of the EPG (59.8% overall): difficulty +55.3 ± 6.1, age
+26.6 ± 8.9, income +19.0 ± 11.7. Prepayment customers are worried more than any other group: **75.5%** worry about
being unable to top up because energy costs rise (Table 158), **76.3%** because general costs rise (Table 159).

**Floor: the older cut energy more, the younger worry more.** 42.8% say they cut energy use because they cannot afford
it. By difficulty +33.1 ± 6.3, by income +14.0 ± 9.2, and by age **-14.3 ± 6.7**: the over-65s cut *more* than the young
despite worrying much less. A cut is the stated action that the comfort floor must guard against, and it is made by the
group the worry measure misses. This is the one place the survey tells a supplier that worry is a poor proxy for harm.

**Switching: life stage, and capability, not need.** 25.0% say they will switch supplier in the next three months and
51.5% that they will compare tariffs. By age the gap is **+31.6 ± 6.4** (41.6% at 16-24, 9.0% at 75+). By difficulty,
those behind on bills say yes **more** (+14.3 ± 6.0). By income, the better off say yes more: -10.4 ± 9.1 for the
poorest on switching supplier, -17.7 ± 9.4 on a new tariff with the current supplier, -15.4 ± 9.5 on comparing. The
advisor's synthesis that shopping propensity is "need × capability × trust × hassle, anti-correlated with need" is
**not supported on stated intent**: the households most in need say they are more willing to move, and the ones with
the least capability (the oldest) say they are least. What need does change is *what* they would move to: against the
no-difficulty group, those behind on bills are less drawn to a one-year fix (**-6.5 ± 6.5**, interval touching zero) and
more to a variable tariff (+6.5 ± 6.0, also touching zero); neither is a result on its own.

**Trust moves attitudes, not stated switching.** Not trusting the supplier to treat you fairly: **-12.0 ± 3.9** on
switching to a variable tariff, -17.8 ± 4.6 on worry that a new supplier would fail, -11.5 ± 4.7 on "only a large
supplier" and **-0.3 ± 4.1** on will switch. The worry and the intention separate.

**Willingness to pay: age and trust, not difficulty.** 25.1% would be happy to pay slightly more for better customer
service and 28.5% would pay slightly more for green energy investment. By age +26.7 ± 6.5 and +21.3 ± 6.7 (the young
agree more), by trust **-10.1 ± 3.9** and **-15.9 ± 4.0**, by difficulty **+3.2 ± 5.8** and **-1.7 ± 6.0** (nothing).
By income the green gap is -15.3 ± 9.3 and the service gap -11.9 ± 9.0, both reaching little above their intervals. A
household behind on its bills is as willing to say it would pay more as one with no difficulty. A stated willingness to
pay "slightly more" that does not fall with inability to pay is a statement of attitude, not of capacity, and it should
not be read as a price a poor household can bear.

## 5. Do these hold in 2023, 2024 and 2025? (D)

Question A15 (why this payment method) and D3_3 (will switch supplier) are asked in Waves 3-6. Contrasts below are
within each wave. **Levels cannot be compared across Waves 3 and 4**: Wave 4 added six answer options, so every Wave 3
share is spread across a longer list (Ofgem's "negative reasons" net is 22.8% in Wave 3 and 11.5% in Wave 4 for that
reason, not necessarily because anything changed). The bill-difficulty column is also redefined: "struggling" splits in
two from Wave 4, and Wave 6 reads *non-energy* household bills. Only "no difficulties" and "behind on bills", which keep
their words, are used.

| A15 / D3_3 row | Contrast | Wave 3 (Nov-Dec 2022) | Wave 4 (Jul 2023) | Wave 5 (Jan-Feb 2024) | Wave 6 (Jan-Feb 2025) |
|---|---|---|---|---|---|
| A15 "gives me more control" | age (16-24 minus 65-74) | **-10.1 ± 6.1** | +1.0 ± 6.2 | **-8.5 ± 6.8** | **-5.6 ± 5.0** |
| A15 "gives me more control" | bills (behind minus none) | **-7.2 ± 5.7** | +2.4 ± 5.4 | -1.6 ± 5.8 | -0.8 ± 4.9 |
| A15 "gives me more control" | income (<16k minus 80k+) | -1.9 ± 8.8 | +0.9 ± 8.0 | -4.6 ± 8.2 | +2.4 ± 5.8 |
| A15 "gives me more control" | trust (not minus trust) | **-5.7 ± 4.2** | **-8.8 ± 3.9** | -2.2 ± 4.4 | -2.6 ± 3.8 |
| A15 Ofgem's negative reasons | age (16-24 minus 65-74) | **+21.7 ± 6.3** | **+13.3 ± 5.1** | **+13.4 ± 6.1** | **+7.6 ± 4.0** |
| A15 Ofgem's negative reasons | bills (behind minus none) | **+19.4 ± 6.1** | **+9.9 ± 4.4** | **+16.6 ± 5.3** | **+4.0 ± 3.8** |
| A15 Ofgem's negative reasons | income (<16k minus 80k+) | +2.6 ± 8.0 | -1.2 ± 6.3 | +1.2 ± 5.6 | -2.4 ± 4.6 |
| A15 Ofgem's negative reasons | trust (not minus trust) | **+8.7 ± 4.2** | **+6.1 ± 3.3** | **+4.7 ± 3.4** | +2.0 ± 3.0 |
| A15 "more convenient" | age (16-24 minus 65-74) | **-29.8 ± 6.7** | **-23.5 ± 6.6** | **-16.4 ± 7.5** | **-16.7 ± 6.1** |
| A15 "more convenient" | bills (behind minus none) | **-24.3 ± 6.2** | **-22.7 ± 5.2** | **-13.5 ± 6.3** | **-14.3 ± 5.2** |
| A15 "more convenient" | income (<16k minus 80k+) | -6.1 ± 9.6 | **-10.2 ± 9.1** | -4.6 ± 8.7 | **-7.9 ± 6.9** |
| A15 "more convenient" | trust (not minus trust) | **-7.9 ± 4.7** | **-7.1 ± 4.5** | **-6.5 ± 4.7** | **-6.4 ± 4.3** |
| A15 "my supplier made me" | age (16-24 minus 65-74) | **+5.4 ± 4.1** | **+4.2 ± 3.7** | +3.4 ± 4.2 | +2.0 ± 3.0 |
| A15 "my supplier made me" | bills (behind minus none) | **+9.6 ± 4.4** | **+6.0 ± 3.5** | **+7.6 ± 3.9** | +1.7 ± 2.9 |
| A15 "my supplier made me" | income (<16k minus 80k+) | **+4.7 ± 4.3** | -0.8 ± 5.2 | +3.1 ± 3.6 | -1.0 ± 3.4 |
| A15 "my supplier made me" | trust (not minus trust) | **+4.3 ± 2.8** | **+4.1 ± 2.6** | **+4.8 ± 2.8** | +0.9 ± 2.3 |
| D3_3 will switch supplier in 3 months | age (16-24 minus 65-74) | **+31.6 ± 6.4** | **+31.8 ± 6.6** | **+18.9 ± 7.1** | **+26.8 ± 5.8** |
| D3_3 will switch supplier in 3 months | bills (behind minus none) | **+14.3 ± 6.0** | **+7.6 ± 5.5** | **+9.8 ± 5.8** | **+8.3 ± 5.8** |
| D3_3 will switch supplier in 3 months | income (<16k minus 80k+) | **-10.4 ± 9.1** | **-10.7 ± 8.9** | -5.4 ± 7.8 | **-10.6 ± 7.0** |
| D3_3 will switch supplier in 3 months | trust (not minus trust) | -0.3 ± 4.1 | **+10.7 ± 4.4** | **+8.7 ± 4.4** | +2.4 ± 4.5 |

What survives, by the reading rule that a contrast must keep its sign and exceed its interval in at least three of four
waves:

- **Survives.** Younger people give passive ("negative") payment reasons and less convenience (all four waves; the
  negative gap shrinks from +21.7 to +7.6). Those behind on bills give more passive reasons (four of four on sign and size,
  Wave 6 only just; +19.4, +9.9, +16.6, +4.0) and less convenience. Younger people say they will switch supplier
  (four of four, +18.9 to +31.8). Those behind on bills say they will switch **more** (four of four on sign and on size, +7.6 to +14.3). Better-off households say they will switch more (four of
  four on sign, three of four on size). Income does not move stated control or passive reasons in any wave.
- **Does not survive.** The sister page's correction "stated control is **lower** for those behind on bills (-7.3 ± 5.7)" was
  a Wave 3 result. Waves 4-6 give +2.4 ± 5.4, -1.6 ± 5.8 and -0.8 ± 4.9. The accurate form is "stated control is **not
  higher** when behind on bills, in any of four waves". The correction of "precarity drives spend control" stands, with the
  weaker wording. Trust and switching intent flips sign by wave (-0.3, +10.7, +8.7, +2.4), so it is not a stable
  moderator of intent; the sister page's trust result on passive reasons (+8.7 in Wave 3) falls to +2.0 by Wave 6.
- **Not testable.** Cost, worry and willingness to pay are asked in different forms across waves, and several were
  Wave 3's crisis-winter questions. They were Wave 3 only here. *Corrected 2026-11-02 (later same day):* `revealed_switching_by_age_and_arrears_and_the_needs_tables_in_cim_waves_4_6_2026-11-02.md` reads them: worry is asked again in Wave 4 only and every contrast keeps its sign (income gradient rises to +24.8 ± 9.5); affordability by arrears and age is stable; willingness to pay by age and trust is stable and arrears never separates it; the older-cut-more floor result does not survive past Wave 4.

## 6. The framing note's figures, re-graded (D / P / S / A)

| Figure in the framing note | Where it comes from | Grade now | Verdict |
|---|---|---|---|
| Payment-method reasons by DD / SC / PPM (section 2.1) | CIM Wave 3 Table 13 | **D** (sister page) | Confirmed within a point; PPM base 553 corrected to 530 |
| "54-62% worried about falling behind, depending on group and wave" (2.3) | CIM Wave 3 report text, "mapping not clean" | **D** | **Corrected**: 55.2% of DD and SC payers (Table 160); **75.5-76.3% of prepayment customers** worry about not being able to top up (Tables 158-159). The range hid the prepayment figure |
| Wave 3 PPM: 19% unable to top up, 12% disconnected over 3 hours, 24% used emergency credit, 19% cut the top-up (2.4) | CIM Wave 3 report text | **D** | Confirmed: 19.0%, 12.5%, 24.0%, 19.4% (Table 142, base 530, effective 463). Also 39.5% cut energy use, 77.3% any recent affordability issue |
| About 6% of PPM households recently moved on "to help manage what I spend" (2.5) | CIM Wave 3 report text | **D** | Confirmed: 6.5%; a further 6.1% say the supplier made them (Table 142). That is the Wave 3 split of chosen against imposed among recent movers |
| 18% of recent switchers wanted a fixed tariff (2.3) | CIM Wave 3 report text | **D** | Confirmed: 17.8% (Table 89, base 726). Also 26.0% a cheaper tariff, 13.9% price-cap protection, 10.1% worried the previous supplier would fail |
| 24% of UK adults low financial resilience (FCA Financial Lives 2024); 14% low savings; 13% heavily burdened; 8% in difficulty (2.2) | FCA publication | **P**, not re-derived | Reported by the body that holds the data. The FLS data tables were not read here (**GAP**: derive the income-band cut) |
| Under £15k income: 22% no savings, over a third under £1,000 (2.2) | the repo's `household_budget_w2_4.md`, marked [L] | **S** | Second-hand; no grade higher until the FLS tables are read |
| Gross domestic credit balances £7.1bn (Q1 2023), £8.1bn (end 2023); £180-400 net per fixed-DD household (2.2) | Ofgem credit-balance data, via `payments_and_direct_debit_2026-10-25.md` | **P** | Reported by the regulator |
| 3.2 million people ran out of credit; 19% of those cut off for 24 hours or more (2.4) | Citizens Advice, from a Yonder poll of 4,384 adults; "households x 2.4" grossing-up | **P** for the poll, **A** for the 3.2m | The headcount is a grossed-up estimate by its publisher's own footnote; use the poll proportions, not the count |
| 150,000 PPM accounts reviewed; 1,925 not safe and reasonably practicable (2.5) | Ofgem market compliance review | **P** | |
| 600,000 forced onto PPM in 2022 (Citizens Advice) against Ofgem's 150,000 (2.5) | Citizens Advice, "based on Ofgem figures" | **S** | Different population and definition; **GAP-8** stands |
| 667,960 smart-PPM self-disconnections in Q2 2022; peak 946,400 in Q3 2023 (2.4) | Ofgem indicators | **P** | |
| 41% "worry that if I switch things will go wrong" (CES 2017) (2.3) | read via C31 s.2.1 | **S** | Third-hand. Against it, CIM Wave 3 now gives **59.3%** worried a new supplier would go out of business and **63.3%** worried costs would rise after switching (Tables 131-132) |
| Fix priced above default in the crisis (£2,096 against £1,277, Oct 2021; £4,599 against £1,971, Sep 2022) (2.3) | Ofgem average fixed-tariff series | **P** | |
| Willingness to pay for price certainty (GAP-6); uncertainty aversion of low-buffer households (GAP-7) | not published | **A** (belief, with a range to be estimated) | Unchanged. Nothing in CIM prices certainty |

## 7. What this means for the parsimony ruling (the factor structure)

The director's 30 Oct ruling: draw a few latent factors from the attributes that strongly predict the rest, and leave
the remainder independent. The candidates were precarity, affluence and life stage. The Wave 3 and Wave 4-6 tables say:

1. **Life stage is the strongest separator on the most outcomes.** It leads on switching intent, willingness to pay,
   payment-method reasons and, by contrast size, is second only to bill difficulty on worry. It is already an observable
   in the world (age), so it needs no new latent. The advisor's "life stage outweighs income" **holds as a statement
   about marginal contrasts** and **fails as evidence of cause**: these are one-way tables, age and income are
   entangled (section 2), and Ofgem does not publish an age-by-income-by-difficulty table. That test needs data this
   project is not allowed to hold (W11).
2. **"Precarity" splits.** Read as difficulty paying bills, it is the strongest separator of cost judgement, cash flow,
   worry and the floor, and it **does not follow income**. Read as income band it is weaker: across all 24 measures income exceeds its interval on 12, bill difficulty on 19,
   age on 20 and trust on 19; and on the 13 cost, cash-flow, floor and worry measures bill difficulty is larger than
   income on every one and larger than age on 11 (age is slightly larger on the two cost-judgement items). If the world draws a precarity factor, its observable signal is arrears and bill
   difficulty, with age; income band is the weakest of its candidate signals in this survey. **A financial-stress state
   already exists in the world and drives nothing yet** (concept `vuln.ability_to_pay`: "financial vulnerability (V2) is
   drawn and drives nothing yet; arrears run off income_stress"). This page is evidence for wiring it before inventing
   another factor.
3. **Affluence is real but narrow, and the survey cannot size it.** The income gradients that exceed their interval are
   on capability and pocket: the better-off say they will compare a tariff (+15.4), switch tariff (+17.7) or take a
   one-year fix (+16.5) more, say they would pay a little more for green (+15.3) or service (+11.9), judge the rise less
   fair, worry less about the end of the EPG (-19.0), and cut necessities and energy less (about 13-14). There is no income gradient on
   noticing the rise, saving, debt or the direct-debit rise. The £80k+ column is 4.1% of the sample, so each of these
   may be larger or smaller than shown. It is evidence for income as a capability and willingness variable, not for a
   separate "affluence" factor beyond income itself.
4. **Trust is a separate attitude axis, not a precarity or life-stage proxy.** It dominates the fairness judgement and
   the stated willingness to pay, and it does not move stated switching intent. It supports the advisor's "moderators"
   claim for attitude outcomes and **contradicts it for switching**.
5. **Switching propensity is not anti-correlated with need** on stated intent. Two traits are still plausible
   (consumption response and shopping propensity), but "anti-correlated with need" should not be drawn without a
   revealed-behaviour source, because the stated direction is the opposite.

None of this changes a world value. It informs the ordering of the roadmap and what the world should be graded against.

## 8. What this page does not establish

- **Cause.** One-way column percentages. No cell is controlled for another; age and income cannot be separated here.
- **Behaviour.** Every row is a stated answer from 21 Nov - 11 Dec 2022, in the crisis winter, seven weeks after the
  Energy Price Guarantee began. Stated intent to switch is not switching; stated willingness to pay is not paying.
- **Time and carbon.** The survey has no time item and one stated carbon-adjacent item. Both stay GAPs.
- **Waves 4-6 for cost, worry and willingness to pay.** Only A15 and D3_3 were read for stability here; the rest is in `revealed_switching_by_age_and_arrears_and_the_needs_tables_in_cim_waves_4_6_2026-11-02.md`, which also adds the revealed switching by age and arrears (behind-on-bills households switched supplier more, +3 to +5 points, not fewer).
- **Wave 7.** Not published on Ofgem's research pages when searched on 2 Nov 2026.
- **The small bands.** Income £80k+ (effective base 86-126) and 16-24 in several tables (unweighted 132-269 across the tables used) carry wide
  intervals; a bold-free cell is "cannot tell", not "no effect".

## 9. Who reads this

- **World:** the roadmap's hidden-needs vector (precarity, affluence, life stage). Section 7 says which of those the
  tables support. Nothing in the world reads this page today and no world value is changed.
- **Supplier:** the observable signals. Bill difficulty is observable to a supplier as arrears and contact; age is not
  held for a household unless the customer gives it; trust is surveyable. Section 4's worry-against-cutting-use split is
  the reason a supplier must not read worry as harm.
- **Next pages in the domain:** trust and capability; price sensitivity split in two; age, life stage and events; stated
  against revealed preference. This page's switching result is the reason to source revealed switching by group before
  the second of those.

## Sources

- Ofgem, *Consumer Impacts of Market Conditions survey: Wave 3 (Nov/Dec 2022)*, data tables (XLSX) and report; Waves 4,
  5 and 6 data tables; Open Government Licence v3.0. Retrieval and hashes: the two `PROVENANCE.md` files under `data/lake/`.
- The framing note and the sister page named at the top; the third-party figures in section 6 as graded there.
