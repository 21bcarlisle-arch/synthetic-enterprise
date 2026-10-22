**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** unbilled-energy-and-revenue-assurance

# A dual household that leaves on its electricity leg is billed gas for up to a year, and the red dates from the commit that made the book dual (2026-10-22)

*Worker tick, 2026-10-22, found while testing the default flip of `THE_SHORTFALL_IS_SHARED_ON_THE_MONTHS_DEMAND`.*

`tests/simulation/test_a_departed_household_is_supplied_on_no_leg_after_it_leaves.py::test_no_leg_settles_on_or_after_the_departure_date`
is in `HEAD_RED_REGISTER.md` since 2026-10-18, with no cause written. Measured here:

- **Not the household-budget switches.** Red at `origin/main` d8d3549b2 with
  `THE_SHORTFALL_IS_SHARED_ON_THE_MONTHS_DEMAND` off and on, and at 768f41ed14^, before the budget
  defaults moved.
- **First bad commit, by `git bisect run` over `simulation/ sim/ company/ saas/` between d45a141f20
  (the test's own commit, green) and 768f41ed14^ (red): `c136809f53`** "The book's fuel is the
  home's: ... 73.6% dual". Before it the founders were 0% dual, so the test's partition leg
  (`test_departures_on_each_fuel_are_in_the_window`) was met by single-fuel accounts and the
  dual-household case was never tested.
- **What it bills.** In the 2016-01 to 2017-04 window, 9 households leave (all on the SVT-segment
  route, `svt_departures`, booked on the electricity leg) and their gas leg goes on settling: 82 to
  345 days after the departure date, several to the window's end. For example `SYN-2016-126`
  left on 2016-04-01 and its gas settled to 2017-03-11.

**Cause: the leading candidate, not tested.** The SVT branch does add the household to
`churned_billing_accounts` (`run_phase2b.py` ~3313), and the top-of-loop skip is household-level
(~2819). So later gas terms are skipped. A gas term already popped before the departure is not,
because a leg's whole term is posted at once. The guard at ~4467 assumes "the household's other
leg, popped after this one". Since c136809f5 a dual household's legs do not share term starts:
gas terms start on, for example, the 10th of the month. So a gas term that started just before the
electricity departure settles in full. The one-variable test is to print, for the 9 households, the
gas term's start and end around the departure date.

**Probably the same cause:** `tests/simulation/test_registration_loss_feed.py::test_every_departure_reaches_the_company_as_exactly_one_notice_per_supply_point`,
also first red on 2026-10-18.

**Why it matters (M2).** The company bills energy to a household that has gone and books debt on an
account nobody holds. That is revenue and bad debt that no real supplier would see.

## Disposition: fixed (worker tick, 2026-10-22)

**The one-variable test confirmed the cause.** On the 2016-01 to 2017-04-30 window, each of the 9
households has a single gas term that starts before its electricity departure and runs past it:
`SYN-2016-126` gas term from 2016-03-12, left 2016-04-01, gas settled to 2017-03-11 (345 days after);
`SYN-2016-190` from 2016-04-16, left 2016-07-01, settled to 2017-04-15; `SYN-2016-283` from
2016-06-21, left 2016-07-01, settled to the window's end. The other 14 departing dual households
left on a date that matched their gas term's own end, so they billed nothing late.

**Knowledge first.** `docs/market_research/unbilled_energy_and_revenue_assurance.md`, "What a
change of supplier ends on each fuel". A dual-fuel switch moves both fuels on one nominated date
(Ofgem Switching Programme). Each fuel's supply ends at its change-of-supplier read on that date.
GAP: how often the two fuels are lost on different dates.

**Fix** (`simulation/run_phase2b.py`). A riding leg's term (a dual household's gas) that has a
decision-leg term start inside it goes back in the heap, keyed to that start. It is asked again
once that start has popped, and then posted either whole or cut so that it ends at the departure
(`term_end` is exclusive). Each departure also writes one `churned` row per supply point it ended,
to a new `leg_departures` output. That row does not go into `customer_events`, because about 40
readers there count `churned` rows as households leaving. A gas row there would count every dual
departure twice.

**Before and after, on one run** (the default seed, `report_end=2017-04-30`, both readings taken by
the same probe at origin `bc1e6ad780`):

| | before | after |
|---|---|---|
| households billed gas on or after their departure | 9 | 0 |
| gas kWh settled on or after departure | 70,599 | 0 |
| gas revenue on or after departure | £2,284.97 | £0.00 |
| departures / registration-loss notices | 28 / 51 | 28 / 51 |

After the fix, each of the 9 gas legs ends the day before its household left (for example
`SYN-2016-126` 2016-03-12 to 2016-03-31). `test_no_leg_settles_on_or_after_the_departure_date` and
`test_every_departure_reaches_the_company_as_exactly_one_notice_per_supply_point` are green, with the
rest of both files and `test_run_phase2b_event_log.py` (32 passed).

**Effect on every run: not measured.** Every dual household's gas term is now posted after the
electricity term start that falls inside it, not before. Each term is still priced and settled on
its own start date. But company state that is read between pops (the treasury balance, the
collections desk) now sees a different order, so stayers' figures can move too. I have not measured
that. Value-arms results taken before this commit are not comparable with results taken after it.
The reorder also removes a look-ahead: an electricity roll used to see the household's gas payments
for a term that started days earlier, through to that term's end.

**Mutations** (departure test file, 3 tests): disabling the hold reds one test, and dropping the
`leg_departures` row reds one test. Both bite.
