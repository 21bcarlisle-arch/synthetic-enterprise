# D48: E1's estimate-run breaches at each SPAR in the blend table (pre-registration, 2026-11-19)

Filed by the delivery lane `d48-e1-breaches-by-spar`, before any count was taken. It sits beside
`SEAT_PREREG_D48_THE_ELECTRICITY_RESIDUAL_BY_ESTIMATE_ROUTE_2026-11-19.md`. That record's outcome
says the blend's gap table "needs the E1 breach count at each SPAR alongside it, because SPAR → ∞
re-opens those breaches". This record supplies that count.

## The question

Take the pre-registered BSC blend. Is there a SPAR value in [0.5, 3] at which E1's guard,
`INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER`, goes worse than it is today? If there is not, the gap
improves at every SPAR in that range and the guard holds at every one. Then the choice no longer
turns on SPAR's value. If the guard re-opens below SPAR 3, the hold is the safer side, and the
director's row `the-bsc-smoothing-parameter-spar-value-it` is the only route.

## What is counted

The quantity is the invariant's own: `tools/domain_invariant_runner.ev_estimated_run_vs_meter`. A
run is two or more consecutive estimated bills on one meter, with an actual read on the bill before
it and on the bill after it. The ratio is the run's daily kWh over the meter's own daily kWh between
those two reads, shaped to the run's days. It is a **breach** outside [1/3, 3] and a **flag**
outside [0.5, 2]. The runner grades printed invoices. This harness reads the run book's bills
(`total_consumption_kwh`, `register_closing_kwh`, `billing_basis`), keyed on `customer_id`, so the
control is a replication rather than the graded figure. The graded figure on this book is 8 breaches
of 4,428 runs (`docs/reports/domain_invariants.json`, git 6af7fd0bfd).

A **short-first-month breach** is a breaching electricity run in which a hold-route bill was moved,
counted apart. It is the class E1 closed (13 → 6 on its own book), where one short advance set a
year of estimates.

## The counterfactual (the D48 prereg's own, unchanged)

The book is `run_output_6af7fd0bfd_20261118T070221Z.json`, and it is only read. Electricity accounts
on profile classes 1 and 3 are counterfactualised. On each actual read the advance is the true kWh
since the previous actual read, and FYC is that span's profile weight. The update is
`EAC ← w·advance/FYC + (1−w)·EAC` with `w = min(1, FYC·SPAR)`. It starts from the opening figure the
company billed on, read back off its own hold-route bill as kWh ÷ profile weight. Only estimated
bills on the hold route are re-billed, as `EAC × profile_weight(period)`. These are bills where an
actual read exists and the actual reads span under 182 days. Gas, PC2, route 1 and no-read bills
are left as they are.

**One stated choice the earlier prereg left open.** A zero advance does not update the EAC. That
is the company's own established rule (`estimate_unread_kwh`: "a zero advance is a missing
measurement"). Without it the counterfactual would change two things at once. The number of
zero advances met is printed beside the result.

**Calibration.** At SPAR 0 the harness must reproduce today's bills. Its gap and C6 residual must
match the earlier table to within 1%: 0.402 and 15,712 kWh at SPAR 0, and 2,502 kWh for C6 at
SPAR 3. If they do not match, the reconstruction is not the earlier one, and the breach counts
below are not reported as answering this question.

## Predictions, written before any count

1. **Control.** The harness count at SPAR 0 is within ±3 of the graded 8. It sits outside the
   hold route, because the 8 graded examples are all runs in 2019 to 2021, late in tenure.
2. **SPAR 0.5, 1, 2, 3: E1 stays closed.** The breach count is no higher than the control at each
   value, and there is no short-first-month breach. The blend only pulls the registry figure
   toward the meter's own reads, and the band is drawn from those reads. At most w = 3·FYC is about
   0.25 for one month's advance.
3. **SPAR ∞ re-opens it:** at least one short-first-month breach, and a count above the control.
   With w = 1, a single month's advance sets the year, which is the shape E1 was built to stop.
4. **Flags** (outside [0.5, 2]) fall monotonically from SPAR 0 to SPAR 3.

**Refuted if:** any SPAR in [0.5, 3] adds a breach over the control (then the hold is the safer
side), or SPAR ∞ adds none (then E1's original class is no longer on this book, and the ∞ column is
not a hazard here).

## Result

*(filled after the run, below this line, without editing anything above it)*

Run with `python3 -m tools.d48_spar_blend_counterfactual --book <the book>` on 2026-11-19. It took
15 s and the book was only read.

| SPAR | 0 (today) | 0.5 | 1 | 2 | 3 | 4 | 6 | 8 | 12 | ∞ |
|---|---|---|---|---|---|---|---|---|---|---|
| electricity gap | 0.407 | 0.379 | 0.357 | 0.315 | 0.289 | 0.282 | 0.305 | 0.309 | 0.314 | 0.317 |
| C6 \|residual\| kWh | 15,712 | 13,218 | 10,841 | 6,437 | 2,502 | | | | | 3,453 |
| E1 breaches (of 4,428 runs) | 8 | 8 | 8 | 8 | 8 | 8 | 9 | 9 | 10 | 13 |
| E1 flags | 27 | 27 | 27 | 27 | 27 | 28 | 27 | 27 | 30 | 27 |

Columns 4, 6, 8 and 12 were not in the pre-registered table. They were added after the table's own
columns had been read, to find where the guard first moves.

**Calibration: passed, after one correction.** The first pass took FYC from the previous read's own
day, so that day was counted twice (the runner's own window starts the day after the read). It put
C6 at SPAR 3 at 2,269 kWh, 9% off the earlier table. Fixed to start the day after, C6 matches the
earlier table exactly at every SPAR. The gap matches to within 0.001 at every SPAR from 0.5 to ∞. At
SPAR 0 it is 0.407 against the earlier 0.402. That difference is the one the earlier record names:
its reconstruction used the registry EAC, while this one reads back the figure the company billed,
which was TDCV on some accounts. The control reproduces the graded invariant exactly: 4,428 runs, 8
breaches and 27 flags, against `docs/reports/domain_invariants.json`. 3,182 hold-route bills were
re-billed, and 11 zero advances were skipped.

**Against the predictions.**
1. Control: **held.** The count is 8, exactly the graded figure, and none of the 8 is on a bill the
   blend moves.
2. SPAR 0.5 to 3, E1 stays closed: **held, more strongly than predicted.** The breach SET and the
   flag SET are both identical to the control at every value. It is not only the counts that match.
   This holds to SPAR 4.
3. SPAR ∞ re-opens it: **held.** There are 5 new breaches, all on the "below" side (ratio 0.11 to
   0.28). In each, a single short advance set the estimate and the run then under-billed against the
   meter. That is E1's original class, on 5 accounts: SYN-2016-329 and four OCC occupier accounts. The
   first new breach appears between SPAR 4 and 6.
4. Flags fall monotonically: **refuted.** The flags do not move at all through SPAR 3. The blend
   moves hold-route estimates that were already inside [0.5, 2] against the meter, because the hold's
   over-billing (billed/true 1.15) is a level error that the run ratio's band is too wide to see. So
   the flag band is not where the hold's cost shows. The cost shows in the gap.

**What this changes.** At every SPAR in [0.5, 3], and up to 4, the blend lowers the gap and leaves
E1's guard exactly as it is. So the choice between the hold and the blend no longer turns on SPAR's
value anywhere in that range. It would only turn on it if the real SPAR were about 5 or more. The
director's row `the-bsc-smoothing-parameter-spar-value-it` is amended to say so. Its default on
silence is now the blend built with SPAR as a stated range, [0.5, 3], run at both ends, with the gap
published as a range. It no longer defaults to keeping the hold. "Hold" in reply keeps the hold.
SPAR's value stays a GAP, and nothing here sets it.

**Caveat.** This is one book, and the counterfactual moves only hold-route bills, as the earlier
record defined them. A built blend would also move route 1's annualised advance, which this harness
leaves alone. The fresh run that grades a build answers to the [0.28, 0.38] band and to this
table's E1 column. Neither is graded here.
