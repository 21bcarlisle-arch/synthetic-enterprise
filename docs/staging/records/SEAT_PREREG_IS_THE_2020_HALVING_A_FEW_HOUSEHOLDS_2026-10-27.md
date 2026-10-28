**Knowledge:** none -- a sample-size test on world-only captures, for the BLOCKING crisis bad-debt finding; no new domain claim

# Is the world's 2020 halving a few households? Two book seeds, pre-registered (2026-10-27)

**Written before either run was launched.**

## Why

The plan split (`SEAT_PREREG_DO_PLANS_END_THE_2020_FAILING_2026-10-27.md`) refutes plans. The world
agrees no plan at all: plan take-up is a named GAP (`PUBLISHED_BASIS.take_up_rate`), so 2,923 offers
go unanswered. The default book's 2019 failed pounds are concentrated. Seven accounts carry about
45% of them in every year and on both dice seeds. Several of these fail **every** bill in 2019, and
one (SYN-2016-549, GBP 1,126 failed of 1,126 billed) fails **none** in 2020 while still billed. The
halving recurs on dice seed 2, but that seed only re-draws payment noise. The households, their
budgets and their income moves are the same. So nothing yet separates "a handful of households'
budgets flip in 2020" from a cause that works across the whole book.

## The runs

The same harness (`/var/tmp/price_held/dump.py`), world-only, at the control arm's code, to
2022-03-31, with `SE_POPULATION_SEED` set to 61101 and to 61102. These are independent casts,
authorised under the seed-family runner (`varied_population_draw_activation.json`). Outputs:
`/var/tmp/price_held/book_{61101,61102}.json`.

## Measure and predictions

The failed share is as in the price-held record: pounds of bills issued in Y that failed, over pounds
billed in Y. The *ratio* is the pooled 2020-21 share over the 2019 share. On the default book it is
0.52.

- **S1 (systematic).** Both seeds' ratios are **at most 0.70**. Then the fall is the world's, and the
  next step is a cause that acts across the book.
- **S2 (a few households).** At least one seed's ratio is **0.85 or more**. Then the default book's
  halving is a property of its cast. The finding's 2020-21 leg then becomes a sample-size statement:
  a bound on what about 300 accounts can show, not a defect to fix.
- A seed between 0.70 and 0.85 is reported as it is, with no verdict from it alone.

## Result (2026-10-28, added after both runs; nothing above is edited). S1 refuted, S2 holds

Graded with `/var/tmp/price_held/grade_books.py`, unchanged. Both runs exited 0 and dumped their
records (61101: 38,505 records over 632 accounts; 61102: 36,478 over 644). They are independent
casts: only 196 and 269 bills match the default cast's (account, issue date, amount).

| cast | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | ratio (2020-21 pooled / 2019) | top 7's share of 2019 failed GBP |
|---|---|---|---|---|---|---|---|---|
| default | 4.21% | 3.37% | 3.62% | 3.80% | 1.87% | 2.10% | 0.52 | about 45% |
| 61101 | 2.91% | 2.07% | 2.69% | 4.60% | 3.46% | 3.06% | **0.710** | 65% |
| 61102 | 2.75% | 2.78% | 3.52% | 3.58% | 3.62% | 3.76% | **1.031** | 64% |

- **S1 (both at most 0.70): REFUTED.** 61101 misses the line by 0.010, and 61102 by 0.33.
- **S2 (at least one at 0.85 or more): HOLDS.** On 61102 the failed share does not fall in 2020-21
  at all. 61101 lands in the no-verdict band. Its fall comes from a 2019 that is high against its
  own 2016-18 (4.60% against 2.07-2.91%), not from a low 2020-21.

**What it means.** The default book's halving is a property of its cast. Across three casts of
about 300 to 640 accounts the ratio runs from 0.52 to 1.03, so at this book size one cast cannot
show a 2020-21 change in the failed share smaller than about half. The finding's 2020-21 leg
becomes that bound. It is not a defect to fix.

**Seen on the way, and not a verdict.** In every cast, seven accounts carry about half or more of
the 2019 failed pounds. That concentration belongs to the world's failure model, not to one cast.
Whether it is real (whether a few households fail repeatedly while most never do) is a separate
knowledge question, and this run does not answer it.

**No next split.** Neither leg names one, so nothing new is launched.
