**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** 4 · **Atom:** `W3_3_the_network_charge_splits_per_unit_and_per_day`

# The W3_3 book cannot carry the network split alone

`background/next_book_requires.yaml` says the W3_3 book "must carry it ALONE: no other world change
between this commit and the build". At 18:50Z on 19 Nov, origin carries these world-side commits after
c71d2521d (`git log c71d2521d..origin/main -- sim/ simulation/`):

- b484f20447, 843143e131: W1_14 ERA5 cells in the weather store the book reads
- f0445b2dcb: stock prepayment households go off supply
- 4accbb828d: W2_30 OCC- gas legs settle on the per-customer shape
- the KNIFE3 commits and 1c5351d187/944eaf3a6f, which state byte-equal or supplier-side replays

The next book is the first since c71d2521d. It is being admitted now, not held, because the 0.12 pair
(THE_VALUE_TEST_REDESIGN s.12f, `vtc-cut012-watch`) lapses on 24 Nov without it, and holding the book
cannot restore isolation anyway: the commits are already on origin.

**What this means for the grade** (SEAT_PREREG_W3_3_..._2026-11-18.md): a move in
`years/<y>/network_cost_gbp` on this book cannot be attributed to the split alone. Weather moves kWh,
and kWh multiplies the per-kWh part. I cannot yet say how much of a move is the split. The
one-variable answer is the W3_3 replay of the prior book (8a300fa561's inputs) at c71d2521d against
its parent, graded per supply-point-day and per kWh. The book's totals are context, not the test.
Writing this before the book exists, so it is a prediction, not an excuse.
