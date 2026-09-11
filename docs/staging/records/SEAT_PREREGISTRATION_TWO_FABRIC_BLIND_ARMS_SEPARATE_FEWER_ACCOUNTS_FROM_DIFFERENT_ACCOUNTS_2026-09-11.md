**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# PRE-REGISTRATION — two fabric-blind arms, to separate FEWER accounts from DIFFERENT accounts

**Filed 2026-09-11, delivery seat, BEFORE either arm was run.** The probe that fixed each arm's
settled book had already run (it is seconds, not minutes, and is reproduced below); **no P&L figure
from either arm existed when these predictions were written.**

Follows `SEAT_RESULT_P6_THE_CHOSEN_BOOK_IS_2_45_PERCENT_WORSE_ON_GROSS_MARGIN_2026-09-11.md`, which
graded P6 as HOLDING at −2.45% and then said plainly what it could not do:

> **I cannot say how much of the −2.45% is FEWER accounts and how much is DIFFERENT accounts.**
> Two things moved together: the book shrank from 91 to 83 settled accounts, and the accounts are
> drawn from different homes. One run cannot separate them.

---

## Why the obvious third arm is not enough on its own

The drawn item names one arm: *the count cull truncated to 83 accounts at the same customer-year
spend*. **The two halves of that sentence cannot both be had.** The systematic cull selects by
POSITION; forcing it to 83 accounts necessarily changes what it spends, because the cost of a
position is its tenure and the rule cannot see tenure. Measured, not assumed — the truncated cull
lands at **1155.4 customer-years**, 3.3% under ARM B's 1194.9. So a count-matched blind arm is
budget-mismatched, and any gap it shows is two things again.

**The repair is a SECOND blind arm matched on the other axis.** Together they bracket ARM B:

| | accounts | customer-years | sees fabric? | matched to ARM B on |
|---|---:|---:|---|---|
| **ARM A** cull (measured) | 91 | 1195.1 | no | — (the baseline) |
| **ARM B** chosen (measured) | 83 | 1194.9 | **yes** | — (the subject) |
| **ARM C** cull truncated to 83 | **83** | 1155.4 | no | **count, exactly** |
| **ARM D** chooser, tenure axis only | 89 | **1199.9** | no | **budget, to 0.4%** |

If both blind arms sit on one side of ARM B, the fabric composition is doing the work and the
account count is not. If ARM B sits between them, the count is.

**ARM D is the arm I did not expect to be able to build.** Stripping `CHOICE_AXES` to
`("customer_years",)` leaves the whole shipped mechanism — the `k` bisection, the year cover, the
NNLS weight fit, the headroom invariant — and removes only what the axes can SEE. It is therefore
also the control on a confound nobody has named yet: that the difference between ARM A and ARM B is
the *selection machinery* rather than the fabric information.

**What the probe already refutes.** ARM D lands at 89 accounts and 1199.9 customer-years — not at
83. So the shrink from 91 to 83 is **not** the `customer_years` axis concentrating the budget on
longer-tenured accounts, which is the explanation the P6 result doc offered ("the chooser spends the
same customer-year budget on fewer, longer-tenured accounts"). That sentence is now doubtful before
any P&L has been measured, and the arms below will settle it.

## The predictions

Reference figures, from the graded and reproduced ARM A / ARM B pair:

```
              gross margin    cy      accts    £/customer-year   £/account
ARM A cull    383,688.97   1195.1      91          321.05         4,216.36
ARM B chosen  374,295.73   1194.9      83          313.24         4,509.59
                                                   −2.43%          +6.95%
```

**PC1 — the cheap control, and it is here to fail loudly if the harness is wrong.** ARM C's gross
margin is BELOW ARM A's £383,688.97. A book with fewer accounts and a smaller budget that earned
more would mean the arm did not run what it says it ran.

**PC2 — THE ATTRIBUTION, and the one this whole exercise is for.** ARM C's gross margin **per
committed customer-year** exceeds ARM B's £313.24/cy by **more than 1.0%** — that is, ARM C's gross
margin is above **£365,586**. *Holding means the blind book earns more per customer-year than the
chosen book at the IDENTICAL account count, so the −2.45% is a COMPOSITION effect and "fewer
accounts" does not explain it. Failing means the count is doing the work and the chooser is
innocent.* I do not know which.

**PC3 — the mechanism control.** ARM D's gross margin is within **±1.5%** of ARM A's £383,688.97
(i.e. £377,934–£389,444). ARM D is fabric-blind at nearly ARM A's size and ARM B's budget, so it
should reproduce the cull. **If PC3 FAILS, the A-vs-B comparison is confounded by the selection
machinery itself and P6's −2.45% cannot be read as a statement about the homes at all.** That would
be the most consequential outcome on this page and it is the reason ARM D is being run.

**PC4 — the bad-debt leg, and the first prediction ever filed about it.** ARM C's and ARM D's bad
debt are BOTH below ARM B's £14,400.86. The P6 result recorded +23.34% on a book 6.37% smaller and
graded nothing, because no prediction had been filed: *"the chooser deliberately pulls in tails, and
on this world the tails pay worse."* If that reading is right, two fabric-blind books cannot
reproduce it. If either blind arm lands at or above ARM B's bad debt, the tails explanation is
wrong and the +23.34% belongs to something else.

**PC5 — determinism, across the process boundary.** Each arm's full run reproduces its own probe
exactly: ARM C settles **83** accounts at **1155.4** cy, ARM D settles **89** at **1199.9** cy, both
at base seed 20260724. The seed-42 cross-check resolves without error in both arms.

## What is fixed before the answer

* **The run path is byte-identical to the HEAD P6 was measured at.** `git diff 3957ba848..HEAD --
  simulation/ company/ saas/ tools/run_annual_report.py interfaces/` is **empty**; only docs, the
  site feed and its generator moved. ARM A and ARM B's pounds are valid comparators at this HEAD,
  and the probe independently reproduces ARM B's book (83 settled / 1194.9 cy) to the decimal.
* **Both arms run under `SIM_FAST_MODE=1`,** identically to ARM A and ARM B. As P6 recorded, the
  absolute pounds are therefore not comparable to `docs/reports/run_output_latest.json`; every
  claim here is a claim about a DIFFERENCE between arms and is graded as one. **Nothing from this
  page goes on a public surface as a headline.**
* **Concurrency is already discharged**, by measurement rather than argument: `8dcffd8d1` re-ran
  ARM A alone and reproduced all five concurrent figures to the penny. ARM C and ARM D therefore
  run concurrently without a caveat.
* **The harness is `/var/tmp/p6_arm3.py`**, outside the repository for the reason the P6 harness
  gave — it is a measurement and not a control, and an orphan module in `tools/` would be worse to
  leave behind. It is reproduced in full in the result that grades this.

## How this can come out badly for me

The outcome I would find hardest to write up is **PC2 failing while PC3 holds**: a clean mechanism
control alongside a count effect that fully explains the −2.45%. That would make the P6 result doc's
central sentence — *"the right sentence is that it is smaller at the same cost, and the total
follows the size"* — correct, and this pre-registration's doubt about it wrong. It is written down
here so that it cannot be quietly re-described afterwards.
