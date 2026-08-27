# Lane 0 — the three-arm A/B and its error bar: in flight since 2026-08-27T21:28:05Z

**STATUS (2026-08-27T22:00Z): PHASE=base LANDED, PHASE=floor IN FLIGHT.** Three attempts today
produced nothing; the fourth produced the reading. `three-arm-and-floor.service` launched
21:28:05Z and wrote `docs/observability/value_cycle_ab_s1_three_arm.json` at **21:56:34Z with
`rc=0`** — 28m29s, ~9.5 min per arm. `PHASE=floor` (nine passes, seeds 11111,22222,33333) began
at 21:56:38Z and is due around **23:20Z**.

The two dead attempts died of *different* causes and neither was detachment: the 15:08Z run was
killed from outside (diagnosed below), the 19:45Z run was stopped by its own bundled commit
gate. **Neither is to be answered by detaching harder**, and this launch answered the second by
removing the bundled gate rather than the detachment.

**THE READING IS PUBLISHED.** The second row exists in
`docs/staging/done/WORKER_FINDING_THE_VALUE_ARMS_ADVANTAGE_IS_THE_LEVEL_NOT_THE_SELECTION_2026-08-27.md`:
world `8d8e9c2c8`, 210 accounts / 187 dual fuel, settled clock; control £113,282.62, value
£120,648.84, level @£44.50 £120,823.40; **level share 102.4%, selection −£174.57**. Per R12 that
is a complete answer and finishes the question the run was launched to ask.

**THE ONE REMAINING SUB-ITEM:** the spread cell in that row still reads IN FLIGHT. It needs
`docs/observability/value_cycle_ab_s1_noise_floor.json`. When it exists, replace the cell with
`selection_gbp_spread.min … .max` / `.stdev`, state `selection_distinguishable_from_zero`, and
check `seeds[].elasticity_draws > 0` on every seed. **If the floor half died where the base half
succeeded, say the spread is unmeasured** — the row already carries the ≈ ±£4,400 scratchpad
upper bound as the nearest measured band, so it is not bare either way.

**Claim id (bind every commit to it):**
`measure-the-widened-world-once-and-bring-its-error-bar-with-it`. Two predecessors were
auto-released by `background/alarm_repetition.py` when the work stopped —
`re-run-the-three-arm-ab-on-the-s1-world` at 2.2h and
`land-the-widened-world-then-run-the-three-arm-ab-once` after the gate refusal. Both releases
were correct: nothing was moving.

---

## The death, with every claim labelled per R9

**OBSERVED**, from `docs/observability/three_arm_s1_run.log`:

| fact | value |
|---|---|
| START line | `pid=1128717 pgid=1128717 sess=1128717 at=2026-08-27T15:08:25Z` |
| session detachment | **held** — pid == pgid == sess, so `setsid` did what it claims |
| last write | `2026-08-27T15:12:53Z` — **4m28s** after launch |
| size | 56,229 lines, 6,050,796 bytes |
| last line | mid-walk, `5,523,400 settlement periods … 2023-04-11 period 21, treasury £258460–466` |
| `END rc=` line | **absent** |
| traceback | **absent** |
| artefact | `value_cycle_ab_s1_three_arm.json` **does not exist** |
| PID 1128717 | gone |

**OBSERVED — it was NOT killed by the OOM killer.** `dmesg -T`'s ring buffer reaches back to
`Wed Aug 26 00:38:56`, so it fully covers the window. It holds 64 `Killed process` records.
**None of them falls between 16:08:25 and 16:12:53 local (=15:08–15:12Z).** The nearest are
`15:29:45` (*before* this run launched) and `16:28:04` (15 minutes *after* it was already dead).
A cgroup or global OOM kill always leaves a `dmesg` record; there is no record, so this was not
an OOM kill.

**OBSERVED — the `oom_kills_total` counter cited in the direction is not a memory-pressure
signal at all.** All 64 records carry
`oom_memcg=…/app.slice/ops2-peak-kill-selftest-<pid>.scope`, and all are the same balloon
(`total-vm:540388kB, anon-rss:523136kB`). That cgroup is created by this repository's own test:
`tests/tools/test_measure_publish_gate_subject_cost.py:3148,3173`,
`unit = "ops2-peak-kill-selftest-{}".format(os.getpid())`. The counter that
`background.resource_headroom.sample()` publishes as `oom_kills_total` (105 at 17:21Z, **107** at
19:12Z) is therefore dominated — in this buffer, entirely — by a control deliberately OOM-ing
*itself* inside a private cgroup. It rises when the publish-gate cost test runs, not when the
machine is under memory pressure. **Filed separately as its own finding; do not cite this
counter as evidence of memory pressure again.** For the record, headroom at 19:12Z was
18,625 MB available of 24,032 MB — no pressure.

**OBSERVED — the whole process group died, not just Python.** The wrapper's shape is
`(…; python3 …; echo "END rc=$?")`. Had only the Python child been signalled, the surrounding
shell would still have written an `END rc=` line. There is no `END` line at all, so the wrapper
shell died in the same event.

**INFERRED (the killer was not caught in the act) — this is the FIFTH death of an
already-diagnosed class, and the diagnosis is written down in this repo.**
`tools/measure_publish_gate_subject_cost.py:207–229`, "SESSION DETACHMENT WAS NOT ENOUGH: THE
FOURTH DEATH (2026-08-10)", records the identical signature: session detachment demonstrably
held, died ~3.5 minutes in, no kernel OOM in the window, and no reaper anywhere in the
repository (`worker_seat.py` states the reaping path is DELETED; `pkill`/`killpg` appear only in
comments). Its conclusion applies unchanged here: **`start_new_session` changes the session and
the group, but it does not change the child's `ppid`**, so a killer that walks `/proc` for a
bounded turn's DESCENDANTS still finds it. That is the shape of a harness cleaning up after the
tick that launched it.

**This is an R3 two-strike signal and it has already been actioned once.** The escalation that
file pre-committed to — "a systemd unit beside `reconcile-watch.timer`, not a fourth identical
launch" — was built, as its `--systemd` path. The 15:08Z run did not use it, because
`tools/run_value_cycle_ab.py` has no launch mode of its own (`--help`: only `--end-year`,
`--out`, `--level-arm`, `--noise-floor-seeds`). So the fix existed and the caller could not
reach it. **Detaching harder is not the answer and must not be tried a sixth time.**

## How the re-run is launched — reparent it, do not detach it

`systemd-run --user` hands the job to the user manager, which re-parents it out of the launching
tick's descendant tree entirely. That is the property `setsid` does not have and the reason the
previous four deaths kept recurring.

```
systemd-run --user --unit=three-arm-ab --same-dir --collect \
  /bin/bash -c '… python3 -m tools.run_value_cycle_ab --level-arm --out <artefact> …'
```

`systemctl --user status three-arm-ab` is the liveness check; the log still carries START/END.

### The 19:45Z run — DEAD, and it did not die of detachment

**OBSERVED**, `docs/observability/three_arm_composite_run.log` and
`journalctl --user -u land-then-three-arm-ab`:

| fact | value |
|---|---|
| START | `pid=1402748 ppid=382 pgid=1402748` at `2026-08-27T19:45:12Z` |
| reparenting | **held** — `ppid=382`, the user manager. Nothing killed it from outside. |
| END line | `END rc=1 PHASE=land -- gate refused, A/B deliberately NOT run` at 19:55:59Z |
| cause | `surgical_land` REFUSED: 2 failed, 485 passed in 621.40s |
| the two reds | `test_phase40a_pass_through::test_pass_through_customer_in_fast_run`, `test_run_phase2b::test_the_run_emits_a_treasury_drawdown_register` |
| artefact | still absent at that point |

So the escalation worked and the *gate* stopped the run — exactly the discriminating outcome
the PHASE tag was added to produce. **Detaching harder was correctly not attempted.**

`8d8e9c2c8` then settled both reds by measurement: a throwaway worktree at clean HEAD
reproduces **both** with no working-tree diff present, so the widened world caused neither, and
the treasury null control is correct and correctly firing (its 2016–2017 fixture window holds
zero drawdown events). Both repairs are QUEUED. That commit also records why the composite was
never one unit: `tests_for()` is per-path, the four paths have disjoint gate sets, and bundling
turned a 0.57s gate into a 621s one.

### The live run — launched 2026-08-27T21:28:05Z

```
unit      three-arm-and-floor.service   (systemd --user; MainPID 1534725, ppid 382)
script    /tmp/three_arm_and_floor.sh
log       docs/observability/three_arm_and_floor_run.log
artefacts docs/observability/value_cycle_ab_s1_three_arm.json      (PHASE=base)
          docs/observability/value_cycle_ab_s1_noise_floor.json    (PHASE=floor)
liveness  systemctl --user is-active three-arm-and-floor.service
world     8d8e9c2c853c6ac2efa1b461a4fbc8698c770084, recorded in the log at launch
```

**The land is no longer bundled into it.** That is the whole change of shape. The A/B measures
the tree it runs on; gating an unrelated four-path pathspec in front of it bought nothing and
cost the reading twice. The one dirty sim path at launch is `simulation/run_phase2b.py`, logged
by the wrapper, and its diff is a `gap_ledger_path=None` test-injection parameter whose default
preserves the live path exactly — behaviour-neutral for a real run, so the named commit does
describe the world that was walked.

It does two things in order, and **the second is conditional on the first**:

1. `PHASE=base` — `run_value_cycle_ab --level-arm --out …_s1_three_arm.json`. The base reading.
2. On `rc=0` only, `PHASE=floor` — `--level-arm --noise-floor-seeds 11111,22222,33333` to a
   separate `--out`. Three seeds × three arms = nine full passes, so it is much the longer half.

**The order is the point.** The noise-floor mode had never once been executed end to end; putting
it second means a defect in it cannot cost the base reading, which is the deliverable. `END rc=`
carries `PHASE=base` or `PHASE=floor` so a reader can tell which half died.

**On R18.** The direction asked for a foreground `tools.wait_for --pid` bound to the run. That is
the right instrument for a job that fits inside a turn and the wrong one for a job designed to
outlive it — a foreground waiter here would itself be killed at the 10-minute tool timeout and
would prove nothing. The subject and the deadline still exist, in the unit name and in the
START/END wrapper. `wait_for` was used twice this turn where it fits: on the control suite
(165s) and on the single-test re-run (540s).

## What is already landed and pushed — do NOT redo it

`bafa625d1` (on origin/main):

1. **Act one, complete.** The 2019 ladder section of `docs/design/THE_VALUE_CYCLE_REALISED_AB.md`
   now opens with a forward pointer to the full-window reading, in the headline table's own
   supersession style. It separates what survives (the win is not price — both windows agree) from
   what does not (the 1.16× figure's direction and size, computed on 6 decisions because 18 priced
   renewals rolled after 2019-12-31 and were dropped). Anchors verified to resolve. **Finished.**
2. **The runner learned the third arm.** `tools/run_value_cycle_ab.py --level-arm` runs
   `flat_at_level` as a third pass **at the value arm's own realised median read off the same
   run** — never the remembered £44.50. New `level_vs_selection` block. 9 R15 tests in
   `tests/tools/test_the_level_arm_in_the_ab_runner.py`, mutation-proven both directions.

## The widened world — landed 2026-08-27, so do NOT rebuild it either

The direction cited "188 uncommitted lines" across `simulation/customer_events.py`,
`simulation/market_switching_propensity.py`, `simulation/population_draw.py`, the
`segmentation_curriculum_v1.json` edit and an untracked
`tests/simulation/test_discoverability_claims_are_enforced.py`. **Most of that had already
landed by the time the doorbell was read** — in `bca9bb3af`, `898d78239`, `3cefa754b` and
`9e52d2254`. Only `simulation/customer_events.py` and `simulation/run_phase2b.py` were still
dirty, and they are adopted as-is (never rebuilt) in the commit that carries this file.

**UPDATE 21:30Z.** `simulation/customer_events.py` is clean at `8d8e9c2c8` — the widening is on
`main`. The one remaining dirty sim path is `simulation/run_phase2b.py`, and its whole diff is a
`gap_ledger_path=None` parameter added to `main()` so a test can redirect the coupled-gap ledger
the `live_ledger_guard` refuses to let it touch. Default `None` = the live path, byte for byte,
so the run in flight walks the world `8d8e9c2c8` describes. That path cannot land alone right
now: its gate includes the 621s `test_run_phase2b` treasury suite, red at clean HEAD for a
reason `8d8e9c2c8` already diagnosed and queued.

## What to do when the artefact lands

Add **a second row** to the three-arm table in
`docs/staging/done/WORKER_FINDING_THE_VALUE_ARMS_ADVANTAGE_IS_THE_LEVEL_NOT_THE_SELECTION_2026-08-27.md`,
naming the world **by commit**, the book from `book_identity.control_arm`, and the settled clock
per R14. Read every number off `level_vs_selection`:

| what to report | key |
|---|---|
| the three nets | `control_net_gbp`, `value_arm_net_gbp`, `level_arm_net_gbp` |
| the level's share of the advantage | `level_share_of_advantage` (was **119.7%**) |
| what the selection was worth | `selection_gbp` (was **−£1,388.80** decade, −£991.38 on 2019) |
| the level actually used | `level_gbp_per_mwh` — the arm's own median, **expect it to have moved** |

And, in the **same row**, the error bar, read off `value_cycle_ab_s1_noise_floor.json`:

| what to report | key |
|---|---|
| the spread on the selection leg | `selection_gbp_spread.min … .max` (and `.stdev`) |
| the spread on the share | `level_share_spread.min … .max` |
| whether the leg is readable at all | `selection_distinguishable_from_zero` |
| that the patch fired | `seeds[].elasticity_draws` — a zero here RAISES rather than reporting a floor of 0 |

A point estimate published without the spread beside it is the defect this half exists to
prevent: no reader can then take the number without its error bar.

**R12 governs the reading.** A selection leg still worth less than nothing FINISHES this. It is
the honest and likely outcome of widening one axis, and it is not a cue to tune the arm until it
wins. **A spread wider than the effect ALSO finishes it, and is the more valuable answer** —
it means every reading built on this instrument needs the caveat, including the 119.7% already
published above.
