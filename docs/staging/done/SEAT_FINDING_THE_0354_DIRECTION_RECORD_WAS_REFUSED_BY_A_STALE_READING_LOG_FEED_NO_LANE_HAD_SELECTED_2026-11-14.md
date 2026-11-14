**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `unminted`

# The 03:54 direction record was refused by a stale reading-log feed that no lane had selected (2026-11-14)

*Claim `the-direction-record-reaches-origin`. Parts (a) and (b) are done in the commit that carries this
file. Part (c) was already spent when the claim was drawn.*

## (c) Spent before the draw

`a23001d35d` (06:50Z) landed the record oriented at 06:23:39Z 14 Nov, carrying DIRECTION.yaml,
decisions.jsonl and the stretch log. That meets the item's "after 06:00" bar. The shared tree read
`git rev-list --count HEAD..origin/main` = **0** at draw time. The door already graded all three paths
`already landed`. Nothing was re-landed. The duplicate-work note pointed at
`weekly-balance-review-2026-11-16-proposal`. That is a different piece of work on the same file, so no
disposition was taken against it.

## (a) The red test, named

Reproduced in a clean worktree at `cc27c048ec` (origin at 03:52Z), **with no direction record applied**,
running `pytest site/`:

    FAILED site/knowledge/test_the_reading_log_door.py::test_the_committed_feed_is_what_the_log_builds_today
    1 failed, 1896 passed, 159 skipped in 681.73s

So it was **red on origin alone**. It is a site-lane defect, not a reader of a direction field.

**Cause.** `db80910fa0` (20:00Z 13 Nov, the advisor actioning) edited `docs/institutional/reading_log.md`.
It did not regenerate `site/data/reading_log.json`. The site lane selects tests only for `site/**`
edits, `site/data/**`, `tools/generate_*_data.py` and three ledgers. For a doc that a feed reads it
selects **nothing**, so that commit passed. The red then waited for the next commit that ran the whole
site suite. That was the seat's record, because its landing carries `site/data/delivery.json`.
`fcdbd4cb09` (04:37Z) regenerated the feed in passing, which is why the 06:50 record landed. The
reading-log and method-results doors are green on origin `dc53f3311e`.

**The fix, as a class.** `tools/site_lane_gate.py` gets a mechanism D. A tool that declares a
`site/data/` output has path constants, and those are its inputs. Each input selects the `site/**`
tests that import that tool. On today's tree, that maps `reading_log.md` and
`the_map/concepts.yaml` to the reading-log door, and `THE_IMPROVEMENT_LOOP.md` to the method-results
door. So a red of this shape now lands on the commit that causes it. Mutations were run against the
new tests. Dropping the lookup from `plan()` reds the live-subject test. Dropping the
writes-`site/data/` filter reds the no-feed test.

## (b) The refusal now names its test

`background/delivery_seat.py::refusal_verdict` cut the refusal at the first `❌`. `surgical_land`
quotes the gate's stdout before its stderr. pytest's `FAILED site/...` lines are on stdout, and the
site lane's banner is on stderr. So every site-lane refusal that reached the seat's journal named the
lane and never the test, which is the 03:54 journal line exactly. Node lines from above the banner are
now kept ahead of it, so the limit cannot cut them. Control:
`test_a_red_site_lane_refusal_names_the_failing_test_not_only_the_banner`. It reds when the nodes are
dropped.

## Not established

The 01:29 refusal was the gate running past 3,600 s. This turn did not reproduce it, and its cause is
still the one the 03:24 record named as unestablished: box load during the fabric A/B. No gate timeout
was raised.

## Done

All three parts are closed in the commit that files this: (c) was spent, (a) is named and fixed as mechanism D, and (b) keeps the nodes. Nothing is left in the queue.
