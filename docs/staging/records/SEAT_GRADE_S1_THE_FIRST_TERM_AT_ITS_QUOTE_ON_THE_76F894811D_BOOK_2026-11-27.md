**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `PB3_book_growth_as_earned_outcome` · **Claim:** `s1-r1-to-r5-are-graded-on-the-76f894811d-book`

# S1 graded: R1–R6 on the 76f894811d book

*Delivery seat, 27 Nov 2026. This grades R1–R6 of
`SEAT_PREREG_THE_FIRST_TERM_CONTRACTED_AT_ITS_QUOTE_2026-11-24.md` on
`docs/reports/run_output_76f894811d_20261126T155009Z.json`. 76f894811d descends from a1eee4d92, and the
switch is `True` at that commit (`simulation/live_population.py:1207`). The method was filed in
`/var/tmp/se-s1grade/PREDICTION.md` before any R figure was read. The probes are `probe2.py` to
`probe4.py` beside it. `rows4.json` has one row per leg, and each probe was run from a 76f894811d
worktree. The switch-off book is `run_output_f2c6979d01_20261124T215935Z.json`. 131 commits separate
the two books, so any comparison between them is read only where the switch is the one thing that
can move it. Nothing is flipped here.*

**Where each rate is read from.** The book does not publish a term's pre-chain strike for these legs.
It writes no `struck_by` marker, and the term-0 default-belief allowance (`run_phase2b.py:3871`) is
not a `rate_decomposition_log` cause, so 140 of the 144 legs have no decomposition entry. So R2 is
graded on the rate each first term was **billed** at (`account_state_log`, `term_index` 0). That rate
is compared with the quote and with the notice-date strike, both re-derived at the book's commit and
seed.

| # | prediction | measured on the book | verdict |
|---|---|---|---|
| R1 | Campaign exact: 242 wins, 3,089 quotes | The campaign re-resolved at 76f894811d gives **242 wins and 3,089 quotes**. The book's 242 won PROS accounts are **the same set** (the 4 `_3` ids are occupier successors). The same 242 appear in the f2c6979d01 book. | **HELD** |
| R2 | Each of the 144 quoted fixed resi elec first terms is struck on its quote, not on `notice_date_unit_rate` | All 144 have a term-0 row starting on the won day. Quote and notice-date strike differ by more than 2.5% on **134** legs, and **134 of 134** are billed nearer the quote. 140 legs are billed at quote × a factor that depends only on the date: **1.0034 to 1.0200**, the same for every leg won on the same day, falling from 2016 to 2025. That factor is the default-belief allowance. The other 4 are capped (R3), and their decomposition `rate_before` is quote × 1.004. **No leg is billed at its notice-date strike.** In the f2c6979d01 book, 136 of 144 sit nearer the notice-date strike. | **HELD** (graded on the billed rate; the pre-chain rate itself is not published, see GAP) |
| R3 | Legs the hold touches: **0**, range 0–6, all in 2021 Q3–2022 and 2025 Q1 | **4**: PROS-2021-0212 (10 Jun 2021, −£3.35/MWh), PROS-2021-0385 (16 Nov, −£2.27), PROS-2021-0396 (12 Dec, −£7.69) and PROS-2021-0399 (20 Dec, −£13.73), the last three clamped to the Oct-21 cap of 184.07. The switch-off book clamps 16. | **Range HELD, point MISSED**. One leg (Jun 2021) also falls outside the named window. |
| R4 | £ the hold removes per win: **£0.0**, range £0–3 | **£0.29 per win** (4 clamps × world EAC, over 242 wins) | **HELD** in range, point missed |
| R5 | First-year billed revenue ON − OFF: **+£30.9/win**, range +£15 to +£50. 2023 +£183/leg (+100 to +260), 2024 +£73 (+40 to +110), 2021 −£24 (−60 to 0) | **+£32.0/win** (book term-0 rate − probe OFF chain, × EAC). 2023 **+£186.1**, 2024 **+£75.2**, 2021 **−£27.3**, 2016–20 +£32 to +£58. Comparing the two books directly gives **+£31.7/win**. | **HELD** on every leg of it |
| R6 | MSC-window won switches (14 Apr 2022 – 31 Mar 2024) = 44 | **44** | **HELD** |

**Correcting R3's mechanism beside it.** The pre-registration named "a positive portfolio premium" as
what pushes a quote gated just under the cap over it. In the book, `portfolio_premium_pct` is null on
every won first term. The push comes from the **term-0 default-belief allowance**: +0.40–0.42% in
2021, applied before the cap, which lifts a quote that sits under the cap by less than that over it.
The pre-registration's own GAP ("the chain's term-0 writers still move a carried quote") is the
mechanism. It fired 4 times, below R3's tripwire of 6. So "the term-0 writers are re-striking past
the quote" is **not** refuted as the next finding, but the writer is the allowance, not the premium.
The switch-off book's 16 clamps against the probe's 13 are the same allowance adding 3. The
2021-06-10 clamp is below the Apr-21 cap window that R3's "2021 Q3" assumed. I cannot yet say why
that one quote sat so close to the cap.

**What R5 does and does not attribute.** The probe's OFF arm has no allowance. The book's ON rate
carries it. So up to about £1/win of the +£32.0 is the allowance, not the switch. Book against book
gives +£31.7, but the books are 131 commits apart. Both routes sit inside +£15 to +£50, and the per-year
shape (2023 and 2024 up, 2021 down) matches the probe's, so the verdict does not depend on which
route is used.

**Not attributable, and not graded.** Company-side acquisition attempts are 3,200 on f2c6979d01 and
3,194 here, with 445 wins on both. That is the company funnel, not the campaign, and nothing the switch
touches reaches it. The 131 commits are the candidates.

## What S2's STEP 0 reads from this

- **The switch acted after the win and on the strike only.** R1 and R2 held, so the off-rule (revert)
  does not apply.
- **The arm `FIRST_TERM_CAP_HOLD_DELETED` will move 4 legs on S1's seeds, not 0.** These are the four
  2021 clamps above. That is inside R3's 0–6, so per the order record (§3 S2), **#2 does not need a
  standing book of its own**, and S2 runs as the arm. Its amendment should carry **4 legs, about £0.29
  per win** as the point to beat. Those are the legs where the default-belief allowance lifts a quote
  over the cap, and deleting the hold bills them above the cap (SLC 28AD: the cap binds a default
  tariff, not a fix). Whether the allowance belongs inside the quote is the decision the
  pre-registration's GAP left open. It is now the only thing between the quote and the bill.

## GAP

- **The pre-chain strike is not published.** `rate_decomposition_log` omits a term whose only writer
  is the default-belief allowance. Where it does log a term, `unit_rate_original` is the rate *after*
  that allowance, not the struck rate. The 4 capped entries read quote × 1.004 as their "original".
  So a published "original → contracted" span leaves out one writer. R2 here is an inference from the
  billed rate, and it is clean only because the allowance is at most 2% while the quote and the
  notice-date strike differ by more than 2.5% on 134 of 144 legs. The 10 legs where they differ by
  less than that could not tell the two strikes apart. Nothing was built for this. It is the next
  session's to file if a reader needs the strike itself.

**Reverse:** revert this file and the one-line pointer in the pre-registration. Nothing else changed.
