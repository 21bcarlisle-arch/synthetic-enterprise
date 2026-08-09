# WORKER FINDING — an anchor is a number AND a window, and only the mutation says which

**Found:** 2026-08-09, worker tick, `H_GAP_fabric_belief_truth_gap` L2→L3 draw.
**Class:** R15 fail-open (a band that clears its own named mutation).
**Status:** the instance is fixed and pinned in this tick. Filed because the CLASS is not.
**Owner atom:** `H_GAP_fabric_belief_truth_gap`.
**Disposition:** QUEUED, not fixed on sight — the null-correction build named below is real work and
the machine is not blocked (SELF_INTERRUPT_DISCIPLINE).

## Observed, with evidence

`observed-with-evidence`. Two cells of the two-level test had carried `AnchorStatus.NEED` since the
suite was written. One real panel — Low Carbon London, 304 households, ≥85% half-hourly coverage of
calendar 2013, already in the repo at `data/lake/lcl_household_load_shapes_2013/` — measures **both**
of the quantities they needed. Both bands were derived from it, on the same day, by the same
pre-stated rule (bootstrap P05 over the panel).

**One is live and one is fail-open.**

| cell | statistic | anchor | model | verdict |
|---|---|---|---|---|
| L2.4 | P90/P10 of household consumption | panel 5.3769, floor 4.8807 | 1.7981 (n=200 drawn) | **fires** — RED |
| L1.4 | per-home weekday-vs-weekend total-variation distance | panel median 0.0724, floor 0.0262 | 0.1247 median | **cannot fire** — removed |

L1.4's own named R15 mutation is "shuffle day-types". Relabelling the day-type calendar at random,
keeping the same 85/35 counts, destroys every trace of real weekday/weekend structure. Over **600
home-permutation samples** on the drawn population, **not one value fell below the floor**:

```
null median   0.0715
null P05      0.0514
null MINIMUM  0.0378      <-- 1.44x the floor it was supposed to breach
floor         0.0262
```

The statistic is biased upward at the coupled run's 120-day window. With 35 weekend days against 85
weekday days, two *arbitrary* subsets of the same home differ by about as much as a real household's
weekday differs from its weekend over a full year — the panel's median (0.0724) and the null median
(0.0715) are the same number to two significant figures.

## The class, stated generally

**An anchor is a number and a window, and the provenance only records the number.**

Both bands came off one panel, by one rule, on one day. The difference:

- **L2.4's statistic is a ratio BETWEEN homes.** It does not care how long each home was watched.
  Transfers across windows for free.
- **L1.4's statistic is a distance between two subsets of ONE home's days.** Its null grows as the
  subsets shrink. Transfers across windows only after null-correction.

Nothing in the anchor's citation, licence, sample size or fetch record distinguishes these. Reading
the panel's documentation more carefully would not have caught it. **Running the mutation did, in one
command.** This is the same lesson as `feedback_mutation_must_dominate_the_natural_spread`, arriving
from the other direction: there, the mutation was too weak to beat the noise; here, the *band* was
below the noise, so the mutation could not reach it.

Sibling shapes already on the register that this sits beside:
- `feedback_band_may_be_applied_to_the_wrong_load_set` — same statistic, different meter.
- `feedback_one_name_two_numbers_across_dimensions` — same phrase, two dimensions.
- `feedback_worst_of_n_control_is_not_scale_invariant` — same generator, different n.

All four are the same family: **a control's threshold carries hidden arguments, and the ones that
are not in its name are the ones that break it.**

## What would close it, and what would only look like closing it

**Would close it:** judge each home against its **own permutation null** — separation minus the median
of k randomised relabellings of that home's own calendar — so a full-year anchor and a 120-day
measurement become the same statistic. The panel's own residual null is then the only remaining
correction, and it is small because a full year's subsets are large. `LCL_WEEKDAY_WEEKEND_TV_FLOOR`
is kept derived-but-unwired in `background/lcl_household_anchors.py` because it is half of that build.

**Would only look like closing it:** lowering the floor until something fails, or measuring over a
longer window so the null shrinks. The first is the goal-seek move R12 forbids. The second changes the
run, not the control, and would leave the same defect waiting for the next short window.

**A cheap sweep worth someone's hour:** this repo has other bands anchored to published statistics
measured over a different window or sample size than the thing they judge. The question to ask each
one is not "is the source real" but **"does this statistic have a null, and is the band above it?"**
The test is mechanical: randomise the structure the statistic is supposed to detect, and see whether
the band notices.

## Pinned, so the finding cannot decay to prose

`tests/harness/test_premise_two_level.py::test_the_L1_4_ANCHOR_DOES_NOT_TRANSFER_to_a_120_day_window`
measures the null and asserts the band is still blank — so a later tick that re-wires the anchor
without null-correcting the statistic fails there rather than shipping a control that cannot fail.
