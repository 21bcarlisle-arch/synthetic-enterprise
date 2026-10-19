**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `the-worlds-2022-non-payment-against-the-published-arrears-record`
**Knowledge:** debt-and-collections -- `docs/market_research/gb_domestic_bill_payment_failure_and_arrears_prevalence.md` §(d), `docs/market_research/debt_and_collections.md` §2.1 (Ofgem Q4 series 2016-2025), `docs/market_research/ofgem_cap_windows.md` (the 2021-23 bills)

# The world's payment draw has no price input, so 2022 cannot raise non-payment, and the budget built for that is not wired in

*Diagnosis only. Nothing in the world changes before the 2026-10-19 publish. The fix below is
filed for a build after it, with its effect predicted before that build. A fidelity decision,
taken blind to company results.*

**The layer that falls short is the world's per-bill payment draw.** That is
`simulation/arrears_engine.payment_outcome`, reached through
`simulation/payment_behaviour_source.generate_payment_event` from
`background/live_payment_triad.py`. Its failure probability is a function of income-stress tier
alone. The bill's size, the price and the household's budget are not inputs to it. **The
yearly table below shows that the larger defect is in the same layer:** each bill is an
independent coin, so a world debtor misses about one bill and resumes. World pounds per account
behind are 9-14× below Ofgem's in every year. The one
mechanism written so that "a crisis-era bad-debt step-up can EMERGE from income-minus-essentials
arithmetic" is `simulation/household_budget.py` (W2_4). No payment path reads it.

## What each published series counts (say this before any figure)

| Series | Experience it counts | Unit | Clock |
|---|---|---|---|
| Ofgem "in arrears" | a bill unpaid for more than 91 days, with **no** repayment arrangement; later consumption excluded | accounts per fuel (heads) | stock at quarter end |
| Ofgem "in debt" | the same unpaid bill, now on an arrangement lasting more than 91 days | accounts per fuel | stock at quarter end |
| Ofgem average arrears / debt | the **pound balance** per account in each of the two buckets | GBP per account | stock at quarter end |
| FCA Financial Lives, "behind on electricity" | adults who say they have fallen behind (2.2% in 2020, 3.0% in 2022, 3.4% in 2024) | people, by survey | point in time |

**The definition used here** is Ofgem's: electricity, at Q4 quarter ends, accounts holding a bill
due at least 91 days earlier and still unpaid. The world has no repayment arrangements (the plan
toggles are off), so every world debtor sits in the no-arrangement bucket. The like-for-like heads
comparator is therefore **arrears + debt**, as `tools/grade_world_debt_against_ofgem.py` already
argues. The pound comparator is printed both ways: the no-plan average, and the blended average
over arrears + debt. The FCA series counts people, not accounts, so it is not used in the table.

## The mechanism, at real 2022 inputs (`/var/tmp/nonpay2022/probe_2022.py`)

Typical dual-fuel bill per year, from `ofgem_cap_windows.md`. The draw was run for 4,000
households × 12 months at each bill:

| Bill | Annual GBP | LOW fail share | MODERATE | HIGH |
|---|---|---|---|---|
| Oct 2021 cap | 1,277 | 0.0090 | 0.0351 | 0.1017 |
| Apr 2022 cap | 1,971 | 0.0090 | 0.0351 | 0.1017 |
| Oct 2022 EPG | 2,500 | 0.0090 | 0.0351 | 0.1017 |
| Oct 2022 cap, without the EPG | 3,549 | 0.0090 | 0.0351 | 0.1017 |

The four rows are identical, not merely close. The amount is carried onto the event and never
read by the draw. Tier table: LOW 0.0087, MODERATE 0.0348, HIGH 0.1015.

Stress comes from `simulation/life_events.py`: job loss, illness, a new baby, retirement and
divorce. It is read once per term at the term's end (`run_phase2b.py`, "Phase MW"). No life event
is keyed to price or year. **Nothing in 2022 can move a household's tier.**

The two other doors that could carry price are both shut:
- **DD4b**, `simulation/dd_shock_response.py`, raises failure while a materially raised direct
  debit is in force. Its strength, `dd4b_failure_uplift_after_shock`, ships at 0 (range 0.25-3.0).
  It reaches direct-debit payers only, and only those whose annual review raises the amount.
- **The hidden budget**, `simulation/household_budget.py`. Drawn over 20,000 ids, with the bill
  rise over Oct 2021 taken out of the monthly margin:

| Bill | Rise per month | Margin below zero | Margin below zero, savings under GBP 1k |
|---|---|---|---|
| Oct 2021 cap | 0 | 7.3% | 2.5% |
| Apr 2022 cap | 57.8 | 8.3% | 2.8% |
| Oct 2022 EPG | 101.9 | 9.0% | 3.0% |
| Oct 2022 cap, without the EPG | 189.3 | 10.8% | 3.6% |

So the budget responds to 2022: under the EPG, 1.7 points more households cross zero. The payment
draw cannot see it.

## The world beside the published series, by year

**Instrument.** `tools.grade_world_debt_against_ofgem capture` to 2024-12-31, default dice, at
c5963a5c0 (5,500 s). It is wrapped to keep each bill's amount and stress, and changes no draw
(`/var/tmp/nonpay2022/capture_with_amounts.py`; reader `read_years.py`, `serial.py`). It reads
the world's own payment truth, not the company's ledger. One seed, about 250 electricity accounts
a year, so one account moves the share by about 0.4 points.

**Definition.** Electricity at Q4: accounts billed in December holding a bill due at least
91 days before 31 December and still unpaid. "GBP aged" is the sum of those bills. Ofgem's
denominator is derived: 694,191 = 2.45% at Q4 2019 and 1,064,138 = 3.6% at Q1 2025, linear
between them.

| Q4 | World billed | Behind | World share (95% CI, account-clustered) | World GBP per account behind, aged | Stress moderate+high | Ofgem arrears | Ofgem arrears + debt | Ofgem GBP per account, arrears | Ofgem GBP per account, arrears + debt |
|---|---|---|---|---|---|---|---|---|---|
| 2016 | 419 | 6 | 1.4% (0.5-2.6) | 47 | 8% | 1.84% | 4.31% | 570 | 488 |
| 2017 | 361 | 17 | 4.7% (2.8-6.9) | 43 | 10% | 2.16% | 4.51% | 555 | 496 |
| 2018 | 322 | 11 | 3.4% (1.6-5.6) | 46 | 12% | 2.31% | 4.66% | 589 | 522 |
| 2019 | 276 | 19 | 6.9% (4.0-10.1) | 45 | 13% | 2.45% | 5.06% | 654 | 553 |
| 2020 | 252 | 19 | 7.5% (4.4-11.1) | 60 | 14% | 2.46% | 5.00% | 774 | 630 |
| 2021 | 243 | 17 | 7.0% (4.1-10.3) | 58 | 15% | 2.69% | 6.09% | 905 | 637 |
| **2022** | 256 | 25 | **9.8% (6.2-13.7)** | **71** | 16% | 2.68% | 5.70% | **1,028** | 764 |
| 2023 | 266 | 26 | 9.8% (6.4-13.5) | 102 | 18% | 3.44% | 6.01% | 1,303 | 1,035 |
| 2024 | 275 | 22 | 8.0% (4.7-11.3) | 114 | 20% | 3.54% | 6.29% | 1,617 | 1,223 |

The quarters around the crisis, world share then GBP per account aged. Ofgem's arrears count
rose sharply to 894,732 in Q2 2022, dipped to 663,189 in Q1 2023 under the EBSS and EPG, then
reached 1,019,640 in Q3 2023.

| Quarter | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| 2021 | 8.9%, £61 | 8.0%, £60 | 7.6%, £56 | 7.0%, £58 |
| 2022 | 6.0%, £71 | **6.1%, £66** | 7.6%, £67 | 9.8%, £71 |
| 2023 | 9.3%, £69 | 8.6%, £90 | 8.9%, £97 | 9.8%, £102 |

How world debt is shaped, pooled over Q4 2017-2024 and all spells:
- Aged unpaid bills per account behind: 1 bill 121 times, 2 bills 24, 3 bills 10, 5 bills 1.
  **78% of world debtors are behind by exactly one bill.**
- P(an unpaid spell starts in a month) = 0.0124. P(the next month is unpaid too, given this
  month is) = 0.0217. **Non-payment is close to independent from month to month.**
- 370 of 444 unpaid spells settle (83%), median 119 days. 74 are never paid.
- The mean electricity monthly bill in the world is £49 in 2019 and £96 in 2022. Ofgem's average
  arrears, £654 (2019) and £1,028 (2022), is about **11-13 months of that bill**. The world's is
  about one month.

### The predictions, beside what happened

*Written at 18:19Z (`/var/tmp/nonpay2022/PREREG.md`), before the capture existed, and committed in
91ad4cad8 before the table.*

- **P1, heads: REFUTED.** Predicted: Q4 2022 within ±1.5 points of Q4 2021. Measured: 7.0% →
  9.8% (+2.8 points). That is 17 → 25 accounts, and the two intervals overlap almost entirely.
  Probe 1 shows the draw cannot respond to price, so the rise is noise plus the stress drift below.
  It is not a crisis response. The world's quarterly shape is the opposite of the record: it
  *falls* to 6.1% in Q2 2022, the quarter in which Ofgem's count jumped.
- **P2, pounds: REFUTED.** Predicted: at least ×1.3. Measured: £58 → £71, ×1.22. The 91-day age
  means the Q4 2022 stock is bills due by 1 October, which are the summer bills of the April cap.
  The EPG winter bills reach the aged stock only in 2023.
- **P3, level: REFUTED in one year.** Predicted: above arrears + debt in every year 2017-2024.
  2018 is 3.4% against 4.66%. Every other year is above, but **2019's interval (4.0-10.1%) now
  contains Ofgem's 5.06%**. The "about 2× high" of the 2026-10-08 finding was measured on earlier
  code. On heads, the world is at most about 1.5× high and statistically indistinguishable in most
  years.
- **P4, persistence: REFUTED.** Predicted: Q4 2023 below 1.2× Q4 2022. Measured: £71 → £102,
  ×1.44, against Ofgem's ×1.27. World pounds per account do climb through 2023-24, but from a base
  a tenth of the record's, and because the bills are bigger, not because debt accumulates. One
  bill is still one bill.

**Stress drifts upwards for a decade:** moderate + high rises from 8% to 20% of the billed
accounts, steadily, crisis or not. Life events push households into HIGH faster than
`_INCOME_RECOVERY_ANNUAL_PROB` lets them out. FCA's share of adults with a negative life event is
flat, at 19-22% (2017-2024). Recorded here, not ranked. It is the likeliest cause of the world's
slow rise in heads.

## What the table says the layer is

The draw has no price input, and the probe proves that. **But the table says the bigger gap is
the shape of non-payment, and the price channel comes second.** On heads, the world is in the
record's range. On pounds per account behind, it is **9-14× low in every year**, crisis or not,
because each world debtor misses one bill and resumes paying. Real arrears are a household that
*stops paying* for many months. The 2022 crisis in Ofgem's series is that intensity growing
("intensity, not incidence"). A world whose non-payment is an independent coin per bill cannot
produce it at any price, so wiring price into that coin will not help.

## The fix, for a build after the publish, and its predicted effect

**Smallest mechanism.** Feed the budget into the tier. Each billed month, a credit-meter household
whose margin falls below zero because of the energy bill's rise over its own pre-shock bill, and
which holds under GBP 1k of savings, is read one tier up (LOW → MODERATE, MODERATE → HIGH) while
that holds. This adds no new probability: it reuses the tier relativities `_DD_TIER_RATIO_TO_LOW`
already holds. The crossing is defined against the household's own pre-shock bill, so households
whose margin is negative before any shock do not move. That leaves the 2016-2021 level untouched,
and the level is a separate, already-filed question (W2_38; the 2026-10-08 finding).

Knowledge page first (K8). The budget's ladder and housing draw are R10 shapes, and the
"savings under GBP 1k" cut is a design choice, not a published figure. The page must say so
before the build.

**Predicted effect on the crisis share (electricity, Q4 2022, the definition above).** Without the
savings condition, 1.7 points of households cross under the EPG. With it, 0.5 points do.
Stock share by tier is taken as proportional to the monthly fail ratio (1 : 4 : 11.7), on a world
share of about 8%, which puts LOW at about 4% and MODERATE at about 17%. That predicts **+0.1 to
+0.2 points** on the Q4 2022 share, and no more than +0.5 points with the uplift on every
crossing household. That is about a 2-6% relative rise.

Two consequences follow, and both are themselves predictions:

1. **On one seed the fix cannot be seen in heads.** The account-clustered interval is about ±3
   points wide. Grade it on pooled dice seeds, or on the budget-crossing households alone.
2. **The heads gap is not where the published crisis is.** Ofgem's arrears + debt fell from 1.755m
   (Q4 2021) to 1.656m (Q4 2022), with the EBSS and EPG in force, while the no-plan average rose
   ×1.8 from 2019 to 2024. **If P2 holds and P4 holds, the remaining crisis gap is persistence:
   world debt clears and the published debt accumulates.** In that case the next layer is the
   cure, `payment_behaviour_source.later_settlement_date` and the "repaid within 22 months"
   rule. Wiring the budget alone will not close it.

*Refutation:* if the build moves Q4 2022 heads by more than +1 point on pooled seeds, the
proportional-stock assumption is wrong, and the tier's unpaid duration differs by tier. Say so
beside this line.

**Correction after the table (same day).** The measured stock share by December tier, pooled over
Q4 2017-2024, is LOW 5.2% (101/1,926), MODERATE 11.3% (25/222) and HIGH 29.1% (30/103). That is
1 : 2.2 : 5.6, not the 1 : 4 : 11.7 assumed above. So the tier-bump fix predicts less: +0.03 to
+0.1 points. More to the point, it keeps every debtor at about one bill, so it cannot touch the
pounds gap. **It is the wrong fix.** It is kept above because it was filed before the table, and
it is superseded by the fix below.

## The fix, revised: the budget decides how much of the bill is paid, month after month

**Mechanism, reusing what exists.** Each billed month, a credit-meter household's money for its
debts is its discretionary margin, plus savings drawn down until they run out. That money goes
through `household_budget.allocate_debt_payments` in its existing priority order, with energy
inside the priority tier. The unpaid part of the energy bill stays unpaid and ages. It stays
unpaid for as long as the margin stays negative, so a household under water misses month after
month, and its arrears grow by about one bill each month. The independent per-bill draw stays as
the transient-failure layer. Its LOW level was sourced as a first-presentation return rate, and
that is what it should go on meaning.

**What this costs, said first.** Households whose margin is negative before any shock (7.3%
before 2022, 2.5% with savings under £1k) would also accumulate arrears in 2016-2021. So the
pre-crisis level moves too, and it has to be graded against Ofgem's level and its pounds together
(W2_38). The budget's ladder and housing draw are R10 shapes, so the knowledge page (K8) comes
first. This is a fidelity change for after the publish, decided blind to company results.

**Pre-registered (electricity, Q4, the definition above, pooled dice seeds, written before any
build):**
- **R1, pounds.** World GBP per account behind, aged, at Q4 2023 is between £200 and £400.
  Today it is £102, against Ofgem's £1,303. The prediction is that the fix closes part of the gap,
  not all of it. What is left is the cure: 83% of spells settle, at a median of 119 days.
- **R2, crisis shape.** The ratio Q4 2023 / Q4 2021 of pounds per account behind stays at or
  above the record's 1.44. Today it is 1.76, and that comes from bigger bills alone. Once
  persistence carries part of the level, the bill-size effect becomes a smaller share of it.
- **R3, heads.** The Q4 2022 share rises by +0.5 to +1.7 points over the no-fix world on the same
  dice. That range runs from the newly crossing households with savings under £1k to all of
  them. Q2 2022 no longer sits below Q4 2021.
- **R4, the serial signature.** P(next month unpaid, given this month unpaid) rises from 0.022 to
  at least 0.25 among the households the budget puts under water.

*Refutation.* If R1 lands below £150, the budget's negative-margin population is too small or
saves its way out, and the residual gap belongs to the cure. If R3 exceeds +3 points, the
negative-margin share is too large for the record's heads, and the level comes first.

**The stress drift is filed on its own.** It is
`WORKER_FINDING_THE_WORLDS_MODERATE_STRESS_HAS_NO_EXIT_SO_STRESS_DRIFTS_FROM_8_TO_20_PERCENT_2026-10-16.md`,
with its own predictions S1-S3. MODERATE has no route back to LOW. It is not part of this fix.

**Fate:** the design is on its knowledge page (K8),
`docs/market_research/household_budget_w2_4.md` §2026-10-16. That section gives the mechanism, the
origin of every part (sourced, R10 shape or GAP), the pre-2022 negative-margin cost, and the
evidence on how long arrears last. **The build is ready to start after the 2026-10-19 publish**,
as the first world change after it. It has one named GAP to research first: the deflator for the
2026/27 essentials floor and income ladder. R1-R4 above are its pre-registration.

**The GAP, researched (2026-10-17).** `household_budget_w2_4.md`, section "The price level,
researched". The floor already holds £24/£33 a week of electricity and gas, so the build's floor
is the basket without energy, deflated line by line on CPIH divisions (£300 a month single in 2016,
£425 at 2026/27). The ladder takes AWE for earners and the April benefit-uprating path for the
bottom. That path puts a benefit household 6.5% under 2021 in real non-energy terms in 2022-23,
before any bill. Which deciles follow which path is still a GAP (HBAI income by source). The build
must name that GAP, not blend the two paths silently. R1-R4 were filed before this research, and
they stand as written. A move that comes from the uprating path is reported apart from the bill.

## 2026-10-19: R1-R4 graded on the paired run. Two hold, two are refuted on the high side, and the switch stays off

**The build** is 718a631a1 (`BUDGET_DECIDES_PAYMENT`, shipped False), plus f8fdb99cc (it pays in
pence). **The run** is world-only, to 2024-12-31, one dice draw, with the switch off and then on.
Off: `/var/tmp/budgetpay/world2_off.json`. On: `world3_on.json`, re-captured after the pence fix;
the first on capture is void (f8fdb99cc). The on arm's tree matches origin's three build files
except for comments and the position of one import. The off arm needs no re-run, because a
switch-off world never reaches the book. Grader: `/var/tmp/budgetpay/grade3.py`. **Caveats, said
first:** this is one seed, not the pooled seeds R1-R4 were written for. The two arms do not hold
quite the same accounts (935 off, 933 on, because payment feeds back into churn). And the heads
are small, 182-260 active electricity accounts a year.

Electricity, Q4. "Behind" means a bill unpaid more than 91 days. Each arm shows accounts active
in December, the number behind, their share with its account-clustered interval, and £ behind per
account behind:

| Q4 | OFF | ON | ON-OFF (points) |
|---|---|---|---|
| 2016 | 260, 6, 2.3% (0.8-4.2), £43 | 260, 9, 3.5% (1.5-5.8), £78 | +1.2 |
| 2019 | 190, 11, 5.8% (2.6-9.5), £76 | 189, 12, 6.3% (3.2-10.1), £185 | +0.6 |
| 2021 | 183, 14, 7.7% (3.8-11.5), £89 | 184, 21, 11.4% (7.1-16.3), £345 | +3.8 |
| 2022 | 192, 20, 10.4% (6.2-15.1), £90 | 193, 29, 15.0% (10.4-20.2), £529 | +4.6 |
| 2023 | 201, 22, 10.9% (7.0-15.4), £138 | 202, 35, 17.3% (12.4-22.8), £1,200 | +6.4 |
| 2024 | 212, 21, 9.9% (6.1-14.2), £145 | 213, 34, 16.0% (11.3-21.1), £1,652 | +6.1 |

- **R1, pounds: refuted, high.** £1,200 at Q4 2023, against a predicted £200-400. Ofgem's figure
  is £1,303. The world now sits near the record, but for the wrong reason (see below).
- **R2, crisis shape: holds, and overshoots.** Q4 2023 / Q4 2021 is 3.48 (off arm 1.55; record
  1.44).
- **R3, heads: refuted, high.** +4.6 points at Q4 2022, past the +3 refutation line. On one seed
  the interval is about ±5 points, so this reading cannot place R3 inside or outside its range.
  But the gap's shape does not depend on the seed: +1.2 in 2016, +3.8 by 2021, before any crisis.
  Q2 2022 (11.8%) no longer sits below Q4 2021 (11.4%), as predicted.
- **R4, serial signature: holds.** P(next month unpaid, given this month unpaid) is 0.987 among the
  households the budget put under water (n=832 month pairs). Off, it was 0.059 (n=17); over all
  accounts it goes from 0.021 to 0.752.

**What the table says the layer does.** The budget ever left a bill unpaid for 47 accounts (26 of
them electricity). Those households carry 66% of Q4 £ behind in 2019, 83% in 2021, 89% in 2022 and
93% in 2023. 14 of the 26 electricity ones never settle a single late bill. At Q4 2023 the largest
debts run to 80 unpaid bills (£3,891) and £6,333 over 12 bills. So a household under water stays
under water, and its debt grows by a bill a month without limit. That is the refutation clause's
case for R3: **"the negative-margin share is too large for the record's heads, and the level comes
first."** The pre-crisis gap grows every year (+1.2 to +3.8 points from 2016 to 2021), so the
excess is chronic negative margin that never cures. It is not a crisis response: the
difference-in-differences between Q4 2022 and Q4 2021 is only +0.8 points. The record's debt
accumulates too, but through repayment arrangements and cure. 83% of spells settle, at a median
of 119 days (R1's own note). In the on world, a budget-under-water spell does not settle.

**What this grade cannot say.** The uprating path's own share of the 2022 move needs an arm with
that path off (the BLOCKING finding's 10-17 prediction). Whether the company's crisis bad-debt
validator steps up needs a full run with the switch on, and this capture is world-only. Both are
"cannot yet say".

**Ruling.** `BUDGET_DECIDES_PAYMENT` stays False. The mechanism produces the serial signature it
was built for (R4) and the record's pounds level (R1, by magnitude). It does that with no exit
from negative margin. The next layer is what ends an under-water spell in the record: an
affordable repayment arrangement (ability to pay, SLC 27), consumption falling under a debt, and
the household's own budget adjusting. That is knowledge first (K8). It needs no new number until
the published practice is read. Handed on as
`the-under-water-household-has-no-exit-so-the-budget-switch-stays-off`.
