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

## Grading

Below, after the scores.
