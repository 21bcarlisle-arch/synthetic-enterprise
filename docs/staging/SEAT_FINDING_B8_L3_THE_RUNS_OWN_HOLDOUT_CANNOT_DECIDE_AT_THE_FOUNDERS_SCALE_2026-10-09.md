**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

# B8 L3: the run now runs its own retention holdout, and at the founders' scale its interval never decides

*2026-10-09. Pre-registered in `SEAT_PREREG_B8_L3_THE_RUNS_OWN_HOLDOUT_2026-10-09.md` before the runs.*

## What was built

- **`DecisionPolicy.retention_runs_holdout`**, off on every standing policy
  (`test_no_standing_policy_runs_the_holdout`), so no standing run and no value-arms headline moves.
- **`discovered_price_sensitivity.RetentionHoldout` and `holdout_arm`.** At each renewal the
  retention guard would consider, the company flips its own coin (50/50, seeded on account and day,
  nothing the world drew). Held out: no offer (`no_offer_reason: "held_out"`). Treated: the standing
  guard's offer while the company's own interval, over rows closed **before** today, is undecided or
  refused; `retention_cut_decision` once it decides, valued at this term's own forward margin as a
  share of its own energy billing. A row is written only where the arm's treatment was given, so a
  treated renewal the decision declined never counts as treated.
- **`simulation/run_phase2b.py`** calls it inside the existing guard and publishes
  `retention_holdout_log` on a run that asks for it. This is the first production path that reads
  the B8 decision; L2 left "no run-loop retention path reads the decision" as the L3 step.
- **Controls**, one partition over held out / treated-learning (empty book) / treated-undecided
  (thin book) / a planted book's rows dated today (not yet closed) / decided-cut / decided-no-cut, and
  the coin's share and re-run stability. **Five mutations, all red:** the look-ahead (`<` to `<=`),
  the holdout never held, an undecided interval treated as decided, the margin pinned to 0.14, and
  the share set to 0. The undecided-as-decided mutation was green on the first draft: an empty book
  is "refused", never "undecided", so the partition had no undecided leg. Added.

## Measured: the default roster (400 founders, `founder_book(42)`) to 2019-12-31, same code, flag off against on

| | flag off | flag on |
|---|---|---|
| renewals the guard considered | — | 121 (62 treated, 59 held out) |
| rows with the interval decided | — | **0 of 121** |
| offers 3% / 5% / 8% | 70 / 33 / 17 (120) | 36 / 19 / 7 (62) |
| kept by an offer | 99 | 52 |
| retention cost logged, GBP | 2,776.90 | 1,397.62 |
| leavers with no offer | 41 | 54 (12 of them held out) |
| headline total net, GBP | 132,658.79 | **133,211.46 (+552.67)** |

The run's own holdout read: treated stayed 52/62 (0.839), held out 47/59 (0.797), **effect +0.042
(−0.096, +0.181), undecided.** At the L2 effect (+0.0114) and this held-out share, the power rule
needs **19,571 decisions per arm**. The book produces about 30 considered renewals a year. That is
roughly 650 years.

## Graded against the pre-registration

1. **The interval never decides. HELD.** 0 of 121.
2. **Offers about halve. HELD in shape, FAILED in the stated range.** 62 against 120 (52%), but I
   predicted 9-19 against 28. I took the base from the 2026-10-09 rate finding's 80-founder run, and
   the pre-registration calls the default roster "80 founders". It has been 400 since the director's
   founder ruling (`ad0afe7b3`); I did not re-read it before predicting. The range was wrong, and is
   left as written.
3. **No departure attributable at this size. HELD.** Departures among considered and unconsidered
   renewals: 62 off (21 offered and left, plus 41 unoffered), 64 on (10 + 54). +2, inside the 0-2
   predicted, and the books diverge from the first held-out renewal.
4. **Net moves by less than the booked retention cost. HELD.** +GBP 553 against GBP 2,777. I cannot
   yet split it between the discount the held-out half was not billed and the stays the offers would
   have bought; the expected value of the latter at the run's mean ΔP(stay) is a fraction of one stay.

## What it means

The company in the run cannot learn its own retention offer's effect from its own renewals. Not
"has not yet": at this book size it cannot within the record. So in the run the B8 decision is
always the "still learning" branch, and the policy is the standing guard on half the book. That
standing guard values every offered household as certain to be saved (`value_protected` is the full
margin plus replacement cost, whatever the offer does), which L2 measured as a loss against "cut for
none" at every cut size.

So the honest choice for the run's company is between three things a supplier of this size can do:
keep making offers it cannot evaluate; run the holdout and accept that it reads nothing for decades;
or price the offer on evidence from outside its book (published retention trials, or an industry
benchmark) and say that is what it did. **That choice is the director's**, because it is what the
company is supposed to be able to know at 400 households. It goes in `for_the_director` with a
recommendation: keep the flag off on standing policies, and treat "an offer the company cannot
evaluate" as the named limit of a small book, not a defect to engineer around.

## What this does not establish

- The margin valued in the decision is the term's forward energy margin over the term's energy
  billing; the standing guard's replacement cost, engagement weight and bad-debt netting are not in
  it. With no decided interval, the decision was never reached, so this did not bear on any row here.
- One seed, one roster, one end date.

## Reproducing it

`/tmp/b8l3/arm.py` (not kept): `CURRENT_POLICY` with `retention_runs_holdout` off and on,
`run.main(report_end="2019-12-31")`. About 26 minutes each, run side by side, about 1.9 GB RSS each.

## Addendum, 2026-10-10: landed against a moved origin

The build above sat unlanded in the shared tree overnight. Three things changed at landing, none of
them to the holdout's own rule:

- **Origin had added a gate in the same place** (2026-10-10): at a term the world does not roll, an
  offer is made only where it can buy a conversion. The holdout coin now flips only on renewals that
  gate lets through, so a renewal no offer could change is not entered into the experiment as a
  held-out row. The table above was measured on code before that gate, so its counts are not the
  current code's; the conclusion (the interval cannot decide at ~30 decisions a year) does not
  depend on them, since the gate can only make the arms smaller.
- **The run no longer imports `company.pricing` directly**, which the epistemic-wall ratchet
  refused as a new crossing. It gets the holdout from the seam,
  `company.interfaces.growth_desk.new_retention_holdout`, with the import inside the function.
- **`retention_runs_holdout` is declared in `test_policy_field_consumption.py`** as reaching the
  run through its argument; the completeness check refused it undeclared.
- **Re-checked on the landed code**, `CURRENT_POLICY` with the flag on under `policy_scope`, to
  2017-12-31: 54 holdout rows, 27 treated (20 stayed) and 27 held out (18 stayed), 0 decided; the 9
  held-out leavers are tagged `held_out` in `no_offer_churn_log`. Both arms are reachable through the
  new gate.

## Re-read on single-levy bills, 2026-10-10

The stretch record listed this reading among those taken on double-levied bills (1d3c28930). It
was re-run at origin `7252e8d72` with the same harness: `CURRENT_POLICY`, flag off against on, 400
founders, to 2019-12-31. The predictions were filed first in
`records/SEAT_PREREG_B8_L3_RE_READ_ON_SINGLE_LEVY_BILLS_2026-10-10.md`: written 14:58 and on origin
at 15:10 (`436dcaa38`). Both arms finished at 15:17. *Correction to that record: the arms started
at 14:58, not the "15:06" it says.* Each arm took 18m47s at about 2.0 GB RSS.

This is not a one-variable comparison with the 10-09 table. The levy fix, the 10-10 conversion
gate and about 80 other commits lie between them.

| | flag off | flag on |
|---|---|---|
| holdout rows (treated / held out) | — | 82 (41 / 41) |
| rows with the interval decided | — | **0 of 82** |
| offers 3% / 5% / 8% | 48 / 23 / 10 (81) | 26 / 12 / 3 (41) |
| kept by an offer | 60 | 31 |
| retention cost logged, GBP | 1,987.40 (24.54 an offer) | 932.06 |
| leavers with no offer | 40 | 53 (12 of them held out) |
| headline total net, GBP | 133,501.74 | **133,817.48 (+315.74)** |

Own interval (`estimate_offer_effect`): treated 31/41 stayed, held out 29/41, effect **+0.049
(-0.141, +0.234), undecided**.

Graded: (1) none decided, **HELD**. (2) 82 rows against 60-140, **HELD**. (3) on/off offers 51%
against 40-65%, **HELD**. (4) |+316| is below 1,987, **HELD**. (5) cost per offer is +6% against
the 10-09 figure, inside ±15%, **HELD**. Taking the levy out of the bill does not change what this
finding says, or the `for_the_director` row that cites it.

**New, not explained.** Considered renewals fall sharply by year: 1 in 2016, 53 in 2017, 25 in
2018, 3 in 2019. The off arm's offers follow the same pattern (53 / 25 / 2), so the holdout did
not cause it. In 2019 there were 17 below-threshold leavers in each arm against 2 offers. So
"about 30 a year" overstates how much the book can teach after year one, and the power argument
above gets worse, not better. I cannot yet say whether the 10-10 conversion gate, the founders'
term structure or the churn estimate's threshold produces the fall.

Harness: `/var/tmp/b8relevy/arm.py`; the per-arm logs are `/var/tmp/b8relevy/{off,on}.json` (not kept).

## Why the considered renewals fall: predictions, 2026-10-10, written before any per-year count

What I had read when I wrote these: the run loop's renewal gate (`simulation/run_phase2b.py`
around the `term_index >= 1 and commodity == _decision_leg` branch), the top-level keys of the
single-levy run (`producing_commit` 7379375f6), and its whole-run totals (600 rolled renewal
events, 112 offers, 75 no-offer leavers). No count by year.

The steps, as the code takes them: a term ends and the next one starts (`account_state_log` row,
`term_index >= 1`); the next term is on the decision leg and not indexed, with a prior rate, so
the company's estimate is computed (the renewal decision); the estimate is above
`RETENTION_THRESHOLD` (0.30), so the guard considers it; the 10-10 gate and the value test pass,
so an offer is made (`retention_log`). The 53 / 25 / 3 above are holdout rows, which come *after*
the 10-10 gate. The tool separates the threshold step from the gate.

1. **The 10-10 conversion gate.** It comes after the threshold, so it cannot move the considered
   count. Prediction: considered (estimate above 0.30) falls by year in the same shape as the
   offers. Among no-offer leavers whose estimate was above 0.30, the gate's own reason
   (`the_discount_cannot_win_the_fix`) is at most a third in each year. **Not the step.**
2. **The founders' term structure.** Prediction: the count of terms that ended on the decision leg
   stays within ±40% of its 2017 value through 2019. **Not the step.**
3. **The churn estimate's offer threshold.** Prediction: renewal decisions reached stay at least 3x
   the considered count in 2019. The share of decisions with an estimate above 0.30 falls from at
   least 40% in 2017 to at most 10% in 2019. The estimate is driven by the rate change at
   renewal, and the large 2017 rises do not recur. **This is the step.**
4. **Book attrition.** Prediction: live accounts fall by at most 35% between 2017 and 2019. That
   accounts for at most a factor of about 1.5 in a fall of about 17x. **Not the step.**

## The counts, beside the predictions (landed after them, `1153f3f8c`)

`python3 -m tools.renewal_population_by_step <run>` on the single-levy run (`producing_commit`
7379375f6, the flag-off standing policy, 2016–2025). These are distinct decision-leg accounts per
year. Both joins between the logs matched every row: 0 events at no boundary, 0 offers at no
considered decision.

There are two routes to a renewal decision, and the 53 / 25 / 3 mixes them. The **fixed-term
route**: a fix ends, and either the household does nothing and rolls onto the default with no
decision (the world's passive roll, `simulation/renewals.py` C1b), or the company estimates churn
and the world rolls. The **default-anniversary route**: a household already on the default is
asked at its anniversary whether it will fix (`svt_conversion`, or `declined_fix` with the default
on both sides). The 10-10 gate acts only on that route.

| year | fixed: ended | rolled to default, no decision | decided | considered | offered | default: decided | considered | offered | **offers** | live accounts |
|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | 281 | 182 | 99 | 53 | 53 | 35 | 0 | 0 | **53** | 444 |
| 2018 | 102 | 60 | 42 | 19 | 19 | 66 | 36 | 6 | **25** | 408 |
| 2019 | 99 | 61 | 38 | 1 | 1 | 56 | 10 | 1 | **2** | 366 |
| 2020 | 84 | 47 | 37 | 1 | 1 | 36 | 1 | 0 | 1 | 309 |
| 2021 | 75 | 42 | 33 | 21 | 21 | 39 | 8 | 0 | 21 | 284 |

The offers, 53 / 25 / 2, are the flag-off arm's offers exactly. All 75 no-offer leavers in the run
were below the threshold.

**Graded**

1. **The 10-10 gate: FAILED.** I said it was not the step. Total considered goes 53 / 55 / 11
   while offers go 53 / 25 / 2. So in 2018 nothing falls at the threshold. The fall is at the last
   step of the default route, where 6 of 36 considered households were offered. The second clause
   cannot be graded: no considered household left without an offer, so 0 rows are weighed. The
   published run cannot split the gate (`the_discount_cannot_win_the_fix`) from the value test
   (`uneconomical`) for a household that stayed. It carries no reason for those households, and
   `renewal_decisions_log` is not in the published payload.
2. **The term structure: FAILED.** I said within ±40% of 2017. Fixed-term endings go 281 → 102 →
   99, down 64%. The 400 founders' first fixes all end in 2017. 65% of them (182 of 281) roll
   passively onto the default and leave the fixed-term route. After that they come back only
   through the default anniversary, where the gate applies.
3. **The threshold: the step for 2019. HELD in direction, narrowly FAILED on both stated bounds.**
   Decisions are 94 against 11 considered in 2019, so 8.5x against the "at least 3x" I said (HELD).
   The share above 0.30 is 39.6% in 2017 (I said at least 40%) and 11.7% in 2019 (I said at most
   10%). On the fixed route alone it is 54% to 2.6%. The estimate follows the renewal price: the
   median fixed renewal rate change is +6.9% (2017), +12.1% (2018), −4.6% (2019), and the median
   estimate is 0.309 / 0.275 / 0.098.
4. **Book attrition: HELD.** Live accounts fall 444 → 366 (−17.6%), a factor of 1.2.

**The step, named.** The fall from 53 to 25 has two causes. One is the founders' term structure:
one cohort's fixes end together, and two thirds roll passively onto the default. The other is the
default route's last step, which offers to 6 of 36 considered households. The fall from 25 to 2 is
the offer threshold: fixed renewals in 2019 were cheaper than the term before, so the estimate
fell below 0.30. All three are how a real supplier's book behaves. A cohort acquired in one year
renews together. Most households do nothing at a term end, and they do not leave at that point. The world's
anchored active share is 35%, and in Ofgem's 2019 End of Fixed Term trial the 81% who did nothing
left at 0%, as cited in C1b. An offer to a household whose price fell
is rarely needed. **None of them is filed as a defect.**

**What it does to the B8 conclusion.** It makes it stronger. After 2018 the guard considers 11 renewals in 2019 and 2 in
2020, then 29 in the 2021 price rise. Over 2019–2025 it considers 97, about 14 a year, and offers
33, about 5 a year. The holdout's "about 30 decisions a year" was set by 2017–2018. The per-customer-versus-flat comparison has almost nothing to compare
in 2019–2020, and that is a property of the book and the price path, not of the code.

**One observation, not graded and not filed.** Below the threshold, the realised leave rate is
0.198 / 0.094 / 0.205 / 0.211 (2017–2020) against a mean estimate of 0.148 / 0.166 / 0.124 /
0.129. In three of the four years the estimate reads low by about a factor of 1.5 among households
it does not consider. Whether that is miscalibration is `churn_model_performance`'s question, and
four years of one run do not settle it.
