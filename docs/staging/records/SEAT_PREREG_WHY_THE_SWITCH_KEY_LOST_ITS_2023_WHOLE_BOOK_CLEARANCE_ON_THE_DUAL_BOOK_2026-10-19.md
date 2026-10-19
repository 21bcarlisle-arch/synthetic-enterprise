# Pre-registration: why the switch key's 2023 whole-book clearance fell on the dual book

**Written 2026-10-19 ~13:55Z, before any per-account figure below was read.** Claim
`why-the-switch-key-lost-its-2023-whole-book-clearance-on-the-dual-book` (Lane 0, worker).
DEVELOPMENT. Subject: B11 grade in
`SEAT_PREREG_B11_C35_C34_ON_THE_FIRST_PUBLISHED_DUAL_FUEL_RUN_2026-10-18.md` §6.

The reading: `backtest_run_output(path, 2023, switch_on_default=True, rescale_over="fit_window")`,
whole book, key minus flat AUC. Old run `run_output_78f77c34e_20261016T140442Z.json` (1% dual,
266 graded): **+0.133 (+0.056, +0.209)**. New run `run_output_8b6fea024_20261019T033010Z.json`
(73% dual, 201 graded): **+0.075 (−0.013, +0.162)**. Both are re-read with today's code, so the
instrument is one variable held fixed.

## What the key reads, said before anything is split

Read from `company/analytics/forward_clv.py` (`_supplier_views`, `run_backtest`, slice 11):

- The key is one binary observable: **months on default at the cut, 36+ or under**, with a
  multiplier fitted on switches (moves censored) and rescaled per segment over the fit window.
  It multiplies only the segment's switch hazard. Within a segment it can do nothing except
  split accounts into two groups.
- **The second leg enters in one place.** A month is "fixed" when ANY leg of the billing
  account is in a fixed term on the 15th. A dual home therefore reads as on default only when
  both legs are. Both legs open on one date with one fix length (C35 finding §2), so I expect
  this to rarely differ from either leg read alone.
- **It reads nothing about the gas bill**, its size, or either leg's balance. Flat and key both
  see fuel only through the segment label (`… dual`, `… electricity`).
- So "the key is blind to the dual leg" is half true by construction: it cannot see the gas
  bill, but its default clock is already household-wide.

## Predictions

**S. Sample alone (old run, a random 201 of its 266 graded, 2,000 draws without replacement,
fixed seed).**
- **S1.** The median subsample point is within ±0.01 of +0.133. Subsampling does not bias a
  paired AUC difference.
- **S2.** The spread of subsample points has SD ≈ SE_full × √(65/201) ≈ 0.039 × 0.57 ≈ 0.022
  (in 0.015…0.030). **A point at or below +0.075 occurs in ≤5% of draws.** If sample size alone
  explained the fall, that share would be near half.
- **S3.** The median half-width rises from 0.076 to 0.083…0.095, about √(266/201) ≈ 1.15×. The
  new run's half-width (0.0875) sits in that range: **sample size explains the WIDTH**.
- **S4.** The clearance survives (lower bound > 0) in ≥85% of draws.

**F. Fuel split at 2023 (new run).** The DeLong difference is re-taken on dual accounts and on
single-fuel accounts separately (departers against stayers within each group, each rule's p as
the backtest gave it).
- **F1.** Dual (≈146 graded) and single (≈55 graded) both "cannot tell". The single group is too
  small to clear anything.
- **F2.** The dual point is within ±0.08 of the single point. The intervals overlap. **The split
  cannot tell dual from single.** I put this at ~75%. If the dual point is ≤0 while the single
  point is ≥ +0.13, F2 is wrong, and the dual leg is where the loss is.
- **F3.** Share of graded accounts in the 36+ band at the cut: dual within ±0.10 of single.
  Same opening date and fix length means the same clock.
- **F4. The whole book's +0.075 is not the weighted average of the two groups' points.** A
  whole-book AUC also counts dual-against-single pairs, and flat ranks those by the segment
  hazard (dual above electricity at every cut). I name that third term before measuring it, so
  that it is not found after the fact.

**C. 2020 and 2022, same split.** **C1.** Nothing clears in either group at either cut (the
whole book did not). **C2.** The dual-minus-single gap has no consistent sign across the three
cuts.

**B. Between books (the residual).** Two independent books at about these sizes differ by
√(0.039² + 0.045²) ≈ 0.06 SD in this figure, so a fall of 0.058 is about 1 SD. **B1.** If S2 and
F2 both hold, I will say the fall is consistent with **a different draw of the world and book**,
not explained by sample size or by fuel. Between-book variance is exactly what more seeds
measure, so the remedy is EP17's seed question, which is his, not a supplier build. One run per
book cannot separate it from a book effect, and the finding will say "cannot tell", with that
width.

## What this item will not do

It does not change the key. If F shows that the dual leg is where the ranking is lost, the
supplier change is filed as its own item, with its K8 page first.

## Grade, 2026-10-19 ~14:05Z (worker). No prediction above was edited

**On order.** The predictions were written at 13:48:33 local and the measuring scripts at 13:48:58
and 13:49:32 (file mtimes). I tried to land the predictions alone first. `surgical_land` refused
that landing because the shared checkout was 15 commits behind origin, so the predictions and
this grade land in one commit. The mtimes are the only evidence of order.

Scripts: subsampling and fuel split, then a within/cross-segment decomposition and a per-leg term
reading. All of it uses today's `forward_clv` on both run files.

### What the reading is made of: the term none of the three hypotheses named

A whole-book AUC is a pair-weighted mean of two terms: departer–stayer pairs **in the same
segment** and pairs **in different segments**. Within a segment, flat gives every account the same
p, so flat is exactly 0.5 there and the key's gain is its own information. Across segments, flat
ranks by its segment hazard, and **that ordering can be worse than chance.**

| 2023 | within-segment pairs: key / flat | cross-segment pairs: key / flat | whole: key / flat | key − flat |
|---|---|---|---|---|
| old (`78f77c34e`) | 4,536: 0.608 / 0.500 | 6,097: **0.560 / 0.409** | 0.580 / **0.448** | +0.133 |
| new (`8b6fea024`) | 3,264: 0.575 / 0.500 | 2,144: 0.619 / 0.545 | 0.592 / 0.518 | +0.075 |

On the old book, flat's cross-segment AUC was **0.409**. `resi gas` (37 single-fuel gas homes)
carried the highest flat 2023 departure p of any resi segment (0.284), and only 2 of the 37
departed. The key's 36+ band multiplies the switch hazard down, and 68% of that segment sat in
it, so the key reordered them below the electricity departers. **About 65% of the old +0.133 was
the key undoing flat's inverted gas segment** (0.573 × 0.151 = 0.087 of 0.133). On the dual book
the gas homes are dual, `resi gas` has 5 graded accounts, and flat's cross-segment term is above
chance.

Shift-share of the fall of 0.058, at old pair weights: the cross-segment term (+0.151 → +0.074)
gives **0.044 (76%)**, and the within-segment term (+0.108 → +0.075) gives **0.014 (24%)**. The
within-segment fall is inside its noise. **The key's own AUC rose (0.580 → 0.592). It did not
get worse at ranking departers. Flat stopped being worse than chance.**

### Each prediction graded

- **S1 (median subsample point within ±0.01 of +0.133): HELD.** +0.1325.
- **S2 (SD ≈ 0.022, a point ≤ +0.075 in ≤5% of draws): HELD.** SD 0.0222, 2.5–97.5% range
  +0.090…+0.179. **9 draws in 2,000 (0.45%)** reach +0.075. Sample size alone does not produce
  the fall.
- **S3 (median half-width 0.083…0.095): HELD.** 0.0881, against the new run's 0.0875. Sample size
  explains the width.
- **S4 (clearance survives in ≥85% of draws): HELD.** 96.8%.
- **F1 (dual and single both cannot tell): HELD.** Dual 146: +0.068 (−0.031, +0.166). Single 55:
  +0.117 (−0.049, +0.283).
- **F2 (dual within ±0.08 of single): HELD.** The gap is 0.049. The old book shows the same sign
  and size within segment: dual +0.083 against electricity +0.125, then dual +0.068 against
  electricity +0.137. That is a ~0.05 dual deficit in both books, and every interval is ±0.09 or
  wider. **Cannot tell.**
- **F3 (36+ share at the cut, dual within ±0.10 of single): WRONG.** It is 0.36 dual against 0.51
  single at 2023 on the new book (0.24 against 0.53 on the old). Dual homes sit in the band less
  often. One measured reason: at the 2023 cut, **16 of 146 dual households have one leg on a fix
  and the other on default**, and the any-leg rule reads them as fixed (clock 0). The figures are
  6/134 at 2022 and 11/132 at 2020. Those are 11%, 4% and 8%: real, not the cause.
- **F4 (the whole book is not the average of the groups, and a cross term exists): HELD, and it
  was the answer.** I named the term and did not predict that it would carry three-quarters of the
  fall.
- **C1 (nothing clears in either group at 2020 or 2022): HELD** on both books.
- **C2 (dual − single gap has no consistent sign across cuts): HELD.** New: −0.028, +0.072, −0.049.
  Old: −0.047, +0.042, −0.084.
- **B1 (the residual is between-book variance, so "cannot tell" and more seeds): WRONG.** The fall
  has a named mechanism: a book-composition change removed the flat rule's inverted segment. Only
  the within-segment quarter is unexplained, and that quarter is the size between-book noise
  gives.

### Correction to the item and to §6 of the B11 prereg

"The 1%-dual book" is wrong for this instrument. `book_from_run_output` merges legs by billing
account. On `78f77c34e`, **89 of 266 graded accounts at 2023 (33%) are `resi dual`** (63/253 at
2020, 73/256 at 2022). The 1% is the *opening* book's founders
(`WORKER_FINDING_THE_OPENING_BOOK_WAS_ONE_PERCENT_DUAL_FUEL_AND_NOW_BEARS_THE_PUBLISHED_SPLIT_2026-10-17.md`).
By the cuts, campaign wins had made the graded book a third dual, so the change of book was 33% → 73%, not 1% → 73%.

### What it means, and the remedy

Neither of the item's two explanations holds. **Sample size** explains the width and not the
point (S2). **The key being blind to the dual leg** does not hold either. Its default clock is
household-wide by construction, it ranks dual homes about as well as single ones (F2: cannot
tell), and its whole-book AUC rose. It reads nothing about the gas bill, and nothing here shows
that costs it ranking. **No supplier build is filed.** The 16-of-146 one-leg-fixed homes would
justify a K8 page only if a dual-only deficit were measured, and F2 cannot tell.

The reading that moved is the **baseline**. "Key against flat, whole book" mixes the key's
information with flat's cross-segment ordering, and that ordering depends on how the book is cut
into segments. A segment flat mis-ranks makes the key look good, and a re-segmentation removes
that credit. The key's own contribution is the **within-segment** term: +0.108 old and +0.075 new,
over 4,536 and 3,264 pairs. That test belongs to B11's instrument, not to a ruling, so changing
it is ours. Filed as its own item:
`docs/staging/WORKER_FINDING_THE_SWITCH_KEYS_WHOLE_BOOK_GAIN_OVER_FLAT_WAS_TWO_THIRDS_FLATS_OWN_INVERTED_GAS_SEGMENT_2026-10-19.md`.
It asks for the within-segment (stratified) term to be reported beside the whole-book figure, so
that a baseline's own mis-ordering is never counted as the key's evidence. More seeds (EP17) would
narrow the within-segment quarter. They would not have changed this answer.
