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
