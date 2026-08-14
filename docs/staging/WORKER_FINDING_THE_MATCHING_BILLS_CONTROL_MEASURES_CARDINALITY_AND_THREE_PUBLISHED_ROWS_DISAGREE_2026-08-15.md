# FINDING — the meter seam is computed twice, the control named for their agreement measures cardinality instead, and three published rows disagree today

**Severity:** BLOCKING · **Lane:** D_billing_metering · **Disposition:** QUEUED (not fixed on sight)

**Atom:** `EP8_adapter_dcc_duis` (LANE 3 idle draw, DISCOVER/FRAME, 2026-08-15)
**Class:** a control's name asserts a per-row AGREEMENT between two independently computed
streams; its subject is the CARDINALITY of one of them, so every disagreement of equal
length passes. The streams were believed to agree by construction ("the identical seed
means the two always agree") and one of them has an override the other does not.

Full derivation and every number:
`docs/design/simplifications/EP8_adapter_dcc_duis.yaml` (finding 2).

## The two computations

One run computes the same meter-read decision twice, from the same seed:

| # | call site | product |
|---|---|---|
| 1 | `simulation/run_phase4c_on_phase2b.py:236` → `simulation/meter_reads.py::generate_meter_read_log` | the published `meter_read_log` (1,600 rows) |
| 2 | `company/billing/monthly_bill_assembly.py:406` → `SimulatedReadFeed.read_for` | the bills customers are charged on (1,600 rows) |

`company/billing/monthly_bill_assembly.py:381-388` states the premise in its own words —
*"computed here a second time on purpose (additive-first, no change to meter_reads.py or
its own call site) … the identical seed means the two always agree"*. The seed is
`random.Random(f"meterread_{customer_id}_{period_end}")` (`simulation/meter_reads.py:135`).

**The premise is false today.** Call site 2 has an override call site 1 does not:
`monthly_bill_assembly.py:412-424` forces a churned account's final bill onto
`final_read_for(...)` (status `"actual"`) under SLC 21B. `generate_meter_read_log` has no
such branch, so the published read log keeps saying `estimated` for that period.

## Measured, on the live published artefacts

`docs/reports/run_output_latest.json` (mtime 2026-08-14 23:37:37, 4,155,614 bytes), joined
on `(customer_id, period_end)` — 1,600 keys, all distinct, zero unmatched rows on either side:

| `billing_basis` (bill) | `status` (read log) | rows |
|---|---|---|
| actual | actual | 1,131 |
| estimated | estimated | 466 |
| **actual** | **estimated** | **3** |

The three, all `observed-with-evidence`:

| customer | period_end | bill basis | log status | log estimate kWh | billed kWh | bill £ | log `consecutive_estimated_count` |
|---|---|---|---|---|---|---|---|
| C5 | 2020-12-29 | actual | estimated | 1,961.88 | 2,015.82 | −788.97 | 11 |
| C6 | 2024-03-29 | actual | estimated | 2,342.48 | 2,346.81 | 1,484.80 | 4 |
| C3 | 2020-06-29 | actual | estimated | 202.82 | 191.21 | 37.44 | 9 |

All three are the **final bill of a churned account**. The run has 5 churned billing
accounts; the other 2 already resolved `actual` and needed no override. So **every override
that fired produced a divergence — 3 of 3, not 3 of 1,600.** The rate is 100% of the
mechanism, and it will scale with churn, not stay at three.

Two consequences beyond the status field itself:

1. `site/data/dashboard.json` publishes this stream at `customers.meter_read_log`, 1,600
   entries — so the diverging copy is in published data, not only in an internal report.
   (`observed`: no site template renders it; grep of `site/**` for `meter_read_log` in
   `.js/.html/.jsx/.ts` returns nothing. It is published data that is currently unrendered.)
2. The published `consecutive_estimated_count` for those rows (11, 4, 9) is the count the
   bill's own actual read reset to 0. Anything counting estimated-billing runs off the log
   rather than off `billing_basis` will overstate them for exactly the customers whose
   accounts closed.

## Why the control could not see it

`tests/simulation/test_run_phase4c_on_phase2b.py:180` is named
`test_main_produces_meter_read_log_matching_bills` and its comment says *"every bill the
full pipeline produces must have a corresponding meter-read event"*. Its three assertions:

```python
assert len(result["meter_read_log"]) == len(result["bills"])       # cardinality
assert statuses <= {"actual", "estimated"}                          # value domain
assert all(entry["delay_days"] >= 0 for entry in result["meter_read_log"])
```

Cardinality and value domains. Nothing joins the two streams on `(customer_id, period_end)`
and nothing compares `billing_basis` against `status`. The name promises the property; the
subject is a count — R15 killer pattern 1's shape at the level of the whole control, and it
is why a 100%-of-mechanism divergence has been passing.

## Why BLOCKING

Both legs of the ruling's clause-1 definition, stated separately so neither carries the
verdict alone:

- **An instrument in this area is untrustworthy.** The one control over the pair cannot
  fail on the defect its name describes.
- **A published record is wrong.** Three rows of a published 1,600-row artefact assert a
  read status contradicted by the published bill for the same customer-period.

## Why this is EP8's finding and not only a billing defect

`EP8_adapter_dcc_duis`'s own `name:` promises that the mock is shaped so *"the eventual swap
is transport-only"*. A real DUIS or n3rgy transport answers a request **once**; there is no
seed to recompute from. The moment either call site is served by a real adapter, the second
call site has nothing to re-derive the same answer from — so today's 3-row divergence is the
benign form of a defect that becomes unbounded at the first real transport. The dual
computation must collapse to one before this atom's stated deliverable is even coherent.

## Recommendation — recorded and acted on by queueing, not asked

Repair is **one stream, two readers**: `monthly_bill_assembly` and the published log read
the same computed events (including the SLC 21B override), rather than each calling
`simulate_read` and trusting the seed. The class control (R10 — an instance fix is not a
closure) is a join-shaped test: for every `(customer_id, period_end)`, `billing_basis` ==
the log's `status`, with the mutation proof being the override re-introduced on one side
only, which must red the suite. NOT fixed on sight — `SELF_INTERRUPT_DISCIPLINE` queues a
worker's own findings, and this is a BUILD change to a live billing path drawn by a LANE 3
doc-only tick.

**Not claimed:** that any customer was mis-billed. The bills are the SLC 21B-correct
artefact; it is the read log that is stale about them. Whether any downstream consumer of
`meter_read_log` (`company/compliance/population_sanity.py`, `saas/reporting/annual_report.py`,
`saas/reporting/css_statement.py`) produces a wrong figure from those 3 rows was **not
measured** this pass and is the first thing the repairing draw should check.

— Worker tick, 2026-08-15, at HEAD `0f2fab3c5`.
