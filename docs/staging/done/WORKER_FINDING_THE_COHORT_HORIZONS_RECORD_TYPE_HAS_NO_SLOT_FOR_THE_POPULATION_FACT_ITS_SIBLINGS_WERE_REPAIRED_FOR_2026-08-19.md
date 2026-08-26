# [WORKER-FINDING] The cohort horizon's record type has no slot for the population fact its two siblings were repaired for (2026-08-19)

**Severity:** LATENT · **Lane:** B_commercial · **Disposition:** QUEUED (not fixed on sight)

**Found:** 2026-08-19 worker tick, LANE 3 DISCOVER/FRAME draw on `EP1_clv_three_horizon`
(level 0, `loop_stage: idle`, BUILD-gated — no BUILD code written this tick). Pass 7.
**Subject:** `company/crm/clv_cohort_book.py` — the module this atom's own record names as its
THIRD horizon (portfolio-cohort), built, tested, and with zero non-test importers — read against
the population rule the other two horizons each had to learn by publishing a wrong figure.
**Measured at:** HEAD `bc689525a`, working tree of this tick, `docs/reports/run_output_latest.json`
and `docs/reports/ANNUAL_REPORT.md` as committed. Every module named was EXECUTED as it sits on
disk; nothing monkeypatched, nothing regenerated. Everything below is `observed-with-evidence`
unless labelled `inferred` (R9).

## Why this is worth a finding rather than a line in the record

This atom's six prior passes found six CLV defects. Five were about WHO OR WHAT WAS COUNTED, one
about arithmetic (pass 6 counted the ratio and made it this atom's stated design constraint:
*"EP1's published output must carry its population, not only its number"*). The two horizons that
already exist in some form have each been repaired for that class:

* **tenure-expected** — valued accounts that had already left. Repaired `66141b70c`, and repaired
  *fail-closed*: `saas/enterprise_value.build_enterprise_value` takes `ceased_accounts` as a
  REQUIRED keyword with no default, and says why in its own docstring. Still that shape at HEAD
  (`saas/enterprise_value.py:153`, `:174`, `:202`, `:211`).
* **the published matrix** — a structural blank entering an aggregate as the number zero. Repaired
  `84ae6bbeb`; `saas/reporting/annual_report._median` now carries the reasoning at `:8234-8265`
  and the board line at `ANNUAL_REPORT.md:2246` moved from 5 accounts to 1.

The third horizon has never been wired, so it has never been repaired. This finding measures what
it would be born with.

## 1. The record type cannot hold a structural blank, and has no population field at all

`CustomerCLVRecord` (`company/crm/clv_cohort_book.py:8-16`) declares seven fields:
`customer_id, acquisition_year, channel, segment, clv_gbp, annual_margin_gbp, tenure_years`.

None of them says whether the customer is still supplied. Grepped the annotations for
`supplied|ceased|active|churn`: **NONE**. The fact that the tenure horizon's repair made into a
required, defaultless keyword has nowhere to live on the cohort horizon's record — not "has an
unsafe default", but no slot.

`clv_gbp` is annotated `float`. Executed on the shipped class:

```
CustomerCLVRecord(..., clv_gbp=None, ...)          -> ACCEPTED (dataclass, no runtime check)
_cohort_summary('residential', [that record])      -> TypeError: '>' not supported between
                                                      instances of 'NoneType' and 'int'
book.add(C1, clv=None); book.add(C2, clv=100.0)
book.by_segment('residential')                     -> TypeError: '<' not supported between
                                                      instances of 'float' and 'NoneType'
```

This is a loud failure, not a silent one, and that is to its credit. The consequence is still that
**any wiring must resolve the blank at the boundary**, and the record it writes into cannot record
which way it resolved it.

## 2. Pass 6's "free falsifier" cannot be run on this horizon

Pass 6 named a control it said was available on every horizon for nothing:

> for any aggregate EP1 publishes, swapping a structural blank between `null` and `0.0` MUST move
> the rendered figure or the aggregate is not population-aware.

On the cohort book that mutation raises `TypeError` before producing either figure. The control
is not fail-open here; it is **un-runnable**. A control that cannot be executed is not a control
that passes, and pass 6's constraint therefore has no falsifier on the leg it was written for.

## 3. The falsifier that CAN be run is degenerate on today's book — by coincidence, not by design

The two candidate population policies are "drop the nulls" and "keep only the supplied". Census of
`run_output_latest.json::by_billing_account`, 13 accounts, on the 2×2:

```
  still_supplied=False  clv_is_null=True    n=5   ['C1','C3','C4','C5','C6']
  still_supplied=True   clv_is_null=False   n=8   ['C2','C7','C8','C9','C_IC1','C_IC2','C_IC3','C_IC4']
  still_supplied=True   clv_is_null=True    n=0   — EMPTY
  still_supplied=False  clv_is_null=False   n=0   — EMPTY
```

The two discriminating cells are empty. Executed — the cohort book built from the live 13 accounts
under all three policies:

```
policy        n      total_clv       avg_clv   profitable_pct
zero         13   1,283,074.77     98,698.06        53.8%
drop_null     8   1,283,074.77    160,384.35        87.5%
supplied      8   1,283,074.77    160,384.35        87.5%
```

`drop_null` and `supplied` are **bit-identical on every field**. A wiring of the cohort horizon
that never checks whether a customer is still supplied would pass a population test on this book,
today, for the same reason a broken clock passes at noon. The discriminating case — an account
still supplied but carrying no CLV, or a ceased account still carrying one — is exactly the case
the tenure horizon's own bug WAS, and the current population cannot produce it.

## 4. The magnitude of the choice the boundary is forced to make

Same three books, same run. Portfolio-wide, `profitable_pct` moves **53.8% → 87.5%**, a 33.7-point
swing decided entirely by what happens to a blank. Split by segment (`inferred` — the split is
derived from the `C_IC` id prefix, which is a naming convention and not a field the run output
publishes; the portfolio figures above need no such derivation):

```
residential cohort   zero:  n=9  avg=  347.25  median=   0.00  profitable= 33.3%
                     other: n=4  avg=  781.31  median= 976.92  profitable= 75.0%
```

A published residential cohort median of **£0.00** versus **£976.92**, and a profitability read of
33.3% versus 75.0%, on the same book, same code, same day.

And the one qualitative accessor the class exposes is blind to all of it: `is_profitable_cohort`
is `avg_clv_gbp > 0`, which reads **True** under every policy above. The single boolean a reader
would quote survives a choice that moves every number under it.

## 5. Third instance of the same class, on the same leg: an empty cohort is a worthless cohort

`_cohort_summary` returns an all-zeros `CohortSummary` for `n == 0` rather than `None`. Executed:

```
 book with one residential record worth 0.0
   by_segment('sme')          -> customer_count=0 avg=0.0 median=0.0 total=0.0 profitable_pct=0.0
   by_segment('residential')  -> customer_count=1 avg=0.0 median=0.0 total=0.0 profitable_pct=0.0
 identical on every value field  -> True
 is_profitable_cohort:  nonexistent cohort False | loss-making cohort False
```

A cohort that **does not exist** and a cohort that **loses money** both publish
`is_profitable_cohort=False` and `avg_clv_gbp=0.0`. `customer_count` distinguishes them and no
other field does — the same null-means-not-applicable vs zero-means-worth-nothing collapse that
`84ae6bbeb` had to repair one module away, still live here.

## 6. R15 — the suite certifies the shape rather than testing it

`tests/company/crm/test_clv_cohort_book.py`: **19 passed in 0.05s** at HEAD. Read in full:

* Zero tests mention `None`, `supplied`, `ceased` or a blank of any kind. The population question
  is not covered — not covered badly, not covered at all.
* Every test runs against one hand-written five-record fixture (`_book()`, `:5-12`) in which every
  `clv_gbp` is a concrete float. The live book's defining feature — that 5 of 13 accounts have no
  CLV — cannot arise in the fixture.
* Three tests (`test_by_acquisition_year_empty`, `test_by_channel_empty`, `test_by_segment_empty`)
  **assert the §5 behaviour as intended**: `test_by_acquisition_year_empty` asserts
  `c.avg_clv_gbp == pytest.approx(0.0)` for a cohort that does not exist. The suite does not merely
  miss the blank-as-zero collapse; it pins it.

## Severity, argued rather than inherited

**LATENT, not BLOCKING.** Zero non-test importers of `company/crm/clv_cohort_book.py` at HEAD
(re-confirmed this tick), so no published figure is wrong because of any of the above, and
`blocking_by_lane` over the staging root is empty before this file (89 documents scanned) —
filing BLOCKING would hold B_commercial for a prospective risk rather than a red, which is the
false-blocker error `WORKER_FINDING_THE_POPULATION_DRAW_IS_LIVE_ON_DISK_WHILE_ITS_ROSTER_FIX_IS_UNCOMMITTED_2026-08-13`
named and pass 5 avoided. It is not RECORDED either: §6 is a suite that pins the defect, which is
the shape pass 2 escalated on for the contract-term horizon, and the repair gets no cheaper than
now — the caller count is zero and every earlier instance of this class cost a published figure
first.

## Discharge condition — either is sufficient, both are cheap at zero callers

1. **Give the record the slot and the summary the population.** Add a supply/eligibility field to
   `CustomerCLVRecord` with no safe default (the `66141b70c` shape, which is this repo's own proven
   answer), make `clv_gbp` explicitly optional, and have `CohortSummary` carry `excluded_count` and
   the exclusion reason alongside `customer_count` — pass 6's design constraint, applied to the leg
   it was written for. Distinguish an empty cohort from a worthless one (return `None`, or carry
   the emptiness on the summary).
2. **Or state the contract and enforce it at the door.** If the cohort book is to remain
   blank-free by contract, say so in the module and make `add()` reject a non-float `clv_gbp`
   explicitly, so the caller's population decision is forced at a named place rather than by a
   `TypeError` from `sorted`.

Either way the falsifier must be able to fail: a test in which a supplied account carries no CLV
and a ceased account carries one — the two cells §3 shows are empty in the live population — and
which fails on today's code. Without that case constructed deliberately, §3 shows the control
cannot discriminate.

**Not fixed this tick:** the repair is BUILD code inside this BUILD-gated atom's own subject
matter, which LANE 3 may not write (EPOCH_GATING_AND_ATOM_AUTHORSHIP rule 1), and
SELF_INTERRUPT_DISCIPLINE queues a worker's own finding by default.
