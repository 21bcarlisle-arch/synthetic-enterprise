**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — a lost push race had a truthful NAME and an untruthful MESSAGE

BLOCKING by construction, and the clause is the right one: the instrument is the director's own
instant channel, and it made a false claim on it. The deadman's fork alarm told him

> landings and publishing stay blocked until someone reconciles.

for an outcome that clears itself on the next five-minute cadence, with nothing to reconcile and
nothing for him to do. `BLOCKED_WORK` is the class he acts on; a page he cannot act on spends the
only scarce resource in this architecture.

**Filed:** 2026-09-05, delivery seat (isolated worktree). **Repaired in the same commit.**

**Discharged:** `tests/background/test_a_benign_lost_push_race_is_not_paged_as_blocked_work.py::test_a_healing_race_does_not_tell_him_work_is_blocked`

---

## The premise, re-measured before starting

The item cites `3d5694078` and the draw-time check reported it already an ancestor of
`origin/main`. **It is, and the premise is NOT spent.** That commit landed the *rename* in
`background/origin_reconcile.py` — `_classify_push_failure` now returns `REFUSED_RACE` for a lost
push race, told apart from `ERROR` at both push sites. What was handed on is the separate defect
that **nothing downstream read the new name**, and that was still true at HEAD:

    $ grep -rn REFUSED_RACE --include=*.py . | grep -v origin_reconcile.py
    tests/background/test_a_lost_push_race_is_named_apart_from_a_reconciler_that_cannot_push.py  (9 hits)
    tests/background/test_a_staged_document_no_longer_blocks_every_landing.py                    (3 hits)

Two test files and no production reader. `deadmans_switch._check_origin_fork` enumerated
LEVEL/RECONCILED/PUSHED/FAST_FORWARDED as clear and GATE_RUNNING as quiet, and everything else —
including the new status — fell through to one `real_alarm` classed `BLOCKED_WORK`.

## Why the obvious repair was the wrong one, and the direction said so

Suppressing `REFUSED_RACE` beside `GATE_RUNNING` would have been two lines and a fail-silent hole.
**The two states are opposites:**

| | what was observed | is the fork open? |
|---|---|---|
| `GATE_RUNNING` | **nothing** — the publish gate holds the lock | unknown |
| `REFUSED_RACE` | the reconciler fetched, merged, gated the merge **clean**, and could not push | **yes, and it stayed open** |

A race is not benign because it is a race. It is benign because it *heals*: the next cadence
re-fetches, re-merges on the new base and gates again. A reconciler that keeps losing has stopped
converging, the fork is standing, and nothing this machine does reaches origin — which is
`BLOCKED_WORK` and genuinely his. Silent suppression is the state in which that never pages at all.

## What was built

A three-way partition on the one thing that distinguishes the benign case — **did it heal?**

* **healing** (episode younger than `RACE_PERSISTENCE_SECONDS`) — logged, nothing sent. Quiet is
  not invisible: the record carries the count and the age every cadence.
* **not converging** (at or beyond it) — paged as `BLOCKED_WORK`, which by then is true, with a
  message that names what is actually wrong (*"something is pushing to origin faster than a gate
  run takes"*) and explicitly does **not** ask him to merge anything by hand, because the merge
  already works.
* **unmeasurable** — the episode record is present and unreadable. Reported, never assumed benign.
  "We cannot tell" is a result and belongs on the surface; the alternative direction is the
  2026-08-09 shape verbatim, a record that cannot be read reporting a fresh episode inside an old
  one, and here it would be a standing race that never pages.

**The window is derived, not picked.** `RACE_PERSISTENCE_SECONDS = BLOCKED_THRESHOLD_SECONDS`. The
question *"how long may work sit undelivered before it is worth his attention"* already has an
answer in this module, and an open fork **is** undelivered work. A second number for one condition
is one name carrying two values by another route. At `POLL_INTERVAL_SECONDS` the self-healing retry
has had nine goes by the time it elapses.

**The episode clock is the self-clearing-alarm class (PW2)** — the failure path writes the state its
own alarm's severity comes off. Guarded with `episode_monotonic.guard_episode`, not a sixth
hand-rolled low-water loop: the race branch may only ever **extend** (`race_since` low-water,
`races` high-water), and the only close is an outcome the *reconciler* reported. `GATE_RUNNING`
closes nothing and extends nothing, which is why the episode is measured in elapsed time and not in
cadences — the clock is the one thing that keeps running when nothing was observed.
Dispositioned `real`/`guarded` in `docs/design/self_clearing_alarm_dispositions.json`.

## Evidence

**Twelve mutations, twelve fired.** Each applied in place and reverted, against the 13 controls in
the new file (`13 passed` clean):

| mutation | red |
|---|---|
| suppress `REFUSED_RACE` beside `GATE_RUNNING` | 8 |
| delete the `REFUSED_RACE` branch (the pre-repair code) | 9 |
| never treat a race as benign (always page) | 4 |
| bypass `guard_episode` and write `race_since` directly | 6 |
| unreadable record reads as absent | 2 |
| no close on a non-race refusal | 1 |
| close the episode from the race path too | 1 |
| transition state keyed on `behind` | 1 |
| an independent literal for the window | 1 |
| `GATE_RUNNING` extends / closes / clears | 1 each |

Two of those "survived" on the first pass and **both were shell-quoting artefacts, not
equivalences** — the patch text never matched. Established rather than assumed, which is the rule:
re-applied through Python with the target asserted present, both fire.

**The loader partition, measured, not claimed** — all seven prior states run against
`_extend_race_episode` before it landed:

| prior | measurable | races | age | preserved |
|---|---|---|---|---|
| missing file | yes | 1 | 0.00h | — |
| empty / truncated / `null` / `[1,2,3]` / `"abc"` | **no** | 1 | — | `.origin_race_episode.json.unreadable` |
| open episode (3h, 36 races) | yes | **37** | **3.00h** | — |

The five unreadable forms page and preserve their bytes rather than degrading to a fresh episode —
deliberately the *opposite* direction to the five carriers `background/episode_prior.py` was written
about, because there an unreadable prior costs a severity and here it costs the whole judgement.

**Suites:** `159 passed` across `test_deadmans_switch.py`,
`test_a_staged_document_no_longer_blocks_every_landing.py`,
`test_a_lost_push_race_is_named_apart_from_a_reconciler_that_cannot_push.py`,
`tests/controls/test_daemon_loop_mutation.py`, `test_self_clearing_alarm_census.py`,
`test_pw4_episode_guards.py`. `self_clearing_alarm_census --check` exits 0.

## What is NOT closed

The fall-through alarm's own transition state is still `f"{status}:{behind}"`, and `behind` moves
every cadence — so a standing `REFUSED_CONFLICT` re-sends on every cycle its count changes, which is
the "a state that moves every cycle cannot suppress anything" shape the worktree reaper's comment
already names two functions above it. **Out of scope here and left deliberately** rather than
widened into: the race branch it was drawn for now keys on the episode. Worth its own pass.
