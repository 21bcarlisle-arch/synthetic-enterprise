**Severity:** BLOCKING · **Lane:** H_harness

# FINDING — the RUNG-1 wedge's independence cross-check reads git ancestry as its clock, and since OPS3 made the marker queue a STACK that clock runs backwards: the gate's green pass is recorded three commits BEHIND the failure it is supposed to supersede

**Found by:** the SCHEDULED-TICK RUNG-1 draw, 2026-08-20 ~16:20Z. This is the **third consecutive
tick** dispatched by this alarm. The two before it (`51f710b49`, `447ef2ded`) each diagnosed a real
and distinct defect and neither could explain why the alarm kept firing. This one is the reason:
the fail-safe that exists to cover both of them cannot fire, for a structural reason neither tick
looked at.

**Class:** R15 — *a two-part control can have each half read a different tree*
(`feedback_a_two_part_control_can_have_each_half_read_a_different_tree.md`), reached from a new
side: here both halves read the **same** tree, and the **ORDERING RELATION BETWEEN THEM** is the
thing that is wrong. Closest sibling: *an EVER-keyed control is blind to the SINCE question*.
R10 applies — the closure is the class (an ordering control must be measured against the order
that actually matters), not this instance.

**Rank requested:** top. It is dispatching PRIORITY-ZERO work on a healthy, publishing pipeline.

## The one-line defect

`supervisor._publish_gate_wedge_supersedes` decides "has a pass superseded these failures?" with
`_commit_is_ancestor(newest_failure, last_tested)` — **git ancestry used as a clock**. Its own
docstring says *"git ancestry supplies the ORDERING neither of them carries."* Since OPS3
(2026-08-14) the publish queue is drained **newest-marker-first** — `order = list(reversed(pending))`
at `background/background_worker.py:392` — and both SHAs being compared are **marker subject
commits**. So across a drain, ancestry is **anti-correlated with time**: the later a run is
processed, the older its commit. The control's stated ordering source reports the reverse of the
order it needs.

## Observed, with evidence

**The gate is GREEN and has published.** `docs/observability/.last_tested_hash` = `43766e01e`,
mtime **15:34:03Z**. Per `LAST_TESTED_HASH_CONTRACT` that file is written by exactly one writer,
`_run_gate_in`, and **only on rc=0** — never on a red, a timeout, or an unavailable checkout. The
publish commit landed one second later:

```
cd4da3219  2026-08-20T16:34:04+01:00  Auto-process run complete: report + LATEST.md + site/ (git=43766e01e, net=£1,529,289)
```

**The alarm is still armed right now.** Run live this tick:

```
>>> background.supervisor._publish_gate_wedge_active()
WEDGE ACTIVE: True
"...the publish gate has been FAILING for ~504 min (3 failures in-window, no pass at HEAD 447ef2ded)..."
```

**The anti-correlation, proven inside the failures list alone** — no need to involve
`.last_tested_hash` at all. `.publish_gate_state.json` holds three failures, ascending in `ts`:

| list position | `ts` | `git_hash` | commit date | history relation |
|---|---|---|---|---|
| 0 | 14:07:37Z | `81449dcb4` | 11:51:06+01 | **descendant** of `8ba61d802` |
| 1 | 14:37:18Z | `8ba61d802` | 11:15:17+01 | **descendant** of `c24e81e07` |
| 2 | 15:07:13Z | `c24e81e07` | 10:39:34+01 | oldest commit, newest failure |

The list is **ascending in time and strictly descending in history**. The predicate walks
`reversed(failures)` and takes position 2 as "the newest failure" — which is the **oldest commit of
the three**. The instrument disagrees with the quantity it is standing in for, within one file,
with no other component involved.

**And the pass sits behind all three:**

```
$ git merge-base --is-ancestor 43766e01e c24e81e07   # exit 0
  YES: the tested commit PREDATES the newest failure
$ git rev-list --count 43766e01e..c24e81e07
  3
```

So the pass is **27 minutes later in time** (15:34:03Z vs 15:07:13Z) and **3 commits earlier in
history**. `_commit_is_ancestor(c24e81e07, 43766e01e)` is `False`, the supersession branch returns
`False`, and the rung stays armed on a gate that is green and publishing.

**Why the pass is behind — the drain order, quoted from the code that chose it** (`background_worker.py:387-393`):

> *The queue is a STACK, not a FIFO: every marker describes the SAME thing (the state of the world
> after a run), so the newest strictly dominates and the older ones carry nothing it lacks.*

```python
order = list(reversed(pending))
```

Four consecutive picks this episode, in strictly descending marker time — three failed, the fourth
published:

| marker | subject commit | outcome |
|---|---|---|
| `run_complete_20260820T105223Z.md` | `81449dcb4` | rc=1, still in staging root |
| `run_complete_20260820T101636Z.md` | `8ba61d802` | rc=1, still in staging root |
| `run_complete_20260820T094053Z.md` | `c24e81e07` | rc=1, still in staging root |
| `run_complete_20260820T090542Z.md` | `43766e01e` | **rc=0, published, archived to `done/`** |

Both mechanisms are individually correct. OPS3's stack drain is a deliberate fidelity fix (it stops
the publisher winding the clock backwards under R11/R14). The wedge cross-check predates it by two
days and was never told. Neither is wrong on its own; jointly they guarantee that a pass which
follows a failure **within one drain** can never clear the alarm.

## Why the two prior ticks could not see it

- `51f710b49` found `blocking_tests` naming a test that is green at HEAD — a stale **payload**. True,
  and not why the rung fires: the rung never reads `blocking_tests`.
- `447ef2ded` found the clear routed through a process still running a second full suite — a stale
  **clear**. Also true: `record_publish_gate_success` has not run, and
  `.publish_gate_state.json` mtime is still **15:07:13Z**, an hour stale, because PID 3066953 is
  still live (74 min, now in its post-publish annotation pass, PID 3132509).

The cross-check on `.last_tested_hash` is precisely the fail-safe designed to cover a stuck clear —
it had the green fact on disk at 15:34:03Z, a full hour before this tick. It did not fire, and
neither prior tick asked why, because both stopped at the state file.

## Proposed closure — the class, not the instance

**Repair:** an ordering control must be measured against the order that matters. The pass/failure
comparison should be made on the **recorded clock**, not on ancestry:

1. `record_publish_gate_failure` already stamps `ts` on every failure row. Have `_run_gate_in` stamp
   the green the same way — a `{"sha": ..., "ts": ...}` beside `.last_tested_hash` (additive; the
   existing one-line file stays, so `run_fast_tests`' SKIP consumer is untouched).
2. `_publish_gate_wedge_supersedes` compares `green_ts > newest_failure_ts`, and keeps the existing
   ancestry test **only** for its other, still-valid job: proving the pass is on HEAD's history
   (an abandoned branch proves nothing). Ancestry stops being the clock; it stays the *provenance*.
3. Keep every fail-safe direction as-is: no usable SHA, no green ts, a pass off HEAD's history, or
   an unreadable file all still fail **toward drawing**.

**R15 mutations — each on its own named defect:**

- **The ordering mutation (the subject).** Failures at `ts` T1<T2<T3 whose SHAs descend through
  history, green at T4>T3 on a SHA that is an *ancestor* of all three — i.e. this morning's exact
  recorded state. Must report **superseded**. Under today's code it reports **wedged**; that
  divergence is the control firing on its own defect.
- **The null control that refuses "just always clear on a green".** A genuine wedge: green
  at T0 followed by failures at T1>T0. Must still report **wedged**. Without this pin the repair
  degenerates into "any green ever recorded silences the alarm", which is the fail-open R15 names
  and is strictly worse than the bug being fixed.
- **The provenance leg, unchanged.** Green ts newer than every failure but on a SHA that is **not**
  on HEAD's history. Must still report **wedged** — proving step 2 kept ancestry's real job and did
  not delete the branch along with the clock.
- **Fail-silent.** Green-ts file absent/corrupt → **wedged**, never a clear. An unavailable check is
  a failed check.

## What was NOT done this tick, and why

**No code was changed.** Two full pytest suites are live in this working tree (PID 3132509, the
post-publish annotation pass, 42 min, 1.03 GB RSS; PID 3196563, the deadman's operational signal,
17 min) on a 15 GB box with ~8 GB available. More decisively, `background/supervisor.py` — the file
this repair edits — **already carries 89 uncommitted lines from another lane** (the pass-ceiling
work, `_exclude_saturated_harden`). Landing here would need a worktree swap under two live suites,
which is the "manufacture the episode's next failure" hazard the doorbell names and the
`feedback_a_two_lane_file_is_a_reason_to_swap_never_a_reason_to_adopt_the_other_lane` rule refuses.

**`.publish_gate_state.json` was not hand-patched** — `background/self_clearing_alarm_census.py:17`
records that as the move the steer explicitly forbade.

**The wedge is not urgent and will self-clear**: when PID 3066953 finishes its annotation pass it
calls `record_publish_gate_success`, which resets `failures`/`alerted_at`. That does not repair
anything — the next drain that fails-then-passes re-arms the same phantom.
