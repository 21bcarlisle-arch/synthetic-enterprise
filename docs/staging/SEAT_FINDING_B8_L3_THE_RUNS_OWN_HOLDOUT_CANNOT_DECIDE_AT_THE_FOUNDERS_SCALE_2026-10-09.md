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
