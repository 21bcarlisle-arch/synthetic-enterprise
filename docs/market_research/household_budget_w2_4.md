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
