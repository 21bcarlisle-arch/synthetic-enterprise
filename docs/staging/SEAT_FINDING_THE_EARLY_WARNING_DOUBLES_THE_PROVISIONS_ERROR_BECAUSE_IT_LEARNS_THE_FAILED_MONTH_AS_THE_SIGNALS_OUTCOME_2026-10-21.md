**Severity:** LATENT · **Lane:** E_finance_treasury · **Epoch:** 4 · **Atom:** `E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build` · **Direction item:** `e6-grade-the-early-warning-on-off-pair`
**Knowledge:** bad-debt-provisioning -- `docs/market_research/bad_debt_provisioning.md`, "Early warning in the forward-cash-forecast provision" (graded and corrected in the same commit)

# The early warning doubles the provision's error on the run's book, because it learns the failed month as the signal's outcome

Grades the pair pre-registered in
`docs/staging/records/SEAT_PREREG_THE_EARLY_WARNING_SIGNALS_ON_AND_OFF_IN_THE_FORWARD_CASH_FORECAST_PROVISION_2026-10-21.md`.
LATENT: the module is default off and has no production caller, so nothing published moves. The
defect is in a learned lift that any future caller would read.

## Set-up

- **One default run** at `cda47a346` (origin/main), `python3 -m simulation.run_phase2b` under an
  import hook that calls the run's own `_company_provision_by_year_end` FIRST, returns its value
  untouched, then pickles the company's ledger book, its ARUDD failure records
  (`_consumer._dd_failures`) and every method-register read the grade needs. 1,293 accounts, 689
  failures (605 code 0, 84 instruction cancelled), 395,739 method reads, 0 errors. Run took 46 min.
- **150 read dates**: 37 quarter-ends, 113 fifteenths, 2016-01 to 2025-05.
- **Off** = `account_provision(signal=None)`. **On** = the same with the signal `signal_at` reads at
  the date, from one `learn(..., signals_of=...)` per date. Accounts with no signal read identically
  by construction. **Control:** at 4 dates the real `book_provision` was called both ways and equals
  this decomposition per account, to the penny, on both arms.
- **Realised** = owed at the read date less the payment credits in the next 365 days (write-offs
  are not cash), for dates with a year of run after them.
- Harness and outputs: `/var/tmp/e6ew/` (`probe.py`, `grade.py`, `readout.py`, `dig.py`,
  `dig2.py`, `grade.json`, `readout.txt`).

## The predictions, graded

| # | Prediction | Result | |
|---|---|---|---|
| P1 | quarter-end on = off within 1% of the book, per account identical on >= 99% | the book total differs at **32 of 32** numbered quarter-ends (only 3 within 1%, worst +10.4%, GBP 60 on GBP 582 at 2022-12-31); per account identical 96.4% | **refuted** |
| P2 | mid-month, signal-read learned accounts: on > off on 100% | 460 of 472 (97.5%); 12 below, where the signal cell's P(pay) beats the chain's | **refuted, narrowly** |
| P3 | `SIGNAL_CODE_0_AGAIN` read on 0 accounts at every date | read on **105** account-dates (30 quarter-end, 75 mid-month) | **refuted** |
| P4 | on total None at 1-3 early mid-month dates, then a number | no date where on is None and off is a number. 10 account-level GAPs, all at or before 2016-07, all while the **off** total is itself None (no transition out of missed state 2-3 yet, through 2017-05-15) | **refuted: masked, not tested** |
| P5 | on-arm MAE below off on signal-read accounts | quarter-end **3.75 vs 1.70** (n 132); mid-month **6.12 vs 3.51** (n 419) | **refuted** |
| P6 | the run's published figures do not move | the hook returns the run's own reading untouched; the only other importer (`company/finance/bad_debt_provision.py`) takes two constants; nothing passes `signals_of` | **held, by construction** |

The money, summed over signal-read accounts with a realised figure:

| Read | n | realised | off | on |
|---|---|---|---|---|
| quarter-end | 132 | **GBP 0.00** | 223.90 | 494.88 |
| mid-month | 419 | 725.22 (1.4% of accounts carry it) | **773.31** | 1,908.10 |

The off arm is already close to the realised mid-month shortfall. The on arm is 2.6 times it.

## Why: two mechanisms, one tested

**D1, the label (tested, one variable).** `_learn_signals` resolves "the monthly step the signal
arrived in" from the signal's own date to the next month-end. Every collection in this world is
value-dated the 28th and observed 0-2 days later. So for a code 0, that step is the same calendar
month whose collection just failed, and the learned "outcome" is mostly the failure that raised the
signal. Learned P(miss | direct debit, code 0) at 2023-12-31: **238 of 296 = 80%**. Reading then
applies that P(miss) to the NEXT month, the first step of the forecast. The manual-missed signal has
the same shape: due date = bill + 14 = the 28th.

Pre-registered before it ran (`/var/tmp/e6ew/relabel/PREREG.md`, sha256 `cc9122c5...`), with one
change: the step resolved from the month-end of the signal's month instead. The first attempt was a
no-op. This box's multiprocessing start method is `forkserver`, so the workers re-imported the
unpatched module and returned byte-identical numbers. Forced to `fork`, then:

| | learned P(miss \| DD, code 0) | Q MAE on / off | M MAE on / off | worst book move |
|---|---|---|---|---|
| as built | 80% | 3.75 / 1.70 | 6.12 / 3.51 | 10.4% / 11.1% |
| step relabelled | **18%** (52 of 296) | **1.86** / 1.70 | **3.68** / 3.51 | 1.6% / 1.5% |

P7 (on-arm MAE falls at both read kinds), P8 (still above off at quarter-ends), P9 (still above
off mid-month): **all held**. The label accounts for most of the excess error. With it corrected,
the early warning is roughly neutral and slightly worse than the chain alone.

**D2, the guard (measured, not yet varied).** P1 rested on "a failed collection leaves its month
unpaid, so the account is in missed state 1 at month-end". That is false for **185 of 605** code-0
months (31%). The chain's month counts as paid when its calendar month's cash reaches half the
median bill. In 76 of the 185, a credit arrives on the same 28th as the failure. It is the world
settling an earlier failed collection: remittance `p24194` on 2016-05-28 for ACC-SYN-2016-012 is
March's returned amount. The rest are cash earlier in the month. A household one or two collections
behind that pays every month is therefore in state 0. The signal passes the guard, "code 0 again"
becomes readable (P3), and the quarter-end read moves (P1). On the quarter-end signal-read accounts
the realised 12-month shortfall is GBP 0: these households do pay.

## What it says, and what it cannot

- **The engine's lead over the chain is not worth wiring anywhere on this book.** As built, it
  more than doubles the error where it fires. With D1 fixed it is about neutral. The prereg's
  question, whether the lead is mid-month only, is moot: there is no lead to place.
- **It cannot say the signals are worthless in the real world.** This world's bad debt runs 5-7x
  below a GB supplier's (`553d7c855`). Its code-0 households also mostly settle the returned amount
  a month or two later. A world where they do not would give the signal more to predict. F11 points
  the same way: erring against the early warning is the safe direction.
- **One run, one seed.** The direction is stable across 37 and 113 dates and every signal kind (in
  `dig.py`, the on arm has the larger MAE in all 12 (read kind x signal x state at signal) cells). The size is one book's.

## Owed

1. **Fix D1 in `company/finance/cash_forecast_provision.py`**: learn each signal's outcome on the
   step the reading applies it to (the month after the one it is about). Use a control that fails
   on today's label: a code 0 whose own month misses and whose next month pays must learn `pay`.
   Keep it default off. Handed on as `e6-the-early-warning-learns-the-next-month-not-the-failed-one`.
2. **D2 is a definition question, not a bug yet.** Is a household that pays every month but runs a
   month behind in state 0 for early-warning purposes? The chain's answer is yes. Whether the
   signal should be guarded on the FIFO age of the oldest unpaid bill instead is for the fix's
   knowledge page to decide (K8), not for this grade.
