**Severity:** LATENT · **Lane:** B_commercial

# `by_billing_account` is built from the seed roster alone, so it names 13 accounts of a book of 80 — and every consumer that walks it inherits the truncation

**Found by:** the R4 diagnosis of EP1's coupled gap, 2026-08-24 (worker tick, LANE 1 BUILD on
`EP1_clv_three_horizon`, pass 16). Not looked for. The gap reading came out BIT-IDENTICAL to the
one taken four passes earlier on a book a sixth the size, and this is why.

## Observed, with evidence (R9) — measured, not read

`saas/reporting/annual_report.py:771` builds the table by iterating `CUSTOMERS`:

```python
for cid, c in {c["customer_id"]: c for c in CUSTOMERS}.items():
```

`CUSTOMERS` is the hand-authored SEED roster. Every neighbouring population in the same run
artefact is built over `CUSTOMERS + SUCCESSOR_CUSTOMERS + DRAWN_CUSTOMERS` — `_build_clv_snapshots`
(same module, line 143) passes exactly that triple to `build_cost_to_serve`, and
`churned_billing_accounts` is accumulated in `simulation/run_phase2b.py`'s term loop over whatever
customers actually settled.

Measured on `docs/reports/run_output_latest.json` as it stands after the 2026-08-24 20:38 run:

| population in the SAME artefact | accounts |
|---|---|
| `by_billing_account` | **13** |
| `per_customer_lifetime` | 80 |
| `clv_snapshots`, distinct accounts ever valued | 72 |
| `churned_billing_accounts` | 22 |
| `three_horizon_clv.accounts` (EP1's own published table) | 75 |
| `site/data/customers.json::customer_count` | 75 |

All 13 rows are the seed ids (`C1`..`C9`, `C_IC1`..`C_IC4`). Not one `PROS-*` account has a row.
The drawn book settles from 2021 (`generator_draw_wiring` activation, 2026-08-13), so this is a
table that stopped growing when the book started.

## What it cost, where it was actually measured

EP1's coupled-gap harness (`tools/couple_clv.py`) walked this table to build its population, and so
scored the estimator on **5 accounts where 19 were available** — every one of the 14 it could not
see was a drawn customer who had lived, been valued at a year end, and left. Same artefact, the two
population sources:

| | counted | available | gap |
|---|---|---|---|
| walking `by_billing_account` | 5 | 13 | 3.7058 |
| walking the union of the run's own populations | **19** | **80** | **2.5955** |

That is repaired in `tools/couple_clv.py` under the same tick, and the repair is a **no-op** on the
older committed artefact (5 counted, gap `1.7620866651009222`, bit-identical) — which is the check
that it un-pins the population rather than redefining the metric.

## Why this is filed rather than fixed

`saas/reporting/annual_report.py` is outside `EP1_clv_three_horizon`'s `file_scope`, and this table
has **other consumers** that were not part of the drawn work (SELF_INTERRUPT_DISCIPLINE):

* `tools/generate_customer_data.py:277` — resolves each published customer row's CLV and churn off
  `bba`, publishing `null` where no row exists. `site/data/customers.json` currently carries 75
  rows and **0** with a non-null top-level `clv_gbp`.
* `tools/generate_customer_sample.py:79`
* `tools/structural_blank_guard.py:88` — its doctrine note names `by_billing_account` as the SOURCE
  side of the published/source key pair.

`inferred` (R9), and the reason this is LATENT rather than BLOCKING: a widened table would give
those consumers 67 more rows, which is a change to a published surface and moves published figures
(`highest_clv`/`lowest_clv`/`avg_clv_gbp` are all computed from this dict at line 800). Whether any
currently-published figure is WRONG as opposed to narrow has not been measured here, and saying so
would be guessing. What IS measured is that the table's population disagrees with every sibling
population in its own artefact by a factor of six.

## The repair, and the class question (R10)

The instance repair is the triple: iterate `CUSTOMERS + SUCCESSOR_CUSTOMERS + DRAWN_CUSTOMERS`, as
`_build_clv_snapshots` in the same module already does. It lands with the before/after of
`highest_clv`, `lowest_clv`, `avg_clv_gbp` and the published customer rows stated (R14), because
each is a published figure.

The CLASS is the interesting half and an instance fix will not close it: **a run artefact publishes
several populations of the same accounts, derived from different rosters, and nothing checks that
they agree.** `enterprise_value_account_count` vs `by_billing_account` is already filed as its own
one-account version of this
(`WORKER_FINDING_THE_BOARDS_ACCOUNT_COUNT_AND_ITS_OWN_ACCOUNT_TABLE_DISAGREE_BY_ONE_2026-08-19`);
this is the same shape at 67 accounts. The control that would catch the family is a
population-reconciliation check over the run artefact — every account-keyed table's key set
compared against the run's own roster, with each intended difference named and frozen — not a
widening of one loop.

## What discharges this document

The table built over the full roster, with the before/after of the four published figures above
stated and verified on the rendered surface (R11); and the class control above, so that the next
table to fall behind its own book fails rather than being found by a gap reading that did not move.
