**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the reconciler is NOT starved, so the publisher's real fork needed a truer refusal, not a new mechanism

**Found:** 2026-09-04 ~21:50–23:10Z, delivery seat, working the Lane 0 direction *"the publisher
meets a real fork and no fast-forward bound can close it"*. Pre-registered before any count was
taken:
`SEAT_PREREGISTRATION_WHETHER_THE_RECONCILER_IS_STARVED_OF_WINDOWS_OR_MERELY_ARRIVES_AFTER_THE_CYCLE_IS_ALREADY_THROWN_AWAY_2026-09-04.md`.

**The decision, first: on a real fork (`ahead > 0` and `behind > 0`) the publisher may do NOTHING
beyond what it already does — refuse before staging, record the cause, and hand to the named
owner. Neither candidate in the direction survives its own measurement.** What was actually broken
is the refusal's *account of who owns the fork*, and that is fixed and controlled.

---

## The direction offered two candidates; the premise under (b) is false

* **(a)** publisher COMMITS but does not push when `ahead > 0`, leaving `origin_reconcile` to merge
  and push it.
* **(b)** give `origin_reconcile` a window the publish cadence cannot close.

(b) rests on a premise stated nowhere and measured nowhere — **that the reconciler is starved.** The
stand-down finding reasons from a 672s cycle and concludes *"the reconcile window is only whatever
gap is left BETWEEN publish cycles"*. That is true only if the publish loop runs back-to-back.

`origin_reconcile.reconcile()` has exactly one caller — `deadmans_switch._check_origin_fork`, once
per `POLL_INTERVAL_SECONDS = 300` — and every verdict is written to
`docs/observability/deadmans-switch-log.md`. The deadman's timer is fixed and uncorrelated with the
publish cycle, so the share of its passes reading `GATE_RUNNING` is an unbiased estimator of the run
lock's duty cycle. **659 verdicts were already on disk.**

| Verdict | n | What it means |
|---|---:|---|
| `LEVEL` | 374 | nothing to reconcile |
| `GATE_RUNNING` | 182 | stood down for the run lock |
| `RECONCILED` | 41 | **real fork, isolated worktree, gated merge, pushed, re-read level** |
| `NOT_ADVANCED` | 38 | `ahead == 0` leg; shared tree would not fast-forward |
| `PUSHED` | 13 | `behind == 0`, landed local-only work |
| `FAST_FORWARDED` | 5 | mechanical advance |
| `REFUSED_GATE` | 3 | real fork, merge gated RED |
| `REFUSED_CONFLICT` | 3 | real fork, genuine conflict — a judgement, correctly kept |

**P1 held: `P(GATE_RUNNING) = 182/659 = 27.6%`** (refutation threshold was ≥80%).
**P2 held, and not marginally: the real-fork branch was reached 47 times** (`RECONCILED` +
`REFUSED_CONFLICT` + `REFUSED_GATE`) — each one required an isolated worktree to be built and
`surgical_land --merge` to be run to a verdict — **and 41 of them closed the fork unaided.**

### An independent route to the same duty cycle

Say what each number counts before dividing. From `docs/observability/publish_gate_duration.jsonl`,
last 400 cycles: **median cycle DURATION 523s**; **median gap between cycle STARTS 2160s** (p90
5534s, max 19454s). Those are different quantities — one is how long the lock is held, the other is
how often it is taken — and their ratio is a real one: **523/2160 = 24% duty cycle**, against 27.6%
sampled from an unrelated ledger by an unrelated timer. Two routes, two instruments, same answer.

**Publish cycles are not back-to-back. They are ~9 minutes of work every ~36 minutes.** The
reconciler has roughly three quarters of the wall clock, and it uses it.

## Why the deadlock is still real, and why it nevertheless resolves

Both things are true and the reconciliation is structural. `_run_lock()` wraps the **whole** of
`_process`, `git_commit_push` included. So **at the instant the publisher meets a real fork,
`gate_is_running()` is `True` by construction** — the reconciler is starved *exactly* when it is
needed, 100% of the time, which is what the stand-down finding correctly felt.

But the publisher then *exits*, the lock frees, and the next deadman pass is ≤300s away. That is
where the 41 closures happened. **The stand-down costs the cycle, not the fork.**

## So what does a dropped cycle actually cost? Less than the direction assumed

* **Frequency.** Across the whole of `docs/observability/sim-runner-log.md`: `behind_origin` = **30**
  refusals. Real-fork refusals (`"the fork is REAL"`, a string that only exists since the advance
  landed today) = **3**.
* **Latency.** A dropped cycle waits for the next publish attempt: **median 36 min, p90 92 min**.
* **Against the declared cadence.** `publish_freshness.PUBLISH_CADENCE_SECONDS = 7 days` — director,
  2026-09-04: *"The site publishes numbers and runs once a week, thoroughly and robustly, not every
  half hour ... The reason is cost."* **p90 latency from this branch is 0.9% of one cadence.**
* **And the comparison that settles it.** In the same log, `commit_refused` = **272**. *Nine times
  more publish cycles are lost to a red gate than to a fork of any kind, and ninety times more than
  to a real fork.* Building either (a) or (b) would be engineering a 3-event path with a 272-event
  path beside it.

**P3 held, by construction rather than by count:** on `ahead > 0` the publisher refuses *before
staging*, so it creates no commit. The `ahead` side of a real fork is built by seats landing through
`surgical_land` without pushing — never by the publish loop. (a) would therefore have reversed the
2026-09-01 refusal to buy a 3-event path a median 36 minutes, on a weekly cadence.

## What WAS broken: the refusal named the one door that is unsafe where it told you to use it

The refusal read:

> *"Reconcile first: `python3 -m tools.surgical_land --merge origin/main`"*

Four lines above that string, in its own docstring, is the reason it is wrong: *"there are routinely
three lanes with uncommitted work in this tree. A daemon that merged unattended would be deciding,
every twelve minutes, to move other people's work."* **A `surgical_land --merge` run in the shared
tree opens the shared index and does exactly that.** The refusal declined to do it automatically for
a reason that does not stop being true when a person types it — and then named it as the remedy.

It was written before `background/origin_reconcile` existed. That module solved the same problem by
merging in an **isolated worktree** — *"a throwaway worktree has its OWN index, so the two
objections dissolve rather than being overridden"* — and the refusal never moved. `grep` over
`tests/` for the remedy string returned **nothing**: a refusal had made a checkable claim and
nothing opened it.

Live at 21:46Z, `.last_publish_cause.json`, the exact branch under study:
`origin/main is 4 commit(s) AHEAD of HEAD ... this tree holds 1 commit(s) of its own`.

**Fixed:** all three refusal surfaces now name `python3 -m background.origin_reconcile` and the
isolation, the real-fork branch names the owner and that it closed 41 forks unaided, and the ntfy
says plainly that this is **not** a call to action — the deadman's `[ORIGIN FORK]` alarm already
pages for the fork that does *not* close, which is the one worth waking someone for.

**Controls:** `tests/background/test_a_forks_refusal_points_at_a_door_that_is_safe_in_the_shared_tree.py`
— five, keyed to the PROPERTY and not to today's wording (*no refusal may send a reader to a bare
shared-tree merge; naming it is allowed only alongside the isolated door*), so they survive a
rewrite of every sentence and fire on a revert. A null control asserts the whole partition is
reachable and that its three legs give three DIFFERENT answers, **before** anything is asserted
about what any of them says — every other assertion here has the form *"this string does not say
X"*, which an empty string or a dead branch would satisfy. Five mutations run and **all five
fired**: revert the remedy, strip the owner, collapse both legs to one string, make the level tree
refuse, make the `ahead > 0` branch unreachable.

## Corrections to my own reading, kept beside the result

* **I was wrong mid-turn about the marker.** Seeing the run marker archived to `done/` *before* the
  commit, I read it as making the fingerprint logic's promise (*"the next identical run must
  re-attempt it"*) false, and nearly built a marker re-offer on top of that. It is not false: the
  promise is that the next run will not be *skipped* by the change-detection gate, not that this
  marker is re-offered. The mechanism is coherent and needed no repair. Recorded because a wrong
  reading beside its correction is the only evidence the check was made.
* **The pre-registration's decision rule sent me to (a), and I did not take it.** It said *"P1 and
  P2 both hold → the work is (a)"*. Both held. But the rule was written before the frequency (3
  events) and the declared weekly cadence were in view, and (a) buys a 3-event path 36 minutes on a
  7-day clock at the cost of reversing a documented refusal. **The rule was mis-specified, not the
  measurement**, and it is left standing in the pre-registration rather than edited.

## What is NOT claimed, and what is next

The race is untouched and unchanged. This closes no mechanism and adds none: it refutes a premise,
records the decision, and repairs a refusal that pointed readers at an unsafe act.

**The next item is `commit_refused` at 272.** That is where publish cycles actually die — nine times
the fork's whole contribution — and nothing in this direction, or the one before it, has looked at
it. It should be measured before anything else on this surface is built.

## Class registration

Belongs to `publish_gate_and_wedge`.

*Declared 2026-09-05 by the delivery seat, on the director's instruction to fold findings into the class registers rather than leave them as individual documents. Classified on the MECHANISM THIS DOCUMENT DESCRIBES (its body), not on its title: the registered classifier greps titles, and the titles have outgrown its vocabulary — which is why 92 findings sat `unclassed` while the six classes held 138 instances. The body carries 6 matches for `publish_gate_and_wedge` against 1 for the runner-up, which is the threshold used; anything below it was left for a reader rather than graded from a sibling.*
