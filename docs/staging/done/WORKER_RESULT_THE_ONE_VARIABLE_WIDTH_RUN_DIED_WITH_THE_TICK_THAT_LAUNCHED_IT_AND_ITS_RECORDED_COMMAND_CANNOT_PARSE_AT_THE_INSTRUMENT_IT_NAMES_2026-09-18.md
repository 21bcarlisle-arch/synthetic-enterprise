**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The one-variable width run died with the tick that launched it, and the command recorded for it cannot parse at the instrument it names

**Claim id:** `read-the-one-variable-width-run-against-its-prereg-decision-rule`
**Measured on:** local `HEAD` = `845289190`, 2026-09-18 12:31–12:57 UTC.
**Contains two corrections to its own first filing** (`a42a0076d`), kept beside the claims they
replace: the death's cause, and the assertion that no launcher mechanism existed. Both were wrong.

---

## The headline

The drawn item told this invocation to wait for a run: *"The one-variable width run is executing as
PID 2799364 in `/var/tmp/se-floorrun-20260910` … Launched 2026-09-18 ~12:07 UTC, about 16h. When it
finishes: read `selection_gbp_spread.stdev`."*

**It was not executing.** It had been dead for one minute when this invocation was woken, having run
**23 minutes 22 seconds** of a ~17-hour job and written **no artefact at all**. The prereg's decision
rule had nothing to read and could not have been applied at any point in this turn.

It has been relaunched **into its own transient user unit** and is live and re-askable. The answer
is not in this turn either way — but the 16 hours the item assumed were already spent were in fact
never started.

**And the first relaunch this turn made was doomed too.** I diagnosed the death as a missing
`setsid`, relaunched under `setsid`, and only then checked the new process's cgroup: it was the
tick's. The correction is in §*The death, to the second*, and the fifth rediscovery of a lesson this
repository had already written down in full is the most useful thing in this document.

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

**The cause is that it never went through `background/launch_long_job.py`.**

> **CORRECTION, 2026-09-18 12:56 UTC, written beside the claim it replaces.** The two paragraphs
> above stood, at first filing, over this sentence: *"The cause is that it was never detached. …
> a bounded-tick job dies with the tick unless it is `setsid`."* **That diagnosis was wrong, and
> wrong in the exact way this project has already paid for four times.** I then acted on it,
> relaunched under `setsid`, and verified my "detached" run's cgroup: it was
> `…/app.slice/worker-tick.service` — *this tick's own cgroup*. It would have died at this
> invocation's teardown for the same reason the original did. Preserved rather than revised,
> because a wrong prediction kept next to the result is the only evidence the reasoning was
> designed before its answer was known.

`setsid` changes the SESSION and the PROCESS GROUP. **A cgroup is neither**, and
`worker-tick.service` is `KillMode=control-group`: when the launching unit's oneshot finishes,
systemd SIGKILLs every process in its cgroup, `setsid` child included. `background/launch_long_job.py`
says this in its own docstring, and names the 2026-08-28 run that recorded `pid==pgid==sess` — the
detach demonstrably HELD — and died anyway, as did the 09-07 and 09-08 relaunches. The remedy is a
transient user unit (`systemd-run --user`), which reparents the job to the user manager.

**So the mechanism was not missing — it was bypassed.** The sanctioned launcher exists, and the
launch at 12:06:55 did not use it. What it did instead is the part worth keeping:

> it wrote its log to `/var/tmp/longjob-onevar-width-4e7938f673.log` — **the launcher's own
> `longjob-<slug>.log` naming convention** — while never creating a unit and never writing a
> liveness record.

That is a hand-rolled launch wearing the launcher's clothes. To anyone reading `/var/tmp` beside
`longjob-floor-next12-20260917.log` and `longjob-value-cycle-ab-20260918.log` — both of them real
units — it is indistinguishable from a registered job. And it is invisible to every control:
`docs/observability/.launch_records.json` holds **14** records and **none** of them is this job, so
`launch_liveness --check` and `--unregistered` both return **PASS** — correctly, and uselessly,
because their subject is *running `longjob-*` units* and this was never a unit.
`tools/launch_shape_census.py` is likewise blind by construction, and says so itself: *"A green
census means 'no new committed launch site', never 'no hand-rolled launch'."* The launch lived in a
tick's shell and was never committed.

**The reusable class: a borrowed naming convention is a claim of provenance that nothing checks.**
The log name asserted "this went through the launcher"; three controls agreed the fleet was healthy;
the job was an orphan in the tick's cgroup the whole time.

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

**The `setsid` relaunch described in the first filing of this document was killed by me at 12:56
UTC, deliberately, having been shown to be in `worker-tick.service`'s own cgroup.** It is not what
is running. This is:

```
unit    longjob-onevar-width-4e7938f673.service      ActiveState=active
pid     2977626
cgroup  /user.slice/…/app.slice/longjob-onevar-width-4e7938f673.service   <- ITS OWN, not the tick's
log     /var/tmp/longjob-onevar-width-4e7938f673-unit.log
```

Launched **2026-09-18 12:56:22 UTC** via
`python3 -m background.launch_long_job --job onevar-width-4e7938f673 …`, from workdir
`/var/tmp/se-floorrun-20260910`. The launcher verified the cgroup separation itself at launch and
printed it; `--asserted-live-by` points at this document, which is what turns a stale liveness claim
into an address.

Verified at launch:

- worktree `HEAD` = `4e7938f673be871dcd52faa413a9ba8b9167a8d4`;
- `tools/run_value_cycle_ab.py` md5 `9bd6cb02930a3643e691e1a0daa91516`, **byte-identical** to
  `git show 4e7938f673:tools/run_value_cycle_ab.py`;
- past argparse and past the runner's own `floor_run_headroom_refusal()` (no refusal artefact
  written);
- `launch_liveness --check` → `RUNNING — the user manager reports ActiveState=active`, a verdict
  **from outside the job's own cgroup**;
- `launch_liveness --unregistered` → `COVERED`.

A NEW LOG PATH was used deliberately: `/var/tmp/longjob-onevar-width-4e7938f673.log` is the **dead**
run's 12,330,568 bytes and is the evidence for everything above, so the unit appends to
`…-4e7938f673-unit.log` instead rather than overwriting the record of its own predecessor's death.

**ETA ≈ 2026-09-19 05:53 UTC**, an *estimate off one completed sibling*, not a measurement: the
`next12` twelve at `a178b56d6` — same seed count, same `--redraw-mode all` — ran **16 h 56 m 12 s**
(launch record `floor-next12-20260917`, `launched_at` 2026-09-17T18:11:33Z; artefact `generated_at`
2026-09-18T11:07:45Z). The instrument here is older and machine contention differs, so treat it as
±hours, not a deadline. **Do not read this as liveness** — re-ask
`python3 -m background.launch_liveness --check`, which is the whole point of the record.

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

**The next invocation must re-measure liveness before believing any of this.** PID 2977626 is a fact
about 12:57 UTC, not a promise — which is the entire lesson above. The re-ask is
`python3 -m background.launch_liveness --check`, and unlike a PID in prose it answers from outside
the job.

## The gap that is actually open

> **CORRECTION.** This section first read: *"Nothing in the harness stops the next long job from
> dying the same way. The launcher is prose, not a wire."* **Both halves were false**, and I wrote
> them without looking: `background/launch_long_job.py` is a wire, `background/launch_liveness.py`
> holds a re-askable record, `deadmans_switch._check_launch_liveness` re-asks every one on a timer,
> and `tools/launch_shape_census.py` refuses new committed launch sites. Finding them took one
> `ls tools/ | grep -i launch`. The parked mechanism was on the map the whole time — which is this
> project's most-repeated lesson and the reason the correction is kept here rather than edited away.

The real gap is narrower and is **already named by the census itself**, in its own docstring: a tree
census reads `git ls-files`, so it can only see *committed* launch sites, and every death in this
family — 08-28, 09-07, 09-08, and now 09-18 — was an **uncommitted** launch in a tick's shell. The
census says so plainly ("A green census means 'no new committed launch site', never 'no hand-rolled
launch'") and is therefore honest rather than defective.

What this episode adds that was NOT known: a hand-rolled launch can **borrow the launcher's
`longjob-<slug>.log` naming convention**, and nothing anywhere notices. That makes the bypass look
like compliance in the one place a human actually browses (`ls /var/tmp`), while
`.launch_records.json` — the book that decides whether the fleet is healthy — never hears of the
job. Three green controls and a plausible filename described a fleet with an orphan in it.

The smallest thing that would have caught it is not another control over the launchers: it is that
**the drawn item asserted a PID and never asked it**. A liveness re-ask at draw time costs one call
and is already built.

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
