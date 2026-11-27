**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` s.8.8a choice 37

# Result: a failed level final nets the world's credit from the level surplus (2026-11-27)

The finding is `docs/staging/SEAT_FINDING_A_FAILED_LEVEL_FINAL_OPENS_A_CASE_ON_CREDIT_THE_WORLD_NETTED_2026-11-27.md`.
Its predictions were written there before this build. They are graded here on a replay of the page walk
(`resolved_settlement` with the refund log's set-offs and the switching credits, as
`tools/generate_billing_ledger.generate` calls it) over the 601887d76a book. The old engine is origin/main's,
and the new one is the working copy (`/var/tmp/flfn/replay.py`).

| Prediction | Before | After | Verdict |
|---|---|---|---|
| OCC-cede70b10116g's case is 8.96 or less | 92.50 (104.68 less 3.22 credit and 8.96 set-off) | 8.96 at the due date, then 0.00 after the 8.96 set-off (92.50 drawn from the level surplus) | held |
| PROS-2024-0270g's case is 13.27 or less | 54.08 | 13.27 (40.81 drawn); the write-off at close is still 13.27 | held |
| No leg's closing balance moves | | 0 of 864 closing balances change, and 0 of 224 write-offs change | held |

**Not predicted: a third leg moved.** SYN-2016-519g's Nov 2017 gas final (24.14, failed, level) carries
`credit_taken_gbp` 5.80. It now nets that 5.80 as credit. Its case falls from 6.43 to 0.63, which is the
world's ask (18.34) less the 17.71 the household repaid. This is the same class as the other two. It was
missed because the grading record listed only legs where the page sat ABOVE the world by more than its
threshold. No other credits row changes (3 of 1,949).

Control: `tests/simulation/test_a_final_bill_resolves_on_what_the_world_asked.py::test_a_failed_level_final_nets_the_worlds_credit_from_the_surplus_and_the_close_holds`.
Three mutations fail it: no draw, no add-back at the close, and no cap at the surplus. A fourth, dropping
the `on_level` guard, passes. That is an equivalence, not a missing test: an off-level leg has no
`level_collection_difference` row, so its surplus is 0 and the cap already refuses.

Named limit: the published page changes only when the next book is published. This record grades the walk
on the existing book, not the rendered page.
