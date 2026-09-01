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

---

# GRADED, 2026-09-01. THREE OF SEVEN REFUTED.

Measured by re-rendering `extract_financial` over the same run
(`run_output_98db658f2_20260901T155311Z.json`) that the live page was built from, and diffing
against the live artefact field by field.

## The after state

| year | payment mean % (95% CI) | n | bill mean % (95% CI) | n | unknown n |
|---|---:|---:|---:|---:|---:|
| 2016 | 44.3 (30.7, 60.2) | 306 | 43.5 (25.4, 65.5) | 78 | 9 |
| 2017 | 35.8 (23.7, 51.1) | 454 | **36.1** (18.4, 59.2) | 143 | 7 |
| 2018 | 35.6 (25.5, 47.4) | 437 | **16.9** (11.8, 22.5) | 134 | 6 |
| 2019 | 43.4 (30.0, 61.0) | 401 | **43.5** (24.5, 66.5) | 153 | 5 |
| 2020 | 46.5 (33.1, 62.6) | 420 | 24.7 (16.4, 34.7) | 158 | 5 |
| 2021 | 43.4 (31.7, 57.8) | 531 | 39.4 (28.5, 52.0) | 220 | 0 |
| 2022 | **63.0** (48.6, 79.2) | 547 | 45.7 (30.6, 65.6) | 252 | 0 |
| 2023 | 48.8 (38.1, 60.6) | 527 | 42.2 (29.3, 59.6) | 242 | 0 |
| 2024 | 45.7 (34.8, 58.1) | 553 | 38.2 (26.2, 52.7) | 230 | 0 |
| 2025 | 43.4 (26.2, 67.3) | 190 | **53.1** (26.3, 90.5) | 86 | 0 |

`out_of_scope` is 0 in every year.

## P1–P7

**P1 — counts tie. CONFIRMED.** Every year's per-population counts sum to its computable-bill count
(393, 604, 577, 559, 583, 751, 799, 769, 783, 276) and to 6,094 in total, and `mixed_all_population`
carries the same n in every year.

**P2 — the weighted mean reproduces the mixed figure. CONFIRMED, against the right target.** My
first grader read the *published* `avg_bill_shock_pct` and reported a mismatch in eight years out of
ten. The code was right and the grader was wrong: that field is `_fmt`'d to two decimals **of a
fraction**, so it is only good to ±0.5 percentage points and cannot settle a reconciliation at this
precision. Graded against the producer's own unrounded mean, all ten tie to within 0.03pp
(2022: weighted 57.544, block 57.5, producer 57.519). **Recorded because it is the more useful half
of this grading: the refutation I nearly filed was an artefact of the resolution of the field I was
checking against, and limit 1 above — the fraction-under-a-`_pct`-name — is what caused it. A
recorded limit bit within the hour.**

**P3 — no existing published field moves. REFUTED ON ITS OWN WORDING, CONFIRMED ON EVERY NUMBER.**
Exactly one field changed and it is not a number: `avg_bill_shock_pct_population`, whose prose I
rewrote in the same commit because it was the misleading half of the defect — a note answering the
population question in the wrong dimension reads as a field whose population question is settled.
Every numeric field of `financial.annual` is byte-identical, and all of `monthly_ops` is
byte-identical.

**I am not reinterpreting the prediction to make it pass.** I wrote "byte-identical outside the new
keys", the change is deliberate, and the prediction as written is refuted. What it protected — that
this is a re-partition and not a re-computation — holds completely. Had I noticed the collision
before filing, the honest fix was to write P3 about *figures* and name the note change as intended;
having not, the honest fix is this paragraph. Leaving a misleading note standing to keep a
prediction green would have been the control driving the code.

**P4 — 2022 is the peak in both populations. REFUTED, and it is the finding I said it would be.**
`payment` peaks in 2022 at 63.0%. **`bill` peaks in 2025 at 53.1%**, with 2022 second at 45.7%.

**But the bound is what makes this readable, and it says: we cannot tell.** `bill`'s 2025 interval is
(26.3, 90.5) on n=86 — it contains 2022's 45.7 comfortably, so the two years are not distinguishable
and 2025 is a partial year besides. The same caution applies to the confirmed half: `payment`'s 2022
interval is (48.6, 79.2) and 2023's point estimate is 48.8, *just inside it*. **So the correct
statement is not "the populations peak in different years" — it is that this book cannot resolve a
peak year in either population, and the pre-split single series was stating one by omission.**
Publishing the interval is what turned a spurious ranking into an honest refusal, which is the whole
argument for the bound.

**P5 — `payment` exceeds `bill` in every year. REFUTED, in three: 2017 (36.1 vs 35.8), 2019 (43.5 vs
43.4) and 2025 (53.1 vs 43.4).** The first two are fractions of a point and mean nothing; 2025 is
visible and sits inside an interval that spans 64 points. **The whole-book 7.2-point gap is not a
year-by-year fact**, and I should not have predicted it was — the whole-book figure is dominated by
the years where the gap is large, which is exactly the aggregation error this exercise is about, made
by me one level up.

**The result that survives its own bound, and the reason the split earns its place:** in **2018**,
`payment` reads 35.6 (25.5, 47.4) and `bill` reads 16.9 (11.8, 22.5) — **non-overlapping intervals.**
One year in ten where the two populations are definitively not the same number. 2020 is nearly a
second (33.1–62.6 against 16.4–34.7, overlapping only in a sliver). That is the split's evidence: not
that the two means differ on average, which a mixed mean could always be accused of manufacturing,
but that there is at least one year where no single figure can honestly stand for both.

**P6 — `out_of_scope` publishes null, never 0.0. CONFIRMED**, in all ten years, and held by a control.

**P7 — at least one year × population cell cannot bound itself. REFUTED.** No cell has `0 < n < 2`;
the smallest non-empty cell is n=5. My reasoning was that 32 `unknown` bills spread over ten years
must leave some year below two. It does not, because **they are not spread: `unknown` is 9, 7, 6, 5,
5 across 2016–2020 and then exactly 0 from 2021 onward.** The unattributed bills are entirely a
feature of the early book. That is a fact worth having and I got it by being wrong about it. The
thin-cell branch is therefore unexercised by real data and is held by a control
(`test_a_cell_too_thin_to_bound_itself_says_so_beside_a_real_count`) and by mutation M8, not by the
artefact — said plainly so nobody reads the refusal path as demonstrated in production.

## What this closes and what it does not

**Closes:** no mean spanning both populations is published on this surface without its two component
means, each with its own `n`, median, max and bootstrap interval, beside it. Both series — flagged
and all-computable — are now split.

**Does not close:** the 32 `unknown` bills are still unattributed; `avg_bill_shock_pct` is still a
fraction under a `_pct` name; and the `payment` population's figure remains a bill-to-bill difference
for households who do not pay the bill. The last of those is the director's named out-of-scope build
and is the only one of the three that changes what the number *means* rather than what it is called.
