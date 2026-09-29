**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3

# Pre-registration: do heartbeat commits cause reconciler lag?

Written at 2026-09-28 20:12 UTC, before any lag figure was computed. The only numbers I had seen
were three commit counts on origin/main over the last 7 days: 766 commits in total, 136 with the
subject `chore(liveness): publish heartbeat` and 180 with the subject `merge origin/main`.

**The claim being graded.** The seat has carried this claim through three stretches without
measuring it: *heartbeat-only commits manufacture the gate cycles the reconciler cannot keep up
with.*

**Predictions, fixed before measuring:**

- **P1: a heartbeat commit starts almost no gate cycles.** I expect it to be a daemon commit made
  on the shared tree with a small pathspec. It should select close to no tests and leave no
  `surgical_land` receipt. The median gate cycles per heartbeat should be at least 5× fewer than
  the median per non-heartbeat landing.
- **P2: a heartbeat does not make the shared tree fall further behind.** A heartbeat is made on the
  shared tree, so on its own it leaves the tree *ahead* of origin, not behind. I expect the median
  time the shared tree spends behind origin after a heartbeat to be within 1.5× of the median
  after a non-heartbeat commit, in either direction.
- **P3: heartbeats do cost merge commits.** I expect at least half of the 136 heartbeats to be
  followed on origin by a `merge origin/main: automatic reconciliation` commit within 30 minutes.
  If this holds, the real cost of a heartbeat is merge churn on origin's history, not gate time.
- **P4: one reader needs the heartbeat to reach origin, but none needs it in git history.** I
  expect the public site's `freshness-banner.js` to need the heartbeat pushed, because the site is
  deployed from the repository. I expect no reader to consume the git history of
  `site/data/tick_heartbeat.json`, so a squashed or out-of-history push would serve every reader
  equally well.

**Refutation.**

- **P1 fails** if the heartbeat's median gate cycles are more than one-fifth of the median for
  non-heartbeat landings.
- **P2 fails** if the median behind-time after a heartbeat is more than 1.5× the median after a
  non-heartbeat commit.

If P2 cannot be attributed from the observational reading, because heartbeats and other landings
interleave too tightly, the brief sets the one-variable run: suspend only the heartbeat publisher
for one fixed window through its existing dial, and compare that window with the one before it.

The result will be filed as
`SEAT_RESULT_DO_HEARTBEAT_COMMITS_CAUSE_RECONCILER_LAG_<date>.md`, and these predictions stay here
unrevised.
