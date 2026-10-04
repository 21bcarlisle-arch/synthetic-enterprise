# The value rule against a flat price set in advance

**Pre-registered 2026-10-04 by the delivery seat, before any ex-ante score was computed.**

## Why

`SEAT_PREREG_A_DECISION_IS_CHARGED_ONLY_THE_BAD_DEBT_OF_ITS_OWN_TERM_2026-10-04.md` graded T1-T4 at
f746cd4f5. On the term basis, the capped value rule against the best flat level IN HINDSIGHT reads
+341, -37, +79 and +40, at SNR 1.29, 0.10, 0.31 and 0.09. That comparator is chosen on the very rows
it is scored on, so it is an upper bound on what any flat rule can do. Parity with it cannot show
that inference beats average. The test a supplier could actually have run is a flat level fixed in
advance from the company's own closed book.

## What is compared, defined before it is measured

- **The rows.** The four term-basis probe runs that graded T1-T4:
  `/var/tmp/se-probe-out/probe_term_{default,61001,61002,61003}.json`. They were taken at base
  `4bf859f0b` on the historical record to 2025-12-31, with no forward world, the world's debt
  objection and debt cure on, and the one-year term window (ddfbc61f6). Nothing is re-run: every
  row already carries the level grid (`level_grid`, 5 to 150 GBP/MWh in 5s) with the world's
  P(stay) and what a stayer pays at each level. Before writing this, I re-derived the published
  hindsight figures from these rows with origin's `tools/decision_probe` and got them exactly:
  levels 45/50/50/55, and +341.27, -37.39, +79.45 and +39.80.
- **Scoring.** `expected_term_margin_gbp` on the term basis (`bad_debt_basis="term"`), as in T1-T4.
  Each difference carries the account-resampled bootstrap SD and its SNR (`decision_probe.score`).
- **A decision is CLOSED** once its one-year term has ended: `term_start + 365 days`. Only then has
  the company seen whether the household stayed, and what that term wrote off.
- **The ex-ante level for decision year Y** is the grid level that maximises the summed term-basis
  margin over every decision closed before Y-01-01. It is chosen with no look-ahead in time. Ties go
  to the lower level. Each decision in year Y is then scored at that level.
- **Two ex-ante choosers**, because they answer different questions:
  - **E-true: the past rows scored on the world's own P(stay).** The company cannot see this: it
    saw only one price per past decision. That makes it the STRICTEST comparator a flat rule
    chosen in advance can have, and the primary one. If the value rule beats E-true, it beats
    every runnable flat-in-advance rule.
  - **E-belief: what the company could actually run.** The same past rows scored on the company's
    own belief of P(stay) at each level (`level_grid[L]["believed"]`), with the write-offs it saw
    on those closed terms. This is a flat-rule supplier using its own book.
- **Which decisions are scored.** No decision closes before 2017-12-31, so 2016 and 2017 have no
  book: 25 or 26 decisions a path. **The primary score is out of sample: decision years 2018-2025
  only** (56 or 57 decisions a path). That leaves 2016-2017 unscored, and I say so on the result
  rather than filling it. A secondary score covers every decision. In the book-less years it charges
  the flat rule the company's own pre-book price (the `flat` rule's offer).
- **The hindsight comparator on the same rows.** The best grid level chosen over the 2018-2025
  rows themselves. Scoring the ex-ante level and the hindsight level on one set separates what not
  knowing the future costs a flat rule from what choosing per customer earns.

One mechanical fact, not a prediction: on any one set of rows, the hindsight level is at least as
good as any level chosen in advance. So capped − E-true ≥ capped − hindsight on the same rows.

## Predictions, written before the scores

- **E1, the book's lesson.** On at least 2 of 4 paths, the E-true level in some scored year
  differs from that path's 2018-2025 hindsight level by 10 GBP/MWh or more. 2018's level is chosen
  on two closed decisions, so I expect the early years to be wrong. Held at 60%.
- **E2, the primary.** capped − E-true on 2018-2025 is positive on at least 3 of 4 paths.
- **E3, not yet a demonstrated win.** The SNR of capped − E-true is below 2 on every path. With
  about 55 decisions a path, I do not expect the ex-ante handicap alone to clear the noise.
- **E4.** capped − E-belief ≥ capped − E-true on every path. Leaning on its own churn belief, which
  is too steep, puts the flat company further from the right level. Held at 70%.
- **E5, what hindsight was worth to flat.** E-true's shortfall to the hindsight level on the same
  rows is under 300 GBP on at least 3 of 4 paths. If the book picks close to the right level
  quickly, the ex-ante handicap is small and the thesis gains little from this test. Held at 50/50.

If E-true and hindsight pick the same level on a path in every scored year, the result on that
path IS the hindsight result. I will say so as a finding: the book teaches the right level at once,
so this test adds nothing there. It is not a win.

## Which world this is

It is the current world as at `4bf859f0b`, on the historical record. The QEP refit of the
level anchors has not reached these rows, and it will move every level's P(stay). So these figures
are re-taken when it lands.

## Grading (2026-10-04, same day)

Scored offline on the four term-probe runs named above, so nothing was re-run. The tool is
`tools/decision_probe.ex_ante_scores`, landed with this grading. The raw output is in
`/var/tmp/se-probe-out/ex_ante_scores.{txt,json}`. **World:** the historical record to 2025 at base
`4bf859f0b`, with the debt objection and debt cure on. **The QEP refit will move every figure
here**, because it moves the P(stay) at every level.

### Two of my own framings were wrong, corrected here beside the claims

- **"One mechanical fact ... capped − E-true ≥ capped − hindsight."** This is false as stated. The
  hindsight comparator is the best SINGLE level for all of 2018-2025. An ex-ante chooser re-picks
  every year, so it can beat it. On 61003 E-belief does, by 34 GBP (SNR 0.75). The fact holds only
  against a chooser that is held to one level.
- **"E-true is the STRICTEST comparator."** Also false. E-true reads the world's true response, but
  in 2018 it reads it on TWO closed decisions, and two noisy rows pick 95 or 15 GBP/MWh. E-belief
  reads the company's smooth churn belief and picks 55-60 from the first year. That is closer to the
  right level, and E-belief is the harder comparator on 3 of 4 paths. **So the verdict below is read
  against whichever chooser is harder on each path**, not against E-true alone.

### Levels chosen, GBP/MWh

| path | hindsight (2018-25) | E-true by year 2018 / 19 / 20 / 21 / 24 / 25 | E-belief by year |
|---|---|---|---|
| default | 45 | 95 / 30 / 30 / 45 / 45 / 45 | 60 / 60 / 60 / 55 / 55 / 55 |
| 61001 | 50 | 15 / 55 / 55 / 55 / 50 / 50 | 60 / 60 / 55 / 55 / 55 / 55 |
| 61002 | 50 | 15 / 55 / 55 / 55 / 50 / 50 | 60 / 60 / 60 / 55 / 55 / 55 |
| 61003 | 55 | 15 / 55 / 55 / 55 / 55 / 55 | 60 / 55 / 55 / 55 / 55 / 55 |

The 2018 level is chosen on the two 2016 decisions, the only ones closed before 2018. From 2019
the book holds about 25 closed decisions, and both choosers settle within 5-10 of the hindsight
level. By 2024 E-true **coincides** with it on every path. **That is a finding about the book, not
a win:** after one full year of closed decisions the company's own book teaches the right flat
level. The ex-ante handicap is concentrated in the first year it has a book.

### The scores: capped value rule minus the flat level, term basis, GBP, SNR in brackets

Out of sample, 2018-2025. 25 or 26 decisions a path (2016-2017) are unscored for want of a book.

| path | n | − E-true | − E-belief | − hindsight, same rows | hindsight − E-true | verdict vs the harder ex-ante chooser |
|---|---|---|---|---|---|---|
| default | 57 | **+744 (4.22)** | **+528 (2.34)** | +215 (1.52) | +529 (2.62) | **BEATS** (+528, SNR 2.34) |
| 61001 | 57 | +399 (0.76) | +69 (0.19) | -42 (0.15) | +440 (1.01) | **TIES** (+69, SNR 0.19) |
| 61002 | 56 | +99 (0.93) | +190 (1.56) | +25 (0.20) | +74 (1.48) | **TIES**, leaning positive (+99, SNR 0.93) |
| 61003 | 56 | +482 (0.77) | +29 (0.09) | +63 (0.21) | +419 (0.83) | **TIES** (+29, SNR 0.09) |

Within 2019-2025 alone, with the two-decision first year removed: capped − E-belief is +392 (2.89),
+4 (0.01), +159 (1.44) and -72 (0.25). capped − E-true is +527 (2.98), -64 (0.23), +89 (0.90) and
-72 (0.25). Once the book has a year in it, the only path the per-customer rule clears is the
default.

**Secondary, all years (pre-registered).** A company with no book charges its own flat rule in
2016-2017. On that basis capped − ex-ante is +2,401 to +2,854, at SNR 2.3-3.8, on every path. **Do
not read that as the choosing winning.** About 2,000-2,300 of it is 2017 alone, and it is there
because the company's own flat rule prices BELOW the base cost. On the default path, its 2017
renewal margin has a median of -2.8 GBP/MWh, and 20 of 24 decisions are below base. This is the
same fact as T4's negative flat totals. It measures how bad the house flat margin is, not what inference earns.
It is reported because I said I would.

**The four paths are not independent samples.** They are the same book under four renewal-dice
seeds, so their SNRs are not pooled here.

### The predictions

- **E1 HELD, 4/4.** E-true's 2018 level is 95 or 15 against a hindsight level of 45-55, and the
  default's 2019-20 level is 30 against 45.
- **E2 HELD, 4/4.** capped − E-true is positive on all four: +744, +399, +99, +482.
- **E3 FAILED, 1 of 4.** On the default path capped − E-true is SNR 4.22, and against E-belief it is
  2.34. I predicted below 2 everywhere.
- **E4 FAILED, 1 of 4 (only 61002).** I predicted that the company's too-steep belief would steer a
  flat chooser further from the right level. It steered it closer: smooth beliefs beat two noisy
  true rows. The miss is the same one that made "E-true is strictest" wrong.
- **E5 FAILED, 1 of 4.** E-true's shortfall to hindsight is 529, 440, 74 and 419 GBP, so under 300
  only on 61002. But the shortfall is mostly the first book year (2018: +217, +463, +11, +554 of the
  capped − E-true difference). After that, it is small.

### What this establishes, and what it does not

- **Against a flat price a supplier could actually have set in advance from its own book, choosing
  per customer is never worse on any path.** Its point estimate is positive against both ex-ante
  choosers on all 8 path-chooser pairs. But it **clears the noise on one path of four (default,
  SNR 2.34 against the harder chooser)** and ties on the other three (SNR 0.09-0.93).
- **The flat-in-advance baseline is weak mainly in its first year with a book**, when it chooses on
  two closed decisions. From the second year it is close to hindsight. So the advantage
  measured here is largely the advantage of not having to WAIT for a book: the value rule prices
  each customer on their own history from the first renewal. That is a real, but narrower, claim
  than "inference beats average".
- **The 2016-2017 years, where a flat supplier has no book at all, are left unscored.** The only
  flat price available there is the house margin, and it loses money. A fairer book-less baseline
  (a market-published margin) is a knowledge question, not a number to pick. It is filed as the
  open edge of this result.
- **Next test of the thesis.** It needs more decisions per path, not another comparator. 56 scored
  decisions a path cannot separate a ~100 GBP edge from noise (SD 107-625). That means the longer or
  larger book the QEP-refit world will run.
