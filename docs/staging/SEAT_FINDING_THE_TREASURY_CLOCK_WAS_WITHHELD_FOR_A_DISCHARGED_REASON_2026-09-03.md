**Severity:** LATENT · **Lane:** E_finance_treasury · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing`

# The treasury clock was withheld for a reason three other modules had already discharged — and the control over that register could not let it be repaired

*Delivery seat, 2026-09-03, lane-0. Grades
`SEAT_PREREGISTRATION_WHETHER_THE_TREASURY_CLOCK_CAN_BE_REPAIRED_2026-09-03.md` (T1–T5), filed
before the repair was attempted and before any test was run against it. Continues act (c) of the
lane-0 direction and the "what follows" §7.2 of
`SEAT_FINDING_THE_OPENING_DD_ESTIMATE_WORKS_AND_NOTHING_PUBLISHED_CAN_SEE_IT_2026-09-03.md`.*

---

## 1. What the direction asked, and the answer

> *"Establish whether that is an accounting identity in `saas/reporting/annual_report.py` or a
> coincidence of this book."*

**It is an identity, it is not a coincidence, and it was already established in three places before
this turn started.** Measured, not assumed:

| subject | `treasury_end − treasury_start − net_margin` |
|---|---|
| the live published portfolio (`site/data/dashboard.json`) | **0.0** |
| `extract_portfolio` over the real run output | **2.9e-11** |

`simulation/run_phase2b.py:2618` is `treasury += rec["net_margin_gbp"]` and nothing else moves it.
`saas/reporting/annual_report.py:964-967` states the same and **refuses the 'banked' label by name**
as *"a label invented for a clock this world does not have"*. And
`simulation/settlement_clocks.reconcile_published_run_output` already runs a **live control** on
`starting + total_net == final`, called from `tools/run_annual_report.py:120`.

**T1 CONFIRMED. T2 CONFIRMED** (below).

## 2. The finding: a debt entry whose stated reason had been discharged elsewhere

`tools/generate_dashboard_data.py` withheld a clock from `treasury_start_gbp` and
`treasury_end_gbp`, giving this reason:

> *"a treasury BALANCE, not a margin — **its clock is 'banked'**, but the banked-clock definition for
> opening/closing balances **has not been written down anywhere a reader can check**, so stating it
> here would be an assertion"*

**Both halves were false by the time I read them.** There is no banked clock for this figure — one
module refuses that label by name — and the definition *was* written down, in the module that runs a
control on it. So the register withheld a label for a reason that had already been discharged, and
**nothing in the repository could notice**: the one-rule/many-implementations class `CLAUDE.md`
names, the same shape as the VAT rule.

The consequence for a reader is exactly what the lane-0 direction predicted. `treasury_end_gbp` was
published **beside** `net_margin_gbp`, with a clock chip on the latter and none on the former, as
though it were an independent cash fact. It is arithmetically that same number plus a constant.

**The repair.** `treasury_end_gbp` now carries `clock: "settled"`,
`derived_from: "net_margin_gbp"`, `cost_basis: "net_of_all_costs"`, and a note that says in the
reader's words what it is: *"Not an independent cash figure… it therefore cannot express payment
timing — no direct-debit or collection arrangement can move it."* `_check_derived_basis_parentage`
now holds that claim to its parent, so if net margin's basis moves and this does not, the **publish
fails** rather than the page quietly disagreeing with itself.

**T2 CONFIRMED.** `treasury_start_gbp` was *not* repairable the same way and stays declared: it is a
run input at t0 and nothing settled to produce it. I predicted that if I found myself giving it a
clock I had invented a label. I did not. Its reason is replaced by a true one, with the false one
quoted in place so the next reader can see what was wrong rather than only what is now right.

Published debt: **5 figures → 4**, which the gate prints on every publish.

## 3. The sharper finding: the control could not let the debt shrink

`test_the_superseded_allowlist_was_blind_to_five_live_figures` asserted

```python
assert set(unseen_by_old_rule) == set(_BASIS_DECLARED_UNLABELLED)
```

while its own docstring said the pin existed *"so a future pass can see the debt shrink"*. **The
equality made shrinking the debt impossible without a red.** Giving one figure the clock it had been
wrongly denied turned that test red — for the code becoming **more honest**.

That is R15's *control pinned to today's answer*, and `CLAUDE.md` states the shape exactly: *"goes
red when the code becomes more honest and stays green when the claim rots. That is exactly
backwards."* The register's own comment promised the debt was **"NON-GROWABLE"**; no assertion
anywhere held it to that. The equality gave the illusion of holding it, because a register that
cannot change at all also cannot grow.

**T3 CONFIRMED exactly. T4 CONFIRMED exactly** — one test red, twelve green, and the red was the
predicted one.

**The re-key.** Now keyed to the property the equality was reaching for: every figure the old
allowlist was blind to is **accounted for** — a label or a written declaration, never silence — and
the register may **shrink to nothing but never grow**. True before the repair, after it, and after
the remaining four are repaired. It also stops asserting that the suffixed key set is *exactly*
those five, which reddened on any properly-labelled addition; two other tests in the same file
already own that case, and the docstring now says so rather than leaving the next reader to wonder
what was dropped.

**T5 CONFIRMED by mutation, not by reading.** Three legs, each with a sole-witness mutation, run
under `python3 -B`:

| mutation | leg | result |
|---|---|---|
| a figure loses **both** its label and its declaration | `unaccounted` | **KILLED** |
| a **new** figure parked as debt instead of labelled | `grown` | **KILLED** |
| the portfolio stops emitting a pinned figure | `vanished` | **KILLED** |

Null control passes before and after all three. The re-keyed assertion is not a tautology — the
thing the pre-registration said must not happen.

## 4. One observation, bounded, that is not a defect

`reconcile_published_run_output`'s docstring calls the identity *"the arithmetic a reader of
`site/data/supplier.json` can do in their head"*. That file's `portfolio_summary` publishes
`final_treasury_gbp` and `total_net_gbp` but **not** `starting_treasury_gbp`, so a reader of that
file cannot in fact do it. The control itself is fine and correctly wired — it runs upstream on the
run output, which carries all three, and it fails closed on absence (I confirmed this by mis-aiming
it at the publish block and getting a named refusal rather than a pass). **Recorded as an
observation about one file's key set, not as a finding**, because I have not established that
`supplier.json` is meant to be self-checkable. Whoever picks that up should settle that question
first.

## 5. What follows

1. **Four figures still carry no clock** — `cost_to_serve_gbp`, `gross_margin_gbp`,
   `net_after_cts_gbp`, `treasury_start_gbp`. Three have reasons that may or may not still be true;
   this turn shows how cheaply a register's reason goes stale while reading as caution. Someone
   should re-read the other three against today's code, which is a bounded and specified job.
2. **`BASIS_ORDER`'s three unreached rungs** (`metered_history`, `customer_declared`,
   `tdcv_typical`) are still unreached from the only live call site — carried over unchanged from
   §7.3 of the DD finding, and not touched here.
3. **The `treasury` name itself.** Labelling it is not the same as renaming it, and a figure named
   "treasury end" that is cumulative net margin is still reading as cash to anyone who does not open
   the basis block. The label is the honest minimum; the name is a separate decision and it is the
   director's, not mine.
