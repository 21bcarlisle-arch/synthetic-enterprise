**Severity:** LATENT · **Lane:** H_harness · **Atom:** none (direction item `the-fork-closed-and-the-publisher-episode-closes-when-its-cause-does`)

# FINDING: a publish episode outlived its cause, and a weekly hold had no reading

The draw's duplicate-work note named a live claim with this same id. That was the draw's own write,
not a second piece of work, so there was no disposition to take.

## What was wrong

`docs/observability/.publish_gate_state.json` held `episode_failures: 1`, `wedge_since`
2026-09-27 ~13:17Z, cause `behind_origin`. The only thing that could close an episode was
`record_publish_gate_success` with the queue drained. Since the weekly window (Monday 04:00 London)
went live, a cycle mid-week is a HOLD: it returns `EXIT_NOTHING_PUBLISHED`, the router records
nothing, and nothing is ever attempted that could succeed. So the surface read FAILING until next
Monday's publish whether or not the cause was still there, and a live refusal and a stale one read
the same. A hold itself left no trace in the state at all.

## What changed

- `process_run_complete.recorded_cause_standing` re-asks the open episode's recorded cause against
  origin/main **now** (one fetch, `FETCH_HEAD...HEAD`). It does not read back the cached refusal.
  `behind_origin` has cleared when HEAD contains origin. `push_never_landed` and `lost_push_race`
  have cleared when origin contains HEAD. Every other cause names a test, a hook or a clock that
  git cannot re-ask, so it answers `unknown` and the episode stays open (fail closed).
- `close_episode_if_cause_cleared` runs first in `record_publish_gate_outcome` on every cycle that
  ran (a lock-skip excepted), including a HOLD. It closes the episode as an evidenced close and
  records `episode_closed_by: {rule: cause_cleared, reason, ts}`, so this close can be told apart
  from one made by a publish.
- The HOLD branch calls `record_publish_hold(reason, next_opens)`. `publish_freshness.publisher_refusal`
  now reads `failing` / `held` / `recovered` / `no_open_episode`, and `describe()` renders a hold as
  `HELD by the weekly window ... the next publish opens <when>`. An open refusal outranks a hold.

## Control

`tests/background/test_a_publish_episode_reads_held_refused_or_recovered.py` is one partition over
the real writers: refused → `failing`, cause cleared → `recovered`, hold → `held`, and all three
distinct. Two mutations were run, and both made it fail:
believing the cached refusal instead of re-asking it (`cleared`→`holds`), and collapsing `held`
into `no_open_episode`. A cause git cannot re-ask never closes an episode, however level the fork
reads.

## Still open

- **The banner JS** (`site/assets/freshness-banner.js`) does not yet render `held`. It treats any
  state other than `failing` as not-evidence-of-health, which is safe, but it does not say
  "held until Monday". Handed on.
- **DONE is observed on the next live cycle, not in this commit.** When the shared tree contains
  origin/main, the first cycle after this lands should log `episode CLOSED because its cause
  cleared` and write `episode_closed_by`. A daemon runs the checkout it started on, so that also
  needs the publisher to pick up this code.
- **Part 1 of the item (closing the shared tree's 2/1 fork): done by the reconciler's own
  cadence, not by this turn.** A seat run of `origin_reconcile` refused with `GATE_RUNNING`. The
  retry found the cadence's own merge already running. That merge landed as `f5be35f3f` on origin,
  carrying the shared tree's `402eac4cc` (meter-read estimates pro-rata by day) and `1694a4b2a`.
  The untracked copy of the account-credit finding needed no work here: the draw's own path check
  graded it identical to HEAD.
