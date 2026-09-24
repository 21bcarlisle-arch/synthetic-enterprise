**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — what a re-ask run from an isolated worktree grades differently, and why

*Lane 0 delivery, 2026-09-24 ~02:15Z. Drawn item:
`alarm-reask-has-never-been-applied-so-the-new-attention-term-runs-entirely-on-its-fallback`.
Filed BEFORE `reask()` was called anywhere by this seat, and after the premise was re-measured.*

## Why the question changed before any measurement was taken

The drawn item asked for one command: `alarm_repetition.reask --apply` against the live
population, on the premise that it *"has never been applied: zero of the ten live alarm documents
carry a `## Re-asked` section"*. **That premise is spent, and it was spent six minutes before this
invocation began.** Measured, not inferred:

| fact | value |
|---|---|
| `465a0dfca` — the commit adding BOTH `reask()` and its only caller | 2026-09-23 23:12:02Z |
| the caller | `background/staging_watcher.py:888`, `reask(apply=True)`, every tick |
| the running `staging_watcher.py` process (pid 2413962) started | 2026-09-24 02:00:23Z |
| all ten live alarm documents rewritten | 2026-09-24 02:00:25Z — **two seconds into its first tick** |
| this invocation (pid 2439669) started | 2026-09-24 ~02:06Z |

So the re-ask was not uncalled. It was called by a daemon that had been running
pre-`465a0dfca` code for **2h48m**, and the missing event was a restart, not a command. The item
was drawn inside that window. All ten shared-tree documents now carry
`- **2026-09-24** — re-asked: **still_holds**.` and one was archived `cleared`
(`..._VALUE_ARM_CHOOSES_A_BOUND_NOT_A_CUSTOMER_WAS_CLAIMED_2026-08-25.md`, quiet since
2026-08-25). All eleven writes are **uncommitted**.

That leaves a question whose answer I do not know, and which the item's instruction would have
walked straight into: **this seat runs in an isolated worktree, and the instruction was to run
`--apply` there.** `reask()` consults two oracles and an isolated worktree has neither in the state
the shared tree has them:

1. `background/notify.TRANSITIONS_FILE` — `docs/observability/.notify_transitions.json`,
   **untracked runtime state**. Confirmed absent in this worktree; 49,561 bytes on the shared tree.
   `_read_transitions_for_reask()` returns `{}` on any failure, so the leg that lets a recent
   FIRING contradict a stale-looking document cannot fire at all here.
2. the alarm documents themselves — this worktree's copies are HEAD's, and HEAD does not have the
   daemon's writes. Measured drift in `last_observed`: 2026-09-15 here vs 2026-09-24 on the
   shared tree for `DEADMAN_ORIGIN_FORK` and `SEAT_CLAIM` (9 days), 2026-09-22 vs 2026-09-24 for
   seven others.

The docstring of `_read_transitions_for_reask` argues the empty read is safe because *"the store is
used exclusively to CONTRADICT ... and the heartbeat leg below still has to pass"*. **The heartbeat
leg's other source is the documents themselves** (`machinery_heartbeat` unions store dates with
`last_observed` over the population), so an absent store does not necessarily make the machinery
read dead. Whether the safety argument holds is exactly what is unknown here.

## Predictions, all three runs, written before any of them

Bars: `REASK_QUIET_DAYS = 3`, `REASK_HEARTBEAT_DAYS = 1`. Today 2026-09-24, so
`quiet_before = 2026-09-21`, `heartbeat_before = 2026-09-23`.

**Run A — this worktree, as the item instructed (no store, HEAD documents), report-only.**
I predict **7 `still_holds`, 3 `cannot_tell`, 0 `cleared`.** Mechanism: the seven copies observed
2026-09-22 clear the 3-day bar on leg 1. The three that do not — `DEADMAN_ORIGIN_FORK` and
`SEAT_CLAIM` (2026-09-15) and the `in_progress/` `VALUE_ARM` copy (2026-08-25) — get no
contradiction from an empty store, and `machinery_heartbeat` can see no date newer than
**2026-09-22**, which is behind the 2026-09-23 bar. So the machinery reads DEAD and all three fail
closed.

**Run B — this worktree with the shared tree's transition store copied in, one variable changed,
report-only.** I predict **9 `still_holds`, 1 `cleared` (`VALUE_ARM`), 0 `cannot_tell`** — the same
split the daemon actually applied. Mechanism: the store supplies today's firings, so the heartbeat
reaches 2026-09-24 and the machinery reads alive; `ORIGIN_FORK` and `SEAT_CLAIM` are then rescued by
the contradiction leg, and `VALUE_ARM`'s family has nothing in the store.

**Run C — the store leg's load-bearingness on the SHARED tree today.** I predict **zero of the
eleven verdicts the daemon wrote turned on the store at all**: every applied line reads
`observed <date>, within the 3-day bar`, which is leg 1. The store is doing no work in the live
configuration, and the isolation hazard is therefore invisible to anyone who only reads the
verdicts.

## What each outcome would mean, stated before it is known

- **A as predicted (0 cleared):** the hazard is real but the heartbeat leg catches it *today*, by
  the magnitude of the drift rather than by mechanism — a worktree 2 days stale trips the 1-day
  heartbeat bar. A worktree only 1 day stale would not, and B's rescue legs would still be absent.
  That is a coincidence of magnitude, not a safety property, and it earns a refusal rather than a
  comment.
- **A shows any `cleared` that B does not:** the instruction in the drawn item would have archived
  a live condition out of the director's queue. Fail-open, in the worst direction this module has.
- **A and B identical:** my whole account of the two oracles is wrong and the store is inert even
  when present; the remedy is nothing, and this pre-registration is refuted.

## The remedy I expect to owe, named before the answer

`reask()` should distinguish an **absent** store from an **empty** one and refuse to reach
`CLEARED` at all when the file does not exist — a named `cannot_tell` reason, not a comment. That
is a one-leg check keyed to the property (can this process see the firing record?) rather than to
today's drift. I am naming it now so that if the measurement does not support it, the record shows
I wanted to build it anyway.
