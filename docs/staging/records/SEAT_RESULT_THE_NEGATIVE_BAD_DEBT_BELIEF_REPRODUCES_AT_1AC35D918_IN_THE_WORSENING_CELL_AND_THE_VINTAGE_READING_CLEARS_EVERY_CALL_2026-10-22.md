**Severity:** RECORDED · **Lane:** 0 delivery · **Direction item:** `reproduce-the-negative-bad-debt-belief-at-1ac35d918`

# Result: the negative bad-debt belief reproduces at `1ac35d918`, all of it in the worsening cell, and the vintage reading clears every call

Graded 22 Oct 2026 against
`SEAT_PREREG_THE_NEGATIVE_BAD_DEBT_BELIEF_REPRODUCED_AT_1AC35D918_WITH_THE_OLD_READING_PRICING_ITS_OWN_PATH_2026-10-22.md`,
filed before the full run (`79fcff71c`). The probe was
`/var/tmp/se-belief-probe-1ac/probe.py`, running the `net` arm from the locked worktree
`/var/tmp/se-belief-1ac-wt` at `1ac35d9188`. The code was clean there; only generated observability
files were dirty. Output: `probe_out.json` (15,657 belief calls, 2016-01-01 to 2025-06-03).

**The run is the original run.** Its log is byte-identical to `/var/tmp/se-retnet/net.log` (443,771
lines) up to the line naming the output path. It made 108 offers and its `total_net` is £600,835.40,
both the same as the original. The wrapper observed the run and changed none of its decisions.

## Predictions

- **P1, the defect reproduces: HELD.** 28 calls read below 0 under the old reading, from −0.008267
  to −0.004556. All three of the original guard values (GOOD −0.008267, POOR −0.004637, POOR
  −0.005272) are among them, matched to 6 d.p. One caveat on method: this probe called the arm
  tool's own `main()`, and its guard rows carry no `belief_rate` field (351 rows, against 240 from
  the `se-retnet` wrapper). So the match is made on the door's returns, not on the guard rows.
- **P2, the vintage reading clears it: HELD.** 0 of 15,657 calls read below 0 under the vintage
  reading. On the 28 calls where the old reading was negative, the vintage reading runs from 0.0089
  to 0.0174.
- **P3, where it sits: REFUTED on both counts.** All 28 negative calls are in `worsening`, not
  `in_arrears_steady`. That cell's old minimum here is 0.0027. One call is dated 2018-03-06, in a
  7-account-year cell. The other 27 run from 2024-07-20 to 2025-05-20, in cells of 262 to about 280
  account-years. Those cells are not thin. The 2024 negatives are driven by large arrears paydowns
  credited to the year they cleared: PROS-2020-0189, standard credit, −£992.70 against £2,286.25
  billed; SYN-2016-256g, −£219.47. That is the mechanism `793989589` names. The thin-cell guess was
  wrong.
- **P4, the whole book: HELD.** At the last call, `*|*` reads 0.0022 under both readings, with the
  charge £5,692.78 under both. The cells move a lot: `*|worsening` goes from −0.0059 to +0.0092, and
  `*|no_debt` from 0.0020 to 0.0006. The book total does not move. (The vintage tabulation counts
  £40,331 more prepayment billed, at zero charge. That moves no rate.)

## What it means

The vintage fix (`793989589`) has now cleared a negative belief at real inputs, on the path where
the old reading produced one. It is no longer exercised only on synthetic controls.

The negative belief did not change a decision in the original pair. All three negative guard rows
were offered both netted and unnetted (`offered: True, offered_unnetted: True`). The defect priced
three offers about £3 too cheaply in contribution terms and flipped none.

**I cannot yet say why `793989589`'s path never went negative.** At this tree the negatives arrive
from mid-2024, in a cell of about 260 account-years. The path and the 78 commits between the trees
remain confounded, as the prereg said. The one-variable leg (the old door restored at `793989589`'s
tree) is still named and still not owed by this item.
