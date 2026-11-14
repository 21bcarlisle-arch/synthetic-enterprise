**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Where the seats collide on shared files (pre-registration, then result)

**Fate (2026-11-14):** RECORD. This is a second, independent measurement of the steer. A worker
tick drew the same advisor file in the same hour and closed the steer under outcome 3 in its own
commit, which was still in its gates when this file landed: "No shared file dominates the lanes'
collisions, so no one-writer trial", with its record `SEAT_MEASURE_WHERE_THE_LANES_COLLIDE_…`.
That commit carries the steer's `## Done` section and the reading-log rows, so this file adds
neither. **The two methods agree.** The worker counted transcript mentions and landed history:
37 to 103 multi-writer file-hours, 12 of 141 merges with a file changed on both sides, and about
9.3 h of contention tool time. This file counts tool-call writes credited per session: 104
file-hours, 17 overlaps in 142 merges, and about 7.2 h. Both reach outcome 3. **The duplicate
draw is itself a live case of cause 2 below:** two lanes worked one item at the same time, and
neither file was the cause.

*Delivery seat, seat-executor worktree, 14 Nov 2026, acting on the director's steer
`DIRECTOR_STEER_ONE_WRITER_PER_SHARED_FILE_MEASURE_WHERE_LANES_COLLIDE_FIRST_2026-11-14.md`.*

## Pre-registration (written before any per-file collision count was run)

**What a collision is.** A *writer* is one Claude session (one transcript jsonl under
`~/.claude/projects/`), or one non-Claude committer (a daemon commit carrying no `Claude-Session`
and no `Co-Authored-By: Claude` line). A *collision hour* for a file is a clock hour in which two or
more distinct writers wrote it: a Write/Edit tool call naming the file, or a commit touching it.
One writer rewriting its own file thirty times is churn and counts zero. Window: 31 Oct 00:00 to
14 Nov 24:00 GMT.

**Contention events** are commits whose subject or body names merge, reconcile, surgical, held
behind origin, sweep, fork, unlanded or stranded. An event is *traced to* a file when the file is
in the commit's diff or named in its message.

**Predictions, mine, beside the advisor's:**

1. P1 (the advisor's): `site/data` and `DIRECTION.yaml` lead; `company/` and `simulation/` are small.
   I agree on direction, and sharpen it: by collision hours, the top file is a generated feed under
   `site/data/` (I guess `publish_provenance.json` or `delivery.json`), and `DIRECTION.yaml` is in
   the top three.
2. P2: `company/` plus `simulation/` together hold under 5% of collision hours.
3. P3: the top three files hold at least 40% of all collision hours. If they hold under 25%, the
   answer is the steer's outcome 3: the cost is spread, paid and known, and no trial is proposed.
4. P4: at least half of contention events trace to a file in the top ten.

The session-time cost estimate is the hardest leg and is graded last: it can only be an
order-of-magnitude reading from transcript timestamps around contention tool calls
(`isolate_hunks`, `surgical_land` refusals, `refresh_to_head`, merge retries).

**Timing, stated plainly.** I wrote the four predictions above and committed them locally
(39f59e0d1) before I ran any count. The first collision count ran while that commit was still
going through its gates. It reached origin a few minutes later, before this result was written.
Nothing in the predictions was changed after the count ran.

## Result

**Method.** I read 728 transcripts (385 worker ticks, 265 seat-executor turns, 77 delivery-seat
sessions) and 758 commits on origin/main from 31 Oct to 14 Nov. A write is a Write or Edit tool
call, or a commit touching the file. Each commit is credited to the session whose tool output
showed its sha first. 757 commits matched a session and one did not. On the first pass I credited
each commit to the session that started earliest, which put long sessions on commits they had
only read: that pass gave 144 collision hours and the corrected pass gives 104. The probe scripts
are in `/tmp/collide/`, outside the repository.

**Collision hours: 104 in 15 days.** These are clock hours in which two or more distinct writers
wrote the same file.

| Rank | File | Collision hours | Share | Cumulative | Writers |
|---|---|---|---|---|---|
| 1 | `docs/direction/DIRECTION.yaml` | 21 | 20.2% | 20.2% | delivery seat, seat executor, worker tick |
| 2 | staging finding: level DD household dunned per bill (7 Nov) | 6 | 5.8% | 26.0% | seat executor, worker tick |
| 3 | `tools/generate_billing_ledger.py` | 6 | 5.8% | 31.7% | seat executor, worker tick |
| 4 | worker finding: level DD journey cures on next instalment (9 Nov) | 6 | 5.8% | 37.5% | seat executor, worker tick |
| 5 | `docs/design/LEVEL_DD_AREA_MAP_2026-11-11.md` | 5 | 4.8% | 42.3% | several seat executors |
| 6 | `docs/design/maturity_map.yaml` | 3 | 2.9% | 45.2% | |
| 7 | `site/data/publish_provenance.json` | 3 | 2.9% | 48.1% | all three kinds |

Shares by area: `docs/staging` 34%, `docs/direction` 21%, other `docs/` 19%, `tools/` 10%,
`tests/` 5%, `site/data` 5%, `company/` plus `simulation/` 2%.

**Contention events: 163 commits.** There are 142 merges, plus 21 non-merge commits whose subject
names one of the contention words. Only 3 of the 163 touch a top-ten collision file in their own
diff.

I counted the files on the local side of each merge, meaning the work that was held behind origin.
The leaders are `DIRECTION.yaml` (31), `SEAT_STRETCH_LOG.md` (26), `site/data/delivery.json` (23),
`decisions.jsonl` (23), `generate_billing_ledger.py` (17), `STARTUP_ANCHORS.md` (16) and
`publish_provenance.json` (15).

I also counted files touched on both sides of a merge since its merge base. Across all 142 merges
there are 17 such overlaps on 12 files. None of them is `DIRECTION.yaml`, the stretch log or a
`site/data` feed. They are `generate_billing_ledger.py` (3 merges), three domain-invariant files,
three tests on the same work and five staging findings, each being worked by two lanes at once.

**Session time spent handling contention.** 778 calls to `isolate_hunks`, `refresh_to_head`,
`git merge`, `merge-base`, `origin_reconcile` or `--content`. Each call is charged the time until
the next tool call, capped at 30 minutes. Total: about 7.2 hours out of 356 active session hours,
or 2.0%. Worker ticks 4.6 h (2.5% of their time), seat executors 2.6 h (1.5%), delivery seat under
0.1 h.

This leaves out one cost: re-running the gates after a promotion is refused because origin moved,
and the gate time on the 142 merges themselves. That is landing cost driven by forks, not by any
one file, and I have not measured it. I expect it is the larger cost, but that is a prediction, not
a reading. It is a GAP.

## Grades

- **P1, partly held.** `DIRECTION.yaml` is first. The top file is not a `site/data` feed:
  `publish_provenance.json` is seventh, at 2.9%. The advisor's `site/data` lead came from counting
  touches. Most of those touches are one writer regenerating its own feed, which is churn, not
  collision.
- **P2, held.** `company/` plus `simulation/` hold 2%, under the 5% I predicted.
- **P3, missed.** The top three hold 31.7%, not 40% or more. That is still above the 25% line at
  which I said no trial would be proposed, so the outcome is in between and I read it below.
- **P4, missed badly.** Only 3 of 163 contention events touch a top-ten collision file in their own
  diff. Merges are forks: they happen whenever origin moves, whatever files moved. They are not
  caused by two writers on one file.

## What it means (the steer's outcomes 2 and 3)

**The steer's condition for a trial is not met.** It asked for a trial if "two or three files
account for most of it", and they do not. One file, `DIRECTION.yaml`, holds a fifth of the
collision hours. The rest is a long tail. Its biggest part is the second cause below, not a
shared file.

1. **`DIRECTION.yaml` is the only candidate for one writer.** It is ruled state with three kinds
   of writer, so the steer's pattern fits: lanes post a change request and one owner writes. But
   it appears on both sides of a merge zero times, so a single writer would remove about 21
   collision hours. That is roughly a fifth of the 2% contention share, about 0.4% of session
   time. It would remove no merges.
2. **The second cause is two lanes drawing the same item, not a hot shared file.** A worker tick
   and a seat executor wrote the same level-DD findings and `generate_billing_ledger.py` in the
   same hours. Every merge overlap falls on that billing and domain-invariant work and its staging
   findings. One writer per file does
   not fix this. One active worker per item does, which is the article's rule applied to the
   draw rather than to files. Measuring how often one item is held by two lanes at once is the
   next question, if he wants one.
3. **The 9 Nov generated-data steer.** `site/data` is 4.8% of collision hours, so this measurement
   gives no collision reason to release it. Its case rests on repository size and gate time, which
   this did not measure, and it stays where it is held.
4. **Which guards a one-writer file would make unnecessary: none.** `isolate_hunks`,
   `surgical_land`, the tree lock and `origin_reconcile` exist for a shared dirty index and for
   forks with origin. Both happen whatever files are written. A single writer on `DIRECTION.yaml`
   removes none of those reasons, so there is no guard to delete.

**Answer: outcome 3.** Collisions on shared files cost about 2% of session time, the cost is spread
across many files, and it is now known. No redesign is proposed. The cost of re-gating after forks is
unmeasured and probably larger. If it is measured, it should be measured as fork frequency against
landing latency, not per file.
