**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` — direction item `b11-read-the-varied-draws-grade-on-the-within-segment-term` · **Subjects:** `EP17_varied_population_draw`

# Pre-registration: the within-segment term on the varied draws, at 2020, 2022 and 2023

**Written 2026-10-19, before any varied-draw book of the B11 prereg exists.** Extends M7 of
`PREREG_B11_PER_CUSTOMER_AGAINST_FLAT_ON_VARIED_DRAWS_2026-10-16.md` to the within-segment term
(`Backtest.departure_ranking_within_segment`, 27ca9dc7a). Its first read is
`SEAT_PREREG_B11_THE_WITHIN_SEGMENT_TERM_ON_8B6FEA024_AND_AD8AFADC5_2026-10-19.md`.

## The premise, re-measured: there are no draws to read yet

The item asked for the varied draws to be read. There are none:

1. **The seeds are not listed.** 61113–61118 are absent from
   `docs/design/curriculum/varied_population_draw_activation.json` on origin. The concern
   `ep17-s-flat-against-per-customer-comparison` in `for_the_director` is still open. No
   member has run, and `tools/book_seed_authorisation.py` refuses all six.
2. **A member could not have been read even after running.** `tools/seed_family.py member` keeps
   a per-home table and a scalar record. It does not keep its run output, so nothing could hand
   a member's book to the backtest. That was the second gap, and it is closed in this
   commit's code.

## What is built (this commit)

Every member now stamps `b11_ranking`: at each of 2020, 2022 and 2023, the key-minus-flat ranking
over the whole book and over same-segment pairs. The key is the one the dual books were read with
(`switch_on_default=True, rescale_over="fit_window"`). The book is folded from the member's own
run (`b11_book`): net margin per leg and month, fuel from the records, segment from the supply
points, and the run's term, bill and move-out registers. It is never the rendered report, which
`annual_report_import_ratchet` refuses to let a tool read; the first landing attempt was refused
there. A cut the book cannot grade keeps its reason. On the published ad8afadc5 book every
settled leg carries a segment, so the fold and the report hand the backtest the same population
labels. `readout` prints
`b11_within_segment`, the within term pooled over the books given: books are independent strata,
so the pooled term is the pair-weighted mean with variance `Σ w² var_b`, the same rule as across
segments inside one book. A book with no interval is named, not pooled.

Printed at real input before the controls were written: on `run_output_ad8afadc5_…132751Z.json`
the stamp reproduces the first read's table exactly: 2020 +0.065 (+0.005, +0.125), 2022 +0.036
(−0.038, +0.109), 2023 +0.074 (−0.015, +0.164). The control pins the stamp to the backtest
called with literal arguments. A mutation of `rescale_over` cannot move the within term, because
the rescale is one constant per segment and so cannot reorder pairs inside one. That is an
equivalence by construction, so the control also pins the whole-book term, and that is where the
mutation fires.

## The decision rule, fixed before any data

- The B11 statement "the key clears flat" requires the **pooled** within term over the six
  `value_arm` books to clear zero at **98.3%** (Bonferroni over the three cuts, z ≈ 2.394) at one
  cut or more. Clearing at 95% only is reported as "suggestive, not established". Anything else
  is "cannot tell", and F11 counts a tie against the thesis.
- Only books from fresh seeds are pooled. The dual books (8b6fea024, ad8afadc5) are one book read
  twice and are never added to the pool. Pooling a book with itself halves the variance, and
  `readout` refuses one seed's homes appearing twice.

## Predictions (six `value_arm` members, 40-founder `all_wins`)

- **Q1.** Accounts graded per book at 2020: 60–250. Departers at 2020: under 60 on every book.
- **Q2.** Per book, the within term at 2020 is "cannot tell" on at least 5 of 6 books (~75%).
- **Q3.** Pooled at 2020: point in 0.00…+0.08 (~65%). The 95% lower bound is above 0 (~40%) and
  the 98.3% bound is above 0 (~25%).
- **Q4.** Pooled at 2022 and 2023: "cannot tell" at 95% on each (~65%). The switching collapse
  after 2021 leaves few departers.
- **Q5.** On each fresh book, whole minus within is within ±0.03 at each cut, on at least 4 of 6
  books (~60%). The flat cross-segment credit seen on the dual books does not recur as a
  systematic term.
- **Q6.** Across the three arms of one seed, the pooled within term at 2020 differs by less than
  its own 95% half-width (~70%). The key reads the book, and the arms move prices more than
  they move who leaves.
- **Q7.** At least one book excludes a segment at some cut, almost always `resi gas` with fewer
  than two departers (~80%).

## What done means for the item

The instrument is landed (this commit). The reading waits on the director's listing of
61113–61118 and then on the eighteen members, so the claim is released. When the members exist,
the read is `python3 -m tools.seed_family readout DIR_VALUE_ARM`, and the grade is appended below.

## Grade

*Appended after the reading. No line above is to be edited.*
