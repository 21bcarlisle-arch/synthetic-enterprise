# [WORKER PREREGISTRATION] What the baseline floor does and does not fix to the published shock series

**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`
**Filed:** 2026-09-01. The prediction below is the **director's own, quoted verbatim from the
delivery instruction, and it was written before this measurement existed.** The result is beside it.

## Why this document exists rather than an assumption

`WORKER_FINDING_THE_LIVE_SITE_PUBLISHES_A_200_PERCENT_AVERAGE_BILL_SHOCK_2026-09-01` closes with:

> `BILL_SHOCK_BASELINE_FLOOR_GBP` landed in `41cdd5b51` … **The next publish corrects the live figure
> with no further change.**

That is a claim about a run nobody had looked at. **It was inherited rather than measured, and the
instruction was to confirm or refute it by running it.** A post-floor run now exists, so it can be.

## The pre-registration, verbatim (director, delivery instruction, 2026-09-01)

> *"My own reading says it is at best partial: the floor removes divisions by a near-zero baseline,
> and it does not touch a **mean over a distribution whose worst month is 137× its median**. Print
> the monthly series post-floor beside the live one before deciding."*

**P1.** The four-figure percentages go. *(implied by "removes divisions by a near-zero baseline")*
**P2.** The mean-over-a-skewed-distribution defect **survives** the floor.
**P3.** Therefore "corrects the live figure with no further change" is **at best partial**.

## The measurement

Two real run artefacts, same book, one variable between them — the floor.

| | pre-floor | post-floor |
|---|---|---|
| run | `fb6e29e6d` (`run_output_fb6e29e6d_20260901T095405Z.json`) | `3df8f7400` (`run_output_3df8f7400_20260901T112345Z.json`) |
| floor present | **no** (`41cdd5b51` is not an ancestor) | **yes** |
| what it is | **what `site/data/dashboard.json` serves at HEAD today** | what the in-flight publish will serve |

Nothing else was changed to produce this table: it is `mean(bill_shock_pct)` per calendar month over
`years[*].bill_shock_events`, exactly as `tools/generate_dashboard_data.py:1416` computes
`monthly_ops.monthly[].avg_shock_pct`.

### P1 — CONFIRMED. The four-figure percentages go.

| month | pre-floor mean | post-floor mean |
|---|---:|---:|
| **2022-04** | **17,284.3%** | **68.3%** |
| 2024-09 | 749.5% | 87.1% |
| 2023-03 | 966.3% | 115.2% |
| 2020-08 | 588.2% | 120.8% |
| worst month, whole run | **17,284.3%** | **315.6%** |
| whole-book mean over events | 390.0% | **108.1%** |
| whole-book **max** single shock | 757,576.0% | 2,593.1% |

At year level the same: **2022 goes from 617.2% to 42.2% and becomes the highest year**, which is
correct — 2022 was the crisis. Pre-floor, 2022 was 13× every other year and no year could be
compared with any other.

### P2 — CONFIRMED. The skew defect survives, untouched.

Post-floor, over 3,161 events:

| statistic | value |
|---|---:|
| mean | **108.1%** |
| **median** | **49.7%** |
| p75 | 96.9% |
| p90 | 236.4% |
| p99 | **986.9%** |
| mean ÷ median | **2.17×** |
| p99 ÷ median | **19.8×** |

**Twelve of 113 published months still carry a mean above 200%**, and in every one of them the mean
is between 1.5× and 4.6× that same month's median:

| month | n | mean | median |
|---|---:|---:|---:|
| 2016-02 | 7 | 205.6% | 107.7% |
| 2016-03 | 10 | 266.1% | 83.5% |
| **2016-08** | **5** | **315.6%** | **68.3%** |
| 2017-02 | 13 | 231.4% | 66.0% |
| 2017-07 | 19 | 202.7% | 96.6% |
| 2017-08 | 12 | 262.6% | 143.1% |
| 2019-09 | 26 | 219.1% | 71.7% |
| 2020-03 | 11 | 298.9% | 121.4% |
| 2020-09 | 20 | 254.6% | 95.2% |
| 2021-01 | 18 | 224.5% | 155.2% |
| 2024-07 | 20 | 229.3% | 99.4% |
| 2025-03 | 23 | 219.9% | 67.7% |

**The worst surviving month is the thinnest one.** 2016-08 publishes "315.6%" off **five events**.
**Thirty-two of 113 months carry fewer than 20 events**, and they hold five of the six worst
surviving means. That is the population-bound gap, and it is not repairable by a floor.

### P3 — CONFIRMED, and the finding's sentence is corrected here rather than in place

"The next publish corrects the live figure with no further change" is **true of the headline it was
written about and false as a general claim.** Precisely:

- **Corrected with no further change:** the four-figure percentage, the year series, and the
  comparability of one year with another. `avg_shock_pct` never again exceeds 315.6%.
- **Not corrected:** a mean is still the published summary of a distribution whose p99 is twenty
  times its median, twelve months still read above 200%, and no month publishes the bound its
  sample size earns.

## A third thing the measurement found, which nobody predicted

**Two published fields are both called the average bill shock and they are means over different
populations.**

| field | where | population | 2016 value | 2022 value |
|---|---|---|---:|---:|
| `years[].avg_bill_shock_pct` | dashboard year rows, annual report | **every bill** | 30.8% | 42.2% |
| `monthly_ops.monthly[].avg_shock_pct` | dashboard monthly series | **only bills already flagged as a shock** (≥20%, `bill_shock_tracker.BILL_SHOCK_THRESHOLD`) | 110.6% | 116.7% |

They differ by 3.6× in 2016 and 2.8× in 2022 and neither carries its population on the surface. A
reader moving from the year row to the monthly chart sees the number treble and has nothing to tell
them why. **This is the same defect one level up from the one this work was drawn for** — *before
measuring a thing, say what it is* — and it is why the finding's "121% over 12 bills" and the
dashboard's "205.6% over 7 events" are both right about 2016-02 and describe different quantities.

Not repaired here. It is a fourth change to a published figure and it gets its own commit.

## A fourth thing, found by running the tests rather than reading them

**The floor landed with four red tests behind an `--ignore`, and nothing could see them.**

`tests/simulation/test_run_phase4c_on_phase2b.py` is one of eight files
`background/process_run_complete.py` passes `--ignore` to its publish suite. Four of its tests build
a customer on 10 kWh months — about a £3 bill — and assert a `bill_shock_pct` against it. The floor
correctly refuses to divide by a baseline below £5, so all four have returned `None` and failed
since `41cdd5b51`, and every publish since has been green.

They are repaired in this commit by scaling the fixtures (10/50 kWh → 300/1500), which changes no
ratio any of them asserts — the 10× jump and the 5× seasonal peak are identical. The point worth
keeping is not the repair: **a suite that excludes a file for cost cannot report the red a change
makes in it, and the excluded file here was the integration test for the exact module the change
was in.** That is the same shape as `a_selection_based_test_gate_is_blind_to_a_consumer_it_did_not_
select`, one level up: not a consumer it failed to select, but a file it was configured never to
select at all.

## What this pre-registration binds the next commits to

1. **The floor is not the repair for the surviving months**, so nothing below may be justified by it.
2. **A mean is the wrong summary** and the median must be published beside it, with `n`.
3. **`n` is the bound.** 2016-08's five events are the case that decides the wording.
4. **The two `avg_*_shock_pct` fields must each name their population** before either is trusted.

*Measured on real artefacts already on disk; no new run was needed and none was made for this
document. Nothing here changes a published figure.*
