**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Item:** `the-gas-aq-fix-is-graded-on-the-first-book-built-after-it`

# The gas AQ fix clears its row on the first book after it, and tips new gas accounts from under- to over-billing (26 Nov 2026)

Filed by the delivery seat. This grades b3f3a23f6f ("A gas premise is registered on the AQ its own meter
makes") on the first books whose git contains it: 3d3a8ee691 (25 Nov) and 001e4f680a (26 Nov). The
control is f2c6979d01 (24 Nov), the book the defect was found on
(`SEAT_FINDING_THE_ESTIMATE_AGAINST_THE_METER_ON_F2C6979D01_IS_7_OF_4250_AND_ONE_IS_A_GAS_AQ_EIGHT_TIMES_ITS_METER_2026-11-25.md`).

## Prediction 1: PROS-2021-0100 gas leaves, and the six electricity rows stay. Confirmed

Method: `tools/domain_invariant_runner.ev_estimated_run_vs_meter` over each run book's bills dressed by
`tools/d48_spar_blend_counterfactual._Dressed` (nothing re-billed). On 001e4f680a the proxy gives
**4,258 checked, 6 breaches, 31 flags**. That matches the gate's own record in
`docs/reports/domain_invariants.json` (git=001e4f680a), so the proxy is the gate on this row.

| Book | Checked | Breaches | Flags | PROS-2021-0100 gas |
|---|---|---|---|---|
| f2c6979d01 (before) | 4,250 | 7 | 32 | breach, 9.484 |
| 3d3a8ee691 (first after) | 4,258 | 6 | 31 | absent, neither breach nor flag |
| 001e4f680a | 4,258 | 6 | 31 | absent |

The six that remain are the same accounts, runs and ratios, to three decimals, on all three books:
SYN-2016-215 (4.272, 4.146), SYN-2016-221 (5.307), PROS-2016-0203 (3.368), SYN-2016-565 (4.663) and
PROS-2017-0364 (3.646). All are electricity, all are summer, and all are cause (a).

**Acted:** the exception's `max_breached` is re-based **down from 8 to 6**, and its scope now names the
six (`docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml`). The ceiling now covers what its reason licenses
and nothing more. A seventh breach of any cause refuses the publish again.

## Prediction 2: D48 gas billed/true in the hold window moves toward 1. Refuted in aggregate

The window is gas estimated bills issued while the account's actual reads span less than
`GAS_AQ_MIN_ADVANCE_DAYS` (273), including bills issued before any actual read. These are the bills
that rest on the registry AQ. The truth is the book's `meter_read_log.true_consumption_kwh` for the
same period. There are 1,576 + 3,620 bills, the same on all three books, with no truth missing.

| Window | f2c6979d01 billed/true (account median) | 001e4f680a billed/true (account median) |
|---|---|---|
| Before the first actual read (328 accounts) | 0.969 (0.994) | **1.112 (1.089)** |
| Reads span under 273 days (423 accounts) | 0.987 (0.996) | 1.056 (1.043) |
| Reads span 273 days or more (control) | 1.003 (1.003) | 1.003 (1.003) |

The control rows did not move, which is the expected result: once the reads span long enough, the AQ
is no longer read. The hold rows moved **away** from 1, from 3% under to 6–11% over. The low tail is
gone: on the 182-day cut, 2% of accounts sat below 0.67 before the fix and 0% after. The centre has
moved up, though: the interquartile range went from 0.89–1.10 to 1.00–1.17.

The pre-fix figure of 0.97 was two errors cancelling. Here is the same window split by the year the
account was acquired (bills before the first actual read, account median):

| Cohort | n | Before | After |
|---|---|---|---|
| 2016 | 197 | 0.909 | 1.050 |
| 2017 | 20 | 1.196 | 1.231 |
| 2018 | 14 | 1.247 | 1.277 |
| 2019 | 20 | 1.055 | 1.100 |
| 2020 | 19 | 0.990 | 1.003 |
| 2021 | 14 | 1.153 | 1.124 |
| 2022 | 10 | 1.173 | 1.393 |
| 2023 | 11 | 1.429 | 1.429 |
| 2024 | 19 | 1.119 | 1.164 |

On the 2016 cohort, the fix did what it says. That cohort was under-registered at 0.91, and it is now
5% over, closer to 1. The later cohorts were **already over-billed at 1.0 to 1.4 before the fix**, and the
fix leaves them there or slightly higher. Their over-billing does not come from the registry AQ being
the drawn level, so it is a separate cause.

## What I cannot yet say

Several explanations fit, and none has been measured:

1. The world's true gas use is not `aq x multiplier`. Something else in demand (occupancy, behaviour,
   price response) lowers use below the level the new AQ assumes, so "the meter's own year" in
   `register_gas_premises_on_their_own_reads` is not the meter's year. This would also explain the
   later cohorts' pre-fix over-billing.
2. The multiplier falls after acquisition (EPC or heating-system change), so the mean over the year
   before acquisition sits above the term's value.
3. Weather: the AQ is a normal year, and the first unread months fall in warmer-than-normal winters.
   Real AQs carry this too, and it is lawful.
4. 2022–23 demand reduction (cohorts 2022 and 2023 are the highest). A lagging AQ over-bills here at a
   real supplier as well.

The one-variable test for 1: on one seed, sum each gas premise's `meter_read_log` truth over the 365
days after acquisition and divide by the registered AQ. If the median is about 0.9, cause 1 holds and
the registration rule's premise is wrong. If it is about 1.0, the residual is in the first months
(causes 3 and 4), and over-billing a new account on a normal-year AQ is what a real supplier does.

Over-billing new accounts errs against our own thesis (F11): the cost lands as debit balances and
DD friction on the company's book. So it is not a reason to undo the fix.

Probes: three throwaway scripts in `/tmp/seat_gasaq/`, not kept. They read the three `run_output_*`
books under `docs/reports/` on the shared tree.
