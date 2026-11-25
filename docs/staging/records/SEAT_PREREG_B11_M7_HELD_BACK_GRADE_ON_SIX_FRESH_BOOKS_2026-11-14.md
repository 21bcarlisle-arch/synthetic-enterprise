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

## Grade, read 2026-11-25

Read at origin `86b52aa88c` from `/var/tmp/b11m7/readout.json` (written 02:50Z, `readout rc=0`,
`readout.err` empty, `refused_members: []`) and the six `member_*.json` stamps beside it.

**Order** (`order.log`): rankq ended 20:03Z on 24 Nov. The owed book was
`run_output_f2c6979d01_20261124T215935Z.json`, logged 23:48Z. The land10 wait returned rc=0 at
01:00Z. Then wave 61113–61115 ran at 01:00Z, wave 61116–61118 at 01:50Z, and the readout at
02:50Z. So the owed book ran before any member did.

**The pin check. The SHAs differ from the pin, but the code is the pin's, so no member is
refused.** No member stamps `16e8323701`. Members 61113–61115 stamp `71930d4d04` and members
61116–61118 stamp `35aa0e8172`. Both commits are `SALVAGE(auto)` descendants of the pin, made in
the pinned worktree while the members ran (01:36Z and 02:26Z, with `df2bbb82f5` between them).
`git diff --stat 16e8323701 35aa0e8172` touches six files, none of them code:
`docs/context-handshake-latest.md`, `docs/observability/{book_growth_campaign,
book_subset_verdict, coupled_gap_ledger, fidelity_evidence_ledger}.json` and `token-log.md`. The
two `simulation/live_population.py` records (`_CAMPAIGN_RECORD`, `_SUBSET_VERDICT_RECORD`) are
written and never read (`git grep` at the pin finds only `write_text` uses). So the salvage
committed the members' own outputs. The six members ran the pin's code, and refusing them would
refuse the pin itself. Read literally, the rule refuses all six, which leaves M7 at "cannot
tell" with 0 of 6 books. I read it by its purpose, and say so here. The worktree has since been
removed (`/var/tmp/b11m7-tree` is absent), so re-running needs a fresh worktree at the pin.

**Per member** (within term: key minus flat, 95% interval; the member's own `b11_ranking`):

| seed | 2020 graded / departed | 2020 within | 2022 within | 2023 within | whole − within (2020, 2022, 2023) | pairs excluded |
|---|---|---|---|---|---|---|
| 61113 | 132 / 54 | +0.006 [−0.048, +0.059] | +0.067 [−0.016, +0.149] | **+0.095 [+0.017, +0.173]** | −0.009, **−0.051**, **−0.038** | 2022: 10 |
| 61114 | 125 / 60 | +0.048 [−0.009, +0.105] | +0.008 [−0.081, +0.096] | −0.022 [−0.112, +0.069] | **−0.030**, +0.004, −0.020 | 2020: 6 |
| 61115 | 130 / 60 | +0.056 [−0.007, +0.119] | −0.028 [−0.123, +0.068] | +0.042 [−0.049, +0.132] | +0.009, +0.012, +0.012 | 2020: 1 |
| 61116 | 139 / 67 | +0.049 [−0.008, +0.106] | +0.059 [−0.022, +0.140] | **+0.092 [+0.025, +0.159]** | −0.022, +0.005, −0.018 | 2023: 9 |
| 61117 | 129 / 54 | **+0.060 [+0.007, +0.113]** | −0.051 [−0.154, +0.051] | +0.063 [−0.028, +0.153] | +0.022, +0.027, **+0.030** | 2022: 8; 2023: 9 |
| 61118 | 124 / 55 | −0.006 [−0.080, +0.068] | −0.063 [−0.169, +0.044] | +0.057 [−0.030, +0.144] | +0.002, +0.021, −0.011 | 2020: 6 |

**Pooled** (`b11_within_segment`, six books; no book is unpooled). The 98.3% bound is the 95% se
times z = 2.394:

| cut | pairs | point | 95% | 98.3% | under the 19 Oct rule |
|---|---|---|---|---|---|
| 2020 | 14,339 | +0.035 | [+0.010, +0.059] | [+0.004, +0.065] | **clears 98.3%** |
| 2022 | 13,997 | +0.002 | [−0.035, +0.040] | [−0.044, +0.049] | cannot tell |
| 2023 | 21,026 | +0.057 | [+0.023, +0.091] | [+0.015, +0.099] | **clears 98.3%** |

**Verdict under the rule: "the key clears flat".** The pooled within-segment term clears zero at
98.3% at two of the three cuts, 2020 and 2023. It does not clear at 2022. On campaign-win-heavy
40-founder `all_wins` books, out of sample, the switch key ranks who leaves better than flat
within segment. That is a ranking result, and it is small: about 3.5 to 6 points of AUC. It does
not say the key's departure level is calibrated. That level is the annual report's held-back
grade, and the member does not stamp it.

**Predictions**, filed blind on 19 Oct and 14 Nov, graded as written:

- **Q1: refuted.** Graded at 2020 was 124–139 on every book, inside 60–250, so that part held.
  "Departers under 60 on every book" failed on three books: 60, 60 and 67. Departers ran 54–67,
  not the 27–33 this record's size re-read expected. The re-read used a home-level fold
  (`first_settled + tenure_days`, not still supplied). Re-run on these six books, that fold gives
  24–37 departers. The backtest's departer is an *account* whose last month is before
  `book_end` (`forward_clv.py`, `AccountForecast(..., a.last_month < book_end)`). **I cannot yet
  say** what the extra departers are; the definitions differ by about 1.7×. More departers make
  the interval narrower than the re-read sized it. That is one reason the pooled 95% half-width
  came out at 0.025 at 2020, not the 0.033–0.039 predicted.
- **Q2: held.** At 2020, 5 of 6 books cannot tell (61117 clears 95%).
- **Q3: held, on all three parts.** The pooled point is +0.035, inside 0.00…+0.08 (~65%). The 95%
  lower bound is above zero (~40%). The 98.3% lower bound is above zero (~25%), so the
  least-likely leg came in.
- **Q4: refuted.** 2022 cannot tell, as predicted. 2023 clears 98.3%. The "switching collapse
  after 2021 leaves few departers" did not happen in the account count: 29–44 departers per book
  at 2023, and 21,026 within pairs, the most of any cut.
- **Q5: refuted, narrowly.** Exact |whole − within| ≤ 0.03 at every cut held on 3 of 6 books
  (61115, 61116, 61118), against "at least 4". 61113 fails at 2022 (−0.051) and 2023 (−0.038).
  61114 fails at 2020 (−0.0305). 61117 fails at 2023 (+0.0302). Most whole-minus-within terms
  are negative (whole below within), which is the opposite sign to the dual books' flat
  cross-segment credit. So that credit did not recur as a systematic positive term. The
  ±0.03 band as written fails.
- **Q6:** dropped (one arm).
- **Q7: held in count; its segment clause is unread.** All six books exclude pairs at some cut
  (`pairs_excluded` > 0). By `_ranking_within_segment`, that is a segment with fewer than two
  departers or two stayers. The stamp keeps the pair count but not `segments_excluded`, so
  "almost always `resi gas`" cannot be read from it.
- **The 16 Oct headline**, "cannot tell on each book; pooled point positive, interval includes
  0": its first part held at 2020 (5 of 6) but not at 2023 (2 of 6 clear 95%). The second held.
  The third was refuted: the pooled interval excludes 0 at two cuts.

**Founder leg, counts only** (home-level fold, the same approximate fold as the size re-read,
not the backtest's count). Founders on the book, then founders supplied on 2020-12-01, then those
of them not still supplied:

| seed | 61113 | 61114 | 61115 | 61116 | 61117 | 61118 |
|---|---|---|---|---|---|---|
| founders | 36 | 36 | 36 | 36 | 36 | 35 |
| graded at 2020 | 11 | 13 | 11 | 15 | 11 | 15 |
| departed | 3 | 0 | 1 | 1 | 1 | 2 |

That is 76 graded founders and 8 departures in total. As filed, M7 is a campaign-win grade. The
founders cannot carry a ranking.

**End-to-end.** The result agrees with the dual books' within term at 2020 (+0.065, interval
+0.005 to +0.125), at about half its size. That is the "transfers, smaller" case: the
pre-registered rule applies, and it clears. These are the explanations the evidence allows,
ranked by evidence:

1. **The key carries real within-segment information.** This is consistent with every per-book
   point except 61118's 2020 and the 2022 cut.
2. **Partly an artefact of the departer definition.** An account-month departer may count leg
   ends that are not departures (the 1.7× gap). That should add noise to the departer set and
   pull the term toward zero, not manufacture a positive term. But an artefact that correlates
   with being on default at the cut could inflate it, and I have not excluded that.
3. **2022 is the crisis regime.** Departures there are driven by supplier failure and price caps,
   not by the household's own switching hazard. A null there is expected, not a contradiction.

The open item that would most change this verdict is (2). It goes into B11's record as the next
check, not a precondition: the rule was fixed with this instrument, and the instrument's
departer definition is the one used on every B11 read since 11 Oct.

**B11 moves 2 → 3** on this grade, recorded self-certified (`gate_authorizations.jsonl`). Reverse
it by reverting the commit that carries this section; the members stay on disk at
`/var/tmp/b11m7/m7/`.
