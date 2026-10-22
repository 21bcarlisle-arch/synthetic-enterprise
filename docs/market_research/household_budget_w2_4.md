# W2_4_household_budget — DISCOVER findings: anchoring the hidden budget state

**Atom:** `W2_4_household_budget` (epoch 3, `docs/design/maturity_map.yaml`). **Status:** DISCOVER
only per EPOCH_GATING_AND_ATOM_AUTHORSHIP.md Rule 1 — BUILD stays gated (registered "Build in M3
with the population draw"). This atom names five hidden-state components to anchor: income band,
essential-cost floor, discretionary margin, savings buffer, priority-of-debts stack.

## Income band / discretionary margin — real, current (2026) UK data

- **[L] Median UK household disposable income (2026): ~£3,225/month (~£38,700/year gross).** A real
  anchor for the centre of the income-band distribution this atom needs.
- **[L] The aggregate "average household has £261/month left after essentials" figure MASKS real
  distributional structure: the bottom 20% of earners face essential expenditure EXCEEDING income
  by £71/month** (a genuinely NEGATIVE discretionary margin, not just a thin one), while middle-
  income households saw small real-terms improvement. This is a critical anchor for this atom's own
  "discretionary margin" concept: the shape must be able to represent a bottom decile/quintile that
  is structurally negative BEFORE any energy price shock is even applied, not merely "low margin" —
  matching this atom's own stated purpose ("arrears are the OUTPUT of a household budget meeting a
  price shock", per the adjudicated finding this atom exists to fix).

## Essential-cost floor — real, current (2026/27), quantified, with a real policy gap already built in

- **[L] JRF/Trussell's "Essentials Guarantee" research quantifies the essential-cost floor directly
  for 2026/27: a single adult needs at least £120/week, a couple £205/week**, covering food,
  clothing, and household bills — this is a real, current, directly-usable anchor for this atom's
  own "essential-cost floor" component, not an abstract concept needing a fresh estimate.
- **[L] From April 2026, Universal Credit's standard allowance (£98/week single, £154/week couple)
  sits BELOW that floor by £22/week (single) and £51/week (couple).** This is a decisive, real,
  quantified finding for the model: a materially-sized real UK population (UC claimants) lives with
  a STRUCTURAL, POLICY-DRIVEN shortfall against the essential-cost floor — i.e. for a real slice of
  the population the "essential-cost floor" is not merely close to income, income is already known
  to sit below it, independent of any energy shock. This should inform how the income-band/
  essential-cost-floor joint distribution is shaped (a genuine floor-vs-income overlap in the lower
  bands, not an assumption that essentials are always affordable in the base case).

## Priority-of-debts stack — a real discrepancy found, not just confirmed (important, not glossed over)

This atom's own registration text asserts an ordering: *"rent/mortgage, council tax, food before
energy"* (i.e. energy ranked LOWER than those four). Checked this directly against real debt-advice
sector guidance (Citizens Advice, StepChange) rather than assuming it — **and found this specific
ordering claim is not well supported as stated**:

- **[L] Citizens Advice / StepChange's own priority-vs-non-priority framework classifies energy debt
  WITH rent/mortgage, council tax, and HMRC debt as a PRIORITY debt — specifically because of
  disconnection risk** (the same class of severe consequence — losing your home, going to prison,
  losing an essential supply — that defines the priority tier), NOT a lower-ranked item paid only
  after those four are covered. Non-priority debts (credit cards, personal loans, other unsecured
  credit) are the ones explicitly described as lower-consequence and dealt with only once priority
  debts are under control.
- **What real guidance does NOT resolve (and this pass did not find further)**: a precise SECONDARY
  ordering WITHIN the priority tier itself (e.g. does a real household actually pay rent before
  energy when both are priority and money is short, or does the shorter disconnection timeline for
  energy make it go first in practice?) — the sources found describe the priority/non-priority
  SPLIT clearly but not a strict within-tier ranking.
- **Implication for the eventual build:** the atom's own registered ordering text should not be
  encoded as-is without revisiting this — "food before energy" in particular has no clear support
  found here (food is not itself a "debt" in the priority/non-priority framework at all, since there
  is no creditor relationship for future food purchases the way there is for rent/energy/council
  tax; food is better modelled as ongoing essential SPENDING competing for the same discretionary
  pool, not a debt-stack entry). This is a real, precise correction for the next FRAME pass, not
  asserted as already fixed here (no code/ordering has been built).

## Savings buffer — real, current (2026), income-band-segmented, closes a named gap

- **[L] FCA Financial Lives data: households earning under £15,000/year — 22% have NO savings at
  all, and over a third have less than £1,000.** Households earning over £50,000/year show the
  opposite pattern: only a small share lack savings, and more than half hold over £10,000. This is
  a real, decisive, INCOME-BAND-SEGMENTED anchor for the "savings buffer" component — the buffer is
  not independent of the income band, it is strongly co-varying with it, and should be modelled as a
  joint distribution (income band x savings buffer), not two independently-drawn parameters.
- **[L] Population-wide: 1 in 10 UK adults have zero cash savings; a further 21% have less than
  £1,000** — a real, current baseline even outside the lowest income band, useful as a sanity check
  on whatever joint distribution this atom eventually encodes.
- **[L] The FCA estimates ~8.9 million UK adults are in "serious financial difficulty"** (missed a
  bill payment in the last 6 months) — a real, current, population-scale anchor connecting this
  atom's own hidden-budget-state concept directly to observable real-world payment-difficulty
  incidence, reinforcing that the model's eventual calibration target (real UK arrears/missed-payment
  rates) has a genuine, sourceable population base to check against.

## Honest open items (R10)

- No precise within-priority-tier secondary ordering (rent vs energy vs council tax, when all three
  are simultaneously in arrears and money is genuinely insufficient for all) was found — a real gap
  for a more targeted search or an explicit director-set curriculum assumption (R13) if no further
  real anchor is found.

---

## 2026-10-16: design for the next build, where the budget decides how much of each bill is paid (K8, knowledge before build)

*Written before any code changes. No world code changes before the 2026-10-19 publish, so that
reading is a reading of one variable. The diagnosis behind this design is
`docs/staging/WORKER_FINDING_THE_WORLDS_PAYMENT_DRAW_HAS_NO_PRICE_INPUT_SO_2022_CANNOT_RAISE_NON_PAYMENT_AND_THE_BUDGET_BUILT_FOR_IT_IS_UNWIRED_2026-10-16.md`.
It contains the measurements and the pre-registered predictions R1 to R4. This section is the page
the build will cite. A fidelity change, decided blind to company results.*

### What the build fixes

Today, whether a bill is paid is decided by an independent draw per bill
(`simulation/arrears_engine.payment_outcome`), keyed on income-stress tier alone. A world debtor
misses one bill and starts paying again. 78% of world debtors are behind by exactly one bill, and
P(next month unpaid | this month unpaid) = 0.022. World pounds per account behind are 9 to 14
times below Ofgem's in every year 2016-2024. In the record, arrears are a household that stops
paying for many months. Nothing on any payment path reads this module.

### The mechanism

For each credit-meter household (not PPM; see "Out of scope" below), in each billed month:

1. **The money available for debts** = `discretionary_margin_monthly` (income minus the essential
   floor) **plus savings drawn down**. When the margin is negative, the shortfall comes out of
   `savings_buffer` until the buffer is empty. Savings are not refilled while the margin is
   negative. If the margin is positive, the surplus is what the household has to service its debts.
2. **The month's bills go through `allocate_debt_payments`** in `DEFAULT_DEBT_PRIORITY_ORDER`, with
   energy inside the priority tier. The energy amount due is the month's bill plus any energy
   arrears carried forward.
3. **The unpaid part of the energy bill stays unpaid and ages.** It ages from its due date, so it
   counts in Ofgem's "more than 91 days" stock once it is three bills old. A household whose margin
   stays negative and whose savings are gone misses month after month. Its arrears grow by about
   one bill a month. This is the "stops paying" shape the record has and the world lacks.
4. **The existing per-bill draw stays as the transient layer.** Its LOW-tier level was sourced as a
   first-presentation return rate (`gb_domestic_bill_payment_failure_and_arrears_prevalence.md`
   §(e)). It goes on meaning a payment that fails and is then caught up. It is not a measure of
   whether the household can afford the bill.
5. **Cure.** Once the margin turns positive again (a lower bill, or recovery from a life event), the
   surplus pays the arrears down in priority order. The existing later-settlement dating
   (`payment_behaviour_source.later_settlement_date`) is not applied to budget-driven arrears.
   Their cure is whatever the budget allows, and that is the point of the change.

### Where each part comes from

| Part | Origin | Status |
|---|---|---|
| Median disposable income, £3,225/month | ONS-reported median (this page, "Income band") | **sourced** (one anchor) |
| The shape of the income ladder by decile (`MONTHLY_DISPOSABLE_INCOME_BY_DECILE`) | fitted to the median and to "bottom 20% essentials exceed income by £71/month" | **R10 shape.** Two anchors fix the centre and the sign of the bottom. The other eight deciles are not cited. |
| Core essentials: single £520/month, couple £888/month | JRF/Trussell Essentials Guarantee 2026/27 (£120 and £205 per week) | **sourced**, at 2026/27 prices. It is **not deflated to 2016-2025**, which is a GAP the build must close or carry (see below). |
| Children add-on, £180/month | none | **R10 shape** |
| Housing cost, uniform £400-1,100/month | none. Tenure and region are not modelled. | **R10 shape.** This draw sets most of the variance in the margin. |
| Savings buckets, <£15k and >£50k tiers | FCA Financial Lives (22% none, over a third under £1k, under £15k a year; more than half over £10k, over £50k a year) | **sourced** at the two ends |
| Savings buckets, middle tier | interpolated to the population figures (10% none, 21% under £1k) | **R10 shape** |
| Priority versus non-priority split, with energy inside priority | StepChange / MoneyHelper / Citizens Advice | **sourced** |
| Order within the priority tier (rent before council tax before ... before energy) | none found | **R10 default.** Open item (above). It decides whether energy or rent goes unpaid first. |
| The rule that savings are drawn before a bill is missed | none. It is the reading of "savings buffer" this page already uses. | **design choice** |
| Applied to credit meters only | PPM cannot build arrears on consumption (self-disconnection; `debt_and_collections.md`) | **sourced reason**, design scope |

**GAP, price level.** The essentials floor is in 2026/27 pounds and the income ladder is anchored to
2026, while the energy bill is in each year's own pounds. The build must index the floor and the
income ladder to the year being run, with an ONS series (CPIH for the floor, and earnings or the
HBAI median for income). Until that is wired, it must carry the gap as a named, explicit refusal
rather than mixing 2026 pounds with 2016 bills. **Which deflator: GAP, to be researched before
the build. Not to be picked.** *Researched 2026-10-17: see the next section. The floor's deflator
is settled. The income ladder's is settled for earnings, and its bottom-decile split is still a GAP.*

### The price level, researched (2026-10-17): the floor already holds energy, and the bottom of the ladder is not earnings

**First, what the floor contains.** JRF's 2026/27 basket (JRF/Trussell, *Guarantee our
essentials*, itemised table) is per week:

| | Food | **Electricity and gas** | Water | Clothes | Communications | Travel | Sundries | Total |
|---|---|---|---|---|---|---|---|---|
| Single | 42 | **24** | 7 | 7 | 8 | 21 | 13 | 120 |
| Couple | 74 | **33** | 11 | 11 | 11 | 42 | 20 | 205 |

So `_ESSENTIALS_GUARANTEE_SINGLE` (£520/month) already holds **£104/month of energy**, and the couple
figure holds £143. The mechanism above pays the month's energy bill out of the margin, so as written
it would **count energy twice**: once at the 2026/27 level inside the floor, and again at the run
year's own bill. In 2022 the double count is also wrong in direction. A floor deflated by all-items
CPIH carries the energy shock in its index, and so does the bill. **Ruling: the floor the build uses
is the basket without electricity and gas**, £425/month single and £732/month couple at 2026/27
prices. The world's own bill takes energy's place. This is a definition, not a tuning: the floor is
"essentials other than the bill being modelled".

**The floor's deflator: each basket line on its own CPIH division.** ONS MM23, 2015=100, release
16-09-2026: food L523 (01), clothing L525 (03), transport L529 (07), communication L52A (08),
sundries on L527 (05, furnishings and household goods), water on all-items L522. The base is the
mean of April to August 2026, the months of 2026/27 published so far. Two lines are mapped by
choice, not by source. JRF does not itemise "sundries", so 05 is the nearest division. The CPIH
water class's CDID was not reached (ONS rate-limited the fetch), so water, 6% of the basket, rides
on all-items CPIH. Annual averages:

| Year | Single, ex-energy, GBP/month | Couple, ex-energy, GBP/month | Basket factor | All-items CPIH factor | AWE (KAB9) factor |
|---|---|---|---|---|---|
| 2016 | 300 | 516 | 0.708 | 0.709 | 0.655 |
| 2017 | 309 | 531 | 0.727 | 0.727 | 0.670 |
| 2018 | 316 | 544 | 0.744 | 0.744 | 0.690 |
| 2019 | 321 | 552 | 0.755 | 0.757 | 0.714 |
| 2020 | 323 | 555 | 0.760 | 0.764 | 0.725 |
| 2021 | 331 | 570 | 0.779 | 0.783 | 0.769 |
| 2022 | 363 | 628 | 0.856 | 0.846 | 0.817 |
| 2023 | 393 | 678 | 0.926 | 0.903 | 0.874 |
| 2024 | 400 | 690 | 0.943 | 0.933 | 0.920 |
| 2025 | 413 | 711 | 0.972 | 0.969 | 0.966 |

The basket tracks all-items CPIH to within half a point, except in 2022-23, where food runs it 1-2
points higher. So the division mapping matters little, and the energy split matters a lot. The floor
the code uses today (£520) is **£220 a month too high in 2016** for a single adult (£300 ex-energy,
plus the year's own bill).

**The income ladder's deflator: earnings for earners, the uprating rule for the bottom.** AWE whole
economy total pay (KAB9, LMS, mean of April to July 2026 as base) is the published monthly series
nearest a household's earned income. It rises faster than prices before 2021 (real wages grew) and
slower in 2022-23. But the deciles where the margin goes negative live mostly on benefits, and those
followed neither AWE nor CPIH. Most working-age benefits rise each April by the previous
September's CPI (Resolution Foundation, *Benefit uprating policy for April 2026*: "September
inflation is usually used to uprate most benefits the following April"). They were frozen from April
2016 to April 2019 (Welfare Reform and Work Act 2016), then uprated by 1.7% (2020), 0.5% (2021),
3.1% (2022), 10.1% (2023), 6.7% (2024), 1.7% (2025) and 3.8% (2026). The September CPI rates
derived from the rounded D7BT index agree with these to within 0.1 point. That path, against the
ex-energy basket, with 2026/27 = 1:

| Year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | **2022** | **2023** | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| Benefit-path factor (calendar average) | 0.765 | 0.765 | 0.765 | 0.765 | 0.775 | 0.781 | 0.800 | 0.867 | 0.932 | 0.959 |
| Real, against the ex-energy basket | 1.081 | 1.053 | 1.029 | 1.014 | 1.020 | 1.003 | **0.935** | **0.937** | 0.989 | 0.987 |

**What this says, before any energy bill.** A household on benefits loses **6.5% of its real
non-energy purchasing power in 2022-23**, because April 2022's 3.1% was set by September 2021's
inflation. The freeze takes 8% off it between 2016 and 2021. A single deflator on the whole ladder,
AWE or CPIH, makes both invisible. This is a crisis channel of its own, on top of the bill, and it
falls on exactly the deciles the budget puts under water.

**What stays a GAP.**
- **Which deciles of the ladder follow the benefit path, and in what share.** HBAI publishes income
  by source by decile. That cut has not been fetched. Until it is, the build either indexes the
  whole ladder on AWE and names the omission, or carries the bottom-decile path with an R10 share,
  labelled. It must not blend the two silently.
- **One-off support.** The £20 UC uplift (2020-21), the £400 EBSS (Oct 2022 to Mar 2023), and the
  2022-23 cost-of-living payments are not in the uprating path. The EBSS already reaches the world
  through the bill. The others do not.
- **Pensions** rose by the triple lock, not by the September rule. The ladder does not separate
  pensioner households.

**Raw series** (ONS MM23 L522, L523, L525, L527, L529, L52A, D7BT; LMS KAB9; fetched 2026-10-17)
are harness-side knowledge only. No world or company code reads them (W6). The build transcribes
the annual factors above as cited constants.

### Do households with a negative margin before 2022 build up debt too? Yes, and this is the cost

Drawn over 20,000 ids, **7.3%** of households have a negative margin on the October 2021 bill, and
**2.5%** have a negative margin and under £1k in savings (the finding, Probe 2). Under this design,
households that are under water before any shock also run arrears in 2016-2021. Once their
savings are gone they build up debt, which is what the design is supposed to do. So the
**pre-crisis level moves**, and it has to be graded on Ofgem's heads and pounds together (W2_38).
Nothing excludes this population from the change. Excluding it was the narrow tier-bump fix, which
the finding has already withdrawn.

**The open risk, stated first.** A household with a negative margin, no savings and no exit draws
arrears every month for ten years. In the record, a household in that position is helped through
the Warm Home Discount, the DRS, plans and benefit uprating, or leaves supply. It does not keep
building debt forever. The world has no repayment plans (the toggles are off). Prediction R3's
refutation clause ("if R3 exceeds +3 points, the level comes first") is the guard. If it fires,
the next layer is the essentials and housing shapes, not this mechanism.

### How long GB arrears last: the evidence the build is graded against

- **Ofgem / DRS impact assessment (Nov 2025, §3.10):** *"The estimated average time for recovering
  outstanding Eligible Debt is more than 22 months"*, from SOR data (`debt_and_collections.md`
  §2.1).
- **Ofgem, Monitoring social obligations 2018:** average weeks to recover a non-PPM debt on an
  arrangement range from 53 (British Gas) to 185 (SSE). **Weighted by entries, that is 95 weeks,
  about 22 months** (derived; `gb_domestic_bill_payment_failure_and_arrears_prevalence.md` §(e)3).
- **Little's law on Ofgem's 2018 stock and flow:** a pool of 1,309,768 accounts over 658,363 entries
  gives **about 2 years** in arrears or debt, and at least 12.4% of a year's inflow is still there a
  year later (derived, same file §(f)).
- **Energy UK Fig. 5:** "recovery rates" on debt more than 12 months old of 31%, 15% and 9%
  (2022-23 to 2024-25). Aged arrears rose from 52% to 65% of all arrears, 2023 to 2025. Old debt
  persists, and it was persisting more after the crisis.
- **FCA Financial Lives:** the share of adults behind on electricity was 2.2% (2020), 3.0% (2022)
  and 3.4% (2024). This is a count of people, not accounts, and it **rose after the crisis
  support ended**. This is the persistence shape at the population level.
- **The world today:** 83% of unpaid spells settle, at a median of **119 days**. That is about a
  sixth of the record's ~22 months. Pre-registered R1 (£200-400 per account behind at Q4 2023) is
  the test of whether a budget that stays negative closes part of this gap. What R1 leaves
  unclosed belongs to the cure layer.

### Out of scope for this build (each its own defect)

- **The stress tier drifts.** This is filed separately, with its own prediction:
  `docs/staging/WORKER_FINDING_THE_WORLDS_MODERATE_STRESS_HAS_NO_EXIT_SO_STRESS_DRIFTS_FROM_8_TO_20_PERCENT_2026-10-16.md`.
  It is not folded in here. Fixing both in one build would make the 2016-2024 movement impossible
  to attribute to either.
- PPM households (no arrears on consumption; self-disconnection is a separate mechanism).
- Repayment plans (the toggles are off; W2_38).

## 2026-10-19: how an under-water spell ends in the record, and the exit the world builds first (K8)

**Why this section exists.** The paired grade of 19 Oct
(`docs/staging/WORKER_FINDING_THE_WORLDS_PAYMENT_DRAW_HAS_NO_PRICE_INPUT_..._2026-10-16.md`, section
2026-10-19) found that a household the budget puts under water never leaves that state. Its debt
grows by one bill a month without limit: 80 unpaid bills at Q4 2023, and 14 of the 26 such
electricity accounts never settle a late bill. The margin is fixed for life. Income decile, housing
cost and composition are drawn once and only deflated by year. **Correction to the item that drew
this work:** the "83% settle, median 119 days" figure is the *world's* own measurement from before
the build ("The world today", above), not a published one. The published durations are the
~22-month recovery figures above.

### What ends an under-water spell, by route

| Route | Who acts | What the record says | Rate or size | In the world today |
|---|---|---|---|---|
| **Income recovers** (job, hours, benefit award, household change) | household | DWP *Income Dynamics 2010 to 2024*, Understanding Society: of individuals in relative low income (below 60% of median) one year, **36% AHC (40% BHC) are not the next**, 2022/23 → 2023/24. Working-age 39% AHC, pensioners 35% AHC. Entry 9% AHC. Earlier BHPS series, 1991-2008: 32% | ~1 in 3 a year | **absent**: margin fixed for life |
| Persistence (the check on that rate) | — | Same release: **11% AHC** of individuals in low income in at least 3 of 4 years (2020/21-2023/24). It says persistent rates are lower than HBAI's single-year rates. HBAI 2022/23 single-year AHC rate: 21% (14.3m). Ratio ≈ 0.52 (derived across two surveys, rough) | ratio ~0.5 | — |
| **Spending compresses below a normative floor** (going without) | household | Citizens Advice debt clients, Sep 2023: **half are in a negative budget** (just over a third in 2019). The average client is **£28 a month in the red**, from a £21 surplus four years earlier. Energy and council tax arrears are the commonest problem debts (50% of clients). *Corrected 2026-10-20: the £28 is the mean over all clients, not the negative-budget ones; StepChange's negative-budget clients average −£464 a month (2023). See "what a household short of money cuts", below.* A margin measured against JRF's *normative* floor can be hundreds of pounds a month. | GAP: what share of a normative shortfall shows up as energy non-payment rather than going without | **absent**: the JRF floor is spent in full before energy |
| Consumption falls (rationing, self-disconnection) | household | Self-disconnection is the PPM form (`debt_and_collections.md` §2). Credit-meter rationing reduces the bill but cannot reach zero | GAP for credit meters | absent; out of scope (demand layer) |
| Repayment arrangement on ability to pay | supplier, SLC 27.8 | ~40% of large-supplier credit plans had at least one miss in 2015. Recovery on arrangement 53-185 weeks by supplier (2018), ~22 months weighted | `debt_and_collections.md` §3 | company side; world plan toggles off (W2_38) |
| PPM for debt, Fuel Direct | supplier, DWP | 30-58% of repayers on a PPM (Q4 2021-Q4 2023). Fuel Direct takes 5% of the UC standard allowance (~£17-33 a month) | `debt_and_collections.md` §2-3 | company side, not reached (`UNREACHED_EXITS`) |
| Write-off, Debt Relief Scheme | supplier, Ofgem | DRS: up to **£500m** for about **195,000** customers who built arrears in the crisis (consultation 2025, launch 2026) | — | company side |

**What the record says, in one line.** An under-water spell ends mostly through the household's
income moving, at about a third a year, and through supplier routes that bound how far the debt
grows. A household does not stay under water for ten years at full normative essentials.

### The exit the world builds first: income moves each year

**Choice.** The household's income is re-read each calendar year. With probability
`INCOME_MOVE_PER_YEAR` it takes a fresh draw from the existing ladder (decile and position in band),
on a new appended salt per year. Otherwise it keeps the previous year's draw. Composition, housing
and the savings drawn at entry do not move. Because a fresh draw comes from the same ladder, **the
stationary distribution is the existing one, so the under-water share each year is unchanged.** The
level question stays W2_38's and the floor's, below, and is not moved by this build.

**Origin of the number.** `INCOME_MOVE_PER_YEAR = 0.41` is *calibrated*, not cited. It is the value
at which the drawn population's exit from under water at 2021 prices equals DWP's 36% AHC exit
(20,000 ids, `margin_in_year < 0`; 5.3% under water). Printed at real inputs before the build:

| Re-draw probability | Exit from under water, one year | Under water ≥3 of 4 years ÷ under water in a year |
|---|---|---|
| 0.20 | 0.17 | — |
| 0.40 | 0.35 | — |
| **0.41** | **0.36** | **0.57** |
| 0.60 | 0.53 | — |
| 1.00 | 0.91 | — |

The range 0.36-0.45 spans the published exits 32% (BHPS 1991-2008) to 40% (BHC 2022/23). The
persistence column is an **independent check** that the calibration did not use: 0.57 against the
record's ~0.52. A ±1-decile step was also printed and rejected. It needs a 0.62 move rate to reach
the same exit, and gives a persistence ratio of 0.66, further from the record.

**R10 shapes and GAPs, said plainly.**
- *Under water ≠ low income.* The rate is DWP's exit from below 60% of median AHC, applied to
  exits from a negative margin. The two populations overlap at the bottom deciles. They are not the
  same, and that is a GAP.
- *A fresh draw can jump deciles.* Most real exits land just above the line. The DWP release
  publishes quintile movements over 2015/16-2023/24, not year to year (GAP). The persistence check
  is the guard on this.
- *The calendar year is the clock.* DWP's waves are annual interviews about a year apart. This is a
  simplification.
- *Savings are not re-drawn.* A household that exits carries whatever money the book left it.

### What this build does not do, and the next layer

**The normative floor is spent in full before energy.** Citizens Advice's negative-budget clients
are about £28 a month short on actual spending *(corrected 2026-10-20: that is the mean over all clients; the negative-budget ones are about £464 short, StepChange 2023, below)*. The world's under-water households are short
against JRF's normative basket, by more. This is the most likely cause of R3's chronic heads excess
(+1.2 points in 2016, +3.8 by 2021), and **GAP: no published source found this pass says how much of
a normative shortfall a household turns into energy non-payment rather than going without.** It is
the next question, before any number. The company-side exits (arrangement, PPM, Fuel Direct,
write-off) are W2_38's and `UNREACHED_EXITS`'s.

### Predictions, written before the build is run (electricity, Q4, one seed, the on arm against `world3_on.json`)

- **U1, the exit exists.** Of electricity accounts the budget ever leaves a bill unpaid, the share
  that never settle a late bill falls from 54% (14/26) to **30% or less**.
- **U2, pounds.** £ behind per account behind at Q4 2023 falls from £1,200 to **£400-1,000**.
- **U3, heads: not fixed by this.** Q4 2022 ON-OFF stays **above +3 points**. R3 stays refuted, and
  the switch stays off until the floor question above is answered. If U3 fails (≤ +3), the
  lifetime margin carried the excess and the floor is not the next layer. Say so beside this line.
- **U4, the serial signature holds.** P(unpaid → unpaid) among the households the budget leaves
  under water stays **≥ 0.9**, because a spell's months are still consecutive.

Sources: [DWP Income Dynamics 2010 to 2024](https://www.gov.uk/government/statistics/income-dynamics-2010-to-2024/income-dynamics-income-movements-and-the-persistence-of-low-income-2010-to-2024);
[ISER summary of the 1991-2008 series](https://www.iser.essex.ac.uk/?p=231042);
[Citizens Advice, "One in four people behind on at least one bill", Sep 2023](https://www.citizensadvice.org.uk/about-us/about-us1/media/press-releases/one-in-four-people-behind-on-at-least-one-bill-as-uk-households-fall-22-billion-in-the-red/);
HBAI 2022/23 AHC rate as reported by [Leeds Observatory](https://observatory.leeds.gov.uk/leeds-poverty-fact-book/relative-and-absolute-poverty/) (secondary, not re-read at DWP);
DRS figures as reported by [moneytothemasses](https://moneytothemasses.com/news/plans-to-write-off-500m-of-energy-debt-who-will-qualify) (secondary; primary in `debt_and_collections.md` §2.1).

### U1-U4 graded (2026-10-19): the exit works, and the level is what keeps the switch off

**The run.** World-only to 2024-12-31, one dice draw, switch on, at 78a36a84c (the capture's tree
was that commit's bytes). Off arm `world2_off.json` and pre-exit on arm `world3_on.json` as on
19 Oct. New on arm `/var/tmp/budgetpay/world4_on_income_moves.json`. Grader
`/var/tmp/budgetpay/grade4.py`, which re-prints the 19 Oct readings exactly from `world3_on.json`
(14/26, £1,200, +4.6, 80 bills) before it reads the new arm. **Caveats, first:** one seed, about
±5 points on heads; 916 accounts against 933, because payment feeds back into churn.

| Q4, electricity | OFF | ON, no exit (19 Oct) | ON, income moves |
|---|---|---|---|
| 2016 | 2.3%, £43 | 3.5%, £78 | 3.5%, £78 |
| 2019 | 5.8%, £76 | 6.3%, £185 | 7.4%, £318 |
| 2021 | 7.7%, £89 | 11.4%, £345 | 9.8%, £352 |
| 2022 | 10.4%, £90 | 15.0%, £529 | 13.5%, £298 |
| 2023 | 10.9%, £138 | 17.3%, £1,200 | 13.9%, £828 |
| 2024 | 9.9%, £145 | 16.0%, £1,652 | 12.2%, £863 |

- **U1, the exit exists: holds.** 7 of 31 (23%) budget-under-water electricity accounts never settle
  a late bill, down from 14 of 26 (54%).
- **U2, pounds: holds.** £828 at Q4 2023, down from £1,200 (Ofgem £1,303).
- **U3, heads not fixed: holds, at the line.** +3.1 points at Q4 2022, against the +3 line. On one
  seed this cannot tell +3.1 from +2.9. The readable part does not depend on the seed: the
  pre-crisis excess is +1.0 to +2.7 points every year from 2016 to 2021, down from up to +3.8.
- **U4, serial signature: holds.** P(unpaid → unpaid) among the under-water accounts is 0.929
  (n=566), from 0.987.
- R1 (£200-400) stays refuted high at £828. R2 is 2.35 (record 1.44). The diff-in-diff, Q4 2022
  less Q4 2021, is +0.9 points, against +0.8 before.

**The 80-bill account is the persistent tail, not a defect.** `PROS-2016-0394` is a decile-1
couple with £1,043 of housing. Its one move before 2024, in 2019, drew decile 1 again. Its 2024
move draws decile 6, with a margin of +£1,825. One account in 31 under water for eight years
against a 0.59 yearly stay rate is about what chance gives (0.59^7 ≈ 2.5% per account, plus repeat
draws into the bottom).

**Ruling.** `BUDGET_DECIDES_PAYMENT` stays False. The spell now ends at the published rate, and the
pounds fall towards the record. What is left is the **level**: a chronic pre-crisis heads excess,
and R1 still high. That is the floor question above: a household spends JRF's normative basket in
full before it pays for energy. Filed as
`docs/staging/WORKER_FINDING_THE_BUDGET_SPENDS_THE_NORMATIVE_FLOOR_IN_FULL_BEFORE_ENERGY_SO_THE_PRE_CRISIS_HEADS_RUN_HIGH_2026-10-19.md`.

## 2026-10-20: what a household short of money cuts, and in what order (K8, knowledge before the arm)

**The question** (from `docs/staging/WORKER_FINDING_THE_BUDGET_SPENDS_THE_NORMATIVE_FLOOR_IN_FULL_BEFORE_ENERGY_SO_THE_PRE_CRISIS_HEADS_RUN_HIGH_2026-10-19.md`):
when a GB household's money falls short of its essentials, which goes unpaid or uncut first,
and how much of a normative floor does it spend before energy arrears begin?

**Correction first, beside the claims above.** The rows above (the route table and "What this
build does not do") read Citizens Advice's "£28 a month in the red" as the shortfall of the
negative-budget clients, and so argued that a shortfall on actual spending is small. It is the
mean over **all** debt clients, of whom about half are in surplus (the release: "the average
person the charity helps with debt is £28 in the red"). Among the negative-budget clients
themselves the shortfall is hundreds of pounds a month: StepChange's clients with a negative
budget after advice, on its Standard Financial Statement budgets, which are actual spending capped
at the SFS guideline figures, averaged **−£464 a month in 2023 and −£532 in 2024** (30% of
clients). So a shortfall measured on actual spending is not small, and the finding's premise that
the floor overstates spending by hundreds of pounds is not established.

### What the record says

| Question | Evidence | Reading |
|---|---|---|
| Is housing paid before energy? | ONS OPN, 14-25 June 2023: **6%** of adults behind on gas or electricity, **2%** behind on rent or mortgage, while 47% and 43% found each very or somewhat hard to afford | **Yes.** About as many struggle with each, and three times as many are behind on energy. Housing is protected. |
| Which bill slips most? | FCA Financial Lives recontact, January 2023: utility bills the most commonly missed (**8.6%** of UK adults), then credit cards (4.8%), council tax (4.4%). Citizens Advice, Sep 2023: energy and council tax arrears the commonest problem debts (50% of debt clients have one or both) | Energy is the bill that slips first. That is consistent with it being paid *after* the things a household protects, not before them. |
| Are food and energy cut one after the other, or together? | JRF cost of living tracker, winter 2022-23, bottom 40% of incomes: **62%** going without essentials (7.2m), **41%** in arrears (4.7m), **37%** both (4.3m). So 91% of the households in arrears are also going without, and 60% of those going without are also in arrears | **Together.** A household in arrears has nearly always cut its essentials too, so the essentials are *not* spent in full before arrears begin. Nor is energy paid in full before essentials are cut: 2.9m go without with no arrears, and 4.3m do both. |
| What do households cut when costs rise? | ONS OPN, 11-22 January 2023, of adults whose costs rose: **59%** using less gas or electricity, **46%** spending less on food and essentials, 23% using savings | Both lines compress at once. |
| Debt advice's own order | StepChange / MoneyHelper / Citizens Advice (above): essential living costs, including energy, are budgeted first, then priority debts (energy arrears inside), then non-priority | A normative rule for what advice tells a household to do, not a measured description of what it does before advice. |

### What this establishes, and what it does not

- **Established.** Housing first. Then food and the other essentials and energy are short
  *together*: no published series shows either one paid in full while the other takes the whole
  shortfall. The world today does the second of those (JRF's ex-energy basket in full, then energy
  takes the whole shortfall), so the order it encodes is contradicted by JRF's overlap.
- **GAP: how a pound of shortfall divides between going without and energy arrears.** No source
  found publishes it. JRF and ONS publish *heads* (who goes without, who is in arrears), never the
  pounds of each. Candidate evidence not read this pass: the Living Costs and Food Survey at the
  bottom decile (actual spend on food against the JRF basket), Trussell *Hunger in the UK*.
- **GAP: what share of a normative floor is spent before arrears begin.** Not published. The SFS
  guidelines (LCF actual spending of lower-income households) and JRF's MIS are compared in
  Loughborough's *Comparing SFS spending guidelines with MIS: 2024 update*, which could not be
  read this pass (HTTP 403). Those figures would bound how far below the floor actual spending
  sits.

### The choice the arm makes, and why

With no measured split, the arm takes the **no-priority** stance between the basket and energy:
money left after housing is shared between the core basket and what is owed on energy **pro rata
to their sizes**, so each is short by the same fraction. It is the one order that reproduces JRF's
"both at once" without a new number. The split is the two amounts themselves. It is a stated
belief, not a measurement. The other two orders the record allows are bounds. Basket first is
today's code, contradicted by the overlap. Energy first is debt advice's rule, and contradicted
by energy being the commonest missed bill. Code: `ENERGY_SHARES_THE_SHORTFALL` in
`simulation/household_budget.py`, default False, read only while `BUDGET_DECIDES_PAYMENT` is on.

Printed at real inputs before the run (20,000 drawn households, savings ignored, one electricity
leg). The share of households short is the same under both orders, because the order does not
change who is short. What changes is how much of the bill goes unpaid:

| Year, monthly bill | Households short | Energy short, £/month, basket first (today) | Energy short, £/month, pro rata | Short by the whole bill: today / pro rata |
|---|---|---|---|---|
| 2019, £55 | 6.4% | £190 | £17 | 5.2% / 0.0% |
| 2022, £95 | 9.0% | £256 | £34 | 6.9% / 0.0% |

Today a short household pays nothing toward its bill. Pro rata it pays about two thirds to three
quarters of each bill and falls behind by the rest.

Sources: [ONS OPN, 14-25 June 2023](https://www.ons.gov.uk/peoplepopulationandcommunity/wellbeing/bulletins/publicopinionsandsocialtrendsgreatbritain/14to25june2023);
[ONS OPN, 11-22 January 2023](https://www.ons.gov.uk/peoplepopulationandcommunity/wellbeing/bulletins/publicopinionsandsocialtrendsgreatbritain/11to22january2023);
[FCA Financial Lives cost of living recontact](https://www.fca.org.uk/publication/financial-lives/financial-lives-cost-of-living-jan-2024-recontact-survey-findings.pdf) (January 2023 rates as reported in secondary coverage; the PDF not re-read this pass);
JRF, *Going under and without: JRF's cost of living tracker, winter 2022/23* (read from a mirrored copy of the PDF, [michaelharrison.org.uk](https://michaelharrison.org.uk/wp-content/uploads/2022/12/Going-under-and-without-JRFs-cost-of-living-tracker-winter-2022-23.pdf), pp. 3-10; the jrf.org.uk original not re-read);
[StepChange, household bills arrears surge (2024 data)](https://www.stepchange.org/media-centre/press-releases/household-bills-arrears-surge.aspx);
[Citizens Advice, Sep 2023](https://www.citizensadvice.org.uk/about-us/about-us1/media/press-releases/one-in-four-people-behind-on-at-least-one-bill-as-uk-households-fall-22-billion-in-the-red/).

### Graded (2026-10-20): sharing the shortfall removes the pre-crisis excess, on one seed

**The run.** As pre-registered in
`docs/staging/records/SEAT_PREREG_THE_BUDGET_SHARES_THE_SHORTFALL_BETWEEN_THE_BASKET_AND_ENERGY_2026-10-20.md`:
world-only to 2024-12-31, one dice draw, both switches on, at 78a36a84c plus only the
`ENERGY_SHARES_THE_SHORTFALL` change. Output `/var/tmp/budgetpay/world5_on_shared_shortfall.json`
(wall 4,998 s, 918 accounts, 55 ever under water, 31 electricity). The arm's worktree had been
removed by grading time, so the grader read `account_clustered` from the main tree
(`grade5b.py`, which differs from `grade5.py` only in that path). It re-printed `world4`'s 23% U1
and £828 exactly before reading the new arm. **Caveats, first:** one seed. Each pre-crisis Q4
difference is 0 to 2 accounts out of about 200, well inside each arm's interval.

| Q4, electricity | OFF | ON, basket first (`world4`) | ON, shared shortfall | Shared ON-OFF |
|---|---|---|---|---|
| 2016 | 2.3%, £43 | 3.5%, £78 | 2.3%, £43 | +0.0 |
| 2017 | 4.4%, £55 | 7.1%, £131 | 5.3%, £53 | +0.9 |
| 2018 | 5.3%, £63 | 6.3%, £252 | 4.3%, £63 | -1.0 |
| 2019 | 5.8%, £76 | 7.4%, £318 | 5.8%, £74 | +0.0 |
| 2020 | 6.6%, £100 | 7.7%, £324 | 6.6%, £101 | +0.0 |
| 2021 | 7.7%, £89 | 9.8%, £352 | 7.1%, £92 | -0.5 |
| 2022 | 10.4%, £90 | 13.5%, £298 | 11.5%, £115 | +1.0 |
| 2023 | 10.9%, £138 | 13.9%, £828 | 11.4%, £244 | +0.5 |
| 2024 | 9.9%, £145 | 12.2%, £863 | 10.4%, £164 | +0.5 |

- **The finding's prediction (filed 2026-10-19): holds.** The excess is under +1 point in every Q4
  from 2016 to 2021 (largest +0.9, in 2017), and U1 is 6%, against a limit of 30%.
- **S1, my prediction that at least one year stays above +1: refuted.** I expected aged debt to
  arrive later but still arrive in most spells. It mostly does not reach 91 days before the spell
  ends. The order was the excess, and the housing draw is not implicated on this seed.
- **S2, U1 at 10% or less: holds.** 2 of 31 (6%) under-water electricity accounts never settle a
  late bill, against 7 of 31 in `world4`.
- **S3, £200-500 at Q4 2023: holds.** £244, against £828. R1's £200-400 now holds too, but it is
  far under Ofgem's £1,303 per account behind.
- **S4, U3 at +0.5 to +2.5 at Q4 2022: holds.** +1.0, against +3.1.
- **S5, U4 at 0.9 or more: holds.** 0.926 (n=529).
- **The crisis step-up survives.** The diff-in-diff, Q4 2022 less Q4 2021, is +1.6 points (+0.9 in
  `world4`). R2, the £ ratio of Q4 2023 to Q4 2021, is 2.64 against the record's 1.44: the pounds
  build mainly in 2023 (£115 at Q4 2022, £324 at Q2 2023).

**What this does not settle.** One seed cannot bound a paired difference of one or two accounts. Pro
rata is still a stated belief (the GAP above stands). The pounds now sit under the record, not
over it, so whether the level is right is a separate, open question.

**Ruling.** Both switches stay False. Per the prereg, `ENERGY_SHARES_THE_SHORTFALL` is a candidate to
move only on a second seed. That means three arms on a new dice draw: off, basket first and shared,
about 85 minutes each, run serially. They are owed next. The housing draw (R10) is not the next
cause, because this seed shows no pre-crisis excess left for it to explain.

### Graded, second seed (2026-10-20): the shared shortfall holds, and both switches default on

Three arms (off, basket first, shared) on dice seed 2, world-only to 2024-12-31 at `5a2468fdf`. The
prereg is `docs/staging/records/SEAT_PREREG_THE_SHARED_SHORTFALL_ON_A_SECOND_DICE_SEED_2026-10-20.md`
and the result, with its table, is
`docs/staging/records/SEAT_RESULT_THE_SHARED_SHORTFALL_HOLDS_ON_A_SECOND_DICE_SEED_2026-10-20.md`.
Every band holds. Shared-off in Q4 2016-2021 runs from -0.5 to +0.9. U1 is 6%. Pounds behind at
Q4 2023 are £302. The diff-in-diff is +2.1. U4 is 0.926. Basket-off is above +1 in 5 of 6 years
and £1,011 at Q4 2023. The under-water set is the same 55 accounts.

**What the second seed can and cannot show.** The dice reach only the payment noise around the
budget. The off arm moves in every year (Q4 2022: 14 heads against seed 1's 20), but U1 and U4 repeat
seed 1 exactly, because the budget, not the dice, decides an under-water household's payment. Two
seeds therefore bound the noise around the budget. They do not bound a re-draw of the budget
population, which stays an open robustness question.

**Ruling: `BUDGET_DECIDES_PAYMENT` and `ENERGY_SHARES_THE_SHORTFALL` default True**
(`simulation/household_budget.py`), in their own commit. Pro rata is still the stated belief from
the GAP above, not a measured split. On this seed, the off world's Q4 2022 heads share falls rather
than rises. The crisis shows in the pounds behind (£94, then £142, then £302), not in the share of
heads.

## 2026-10-22: stock or demand. What the pro-rata line shares against (K8, knowledge before the arm)

**The question** (from the crisis bad-debt finding, "the depth is the shortfall rule's fixed point", and
the world finding on parked arrears, 2026-10-21): when a household is short, is its shortfall shared
between the basket and energy in proportion to **what it owes on energy in total** (the arrears stock
plus this month's bill), or to **this month's demand** (this month's bill)?

**What the record can say.** Nothing direct. The JRF and ONS rows above establish that food and energy
are short *together* and that housing is protected. They publish heads, never pounds, and nothing about
how a household weighs an old balance against a new bill. What the record does say is the outcome a
rule must be able to reach: Ofgem's average electricity arrears are **£555 (2017) to £1,303 (2023)**
per account in arrears, about most of a year of that fuel's bill, and **rising every year**
(`debt_and_collections.md` §2.5a). Debt advice (StepChange, Citizens Advice) budgets a household's
essentials and its current energy use first, then offers what is left against arrears: a demand
reading, but normative, not a measurement of what households do before advice.

**What the stock reading does, measured.** Sharing against the stock lets energy's part `A·O/(C+O)`
grow as the debt `O` grows, so the debt stops at `O*/B = C/(A−B)` bills. Over the 256 credit
account-years whose margin is below their bill (world dump to 2023), that cap is a median **1.67
bills** (p90 3.49), and the world's live arrears are 1.4-2.4 months of bill at every 31 December
against the record's most of a year. A household with a large backlog also cuts food to repay it even
when this month's money covers this month's basket and bill. No source supports that, and debt
advice says the opposite.

**What the demand reading does, printed at real inputs before the build** (same 256 account-years,
`/var/tmp/leaver_trace/demand.py`). Energy's part is `A·B/(C+B)` while `A < C+B`, so the stock grows
by `1 − A/(C+B)` bills a month with no cap: a median **0.34** (p25 0.15, p90 0.63), about **4 bills a
year** (p90 7.6). The spell is ended by the income move (0.41 a year, above), not by the rule.
2016-23 medians run 0.24-0.40 a month, with no crisis step in the rate itself; the crisis enters
through more households having `A < C+B` and through larger bills.

**The choice, and why.** The demand reading: the basket is short by the fraction this month's money
falls short of this month's basket and bill, `basket = min(C, C·A/(C+B))`, and everything else after
housing goes to energy, oldest bill first. A household that can meet this month keeps its basket
whole and repays the backlog out of the rest. It is still a stated belief. **GAP (unchanged): how a
pound of shortfall divides between going without and arrears.** This changes only what the pro-rata
line is pro rata *to*. Code: `THE_SHORTFALL_IS_SHARED_ON_THE_MONTHS_DEMAND` in
`simulation/household_budget.py`, default False, read only inside `ENERGY_SHARES_THE_SHORTFALL`. It is
decided blind to company results and graded world-only on the depth column. Pre-registration:
`docs/staging/records/SEAT_PREREG_THE_SHORTFALL_SHARED_ON_THE_MONTHS_DEMAND_2026-10-22.md`.

**What can refute it.** Overshoot is the risk the stock reading never had: with no cap, a household
under water for several years can owe several years of bills, and the record's average is under one.
The pre-registration bounds it from above as well as below.

### Graded, seed 1 (2026-10-22): the demand reading doubles the depth, inside every band

World-only to 2023-12-31. Result:
`docs/staging/records/SEAT_RESULT_THE_SHORTFALL_SHARED_ON_THE_MONTHS_DEMAND_SEED_1_2026-10-22.md`. The
mean months behind at 31 December rise from 1.4-2.4 to 3.3-6.8, and £ per account in arrears at 2023
from £198 to £580 (Ofgem £1,303). Heads rise by 0.3-4.1 points, and there is no overshoot. All five
pre-registered bands hold. The median is nearly unchanged, so the gain is the persistent-deficit tail.
Depth falls after 2019, where the record's rises, and that is not yet explained. **The switch stays
off until the queued second seed is graded.**

### Graded, seed 2 (2026-10-22): all five bands hold again

Result: `docs/staging/records/SEAT_RESULT_THE_SHORTFALL_SHARED_ON_THE_MONTHS_DEMAND_SEED_2_2026-10-22.md`.
Depth runs 2.8-6.0 against 1.6-2.6, and £ per account in arrears at 2023 is £710 against £250 (Ofgem
£1,303). Heads rise by 0.3-4.1 points, and no year overshoots. The fall in depth after 2019 comes back
on this seed, so it belongs to the budget population and is not payment noise. With two seeds held, the
switch can go on, by the same two-seed rule as `ENERGY_SHARES_THE_SHORTFALL`.
