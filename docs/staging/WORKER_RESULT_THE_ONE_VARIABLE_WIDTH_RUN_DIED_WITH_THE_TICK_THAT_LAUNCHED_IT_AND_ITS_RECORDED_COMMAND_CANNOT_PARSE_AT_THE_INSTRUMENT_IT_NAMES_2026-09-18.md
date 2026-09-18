**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The one-variable width run died with the tick that launched it, and the command recorded for it cannot parse at the instrument it names

**Claim id:** `read-the-one-variable-width-run-against-its-prereg-decision-rule`
**Measured on:** local `HEAD` = `845289190`, 2026-09-18 12:31–12:40 UTC.

---

## The headline

The drawn item told this invocation to wait for a run: *"The one-variable width run is executing as
PID 2799364 in `/var/tmp/se-floorrun-20260910` … Launched 2026-09-18 ~12:07 UTC, about 16h. When it
finishes: read `selection_gbp_spread.stdev`."*

**It was not executing.** It had been dead for one minute when this invocation was woken, having run
**23 minutes 22 seconds** of a ~17-hour job and written **no artefact at all**. The prereg's decision
rule had nothing to read and could not have been applied at any point in this turn.

It has been relaunched, detached, and is live. The answer is not in this turn either way — but the
16 hours the item assumed were already spent were in fact never started.

## The death, to the second

`/var/tmp/longjob-onevar-width-4e7938f673.log`, 12,330,568 bytes:

| event | UTC |
|---|---|
| log Birth (run starts) | **12:06:55** |
| `ops2-peak-kill-selftest` cgroup OOM kill (pid 2896949, anon-rss 523 MB) | 12:29:55 |
| run's **last write** | **12:30:17** |
| daemon cohort restart — `supervisor.py`, `background_worker.py`, `deadmans_switch.py` | **12:30:28** |
| this invocation woken; PID 2799364 already gone | 12:31:35 |

**It was not OOM-killed.** The only OOM kills in `dmesg` today are inside the
`ops2-peak-kill-selftest-*.scope` cgroup — a deliberate self-test, a different memory cgroup, and a
523 MB victim. No kernel line names our run, and `available_mb` was 18,856 of 24,032 throughout.

**It was killed from outside.** The log ends mid-sentence, on a per-customer term line, with no
traceback, no `Killed`, and no non-zero exit written anywhere — the signature of a signal, not a
Python fault. It died **11 seconds before** the daemon cohort was restarted, which is the shape of a
process-group kill that precedes the restart.

**The cause is that it was never detached.** It was launched as an ordinary child of the launching
tick, in that tick's process group. This is the failure mode the harness has already paid for and
written down — *a bounded-tick job dies with the tick unless it is `setsid`*.

### How far it actually got

Not "most of the way". `--noise-floor-seeds` costs **3 full passes per seed**, so 12 seeds is 36
passes. The log carries **2** `=== Phase 2b — Gas Dual Fuel ===` markers and **1**
`=== SURVIVED full window` — **one pass of 36 complete**, killed partway through the second.

I am deliberately *not* deriving an ETA from that marker count: a marker whose per-unit meaning has
not been established is how this lane got an ETA wrong by seven hours on 2026-09-17. The ruler used
below is a **completed sibling run** instead.

## The second trap, which the relaunch would have hit

The command recorded for this run — in
`WORKER_RESULT_THE_SELECTION_LEG_DIFFERENCES_TWO_ARMS_OVER_DIFFERENT_PRICED_POPULATIONS…` — is:

```
python3 -u -m tools.run_value_cycle_ab --noise-floor-seeds 3100001..3100012
   --redraw-mode all --redraw-key elasticity
   --out /var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json
```

That command was run at `a178b56d6`. **It cannot run at `4e7938f673`,** which is the whole point of
this experiment — the instrument is deliberately the older one:

| | `a178b56d6` (the wide twelve) | `4e7938f673` (this run) |
|---|---|---|
| `--redraw-key` flag | present (artefact records `redraw_key='elasticity'`) | **absent** — `grep -c redraw_key` = **0** |
| seed parsing | accepts `3100001..3100012` | `[int(s) for s in split(",")]` → **`ValueError: invalid literal for int() with base 10: '3100001..3100012'`** |

Copied forward verbatim, the relaunch would have died in argparse in under a second and left the
same absent artefact — reading, again, exactly like a run still in progress. The seeds were expanded
to an explicit comma list and `--redraw-key` dropped.

**The reusable class: a long job's recorded invocation is pinned to the commit it ran at.** Carrying
it to a different checkout of the same tool is an un-re-asked prediction that the CLI did not move —
and on a one-variable instrument swap, the CLI moving is precisely what is being tested.

## What is now running

```
PID 2914778   SID 2914778   PGID 2914778      <- its own session: setsid, so a process-group
                                                 kill of any tick cannot reach it
python3 -u -m tools.run_value_cycle_ab
  --noise-floor-seeds 3100001,3100002,...,3100012
  --redraw-mode all
  --out /var/tmp/se-floorrun-20260910/docs/observability/value_cycle_ab_s1_noise_floor_next12_at_4e7938f673.json
```

Launched **2026-09-18 12:37:18 UTC** from `/var/tmp/se-floorrun-20260910`, verified at launch:

- worktree `HEAD` = `4e7938f673be871dcd52faa413a9ba8b9167a8d4`;
- `tools/run_value_cycle_ab.py` md5 `9bd6cb02930a3643e691e1a0daa91516`, **byte-identical** to
  `git show 4e7938f673:tools/run_value_cycle_ab.py`;
- past argparse and past the runner's own `floor_run_headroom_refusal()` (no refusal artefact
  written);
- progressing — CPU time 11 s → 27 s over 40 s wall, RSS 605 → 821 MB.

**ETA ≈ 2026-09-19 05:34 UTC**, and this is an *estimate off one completed sibling*, not a
measurement: the `next12` twelve at `a178b56d6` — same seed count, same `--redraw-mode all` — ran
**16 h 56 m 54 s** (start 2026-09-17 18:10:51 UTC, `generated_at` 2026-09-18T11:07:45Z). The
instrument here is older and machine contention differs, so treat it as ±hours, not a deadline.

## What is still owed, and the decision rule is untouched

`docs/staging/records/PREREG_THE_ONE_VARIABLE_WIDTH_CHECK_SEPARATES_THE_INSTRUMENT_FROM_THE_SEED_SET_2026-09-18.md`
is landed and tracked, and **its decision rule is unchanged and unread** — nothing in this turn
touched it, because nothing in this turn had a number to test it against:

- `sd_X < 3000` → width is the **instrument's**; published sign's width defensible.
- `sd_X > 4000` → width is the **seed set's**; `NOISE_FLOOR_PATH`'s sign must be **withdrawn** from
  the page, not caveated.
- `3000 ≤ sd_X ≤ 4000` → INDETERMINATE; the page says so.

The contrast figures the prereg names were re-verified against the artefact on disk this turn:
`value_cycle_ab_s1_noise_floor_20260910.json` is n=9, mean −1749.47, **stdev 1840.39**, seeds
11111…99999, and is single-valued at `4e7938f673`. The prereg's table is correct.

**The next invocation must re-measure liveness before believing any of this.** PID 2914778 is a fact
about 12:40 UTC, not a promise — which is the entire lesson above.

## The mechanism defect, unfixed

Nothing in the harness stops the next long job from dying the same way. The launcher is prose, not a
wire: there is no check that a job expected to outlive its tick was started in its own session, and
an absent artefact is indistinguishable from a running one — the runner's own `--ignore-headroom`
help text says exactly this about OOM ("writes no artefact and reads like one still running") and
the same ambiguity swallowed a signal kill here.

Filed LATENT rather than BLOCKING deliberately, and this document does not claim any published
figure is wrong: nothing here moved a number on any page, and no control returned a false verdict.
The contested *width* behind the published selection sign is a separate, already-BLOCKING finding
in lane `A_strategy_governance`
(`SEAT_RESULT_THE_TWELVE_REPLICATE_THE_LEVEL_AND_REFUTE_THE_WIDTH_AND_THE_SIGN_WAS_A_PROPERTY_OF_THE_WIDTH_2026-09-18.md`),
which owns that question; this one is about the launcher and must not duplicate that severity into
`H_harness`.

What this cost was ~23 minutes of compute and, more expensively, an invocation that was told to wait
for something already dead. The smallest thing that would have caught it is a liveness probe on the
PID at draw time — the item asserted the PID and never asked it.
