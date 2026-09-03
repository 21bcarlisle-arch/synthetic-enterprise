**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing`

# Pre-registration — what giving the direct debit an estimate must show

*Delivery seat, 2026-09-02, lane-0. Written BEFORE the estimator exists and BEFORE any run of it
was read. Atom `D_opening_dd_seasonal_sizing`.*

The director's correction, 2026-09-01, verbatim:

> *"There's no such thing as a half-month direct debit — an annualised plan divides estimated annual
> cost by twelve whatever the start date. The real defect is that the DD is only as good as the
> estimated annual consumption behind it: when that estimate is wrong the account drifts into credit
> or debit, and the correction arrives later as a change the customer didn't expect."*

---

## The state at HEAD, measured this orientation

* `company/billing/dd_review_runner.py:155` — `standing_dd = seq[0][1]  # initial estimate = first
  issued bill`.
* `simulation/dd_balance_book.py:243` — `standing = seq[0][1]`, the **same artefact**, in a second
  module, describing itself as "exactly dd_review_runner's … initial mandate sizing".
* `grep -rn annual_consumption_kwh company/billing/ saas/` returns only `exit_fee.py` and
  `renewal_engine.py`. Nothing in the DD path estimates anything.

**Two implementations of one defect.** That is the VAT shape and it is why a control keyed to only
one of them would be worthless. Both are in scope.

---

## Predictions, filed before the run

**P1 — the opening DD moves for essentially every customer.** The first issued bill is a *period*
bill; an annualised plan is `estimated annual cost / 12`. These agree only where the first bill
happens to equal one twelfth of the year. I predict **> 90%** of customers see a different opening
DD, and the direction is **not** uniformly one way: a first bill falling in winter over-sizes the DD,
one falling in summer under-sizes it.

**P2 — the first-year review population changes, and the variance distribution narrows.** Today's
first review compares a year's actual spend against `first_bill × 12`. Against a proper annualised
estimate the variance should be *smaller in absolute value* on average, because the estimate is
aimed at the year rather than at one month. I predict the mean |variance| at window 0 **falls**.
If it does not fall, the estimator is not better than the accident it replaced and I must say so.

**P3 — a population will have no estimate at all, and the honest count is not zero.** Any customer
for whom no EAC, no declaration and no metered history is reachable gets `None`, not a number.
I predict this count is **> 0** and I will publish it rather than fill it.

**P4 — the seasonal balance amplitude changes sign for some customers.** `dd_balance_book` builds
credit through summer and draws it down through winter *given a standing DD*. Change the standing
DD and the peak held-credit liability moves. I predict the portfolio held-credit figure moves by a
**material** amount (>5%), and I will not treat "it barely moved" as reassurance — that would mean
the opening estimate is not load-bearing, which would refute the premise of this whole item.

**P5 — I expect the published record NOT to establish the arithmetic.** I predict SLC establishes
the *duty* (best and most current information) and the *review*, but names no formula converting an
annual estimate into a monthly amount, and no ±5% threshold. If so, `/12` is the director's
practitioner statement, cited as such, and the ±5% currently attributed to "SLC 27B" is a citation
that cannot be checked.

---

## What must NOT happen

1. **No ground-truth annual consumption may reach the estimator.** The estimate is built only from
   what a supplier holds: the registration EAC/AQ, the customer's declaration, metered history, and
   the published TDCV where none of those exist. If I find myself passing the household's true
   annual usage in, the work is wrong and stops.
2. **No number invented to fill a slot.** Every constant carries its origin or the code carries
   `None` with a named reason.
3. **No control keyed to today's answer.** The control must go red on the *property* — "the standing
   DD was taken from an issued bill" — not on a current figure.
4. **The published DD review surface must not silently go to zero.** A producer turning fail-closed
   that leaves its consumers empty is a regression dressed as rigour. If the estimate cannot be
   supplied to a caller in this increment, the surface must say the count and the reason, on the
   page, not in a footnote.

## How I will know I was wrong

If P2 fails — mean |variance| at window 0 does not fall — the annualised estimate is not better
than the first-bill accident on the only measure that matters, and the correct response is to
publish that, not to re-cut the statistic until it agrees.
