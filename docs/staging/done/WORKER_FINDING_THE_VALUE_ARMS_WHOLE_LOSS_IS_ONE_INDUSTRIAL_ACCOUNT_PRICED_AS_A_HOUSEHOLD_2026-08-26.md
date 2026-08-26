# The value arm's whole loss is one industrial account priced as a household

**Severity:** HIGH — it is 99.5% of the number the thesis is scored on
**Lane:** C_company / H_harness
**Class:** a model applied outside its calibrated domain, because two subsystems disagreed
about how many segments exist
**Status:** MEASURED AND FILED. The diagnostics that found it are landed; the one-line
repair is deliberately NOT in this commit — see "Why the fix is filed and not applied".

## The headline is one account

`docs/observability/value_cycle_ab.json`, run 2026-08-26. The control reproduces
bit-identically between runs (net £1,145,681.029513), so the only variable is the arm.

`margin_movers` over all 259 accounts, realised whole-life margin, each from its own arm's
settled records:

| account | control | value arm | delta |
|---|---|---|---|
| **C_IC3** | £195,317.43 | £101,003.25 | **−£94,314.19** |
| C_IC1 | £531,323.45 | £500,194.97 | −£31,128.48 |
| C_IC2 | £365,689.29 | £381,042.87 | +£15,353.59 |
| C9 | £1,502.29 | £6,746.70 | +£5,244.41 |
| …255 more | | | |

**`concentration_top_n_share_of_absolute_movement` = 0.9968.** Net delta −£94,813.70, of
which **C_IC3 alone is −£94,314.19 — 99.5%.**

So "the value arm loses £93,555" is a statement about **one industrial customer**. Every
domestic account in the book could be deleted from the experiment and the headline would
barely move. `n = 1` is not a thesis, and until this run the artefact could not say so.

## The churn story was a red herring, and the diff killed it

`churn_roster_diff`: the value arm loses C1_2, C3, C6, C7 and SAVES PROS-2019-0003 — four
and one, which the net "+3" had hidden. **Not one of the five I&C accounts churns
differently.** Those four are worth £266.85, £975.36, £4,405.10 and £887.90 — £6,534 in
total, and three of them are BETTER off under the arm than the control. The churns are
noise.

The loss is not customers leaving. It is one customer **staying, at the wrong price**.

## The mechanism, observed rather than inferred

`company/pricing/value_based_renewal.py:869`, the only production caller of the arm:

```python
segment = "resi" if is_domestic else "SME"
```

Its docstring gives the reason, and the reason is sound for the thing it was thinking
about: *"the door already carries that boolean and `cost_to_serve_for_period` accepts
exactly two segments, so mapping here keeps ONE vocabulary for one fact instead of two
that can disagree."*

But `company/crm/churn_model.estimate_churn_probability` branches **three** ways, and its
I&C arm exists precisely to switch bill-size-driven churn OFF:

```python
IC_BILL_STRESS_SENSITIVITY = 0.0    # I&C: rate-driven churn, not bill-size-driven
BILL_STRESS_SENSITIVITY   = 0.25
BILL_STRESS_THRESHOLD_GBP = 3000.0
```

The stress term is `sensitivity × max(0, annual_bill / threshold − 1)`. C_IC3 consumes
**3,936,105 kWh/year** — an annual bill in the hundreds of thousands against a £3,000
threshold. Measured directly, calling the company's own estimator on a C_IC3-shaped
account:

| offered margin | SME path (what the arm gets) | I&C path (unreachable) |
|---|---|---|
| £0.50 (the floor) | **1.0000** | 0.0288 |
| £2.00 (the control) | **1.0000** | 0.0288 |
| £20.00 | **1.0000** | 0.2753 |
| £46.00 | **1.0000** | 0.8094 |

The same shape at domestic volume (4,004 kWh) gives 0.0288 on the resi path — identical to
the I&C answer. **The curve is correct for households and saturates at industrial volume.**

So on the only path a live run uses, the arm believes a 3.9 GWh customer is **certain to
leave at any price it could offer, including a price BELOW what it already charges**. With
`p_retain = 0` flat across the whole candidate grid, `expected_value_gbp` has nothing to
maximise and the search falls to the **floor — £0.50/MWh, below the control's £2.00**. That
is `endpoint_at_floor: 16` in the decision shape, and on 3.94 GWh a £1.50/MWh giveaway is
~£5,900 a year, compounding to the £94,314 above.

## Why this survived the previous two repairs

`8b450a839` fixed the rate basis and the ceiling and the loss moved 6.4% (−£118,252 →
−£110,731). It could not have fixed this: `p_leave` is **saturated at 1.0**, so correcting
which rate is compared changes nothing a saturated term will notice. The same is true of
the standing charge. Both repairs were real and both were downstream of a term that had
already lost all its information.

`tools/couple_value_based_pricing.py` never saw it because the probe passes the account's
**true** segment (`record.get("segment") or "resi"`), so it reaches the I&C branch and
reports C_IC3 at £46.00/MWh, endpoint-unbound. Same module, same book, different
information — the SECOND instance of the class `8b450a839` named on its first.

## Why the fix is filed and not applied in this commit

The repair is one line: pass the account's real segment instead of a two-valued
`is_domestic` boolean, and give `cost_to_serve_for_period` its own mapping rather than
making the churn model share a vocabulary sized for costs.

**I found this by chasing a loss, and I already know which way fixing it moves the
headline** — the arm currently gives away margin on its three largest accounts, so
repairing it will very likely turn the thesis's headline number positive. R12 exists for
exactly this moment. So the mechanism, the evidence and the expected direction are recorded
HERE, in advance, and the fix is a separate, explicit act rather than something that
arrives inside a diagnosis commit with the number already moving.

Stated plainly for the record: **this is a wiring defect and would be one whichever way it
moved the money.** A supplier whose churn model has an industrial branch, and whose renewal
desk cannot reach it, is wrong about its customers regardless of the P&L. But the honest
order is to say so before the number changes, not after.

## What remains open

1. **The one-line repair**, and a re-run to measure it. The prediction is on the record
   above.
2. **`margin_movers` reports `segment: null`** on the settled-records basis, because
   `all_records` carries no segment field. The accounts are identifiable by id, so this
   cost nothing here, but a book without `C_*` naming conventions would be harder to read.
3. **Whether any OTHER company model is applied outside its calibrated domain by the same
   route.** `cost_to_serve_for_period` takes two segments and the churn model takes three;
   nothing checks that a caller's segment vocabulary matches the callee's. That is the
   class, and it is bigger than this instance.
