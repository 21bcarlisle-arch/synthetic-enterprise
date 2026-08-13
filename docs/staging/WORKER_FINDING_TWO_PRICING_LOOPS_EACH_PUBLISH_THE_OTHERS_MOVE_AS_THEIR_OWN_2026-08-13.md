# [WORKER-FINDING] Two pricing loops, and each publishes the other's move as its own (2026-08-13)

**Severity:** BLOCKING · **Lane:** B_commercial

**Status:** measured and reported, not fixed. A published table's three columns contradict each
other arithmetically, so a reader who checks the row gets a different answer than the row gives.
Found during the `EP2_variance_learning_loop` DISCOVER draw — attribution of a realised change to
its causes is EP2's own subject, and it is failing on a board surface.

## The rendered defect

`docs/reports/ANNUAL_REPORT.md:895`, section **Margin Recovery Surcharges (Phase 16c + 19a)**:

```
| C_IC1 | electricity | 2018-01-31 | £-5,651.81 | £10,420.08 | +20.0% | £112.24/MWh | £153.39/MWh |
```

£112.2436 × 1.20 = **£134.69**, not £153.39. `observed-with-evidence`, read off the published
artefact (R11), not off the code.

The missing factor is +13.88%, and it is not missing at all — it is published forty lines away in
a *different* table off the *same* starting rate. `ANNUAL_REPORT.md:2376`, **Dynamic Pricing
Activity**, same customer, same commodity, same term start:

```
portfolio_premium_pct: 13.88 | unit_rate_before: 112.2436 | unit_rate_after: 127.8264
```

112.2436 × 1.1388 × 1.20 = 153.39. Both tables are right about their own coefficient and wrong
about their own span.

## The mechanism

`simulation/run_phase2b.py`, one renewal, two multiplications of the same variable:

* line ~1166 — Loop B, portfolio premium: `unit_rate *= (1.0 + portfolio_prem)`
* line ~1183 — Loop A, recovery surcharge: `unit_rate *= (1.0 + surcharge)`

Loop A then logs (line ~1191):

```python
"unit_rate_before": round(term["unit_rate_gbp_per_mwh"] or 0.0, 4),   # the PRE-premium original
"unit_rate_after":  round(unit_rate, 4),                              # after BOTH
```

`term["unit_rate_gbp_per_mwh"]` is never rebound, so Loop A's "before" is the rate as it stood
*before Loop B*, while its "after" carries both moves. Loop B's log, written earlier, records the
same original as its "before" and its own intermediate as its "after" — an intermediate no
customer was ever charged.

## Population, not instance (R10)

Over `docs/reports/run_output_latest.json`:

* **28 of 29** margin-feedback rows: own `before→after` span disagrees with the stated
  `surcharge_pct` by more than 0.05pp. (The 29th agrees only because that renewal's premium was
  ≈0.)
* **29 of 115** dynamic-pricing rows publish a `rate_after` that is **not** the rate the customer
  contracted — every renewal both loops touched.
* Every one of the 29 margin events is a term the premium loop also moved: the overlap is
  **29 of 29**, not an edge case.

So the class is "two writers to one quantity, each logging a before/after pair as though it were
the only writer" — and the fix has to be the pair being made a *chain* (one span, decomposed by
cause), not a patch to whichever log is read next.

## A third figure inherits it

Same report, **Dynamic Pricing Activity** year table (`ANNUAL_REPORT.md:1735`):

* `saas/reporting/annual_report.py:7411` — `emergency = len(mfl_by_year.get(yr, []))`. The
  **Emergency** column *is* the margin-feedback count, relabelled. Its caption says "Emergency
  reprices triggered when recent margin dropped below cost floor" — but `compute_margin_surcharge`
  has no cost floor; it fires on a prior-term realised loss above 5% of revenue, at renewal. The
  only `_cost_floor` in the tree is in `company/pricing/renewal_pricing_engine.py`, a different
  module that does not produce this column. `**Emergency reprices: 29 total**` is the surcharge
  count wearing another mechanism's name.
* `Avg Delta £/MWh` is computed from the dynamic-pricing log only, under a caption reading "Rate
  adjustments driven by the margin feedback loop".

## Why BLOCKING

Per `background/finding_severity.py`: *a published figure may be wrong*. Three published figures
are: the surcharge table's `Rate after` span, the dynamic-pricing table's `Rate after` value, and
the `Emergency reprices` label. All three are on the annual report, which is a board surface.

**What would clear it:** the two loops publishing one decomposed span per renewal (original →
contracted, with the premium and the surcharge as named components), plus the Emergency column
either renamed to what it counts or dropped. That is sub-atom 3 of the EP2 FRAME
(`docs/design/EP2_VARIANCE_LEARNING_LOOP_DISCOVER_FRAME.md` §8) — this finding is discharged by
EP2's build, not by a patch ahead of it.

**Not fixed in this tick, deliberately:** SELF-INTERRUPT DISCIPLINE — queue by default. Fixing the
`unit_rate_before` field alone would green the arithmetic while leaving two undecomposed writers on
one quantity, which is the actual defect.
