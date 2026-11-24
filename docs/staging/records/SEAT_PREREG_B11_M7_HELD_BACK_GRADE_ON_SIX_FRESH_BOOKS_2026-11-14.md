**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` · **Subjects:** `EP17_varied_population_draw` · **Claim:** `b11-m7-held-back-grade-on-fresh-books-is-preregistered-and-seeded` (Lane 0 delivery)

# Pre-registration: B11's held-back grade (M7 only) on six fresh 40-founder books

Written 2026-11-14 at origin `d7b9f0d32`, before any member on seeds 61113–61118 exists. No
member on these seeds has run under any arm.

## Why M7 stands alone now

The 2026-10-16 prereg (`PREREG_B11_PER_CUSTOMER_AGAINST_FLAT_ON_VARIED_DRAWS_2026-10-16.md`)
planned eighteen members: six seeds, three arms. Its money and selection legs (M1–M6) now belong
to `docs/design/THE_VALUE_TEST_REDESIGN.md`. Rule 1 there is one book at one commit. Rule 2 is a
book big enough to tell £3 per household-year from zero, and a 40-founder book is too small. So
those legs are dropped here, and nothing below grades them.

M7 is different. It is B11's own forward-value grade, made out of sample on books the model was not
built on. Nothing in the redesign computes it (B11 simplification record, 2026-11-14 park re-read).
It needs no flat arm, so this run is **six `value_arm` members only**.

## The seeds

61113, 61114, 61115, 61116, 61117 and 61118 are listed in
`docs/design/curriculum/varied_population_draw_activation.json` in the same commit as this
record. The listing is made under the director's 2026-10-15 ruling ("a fresh draw per run, as
canon F13 says"). It quotes the 26 Oct advisor steer, s.1 item 5, which put "EP17 seeds
61113–61118 under the 15 Oct ruling" among the items that are "not reserved. Close them yourself
on your own recommendation". `tools/book_seed_authorisation.book_seed_authorisation_refusal` now
returns None for the six. For 61119 it still refuses, which is the control.

## The instrument, the rule and the predictions: inherited, not re-written

M7's instrument changed on 2026-10-19. The member now stamps `b11_ranking`: at cuts 2020, 2022 and
2023, the switch key's departure ranking minus flat's, over the whole book and within segment.
`readout` pools the within term over books (`tools/seed_family.py`, `b11_ranking` and `pool_b11`).
The decision rule and predictions Q1–Q5 and Q7 in
`SEAT_PREREG_B11_THE_WITHIN_SEGMENT_TERM_ON_THE_VARIED_DRAWS_2026-10-19.md` are this run's. They
are not restated here, so that one rule cannot have two copies. **Q6 is dropped**, because it
compares the three arms and only one arm runs. The 2026-10-16 M7 line ("cannot tell on each book;
pooled point positive, interval includes 0; flat level over-predicts departure on every book")
stays the headline prediction. Its third part is not read: the member keeps the ranking terms,
not the level.

## The re-read of "cannot tell on each book" against the book's size (before anything runs)

The task asked for this check before any run. **What each count counts:** an account is a
billing account. It is *graded* when it is supplied on 2020-12-01. It is a *departer* when it is
graded and no longer supplied at the end of the book. Neither count is per year.

The sizes come from the four 40-founder `all_wins` members that already exist: seeds 61109–61112,
commit `ee5f86db0`, `/var/tmp/provgrade/out/homes_*.csv`. Those members carry **no `b11_ranking`
stamp**, so only their sizes were read, never a grade. The fold is approximate:
`first_settled + tenure_days`, not the backtest's own count.

| seed | homes | graded at 2020 | departers | stayers | founders graded | founder departers |
|---|---|---|---|---|---|---|
| 61109 | 453 | 129 | 33 | 96 | 16 | 1 |
| 61110 | 478 | 115 | 27 | 88 | 13 | 0 |
| 61111 | 521 | 143 | 30 | 113 | 15 | 1 |
| 61112 | 457 | 112 | 27 | 85 | 15 | 1 |

Here is how that compares with the one measured width. On the 400-founder book `8b6fea024`, the
within term at 2020 had se 0.030 from 75 departers and 109 stayers (27ca9dc7a, as re-read in
`SEAT_FINDING_B11_SIX_SEEDS_CAN_RESOLVE_..._2026-10-21.md`). Scale it to about 29 departers and 95
stayers. If the departer term carries the whole variance, se ≈ 0.048. If it carries half, se ≈
0.041. **The per-book 95% half-width is therefore about 0.08–0.09.** The largest within effect
ever measured at 2020 is +0.061 to +0.075, on the dual books. That is below the per-book
half-width, so **"cannot tell on each book" stands, and is if anything firmer**. Pooled over six
books, the half-width is about 0.033–0.039 at 95%, and about 0.040–0.047 at the 98.3% Bonferroni
bound.

**So the pooled result depends on whether the dual books' effect transfers.** If it does, the pooled
term clears 98.3%. Q3 puts that at about 25%. I keep Q3 unrevised, for this reason: a 40-founder
`all_wins` book is about nine-tenths campaign wins at the cut, which are selected new shoppers,
while the dual books are the 400-founder production shape. I have not measured their founder
share at the cut. The arithmetic says the run *can* resolve the effect. It
does not say the effect is there.

**The founder leg cannot be graded, by construction.** The director's 2026-10-10 condition 1 asks
for founders and wins to be reported apart. A book grades 13–16 founders at 2020, with 0–1 founder
departers. Pooled over six books, that is roughly 3–6, and an AUC needs a departer on each side of
every pair. `pool_b11` is whole-book only, and `readout --where` does not reach it. **M7 is
therefore a campaign-win grade and will be quoted as one.** The founder leg is reported as its
counts (graded, departed) with "too few to tell". The result is not extrapolated to the
400-founder book.

## Launch condition and shape

- **Not before** the churn_roll family (redesign s.8) is graded and candidate A (s.9) has released
  the memory budget. The value test goes first (13 Nov steer).
- One origin commit is pinned for all six members and read from each member's stamp. A member
  whose stamp disagrees is refused, not pooled.
- The members are `python3 -m tools.seed_family launch --seeds 61113,...,61118 --policy value_arm
  --shape all_wins --out /var/tmp/b11m7 --tag m7`, in waves no wider than `--parallel`, with
  admission deciding. At `ee5f86db0`, a member's peak was 2.37–2.73 GB (cgroup) and its wall time
  was 62–74 min. Re-read both from the first member's own stamp. Do not quote these figures as
  current.
- The read is `python3 -m tools.seed_family readout /var/tmp/b11m7`, field `b11_within_segment`.
  It is graded against the 19 Oct rule and appended below.

## Grade

*Appended after the reading. No line above is to be edited.*

## Not launched, 14 Nov 19:46Z: the launch gate is unmet

Drawn as `b11-m7-six-fresh-value-arm-members-are-run-and-graded`. The item's own gate says "do not
launch before the `churn_roll` family (THE_VALUE_TEST_REDESIGN §8) is graded and candidate A (§9)
has released the memory budget". At 19:46Z neither holds: `/var/tmp/vtcr-out/` holds 2 of 12
member/control pairs, the third (`55555_66666`) is running under `/var/tmp/vtcr-driver/driver.py`,
and §8 puts the read at about 09:00Z on 15 Nov. Candidate A has not launched (§9: one draw about
1.5 h, twelve about 19 h). No member on 61113–61118 exists, so the predictions above remain filed
blind. **Earliest launch:** after candidate A's driver exits, on one pinned origin commit,
`tools.seed_family launch --policy value_arm` over the six seeds in waves within `--parallel`.

## Not graded, 24 Nov 15:50Z: all six members are GAP, and the six are declared behind rankq and the owed book

The launch gate above is now met: churn_roll was graded in redesign s.10 on 15 Nov, and candidate A
was run and graded through s.12. Drawn as `b11-m7-held-back-grade-on-the-six-fresh-books`, at
origin `16e8323701`. The question was whether a run output already on disk can feed this grade. The
grade's reader is `tools.seed_family` `b11_ranking`, which goes through `forward_clv.book_from_run_output`.
That reader needs `years[*].per_customer_monthly` and `per_customer_lifetime`, or a member's stamp.

| seed | grade | why |
|---|---|---|
| 61113 | **GAP** | No member, run output or launch record exists under any arm. Searched: `/var/tmp` (depth 4, with `vtn-out/rankq` pruned), the seed stamps in `docs/reports/**/*.json`, and the 499 rows of `docs/observability/.launch_records.json`. |
| 61114 | **GAP** | Same: no output anywhere. |
| 61115 | **GAP** | Same: no output anywhere. |
| 61116 | **GAP** | Same: no output anywhere. |
| 61117 | **GAP** | Same. The only files on disk are `/var/tmp/vtn-driver/ids{,2}_61117.json`. These are population probes (customer traits at import), not runs. |
| 61118 | **GAP** | **Correction to this record's opening line.** Redesign s.12g (21 Nov) and rankq (running now) use **population seed 61118**, with churn pair 13131/14141. So `/var/tmp/vtn-out/{A,cut,twin}/*_13131_14141.json` are 61118 outputs. They cannot feed M7 for three reasons. (1) They hold per-account net totals and decisions, but no `years` / `per_customer_monthly` and no `b11_ranking`, so the grade's reader cannot rebuild a held-back book from them. (2) They are the 698-founder production shape, not this record's 40-founder `all_wins` shape. (3) They pair a value arm with a control, which is not a `value_arm` member. Nothing in them is a departure ranking, so no M7 prediction has been exposed to them, and the predictions stay blind. `rankq/` was not opened. |

**Pooled M7: cannot tell, 0 of 6 books.** No prediction is revised.

**Declared, not run now.** User unit `b11m7-watch` runs `/var/tmp/box-plan/b11m7/arm.sh` (sha256
`d60d685c…`), from the pinned worktree `/var/tmp/b11m7-tree` at `16e8323701`. It refuses if that
tree is not at the pin or is dirty. It does four things, in order:
1. It waits for rankq (`longjob-value-test-s12g-rankq`, pid 1718464) to exit.
2. It waits up to 6 h for sim-runner's owed book: the first dated `run_output_*` after rankq. It
   logs which book that was, or "none".
3. It runs `tools.seed_family launch --policy value_arm --shape all_wins --out /var/tmp/b11m7
   --tag m7` in two waves of three (61113–61115, then 61116–61118). Each member declares itself
   through `launch_long_job` at the seed-family default peak of 3,500 MB. The order is logged to
   `/var/tmp/b11m7/order.log`.
4. It runs `seed_family readout /var/tmp/b11m7/m7`, which writes `/var/tmp/b11m7/readout.json`.

Unlike what the drawing item asked, the waiting unit is not a `launch_long_job` unit.
`resource_headroom.running_long_jobs` makes sim-runner yield to any declared long job with a live
process, and `sim_runner.queued_long_jobs` makes it yield to any queued one. So a long job waiting
here would hold off the very book it waits behind until the 6 h fallback. This is the same pattern
as `s12g-rankq-watch`.

**Reverse:** `systemctl --user stop b11m7-watch`, then stop any `longjob-seed-family-m7-*`.
**Next read:** grade `readout.json`'s `b11_within_segment` under the 19 Oct rule. Append the result
at the end of this file under `## Grade, read <date>`, without editing any line above it.
