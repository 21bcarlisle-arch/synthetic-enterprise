# Lane 0 — the three-arm A/B: the 15:08Z run is DEAD, and it died of a known cause

**STATUS (2026-08-27T19:2xZ): the run is not in flight. It was killed 4m28s in and this file
said "in flight" for the next 2h12m.** That is now corrected. The blocking sub-item below is
the artefact, and the route to it has changed — see *How the re-run is launched*.

**BLOCKING SUB-ITEM:** the second row of the three-arm table. It needs the artefact
`docs/observability/value_cycle_ab_s1_three_arm.json`.

**WHAT UNBLOCKS IT:** that file existing with `level_vs_selection.available == true`.

**Claim id (bind every commit to it):** `land-the-widened-world-then-run-the-three-arm-ab-once`
(the earlier `re-run-the-three-arm-ab-on-the-s1-world` was auto-released by
`background/alarm_repetition.py` at 2.2h — correctly, the work had stopped.)

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

**R12 governs the reading.** A selection leg still worth less than nothing FINISHES this. It is
the honest and likely outcome of widening one axis, and it is not a cue to tune the arm until it
wins.
