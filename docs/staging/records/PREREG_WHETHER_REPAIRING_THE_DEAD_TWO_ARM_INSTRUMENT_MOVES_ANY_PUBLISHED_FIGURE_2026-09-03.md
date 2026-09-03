**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing`

# Pre-registration: whether repairing the dead two-arm instrument moves any published figure

Written **before** the instrument was re-run, at HEAD `a298e7a9f`, 2026-09-03, by the delivery seat
working the claim `the-dd-estimate-changes-no-published-number`.

## What is already known (measured, not predicted)

Established before this file was written, so **not** predictions:

- `python3 -m tools.dd_opening_arms` at HEAD raises
  `TypeError: estimate_annual_consumption() got an unexpected keyword argument 'metered_annual_kwh'`
  at `tools/dd_opening_arms.py:130`. The instrument that answers this claim **cannot run**.
- Cause and order. `e07449df5` (04:30) landed the instrument. `4e1502524` (06:09) narrowed
  `estimate_annual_consumption` from four parameters to two, removing `metered_annual_kwh` and
  `declared_annual_kwh`. The narrowing was right; nothing re-ran the instrument under it.
- `tests/tools/test_dd_opening_arms.py` is **6 passed in 0.06s**. No control touches `run()`,
  `_basis_and_rate_by_customer` or `estimate_opening_by_customer`, so the instrument being dead is
  invisible to its own suite.
- `tools/dd_opening_arms.py` is the **only** broken caller: the sole other tree hits for the two
  removed names are `dd_review_outcome.py`'s own docstring and the control that keeps them removed.
- The published feed `site/data/dd_opening_arms.json` and the artefact
  `docs/reports/dd_opening_arms.json` are committed and were produced at `e07449df5`, i.e. **before**
  the narrowing. They are frozen output of a producer that can no longer run.

## The predictions

**P1 — no figure moves.** Both removed arguments were passed `None` at the only call site, and
`estimate_annual_consumption` treats a non-positive/absent value as establishing nothing. So the walk
was already `REGISTRY_EAC → TDCV_TYPICAL` before the narrowing and is the same walk after it.
Repairing the call therefore changes **no number** in `docs/reports/dd_opening_arms.json`.

*Refuted by:* any numeric leaf in the re-run artefact differing from the committed one.

**P2 — `basis_split` stays exactly `{"registry_eac": 142}`.** Same reason, stated separately because
it is the one field that reads the precedence directly and would move first if P1 is wrong.

*Refuted by:* a different count, or any second key appearing.

**P3 — the published basis block is now FALSE, and falsifiably so.** `publish_view`'s `basis_note`
says "SLC 27.15's **four** sources … **three of the four** are unreached by the live call site", and
`site/capabilities/index.html` renders a four-row split printing `our own meter reads 0` and
`what the customer told us 0`. After `4e1502524` those two rungs are not *unreached*: they are
**excluded by construction**, with no parameter left to arrive through, for two reasons of
**different kinds** — `METERED_HISTORY` definitionally (the account is being opened; 0 of 257 supply
points hold prior metering of ours) and `CUSTOMER_DECLARED` as a world gap that lifts the day the
registration flow carries a declaration. A rendered `0` says the supplier looked and found none.

*Refuted by:* `BASIS_ORDER` still having four members, or `NOT_REACHABLE_AT_OPENING` being empty.

**P4 — the repair must not be keyed to today's answer.** The stale note is stale because the count
"four" was authored as prose. If the replacement hard-codes "two" it will rot the same way the day a
rung returns. The published block must be **derived from `BASIS_ORDER` and
`NOT_REACHABLE_AT_OPENING`**, so that returning `CUSTOMER_DECLARED` to the precedence changes the
page without anyone editing the page.

*Refuted by:* a literal rung count, or a literal rung name, surviving in `publish_view` or in the
page's JavaScript.

## The constraint this work must not violate

The repair may not touch `company/billing/annual_consumption_estimate.py` or
`company/interfaces/dd_review_outcome.py`. The narrowing was correct and is held by
`tests/company/billing/test_the_declared_precedence_is_the_walked_one.py`; the defect is entirely on
the instrument and the surface. If the repair finds itself widening the door's signature back, it has
misdiagnosed which side was wrong.

*Discharged by:* `git status --porcelain` over both paths, pasted into the finding.
