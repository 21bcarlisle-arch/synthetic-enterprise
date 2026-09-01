# [WORKER PREREGISTRATION] What splitting the annual shock mean by population must show

**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** unminted
**Filed:** 2026-09-01, **before the code that settles it exists.** Every before-figure below was read
out of the artefact that is live right now.
**Knowledge:** `docs/market_research/what_bill_shock_is.md` — the definition, established and NOT
re-opened.
**Predecessors:** the monthly series was split at `98db658f2` and the sign fixed at `da0431897`; both
reached the published surface and were graded at `63deb6405`.

## Class registration

Belongs to `measurements_that_mirror` — a mean over a mixed subject that reports one number for two
populations, which is the same failure the monthly split just ended, one level up and on a larger
sample.

## Why this exists

`financial.annual[].avg_bill_shock_pct` in `site/data/dashboard.json` is **one mean spanning both
populations.** It is not the series that was split: that one (`monthly_ops.monthly[].avg_shock_pct`)
covers the 1,748 bills *flagged* as shocks. This one covers **every bill with a computable shock —
6,094 of them**, three and a half times as many, and it is the figure the year table shows.

It carries an `avg_bill_shock_pct_population` note. **The note says which BILLS it covers and is
silent on which HOUSEHOLDS** — so it reads as a field whose population question has been settled,
while being the exact defect the monthly split exists to end. That is worse than saying nothing:
`63deb6405` graded the monthly labels as having read as proof a correction had happened before it
had, and this is the same shape.

It also carries **no `n` and no bound of any kind.**

## The before state, measured now, on the live artefact

`site/data/dashboard.json`, `financial.annual[].avg_bill_shock_pct` — note these are **fractions**
published under a `_pct` name, which is itself recorded below as a limit and not repaired here:

| year | published | computable bills |
|---|---:|---:|
| 2016 | 0.43 | 393 |
| 2017 | 0.36 | 604 |
| 2018 | 0.31 | 577 |
| 2019 | 0.43 | 559 |
| 2020 | 0.41 | 583 |
| 2021 | 0.42 | 751 |
| 2022 | **0.58** | 799 |
| 2023 | 0.47 | 769 |
| 2024 | 0.43 | 783 |
| 2025 | 0.46 | 276 |

Whole book, across all years, from the run behind that page
(`run_output_98db658f2_20260901T155311Z.json`) — **already measured and therefore stated as a fact,
not offered as a prediction**:

| population | n | mean % | median % |
|---|---:|---:|---:|
| `payment` (direct debit) | 4,366 | 45.58 | 3.79 |
| `bill` (standard credit) | 1,696 | 38.40 | 5.97 |
| `unknown` (no channel) | 32 | 23.15 | 0.14 |
| `out_of_scope` (prepayment) | 0 | — | — |

Two things are visible there before any change. The populations **differ by 7.2 points of mean**, so
the split is not cosmetic. And **both medians are near zero against means in the forties** — this
distribution is far more skewed than the flagged-shock one, which is why the bound and the median
matter more here, not less.

## The predictions

**P1 — the per-population counts sum exactly to the year's computable-bill count**, for all ten
years and to 6,094 in total. *Refuted by* any year not tying.

**P2 — the n-weighted mean of the per-population means reproduces the published mixed figure** for
every year, to rounding. This is what makes the split checkable from the artefact alone rather than
from the diff. *Refuted by* any year where it does not tie.

**P3 — no existing published field moves.** This is additive: `avg_bill_shock_pct`, every other
`financial.annual` field, and all of `monthly_ops` must be byte-identical on a re-render of the same
run. *Refuted by* any diff outside the new keys.

**P4 — 2022 is the highest year in BOTH populations.** 2022 is the crisis and is currently the
highest mixed year at 0.58. This is genuinely at risk and I have not measured it: the two populations
could peak in different years, and if they do **that is a finding, not a defect** — it would mean the
crisis reached direct-debit and full-payment households on different clocks, which is exactly what
the definition page says to expect ("same commercial decision, two different experiences, two
different lags"). *Refuted by* either population peaking anywhere but 2022.

**P5 — `payment`'s mean exceeds `bill`'s in every year.** Whole-book it does, by 7.2 points; whether
that holds year by year is not measured. *Refuted by* any year where `bill` >= `payment`.

**P6 — `out_of_scope` is 0 in every year and publishes `null`, never `0.0`.** This world has two
payment channels and no prepayment household. A `0.0` there would be an unobservable published as a
measured zero. *Refuted by* any `0.0` in an empty cell.

**P7 — at least one year x population cell cannot bound itself and says so.** `unknown` is 32 bills
across ten years, so some year holds fewer than two. Its interval must come back `null` with its `n`
beside it, not a fabricated bound and not a suppressed row. *Refuted by* every cell carrying an
interval, which would mean the thin case is not being reported.

## What is deliberately NOT predicted

**Any per-year per-population value.** They are computable from the artefact on disk right now, so
"predicting" them would be transcription. The predictions above are all about properties that a
plausible implementation can get wrong.

**Whether the split changes anyone's mind about the level.** It should not: the mixed figure is a
weighted average of the two and P2 requires it to stay reconcilable.

## Limits recorded before the fact, so they cannot read as discoveries

1. **`avg_bill_shock_pct` is a FRACTION under a `_pct` name** (0.43, not 43). The new per-population
   block will publish **percentages**, because it must match `monthly_ops.shock_by_population` field
   for field and unit for unit — a reader who has learned one has learned the other. Two adjacent
   `_pct` fields in different units is a trap, so the block publishes its own mixed figure in its own
   units alongside, making the mismatch checkable in one place instead of latent. **Renaming the
   legacy field is not done here** and would move a figure every consumer reads.
2. **`unknown` is not attributed by this change.** 32 bills carry no `payment_channel`. Splitting
   names them; it does not resolve them. Separate item, already recorded at `63deb6405`.
3. **The `payment` population's number is still a bill-to-bill difference for households who do not
   pay the bill.** Publishing it under its own name is not the same as measuring their experience,
   which is a change in the amount collected and which this codebase cannot compute because the
   direct debit is not a modelled quantity. That build is named out of scope by the director's own
   correction and stays out.

## What settles it

Re-render the dashboard from the same run output and grade P1–P7 in this file, beside the
predictions, whichever way they fall.
