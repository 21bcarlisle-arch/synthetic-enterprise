**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` — measurement instrument; direction item `why-the-switch-key-lost-its-2023-whole-book-clearance-on-the-dual-book`

# The switch key's whole-book gain over flat was two-thirds flat's own inverted gas segment

Evidence and grade:
`docs/staging/records/SEAT_PREREG_WHY_THE_SWITCH_KEY_LOST_ITS_2023_WHOLE_BOOK_CLEARANCE_ON_THE_DUAL_BOOK_2026-10-19.md`.

**What was measured.** `ranking_between` and `Backtest.departure_ranking` compare the key with
flat over every departer–stayer pair in the book. Within a segment, flat gives every account the
same p, so it scores exactly 0.5 there. Across segments, it ranks by segment hazard. At 2023 on
`78f77c34e`, flat's cross-segment AUC was **0.409**, worse than chance: `resi gas` had the highest
flat departure p (0.284) and 2 departures in 37. The key's 36+ band pushed those homes down, and
that repair contributed 0.087 of the published **+0.133**. On the dual book (`8b6fea024`) the gas
homes are dual, flat's cross term is 0.545, and the figure is +0.075. The key's own AUC rose
(0.580 → 0.592).

**Why it matters.** The whole-book "key − flat" figure credits the key for whatever its baseline
gets wrong, and a re-segmentation of the book can move that credit by more than the key's own
contribution. The clearance the seat carried as the thesis's central reading was mostly this
credit.

**The change (ours, reversible, no ruling touched).** Report the **within-segment term** beside
every whole-book ranking: `Ranking`'s difference restricted to departer–stayer pairs in the same
segment, with its own interval (a stratified DeLong, or a bootstrap over accounts within segment).
Do not replace the whole-book figure. Show both, and grade "the key clears flat" on the
within-segment term. Readings today: within-segment key − 0.5 at 2023 is **+0.108** old and
**+0.075** new. Their intervals are owed by this item. Do not change the key itself.

**Smallest control.** Use a synthetic book with two segments, where flat's segment order is the
reverse of the departure rates and the key carries no within-segment information (a constant
multiplier). The whole-book difference must be positive and the within-segment difference must
be 0.

**Downstream.** `docs/staging/records/PREREG_B11_PER_CUSTOMER_AGAINST_FLAT_ON_VARIED_DRAWS_2026-10-16.md`
grades B11 across varied population draws. Each draw re-cuts which segments flat mis-orders, so
its whole-book difference carries this credit as a varying term. Read its spread across draws
next to the within-segment term, or a wide spread will be read as seed noise in the key.

**Built and read (2026-10-19 ~18:55 BST, worker).** `Backtest.departure_ranking_within_segment`
(`WithinSegmentRanking`, stratified DeLong) now prints beside `departure_ranking`. The control is
`test_a_key_that_only_reorders_segments_clears_flat_on_the_whole_book_and_not_within`, and the
mutation `within-pairs-across-segments` reds it. The read on `8b6fea024` and `ad8afadc5` (unpublished)
gives: **2020 clears** (+0.061 (+0.002, +0.120); +0.065 (+0.005, +0.125)), **2022 and 2023 cannot
tell**. **B11: cannot tell at this width.** Grade and reasons:
`docs/staging/records/SEAT_PREREG_B11_THE_WITHIN_SEGMENT_TERM_ON_8B6FEA024_AND_AD8AFADC5_2026-10-19.md`.
