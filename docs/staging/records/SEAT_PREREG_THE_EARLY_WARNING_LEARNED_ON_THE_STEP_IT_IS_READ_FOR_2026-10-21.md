**Severity:** RECORDED · **Lane:** E_finance_treasury · **Epoch:** 4 · **Atom:** `E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build` · **Direction item:** `e6-the-early-warning-learns-the-next-month-not-the-failed-one`
**Knowledge:** bad-debt-provisioning -- `docs/market_research/bad_debt_provisioning.md`, "Early warning in the forward-cash-forecast provision", choice 6

# Pre-registration: the early warning learned on the step it is read for

**Graded 2026-10-21 18:4x:** P13 held; P10, P11 and P12 refuted. Predictions kept as written; the
grade is at the foot.

Written 2026-10-21 18:13 BST, after the fix is built and tested on synthetic books and BEFORE it is
run over the captured book (`/var/tmp/e6ew/out/capture.pkl`, the default run at `cda47a346`).

**The change (one design, two parts, so not one variable against the relabel probe).** A signal now
carries the month it is about (the returned collection's value date, the missed bill's due date).
It is read only by a forecast whose first step is that month (lag 0) or the next (lag 1), and it is
learned on that same step, from an account in missed state 0 at the step's START (for lag 1: the
about-month's end), not at the signal's arrival. The relabel probe (`/var/tmp/e6ew/relabel/`)
changed only the step. This also changes the learning population to the reading's: the households
whose returned month already aged the chain are no longer in the lag-1 cell. That is the D2 question.

**Run:** `/var/tmp/e6ew/grade.py` unmodified, from this worktree, against the module as built here,
into `/var/tmp/e6ew/fix/grade.json`; `readout.py` over it. Same 150 dates.

| # | Prediction |
|---|---|
| P10 | Learned P(miss \| direct debit, code 0, lag 1) at 2023-12-31 is below the relabel's 18%, under 10%: the guard keeps only the ~31% of code-0 months that counted paid, and those households pay. |
| P11 | On-arm MAE on signal-read accounts is at or below the relabel's (Q 1.86, M 3.68) at both read kinds. At quarter-ends it falls BELOW the off arm (1.70), because the realised shortfall there is GBP 0 and the learned lag-1 P(miss) is below the chain's state-0 P(miss). Mid-month: within 5% of off (3.51), direction not predicted. |
| P12 | Signal-read account-dates fall by no more than 5% from the as-built grade at either read kind (the read guard is unchanged; only lag >= 2 signals, a February return seen in March, drop out). |
| P13 | The harness control holds: the per-account decomposition equals `book_provision` on both arms at its 4 dates. |

A refuted P11 at quarter-ends does not block landing: the fix is about what the cell MEANS (learned
on the step it is read for), which the synthetic control establishes. The grade says what the
corrected lift is worth on this book.

*Amended 18:2x, before any result was read: `grade.py` keyed a counter by the value `signal_at` returns, now a `Signal` tuple, which JSON cannot write; the run uses `/var/tmp/e6ew/fix/grade_fix.py`, the same script recording `sig.kind`. Predictions unchanged.*

## Graded (2026-10-21; `/var/tmp/e6ew/fix/grade.json`, `readout.txt`)

| # | Result | |
|---|---|---|
| P10 | lag-1 P(miss \| DD, code 0) at 2023-12-31 is **19 of 87 = 22%**, not under 10%. The households one collection behind that pay every month miss the next month about one time in five. The lag-0 cell, the failed month, is 235 of 280 = 84%, as the as-built label read it. | **refuted** |
| P11 | quarter-end on **1.95** (n 120) vs off 1.81; mid-month **3.72** (n 416) vs off 3.51. Neither at or below the relabel, not below off at quarter-ends, 6% above off mid-month. | **refuted** |
| P12 | quarter-end reads fall 157 to **143 (-9%)**; mid-month unchanged (480 and 472 learned, identical). All 14 drops are at a 31 March: February's 28th collection, returned on 1-2 March, is lag 2 there. February's short month was not in the 5% estimate. | **refuted** |
| P13 | decomposition equals `book_provision` per account on both arms at all 4 control dates | **held** |

The read population changed (P12), so the MAEs above are not like-for-like with the relabel's.
Restricted to the account-dates every arm reads (120 quarter-end, 415 mid-month):

| | off | as built | relabel probe | fixed |
|---|---|---|---|---|
| quarter-end MAE | 1.81 | 3.89 | 1.94 | **1.95** |
| mid-month MAE | 3.52 | 6.13 | 3.69 | **3.73** |

Mid-month money on those 415: realised GBP 725.22, off 766.14, fixed 856.13. The fix removes the
error D1 caused. Changing the learning population to the reading's (D2) moved nearly nothing,
because the D2 households miss their next month at 22%, more often than the chain's state 0.
On this book the early warning stays about neutral, slightly worse than the chain alone. Default off stands.
