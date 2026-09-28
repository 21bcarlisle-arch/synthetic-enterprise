**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3

# Result: heartbeat commits are not what keeps the shared tree behind origin

Graded against `SEAT_PREREG_DO_HEARTBEAT_COMMITS_CAUSE_RECONCILER_LAG_2026-09-28.md`, which was
written before any of these figures were computed.

**The carried claim is WITHDRAWN.** The claim was that heartbeat-only commits manufacture the gate
cycles the reconciler cannot keep up with.

- The shared tree was behind origin for **37.0 h of the 95.0 h** the reconciler has logged its
  fork state (2026-09-24 21:10 → 2026-09-28 20:10 UTC).
- Heartbeat work accounts for **2.4 h (6.5 %)** of that behind time.
- The rest comes from four other causes:

| Cause | Share of behind time |
|---|---|
| The content-publish gate holding the run lock | 29 % |
| Merge conflicts between two lanes on one file | 26 % |
| Dirty paths on the shared tree that collide with origin | 20 % |
| The reconcile worktree was busy, or the reconciler errored | 11 % |

The heartbeat does carry a real cost of its own, described under P3, but it is not the lag.

## The readings

**Sources.**
- **Behind/ahead state:** the fork lines in `docs/observability/reconcile-watch-log.md`. The
  reconciler writes one on each 5-minute tick while the tree is off level, and each carries its
  own reason. These lines only begin on 2026-09-24 21:12, so this reading covers **4 days, not the
  7 the brief asked for.**
- **Heartbeat attempts:** `docs/observability/sim-runner-log.md` records 133 in the window. 51 were
  published, 42 were committed but did not advance origin on push, 36 were refused before staging,
  and 4 stood down.
- **Content-publish gates:** `docs/observability/publish_gate_duration.jsonl` records 37 in the
  window.
- **Commit shapes:** `git log origin/main` over 7 days.

**Where the behind time came from.** A 5-minute interval counts as behind when its fork line says
`behind > 0`. The interval is attributed to the reason that fork line names. A GATE_RUNNING
reading is attributed to the heartbeat when it falls within one minute of a heartbeat attempt in
`sim-runner-log`, and to content publishing otherwise.

| Cause (the reconciler's own reason field) | Behind minutes | Share |
|---|---:|---:|
| run lock held: content publish or other publisher work | 644 | 29.0 % |
| `REFUSED_CONFLICT`: two lanes, one file | 576 | 25.9 % |
| `NOT_ADVANCED`: dirty shared-tree paths collide with origin | 433 | 19.5 % |
| `ERROR`: reconcile worktree busy or error | 243 | 10.9 % |
| **run lock held: heartbeat attempt** | **144** | **6.5 %** |
| other `NOT_ADVANCED` / `FAST_FORWARDED` / `RECONCILED` (transient) | 181 | 8.1 % |

No conflicted path and no "Refused by N path(s)" list in the whole log names
`site/data/tick_heartbeat.json` or `docs/observability/agent_status.json`. There are 104 such
lists. The conflicts are on `background/delivery_lane.py`, a test module and staging documents.

**Time until the tree is next level after an origin commit.** This is the measure the brief named.
A tick counts as level only when no fork line falls within ±3 minutes of it. The first pass
without that rule split episodes on the 1-minute offset between a DRIFT tick and its fork line.

| Commit on origin | n | Median | p75 | Mean |
|---|---:|---:|---:|---:|
| heartbeat | 91 | 4.6 min | 14.2 | 19.7 |
| other landing | 187 | 6.2 min | 31.8 | 35.5 |
| reconcile merge | 69 | 11.1 min | 36.6 | 35.2 |

This comparison is confounded. Heartbeats fire when content is unchanged, which is the quieter
periods. It is not the attribution. The attribution is the reason table above, and this table
only fails to contradict it.

## The predictions, graded

- **P1 was WRONG.** I predicted a heartbeat starts almost no gate cycles.
  - Every heartbeat that commits runs the full `tools/git-hooks/pre-commit` chain. Each commit
    carries `[hook-gate mark] … chain completed`.
  - The chain runs inside `process_run_complete`'s run lock. Its log puts one attempt at roughly
    2–5 minutes, for example 18:36→18:41 and 18:57→19:02 UTC on 2026-09-28.
  - 93 of the 133 attempts reached that chain.
  - I cannot compute the ratio I pre-registered, because heartbeat gate time is not written to
    `publish_gate_duration.jsonl`. At 2–5 minutes against a 33–37 minute content gate, a heartbeat
    gate costs roughly 1/7 to 1/15 of one. The bar was 1/5, so on the ratio it would pass. The
    premise behind P1, that heartbeats barely gate at all, was false.
- **P2 HOLDS.** Behind time after a heartbeat is not longer than after other landings: medians of
  4.6 and 6.2 minutes, against a bar of 1.5×.
- **P3 was WRONG on its number, and the mechanism is real.**
  - 40 of the 136 heartbeats over 7 days (29 %) became the first parent of a
    `merge origin/main: automatic reconciliation` commit. I predicted at least 50 %.
  - That is 41 of the 180 reconcile merges on origin (23 %). Each one is one more gated merge.
  - The cause is that the heartbeat is committed onto a shared tree that is already behind, so
    its push is non-fast-forward. The evening of 2026-09-28 shows it: the tree was 7–10 behind
    because of 3 dirty paths, and three consecutive heartbeats all logged "push did NOT advance
    origin".
  - So a heartbeat does not cause the lag. The lag causes heartbeat churn.
- **P4 HOLDS, with one addition.** The readers are listed in the next section.

## Does the heartbeat need to be a commit?

| Reader of `site/data/tick_heartbeat.json` | How it reads | Needs a commit? |
|---|---|---|
| `site/assets/freshness-banner.js` (public site) | fetches `/data/tick_heartbeat.json` from the deployed site | **Yes, while the only deploy route is `.github/workflows/deploy-pages.yml`.** That deploys `site/` on a push to `main` touching `site/**`, so the heartbeat reaches the reader only as a commit on origin/main. |
| `background/worker_tick.py` | the writer: rewrites the file on disk every 60 s | no |
| `background/publish_gate_blocking_read.py` | `LIVENESS_SURFACE_FILES`: names the paths the publisher commits | no; it is the commit's own list |
| `background/publish_freshness.py` | reads the local copy | no |
| `site/test_*` doors | read the local or index copy | no |

Nothing reads the file's git **history**. The commit is only the way the file gets deployed.

**The addition.** 54 of the 136 heartbeat commits over 7 days (40 %) changed **only**
`docs/observability/agent_status.json` and not `site/`. So they deployed nothing to the one
reader that needs a commit. `a88ae865d` is the latest example. A grep found no reader of
`agent_status.json` on origin: `tools/generate_*` read the disk copy. All 54 commits paid a
full hook chain, 18 of them also paid a reconcile merge, and no reader was found for any of
them. Those 18 are 45 % of the 40 heartbeats that needed a merge. I am not rewriting the
publisher in this item. That is a separate change, handed on below.

## The one-variable run was not run, for two named reasons

1. **The observational reading already attributes the lag.** The reconciler records the reason it
   did not level on every tick. The heartbeat appears only in the run-lock rows, which are 6.5 %
   of the behind time.
2. **No dial suspends only the heartbeat, and the brief says build none.**
   - `_refresh_published_liveness_on_skip` is gated by `is_resident_seat()` and by
     `PUSH_THROTTLE_SECONDS = 30 * 60`, a hard-coded constant.
   - Standing down the whole `process_run_complete` would also stop the content publisher. That
     changes two variables at once.
   - A window run now would also read nothing. The tree is pinned 10 behind by three dirty paths,
     starting with `background/process_manifest.yaml`, so both windows would show the same lag for
     a reason unrelated to heartbeats.

   Nothing was suspended, so there is nothing to reverse.

## What is handed on

The heartbeat's avoidable cost is two behaviours:
- the 40 % of heartbeat commits that deploy nothing;
- committing onto a tree already known to be behind, which produced 29 % of heartbeats needing a
  reconcile merge. The publisher's own log line already reads "origin/main is N commit(s) ahead"
  before it commits.

Both are cheaper mechanisms, not new dials. The largest single lever on reconciler lag is not the
heartbeat. It is the dirty-path and conflict classes, which together are 45 % of the behind time.
