**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** `price-cap` -- `docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`

# A gas SVT term that starts off a cap quarter is billed at the mean of every rate it has carried, not the rate in force

Found by naming the six bills that the closing run of the EPG fold fix grades above min(cap, EPG)
(`1c30d6c728`, `/var/tmp/se-epgfold-out/run_output_1c30d6c728.json`; the grade is
`SEAT_FINDING_THE_VOID_STUB_EPG_FIX_..._2026-10-24.md`, now in `done/`). There are two known causes
for a bill above the ceiling: a ToU pair graded at its split (SLC 28AD.4), and an incoming occupant's
stub. Neither of them fits these six. **This is a third cause.**

## The six

They are all gas, all `svt`, and none sits on a ToU pair: the pair is electricity only. None is an
incoming occupant either: these are `SYN-`/`PROS-` legs that have been ours for years. Rates are
ex-VAT GBP/MWh. "Struck" is what the bill charged, with VAT, in p/kWh, and the ceiling is the
grader's min(cap, EPG).

| account | month | basis | rate billed | rate in force (the log's row) | struck p/kWh | ceiling p/kWh |
|---|---|---|---|---|---|---|
| SYN-2016-428g | Jan 2019 | actual | 36.616 | 35.524 (from 1 Jan) | 3.845 | 3.730 |
| SYN-2016-428g | Feb 2019 | estimated | 36.616 | 35.524 | 3.845 | 3.730 |
| PROS-2017-0393g | Apr 2024 | estimated | 64.603 | 57.524 (from 1 Apr) | 6.783 | 6.040 |
| PROS-2017-0393g | May 2024 | estimated | 64.603 | 57.524 | 6.783 | 6.040 |
| PROS-2017-0393g | Jun 2024 | estimated | 64.604 | 57.524 | 6.783 | 6.040 |
| PROS-2017-0393g | Aug 2024 | estimated | 61.500 | 52.190 (from 1 Jul) | 6.458 | 5.480 |

Measured from these six bills' own fields, the overcharge above the ceiling is about GBP 23 in total.
Mar 2019 and Jul and Sep 2024 carry the same wrong rate, but they are catch-ups, so the grader does
not grade them.

## The cause, measured

Each household's SVT stint began off a quarter boundary: SYN-2016-428g on 27 Sep 2018, and
PROS-2017-0393g on 21 Dec 2023. Each cap quarter after that is logged as a further
`account_state_log` row with the **same** `term_index` and the **same** `term_end`. The rows before
it are never closed:

    PROS-2017-0393g  term 18  2023-12-21 -> 2024-10-01  65.619
                     term 18  2024-01-01 -> 2024-10-01  70.667
                     term 18  2024-04-01 -> 2024-10-01  57.524
                     term 18  2024-07-01 -> 2024-10-01  52.190

The bill charges the **mean of the rows that cover its month**. Every case checks:
- Jan 2024: (65.619 + 70.667) / 2 = 68.143, which is billed.
- Apr 2024: the three-row mean is 64.603, which is billed.
- Jul 2024: the four-row mean is 61.500, which is billed.
- SYN-2016-428g, Jan 2019: (37.161 + 37.161 + 35.524) / 3 = 36.615, against 36.616 billed.

When the cap falls, the mean sits above it. When the cap rises, the mean sits below: Jan 2024 billed
68.14 against 70.67, so the household was undercharged. **The over-cap count only sees the falling
half.**

## How big the class is (the same run)

- Of 1,296 legs, 11 carry overlapping term rows: 33 overlapping pairs, every one of them on a
  default tariff and every one on a gas leg.
- On 5 of those 11 legs the overlapping rates differ, so the bills are wrong. The other 6 overlap at
  one rate and are harmless today.
- 26 non-catch-up bills fall in a month with two or more covering rows. **22 are priced at the mean
  of the covering rows, and 4 at the latest row.**

The class is small. But it is a pricing defect on the bill itself, not an artefact of the grader.
The grader has a quirk of its own: `next(...)` takes the earliest covering row, so it reads the term
type correctly but would quote the stale rate.

## Not yet known (GAP)

- **Which writer emits the unclosed rows.** It has to be a gas-only path, because no electricity leg
  overlaps. The lead belief is the route that re-strikes a default term at each cap quarter for a
  leg whose stint began mid-quarter. It writes a new segment and never shortens the one before. Not
  located in `simulation/run_phase2b.py` this turn.
- **Where the bill takes the mean.** It is either the settlement fold over a term's rows or the
  bill's own unit-rate read. Not located either.
- Why only 11 of the legs whose stint starts mid-quarter carry it, when many must start mid-quarter.

## Why LATENT, not BLOCKING

Monday's publisher grade passes this run: 6 of 24,597 is 0.02%, against `OVER_CEILING_SHARE_BOUND`
of 2%. The over-cap count it would publish, 6 bills on 2 households, is a true count, and this file
now names its cause. No published figure is wrong. The bills of 5 households are, by small amounts in
both directions. A default-tariff bill above the cap is an SLC 28AD breach whatever its size, so this
is the next billing-accuracy item for D48 after Monday. It does not gate Monday.

**To close:** each month of a default term is billed at the one row in force for it. Measured: on a
fresh run, no leg carries two `account_state_log` rows covering one day at different rates, and the
over-cap count outside the ToU misgrade is 0. A one-leg control fits: no two covering rows for one
leg on one day. It would live with the class invariants
(`company/compliance/domain_invariants.py`) or in the grader.

## Located and fixed (2026-10-25, delivery seat)

**The writer.** `simulation/run_phase2b.py`, at the head of the term loop: once a household is in
`churned_billing_accounts`, `term_end_str = _departed_on[billing_account]` was assigned outright.
It was meant to cut a riding leg's term at the departure, but it also *lengthened* any term that
ended first. The rest of the mechanism follows from that:

1. The gas leg is the riding leg, and its decision leg is electricity. Its fixed offer at the
   anniversary is held in the heap until the electricity leg has rolled every start inside it
   ("a riding leg waits for the roll it rides on").
2. In those rolls the electricity leg leaves on its default tariff at a later cap boundary.
3. The gas leg then pops, declines its fix (`[DECLINED-FIX] ... gas`), and splices five default
   segments with past starts. Each one pops at once, sees a departed household and gets
   `term_end` = the departure date.

**All 11 overlapping legs fit, and nothing else does.** On every one of them, every stretched row
ends on its household's departure (`customer_events` `churned`), as read from the 1c30d6c728 output:
SYN-2016-032g/194g/193g on 2018-10-01, 159g/121g and PROS-2016-0112g on 2017-10-01, 428g on 2019-07-01,
560g on 2018-07-01, PROS-2017-0393g on 2024-10-01, PROS-2018-0359g on 2022-07-01, PROS-2020-0090g on
2021-10-01. That also answers the GAP of "why only 11": a leg needs all three of a riding gas leg, a
declined fix, and a departure inside that fix's window.

**Where the mean came from.** Nothing in the bill takes a mean. Each stretched segment was settled
separately over the whole window up to the departure, so a month covered by k rows was settled k
times, and the bill priced that month off the k rows together. **So the defect is larger than the
rate.** The leg's energy and revenue for those months were counted k times over, not just priced at
the wrong rate. The run log shows it: PROS-2017-0393g term 18 settles four segments ending
2024-10-01, with actual_net GBP 135, 157, 80 and 27.

**The fix.** `_riding_leg_term_end(term_end, departed_on)` returns the earlier of the two. A
departure cuts a term and never lengthens one. Control:
`tests/simulation/test_a_departure_cuts_a_riding_term_and_never_lengthens_one.py`. It covers both
branches, plus an AST read that the loop uses the helper and never the bare assignment. Mutation:
making the helper return the departure outright reds 2 of the 3 tests.

## Pre-registration (written before the run below returned)

A fresh full run on the fix is in flight (`/var/tmp/se-svtcut-out/`, `tools.run_annual_report`
then `tools.grade_svt_invoices_over_ceiling`). Predictions:

- P1: 0 legs carry two `account_state_log` rows covering one day (was 11 legs, 33 pairs).
- P2: the over-ceiling grade's gas `svt` bills outside the ToU misgrade: 0 (was 6).
- P3: the 11 households' gas legs settle less in total than at 1c30d6c728, because months
  settled k times are now settled once. Book-level gross margin moves by less than 0.5%. That
  bound is a guess at the size, not a derived figure.
- P4: no other leg's account-state rows change. I cannot fully assert this: the run's draws
  depend on order, and the fix changes what is settled, so the downstream effects may not be
  byte-stable. If anything else moves, I will say I cannot yet attribute it.
